#!/bin/bash

# Production startup script for Product Listing System

echo "🚀 Starting Product Listing System in Production Mode"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads

# Set environment variables
export DATABASE_URL="${DATABASE_URL:-sqlite:///./product_listing.db}"
export DEBUG="False"

# Start the application with Gunicorn
echo "🌟 Starting FastAPI application with Gunicorn..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 Swagger UI will be available at: http://localhost:8000/docs"
echo ""

gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --access-logfile - --error-logfile -

