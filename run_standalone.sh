#!/bin/bash
# Voice Converter Standalone GUI起動スクリプト

echo "Starting Voice Converter Standalone GUI..."

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# rvc環境のPythonを直接使用
PYTHON_CMD="/opt/homebrew/Caskroom/miniconda/base/envs/rvc/bin/python"

# Pythonパスが存在するか確認
if [ ! -f "$PYTHON_CMD" ]; then
    echo "Error: RVC environment Python not found at $PYTHON_CMD"
    echo "Please ensure the RVC conda environment is installed."
    echo "You can install it with: conda create -n rvc python=3.11"
    exit 1
fi

# スタンドアロンGUIを起動
$PYTHON_CMD gui_nuitka_standalone.py