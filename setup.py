#!/usr/bin/env python3
"""
Setup script to install all Phase 1 and Phase 2 dependencies
Installs everything in D:\ drive Python packages folder
"""

import subprocess
import sys
import os

# Set Python packages path to D:\ drive
PYTHON_PACKAGES_PATH = "D:\\PythonPackages"
PIP_TARGET_PATH = os.path.join(PYTHON_PACKAGES_PATH, "lib")

def setup_python_path():
    """Setup Python path for D:\ drive installation"""
    # Create directories if they don't exist
    os.makedirs(PIP_TARGET_PATH, exist_ok=True)
    
    # Also create models cache directory
    models_cache_path = os.path.join(PYTHON_PACKAGES_PATH, "models_cache")
    os.makedirs(models_cache_path, exist_ok=True)
    
    # Add to Python path
    if PIP_TARGET_PATH not in sys.path:
        sys.path.insert(0, PIP_TARGET_PATH)
    
    # Set environment variables for pip and models
    os.environ['PYTHONPATH'] = PIP_TARGET_PATH
    os.environ['TRANSFORMERS_CACHE'] = models_cache_path
    os.environ['TORCH_HOME'] = models_cache_path
    os.environ['XDG_CACHE_HOME'] = models_cache_path
    
    print(f"📁 Python packages will be installed to: {PIP_TARGET_PATH}")
    print(f"📁 AI models will be cached to: {models_cache_path}")

def download_ai_models():
    """Download AI models to D:\ drive"""
    print("\n🤖 Downloading AI Models to D:\\ drive...")
    
    # Download Whisper model
    try:
        print("\n   📥 Downloading Whisper base model...")
        import whisper
        model = whisper.load_model("base")
        print("   ✓ Whisper base model downloaded successfully")
    except Exception as e:
        print(f"   ✗ Failed to download Whisper model: {e}")
    
    # Download FLAN-T5 model
    try:
        print("\n   📥 Downloading FLAN-T5 small model...")
        from transformers import T5ForConditionalGeneration, T5Tokenizer
        
        # Download small model first (faster)
        tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
        model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")
        print("   ✓ FLAN-T5 small model downloaded successfully")
        
        # Optionally download large model
        print("\n   📥 Downloading FLAN-T5 large model (this may take a while)...")
        tokenizer_large = T5Tokenizer.from_pretrained("google/flan-t5-large")
        model_large = T5ForConditionalGeneration.from_pretrained("google/flan-t5-large")
        print("   ✓ FLAN-T5 large model downloaded successfully")
        
    except Exception as e:
        print(f"   ✗ Failed to download FLAN-T5 model: {e}")
    
    print("\n✅ Model downloads complete!")

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n🔧 {description}")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, env=os.environ)
        if result.returncode == 0:
            print(f"   ✓ {description} - SUCCESS")
            if result.stdout:
                print(f"   Output: {result.stdout[:200]}..." if len(result.stdout) > 200 else f"   Output: {result.stdout}")
            return True
        else:
            print(f"   ✗ {description} - FAILED")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ✗ {description} - FAILED: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI Social Media Post Generator - Phase 1 & 2 Setup")
    print("=" * 60)
    
    # Setup Python path for D:\ drive installation
    setup_python_path()
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Install Python dependencies to D:\ drive
    python_deps = [
        "flask==2.3.3",
        "flask-cors==4.0.0",
        "python-dotenv==1.0.0",
        "openai-whisper",
        "transformers",
        "torch",
        "librosa",
        "pydub",
        "numpy<2.0.0",  # Fix numpy compatibility
        "requests",
        "werkzeug",
        "soundfile",
        "scipy"
    ]
    
    print("\n📦 Installing Python Dependencies to D:\\ drive...")
    for dep in python_deps:
        # Use pip with --target to install to D:\ drive
        pip_command = f"pip install --target \"{PIP_TARGET_PATH}\" --upgrade {dep}"
        success = run_command(pip_command, f"Installing {dep} to D:\\ drive")
        if not success:
            print(f"⚠️  Failed to install {dep}, continuing...")
    
    # Test installations
    print("\n🧪 Testing Python Installations...")
    test_imports = [
        "flask",
        "flask_cors",
        "whisper",
        "transformers",
        "torch",
        "librosa",
        "pydub"
    ]
    
    successful_imports = 0
    for module in test_imports:
        try:
            __import__(module)
            print(f"   ✓ {module} imported successfully")
            successful_imports += 1
        except ImportError as e:
            print(f"   ✗ {module} import failed: {e}")
    
    # Download AI models if imports were successful
    if successful_imports >= 6:  # Most imports successful
        download_ai_models()
    else:
        print("\n⚠️  Skipping model downloads due to import failures")
    
    # Check if Node.js is available
    print("\n🟢 Checking Node.js...")
    node_available = run_command("node --version", "Node.js version check")
    npm_available = run_command("npm --version", "npm version check")
    
    if node_available and npm_available:
        print("\n📦 Installing Frontend Dependencies...")
        os.chdir("frontend")
        run_command("npm install", "Installing React dependencies")
        os.chdir("..")
    else:
        print("\n⚠️  Node.js/npm not found. Please install Node.js manually.")
    
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Test the setup: python backend/quick_model_test.py")
    print("2. Run full tests: python backend/test_phase_1_2.py")
    print("3. Start backend: python backend/app.py")
    print("4. Start frontend: cd frontend && npm start")
    print("=" * 60)

if __name__ == "__main__":
    main()
