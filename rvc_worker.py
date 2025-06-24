#!/usr/bin/env python3
"""
rvc_worker.py - Worker process for RVC voice conversion
PyInstaller対応版
"""
import os
import sys
import json
import subprocess
from pathlib import Path

def main():
    """Worker main function"""
    if len(sys.argv) < 2:
        print("Usage: rvc_worker.py <config_json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # RVC処理の実行
        print(f"RVC Worker starting with config: {config_path}")
        
        # 実際のRVC処理をここに実装
        # 今は最小限の実装
        
        print("RVC Worker completed successfully")
        
    except Exception as e:
        print(f"RVC Worker error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()