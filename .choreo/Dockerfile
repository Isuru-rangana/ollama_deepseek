FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user with UID 10016 (Choreo requirement)
RUN groupadd -g 10016 choreo && \
    useradd -u 10016 -g choreo -s /bin/bash -m choreouser

# Copy the application code
COPY app/ .

# Change ownership of the application files
RUN chown -R 10016:10016 /app

# Switch to non-root user using explicit UID (Choreo requirement)
USER 10016

# Expose the port
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 