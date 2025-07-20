#!/usr/bin/env python3
"""
Startup script for the Social Media Post Generator backend
This script handles proper module imports and starts the Flask application
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for proper imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Set up basic logging first (fallback if complex logging fails)
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Try to set up the complex logging, fall back to basic if it fails
try:
    from app_logging.logger_config import setup_logger
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Advanced logging configured successfully")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Advanced logging failed, using basic logging: {e}")

# Configure audio processing
try:
    from config.audio_config import configure_audio_processing
    configure_audio_processing()
    logger.info("Audio processing configured")
except Exception as e:
    logger.warning(f"Audio configuration failed: {e}")

# Now import and run the Flask app
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": os.getenv('CORS_ORIGINS', '*')}})
    
    # Import services with error handling
    try:
        from services.upload_handler import AudioUploadHandler
        from services.whisper_service import WhisperService
        
        # Initialize services
        upload_handler = AudioUploadHandler(
            upload_folder=os.getenv('UPLOAD_FOLDER', '../uploads/audio'),
            data_folder=os.getenv('DATA_FOLDER', '../uploads/data')
        )
        
        whisper_service = WhisperService(
            model_name=os.getenv('WHISPER_MODEL', 'base')
        )
        
        logger.info("Core services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing core services: {e}")
        # Continue with basic functionality
        upload_handler = None
        whisper_service = None
    
    # Try to import advanced services
    try:
        from services.text_generation.flan_t5_service import flan_t5_service
        from services.text_generation.content_processor import ContentProcessor
        from services.text_generation.post_storage import post_storage
        from templates.platform_templates import get_template
        advanced_services = True
        logger.info("Advanced services initialized successfully")
    except Exception as e:
        logger.warning(f"Advanced services failed to load: {e}")
        advanced_services = False
    
    # Try to import performance and monitoring modules
    try:
        from performance.memory_manager import MemoryManager
        from performance.worker_manager import WorkerManager
        from monitoring.system_monitor import capture_metrics
        from monitoring.app_monitor import metric_store
        import threading
        
        # Initialize performance modules
        memory_manager = MemoryManager()
        memory_manager.start()
        
        worker_manager = WorkerManager(max_workers=int(os.getenv('MAX_WORKERS', 4)))
        
        def run_sync_in_worker(fn, *, description="job"):
            """Run function in worker pool synchronously and return the result."""
            completed = threading.Event()
            container = {}
            
            def _wrap():
                container['result'] = fn()
                completed.set()
            
            worker_manager.submit_job(_wrap, description=description)
            completed.wait()
            return container.get('result')
        
        performance_enabled = True
        logger.info("Performance and monitoring modules loaded successfully")
    except Exception as e:
        logger.warning(f"Performance modules failed to load: {e}")
        performance_enabled = False
        
        # Fallback function
        def run_sync_in_worker(fn, *, description="job"):
            """Fallback synchronous execution."""
            return fn()
    
    # Try to initialize models
    try:
        if whisper_service:
            whisper_service.load_whisper_model()
        if advanced_services:
            flan_t5_service.load_model()
        logger.info("Models loaded successfully on startup")
    except Exception as e:
        logger.error(f"Failed to load models on startup: {e}")
    
    # Define routes
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'services': {
                'upload_handler': upload_handler is not None,
                'whisper_service': whisper_service is not None,
                'advanced_services': advanced_services,
                'performance_enabled': performance_enabled
            },
            'whisper_model': whisper_service.model_name if whisper_service else None,
            'model_loaded': whisper_service.model is not None if whisper_service else False
        }), 200
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """Upload audio file"""
        if not upload_handler:
            return jsonify({'error': 'Upload service not available'}), 503
            
        try:
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No file provided'
                }), 400
            
            file = request.files['file']
            result = upload_handler.save_audio_file(file)
            
            if result['success']:
                return jsonify({
                    'file_id': result['file_id'],
                    'status': 'uploaded',
                    'filename': result['filename'],
                    'size': result['size'],
                    'duration': result.get('duration', 0),
                    'format': result.get('format', 'unknown')
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'errors': result['errors']
                }), 400
                
        except Exception as e:
            logger.error(f"Error in upload endpoint: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @app.route('/api/transcribe', methods=['POST'])
    def transcribe_audio():
        """Start transcription process"""
        if not whisper_service:
            return jsonify({'error': 'Transcription service not available'}), 503
            
        try:
            data = request.get_json()
            
            if not data or 'file_id' not in data:
                return jsonify({
                    'success': False,
                    'error': 'No file_id provided'
                }), 400
            
            file_id = data['file_id']
            
            # Get file metadata
            file_metadata = upload_handler.get_file_metadata(file_id)
            if not file_metadata:
                return jsonify({
                    'success': False,
                    'error': 'File not found'
                }), 404
            
            # Start transcription - fix file path format
            file_path = os.path.abspath(file_metadata['file_path'])
            transcription_result = run_sync_in_worker(
                lambda: whisper_service.transcribe_audio(file_path), 
                description="transcription"
            )
            
            # Save transcription
            whisper_service.save_transcription(file_id, transcription_result)
            
            return jsonify({
                'transcription_id': transcription_result['transcription_id'],
                'status': transcription_result['status'],
                'text': transcription_result['text'],
                'language': transcription_result['language'],
                'confidence': transcription_result['confidence_metrics']['overall_confidence'],
                'processing_time': transcription_result['processing_time']
            }), 200
            
        except Exception as e:
            logger.error(f"Error in transcription endpoint: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @app.route('/api/transcription/<transcription_id>', methods=['GET'])
    def get_transcription(transcription_id):
        """Get transcription status/result"""
        if not whisper_service:
            return jsonify({'error': 'Transcription service not available'}), 503
            
        try:
            transcription = whisper_service.get_transcription(transcription_id)
            
            if not transcription:
                return jsonify({
                    'success': False,
                    'error': 'Transcription not found'
                }), 404
            
            return jsonify({
                'status': transcription['status'],
                'text': transcription['text'],
                'language': transcription['language'],
                'confidence': transcription['confidence_metrics']['overall_confidence'],
                'processing_time': transcription['processing_time'],
                'transcribed_at': transcription['transcribed_at'],
                'edited': transcription.get('edited', False),
                'edited_at': transcription.get('edited_at')
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting transcription: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @app.route('/api/transcription/<transcription_id>', methods=['PUT'])
    def update_transcription(transcription_id):
        """Update transcription text"""
        if not whisper_service:
            return jsonify({'error': 'Transcription service not available'}), 503
            
        try:
            data = request.get_json()
            
            if not data or 'text' not in data:
                return jsonify({
                    'success': False,
                    'error': 'No text provided'
                }), 400
            
            new_text = data['text'].strip()
            
            if not new_text:
                return jsonify({
                    'success': False,
                    'error': 'Text cannot be empty'
                }), 400
            
            # Update the transcription
            success = whisper_service.update_transcription(transcription_id, new_text)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Transcription updated successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Transcription not found'
                }), 404
                
        except Exception as e:
            logger.error(f"Error updating transcription: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @app.route('/api/generate-posts', methods=['POST'])
    def generate_posts():
        """Generate social media posts from transcription"""
        if not advanced_services:
            return jsonify({'error': 'Text generation service not available'}), 503
            
        try:
            data = request.get_json()
            
            transcription_id = data.get('transcription_id')
            platforms = data.get('platforms', [])
            tone = data.get('tone', 'professional')
            
            if not transcription_id:
                return jsonify({'error': 'transcription_id is required'}), 400
            
            # Fetch transcription content from storage
            transcription = whisper_service.get_transcription(transcription_id)
            if not transcription:
                return jsonify({'error': 'Transcription not found'}), 404
            
            transcription_text = transcription.get('text', '')
            if not transcription_text:
                return jsonify({'error': 'No transcription text found'}), 400
            
            posts = {}
            for platform in platforms:
                try:
                    # Optimize prompt
                    prompt = get_template(platform, tone).format(content=transcription_text)
                    
                    # Generate text using FLAN-T5
                    generation_result = run_sync_in_worker(
                        lambda: flan_t5_service.generate_text(prompt), 
                        description="flan-generate"
                    )
                    generated_text = generation_result.get('text')
                    
                    # Process content
                    processor = ContentProcessor()
                    formatted_text = processor.format_for_platform(generated_text, platform)
                    
                    posts[platform] = formatted_text
                except Exception as e:
                    logger.error(f"Error generating post for {platform}: {e}")
            
            # Save generated posts
            generation_metadata = generation_result.get('metadata', {}) if 'generation_result' in locals() else {}
            post_id = post_storage.save_post(
                transcription_id=transcription_id,
                platforms=platforms,
                tone=tone,
                posts=posts,
                generation_metadata=generation_metadata
            )
            
            return jsonify({
                'post_id': post_id,
                'posts': posts,
                'status': 'completed'
            }), 200
            
        except Exception as e:
            logger.error(f"Error in generate_posts endpoint: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/files/<file_id>', methods=['DELETE'])
    def delete_file(file_id):
        """Clean up uploaded file"""
        if not upload_handler:
            return jsonify({'error': 'Upload service not available'}), 503
            
        try:
            result = upload_handler.delete_file(file_id)
            
            if result['success']:
                return jsonify({
                    'status': 'deleted',
                    'message': result['message']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
                
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    # Add more health endpoints if performance monitoring is available
    if performance_enabled:
        @app.route('/api/health/detailed', methods=['GET'])
        def health_detailed():
            """Return detailed system status."""
            try:
                sys_metrics = capture_metrics()
                return jsonify(sys_metrics.to_dict()), 200
            except Exception as e:
                logger.error(f"Error in detailed health check: {e}")
                return jsonify({'error': 'Monitoring unavailable'}), 503
        
        @app.route('/api/metrics', methods=['GET'])
        def metrics():
            """Return basic performance metrics collected in memory."""
            try:
                return jsonify({
                    'avg_response_ms': metric_store.avg_response_ms,
                    'error_rate': metric_store.error_rate,
                    'request_count': metric_store.request_count,
                }), 200
            except Exception as e:
                logger.error(f"Error in metrics endpoint: {e}")
                return jsonify({'error': 'Metrics unavailable'}), 503
    
    # Try to initialize security and performance optimizations (temporarily disabled)
    try:
        # from security.security_headers import init_security_headers
        from security.rate_limiter import init_rate_limiter
        from monitoring.app_monitor import register_middleware
        from performance.response_optimizer import init_response_optimizer
        
        # init_security_headers(app)  # Temporarily disabled due to Talisman issues
        init_rate_limiter(app)
        register_middleware(app)
        init_response_optimizer(app)
        
        logger.info("Security and performance optimizations loaded (headers disabled)")
    except Exception as e:
        logger.warning(f"Security/performance optimizations failed to load: {e}")
    
    # Start the application
    if __name__ == '__main__':
        logger.info("Starting Flask application...")
        app.run(
            debug=os.getenv('FLASK_ENV') != 'production',
            host='0.0.0.0',
            port=5000
        )

except Exception as e:
    print(f"Critical error starting application: {e}")
    sys.exit(1)
