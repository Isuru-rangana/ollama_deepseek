from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from ..core.ollama_client import ollama_client
from ..models.request_models import GenerateRequest
from ..models.response_models import GenerateResponse, ModelInfoResponse
from ..core.config import settings
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")

@router.get("/")
def read_root():
    return {"message": "Welcome to Ollama DeepSeek API"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "service": "deepseek-coder-api",
            "environment": os.getenv("CHOREO_ENV", "local"),
            "ollama_url": settings.OLLAMA_API_BASE_URL,
            "model": settings.OLLAMA_MODEL_NAME
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@router.post("/generate", response_model=GenerateResponse)
async def generate_code(request: GenerateRequest):
    """
    Generate code using DeepSeek Coder
    """
    try:
        response = await ollama_client.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return GenerateResponse(
            generated_code=response.get("response", ""),
            model=response.get("model", ""),
            total_duration=response.get("total_duration", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model", response_model=ModelInfoResponse)
async def get_model_info():
    """
    Get information about the loaded model
    """
    try:
        response = await ollama_client.get_model_info()
        return ModelInfoResponse(
            model_name=ollama_client.model,
            status="loaded",
            details=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 