import uuid
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.extraction import Extraction
from app.services.pdf_processor import PDFProcessor
from app.services.llm_service import LLMService, Provider
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ExtractionService:
    """Service for managing contract clause extractions"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        # LLM service will be initialized per request with the provider
        self._llm_service_cache = {}
    
    def _get_llm_service(self, provider: Provider = "openai") -> LLMService:
        """Get or create LLM service for the specified provider"""
        if provider not in self._llm_service_cache:
            logger.debug(f"Creating new LLM service instance for provider: {provider}")
            self._llm_service_cache[provider] = LLMService(provider=provider)
        else:
            logger.debug(f"Reusing cached LLM service instance for provider: {provider}")
        return self._llm_service_cache[provider]
    
    def process_contract(
        self,
        file_content: bytes,
        filename: str,
        db: Session,
        provider: Provider = "openai"
    ) -> Extraction:
        """
        Process a contract document and extract clauses
        
        Args:
            file_content: PDF file content as bytes
            filename: Original filename
            db: Database session
            provider: LLM provider to use ("openai" or "gemini"), defaults to "openai"
            
        Returns:
            Extraction record from database
        """
        logger.info(f"Processing contract: {filename} with provider: {provider}")
        logger.debug(f"File size: {len(file_content)} bytes")
        
        # Extract text from PDF
        try:
            logger.debug("Extracting text from PDF")
            pdf_data = self.pdf_processor.extract_text_from_pdf(file_content)
            text = pdf_data["text"]
            pdf_metadata = pdf_data["metadata"]
            logger.info(f"PDF processed: {pdf_metadata.get('page_count', 0)} pages, text length: {len(text)} chars")
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}", exc_info=True)
            raise
        
        # Extract clauses using LLM
        try:
            logger.debug(f"Extracting clauses using {provider}")
            llm_service = self._get_llm_service(provider)
            clauses = llm_service.extract_clauses(text)
            logger.info(f"Extracted {len(clauses)} clauses from document")
        except Exception as e:
            logger.error(f"Failed to extract clauses: {str(e)}", exc_info=True)
            raise
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        logger.debug(f"Generated document ID: {document_id}")
        
        # Prepare metadata
        metadata = {
            **pdf_metadata,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "clause_count": len(clauses),
            "provider": provider,
        }
        
        # Create database record
        try:
            logger.debug("Creating database record")
            extraction = Extraction(
                document_id=document_id,
                filename=filename,
                clauses=clauses,
                doc_metadata=metadata,
                created_at=datetime.utcnow()
            )
            
            db.add(extraction)
            db.commit()
            db.refresh(extraction)
            logger.info(f"Successfully saved extraction to database: {document_id}")
        except Exception as e:
            logger.error(f"Failed to save extraction to database: {str(e)}", exc_info=True)
            db.rollback()
            raise
        
        return extraction
    
    def get_extraction(self, document_id: str, db: Session) -> Extraction:
        """
        Get extraction by document ID
        
        Args:
            document_id: Unique document identifier
            db: Database session
            
        Returns:
            Extraction record or None
        """
        logger.debug(f"Retrieving extraction: {document_id}")
        extraction = db.query(Extraction).filter(Extraction.document_id == document_id).first()
        if extraction:
            logger.debug(f"Found extraction: {document_id} (filename: {extraction.filename})")
        else:
            logger.warning(f"Extraction not found: {document_id}")
        return extraction
    
    def list_extractions(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        List all extractions with pagination
        
        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with total count and list of extractions
        """
        logger.debug(f"Listing extractions: page={page}, page_size={page_size}")
        query = db.query(Extraction)
        total = query.count()
        
        offset = (page - 1) * page_size
        extractions = query.order_by(Extraction.created_at.desc()).offset(offset).limit(page_size).all()
        
        logger.debug(f"Found {len(extractions)} extractions (total: {total})")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "extractions": extractions
        }
