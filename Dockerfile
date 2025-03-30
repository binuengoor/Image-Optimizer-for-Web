FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV DEBUG=False

# Expose the application port
EXPOSE 3756

# Run the application
CMD ["python", "script.py"]