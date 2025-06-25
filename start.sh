#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for Ollama to start
echo "Waiting for Ollama to start..."
until curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 1
done

# Pull the model
echo "Pulling DeepSeek Coder model..."
ollama pull deepseek-coder

# Start the FastAPI application
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8080 