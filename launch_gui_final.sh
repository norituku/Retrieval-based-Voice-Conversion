#!/bin/bash
# 最終版GUI起動スクリプト - 混合モード対応

echo "🚀 RVC Enhanced GUI起動中..."

# 必要な環境変数設定
export SKIP_POETRY_CHECK=1
export PYTHONUNBUFFERED=1

# tkinter対応Pythonを使用してGUIを起動
TKINTER_PYTHON="/opt/homebrew/bin/python3"

if [ -f "$TKINTER_PYTHON" ]; then
    echo "✅ tkinter対応Python: $TKINTER_PYTHON"
    echo "🎨 Enhanced GUIを起動しています..."
    
    # GUI起動
    exec $TKINTER_PYTHON gui_dark_mode_enhanced.py "$@"
else
    echo "❌ tkinter対応Pythonが見つかりません"
    echo "以下のコマンドでインストールしてください:"
    echo "brew install python-tk"
    exit 1
fi