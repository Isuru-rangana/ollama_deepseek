from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .api.routes import router as api_router
from .core.config import settings
import os
import logging
import time
import httpx
from pydantic import BaseModel
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DeepSeek Coder API",
    description="REST API for DeepSeek Coder using OLLAMA",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your Choreo settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.2f}s"
    )
    return response

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Environment variables
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "deepseek-coder")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Request model
class GenerateRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048

@app.get("/")
def read_root():
    return {"message": "Welcome to Ollama DeepSeek API"}

@app.get("/health")
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

@app.get("/api/v1/model")
async def get_model_info():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_API_BASE_URL}/api/show", 
                                      params={"name": OLLAMA_MODEL_NAME},
                                      timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate")
async def generate_code(request: GenerateRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_API_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL_NAME,
                    "prompt": request.prompt,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                },
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add Choreo-specific startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    - Validates environment variables
    - Checks OLLAMA connectivity
    """
    logger.info("Starting DeepSeek Coder API service...")
    
    # Validate required environment variables
    required_vars = ["OLLAMA_API_BASE_URL", "OLLAMA_MODEL_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Log startup information
    logger.info(f"OLLAMA URL: {settings.OLLAMA_API_BASE_URL}")
    logger.info(f"Model name: {settings.OLLAMA_MODEL_NAME}")
    logger.info(f"Environment: {os.getenv('CHOREO_ENV', 'local')}")
    logger.info("Service started successfully") 