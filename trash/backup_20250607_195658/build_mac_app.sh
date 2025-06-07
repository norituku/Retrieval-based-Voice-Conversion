#!/bin/bash
# Voice Converter Mac App ビルドスクリプト

echo "Building Voice Converter for macOS..."

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# アプリケーション情報
APP_NAME="Voice Converter"
APP_VERSION="1.0.0"
BUNDLE_ID="com.rvc.voiceconverter"
MAIN_SCRIPT="gui_dark_mode.py"
OUTPUT_DIR="dist"

# クリーンアップ
echo "Cleaning previous builds..."
rm -rf build dist *.build *.dist

# 必要なディレクトリを作成
mkdir -p "$OUTPUT_DIR"

# Nuitkaでビルド
echo "Building with Nuitka..."
python -m nuitka \
    --standalone \
    --macos-create-app-bundle \
    --macos-app-name="$APP_NAME" \
    --macos-app-version="$APP_VERSION" \
    --macos-app-mode=gui \
    --enable-plugin=tk-inter \
    --include-data-dir=configs=configs \
    --include-data-dir=model_dir=model_dir \
    --include-data-file=gui_settings.json=gui_settings.json \
    --include-module=tkinter \
    --include-module=tkinter.ttk \
    --include-module=tkinter.filedialog \
    --include-module=tkinter.messagebox \
    --include-module=json \
    --include-module=subprocess \
    --include-module=threading \
    --include-module=pathlib \
    --include-module=datetime \
    --include-module=os \
    --include-module=sys \
    --include-module=math \
    --include-module=time \
    --assume-yes-for-downloads \
    --output-dir="$OUTPUT_DIR" \
    --remove-output \
    --quiet \
    --show-progress \
    --show-memory \
    "$MAIN_SCRIPT"

# アプリバンドルの場所を確認
APP_BUNDLE="$OUTPUT_DIR/$APP_NAME.app"

if [ -d "$APP_BUNDLE" ]; then
    echo "App bundle created successfully at: $APP_BUNDLE"
    
    # アイコンを設定（もしあれば）
    if [ -f "icon.icns" ]; then
        echo "Setting app icon..."
        cp icon.icns "$APP_BUNDLE/Contents/Resources/icon.icns"
    fi
    
    # コード署名（オプション）
    # echo "Code signing..."
    # codesign --force --deep --sign - "$APP_BUNDLE"
    
    echo "Build completed successfully!"
    echo "You can now run the app: open '$APP_BUNDLE'"
else
    echo "Build failed! App bundle not found."
    exit 1
fi