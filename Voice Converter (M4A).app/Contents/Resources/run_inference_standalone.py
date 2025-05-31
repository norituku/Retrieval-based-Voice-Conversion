#!/usr/bin/env python3
"""
Standalone inference runner for Voice Converter app
This ensures the app uses its bundled RVC code with M4A support
"""

import sys
import os
from pathlib import Path

# Get app's resource directory
app_resources = Path(__file__).parent
sys.path.insert(0, str(app_resources))

# Set environment variables
os.environ['RVC_ROOT'] = str(app_resources)
os.environ['PYTHONPATH'] = str(app_resources) + ":" + os.environ.get('PYTHONPATH', '')

# Import and run the actual inference
if __name__ == "__main__":
    from run_inference import main
    main()