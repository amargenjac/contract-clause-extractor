import uuid
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.extraction import Extraction
from app.services.pdf_processor import PDFProcessor
from app.services.llm_service import LLMService, Provider


class ExtractionService:
    """Service for managing contract clause extractions"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        # LLM service will be initialized per request with the provider
        self._llm_service_cache = {}
    
    def _get_llm_service(self, provider: Provider = "openai") -> LLMService:
        """Get or create LLM service for the specified provider"""
        if provider not in self._llm_service_cache:
            self._llm_service_cache[provider] = LLMService(provider=provider)
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
        # Extract text from PDF
        pdf_data = self.pdf_processor.extract_text_from_pdf(file_content)
        text = pdf_data["text"]
        pdf_metadata = pdf_data["metadata"]
        
        # Extract clauses using LLM
        llm_service = self._get_llm_service(provider)
        clauses = llm_service.extract_clauses(text)
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Prepare metadata
        metadata = {
            **pdf_metadata,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "clause_count": len(clauses),
        }
        
        # Create database record
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
        return db.query(Extraction).filter(Extraction.document_id == document_id).first()
    
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
        query = db.query(Extraction)
        total = query.count()
        
        offset = (page - 1) * page_size
        extractions = query.order_by(Extraction.created_at.desc()).offset(offset).limit(page_size).all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "extractions": extractions
        }
