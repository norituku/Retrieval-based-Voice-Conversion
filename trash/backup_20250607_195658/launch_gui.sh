#!/bin/bash
# GUI起動スクリプト - macOS tkinter対応版（改良版）

echo "🚀 RVC Dark Mode GUI起動中..."

# tkinter対応Pythonを優先順位で定義（診断結果を基に）
PYTHON_PATHS=(
    "/opt/homebrew/bin/python3"           # Homebrew Python（推奨）
    "/usr/local/bin/python3"              # 古いHomebrew Python
    "/usr/bin/python3"                    # システムPython
    "/System/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
    "/System/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"
    "/System/Library/Frameworks/Python.framework/Versions/3.9/bin/python3"
)

# GUI起動前に必要な環境変数を設定
export SKIP_POETRY_CHECK=1
export PYTHONUNBUFFERED=1

# tkinterテスト関数
test_tkinter() {
    local python_path="$1"
    if [ ! -f "$python_path" ]; then
        return 1
    fi
    
    # tkinterの実際のウィンドウ作成テスト
    if $python_path -c "
import tkinter as tk
try:
    root = tk.Tk()
    root.withdraw()
    print('SUCCESS')
    root.destroy()
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
" 2>/dev/null | grep -q "SUCCESS"; then
        return 0
    else
        return 1
    fi
}

# Python版本情報を取得
get_python_version() {
    local python_path="$1"
    $python_path --version 2>/dev/null | cut -d' ' -f2
}

echo "🔍 tkinter対応Pythonを検索中..."

# 動作するPythonを見つける
for python_path in "${PYTHON_PATHS[@]}"; do
    if test_tkinter "$python_path"; then
        version=$(get_python_version "$python_path")
        echo "✅ tkinter対応Python発見: $python_path (Python $version)"
        echo "🎨 GUIを起動しています..."
        
        # GUI起動（tkinter対応Pythonを使用）
        echo "🎯 Starting GUI with Python: $python_path"
        echo "🔧 Using system Python for tkinter compatibility..."
        exec $python_path gui_dark_mode_enhanced.py "$@"
    else
        echo "❌ $python_path: tkinter不可"
    fi
done

# すべて失敗した場合
echo ""
echo "❌ エラー: tkinter対応のPythonが見つかりません"
echo ""
echo "🛠️  修復方法:"
echo "1. Homebrewでtkinter付きPythonをインストール:"
echo "   brew install python-tk"
echo ""
echo "2. または、pyenvでtk付きPythonを再インストール:"
echo "   brew install tcl-tk"
echo "   pyenv install 3.11.9"
echo ""
echo "3. 手動で動作するPythonを使用:"
echo "   /opt/homebrew/bin/python3 gui_dark_mode_enhanced.py"
echo ""
exit 1