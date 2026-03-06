FROM python:3.11-slim

# Update package list and install system dependencies
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
    && rm -rf /var/lib/apt/lists/*

# Verify tesseract installation
RUN tesseract --version

# Set Tesseract path
ENV TESSERACT_PATH=/usr/bin/tesseract
ENV PATH="/usr/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Test tesseract after installation
RUN python -c "import pytesseract; print(f'Tesseract path: {pytesseract.pytesseract.tesseract_cmd}')"

CMD ["python", "bot.py"]
