# Use official Python image
FROM python:3.12-slim

# Set work directory inside container
WORKDIR /app

# Copy server code
COPY server/ ./server/

# Copy frontend static files
COPY frontend/ ./frontend/

# Install dependencies
RUN pip install --no-cache-dir -r server/requirements.txt

# Expose port Flask will run on
EXPOSE 5000

# Use Gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server.app:app"]
