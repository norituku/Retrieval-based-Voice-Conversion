#!/bin/bash
# スタンドアロン版実行テストスクリプト

echo "🚀 RVC スタンドアロン版実行テスト"

cd "$(dirname "$0")"

echo "📁 現在ディレクトリ: $(pwd)"
echo "📱 アプリ確認..."

if [ -d "dist/RVC Voice Converter Complete.app" ]; then
    echo "✅ スタンドアロンアプリ発見"
    echo "📏 サイズ: $(du -sh "dist/RVC Voice Converter Complete.app" | cut -f1)"
    
    echo "🔧 実行ファイル確認..."
    EXEC_PATH="dist/RVC Voice Converter Complete.app/Contents/MacOS/RVC_Complete_Standalone"
    
    if [ -f "$EXEC_PATH" ]; then
        echo "✅ 実行ファイル発見: $EXEC_PATH"
        echo "🚀 スタンドアロンアプリ実行中..."
        
        # 環境変数設定
        export PYTHONPATH="$(pwd)"
        
        # 実行
        "$EXEC_PATH" 2>&1
    else
        echo "❌ 実行ファイルが見つかりません"
        echo "📂 Contents/MacOS ディレクトリ内容:"
        ls -la "dist/RVC Voice Converter Complete.app/Contents/MacOS/"
    fi
else
    echo "❌ スタンドアロンアプリが見つかりません"
    echo "📂 dist ディレクトリ内容:"
    ls -la dist/
fi