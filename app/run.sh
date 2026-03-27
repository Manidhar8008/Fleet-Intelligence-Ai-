#!/bin/bash

# Fleet Intelligence AI - Run Script
# Production-ready startup script with safety checks

set -e  # Exit on error

echo "🚀 Fleet Intelligence AI - Starting..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

echo "✓ Python version: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null
pip install -r requirements.txt > /dev/null

# Check for sample data
if [ ! -f "data/sample_fleet.csv" ]; then
    echo "⚠️  Sample data not found at data/sample_fleet.csv"
    echo "   You can upload data via the Streamlit interface or add sample_fleet.csv"
fi

# Run Streamlit app
echo "🎯 Launching Streamlit application..."
echo "   Opening at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run main.py --logger.level=info
