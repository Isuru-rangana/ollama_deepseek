from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Constants - Read from environment variables with defaults
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "deepseek-coder")
TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))

# Log startup configuration
logger.info(f"Starting service with configuration:")
logger.info(f"Ollama API URL: {OLLAMA_API_BASE_URL}")
logger.info(f"Model Name: {MODEL_NAME}")
logger.info(f"Timeout: {TIMEOUT_SECONDS} seconds")

class GenerateRequest(BaseModel):
    prompt: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{OLLAMA_API_BASE_URL}/api/tags")
            if response.status_code != 200:
                logger.error(f"Ollama health check failed: Status {response.status_code}, Response: {response.text}")
                return {
                    "status": "unhealthy",
                    "service": "deepseek-coder-api",
                    "ollama": {
                        "url": OLLAMA_API_BASE_URL,
                        "status": "disconnected",
                        "error": response.text
                    }
                }
            return {
                "status": "healthy",
                "service": "deepseek-coder-api",
                "ollama": {
                    "url": OLLAMA_API_BASE_URL,
                    "status": "connected",
                    "model": MODEL_NAME
                }
            }
    except httpx.TimeoutError:
        logger.error(f"Health check timeout connecting to Ollama at {OLLAMA_API_BASE_URL}")
        return {
            "status": "unhealthy",
            "service": "deepseek-coder-api",
            "ollama": {
                "url": OLLAMA_API_BASE_URL,
                "status": "timeout",
                "error": "Connection timed out"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "deepseek-coder-api",
            "ollama": {
                "url": OLLAMA_API_BASE_URL,
                "status": "error",
                "error": str(e)
            }
        }

@app.post("/generate")
async def generate_code(request: GenerateRequest):
    """Generate code using DeepSeek Coder"""
    try:
        # Log the incoming request
        logger.info(f"Received code generation request")
        logger.debug(f"Prompt: {request.prompt}")  # Debug level for full prompt
        
        # Make request to Ollama
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            logger.info(f"Sending request to Ollama at {OLLAMA_API_BASE_URL}")
            response = await client.post(
                f"{OLLAMA_API_BASE_URL}/api/generate",
                json={
                    "model": MODEL_NAME,
                    "prompt": request.prompt,
                    "stream": False
                }
            )
            
            # Log response status
            logger.info(f"Ollama response status: {response.status_code}")
            
            # Check if response is successful
            if response.status_code != 200:
                logger.error(f"Ollama API error: Status {response.status_code}, Response: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ollama API error: {response.text}"
                )
            
            # Parse the response
            result = response.json()
            
            # Return the generated code
            return {
                "status": "success",
                "model": MODEL_NAME,
                "generated_code": result.get("response", ""),
            }
            
    except httpx.TimeoutError:
        error_msg = f"Request to Ollama timed out after {TIMEOUT_SECONDS} seconds"
        logger.error(error_msg)
        raise HTTPException(
            status_code=504,
            detail=error_msg
        )
    except httpx.RequestError as e:
        error_msg = f"Failed to connect to Ollama at {OLLAMA_API_BASE_URL}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=502,
            detail=error_msg
        )
    except Exception as e:
        error_msg = f"Code generation failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        ) 