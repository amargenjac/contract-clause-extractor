from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON

from app.core.database import Base


class Extraction(Base):
    """Database model for contract clause extractions"""
    
    __tablename__ = "extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    clauses = Column(JSON, nullable=False)
    doc_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
