"""
File upload handling functionality
"""

import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime

class FileUploader:
    def __init__(self, upload_folder="uploads"):
        """Initialize file uploader."""
        self.upload_folder = upload_folder
        self.allowed_extensions = {'mp3', 'wav', 'm4a', 'ogg', 'flac'}
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Initialize JSON storage files
        self.audio_files_json = os.path.join(upload_folder, "audio_files.json")
        self.transcriptions_json = os.path.join(upload_folder, "transcriptions.json")
        self.posts_json = os.path.join(upload_folder, "posts.json")
        
        # Create JSON files if they don't exist
        for json_file in [self.audio_files_json, self.transcriptions_json, self.posts_json]:
            if not os.path.exists(json_file):
                with open(json_file, 'w') as f:
                    json.dump([], f)
    
    def allowed_file(self, filename):
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_file(self, file):
        """Save uploaded file."""
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            filepath = os.path.join(self.upload_folder, filename)
            file.save(filepath)
            
            # Save file metadata
            file_info = {
                "id": timestamp,
                "filename": filename,
                "original_name": file.filename,
                "filepath": filepath,
                "upload_time": datetime.now().isoformat(),
                "size": os.path.getsize(filepath)
            }
            
            self.save_to_json(self.audio_files_json, file_info)
            
            return file_info
        return None
    
    def save_to_json(self, json_file, data):
        """Save data to JSON file."""
        try:
            with open(json_file, 'r') as f:
                existing_data = json.load(f)
        except:
            existing_data = []
        
        existing_data.append(data)
        
        with open(json_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def get_from_json(self, json_file):
        """Get data from JSON file."""
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except:
            return []

# Test function
def test_upload():
    """Test file upload functionality."""
    try:
        uploader = FileUploader()
        print("✓ File uploader initialized successfully")
        print(f"✓ Upload folder: {uploader.upload_folder}")
        print(f"✓ Allowed extensions: {uploader.allowed_extensions}")
        return True
    except Exception as e:
        print(f"✗ File uploader initialization failed: {e}")
        return False

if __name__ == "__main__":
    test_upload()
