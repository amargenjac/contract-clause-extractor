import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import io

from app.main import app
from app.core.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_extractions_empty():
    """Test listing extractions when database is empty"""
    response = client.get("/api/extractions")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "extractions" in data
    assert isinstance(data["extractions"], list)


def test_get_extraction_not_found():
    """Test getting non-existent extraction"""
    response = client.get("/api/extractions/non-existent-id")
    assert response.status_code == 404


def test_extract_invalid_file_type():
    """Test extraction with invalid file type"""
    files = {"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
    response = client.post("/api/extract", files=files)
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]
