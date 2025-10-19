#!/bin/bash

# Virtual environment setup script for Product Listing System

echo "🔧 Setting up Product Listing System Development Environment"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version is installed, but Python $required_version or higher is required."
    exit 1
fi

echo "✅ Python $python_version is installed"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Set up environment file
echo "⚙️ Setting up environment file..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "📝 Created .env file from template. Please review and update as needed."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To start the development server:"
echo "  ./scripts/start_dev.sh"
echo ""
echo "To run tests:"
echo "  python run_tests.py"
echo ""
echo "To start with Docker:"
echo "  docker-compose up -d"

