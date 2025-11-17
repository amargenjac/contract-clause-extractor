from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import extraction

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(extraction.router)


@app.get("/", tags=["health"])
def read_root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": settings.api_title,
        "version": settings.api_version
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
