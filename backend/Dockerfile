FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Verify SQLite version
RUN sqlite3 --version

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p files data/vectorstore

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]