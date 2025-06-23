from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .core.config import settings
import os

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

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "deepseek-coder-api",
        "environment": os.getenv("CHOREO_ENV", "local")
    }

# Add Choreo-specific startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    - Validates environment variables
    - Checks OLLAMA connectivity
    """
    required_vars = ["OLLAMA_API_BASE_URL", "OLLAMA_MODEL_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Log startup information
    print(f"Starting API with OLLAMA URL: {settings.OLLAMA_API_BASE_URL}")
    print(f"Model name: {settings.OLLAMA_MODEL_NAME}")
    print(f"Environment: {os.getenv('CHOREO_ENV', 'local')}") 