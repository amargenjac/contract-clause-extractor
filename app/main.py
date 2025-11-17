from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging_config import setup_logging
from app.routers import extraction

# Setup logging
setup_logging()

# Import logger after setup
from app.core.logging_config import get_logger
logger = get_logger(__name__)

# Create database tables
logger.info("Creating database tables if they don't exist")
Base.metadata.create_all(bind=engine)
logger.info("Database tables ready")

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)
logger.info(f"FastAPI application initialized: {settings.api_title} v{settings.api_version}")

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
    logger.debug("Root endpoint accessed")
    return {
        "status": "ok",
        "service": settings.api_title,
        "version": settings.api_version
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy"}
