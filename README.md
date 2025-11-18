# Contract Clause Extractor

A FastAPI service that extracts and structures key clauses from legal contracts using LLM APIs (OpenAI GPT or Google Gemini).

## Features

- **PDF Processing**: Extracts text from PDF contract documents
- **Multi-LLM Support**: Choose between OpenAI GPT or Google Gemini for clause extraction
- **Structured Output**: Uses OpenAI's structured output API with Pydantic models for reliable parsing
- **RESTful API**: Easy-to-use endpoints for extraction and retrieval
- **Database Storage**: Stores extraction results for later retrieval
- **Pagination**: List all extractions with pagination support
- **Comprehensive Logging**: Detailed logging with file rotation for debugging and monitoring
- **Type Safety**: Full type hints and Pydantic validation throughout

## API Endpoints

### 1. Extract Contract Clauses
**POST** `/api/extract`

Accepts a PDF contract document and returns structured JSON with extracted clauses.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file upload
- Query Parameters:
  - `provider` (optional): LLM provider to use - `"openai"` or `"gemini"` (default: `"openai"`)

**Example:**
```bash
# Using OpenAI (default)
curl -X POST "http://localhost:8000/api/extract" \
  -F "file=@contract.pdf"

# Using Gemini
curl -X POST "http://localhost:8000/api/extract?provider=gemini" \
  -F "file=@contract.pdf"
```

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
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-2024-08-06

# Gemini API configuration (optional)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-flash

# Logging configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# API configuration
API_TITLE=Contract Clause Extractor API
API_VERSION=1.0.0
```

**Note:** You need at least one API key (OpenAI or Gemini) to use the service. The provider parameter in the API request determines which one to use.

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

## Logging

The application includes comprehensive logging:

- **Console Output**: Simple formatted logs to stdout
- **File Logs**: Detailed logs saved to `logs/app.log` (rotating, 10MB max, 5 backups)
- **Error Logs**: Errors and above saved to `logs/errors.log`

Log levels can be configured via the `LOG_LEVEL` environment variable.

## Project Structure

```
contract-clause-extractor/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── database.py       # Database setup
│   │   └── logging_config.py # Logging configuration
│   ├── models/
│   │   └── extraction.py    # SQLAlchemy models
│   ├── schemas/
│   │   └── extraction.py    # Pydantic schemas (including ClauseExtractionResponse)
│   ├── services/
│   │   ├── pdf_processor.py       # PDF text extraction
│   │   ├── llm_service.py         # LLM clause extraction (OpenAI & Gemini)
│   │   └── extraction_service.py # Orchestration service
│   └── routers/
│       └── extraction.py    # API endpoints
├── tests/
│   └── test_api.py         # API tests
├── logs/                   # Application logs (auto-created)
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Potential Future Enhancements

### High Priority
- [ ] **Batch Processing**: Support for processing multiple PDFs in a single request
- [ ] **Async Processing**: Background job queue for long-running extractions with status polling
- [ ] **Export Formats**: Export extracted clauses to CSV, Excel, or Word documents
- [ ] **Clause Templates**: Pre-defined clause type templates for different contract types (employment, NDA, etc.)
- [ ] **Comparison Tool**: Compare clauses across multiple contracts
- [ ] **Search & Filter**: Advanced search and filtering capabilities for stored extractions

### Low Priority / Nice to Have
- [ ] **Additional LLM Providers**: Support for Anthropic Claude, Cohere, or other providers
- [ ] **Custom Models**: Fine-tuned models for specific contract types
- [ ] **Contract Templates**: Generate contracts from extracted clause templates
- [ ] **Compliance Checking**: Check contracts against regulatory requirements
- [ ] **Smart Suggestions**: AI-powered suggestions for missing clauses
- [ ] **Integration APIs**: Pre-built integrations with contract management systems

### Technical Improvements
- [ ] **Caching Layer**: Redis caching for frequently accessed extractions
- [ ] **Database Migration**: Migrations for schema changes
- [ ] **Performance Optimization**: Optimize PDF processing for large documents
- [ ] **CI/CD Pipeline**: Automated testing and deployment
- [ ] **API Versioning**: Support for multiple API versions

## License

MIT