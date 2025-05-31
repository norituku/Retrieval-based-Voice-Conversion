#!/usr/bin/env python3
"""
Voice Converter - Simple Nuitka Build Script for macOS
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_app():
    """シンプルなアプリビルド"""
    project_dir = Path(__file__).parent
    
    print("🎵 Voice Converter - Simple Build")
    print("=================================")
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for dir_name in ['build', 'dist']:
        dir_path = project_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   ✓ Removed {dir_name}")
    
    # Build command
    cmd = [
        sys.executable, '-m', 'nuitka',
        '--standalone',
        '--macos-create-app-bundle',
        '--macos-app-name=Voice Converter',
        '--macos-app-version=1.0.0',
        '--macos-app-mode=gui',
        '--enable-plugin=tk-inter',
        '--static-libpython=no',
        '--include-data-dir=rvc=rvc',
        '--include-data-file=gui_settings.json=gui_settings.json',
        '--output-dir=dist',
        '--remove-output',
        '--show-progress',
        '--assume-yes-for-downloads',
        'gui_dark_mode.py'
    ]
    
    print("📋 Running simplified Nuitka command...")
    print(f"   {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=project_dir, check=True)
        print("✅ Build successful!")
        
        # Check if app was created
        app_path = project_dir / "dist" / "Voice Converter.app"
        if app_path.exists():
            print(f"🚀 App created at: {app_path}")
        else:
            print("❌ App bundle not found")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with exit code {e.returncode}")
        return False
        
    return True

if __name__ == "__main__":
    build_app()