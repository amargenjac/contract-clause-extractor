from typing import List, Dict, Any
import json
from openai import OpenAI

from app.core.config import settings


class LLMService:
    """Service for extracting clauses using LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.openai_model
    
    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract clauses from contract text using LLM
        
        Args:
            text: Contract text to analyze
            
        Returns:
            List of extracted clauses with their types and content
        """
        if not self.client:
            # Fallback for when no API key is provided
            return self._mock_extraction(text)
        
        prompt = self._create_extraction_prompt(text)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal document analyzer. Extract and categorize clauses from contracts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
            )
            
            result = response.choices[0].message.content
            clauses = self._parse_llm_response(result)
            return clauses
            
        except Exception as e:
            raise ValueError(f"Error calling LLM API: {str(e)}")
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create prompt for LLM clause extraction"""
        return f"""Analyze the following legal contract and extract all key clauses.
For each clause, provide:
1. clause_type: The category of the clause (e.g., "Payment Terms", "Confidentiality", "Termination", "Liability", "Governing Law", etc.)
2. content: The actual text of the clause
3. page_number: The page number where the clause appears (if mentioned in the text)

Return the result as a JSON array of objects with these fields.

Contract text:
{text}

Return only valid JSON in this exact format:
[
  {{
    "clause_type": "string",
    "content": "string",
    "page_number": number or null
  }}
]
"""
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured clauses"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                clauses = json.loads(json_str)
                return clauses
            else:
                # If no valid JSON found, return empty list
                return []
        except json.JSONDecodeError:
            # If JSON parsing fails, return empty list
            return []
    
    def _mock_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Mock extraction for testing without API key"""
        # Simple mock that creates a few sample clauses
        words = text.split()[:100]  # Take first 100 words
        return [
            {
                "clause_type": "General Terms",
                "content": " ".join(words[:30]) if len(words) >= 30 else " ".join(words),
                "page_number": 1
            },
            {
                "clause_type": "Obligations",
                "content": " ".join(words[30:60]) if len(words) >= 60 else " ".join(words[30:]),
                "page_number": 1
            }
        ]
