#!/bin/bash
# Voice Converter スタンドアロンアプリビルドスクリプト（修正版）

set -e

echo "🚀 Voice Converter スタンドアロンアプリのビルドを開始します..."

# プロジェクトディレクトリ
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# ビルドディレクトリのクリーンアップ
echo "📁 ビルドディレクトリをクリーンアップ中..."
rm -rf build dist

# PyInstallerビルド実行
echo "🔨 PyInstallerでアプリをビルド中..."
pyinstaller voice_converter_fixed.spec --clean

# ビルド成功確認
if [ -d "dist/VoiceConverter.app" ]; then
    echo "✅ ビルド成功！"
    
    # アプリのサイズ確認
    APP_SIZE=$(du -sh "dist/VoiceConverter.app" | cut -f1)
    echo "📦 アプリサイズ: $APP_SIZE"
    
    # 必要なライブラリの存在確認
    echo "🔍 重要なファイルの存在確認..."
    
    # torch._Cの確認
    if find "dist/VoiceConverter.app" -name "*_C*.so" -o -name "*libtorch*.dylib" | grep -q .; then
        echo "✅ PyTorch C拡張が含まれています"
    else
        echo "⚠️  警告: PyTorch C拡張が見つかりません"
    fi
    
    # RVCモジュールの確認
    if [ -d "dist/VoiceConverter.app/Contents/Resources/rvc" ]; then
        echo "✅ RVCモジュールが含まれています"
    else
        echo "⚠️  警告: RVCモジュールが見つかりません"
    fi
    
    # 署名
    echo "🔐 アプリに署名中..."
    codesign --force --deep --sign - "dist/VoiceConverter.app"
    
    # DMG作成オプション
    read -p "💿 DMGファイルを作成しますか？ (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        DMG_NAME="VoiceConverter_Standalone.dmg"
        
        # 既存のDMGを削除
        rm -f "$DMG_NAME"
        
        # DMG作成
        echo "💿 DMGファイルを作成中..."
        hdiutil create -volname "Voice Converter" \
                      -srcfolder "dist/VoiceConverter.app" \
                      -ov -format UDZO \
                      "$DMG_NAME"
        
        echo "✅ DMGファイル作成完了: $DMG_NAME"
    fi
    
    echo ""
    echo "🎉 ビルド完了！"
    echo ""
    echo "アプリを起動するには:"
    echo "  open dist/VoiceConverter.app"
    echo ""
    echo "⚠️  初回起動時の注意:"
    echo "  1. セキュリティ警告が出た場合は、システム設定 > プライバシーとセキュリティで許可"
    echo "  2. model_dirディレクトリにモデルファイルを配置してください"
    
else
    echo "❌ ビルド失敗！"
    echo "エラーログを確認してください。"
    exit 1
fi
