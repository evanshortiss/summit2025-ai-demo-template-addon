FROM registry.redhat.io/ubi9/python-39@sha256:2ad08a50ddfa773d508f225a101395c271f315af88dba8ad2203f2fe22683e40

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