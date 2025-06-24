#!/bin/bash
# Voice Converter トラブルシューティングスクリプト

echo "=== Voice Converter 起動問題の診断 ==="

# アプリの場所
APP_PATH="/Applications/VoiceConverter.app"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ エラー: VoiceConverter.app が /Applications にインストールされていません"
    echo "DMGファイルを開いて、アプリをApplicationsフォルダにドラッグしてください"
    exit 1
fi

echo "✅ アプリが見つかりました: $APP_PATH"

# 権限の確認
echo -e "\n🔍 権限の確認..."
ls -la "$APP_PATH/Contents/MacOS/VoiceConverter"

# 拡張属性の削除
echo -e "\n🔧 拡張属性を削除..."
sudo xattr -cr "$APP_PATH"
echo "✅ 拡張属性を削除しました"

# Gatekeeper例外の追加
echo -e "\n🔓 Gatekeeperの例外に追加..."
sudo spctl --add "$APP_PATH"
sudo spctl --enable --label "$APP_PATH"
echo "✅ Gatekeeper例外に追加しました"

# 署名の再実行
echo -e "\n✏️ アプリに再署名..."
sudo codesign --force --deep -s - "$APP_PATH"
echo "✅ 署名を更新しました"

# 起動テスト
echo -e "\n🚀 アプリを起動します..."
open "$APP_PATH"

echo -e "\n✅ トラブルシューティング完了"
echo "もしまだ起動しない場合は、以下を確認してください："
echo "1. macOSのバージョンが11.0以降か"
echo "2. システム設定 > プライバシーとセキュリティ で許可が必要か"
echo "3. ターミナルで直接実行: $APP_PATH/Contents/MacOS/VoiceConverter"
