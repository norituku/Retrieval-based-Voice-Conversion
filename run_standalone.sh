#!/bin/bash
# Voice Converter Standalone GUI起動スクリプト

echo "Starting Voice Converter Standalone GUI..."

# macOS固有の警告を抑制
export PYTHONWARNINGS="ignore"
export TK_SILENCE_DEPRECATION=1

# macOSのIMK関連の警告を抑制
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

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
# gui_dark_mode.pyを使用（スタンドアロン版として最も完成度が高い）
if [ -f "gui_dark_mode.py" ]; then
    echo "Starting GUI with Dark Mode interface..."
    echo "Tip: Press Ctrl+C to stop the application"
    echo ""
    
    # エラー出力を/dev/nullにリダイレクトして警告を完全に抑制
    # 標準出力は維持してアプリケーションのメッセージを表示
    $PYTHON_CMD gui_dark_mode.py 2>/dev/null
    
    # 終了コードをチェック
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        echo "GUI closed successfully."
    else
        echo "GUI exited with code: $EXIT_CODE"
    fi
else
    echo "Error: gui_dark_mode.py not found!"
    echo "Available GUI files:"
    ls -la *.py | grep gui
    exit 1
fi