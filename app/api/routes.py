from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from ..core.ollama_client import ollama_client
from ..models.request_models import GenerateRequest
from ..models.response_models import GenerateResponse, ModelInfoResponse

router = APIRouter()

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