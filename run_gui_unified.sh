#!/bin/bash
# 統一されたGUI起動スクリプト
# 使用方法: 
#   ./run_gui_unified.sh              # リファクタリング版GUI
#   ./run_gui_unified.sh --legacy     # レガシー版GUI
#   ./run_gui_unified.sh --standalone # スタンドアロン版

echo "Voice Converter GUI Launcher"
echo "============================="

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

# 引数に応じて起動するGUIを選択
case "${1:-default}" in
    --legacy)
        echo "Starting Legacy Dark Mode GUI..."
        $PYTHON_CMD gui_dark_mode.py
        ;;
    --standalone)
        echo "Starting Standalone GUI..."
        $PYTHON_CMD gui_nuitka_standalone.py
        ;;
    --help|-h)
        echo "Usage: $0 [option]"
        echo "Options:"
        echo "  (no option)   Start refactored GUI (recommended)"
        echo "  --legacy      Start legacy dark mode GUI"
        echo "  --standalone  Start standalone GUI"
        echo "  --help, -h    Show this help message"
        exit 0
        ;;
    *)
        echo "Starting Refactored GUI (recommended)..."
        $PYTHON_CMD gui/main.py
        ;;
esac

echo "GUI closed."