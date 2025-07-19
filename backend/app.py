#!/usr/bin/env python3
"""
Main Flask application for AI Social Media Post Generator
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Structured logging setup must occur before other imports configure logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logging import getLogger
from app_logging.logger_config import setup_logger

setup_logger()
logger = getLogger(__name__)

import logging

# Configure FFmpeg before importing services that need it
import ffmpeg_config

# Import our services
from services.upload_handler import AudioUploadHandler
from services.whisper_service import WhisperService
from services.text_generation.flan_t5_service import flan_t5_service
from services.text_generation.content_processor import ContentProcessor
from services.text_generation.post_storage import post_storage
from templates.platform_templates import get_template

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv('CORS_ORIGINS', '*')}})

# Logger already configured globally via logger_config; retain `logger` defined above

# Initialize services
upload_handler = AudioUploadHandler(
    upload_folder=os.getenv('UPLOAD_FOLDER', '../uploads/audio'),
    data_folder=os.getenv('DATA_FOLDER', '../uploads/data')
)

whisper_service = WhisperService(
    model_name=os.getenv('WHISPER_MODEL', 'base')
)

# Start background memory manager
from performance.memory_manager import MemoryManager  # noqa: E402
_memory_manager = MemoryManager()
_memory_manager.start()

# Worker pool for concurrent heavy tasks
from performance.worker_manager import WorkerManager  # noqa: E402
import threading

_worker_manager = WorkerManager(max_workers=int(os.getenv('MAX_WORKERS', 4)))

def run_sync_in_worker(fn, *, description="job"):
    """Run *fn* inside worker pool synchronously and return the result."""
    completed = threading.Event()
    container = {}

    def _wrap():  # noqa: D401
        container['result'] = fn()
        completed.set()

    _worker_manager.submit_job(_wrap, description=description)
    completed.wait()
    return container.get('result')

# Load Whisper and FLAN-T5 models on startup
try:
    whisper_service.load_whisper_model()
    flan_t5_service.load_model()
    logger.info("Models loaded successfully on startup")
except Exception as e:
    logger.error(f"Failed to load models on startup: {e}")

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload audio file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Handle file upload
        result = upload_handler.save_audio_file(file)
        
        if result['success']:
            return jsonify({
                'file_id': result['file_id'],
                'status': 'uploaded',
                'filename': result['filename'],
                'size': result['size'],
                'duration': result['duration'],
                'format': result['format']
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
    try:
        logger.info("[ENDPOINT] /api/transcribe called")
        data = request.get_json()
        logger.info(f"[ENDPOINT] Request data: {data}")
        
        if not data or 'file_id' not in data:
            logger.error("[ENDPOINT] No file_id provided")
            return jsonify({
                'success': False,
                'error': 'No file_id provided'
            }), 400
        
        file_id = data['file_id']
        logger.info(f"[ENDPOINT] Processing file_id: {file_id}")
        
        # Get file metadata
        file_metadata = upload_handler.get_file_metadata(file_id)
        if not file_metadata:
            logger.error(f"[ENDPOINT] File not found: {file_id}")
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        logger.info(f"[ENDPOINT] File metadata: {file_metadata}")
        
        # Start transcription in worker
        file_path = file_metadata['file_path']
        logger.info(f"[ENDPOINT] Submitting transcription job for: {file_path}")
        
        def transcribe_job():
            logger.info(f"[WORKER] Starting transcription job for: {file_path}")
            result = whisper_service.transcribe_audio(file_path)
            logger.info(f"[WORKER] Transcription job completed with status: {result.get('status', 'unknown')}")
            return result
        
        transcription_result = run_sync_in_worker(transcribe_job, description=f"transcription-{file_id}")
        logger.info(f"[ENDPOINT] Worker completed, saving transcription")
        
        # Save transcription
        whisper_service.save_transcription(file_id, transcription_result)
        logger.info(f"[ENDPOINT] Transcription saved successfully")
        
        response_data = {
            'transcription_id': transcription_result['transcription_id'],
            'status': transcription_result['status'],
            'text': transcription_result['text'],
            'language': transcription_result['language'],
            'confidence': transcription_result['confidence_metrics']['overall_confidence'],
            'processing_time': transcription_result['processing_time']
        }
        logger.info(f"[ENDPOINT] Returning response: status={transcription_result['status']}, text_length={len(transcription_result['text'])}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in transcription endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/transcription/<transcription_id>', methods=['GET'])
def get_transcription(transcription_id):
    """Get transcription status/result"""
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
            'transcribed_at': transcription['transcribed_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transcription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Clean up uploaded file"""
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

