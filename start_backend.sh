#!/bin/bash

echo "======================================"
echo "Starting AI Social Media Post Generator Backend"
echo "======================================"

# Navigate to backend directory (relative to script location)
PROJECT_ROOT="$(dirname "$(realpath "$0")")"
cd "$PROJECT_ROOT/backend" || {
    echo "Error: Could not change to backend directory"
    exit 1
}

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found at .venv/bin/activate"
    echo "Please run setup.sh first to create the virtual environment"
    exit 1
fi

# Set Python path to include current directory
export PYTHONPATH=.:$PYTHONPATH

echo ""
echo "Starting Flask backend server..."
echo "Backend will be available at: http://localhost:5000"
echo ""

# Start the application
python app.py

# Keep terminal open on error (bash equivalent of pause)
if [ $? -ne 0 ]; then
    echo "Press any key to continue..."
    read -n 1 -s -r
fi
