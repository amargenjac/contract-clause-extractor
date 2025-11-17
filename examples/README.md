# API Usage Examples

This directory contains example scripts demonstrating how to use the Contract Clause Extractor API.

## Prerequisites

Before running the examples, make sure:

1. The API server is running:
   ```bash
   python run.py
   ```

2. Install the `requests` library (for Python examples):
   ```bash
   pip install requests
   ```

## Python Example

The `test_api.py` script demonstrates the complete API workflow:

```bash
python examples/test_api.py
```

To extract a real PDF, edit the script and uncomment the extraction section with your PDF path.

## cURL Examples

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

### 2. Extract Clauses from PDF
```bash
curl -X POST http://localhost:8000/api/extract \
  -F "file=@/path/to/contract.pdf"
```

### 3. Get Extraction by ID
```bash
curl http://localhost:8000/api/extractions/{document_id}
```

### 4. List All Extractions
```bash
curl "http://localhost:8000/api/extractions?page=1&page_size=10"
```

## Response Examples

### Extraction Response
```json
{
  "document_id": "uuid-here",
  "filename": "contract.pdf",
  "clauses": [
    {
      "clause_type": "Payment Terms",
      "content": "The Client agrees to pay...",
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

### List Response
```json
{
  "total": 50,
  "page": 1,
  "page_size": 10,
  "extractions": [...]
}
```

## Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can test all endpoints directly in your browser.
