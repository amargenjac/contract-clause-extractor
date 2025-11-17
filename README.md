# Contract Clause Extractor

A FastAPI service that extracts and structures key clauses from legal contracts using LLM APIs.

## Features

- **PDF Processing**: Extracts text from PDF contract documents
- **LLM-powered Clause Extraction**: Uses OpenAI's GPT models to identify and categorize contract clauses
- **RESTful API**: Easy-to-use endpoints for extraction and retrieval
- **Database Storage**: Stores extraction results for later retrieval
- **Pagination**: List all extractions with pagination support

## API Endpoints

### 1. Extract Contract Clauses
**POST** `/api/extract`

Accepts a PDF contract document and returns structured JSON with extracted clauses.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file upload

**Response:**
```json
{
  "document_id": "uuid",
  "filename": "contract.pdf",
  "clauses": [
    {
      "clause_type": "Payment Terms",
      "content": "The payment shall be made within 30 days...",
      "page_number": 1
    }
  ],
  "metadata": {
    "page_count": 5,
    "extraction_timestamp": "2024-01-01T00:00:00",
    "clause_count": 10
  },
  "created_at": "2024-01-01T00:00:00"
}
```

### 2. Get Extraction by ID
**GET** `/api/extractions/{document_id}`

Retrieve extraction results for a specific document.

**Response:** Same as extract endpoint

### 3. List All Extractions
**GET** `/api/extractions?page=1&page_size=10`

List all extractions with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)

**Response:**
```json
{
  "total": 50,
  "page": 1,
  "page_size": 10,
  "extractions": [...]
}
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/amargenjac/contract-clause-extractor.git
cd contract-clause-extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. Run the application:
```bash
python run.py
# Or using uvicorn directly:
# uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Deployment

You can also run the application using Docker:

```bash
# Build and run with docker-compose
docker-compose up -d

# Or build and run manually
docker build -t contract-extractor .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key contract-extractor
```

## Configuration

Create a `.env` file with the following variables:

```env
# Database configuration
DATABASE_URL=sqlite:///./contract_extractions.db

# OpenAI API configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# API configuration
API_TITLE=Contract Clause Extractor API
API_VERSION=1.0.0
```

## Testing

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

Run tests:
```bash
pytest tests/ -v
```

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## Project Structure

```
contract-clause-extractor/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   └── database.py      # Database setup
│   ├── models/
│   │   └── extraction.py    # SQLAlchemy models
│   ├── schemas/
│   │   └── extraction.py    # Pydantic schemas
│   ├── services/
│   │   ├── pdf_processor.py       # PDF text extraction
│   │   ├── llm_service.py         # LLM clause extraction
│   │   └── extraction_service.py  # Orchestration service
│   └── routers/
│       └── extraction.py    # API endpoints
├── tests/
│   └── test_api.py         # API tests
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## License

MIT