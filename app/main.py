from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Constants
OLLAMA_API_BASE_URL = "http://ollama:11434"
MODEL_NAME = "deepseek-coder"

class GenerateRequest(BaseModel):
    prompt: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_API_BASE_URL}/api/tags")
            if response.status_code != 200:
                return {
                    "status": "unhealthy",
                    "service": "deepseek-coder-api",
                    "ollama": {
                        "url": OLLAMA_API_BASE_URL,
                        "status": "disconnected"
                    }
                }
            return {
                "status": "healthy",
                "service": "deepseek-coder-api",
                "ollama": {
                    "url": OLLAMA_API_BASE_URL,
                    "status": "connected"
                }
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "deepseek-coder-api",
            "error": str(e)
        }

@app.post("/generate")
async def generate_code(request: GenerateRequest):
    """Generate code using DeepSeek Coder"""
    try:
        # Log the incoming request
        logger.info(f"Received prompt: {request.prompt}")
        
        # Make request to Ollama
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_API_BASE_URL}/api/generate",
                json={
                    "model": MODEL_NAME,
                    "prompt": request.prompt,
                    "stream": False
                },
                timeout=60.0
            )
            
            # Log the raw response
            logger.info(f"Raw response: {response.text}")
            
            # Check if response is successful
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ollama API returned status code {response.status_code}"
                )
            
            # Parse the response
            result = response.json()
            
            # Return the generated code
            return {
                "generated_code": result.get("response", ""),
                "status": "success"
            }
            
    except httpx.TimeoutError:
        logger.error("Request to Ollama timed out")
        raise HTTPException(
            status_code=504,
            detail="Request timed out"
        )
    except httpx.RequestError as e:
        logger.error(f"Request to Ollama failed: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to connect to Ollama: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 