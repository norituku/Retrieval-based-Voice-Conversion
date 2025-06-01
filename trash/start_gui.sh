#!/bin/bash
# Voice Converter GUI起動スクリプト（macOS用）

echo "Voice Converter GUIを起動中..."

# macOS環境変数を設定して警告を抑制
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PYOBJC_DISABLE_GIL_VALIDATION=1
export TK_SILENCE_DEPRECATION=1

# NSOpenPanelとIMKの警告を標準エラー出力から除外
python3 gui_dark_mode.py 2>&1 | grep -v -E "(NSOpenPanel|IMKCFRunLoopWakeUpReliable|The class.*overrides the method|error messaging the mach port)"
