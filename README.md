# DeepSeek Coder API

A FastAPI-based REST API for DeepSeek Coder using OLLAMA.

## Features

- Code generation using DeepSeek Coder model
- Model information endpoint
- Health check endpoint
- Docker and Docker Compose support
- Production-ready configuration

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

## Quick Start

1. Clone the repository
2. Start the services:
   ```bash
   docker-compose up -d
   ```
3. The API will be available at http://localhost:8000
4. Access the API documentation at http://localhost:8000/docs

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/v1/model` - Get model information
- `POST /api/v1/generate` - Generate code

### Generate Code Example

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to calculate fibonacci numbers",
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

## Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the API locally:
   ```bash
   uvicorn app.main:app --reload
   ```

## Deployment

The application is containerized and ready for deployment to Choreo or any other container orchestration platform.

## Environment Variables

- `OLLAMA_API_BASE_URL` - OLLAMA API base URL (default: http://localhost:11434)
- `OLLAMA_MODEL_NAME` - Model name (default: deepseek-coder)
- `REQUEST_TIMEOUT` - Request timeout in seconds (default: 300)
- `RATE_LIMIT_PER_MINUTE` - Rate limit per minute (default: 60)

## License

MIT 