# ---------------------------------------------------------------------------
# Health & monitoring endpoints
# ---------------------------------------------------------------------------
from monitoring.system_monitor import capture_metrics  # noqa: E402
from monitoring.app_monitor import metric_store  # noqa: E402


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'whisper_model': whisper_service.model_name,
        'model_loaded': whisper_service.model is not None
    }), 200


@app.route('/api/health/detailed', methods=['GET'])
def health_detailed():
    """Return detailed system status."""
    sys_metrics = capture_metrics()
    return jsonify(sys_metrics.to_dict()), 200


@app.route('/api/health/models', methods=['GET'])
def health_models():
    """Return status of AI models."""
    return jsonify({
        'whisper_loaded': whisper_service.model is not None,
        'flan_t5_loaded': flan_t5_service.model is not None,
    }), 200


@app.route('/api/health/storage', methods=['GET'])
def health_storage():
    """Check storage space in upload directory."""
    import shutil, pathlib
    upload_dir = pathlib.Path(upload_handler.upload_folder)
    total, used, free = shutil.disk_usage(upload_dir)
    return jsonify({
        'upload_dir': str(upload_dir),
        'total_gb': total / 1024 ** 3,
        'used_gb': used / 1024 ** 3,
        'free_gb': free / 1024 ** 3,
    }), 200


@app.route('/api/metrics', methods=['GET'])
def metrics():
    """Return basic performance metrics collected in memory."""
    return jsonify({
        'avg_response_ms': metric_store.avg_response_ms,
        'error_rate': metric_store.error_rate,
        'request_count': metric_store.request_count,
    }), 200

