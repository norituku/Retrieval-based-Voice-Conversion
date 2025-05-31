#!/bin/bash
# Voice Converter GUI起動スクリプト - Poetry環境を強制

cd "$(dirname "$0")"

echo "Voice Converter GUIを起動中..."

# Poetry環境を確実に使用
export POETRY_ACTIVE=1
export POETRY_VIRTUALENVS_IN_PROJECT=0

# macOS環境変数を設定
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export TK_SILENCE_DEPRECATION=1

# Conda環境を無効化
unset CONDA_DEFAULT_ENV
unset CONDA_PREFIX
unset CONDA_PYTHON_EXE
unset CONDA_EXE
unset CONDA_PROMPT_MODIFIER

# GUIを起動（警告を抑制）
python3 gui_dark_mode.py 2>&1 | grep -v -E "(NSOpenPanel|IMKCFRunLoopWakeUpReliable|The class.*overrides the method|error messaging the mach port)"
