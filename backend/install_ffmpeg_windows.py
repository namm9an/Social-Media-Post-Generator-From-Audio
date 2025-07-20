#!/usr/bin/env python3
"""
FFmpeg installation script for Windows
Downloads and configures FFmpeg for audio processing
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path
import winreg

def check_ffmpeg_installed():
    """Check if FFmpeg is already installed and accessible."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ FFmpeg is already installed and accessible")
            return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    print("✗ FFmpeg not found in system PATH")
    return False

def download_ffmpeg():
    """Download FFmpeg for Windows."""
    print("Downloading FFmpeg for Windows...")
    
    # FFmpeg download URL (static build)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    download_path = Path("ffmpeg-release-essentials.zip")
    
    try:
        print(f"Downloading from: {ffmpeg_url}")
        urllib.request.urlretrieve(ffmpeg_url, download_path)
        print(f"✓ Downloaded FFmpeg to: {download_path}")
        return download_path
    except Exception as e:
        print(f"✗ Failed to download FFmpeg: {e}")
        return None

def extract_ffmpeg(zip_path):
    """Extract FFmpeg archive."""
    print("Extracting FFmpeg...")
    
    extract_dir = Path("ffmpeg_temp")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the extracted folder (it has a version number)
        extracted_folders = list(extract_dir.glob("ffmpeg-*"))
        if not extracted_folders:
            raise Exception("No FFmpeg folder found in archive")
        
        ffmpeg_folder = extracted_folders[0]
        print(f"✓ Extracted FFmpeg to: {ffmpeg_folder}")
        return ffmpeg_folder
        
    except Exception as e:
        print(f"✗ Failed to extract FFmpeg: {e}")
        return None

def install_ffmpeg_locally(ffmpeg_folder):
    """Install FFmpeg to local project directory."""
    print("Installing FFmpeg locally...")
    
    # Create local ffmpeg directory
    local_ffmpeg_dir = Path("ffmpeg")
    local_ffmpeg_dir.mkdir(exist_ok=True)
    
    try:
        # Copy ffmpeg binaries
        bin_source = ffmpeg_folder / "bin"
        bin_dest = local_ffmpeg_dir / "bin"
        
        if bin_source.exists():
            shutil.copytree(bin_source, bin_dest, dirs_exist_ok=True)
            print(f"✓ FFmpeg binaries installed to: {bin_dest}")
            
            # Make sure ffmpeg.exe exists
            ffmpeg_exe = bin_dest / "ffmpeg.exe"
            if ffmpeg_exe.exists():
                print("✓ ffmpeg.exe found in local installation")
                return bin_dest
            else:
                print("✗ ffmpeg.exe not found in installation")
                return None
        else:
            print("✗ Source bin directory not found")
            return None
            
    except Exception as e:
        print(f"✗ Failed to install FFmpeg locally: {e}")
        return None

def add_to_system_path(ffmpeg_bin_path):
    """Add FFmpeg to system PATH (requires admin privileges)."""
    try:
        # Try to add to user PATH first (doesn't require admin)
        print("Adding FFmpeg to user PATH...")
        
        # Get current user PATH
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
        try:
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""
        
        # Add FFmpeg path if not already present
        ffmpeg_path_str = str(ffmpeg_bin_path.absolute())
        if ffmpeg_path_str not in current_path:
            new_path = f"{current_path};{ffmpeg_path_str}" if current_path else ffmpeg_path_str
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✓ Added to user PATH: {ffmpeg_path_str}")
        else:
            print("✓ FFmpeg already in user PATH")
            
        winreg.CloseKey(key)
        return True
        
    except Exception as e:
        print(f"✗ Failed to add to PATH: {e}")
        print("You may need to add FFmpeg to PATH manually")
        return False

def setup_environment_variable(ffmpeg_bin_path):
    """Set up FFMPEG_BINARY environment variable for pydub."""
    ffmpeg_exe = ffmpeg_bin_path / "ffmpeg.exe"
    
    if ffmpeg_exe.exists():
        # Set environment variable for current session
        os.environ["FFMPEG_BINARY"] = str(ffmpeg_exe)
        print(f"✓ Set FFMPEG_BINARY environment variable: {ffmpeg_exe}")
        
        # Try to set permanently for user
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, "FFMPEG_BINARY", 0, winreg.REG_SZ, str(ffmpeg_exe))
            winreg.CloseKey(key)
            print("✓ Set FFMPEG_BINARY permanently in user environment")
        except Exception as e:
            print(f"Warning: Could not set permanent environment variable: {e}")
        
        return True
    else:
        print("✗ ffmpeg.exe not found for environment variable setup")
        return False

def cleanup_temp_files():
    """Clean up temporary download and extraction files."""
    try:
        # Remove zip file
        zip_path = Path("ffmpeg-release-essentials.zip")
        if zip_path.exists():
            zip_path.unlink()
            print("✓ Cleaned up download file")
        
        # Remove temp extraction directory
        temp_dir = Path("ffmpeg_temp")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print("✓ Cleaned up temporary files")
            
    except Exception as e:
        print(f"Warning: Could not clean up temp files: {e}")

def test_installation():
    """Test the FFmpeg installation."""
    print("Testing FFmpeg installation...")
    
    try:
        # Test direct path first
        local_ffmpeg = Path("ffmpeg/bin/ffmpeg.exe")
        if local_ffmpeg.exists():
            result = subprocess.run([str(local_ffmpeg), '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✓ Local FFmpeg installation working")
                return True
        
        # Test system PATH
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ FFmpeg accessible from system PATH")
            return True
            
    except Exception as e:
        print(f"✗ FFmpeg test failed: {e}")
    
    return False

def create_ffmpeg_config():
    """Create configuration file for FFmpeg paths."""
    config_content = '''# FFmpeg Configuration
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
'''
    
    config_path = Path("ffmpeg_config.py")
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✓ Created FFmpeg configuration: {config_path}")

def main():
    """Main installation function."""
    print("=== FFmpeg Installation for Windows ===\n")
    
    # Check if already installed
    if check_ffmpeg_installed():
        print("FFmpeg is already available. No installation needed.")
        return True
    
    print("Installing FFmpeg...")
    
    # Download FFmpeg
    zip_path = download_ffmpeg()
    if not zip_path:
        return False
    
    # Extract FFmpeg
    ffmpeg_folder = extract_ffmpeg(zip_path)
    if not ffmpeg_folder:
        return False
    
    # Install locally
    ffmpeg_bin_path = install_ffmpeg_locally(ffmpeg_folder)
    if not ffmpeg_bin_path:
        return False
    
    # Set up environment
    setup_environment_variable(ffmpeg_bin_path)
    add_to_system_path(ffmpeg_bin_path)
    
    # Create config
    create_ffmpeg_config()
    
    # Clean up
    cleanup_temp_files()
    
    # Test installation
    if test_installation():
        print("\n🎉 FFmpeg installation completed successfully!")
        print("\nNext steps:")
        print("1. Restart your terminal/command prompt")
        print("2. Restart your Python application")
        print("3. FFmpeg should now work with pydub for audio processing")
        return True
    else:
        print("\n❌ FFmpeg installation completed but testing failed")
        print("You may need to restart your terminal and try again")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
