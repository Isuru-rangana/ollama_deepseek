# Development stage
FROM python:3.9-slim AS development

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the application code
COPY . .

# Run tests
CMD ["python3", "-m", "pytest", "tests/", "-v"]

# Production stage
FROM python:3.9-slim AS production

WORKDIR /app

# Copy only the necessary files for production
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# Create a new user with UID 10016 (Choreo requirement)
RUN groupadd -g 10016 choreo && \
    useradd -u 10016 -g choreo -s /bin/bash -m choreouser

# Switch to the new user
USER 10016

EXPOSE 8000

# Start the FastAPI application
CMD ["python", "main.py"] 