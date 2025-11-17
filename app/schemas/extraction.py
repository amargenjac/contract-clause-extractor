from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Clause(BaseModel):
    """Schema for a single clause"""
    clause_type: str
    content: str
    page_number: Optional[int] = None


class ExtractionResponse(BaseModel):
    """Schema for extraction response"""
    document_id: str
    filename: str
    clauses: List[Clause]
    metadata: Dict[str, Any]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ExtractionListResponse(BaseModel):
    """Schema for paginated extraction list response"""
    total: int
    page: int
    page_size: int
    extractions: List[ExtractionResponse]


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
