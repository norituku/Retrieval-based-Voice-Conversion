#!/bin/bash
# RVC ハイブリッドスタンドアロンアプリ起動スクリプト

set -e

# アプリケーション内のリソースディレクトリを取得
if [[ "$0" == *.app/Contents/Resources/* ]]; then
    # .app内部から実行された場合
    BUNDLE_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
    RESOURCES_DIR="$BUNDLE_DIR/Contents/Resources"
    PROJECT_DIR="$RESOURCES_DIR"
else
    # 通常のディレクトリから実行された場合
    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    RESOURCES_DIR="$PROJECT_DIR"
fi

echo "🎵 RVC Voice Converter - ハイブリッドスタンドアロン版"
echo "📁 プロジェクトディレクトリ: $PROJECT_DIR"

cd "$PROJECT_DIR"

# 既存のvenv_tkinter_fix環境が利用可能かチェック
VENV_TKINTER="$PROJECT_DIR/venv_tkinter_fix"

if [ ! -d "$VENV_TKINTER" ]; then
    echo "🔧 tkinter対応仮想環境を作成中..."
    
    # Homebrew Python 3.11の確認・インストール
    if [ ! -f "/opt/homebrew/bin/python3.11" ]; then
        echo "📦 Homebrew Python 3.11をインストール中..."
        if ! command -v brew &> /dev/null; then
            echo "📦 Homebrewをインストール中..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        brew install python@3.11 python-tk@3.11
    fi
    
    # tkinter対応仮想環境作成
    /opt/homebrew/bin/python3.11 -m venv "$VENV_TKINTER"
    
    echo "📦 基本パッケージをインストール中..."
    "$VENV_TKINTER/bin/python" -m ensurepip --upgrade
    "$VENV_TKINTER/bin/pip" install click
fi

# Poetry環境セットアップ
if command -v poetry &> /dev/null; then
    echo "🔧 Poetry環境をセットアップ中..."
    poetry install --only=main
    echo "✅ Poetry環境セットアップ完了"
fi

# GUIを起動
echo "🚀 GUI起動中..."
"$VENV_TKINTER/bin/python" "$PROJECT_DIR/gui_dark_mode.py"
