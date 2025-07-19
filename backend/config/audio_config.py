"""Audio processing configuration."""
import os
import logging
from pydub import AudioSegment
from pydub.utils import which

logger = logging.getLogger(__name__)

def configure_audio_processing():
    """Configure audio processing with proper codec paths."""
    try:
        # Try to find ffmpeg in common locations
        possible_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            which("ffmpeg")
        ]
        
        ffmpeg_path = None
        for path in possible_paths:
            if path and os.path.exists(path):
                ffmpeg_path = path
                break
        
        if ffmpeg_path:
            AudioSegment.converter = ffmpeg_path
            AudioSegment.ffmpeg = ffmpeg_path
            AudioSegment.ffprobe = ffmpeg_path.replace("ffmpeg", "ffprobe")
            logger.info(f"FFmpeg configured at: {ffmpeg_path}")
        else:
            logger.warning("FFmpeg not found. Audio processing may be limited.")
            
    except Exception as e:
        logger.error(f"Error configuring audio processing: {e}")
        
def test_audio_processing():
    """Test if audio processing is working."""
    try:
        # Create a simple test audio segment
        from pydub.generators import Sine
        tone = Sine(440).to_audio_segment(duration=100)
        logger.info("Audio processing test successful")
        return True
    except Exception as e:
        logger.error(f"Audio processing test failed: {e}")
        return False
