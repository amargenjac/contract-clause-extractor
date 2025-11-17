"""
Example script demonstrating how to use the Contract Clause Extractor API
"""
import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"


def test_health():
    """Test the health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.json()}")
    return response.status_code == 200


def extract_contract(pdf_path):
    """
    Upload and extract clauses from a PDF contract
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        dict: Extraction result with document_id, clauses, and metadata
    """
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        response = requests.post(f"{BASE_URL}/api/extract", files=files)
    
    if response.status_code == 201:
        result = response.json()
        print(f"\n✓ Extraction successful!")
        print(f"  Document ID: {result['document_id']}")
        print(f"  Filename: {result['filename']}")
        print(f"  Clauses found: {len(result['clauses'])}")
        print(f"  Pages: {result['metadata']['page_count']}")
        
        print("\n  Extracted Clauses:")
        for i, clause in enumerate(result['clauses'], 1):
            print(f"    {i}. {clause['clause_type']}")
            print(f"       Page: {clause.get('page_number', 'N/A')}")
            print(f"       Content preview: {clause['content'][:100]}...")
        
        return result
    else:
        print(f"✗ Extraction failed: {response.json()}")
        return None


def get_extraction(document_id):
    """
    Retrieve a specific extraction by document ID
    
    Args:
        document_id: The unique document identifier
        
    Returns:
        dict: Extraction result
    """
    response = requests.get(f"{BASE_URL}/api/extractions/{document_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Retrieved extraction for: {result['filename']}")
        return result
    else:
        print(f"✗ Failed to retrieve extraction: {response.json()}")
        return None


def list_extractions(page=1, page_size=10):
    """
    List all extractions with pagination
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        dict: List of extractions with pagination info
    """
    response = requests.get(
        f"{BASE_URL}/api/extractions",
        params={'page': page, 'page_size': page_size}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Found {result['total']} extractions")
        print(f"  Showing page {result['page']} (size: {result['page_size']})")
        
        for extraction in result['extractions']:
            print(f"  - {extraction['filename']} (ID: {extraction['document_id'][:8]}...)")
        
        return result
    else:
        print(f"✗ Failed to list extractions: {response.json()}")
        return None


def main():
    """Main example workflow"""
    print("=== Contract Clause Extractor API Example ===\n")
    
    # 1. Check health
    print("1. Checking API health...")
    if not test_health():
        print("API is not healthy. Please start the server.")
        return
    
    # 2. Extract from a PDF (you need to provide a real PDF path)
    # Uncomment and modify the path below to test with your own PDF:
    # print("\n2. Extracting clauses from PDF...")
    # result = extract_contract("/path/to/your/contract.pdf")
    # if result:
    #     document_id = result['document_id']
    #     
    #     # 3. Retrieve the extraction
    #     print("\n3. Retrieving extraction...")
    #     get_extraction(document_id)
    
    # 4. List all extractions
    print("\n4. Listing all extractions...")
    list_extractions()
    
    print("\n=== Example complete ===")


if __name__ == "__main__":
    main()
