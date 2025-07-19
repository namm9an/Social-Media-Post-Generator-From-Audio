import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import librosa
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_DURATION = 600  # 10 minutes

class AudioUploadHandler:
    def __init__(self, upload_folder="../uploads/audio", data_folder="../uploads/data"):
        self.upload_folder = upload_folder
        self.data_folder = data_folder
        self.audio_files_json = os.path.join(data_folder, "audio_files.json")
        
        # Ensure directories exist
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(data_folder, exist_ok=True)
        
        # Initialize JSON file if it doesn't exist
        if not os.path.exists(self.audio_files_json):
            with open(self.audio_files_json, 'w') as f:
                json.dump({}, f)
    
    def generate_file_id(self):
        """Generate unique file identifier"""
        return str(uuid.uuid4())
    
    def validate_file(self, file):
        """Alias for validate_audio_file for compatibility"""
        is_valid, errors = self.validate_audio_file(file)
        return {'valid': is_valid, 'errors': errors}
    
    def validate_audio_file(self, file):
        """Check format, size, and other file properties"""
        errors = []
        
        if not file:
            errors.append("No file provided")
            return False, errors
        
        if not file.filename:
            errors.append("No filename provided")
            return False, errors
        
        # Check file extension
        if '.' not in file.filename:
            errors.append("File has no extension")
            return False, errors
        
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            errors.append(f"Invalid file format. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}")
            return False, errors
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            errors.append(f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB")
            return False, errors
        
        if file_size == 0:
            errors.append("File is empty")
            return False, errors
        
        return True, errors
    
    def validate_audio_duration(self, file_path):
        """Validate audio duration using librosa"""
        try:
            duration = librosa.get_duration(path=file_path)
            if duration > MAX_DURATION:
                return False, f"Audio too long. Maximum duration: {MAX_DURATION/60:.1f} minutes"
            return True, None
        except Exception as e:
            return False, f"Could not analyze audio file: {str(e)}"
    
    def save_audio_file(self, file):
        """Store file securely and return metadata"""
        try:
            # Validate file
            is_valid, errors = self.validate_audio_file(file)
            if not is_valid:
                return {
                    'success': False,
                    'errors': errors
                }
            
            # Generate unique filename
            file_id = self.generate_file_id()
            original_filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stored_filename = f"{file_id}_{timestamp}_{original_filename}"
            file_path = os.path.abspath(os.path.join(self.upload_folder, stored_filename))
            
            # Save file
            file.save(file_path)
            
            # Validate audio duration
            duration_valid, duration_error = self.validate_audio_duration(file_path)
            if not duration_valid:
                os.remove(file_path)  # Clean up invalid file
                return {
                    'success': False,
                    'errors': [duration_error]
                }
            
            # Get file metadata
            file_size = os.path.getsize(file_path)
            duration = librosa.get_duration(path=file_path)
            
            # Save metadata to JSON
            metadata = {
                'file_id': file_id,
                'filename': original_filename,
                'stored_filename': stored_filename,
                'file_path': file_path,
                'size': file_size,
                'duration': duration,
                'format': original_filename.rsplit('.', 1)[1].lower(),
                'uploaded_at': datetime.now().isoformat(),
                'status': 'uploaded'
            }
            
            # Load existing data
            with open(self.audio_files_json, 'r') as f:
                audio_files = json.load(f)
            
            # Add new file
            audio_files[file_id] = metadata
            
            # Save back to JSON
            with open(self.audio_files_json, 'w') as f:
                json.dump(audio_files, f, indent=2)
            
            logger.info(f"Audio file uploaded successfully: {file_id}")
            
            return {
                'success': True,
                'file_id': file_id,
                'filename': original_filename,
                'size': file_size,
                'duration': duration,
                'format': metadata['format'],
                'uploaded_at': metadata['uploaded_at']
            }
            
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            return {
                'success': False,
                'errors': [f"Internal server error: {str(e)}"]
            }
    
    def save_file_metadata(self, file_id, metadata):
        """Save file metadata to JSON"""
        try:
            with open(self.audio_files_json, 'r') as f:
                audio_files = json.load(f)
            
            audio_files[file_id] = metadata
            
            with open(self.audio_files_json, 'w') as f:
                json.dump(audio_files, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving file metadata: {str(e)}")
            return False
    
    def get_file_metadata(self, file_id):
        """Get file metadata by ID"""
        try:
            with open(self.audio_files_json, 'r') as f:
                audio_files = json.load(f)
            return audio_files.get(file_id)
        except Exception as e:
            logger.error(f"Error reading file metadata: {str(e)}")
            return None
    
    def delete_file(self, file_id):
        """Delete file and its metadata"""
        try:
            # Get file metadata
            metadata = self.get_file_metadata(file_id)
            if not metadata:
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            # Delete physical file
            file_path = metadata['file_path']
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove from JSON
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
        """Remove old uploads"""
        try:
            from datetime import timedelta
            
            cutoff_time = datetime.now() - timedelta(hours=hours_old)
            deleted_files = []
            
            with open(self.audio_files_json, 'r') as f:
                audio_files = json.load(f)
            
            files_to_delete = []
            for file_id, metadata in audio_files.items():
                uploaded_at = datetime.fromisoformat(metadata['uploaded_at'])
                if uploaded_at < cutoff_time:
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
