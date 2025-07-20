#!/usr/bin/env python3
"""
Test script to verify all dependencies are installed correctly
"""

try:
    print("Testing Flask...")
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    print("✅ Flask imports successful")
    
    print("Testing dotenv...")
    from dotenv import load_dotenv
    print("✅ dotenv import successful")
    
    print("Testing PyTorch...")
    import torch
    print(f"✅ PyTorch imported successfully")
    
    print("Testing Transformers...")
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    print("✅ Transformers imported successfully")
    
    print("Testing Whisper...")
    import whisper
    print("✅ Whisper imported successfully")
    
    print("Testing audio libraries...")
    import librosa
    import soundfile as sf
    from pydub import AudioSegment
    print("✅ Audio libraries imported successfully")
    
    print("Testing monitoring libraries...")
    import psutil
    from pythonjsonlogger import jsonlogger
    print("✅ Monitoring libraries imported successfully")
    
    print("Testing Flask extensions...")
    from flask_limiter import Limiter
    from flask_talisman import Talisman
    print("✅ Flask extensions imported successfully")
    
    print("\n🎉 All dependencies installed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
