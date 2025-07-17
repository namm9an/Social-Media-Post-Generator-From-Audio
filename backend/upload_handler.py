"""
Audio File Upload Handler with Validation
Handles file uploads, validation, and storage for the AI Social Media Post Generator
"""

import os
import json
import uuid
import time
import librosa
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AudioUploadHandler:
    def __init__(self, upload_folder="uploads/audio", max_file_size=50*1024*1024, max_duration=600):
        """
        Initialize the audio upload handler.
        
        Args:
            upload_folder (str): Directory to store uploaded files
            max_file_size (int): Maximum file size in bytes (default: 50MB)
            max_duration (int): Maximum audio duration in seconds (default: 10 minutes)
        """
        self.upload_folder = upload_folder
        self.max_file_size = max_file_size
        self.max_duration = max_duration
        self.supported_formats = {'mp3', 'wav', 'm4a', 'ogg', 'flac'}
        
        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # JSON storage files
        self.audio_files_json = os.path.join("uploads", "audio_files.json")
        self.transcriptions_json = os.path.join("uploads", "transcriptions.json")
        
        # Initialize JSON files if they don't exist
        self._init_json_files()
    
    def _init_json_files(self):
        """Initialize JSON storage files if they don't exist."""
        for json_file in [self.audio_files_json, self.transcriptions_json]:
            if not os.path.exists(json_file):
                with open(json_file, 'w') as f:
                    json.dump({}, f)
    
    def generate_file_id(self):
        """Generate unique file identifier."""
        return str(uuid.uuid4())
    
    def validate_audio_file(self, file):
        """
        Validate uploaded audio file.
        
        Args:
            file: Flask file object
            
        Returns:
            dict: Validation result with success status and error messages
        """
        validation_result = {
            'valid': True,
            'errors': []
        }
        
        # Check if file exists
        if not file:
            validation_result['valid'] = False
            validation_result['errors'].append("No file provided")
            return validation_result
        
        # Check filename
        if not file.filename:
            validation_result['valid'] = False
            validation_result['errors'].append("No filename provided")
            return validation_result
        
        # Check file format
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_extension not in self.supported_formats:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Unsupported file format. Supported formats: {', '.join(self.supported_formats)}")
        
        # Check file size (this is approximate since we can't get exact size without reading the file)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.max_file_size:
            validation_result['valid'] = False
            validation_result['errors'].append(f"File size ({file_size / (1024*1024):.1f}MB) exceeds maximum allowed size ({self.max_file_size / (1024*1024):.1f}MB)")
        
        return validation_result
    
    def validate_audio_duration(self, file_path):
        """
        Validate audio file duration using librosa.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            dict: Validation result with duration info
        """
        try:
            # Load audio file and get duration
            duration = librosa.get_duration(path=file_path)
            
            if duration > self.max_duration:
                return {
                    'valid': False,
                    'duration': duration,
                    'error': f"Audio duration ({duration:.1f}s) exceeds maximum allowed duration ({self.max_duration}s)"
                }
            
            return {
                'valid': True,
                'duration': duration,
                'error': None
            }
        except Exception as e:
            return {
                'valid': False,
                'duration': None,
                'error': f"Could not analyze audio file: {str(e)}"
            }
    
    def save_audio_file(self, file):
        """
        Save uploaded audio file with validation.
        
        Args:
            file: Flask file object
            
        Returns:
            dict: Result with file_id and metadata or error information
        """
        try:
            # Validate file
            validation = self.validate_audio_file(file)
            if not validation['valid']:
                return {
                    'success': False,
                    'errors': validation['errors']
                }
            
            # Generate unique file ID and secure filename
            file_id = self.generate_file_id()
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stored_filename = f"{file_id}_{timestamp}_{original_filename}"
            file_path = os.path.join(self.upload_folder, stored_filename)
            
            # Save file
            file.save(file_path)
            
            # Validate audio duration
            duration_validation = self.validate_audio_duration(file_path)
            if not duration_validation['valid']:
                # Remove invalid file
                os.remove(file_path)
                return {
                    'success': False,
                    'errors': [duration_validation['error']]
                }
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Store metadata
            file_metadata = {
                'file_id': file_id,
                'filename': original_filename,
                'stored_filename': stored_filename,
                'file_path': file_path,
                'file_size': file_size,
                'duration': duration_validation['duration'],
                'format': file_extension,
                'uploaded_at': datetime.now().isoformat(),
                'status': 'uploaded'
            }
            
            # Save to JSON storage
            self._save_file_metadata(file_id, file_metadata)
            
            logger.info(f"Audio file uploaded successfully: {file_id}")
            
            return {
                'success': True,
                'file_id': file_id,
                'filename': original_filename,
                'size': file_size,
                'duration': duration_validation['duration'],
                'format': file_extension,
                'uploaded_at': file_metadata['uploaded_at']
            }
            
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            return {
                'success': False,
                'errors': [f"Internal server error: {str(e)}"]
            }
    
    def _save_file_metadata(self, file_id, metadata):
        """Save file metadata to JSON storage."""
        try:
            # Read existing data
            with open(self.audio_files_json, 'r') as f:
                audio_files = json.load(f)
            
            # Add new file metadata
            audio_files[file_id] = metadata
            
            # Write back to file
            with open(self.audio_files_json, 'w') as f:
                json.dump(audio_files, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving file metadata: {str(e)}")
            raise
    
    def get_file_metadata(self, file_id):
        """Get file metadata by ID."""
        try:
            with open(self.audio_files_json, 'r') as f:
                audio_files = json.load(f)
            return audio_files.get(file_id)
        except Exception as e:
            logger.error(f"Error reading file metadata: {str(e)}")
            return None
    
    def delete_file(self, file_id):
        """
        Delete uploaded file and its metadata.
        
        Args:
            file_id (str): File identifier
            
        Returns:
            dict: Deletion result
        """
        try:
            # Get file metadata
            file_metadata = self.get_file_metadata(file_id)
            if not file_metadata:
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            # Delete physical file
            file_path = file_metadata['file_path']
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove from JSON storage
            with open(self.audio_files_json, 'r') as f:
                audio_files = json.load(f)
            
            if file_id in audio_files:
                del audio_files[file_id]
                
                with open(self.audio_files_json, 'w') as f:
                    json.dump(audio_files, f, indent=2)
            
            logger.info(f"File deleted successfully: {file_id}")
            
            return {
                'success': True,
                'message': 'File deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return {
                'success': False,
                'error': f"Error deleting file: {str(e)}"
            }
    
    def cleanup_old_files(self, hours_old=24):
        """
        Clean up files older than specified hours.
        
        Args:
            hours_old (int): Delete files older than this many hours
            
        Returns:
            dict: Cleanup result
        """
        try:
            cleanup_time = datetime.now() - timedelta(hours=hours_old)
            deleted_files = []
            
            with open(self.audio_files_json, 'r') as f:
                audio_files = json.load(f)
            
            files_to_delete = []
            for file_id, metadata in audio_files.items():
                uploaded_at = datetime.fromisoformat(metadata['uploaded_at'])
                if uploaded_at < cleanup_time:
                    files_to_delete.append(file_id)
            
            for file_id in files_to_delete:
                result = self.delete_file(file_id)
                if result['success']:
                    deleted_files.append(file_id)
            
            logger.info(f"Cleaned up {len(deleted_files)} old files")
            
            return {
                'success': True,
                'deleted_files': deleted_files,
                'count': len(deleted_files)
            }
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return {
                'success': False,
                'error': f"Cleanup error: {str(e)}"
            }

# Test function
def test_upload_handler():
    """Test the upload handler functionality."""
    try:
        handler = AudioUploadHandler()
        print("✓ AudioUploadHandler initialized successfully")
        print(f"✓ Upload folder: {handler.upload_folder}")
        print(f"✓ Supported formats: {handler.supported_formats}")
        print(f"✓ Max file size: {handler.max_file_size / (1024*1024):.1f}MB")
        print(f"✓ Max duration: {handler.max_duration}s")
        return True
    except Exception as e:
        print(f"✗ AudioUploadHandler initialization failed: {e}")
        return False

if __name__ == "__main__":
    test_upload_handler()
