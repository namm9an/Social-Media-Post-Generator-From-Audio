#!/usr/bin/env python3
"""
Test script to validate core functionality before starting the application.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_file_paths():
    """Test that required directories and files exist."""
    logger.info("Testing file paths...")
    
    # Check uploads directory
    uploads_dir = Path("../uploads")
    if not uploads_dir.exists():
        logger.error(f"Uploads directory not found: {uploads_dir.absolute()}")
        return False
    
    audio_dir = uploads_dir / "audio"
    data_dir = uploads_dir / "data"
    
    if not audio_dir.exists():
        logger.error(f"Audio directory not found: {audio_dir.absolute()}")
        return False
        
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir.absolute()}")
        return False
    
    # Check JSON files exist
    audio_json = data_dir / "audio_files.json"
    transcriptions_json = data_dir / "transcriptions.json"
    
    if not audio_json.exists():
        logger.warning(f"Creating missing audio_files.json")
        with open(audio_json, 'w') as f:
            json.dump({}, f)
    
    if not transcriptions_json.exists():
        logger.warning(f"Creating missing transcriptions.json")
        with open(transcriptions_json, 'w') as f:
            json.dump({}, f)
    
    logger.info("✓ File paths OK")
    return True

def test_imports():
    """Test that all required modules can be imported."""
    logger.info("Testing imports...")
    
    try:
        from services.upload_handler import AudioUploadHandler
        logger.info("✓ Upload handler imported")
    except Exception as e:
        logger.error(f"✗ Upload handler import failed: {e}")
        return False
    
    try:
        from services.whisper_service import WhisperService
        logger.info("✓ Whisper service imported")
    except Exception as e:
        logger.error(f"✗ Whisper service import failed: {e}")
        return False
    
    try:
        from services.text_generation.flan_t5_service import flan_t5_service
        logger.info("✓ FLAN-T5 service imported")
    except Exception as e:
        logger.error(f"✗ FLAN-T5 service import failed: {e}")
        return False
    
    try:
        from services.text_generation.content_processor import ContentProcessor
        logger.info("✓ Content processor imported")
    except Exception as e:
        logger.error(f"✗ Content processor import failed: {e}")
        return False
    
    try:
        from templates.platform_templates import get_template
        logger.info("✓ Platform templates imported")
    except Exception as e:
        logger.error(f"✗ Platform templates import failed: {e}")
        return False
    
    logger.info("✓ All imports OK")
    return True

def test_services_initialization():
    """Test that services can be initialized."""
    logger.info("Testing services initialization...")
    
    try:
        from services.upload_handler import AudioUploadHandler
        upload_handler = AudioUploadHandler(
            upload_folder="../uploads/audio",
            data_folder="../uploads/data"
        )
        logger.info("✓ Upload handler initialized")
    except Exception as e:
        logger.error(f"✗ Upload handler initialization failed: {e}")
        return False
    
    try:
        from services.whisper_service import WhisperService
        whisper_service = WhisperService(model_name="base")
        logger.info("✓ Whisper service initialized")
    except Exception as e:
        logger.error(f"✗ Whisper service initialization failed: {e}")
        return False
    
    logger.info("✓ Services initialization OK")
    return True

def test_existing_data():
    """Test that existing data files can be read."""
    logger.info("Testing existing data...")
    
    try:
        data_dir = Path("../uploads/data")
        
        # Test audio files
        audio_json = data_dir / "audio_files.json"
        with open(audio_json, 'r') as f:
            audio_data = json.load(f)
        logger.info(f"✓ Audio files data loaded ({len(audio_data)} files)")
        
        # Test transcriptions
        transcriptions_json = data_dir / "transcriptions.json"  
        with open(transcriptions_json, 'r') as f:
            transcription_data = json.load(f)
        logger.info(f"✓ Transcriptions data loaded ({len(transcription_data)} transcriptions)")
        
        # Check for file path issues
        for file_id, file_data in audio_data.items():
            file_path = file_data.get('file_path', '')
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
            else:
                logger.info(f"✓ File exists: {os.path.basename(file_path)}")
        
    except Exception as e:
        logger.error(f"✗ Data loading failed: {e}")
        return False
    
    logger.info("✓ Existing data OK")
    return True

def main():
    """Run all tests."""
    logger.info("Starting core functionality tests...")
    
    tests = [
        test_file_paths,
        test_imports,
        test_services_initialization,
        test_existing_data
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                logger.error(f"Test failed: {test.__name__}")
        except Exception as e:
            logger.error(f"Test error in {test.__name__}: {e}")
    
    logger.info(f"Tests completed: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        logger.info("🎉 All tests passed! Application should start successfully.")
        return True
    else:
        logger.error("❌ Some tests failed. Fix issues before starting application.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
