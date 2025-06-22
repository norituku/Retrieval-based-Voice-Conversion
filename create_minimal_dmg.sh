#!/bin/bash
# Voice Converter 最小限DMG作成スクリプト
# 権限問題を回避する最もシンプルな実装

set -e

# 基本設定
APP_NAME="VoiceConverter"
DMG_NAME="VoiceConverter-Universal.dmg"

echo "🔨 Voice Converter DMGを作成します..."

# 1. 既存のDMGを削除
[ -f "$DMG_NAME" ] && rm -f "$DMG_NAME"

# 2. 一時フォルダ作成
rm -rf dmg_temp
mkdir dmg_temp

# 3. アプリをコピーして権限設定
echo "📦 アプリをコピー中..."
cp -R "dist/$APP_NAME.app" dmg_temp/

# 実行権限を確保
chmod -R 755 "dmg_temp/$APP_NAME.app"

# 拡張属性（隔離フラグ等）をクリア
xattr -cr "dmg_temp/$APP_NAME.app" 2>/dev/null || true

# 特にcom.apple.provenanceを確実に削除
xattr -d com.apple.provenance "dmg_temp/$APP_NAME.app" 2>/dev/null || true

# 4. アドホック署名（重要：これがないとmacOS 10.15以降で起動できない）
echo "✍️  署名を適用中..."
codesign --force --deep --sign - "dmg_temp/$APP_NAME.app"

# 5. Applicationsへのリンク作成
ln -s /Applications dmg_temp/Applications

# 6. DMG作成（シンプルな単一コマンド）
echo "💿 DMGを作成中..."
hdiutil create \
    -volname "Voice Converter" \
    -srcfolder dmg_temp \
    -ov \
    -format UDZO \
    "$DMG_NAME"

# 7. クリーンアップ
rm -rf dmg_temp

# 8. 完了
if [ -f "$DMG_NAME" ]; then
    echo "✅ 完了: $DMG_NAME"
    echo "サイズ: $(du -h "$DMG_NAME" | cut -f1)"
else
    echo "❌ エラー: DMGの作成に失敗しました"
    exit 1
fi