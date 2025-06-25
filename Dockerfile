# Stage 1: Build Ollama
FROM ubuntu:22.04 as ollama

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Stage 2: Python API Service
FROM python:3.9-slim

# Install Ollama
COPY --from=ollama /usr/local/bin/ollama /usr/local/bin/ollama

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app .

# Create directory for Ollama models
RUN mkdir -p /root/.ollama

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose ports
EXPOSE 8080 11434

# Start both services
CMD ["/start.sh"] 