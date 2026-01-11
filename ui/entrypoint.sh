#!/bin/bash
set -e

echo "Starting UI Service..."

# Set Python path to include the project root
export PYTHONPATH="/app:$PYTHONPATH"

# Change to the ui directory
cd /app/ui

echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8080 --reload
