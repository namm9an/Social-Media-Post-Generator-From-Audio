#!/usr/bin/env python3
"""
FFmpeg installer for Windows
This script downloads and installs FFmpeg for Windows systems
"""

import os
import sys
import urllib.request
import zipfile
import tempfile
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_ffmpeg():
    """Install FFmpeg on Windows system"""
    try:
        # Check if FFmpeg is already installed
        if shutil.which('ffmpeg') is not None:
            logger.info("FFmpeg is already installed and available in PATH")
            return True
        
        logger.info("Installing FFmpeg for Windows...")
        
        # FFmpeg Windows build URL (official release)
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "ffmpeg.zip"
            
            # Download FFmpeg
            logger.info("Downloading FFmpeg...")
            urllib.request.urlretrieve(ffmpeg_url, zip_path)
            
            # Extract the zip file
            logger.info("Extracting FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            # Find the extracted directory
            extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir() and d.name.startswith('ffmpeg')]
            if not extracted_dirs:
                raise Exception("Could not find extracted FFmpeg directory")
            
            ffmpeg_dir = extracted_dirs[0]
            
            # Create installation directory
            install_dir = Path.home() / "ffmpeg"
            if install_dir.exists():
                shutil.rmtree(install_dir)
            
            # Copy FFmpeg to installation directory
            logger.info(f"Installing FFmpeg to {install_dir}")
            shutil.copytree(ffmpeg_dir, install_dir)
            
            # Add to PATH
            bin_dir = install_dir / "bin"
            if bin_dir.exists():
                # Add to current session PATH
                current_path = os.environ.get('PATH', '')
                if str(bin_dir) not in current_path:
                    os.environ['PATH'] = str(bin_dir) + os.pathsep + current_path
                
                logger.info("FFmpeg installed successfully!")
                logger.info(f"FFmpeg binaries are located at: {bin_dir}")
                
                # Test installation
                if shutil.which('ffmpeg') is not None:
                    logger.info("FFmpeg is now available in PATH")
                    return True
                else:
                    logger.warning("FFmpeg installed but not found in PATH")
                    logger.warning(f"Please add {bin_dir} to your system PATH manually")
                    return False
            else:
                raise Exception("FFmpeg bin directory not found after installation")
                
    except Exception as e:
        logger.error(f"Failed to install FFmpeg: {e}")
        return False

def main():
    """Main installation function"""
    logger.info("FFmpeg Installation Script for Windows")
    logger.info("=" * 50)
    
    if sys.platform != 'win32':
        logger.error("This script is designed for Windows only")
        sys.exit(1)
    
    success = install_ffmpeg()
    
    if success:
        logger.info("Installation completed successfully!")
        logger.info("You can now run your audio processing application.")
    else:
        logger.error("Installation failed!")
        logger.error("Please install FFmpeg manually from https://ffmpeg.org/download.html")
        sys.exit(1)

if __name__ == "__main__":
    main()
