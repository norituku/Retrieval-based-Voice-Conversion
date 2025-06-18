#!/bin/bash
# RVC macOSアプリケーション作成スクリプト
# 使用方法: ./create_macos_app.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="RVC Voice Converter"
APP_BUNDLE="${PROJECT_DIR}/${APP_NAME}.app"

echo "🍎 RVC macOSアプリケーション作成ツール"
echo "📁 プロジェクトディレクトリ: ${PROJECT_DIR}"

# 1. 必要なツールの確認・インストール
echo "🔧 必要なツールを確認中..."

# Platypusの確認
if ! command -v platypus &> /dev/null; then
    echo "📦 Platypusをインストール中..."
    if command -v brew &> /dev/null; then
        brew install --cask platypus
    else
        echo "❌ Homebrewが見つかりません。手動でPlatypusをインストールしてください:"
        echo "   https://sveinbjorn.org/platypus"
        exit 1
    fi
fi

# 2. アプリ用起動スクリプトの作成
echo "📝 アプリ用起動スクリプトを作成中..."
cat > "${PROJECT_DIR}/run_gui_app.sh" << 'EOF'
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
EOF

chmod +x "${PROJECT_DIR}/run_gui_app.sh"

# 3. アイコンファイルの準備
ICON_FILE="${PROJECT_DIR}/app_icons/rvc_icon.icns"
if [ ! -f "$ICON_FILE" ]; then
    echo "⚠️  アイコンファイルが見つかりません: $ICON_FILE"
    ICON_FILE=""
fi

# 4. Platypusでアプリケーション作成
echo "🏗️  .appバンドルを作成中..."

# Platypusコマンドライン引数
PLATYPUS_ARGS=(
    -a "$APP_NAME"                          # アプリ名
    -o "None"                               # 出力タイプ（Noneでコンソール出力なし）
    -p "/bin/bash"                          # インタープリター
    -V "1.0"                                # バージョン
    -u "RVC Project Team"                   # 作者
    -I "com.rvc.voiceconverter"            # Bundle ID
    -X "*"                                  # ファイル拡張子（任意のファイル）
    -T "*"                                  # ファイルタイプ
    -B                                      # バックグラウンドで実行
    -R                                      # アプリ終了時にシェルスクリプトも終了
)

# アイコンファイルがある場合は追加
if [ -n "$ICON_FILE" ]; then
    PLATYPUS_ARGS+=(-i "$ICON_FILE")
fi

# アプリケーション作成
platypus "${PLATYPUS_ARGS[@]}" "$APP_BUNDLE" "${PROJECT_DIR}/run_gui_app.sh"

echo "✅ アプリケーション作成完了!"
echo "📱 作成されたアプリ: $APP_BUNDLE"

# 5. DMGディスクイメージの作成（オプション）
read -p "DMGディスクイメージを作成しますか？ (y/N): " create_dmg
if [[ $create_dmg =~ ^[Yy] ]]; then
    DMG_NAME="RVC-Voice-Converter-v1.0.dmg"
    echo "💿 DMGを作成中: $DMG_NAME"
    
    # 一時的なDMGディレクトリを作成
    DMG_DIR="${PROJECT_DIR}/dmg_contents"
    mkdir -p "$DMG_DIR"
    
    # アプリをDMGディレクトリにコピー
    cp -R "$APP_BUNDLE" "$DMG_DIR/"
    
    # Applicationsフォルダへのシンボリックリンクを作成
    ln -s /Applications "$DMG_DIR/Applications"
    
    # README.txtを作成
    cat > "$DMG_DIR/README.txt" << 'EOF'
RVC Voice Converter - macOS版

インストール方法:
1. "RVC Voice Converter.app"をApplicationsフォルダにドラッグ&ドロップ
2. 初回起動時は依存関係のダウンロードのため時間がかかります
3. セキュリティ警告が表示された場合は「システム環境設定」→「セキュリティとプライバシー」から許可してください

サポート: https://github.com/your-repo/Retrieval-based-Voice-Conversion
EOF
    
    # DMGを作成
    hdiutil create -volname "RVC Voice Converter" -srcfolder "$DMG_DIR" -ov -format UDZO "$DMG_NAME"
    
    # 一時ディレクトリを削除
    rm -rf "$DMG_DIR"
    
    echo "✅ DMG作成完了: $DMG_NAME"
fi

echo ""
echo "🎉 macOSアプリケーション作成プロセス完了!"
echo ""
echo "📋 次のステップ:"
echo "1. アプリをテスト: open '$APP_BUNDLE'"
echo "2. 他のMacでの動作確認"
echo "3. 必要に応じてコード署名とノータリゼーション"
echo ""
echo "⚠️  注意事項:"
echo "- 初回実行時はインターネット接続が必要です"
echo "- Homebrew/Poetry/Pythonの自動インストールには管理者権限が必要な場合があります"
echo "- 大きなAIモデルのダウンロードには時間がかかります"