#!/usr/bin/env python3
"""
Enhanced error handling utility for the AI Social Media Post Generator
"""

import logging
import traceback
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from functools import wraps
import sys


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class CustomExceptionTypes:
    """Custom exception classes for different error types"""
    
    class ModelLoadError(Exception):
        """Raised when model loading fails"""
        pass
    
    class TranscriptionError(Exception):
        """Raised when transcription fails"""
        pass
    
    class GenerationError(Exception):
        """Raised when post generation fails"""
        pass
    
    class FileProcessingError(Exception):
        """Raised when file processing fails"""
        pass
    
    class ValidationError(Exception):
        """Raised when input validation fails"""
        pass
    
    class NetworkError(Exception):
        """Raised when network operations fail"""
        pass


class ErrorHandler:
    """Comprehensive error handling and logging utility"""
    
    def __init__(self, log_file: str = 'app_errors.log'):
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Setup enhanced logging configuration"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure detailed file logging
        file_handler = logging.FileHandler(f'logs/{self.log_file}')
        file_handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None, user_id: str = None) -> str:
        """
        Log detailed error information
        
        Args:
            error: The exception that occurred
            context: Additional context information
            user_id: Optional user identifier
            
        Returns:
            Error ID for tracking
        """
        error_id = self._generate_error_id()
        
        error_details = {
            'error_id': error_id,
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'user_id': user_id
        }
        
        # Log to file
        logger.error(f"Error ID: {error_id}", extra=error_details)
        
        # Save detailed error to JSON file for debugging
        self._save_error_details(error_id, error_details)
        
        return error_id
    
    def _generate_error_id(self) -> str:
        """Generate a unique error ID"""
        return f"ERR_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{id(self)}"
    
    def _save_error_details(self, error_id: str, error_details: Dict[str, Any]):
        """Save detailed error information to JSON file"""
        try:
            os.makedirs('logs/errors', exist_ok=True)
            
            with open(f'logs/errors/{error_id}.json', 'w') as f:
                json.dump(error_details, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save error details: {e}")
    
    def format_user_error(self, error: Exception, operation: str = "operation") -> Dict[str, Any]:
        """
        Format error for user-friendly response
        
        Args:
            error: The exception that occurred
            operation: The operation that failed
            
        Returns:
            User-friendly error response
        """
        error_type = type(error).__name__
        
        # Map technical errors to user-friendly messages
        user_messages = {
            'ModelLoadError': 'AI model is currently unavailable. Please try again later.',
            'TranscriptionError': 'Audio transcription failed. Please check your audio file and try again.',
            'GenerationError': 'Post generation failed. Please try again with different settings.',
            'FileProcessingError': 'File processing failed. Please check your file format and try again.',
            'ValidationError': 'Invalid input provided. Please check your data and try again.',
            'NetworkError': 'Network connection failed. Please check your connection and try again.',
            'ConnectionError': 'Unable to connect to external services. Please try again later.',
            'TimeoutError': 'Operation timed out. Please try again.',
            'MemoryError': 'System resources are temporarily unavailable. Please try again later.',
            'FileNotFoundError': 'Required file not found. Please check your upload.',
            'PermissionError': 'Permission denied. Please check file permissions.',
        }
        
        user_message = user_messages.get(error_type, 
                                       f"An unexpected error occurred during {operation}. Please try again.")
        
        return {
            'success': False,
            'error': user_message,
            'error_type': error_type,
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def handle_model_error(self, error: Exception, model_name: str = "AI model") -> Dict[str, Any]:
        """Handle model-related errors"""
        error_id = self.log_error(error, {'model': model_name})
        
        if "CUDA" in str(error) or "GPU" in str(error):
            message = "GPU processing is currently unavailable. Falling back to CPU processing."
        elif "memory" in str(error).lower():
            message = "Insufficient memory to load the model. Please try again later."
        elif "download" in str(error).lower() or "connection" in str(error).lower():
            message = "Unable to download model files. Please check your internet connection."
        else:
            message = f"{model_name} is currently unavailable. Please try again later."
        
        return {
            'success': False,
            'error': message,
            'error_id': error_id,
            'suggestions': [
                'Check your internet connection',
                'Try again in a few minutes',
                'Contact support if the problem persists'
            ]
        }
    
    def handle_file_error(self, error: Exception, filename: str = None) -> Dict[str, Any]:
        """Handle file-related errors"""
        error_id = self.log_error(error, {'filename': filename})
        
        if isinstance(error, FileNotFoundError):
            message = f"File not found: {filename}" if filename else "Required file not found."
        elif isinstance(error, PermissionError):
            message = "Permission denied. Please check file permissions."
        elif "size" in str(error).lower():
            message = "File is too large. Please use a smaller file."
        elif "format" in str(error).lower() or "codec" in str(error).lower():
            message = "Unsupported file format. Please use MP3, WAV, or AAC files."
        else:
            message = "File processing failed. Please check your file and try again."
        
        return {
            'success': False,
            'error': message,
            'error_id': error_id,
            'suggestions': [
                'Check file format (MP3, WAV, AAC supported)',
                'Ensure file size is under 100MB',
                'Try uploading a different file'
            ]
        }
    
    def handle_api_error(self, error: Exception, endpoint: str = None) -> Tuple[Dict[str, Any], int]:
        """
        Handle API errors and return appropriate HTTP status codes
        
        Returns:
            Tuple of (error_response, status_code)
        """
        error_id = self.log_error(error, {'endpoint': endpoint})
        
        # Map exceptions to HTTP status codes
        status_codes = {
            'ValidationError': 400,
            'FileNotFoundError': 404,
            'PermissionError': 403,
            'TimeoutError': 408,
            'ConnectionError': 503,
            'NetworkError': 503,
            'ModelLoadError': 503,
            'TranscriptionError': 500,
            'GenerationError': 500,
            'FileProcessingError': 400,
            'MemoryError': 503,
        }
        
        error_type = type(error).__name__
        status_code = status_codes.get(error_type, 500)
        
        response = self.format_user_error(error, f"API call to {endpoint}" if endpoint else "API call")
        response['error_id'] = error_id
        
        return response, status_code


# Global error handler instance
error_handler = ErrorHandler()


def handle_exceptions(operation: str = "operation"):
    """
    Decorator to handle exceptions in API endpoints
    
    Args:
        operation: Description of the operation being performed
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_response, status_code = error_handler.handle_api_error(e, operation)
                return error_response, status_code
        return wrapper
    return decorator


def log_performance(operation: str):
    """
    Decorator to log performance metrics
    
    Args:
        operation: Description of the operation being performed
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                logger.info(f"{operation} completed successfully in {duration:.2f} seconds")
                return result
                
            except Exception as e:
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                logger.error(f"{operation} failed after {duration:.2f} seconds: {str(e)}")
                raise
                
        return wrapper
    return decorator


def validate_input(validation_func):
    """
    Decorator to validate input parameters
    
    Args:
        validation_func: Function to validate input
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validation_func(*args, **kwargs)
                return func(*args, **kwargs)
            except ValueError as e:
                raise CustomExceptionTypes.ValidationError(str(e))
        return wrapper
    return decorator


# Utility functions for common error scenarios
def safe_model_load(model_loader, model_name: str):
    """
    Safely load a model with proper error handling
    
    Args:
        model_loader: Function to load the model
        model_name: Name of the model being loaded
        
    Returns:
        Loaded model or None if loading fails
    """
    try:
        logger.info(f"Loading {model_name}...")
        model = model_loader()
        logger.info(f"{model_name} loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to load {model_name}: {str(e)}")
        raise CustomExceptionTypes.ModelLoadError(f"Failed to load {model_name}: {str(e)}")


def safe_file_operation(file_operation, filename: str = None):
    """
    Safely perform file operations with proper error handling
    
    Args:
        file_operation: Function to perform file operation
        filename: Name of the file being processed
        
    Returns:
        Result of file operation
    """
    try:
        return file_operation()
    except Exception as e:
        logger.error(f"File operation failed for {filename}: {str(e)}")
        raise CustomExceptionTypes.FileProcessingError(f"File operation failed: {str(e)}")


def cleanup_resources(cleanup_func):
    """
    Decorator to ensure resources are cleaned up
    
    Args:
        cleanup_func: Function to clean up resources
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                try:
                    cleanup_func()
                except Exception as e:
                    logger.error(f"Resource cleanup failed: {str(e)}")
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test error handling
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_id = error_handler.log_error(e, {'test': True})
        print(f"Error logged with ID: {error_id}")
        
        user_response = error_handler.format_user_error(e, "test operation")
        print(f"User response: {user_response}")
