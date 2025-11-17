from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.extraction import (
    ExtractionResponse,
    ExtractionListResponse,
    ErrorResponse,
    Clause
)
from app.services.extraction_service import ExtractionService
from app.services.llm_service import Provider

router = APIRouter(prefix="/api", tags=["extractions"])
extraction_service = ExtractionService()


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def extract_contract_clauses(
    file: UploadFile = File(..., description="PDF contract document"),
    provider: Provider = Query("openai", description="LLM provider to use: 'openai' or 'gemini'"),
    db: Session = Depends(get_db)
):
    """
    Extract and structure key clauses from a legal contract.
    
    - **file**: PDF contract document to process
    - **provider**: LLM provider to use ("openai" or "gemini"), defaults to "openai"
    
    Returns structured JSON with:
    - document_id: Unique identifier for the extraction
    - filename: Original filename
    - clauses: List of extracted clauses with type, content, and page number
    - metadata: Document metadata including page count and extraction info
    - created_at: Timestamp of extraction
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate provider
    if provider not in ["openai", "gemini"]:
        raise HTTPException(status_code=400, detail="Provider must be 'openai' or 'gemini'")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process the contract
        extraction = extraction_service.process_contract(
            file_content=file_content,
            filename=file.filename,
            db=db,
            provider=provider
        )
        
        # Convert clauses to Pydantic models
        clauses = [Clause(**clause) for clause in extraction.clauses]
        
        return ExtractionResponse(
            document_id=extraction.document_id,
            filename=extraction.filename,
            clauses=clauses,
            metadata=extraction.doc_metadata,
            created_at=extraction.created_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.get(
    "/extractions/{document_id}",
    response_model=ExtractionResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Document not found"}
    }
)
def get_extraction(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve extraction results for a specific document.
    
    - **document_id**: Unique identifier of the document
    
    Returns the extraction results including all clauses and metadata.
    """
    extraction = extraction_service.get_extraction(document_id, db)
    
    if not extraction:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Convert clauses to Pydantic models
    clauses = [Clause(**clause) for clause in extraction.clauses]
    
    return ExtractionResponse(
        document_id=extraction.document_id,
        filename=extraction.filename,
        clauses=clauses,
        metadata=extraction.doc_metadata,
        created_at=extraction.created_at
    )


@router.get(
    "/extractions",
    response_model=ExtractionListResponse
)
def list_extractions(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """
    List all contract extractions with pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)
    
    Returns paginated list of all extractions.
    """
    result = extraction_service.list_extractions(db, page=page, page_size=page_size)
    
    # Convert extractions to response models
    extractions = []
    for extraction in result["extractions"]:
        clauses = [Clause(**clause) for clause in extraction.clauses]
        extractions.append(
            ExtractionResponse(
                document_id=extraction.document_id,
                filename=extraction.filename,
                clauses=clauses,
                metadata=extraction.doc_metadata,
                created_at=extraction.created_at
            )
        )
    
    return ExtractionListResponse(
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        extractions=extractions
    )
