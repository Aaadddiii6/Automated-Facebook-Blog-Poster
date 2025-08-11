#!/bin/bash

# Startup script for Flask application on Render

echo "Starting Makesupabase Backend..."

# Create storage directory if it doesn't exist
mkdir -p ./storage/videos
mkdir -p ./logs

# Set environment variables
export FLASK_ENV=production
export PORT=${PORT:-10000}

# Check if we should use gunicorn config file
if [ -f "gunicorn.conf.py" ]; then
    echo "Using gunicorn configuration file..."
    gunicorn main:create_app() -c gunicorn.conf.py
else
    echo "Using default gunicorn settings..."
    gunicorn main:create_app() --bind 0.0.0.0:$PORT --workers 2 --timeout 120
fi
