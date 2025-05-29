# Start with Python 3.12
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# COPY requirements file FIRST
COPY requirements.txt .

# THEN install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and env file
COPY app/ ./app/
COPY .env .

# Expose port for API
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]