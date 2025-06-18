#!/bin/bash
# 完全スタンドアロン版テストスクリプト

echo "🧪 完全スタンドアロン版動作テスト"
cd "$(dirname "$0")/dist"

echo "📱 アプリ: RVC Voice Converter Complete.app"
echo "📏 サイズ: $(du -sh "RVC Voice Converter Complete.app" | cut -f1)"

echo "🚀 アプリケーション実行ファイルをテスト..."
"RVC Voice Converter Complete.app/Contents/MacOS/RVC_Complete_Standalone" 2>&1