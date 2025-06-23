from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DeepSeek Coder API"
    
    # OLLAMA Configuration
    OLLAMA_API_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_NAME: str = "deepseek-coder"
    
    # Timeout settings (in seconds)
    REQUEST_TIMEOUT: int = 300
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 