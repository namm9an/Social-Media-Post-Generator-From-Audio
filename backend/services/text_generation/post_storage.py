#!/usr/bin/env python3
"""
Post Storage Service

Enterprise-grade storage and retrieval service for generated social media posts.
Handles JSON file operations with thread safety and error handling.
"""

import os
import json
import uuid
import time
import logging
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostStorageError(Exception):
    """Custom exception for post storage operations"""
    pass

class PostStorage:
    """
    Thread-safe storage service for generated posts with enterprise features:
    - Atomic file operations
    - Data validation
    - Error handling
    - Backup functionality
    """
    
    def __init__(self, data_file: str = "../uploads/data/generated_posts.json"):
        """
        Initialize the post storage service
        
        Args:
            data_file: Path to the JSON data file
        """
        self.data_file = os.path.abspath(data_file)
        self.data_dir = os.path.dirname(self.data_file)
        self.backup_dir = os.path.join(self.data_dir, 'backups')
        self._file_lock = threading.Lock()
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Initialize data file if it doesn't exist
        if not os.path.exists(self.data_file):
            self._write_data({})
        
        logger.info(f"PostStorage initialized with data file: {self.data_file}")
    
    def _read_data(self) -> Dict[str, Any]:
        """
        Read data from the JSON file with error handling
        
        Returns:
            Dictionary containing all stored posts
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Error reading data file: {e}. Initializing with empty data.")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error reading data file: {e}")
            raise PostStorageError(f"Failed to read data file: {e}")
    
    def _write_data(self, data: Dict[str, Any]):
        """
        Write data to the JSON file with atomic operations
        
        Args:
            data: Dictionary to write to file
        """
        try:
            # Write to temporary file first for atomic operation
            temp_file = f"{self.data_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Replace original file with temporary file
            if os.path.exists(self.data_file):
                os.replace(temp_file, self.data_file)
            else:
                os.rename(temp_file, self.data_file)
                
        except Exception as e:
            # Clean up temporary file if it exists
            if os.path.exists(temp_file):
                os.remove(temp_file)
            logger.error(f"Error writing data file: {e}")
            raise PostStorageError(f"Failed to write data file: {e}")
    
    def _validate_post_data(self, post_data: Dict[str, Any]) -> bool:
        """
        Validate post data structure
        
        Args:
            post_data: Post data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['transcription_id', 'platforms', 'tone', 'posts', 'metadata']
        
        for field in required_fields:
            if field not in post_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate posts structure
        if not isinstance(post_data['posts'], dict):
            logger.error("Posts field must be a dictionary")
            return False
        
        # Validate metadata structure
        if not isinstance(post_data['metadata'], dict):
            logger.error("Metadata field must be a dictionary")
            return False
        
        return True
    
    def _create_backup(self) -> str:
        """
        Create a backup of the current data file
        
        Returns:
            Path to the backup file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"generated_posts_backup_{timestamp}.json")
            
            if os.path.exists(self.data_file):
                import shutil
                shutil.copy2(self.data_file, backup_file)
                logger.info(f"Backup created: {backup_file}")
                return backup_file
            
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
        
        return ""
    
    def save_post(
        self,
        transcription_id: str,
        platforms: List[str],
        tone: str,
        posts: Dict[str, str],
        generation_metadata: Dict[str, Any]
    ) -> str:
        """
        Save a generated post to storage
        
        Args:
            transcription_id: ID of the source transcription
            platforms: List of platforms the post was generated for
            tone: Tone used for generation
            posts: Dictionary of platform -> post content
            generation_metadata: Metadata about the generation process
            
        Returns:
            Unique post ID
        """
        with self._file_lock:
            try:
                # Generate unique post ID
                post_id = str(uuid.uuid4())
                
                # Prepare post data
                post_data = {
                    'transcription_id': transcription_id,
                    'platforms': platforms,
                    'tone': tone,
                    'posts': posts,
                    'metadata': {
                        'created_at': datetime.now().isoformat(),
                        'model_used': generation_metadata.get('model', 'unknown'),
                        'generation_time': generation_metadata.get('generation_time', 0),
                        'device': generation_metadata.get('device', 'unknown'),
                        'post_id': post_id
                    }
                }
                
                # Validate post data
                if not self._validate_post_data(post_data):
                    raise PostStorageError("Invalid post data structure")
                
                # Read current data
                data = self._read_data()
                
                # Create backup before modification
                self._create_backup()
                
                # Add new post
                data[post_id] = post_data
                
                # Write updated data
                self._write_data(data)
                
                logger.info(f"Post saved successfully with ID: {post_id}")
                return post_id
                
            except Exception as e:
                logger.error(f"Error saving post: {e}")
                raise PostStorageError(f"Failed to save post: {e}")
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a post by ID
        
        Args:
            post_id: Unique post identifier
            
        Returns:
            Post data or None if not found
        """
        with self._file_lock:
            try:
                data = self._read_data()
                return data.get(post_id)
                
            except Exception as e:
                logger.error(f"Error retrieving post {post_id}: {e}")
                raise PostStorageError(f"Failed to retrieve post: {e}")
    
    def get_posts_by_transcription(self, transcription_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all posts for a specific transcription
        
        Args:
            transcription_id: Transcription identifier
            
        Returns:
            List of post data
        """
        with self._file_lock:
            try:
                data = self._read_data()
                posts = []
                
                for post_id, post_data in data.items():
                    if post_data.get('transcription_id') == transcription_id:
                        post_data['post_id'] = post_id  # Add post ID to response
                        posts.append(post_data)
                
                return posts
                
            except Exception as e:
                logger.error(f"Error retrieving posts for transcription {transcription_id}: {e}")
                raise PostStorageError(f"Failed to retrieve posts: {e}")
    
    def update_post(self, post_id: str, platform: str, new_content: str) -> bool:
        """
        Update a specific post's content for a platform
        
        Args:
            post_id: Unique post identifier
            platform: Platform to update
            new_content: New content for the platform
            
        Returns:
            True if successful, False otherwise
        """
        with self._file_lock:
            try:
                data = self._read_data()
                
                if post_id not in data:
                    logger.warning(f"Post {post_id} not found for update")
                    return False
                
                # Create backup before modification
                self._create_backup()
                
                # Update the post content
                data[post_id]['posts'][platform] = new_content
                data[post_id]['metadata']['updated_at'] = datetime.now().isoformat()
                
                # Write updated data
                self._write_data(data)
                
                logger.info(f"Post {post_id} updated for platform {platform}")
                return True
                
            except Exception as e:
                logger.error(f"Error updating post {post_id}: {e}")
                raise PostStorageError(f"Failed to update post: {e}")
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post by ID
        
        Args:
            post_id: Unique post identifier
            
        Returns:
            True if successful, False if not found
        """
        with self._file_lock:
            try:
                data = self._read_data()
                
                if post_id not in data:
                    logger.warning(f"Post {post_id} not found for deletion")
                    return False
                
                # Create backup before modification
                self._create_backup()
                
                # Remove the post
                del data[post_id]
                
                # Write updated data
                self._write_data(data)
                
                logger.info(f"Post {post_id} deleted successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting post {post_id}: {e}")
                raise PostStorageError(f"Failed to delete post: {e}")
    
    def get_all_posts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve all posts with pagination
        
        Args:
            limit: Maximum number of posts to return
            offset: Number of posts to skip
            
        Returns:
            List of post data
        """
        with self._file_lock:
            try:
                data = self._read_data()
                
                # Convert to list with post IDs
                posts = []
                for post_id, post_data in data.items():
                    post_data['post_id'] = post_id
                    posts.append(post_data)
                
                # Sort by creation time (newest first)
                posts.sort(
                    key=lambda x: x.get('metadata', {}).get('created_at', ''),
                    reverse=True
                )
                
                # Apply pagination
                return posts[offset:offset + limit]
                
            except Exception as e:
                logger.error(f"Error retrieving all posts: {e}")
                raise PostStorageError(f"Failed to retrieve posts: {e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage statistics
        """
        with self._file_lock:
            try:
                data = self._read_data()
                
                stats = {
                    'total_posts': len(data),
                    'file_size': os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0,
                    'data_file': self.data_file,
                    'backup_dir': self.backup_dir
                }
                
                # Platform breakdown
                platform_counts = {}
                for post_data in data.values():
                    platforms = post_data.get('platforms', [])
                    for platform in platforms:
                        platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                stats['platform_breakdown'] = platform_counts
                
                return stats
                
            except Exception as e:
                logger.error(f"Error getting storage stats: {e}")
                return {'error': str(e)}

# Global storage instance
post_storage = PostStorage()
