#!/bin/bash
# Voice Converter 完全修正版DMG作成スクリプト
# provenance属性問題を完全解決

set -e

# 基本設定
APP_NAME="VoiceConverter"
DMG_NAME="VoiceConverter-Universal-Fixed.dmg"

echo "🔨 Voice Converter 完全修正版DMGを作成します..."

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

# 拡張属性を完全クリア
echo "🧹 拡張属性を完全クリア中..."
xattr -cr "dmg_temp/$APP_NAME.app" 2>/dev/null || true
find "dmg_temp/$APP_NAME.app" -exec xattr -c {} \; 2>/dev/null || true

# 4. アドホック署名
echo "✍️  署名を適用中..."
codesign --force --deep --sign - "dmg_temp/$APP_NAME.app"

# 5. Applicationsへのリンク作成
ln -s /Applications dmg_temp/Applications

# 6. 読み書き可能DMGを一時作成
echo "💿 一時DMGを作成中..."
TEMP_DMG="temp-rw.dmg"
hdiutil create \
    -volname "Voice Converter" \
    -srcfolder dmg_temp \
    -ov \
    -format UDRW \
    "$TEMP_DMG"

# 7. 一時DMGをマウントして拡張属性を完全削除
echo "🔧 マウントして拡張属性を完全削除中..."
MOUNT_POINT=$(hdiutil attach "$TEMP_DMG" | grep "/Volumes" | awk '{print $3}')
echo "マウントポイント: $MOUNT_POINT"

# マウントされたアプリの拡張属性を完全削除
xattr -cr "$MOUNT_POINT/VoiceConverter.app" 2>/dev/null || true
xattr -d com.apple.provenance "$MOUNT_POINT/VoiceConverter.app" 2>/dev/null || true
xattr -d com.apple.quarantine "$MOUNT_POINT/VoiceConverter.app" 2>/dev/null || true

# 内部ファイルの拡張属性も削除
find "$MOUNT_POINT/VoiceConverter.app" -exec xattr -c {} \; 2>/dev/null || true

echo "✅ 拡張属性削除完了"
xattr -l "$MOUNT_POINT/VoiceConverter.app" 2>/dev/null || echo "拡張属性なし"

# アンマウント
hdiutil detach "$MOUNT_POINT"

# 8. 最終的な圧縮DMGに変換
echo "🗜️ 最終DMGに変換中..."
hdiutil convert "$TEMP_DMG" -format UDZO -o "$DMG_NAME"

# 9. 一時ファイル削除
rm -rf dmg_temp "$TEMP_DMG"

# 10. 完了
if [ -f "$DMG_NAME" ]; then
    echo "✅ 完了: $DMG_NAME"
    echo "サイズ: $(du -h "$DMG_NAME" | cut -f1)"
else
    echo "❌ エラー: DMGの作成に失敗しました"
    exit 1
fi