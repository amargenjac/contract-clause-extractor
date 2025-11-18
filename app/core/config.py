from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    database_url: str = "sqlite:///./contract_extractions.db"
    
    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1"
    
    # Gemini settings
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    
    # API settings
    api_title: str = "Contract Clause Extractor API"
    api_version: str = "1.0.0"
    api_description: str = "API for extracting and structuring key clauses from legal contracts"
    
    # Logging settings
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
