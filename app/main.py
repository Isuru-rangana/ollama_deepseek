from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-coder")

app = FastAPI(
    title="DeepSeek Coder API",
    description="REST API for code generation using DeepSeek Coder",
    version="1.0.0"
)

class GenerateRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to DeepSeek Coder API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Try to connect to Ollama
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_API_BASE_URL}/api/tags")
            is_ollama_healthy = response.status_code == 200
    except Exception as e:
        logger.error(f"Ollama health check failed: {str(e)}")
        is_ollama_healthy = False

    health_status = {
        "status": "healthy" if is_ollama_healthy else "unhealthy",
        "service": "deepseek-coder-api",
        "ollama": {
            "url": OLLAMA_API_BASE_URL,
            "status": "connected" if is_ollama_healthy else "disconnected"
        },
        "model": MODEL_NAME
    }

    return health_status if is_ollama_healthy else HTTPException(
        status_code=503,
        detail=health_status
    )

@app.post("/generate")
async def generate_code(request: GenerateRequest):
    """Generate code using DeepSeek Coder"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_API_BASE_URL}/api/generate",
                json={
                    "model": MODEL_NAME,
                    "prompt": request.prompt,
                    "system": request.system_prompt,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens
                    }
                },
                timeout=60.0  # Set timeout to 60 seconds
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error("Request to Ollama timed out")
        raise HTTPException(
            status_code=504,
            detail="Request to code generation service timed out"
        )
    except Exception as e:
        logger.error(f"Code generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Code generation failed: {str(e)}"
        )

@app.get("/model")
async def get_model_info():
    """Get information about the loaded model"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_API_BASE_URL}/api/show",
                json={"name": MODEL_NAME},
                timeout=30.0
            )
            response.raise_for_status()
            return {
                "model_name": MODEL_NAME,
                "status": "loaded",
                "details": response.json()
            }
    except httpx.TimeoutException:
        logger.error("Request to get model info timed out")
        raise HTTPException(
            status_code=504,
            detail="Request to get model info timed out"
        )
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model info: {str(e)}"
        ) 