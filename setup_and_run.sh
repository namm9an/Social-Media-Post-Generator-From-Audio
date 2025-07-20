#!/bin/bash

# ============================================================
# AI Social Media Post Generator – Environment & Runner
# Creates Python virtualenv, installs deps, then starts back & front
# ============================================================

set -e  # Exit on any error

# Function to handle errors
handle_error() {
    echo ""
    echo "ERROR occurred during setup. Verify Python/Node installations."
    exit 1
}

# Set error handler
trap handle_error ERR

# Change to project root (directory containing this script)
PROJECT_ROOT="$(dirname "$(realpath "$0")")"
cd "$PROJECT_ROOT" || exit 1

echo "============================================================"
echo "AI Social Media Post Generator – Environment & Runner"
echo "Project root: $PROJECT_ROOT"
echo "============================================================"

# ------------------------------------------------------------
# 1. Python virtual environment
# ------------------------------------------------------------
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment in .venv ..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install root + backend requirements
if [ -f "requirements.txt" ]; then
    echo "Installing root requirements..."
    python -m pip install -r requirements.txt
fi

if [ -f "backend/requirements.txt" ]; then
    echo "Installing backend requirements..."
    python -m pip install -r backend/requirements.txt
fi

# ------------------------------------------------------------
# 2. Node dependencies (frontend)
# ------------------------------------------------------------
if [ -d "frontend" ]; then
    echo "Setting up frontend dependencies..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "Installing React dependencies ..."
        npm install
    fi
    
    cd ..
fi

# ------------------------------------------------------------
# 3. Set environment variables for model caching
# ------------------------------------------------------------
export TRANSFORMERS_CACHE="$HOME/.cache/transformers"
export TORCH_HOME="$HOME/.cache/torch"
export XDG_CACHE_HOME="$HOME/.cache"

# Create cache directories
mkdir -p "$TRANSFORMERS_CACHE"
mkdir -p "$TORCH_HOME"

echo ""
echo "Environment setup complete!"
echo ""

# ------------------------------------------------------------
# 4. Launch backend in background
# ------------------------------------------------------------
echo "Starting backend server in background..."
cd backend
source ../venv/bin/activate 2>/dev/null || source ../.venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

echo "Backend started with PID: $BACKEND_PID"
echo "Backend available at: http://localhost:5000"

# ------------------------------------------------------------
# 5. Launch frontend
# ------------------------------------------------------------
if [ -d "frontend" ]; then
    echo ""
    echo "Starting frontend development server..."
    echo "Frontend will be available at: http://localhost:3000"
    echo ""
    
    cd frontend
    
    # Function to cleanup background processes
    cleanup() {
        echo ""
        echo "Shutting down servers..."
        if [ ! -z "$BACKEND_PID" ]; then
            kill $BACKEND_PID 2>/dev/null || true
        fi
        exit 0
    }
    
    # Set cleanup trap
    trap cleanup INT TERM
    
    # Start frontend (this will block)
    npm start
else
    echo "Frontend directory not found. Backend is running at http://localhost:5000"
    echo "Press Ctrl+C to stop the backend server..."
    
    # Wait for interrupt
    trap 'kill $BACKEND_PID 2>/dev/null || true; echo "Backend stopped."; exit 0' INT TERM
    wait $BACKEND_PID
fi
