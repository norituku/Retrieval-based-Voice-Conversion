#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add RVC to Python path
app_dir = Path(__file__).parent.parent
resources_dir = app_dir / "Resources"
sys.path.insert(0, str(resources_dir))

# Change to resources directory
os.chdir(resources_dir)

# Run the main GUI
exec(open("/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/Voice Converter (M4A).app/Contents/MacOS/Voice Converter").read())
