from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.config import settings
from app.core.metrics import track_request_metrics
from prometheus_client import make_asgi_app
import os
import logging
import time
import httpx
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DeepSeek Coder API",
    description="REST API for DeepSeek Coder using OLLAMA",
    version="1.0.0"
)

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your Choreo settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging and metrics middleware
@app.middleware("http")
async def log_and_track_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log request
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.2f}s"
    )
    
    # Track metrics
    track_request_metrics(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
        duration=duration
    )
    
    return response

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

async def check_ollama_connection():
    """Check if Ollama service is accessible"""
    max_retries = 5
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(base_url=settings.OLLAMA_API_BASE_URL) as client:
                response = await client.get("/api/tags")
                if response.status_code == 200:
                    return True
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
    
    return False

# Add Choreo-specific startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    - Validates configuration
    - Checks OLLAMA connectivity
    """
    logger.info("Starting DeepSeek Coder API service...")
    
    # Log configuration
    logger.info(f"OLLAMA URL: {settings.OLLAMA_API_BASE_URL}")
    logger.info(f"Model name: {settings.MODEL_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Check Ollama connection
    if await check_ollama_connection():
        logger.info("Successfully connected to Ollama")
        logger.info("Ollama service is accessible")
        logger.info("Service started successfully")
    else:
        logger.error("Failed to connect to Ollama service")
        raise Exception("Ollama service is not accessible") 