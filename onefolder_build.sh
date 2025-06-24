#!/bin/bash
# RVC Voice Converter OneFolder ビルドスクリプト

echo "🚀 RVC Voice Converter OneFolder ビルド開始..."

# 既存のビルドとキャッシュを完全にクリーンアップ
echo "🧹 完全クリーンアップ中..."
rm -rf build dist
rm -rf /Users/norikene_satoshi/Library/Application\ Support/pyinstaller

# PyInstallerでビルド（OneFolder版）
echo "🔨 PyInstallerでビルド中（OneFolder版）..."
/opt/homebrew/bin/python3.11 -m PyInstaller RVC_Final_OneFolder.spec --clean --noconfirm

if [ -d "dist/RVC Voice Converter Final.app" ]; then
    echo "✅ ビルド成功!"
    
    # アプリケーションサイズを表示
    APP_SIZE=$(du -sh "dist/RVC Voice Converter Final.app" | cut -f1)
    echo "📦 アプリケーションサイズ: $APP_SIZE"
    
    # アプリケーションを起動
    echo "🚀 アプリケーションを起動中..."
    open "dist/RVC Voice Converter Final.app"
else
    echo "❌ ビルド失敗!"
    exit 1
fi
