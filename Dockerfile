# Use Python 3.11-slim as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application code into the container
RUN echo "Copying content from current directory to app"
COPY . /app

# Install system dependencies and PostgreSQL client
RUN echo "Updating apt-get and cleaning..." && \
    apt-get update && \
    apt-get clean 

# Install Python dependencies
RUN echo "Installing Python dependencies..." && \
    pip install --upgrade pip &&\ 
    pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5000

# Set environment variables for Flask/Quart
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Quart application
CMD echo "Starting the Quart application..." && \
    quart run --host 0.0.0.0
