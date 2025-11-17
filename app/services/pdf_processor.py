from typing import Dict, Any
import PyPDF2
from io import BytesIO

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class PDFProcessor:
    """Service for processing PDF documents"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> Dict[str, Any]:
        """
        Extract text from PDF file
        
        Args:
            file_content: PDF file content as bytes
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            logger.debug(f"Extracting text from PDF (size: {len(file_content)} bytes)")
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            page_count = len(pdf_reader.pages)
            logger.debug(f"PDF has {page_count} pages")
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num} ---\n{page_text}"
                logger.debug(f"Extracted text from page {page_num} ({len(page_text)} chars)")
            
            has_text = bool(text.strip())
            logger.info(f"PDF text extraction complete: {page_count} pages, {len(text)} total chars, has_text: {has_text}")
            
            metadata = {
                "page_count": page_count,
                "has_text": has_text
            }
            
            # Add PDF metadata if available
            if pdf_reader.metadata:
                metadata["pdf_metadata"] = {
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                    "creator": pdf_reader.metadata.get("/Creator", ""),
                }
                logger.debug(f"PDF metadata found: {metadata['pdf_metadata']}")
            
            return {
                "text": text,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            raise ValueError(f"Error processing PDF: {str(e)}")
