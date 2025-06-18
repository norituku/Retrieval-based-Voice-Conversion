#!/bin/bash
# RVC GUI - macOSアプリ版起動スクリプト

set -e

# アプリケーションディレクトリを取得
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$APP_DIR" == *.app/Contents/Resources ]]; then
    # .app内部から実行された場合
    PROJECT_DIR="$(dirname "$(dirname "$(dirname "$APP_DIR")")")/RVC-Project"
else
    # 通常のディレクトリから実行された場合
    PROJECT_DIR="$APP_DIR"
fi

echo "🎵 RVC Voice Converter 起動中..."
echo "📁 プロジェクトディレクトリ: ${PROJECT_DIR}"

# プロジェクトディレクトリが存在しない場合は作成
if [ ! -d "${PROJECT_DIR}" ]; then
    echo "📁 プロジェクトディレクトリを作成中..."
    mkdir -p "${PROJECT_DIR}"
    cd "${PROJECT_DIR}"
    
    # Gitリポジトリのクローン（初回のみ）
    echo "📥 RVCプロジェクトをダウンロード中..."
    git clone https://github.com/your-repo/Retrieval-based-Voice-Conversion.git .
fi

cd "${PROJECT_DIR}"

# 必要なツールの自動インストール
echo "🔧 システム要件をチェック中..."

# 1. Homebrewの確認・インストール
if ! command -v brew &> /dev/null; then
    echo "📦 Homebrewをインストール中..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# 2. Python 3.11とpython-tkの確認・インストール
if [ ! -f "/opt/homebrew/bin/python3.11" ]; then
    echo "🐍 Python 3.11をインストール中..."
    brew install python@3.11 python-tk@3.11
fi

# 3. Poetryの確認・インストール
if ! command -v poetry &> /dev/null; then
    echo "📦 Poetryをインストール中..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# 4. run_gui.shの実行
echo "🚀 RVC GUIを起動中..."
if [ -f "${PROJECT_DIR}/run_gui.sh" ]; then
    chmod +x "${PROJECT_DIR}/run_gui.sh"
    "${PROJECT_DIR}/run_gui.sh"
else
    echo "❌ run_gui.shが見つかりません。"
    echo "プロジェクトの整合性を確認してください。"
    exit 1
fi
