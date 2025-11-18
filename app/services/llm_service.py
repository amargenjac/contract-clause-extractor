from typing import List, Dict, Any, Literal
import json
from openai import OpenAI
import google.generativeai as genai

from app.core.config import settings
from app.core.logging_config import get_logger
from app.schemas.extraction import ClauseExtractionResponse

logger = get_logger(__name__)

Provider = Literal["openai", "gemini"]


class LLMService:
    """Service for extracting clauses using LLM"""
    
    def __init__(self, provider: Provider = "openai"):
        """
        Initialize LLM service with specified provider
        
        Args:
            provider: LLM provider to use ("openai" or "gemini")
        """
        self.provider = provider
        logger.info(f"Initializing LLM service with provider: {provider}")
        
        if provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
            self.model = settings.openai_model
            if not settings.openai_api_key:
                logger.warning("OpenAI API key not provided, will use mock extraction")
            else:
                logger.debug(f"OpenAI client initialized with model: {self.model}")
        elif provider == "gemini":
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                self.client = genai.GenerativeModel(settings.gemini_model)
                logger.debug(f"Gemini client initialized with model: {settings.gemini_model}")
            else:
                self.client = None
                logger.warning("Gemini API key not provided, will use mock extraction")
            self.model = settings.gemini_model
        else:
            logger.error(f"Unsupported provider: {provider}")
            raise ValueError(f"Unsupported provider: {provider}")
    
    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract clauses from contract text using LLM
        
        Args:
            text: Contract text to analyze
            
        Returns:
            List of extracted clauses with their types and content
        """
        text_length = len(text)
        logger.info(f"Starting clause extraction with {self.provider} (text length: {text_length} chars)")
        
        if not self.client:
            logger.warning("No API client available, using mock extraction")
            return self._mock_extraction(text)
        
        prompt = self._create_extraction_prompt(text)
        logger.debug(f"Created extraction prompt (length: {len(prompt)} chars)")
        
        try:
            if self.provider == "openai":
                clauses = self._extract_with_openai(prompt)
            elif self.provider == "gemini":
                clauses = self._extract_with_gemini(prompt)
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            logger.info(f"Successfully extracted {len(clauses)} clauses using {self.provider}")
            logger.debug(f"Extracted clause types: {[c.get('clause_type') for c in clauses]}")
            return clauses
        except Exception as e:
            logger.error(f"Error calling {self.provider} API: {str(e)}", exc_info=True)
            raise ValueError(f"Error calling LLM API: {str(e)}")
    
    def _extract_with_openai(self, prompt: str) -> List[Dict[str, Any]]:
        """Extract clauses using OpenAI with structured output"""
        logger.debug(f"Calling OpenAI API with structured output, model: {self.model}")
        # Use OpenAI's structured output feature with Pydantic model
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": "You are a legal document analyzer. Extract and categorize clauses from contracts."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            text_format=ClauseExtractionResponse,
            temperature=0.3,
        )
        
        # Get parsed output from structured response
        extraction_result = response.output_parsed
        logger.debug(f"OpenAI structured response received: {len(extraction_result.clauses)} clauses")
        
        # Convert Pydantic models to dictionaries
        clauses = [clause.model_dump() for clause in extraction_result.clauses]
        logger.debug(f"Converted {len(clauses)} clauses to dictionary format")
        
        return clauses
    
    def _extract_with_gemini(self, prompt: str) -> List[Dict[str, Any]]:
        """Extract clauses using Gemini"""
        logger.debug(f"Calling Gemini API with model: {self.model}")
        try:
            # Use JSON format prompt for Gemini
            json_prompt = self._create_extraction_prompt_json(prompt.split("Contract text:")[1] if "Contract text:" in prompt else prompt)
            full_prompt = f"""You are a legal document analyzer. Extract and categorize clauses from contracts.

{json_prompt}"""
            
            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.3,
                }
            )
            
            result = response.text
            logger.debug(f"Gemini response received (length: {len(result)} chars)")
            
            # Log token usage if available
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                logger.debug(f"Gemini token usage - prompt: {usage.prompt_token_count}, completion: {usage.candidates_token_count}, total: {usage.total_token_count}")
            
            clauses = self._parse_llm_response(result)
            return clauses
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}", exc_info=True)
            raise
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create prompt for LLM clause extraction"""
        return f"""Analyze the following legal contract and extract all key clauses.
For each clause, provide:
1. clause_type: The category of the clause (e.g., "Payment Terms", "Confidentiality", "Termination", "Liability", "Governing Law", etc.)
2. content: The actual text of the clause
3. page_number: The page number where the clause appears (if mentioned in the text)

Contract text:
{text}
"""
    
    def _create_extraction_prompt_json(self, text: str) -> str:
        """Create prompt for LLM clause extraction with JSON format instructions (for Gemini)"""
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
                logger.debug(f"Successfully parsed {len(clauses)} clauses from LLM response")
                return clauses
            else:
                # If no valid JSON found, return empty list
                logger.warning("No valid JSON array found in LLM response")
                logger.debug(f"Response preview: {response[:200]}...")
                return []
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return empty list
            logger.warning(f"JSON parsing failed: {str(e)}")
            logger.debug(f"Response that failed to parse: {response[:500]}...")
            return []
    
    def _mock_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Mock extraction for testing without API key"""
        logger.warning("Using mock extraction (no API key available)")
        # Simple mock that creates a few sample clauses
        words = text.split()[:100]  # Take first 100 words
        mock_clauses = [
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
        logger.debug(f"Mock extraction generated {len(mock_clauses)} clauses")
        return mock_clauses
