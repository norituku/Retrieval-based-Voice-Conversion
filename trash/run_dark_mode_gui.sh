#!/bin/bash

# Voice Converter Dark Mode GUI 実行スクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# プロジェクトディレクトリに移動
cd "$SCRIPT_DIR"

# Poetry環境のアクティベート
if command -v poetry &> /dev/null; then
    echo "Starting Voice Converter with Poetry..."
    poetry run python gui_dark_mode.py
else
    echo "Poetry not found. Trying to install..."
    
    # Homebrewがインストールされているか確認
    if command -v brew &> /dev/null; then
        echo "Installing Poetry via Homebrew..."
        brew install poetry
        poetry install
        poetry run python gui_dark_mode.py
    else
        echo "Error: Poetry is required to run this application."
        echo "Please install Poetry: https://python-poetry.org/docs/#installation"
        exit 1
    fi
fi
