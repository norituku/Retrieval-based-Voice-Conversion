#!/bin/bash
# RVC Voice Converter クイックリビルドスクリプト

echo "🚀 RVC Voice Converter クイックリビルド開始..."

# 既存のビルドをクリーンアップ
echo "🧹 既存のビルドをクリーンアップ中..."
rm -rf build dist

# PyInstallerでビルド（キャッシュを使用して高速化）
echo "🔨 PyInstallerでビルド中..."
/opt/homebrew/bin/python3.11 -m PyInstaller RVC_Final.spec --noconfirm

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
