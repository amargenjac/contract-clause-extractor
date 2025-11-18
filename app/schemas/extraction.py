from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Clause(BaseModel):
    """Schema for a single clause"""
    clause_type: str = Field(description="The category of the clause (e.g., 'Payment Terms', 'Confidentiality', 'Termination', 'Liability', 'Governing Law', etc.)")
    content: str = Field(description="The actual text of the clause")
    page_number: Optional[int] = Field(None, description="The page number where the clause appears (if mentioned in the text)")


class ClauseExtractionResponse(BaseModel):
    """Schema for AI response containing extracted clauses"""
    clauses: List[Clause] = Field(description="List of extracted clauses from the contract")


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
