# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all files from current directory to container
COPY *.py requirements.txt start.sh /app/

RUN chmod +x start.sh

# Install dependencies if you have a requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script
CMD ["./start.sh"]