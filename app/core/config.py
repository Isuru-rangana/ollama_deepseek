from pydantic_settings import BaseSettings
from typing import Optional
import os
import socket
import logging

logger = logging.getLogger(__name__)

def get_host_ip():
    """Get the host IP address for local development"""
    try:
        # Try to get the host IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host_ip = s.getsockname()[0]
        s.close()
        return f"http://{host_ip}:11434"
    except:
        # Fallback to localhost
        return "http://127.0.0.1:11434"

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DeepSeek Coder API"
    
    # OLLAMA Configuration
    OLLAMA_API_BASE_URL: str = os.getenv(
        "OLLAMA_API_BASE_URL",
        get_host_ip()
    )
    MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-coder")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    
    # Request Configuration
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    class Config:
        case_sensitive = True

    def validate_settings(self):
        """Validate and adjust settings based on environment"""
        logger.info(f"Using OLLAMA API URL: {self.OLLAMA_API_BASE_URL}")
        logger.info(f"Using model: {self.MODEL_NAME}")
        return self

settings = Settings().validate_settings() 