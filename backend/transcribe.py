"""
Whisper Service - Complete transcription service with preprocessing and confidence scoring
Handles audio transcription using OpenAI Whisper with advanced features
"""

import whisper
import os
import json
import uuid
import logging
from datetime import datetime
from pydub import AudioSegment
from pydub.effects import normalize
import librosa
import numpy as np

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self, model_name="base"):
        """
        Initialize Whisper transcription service.
        
        Args:
            model_name (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_name = model_name
        self.model = None
        self.transcriptions_json = os.path.join("uploads", "transcriptions.json")
        
        # Initialize JSON file if it doesn't exist
        if not os.path.exists(self.transcriptions_json):
            with open(self.transcriptions_json, 'w') as f:
                json.dump({}, f)
    
    def load_whisper_model(self):
        """
        Load Whisper model once and cache it.
        
        Returns:
            whisper.Whisper: Loaded Whisper model
        """
        if self.model is None:
            try:
                logger.info(f"Loading Whisper model: {self.model_name}")
                self.model = whisper.load_model(self.model_name)
                logger.info(f"Whisper model {self.model_name} loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {str(e)}")
                raise
        return self.model
    
    def preprocess_audio(self, file_path):
        """
        Preprocess audio file for better transcription results.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            str: Path to preprocessed audio file
        """
        try:
            # Load audio file with pydub
            audio = AudioSegment.from_file(file_path)
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Normalize audio
            audio = normalize(audio)
            
            # Set sample rate to 16kHz (Whisper's preferred rate)
            audio = audio.set_frame_rate(16000)
            
            # Export preprocessed audio
            preprocessed_path = file_path.replace('.', '_preprocessed.')
            audio.export(preprocessed_path, format="wav")
            
            logger.info(f"Audio preprocessed: {preprocessed_path}")
            return preprocessed_path
            
        except Exception as e:
            logger.warning(f"Audio preprocessing failed, using original file: {str(e)}")
            return file_path
    
    def get_transcription_confidence(self, result):
        """
        Extract confidence scores from Whisper transcription result.
        
        Args:
            result (dict): Whisper transcription result
            
        Returns:
            dict: Confidence metrics
        """
        try:
            # Extract segment-level confidence scores
            segments = result.get('segments', [])
            if not segments:
                return {
                    'overall_confidence': 0.0,
                    'word_confidence': 0.0,
                    'segment_count': 0
                }
            
            # Calculate average confidence across segments
            segment_confidences = []
            word_confidences = []
            
            for segment in segments:
                if 'avg_logprob' in segment:
                    # Convert log probability to confidence (approximate)
                    confidence = min(1.0, max(0.0, np.exp(segment['avg_logprob'])))
                    segment_confidences.append(confidence)
                
                # Extract word-level confidence if available
                if 'words' in segment:
                    for word in segment['words']:
                        if 'probability' in word:
                            word_confidences.append(word['probability'])
            
            overall_confidence = np.mean(segment_confidences) if segment_confidences else 0.0
            word_confidence = np.mean(word_confidences) if word_confidences else 0.0
            
            return {
                'overall_confidence': float(overall_confidence),
                'word_confidence': float(word_confidence),
                'segment_count': len(segments)
            }
            
        except Exception as e:
            logger.warning(f"Could not extract confidence scores: {str(e)}")
            return {
                'overall_confidence': 0.0,
                'word_confidence': 0.0,
                'segment_count': 0
            }
    
    def transcribe_audio(self, file_path, language=None, task="transcribe"):
        """
        Main transcription function with preprocessing and confidence scoring.
        
        Args:
            file_path (str): Path to audio file
            language (str): Language code (auto-detect if None)
            task (str): 'transcribe' or 'translate'
            
        Returns:
            dict: Transcription result with metadata
        """
        try:
            # Load model
            model = self.load_whisper_model()
            
            # Preprocess audio
            preprocessed_path = self.preprocess_audio(file_path)
            
            # Transcribe audio
            logger.info(f"Starting transcription: {file_path}")
            start_time = datetime.now()
            
            result = model.transcribe(
                preprocessed_path,
                language=language,
                task=task,
                word_timestamps=True,
                verbose=False
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Get confidence scores
            confidence_metrics = self.get_transcription_confidence(result)
            
            # Clean up preprocessed file if it's different from original
            if preprocessed_path != file_path:
                try:
                    os.remove(preprocessed_path)
                except Exception as e:
                    logger.warning(f"Could not remove preprocessed file: {str(e)}")
            
            # Prepare result
            transcription_result = {
                'transcription_id': str(uuid.uuid4()),
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
                'confidence_metrics': confidence_metrics,
                'processing_time': processing_time,
                'model_used': self.model_name,
                'task': task,
                'segments': result.get('segments', []),
                'transcribed_at': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            logger.info(f"Transcription completed in {processing_time:.2f}s")
            return transcription_result
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {
                'transcription_id': str(uuid.uuid4()),
                'text': '',
                'language': 'unknown',
                'confidence_metrics': {'overall_confidence': 0.0, 'word_confidence': 0.0, 'segment_count': 0},
                'processing_time': 0.0,
                'model_used': self.model_name,
                'task': task,
                'segments': [],
                'transcribed_at': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e)
            }
    
    def save_transcription(self, file_id, transcription_result):
        """
        Save transcription result to JSON storage.
        
        Args:
            file_id (str): Original file ID
            transcription_result (dict): Transcription result
        """
        try:
            # Read existing transcriptions
            with open(self.transcriptions_json, 'r') as f:
                transcriptions = json.load(f)
            
            # Add file_id to transcription result
            transcription_result['file_id'] = file_id
            
            # Save transcription
            transcriptions[transcription_result['transcription_id']] = transcription_result
            
            # Write back to file
            with open(self.transcriptions_json, 'w') as f:
                json.dump(transcriptions, f, indent=2)
            
            logger.info(f"Transcription saved: {transcription_result['transcription_id']}")
            
        except Exception as e:
            logger.error(f"Error saving transcription: {str(e)}")
            raise
    
    def get_transcription(self, transcription_id):
        """
        Get transcription by ID.
        
        Args:
            transcription_id (str): Transcription identifier
            
        Returns:
            dict: Transcription data or None
        """
        try:
            with open(self.transcriptions_json, 'r') as f:
                transcriptions = json.load(f)
            return transcriptions.get(transcription_id)
        except Exception as e:
            logger.error(f"Error reading transcription: {str(e)}")
            return None
    
    def get_transcriptions_by_file_id(self, file_id):
        """
        Get all transcriptions for a specific file.
        
        Args:
            file_id (str): File identifier
            
        Returns:
            list: List of transcriptions for the file
        """
        try:
            with open(self.transcriptions_json, 'r') as f:
                transcriptions = json.load(f)
            
            file_transcriptions = []
            for transcription_id, transcription_data in transcriptions.items():
                if transcription_data.get('file_id') == file_id:
                    file_transcriptions.append(transcription_data)
            
            return file_transcriptions
        except Exception as e:
            logger.error(f"Error reading transcriptions: {str(e)}")
            return []

# Test function
def test_whisper_service():
    """Test Whisper service functionality."""
    try:
        service = WhisperService()
        model = service.load_whisper_model()
        print("✓ Whisper service initialized successfully")
        print(f"✓ Model: {service.model_name}")
        print(f"✓ Model loaded: {model is not None}")
        return True
    except Exception as e:
        print(f"✗ Whisper service initialization failed: {e}")
        return False

if __name__ == "__main__":
    test_whisper_service()
