#!/bin/bash
# Voice Converter GUI - Poetry環境で実行

cd "$(dirname "$0")"

echo "Voice Converter GUIをPoetry環境で起動中..."

# macOS環境変数を設定
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export TK_SILENCE_DEPRECATION=1

# Poetry環境でGUIを実行
poetry run python gui_dark_mode.py 2>&1 | grep -v -E "(NSOpenPanel|IMKCFRunLoopWakeUpReliable|The class.*overrides the method|error messaging the mach port)"
