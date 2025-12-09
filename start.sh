#!/bin/bash

# IaC Factory GUI Startup Script

echo "🚀 Starting IaC Factory GUI..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -q -r gui/backend/requirements.txt

echo ""
echo "✨ Starting server on http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

# Start the server using the run script
python run_gui.py
