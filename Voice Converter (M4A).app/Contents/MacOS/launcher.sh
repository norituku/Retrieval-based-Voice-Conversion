#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$( cd "$DIR/../.." && pwd )"
RESOURCES_DIR="$APP_DIR/Contents/Resources"

# Set environment variables
export PYTHONPATH="$RESOURCES_DIR:$PYTHONPATH"
export RVC_ROOT="$RESOURCES_DIR"
export GUI_SETTINGS_FILE="$RESOURCES_DIR/gui_settings.json"

# Suppress macOS warnings
export PYTHONDONTWRITEBYTECODE=1
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export no_proxy=*

# Change to resources directory
cd "$RESOURCES_DIR"

# Find python3 that supports tkinter
PYTHON_CMD=""
for py in /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
    if [ -x "$py" ] && $py -c "import tkinter" 2>/dev/null; then
        PYTHON_CMD="$py"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: No Python3 with tkinter support found"
    exit 1
fi

# Run the GUI
exec "$PYTHON_CMD" gui_dark_mode.py