#!/bin/bash

# Development startup script for Product Listing System

echo "🚀 Starting Product Listing System in Development Mode"

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
export DATABASE_URL="sqlite:///./product_listing.db"
export DEBUG="True"

# Start the application
echo "🌟 Starting FastAPI application..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 Swagger UI will be available at: http://localhost:8000/docs"
echo "📖 ReDoc will be available at: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

