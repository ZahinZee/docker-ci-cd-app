FROM python:3.12.3-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# --- Security: create non-root user ---
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port Flask runs on
EXPOSE 3000

# Command to run the application
CMD ["python", "app.py"]
