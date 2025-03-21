FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app

# Run the API server
CMD ["python", "src/api/server.py"] 