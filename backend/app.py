#!/usr/bin/env python3
"""
Main Flask application for AI Social Media Post Generator
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
upload_handler = AudioUploadHandler(
    upload_folder=os.getenv('UPLOAD_FOLDER', '../uploads/audio'),
    data_folder=os.getenv('DATA_FOLDER', '../uploads/data')
)

whisper_service = WhisperService(
    model_name=os.getenv('WHISPER_MODEL', 'base')
)

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
        
        # Start transcription
        file_path = file_metadata['file_path']
        transcription_result = whisper_service.transcribe_audio(file_path)
        
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'whisper_model': whisper_service.model_name,
        'model_loaded': whisper_service.model is not None
    }), 200

@app.route('/api/generate-posts', methods=['POST'])
def generate_posts():
    """Generate social media posts from transcription"""
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
                result = flan_t5_service.generate_text(prompt)
                generated_text = result.get('text')

                # Process content
                processor = ContentProcessor()
                formatted_text = processor.format_for_platform(generated_text, platform)

                posts[platform] = formatted_text
            except Exception as e:
                logger.error(f"Error generating post for {platform}: {e}")

        # Save generated posts
        post_id = post_storage.save_post(
            transcription_id=transcription_id,
            platforms=platforms,
            tone=tone,
            posts=posts,
            generation_metadata=result['metadata']
        )

        return jsonify({
            'post_id': post_id,
            'posts': posts,
            'status': 'completed'
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
        result = flan_t5_service.generate_text(prompt)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

