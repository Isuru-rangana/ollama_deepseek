from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DeepSeek Coder API"
    
    # OLLAMA Configuration
    OLLAMA_API_BASE_URL: str = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL_NAME: str = os.getenv("OLLAMA_MODEL_NAME", "deepseek-coder")
    
    # Timeout settings (in seconds)
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "300"))
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    class Config:
        case_sensitive = True

    def validate_settings(self):
        """Validate critical settings"""
        if not self.OLLAMA_API_BASE_URL:
            raise ValueError("OLLAMA_API_BASE_URL must be set")
        if not self.OLLAMA_MODEL_NAME:
            raise ValueError("OLLAMA_MODEL_NAME must be set")
        return self

settings = Settings().validate_settings() 