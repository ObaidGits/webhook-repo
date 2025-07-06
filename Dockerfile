# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy code EXCLUDING .env
COPY server/ ./server/
COPY frontend/ ./frontend/

# Install dependencies
RUN pip install --no-cache-dir -r server/requirements.txt

# Expose port
EXPOSE 5000

# Production server with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server.app:app"]
