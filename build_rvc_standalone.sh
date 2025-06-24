#!/bin/bash

echo "🚀 RVC Standalone Build Script (Ultra Think Edition)"
echo "=================================================="

# ビルドディレクトリのクリーンアップ
echo "🧹 Cleaning previous builds..."
rm -rf build dist RVCStandalone.app

# PyInstallerでビルド
echo "🔨 Building RVC Standalone with PyInstaller..."
pyinstaller rvc_standalone.spec --clean --noconfirm

# ビルド成功確認
if [ -d "dist/RVCStandalone.app" ]; then
    echo "✅ Build successful!"
    
    # アプリケーションサイズを表示
    APP_SIZE=$(du -sh dist/RVCStandalone.app | cut -f1)
    echo "📦 Application size: $APP_SIZE"
    
    # DMG作成（オプション）
    read -p "Create DMG installer? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📀 Creating DMG installer..."
        
        # DMGビルド用の一時ディレクトリ
        DMG_TEMP="dmg_temp"
        rm -rf "$DMG_TEMP"
        mkdir -p "$DMG_TEMP"
        
        # アプリケーションをコピー
        cp -R "dist/RVCStandalone.app" "$DMG_TEMP/"
        
        # Applications へのシンボリックリンク作成
        ln -s /Applications "$DMG_TEMP/Applications"
        
        # DMG作成
        DMG_NAME="RVCStandalone-1.0.0.dmg"
        hdiutil create -volname "RVC Standalone" \
            -srcfolder "$DMG_TEMP" \
            -ov -format UDZO \
            "$DMG_NAME"
        
        # クリーンアップ
        rm -rf "$DMG_TEMP"
        
        if [ -f "$DMG_NAME" ]; then
            DMG_SIZE=$(du -sh "$DMG_NAME" | cut -f1)
            echo "✅ DMG created successfully!"
            echo "📀 DMG size: $DMG_SIZE"
            echo "📍 Location: $(pwd)/$DMG_NAME"
        else
            echo "❌ DMG creation failed"
        fi
    fi
    
    echo ""
    echo "🎉 Build complete!"
    echo "📍 Application location: $(pwd)/dist/RVCStandalone.app"
    echo ""
    echo "To run the app:"
    echo "  open dist/RVCStandalone.app"
    
else
    echo "❌ Build failed!"
    echo "Check the error messages above for details."
    exit 1
fi 