@app.route('/api/generate-posts', methods=['POST'])
def generate_posts():
    """Generate social media posts from transcription using advanced post generator"""
    try:
        data = request.get_json()

        transcription_id = data.get('transcription_id')
        platforms = data.get('platforms', [])
        tone = data.get('tone', 'professional')
        include_hashtags = data.get('include_hashtags', True)
        include_emojis = data.get('include_emojis', True)
        call_to_action = data.get('call_to_action', False)
        target_audience = data.get('target_audience')
        key_points = data.get('key_points', [])

        if not transcription_id:
            return jsonify({'error': 'transcription_id is required'}), 400

        # Fetch transcription content from storage
        transcription = whisper_service.get_transcription(transcription_id)
        if not transcription:
            return jsonify({'error': 'Transcription not found'}), 404
        
        transcription_text = transcription.get('text', '')
        if not transcription_text:
            return jsonify({'error': 'No transcription text found'}), 400

        # Import the post generator
        from services.text_generation.post_generator import post_generator, PostTone, PostGenerationConfig
        
        # Convert tone string to enum
        try:
            tone_enum = PostTone(tone.lower())
        except ValueError:
            logger.warning(f"Invalid tone '{tone}', using professional")
            tone_enum = PostTone.PROFESSIONAL
        
        posts = {}
        generation_metadata = {}
        
        for platform in platforms:
            try:
                # Create platform-specific config
                config = PostGenerationConfig(
                    tone=tone_enum,
                    max_length=280 if platform == 'twitter' else 500,
                    include_hashtags=include_hashtags,
                    include_emojis=include_emojis,
                    call_to_action=call_to_action,
                    target_audience=target_audience,
                    key_points=key_points if key_points else None,
                    generation_timeout=30
                )
                
                # Generate post with timeout protection
                result = run_sync_in_worker(
                    lambda: post_generator.generate_post(transcription_text, config),
                    description="post-generation"
                )
                
                if result['status'] == 'success':
                    posts[platform] = result['post']
                    generation_metadata[platform] = {
                        'generation_time': result['generation_time'],
                        'word_count': result['word_count'],
                        'character_count': result['character_count'],
                        'tone': result['tone']
                    }
                else:
                    logger.error(f"Failed to generate post for {platform}: {result.get('error', 'Unknown error')}")
                    posts[platform] = f"Error: {result.get('error', 'Generation failed')}"
                    
            except Exception as e:
                logger.error(f"Error generating post for {platform}: {e}")
                posts[platform] = f"Error: {str(e)}"

        # Save generated posts
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
            'metadata': generation_metadata,
            'status': 'completed',
            'available_tones': [t.value for t in PostTone]
        }), 200

    except Exception as e:
        logger.error(f"Error in generate_posts endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/regenerate-post', methods=['POST'])
def regenerate_post():
    """Regenerate specific post with different tone"""
    try:
        data = request.get_json()

        transcription_id = data.get('transcription_id')
        platform = data.get('platform')
        tone = data.get('tone', 'professional')

        if not transcription_id or not platform:
            return jsonify({'error': 'Both transcription_id and platform are required'}), 400

        # Fetch transcription content from storage
        transcription = whisper_service.get_transcription(transcription_id)
        if not transcription:
            return jsonify({'error': 'Transcription not found'}), 404
        
        transcription_text = transcription.get('text', '')
        if not transcription_text:
            return jsonify({'error': 'No transcription text found'}), 400

        # Optimize prompt
        prompt = get_template(platform, tone).format(content=transcription_text)
        
        # Generate text using FLAN-T5
        result = run_sync_in_worker(lambda: flan_t5_service.generate_text(prompt), description="flan-generate")
        generated_text = result.get('text')

        # Process content
        processor = ContentProcessor()
        formatted_text = processor.format_for_platform(generated_text, platform)

        # Update post
        post_updated = post_storage.update_post(
            post_id=transcription_id,  # Using transcription_id as mock post_id for updating purposes
            platform=platform,
            new_content=formatted_text
        )

        if not post_updated:
            return jsonify({'error': 'Failed to update post content'}), 500

        return jsonify({
            'post': formatted_text,
            'status': 'completed'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in regenerate_post endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/posts/<post_id>', methods=['GET'])
def get_generated_posts(post_id):
    """Retrieve generated posts"""
    try:
        post = post_storage.get_post(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404

        return jsonify({
            'posts': post.get('posts', {}),
            'metadata': post.get('metadata', {})
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving posts for {post_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tones', methods=['GET'])
def get_available_tones():
    """Get available post generation tones"""
    try:
        from services.text_generation.post_generator import PostTone
        
        tones = [{
            'value': tone.value,
            'name': tone.value.title().replace('_', ' '),
            'description': {
                'witty': 'Clever and humorous posts with wordplay and smart observations',
                'professional': 'Clear, authoritative posts focused on key insights',
                'motivational': 'Inspiring and uplifting content that encourages action',
                'casual': 'Friendly, conversational posts that feel relatable',
                'educational': 'Informative content focused on teaching and explaining',
                'humorous': 'Funny and entertaining posts designed to make people smile',
                'inspirational': 'Hope-focused content about dreams and positive transformation',
                'urgent': 'Action-oriented posts that create a sense of immediacy'
            }.get(tone.value, f'Posts with {tone.value} tone')
        } for tone in PostTone]
        
        return jsonify({
            'tones': tones,
            'default': 'professional'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting available tones: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ---------------------------------------------------------------------------
# Production security & monitoring middleware (initialised **after** routes)
# ---------------------------------------------------------------------------
from security.security_headers import init_security_headers  # noqa: E402
from security.rate_limiter import init_rate_limiter  # noqa: E402
from monitoring.app_monitor import register_middleware  # noqa: E402

init_security_headers(app)
init_rate_limiter(app)
register_middleware(app)

# Performance response optimisation (gzip, keep-alive)
from performance.response_optimizer import init_response_optimizer  # noqa: E402
init_response_optimizer(app)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') != 'production', host='0.0.0.0', port=5000)

