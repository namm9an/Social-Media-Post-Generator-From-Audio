# FFmpeg Configuration
# This file helps pydub find FFmpeg

import os
from pathlib import Path

# Get the directory where this config file is located
current_dir = Path(__file__).parent

# Set FFmpeg binary path
FFMPEG_BIN_PATH = current_dir / "ffmpeg" / "bin"
FFMPEG_BINARY = FFMPEG_BIN_PATH / "ffmpeg.exe"

# Set environment variable if FFmpeg exists locally
if FFMPEG_BINARY.exists():
    os.environ["FFMPEG_BINARY"] = str(FFMPEG_BINARY)
    print(f"FFmpeg configured: {FFMPEG_BINARY}")
else:
    print("Warning: Local FFmpeg not found, using system PATH")
