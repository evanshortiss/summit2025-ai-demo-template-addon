FROM registry.access.redhat.com/ubi8/python-39@sha256:49118ed4ee77feab76867aa49cbadbedc02cfee9a6fdca70caf7f3a05b64b897

LABEL maintainer="${{ values.owner }}"
LABEL description="${{ values.description }}"

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8080

# Run the application
CMD ["python", "main.py"] 