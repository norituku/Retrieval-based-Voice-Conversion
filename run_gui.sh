#!/bin/bash
# RVC GUI 一発実行スクリプト
# 使用方法: ./run_gui.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_TKINTER="${PROJECT_DIR}/venv_tkinter_fix"

echo "🎵 RVC GUI 起動スクリプト"
echo "📁 プロジェクトディレクトリ: ${PROJECT_DIR}"

# 1. tkinter対応の仮想環境が存在しない場合は作成
if [ ! -d "${VENV_TKINTER}" ]; then
    echo "🔧 tkinter対応仮想環境を作成中..."
    /opt/homebrew/bin/python3.11 -m venv "${VENV_TKINTER}"
    
    echo "📦 pipとclickをインストール中..."
    "${VENV_TKINTER}/bin/python" -m ensurepip --upgrade
    "${VENV_TKINTER}/bin/pip" install click
fi

# 2. Poetry環境をセットアップ
echo "🔧 Poetry環境をセットアップ中..."
cd "${PROJECT_DIR}"
echo "📦 Poetry依存関係をインストール中（初回は時間がかかります）..."
poetry install --only=main
echo "✅ Poetry環境セットアップ完了"

# 3. GUIを起動
echo "🚀 GUI起動中..."
echo "⚠️  初回起動時は依存関係のインストールで時間がかかる場合があります"

# tkinter環境でGUIを実行
"${VENV_TKINTER}/bin/python" "${PROJECT_DIR}/gui_dark_mode.py"