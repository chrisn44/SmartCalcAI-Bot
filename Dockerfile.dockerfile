FROM python:3.11-slim

# Install system dependencies for OCR and OpenCV
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libleptonica-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Verify tesseract installation
RUN tesseract --version

# Set Tesseract path
ENV TESSERACT_PATH=/usr/bin/tesseract
ENV PATH="/usr/bin:${PATH}"

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Make start script executable
RUN chmod +x start.sh 2>/dev/null || echo "start.sh not found, will use default"

# Test tesseract after installation
RUN python -c "import pytesseract; print(f'✅ Tesseract path: {pytesseract.pytesseract.tesseract_cmd}')" || echo "⚠️ Tesseract test failed but continuing"

# Use supervisor if available, otherwise run bot directly
CMD if [ -f "bot_supervisor.py" ]; then \
        echo "🚀 Starting bot with supervisor..."; \
        python bot_supervisor.py; \
    else \
        echo "🚀 Starting bot directly..."; \
        python bot.py; \
    fi
