#!/bin/bash
# Voice Converter 起動スクリプト（正しいPython環境を使用）

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Voice Converter を起動中..."

# 環境変数を設定
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PYOBJC_DISABLE_GIL_VALIDATION=1
export TK_SILENCE_DEPRECATION=1

# 正しいPython環境（3.11.9）でgui_dark_modeを起動
echo "Python 3.11.9環境で起動します..."
/usr/local/bin/python3 gui_dark_mode.py "$@"

# 代替オプション（Python 3.9.6を使用する場合）
# /usr/bin/python3 gui_fixed.py "$@"
