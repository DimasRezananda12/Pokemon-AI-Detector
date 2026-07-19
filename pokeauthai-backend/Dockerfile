FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for OpenCV and EasyOCR
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download and cache EasyOCR model during build (optional, saves time on startup)
# RUN python -c "import easyocr; easyocr.Reader(['en'], gpu=False)"

COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
