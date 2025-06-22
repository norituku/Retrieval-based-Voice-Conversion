# RVC Voice Converter DMG作成ガイド & 現状課題

## 📋 概要

本ドキュメントは、RVC Voice ConverterのmacOS配布用DMG作成方法と、2025年6月22日時点での未解決課題について記載します。

## 🔨 DMG作成方法

### 前提条件
- macOS (Apple Silicon または Intel Mac)
- Python 3.11 + Poetry環境
- PyInstallerでビルド済みの.appファイル

### 1. アプリケーションのビルド

#### Poetry環境の直接パス使用（重要）
```bash
# Poetry環境パスを確認
poetry env info --path
# 例: /Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11

# PyInstallerで直接ビルド（poetry runは使わない）
/path/to/poetry-env/bin/pyinstaller --clean --noconfirm rvc_minimal.spec
```

#### specファイルの重要設定
```python
# rvc_minimal.spec
app = BUNDLE(
    coll,
    name='VoiceConverter.app',
    icon='app_icons/rvc_icon.icns',
    bundle_identifier='com.rvc.voiceconverter',
    version='1.0.0',
    info_plist={
        'LSEnvironment': {
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
        },
        'NSHighResolutionCapable': True,
    },
)
```

### 2. コード署名の適用

```bash
# fix_codesign.shスクリプトを実行
./fix_codesign.sh

# または手動で
codesign --remove-signature dist/VoiceConverter.app
xattr -cr dist/VoiceConverter.app
codesign --force --deep --sign - dist/VoiceConverter.app
```

### 3. DMG作成スクリプト

#### create_minimal_dmg.sh
```bash
#!/bin/bash
set -e

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
```

### 4. 実行手順

```bash
# スクリプトに実行権限を付与
chmod +x create_minimal_dmg.sh

# DMGを作成
./create_minimal_dmg.sh
```

## 🚨 現状の課題

### 主要問題: GUIクリック起動時のPoetryエラー

#### 症状
| 起動方法 | 結果 | パス例 |
|---------|------|--------|
| ターミナル起動 | ✅ 正常動作 | `/Applications/VoiceConverter.app/Contents/MacOS/VoiceConverter` |
| GUIクリック起動 | ❌ Poetryエラー | `/Applications/VoiceConverter.app` (Finderでダブルクリック) |
| DMG内直接実行 | ❌ Poetryエラー | `/Volumes/Voice Converter/VoiceConverter.app` |

#### エラーメッセージ
```
Poetry not found. Please install Poetry first.
```

#### 根本原因（推定）
1. **環境変数の違い**
   - ターミナル起動: シェルの完全な環境変数を継承
   - GUIクリック起動: macOSの制限された環境

2. **LSEnvironmentの限界**
   - Info.plistにLSEnvironmentでPATH設定済み
   - しかし、GUIクリック時には効果が限定的

3. **アプリ内でのPoetryコマンド呼び出し**
   - gui_dark_mode.py内でフォールバック処理として`poetry run`を使用
   - スタンドアロンアプリ内でPoetryを探そうとして失敗

### 試行済みの対策（効果なし）

1. **LSEnvironment設定**
   ```xml
   <key>LSEnvironment</key>
   <dict>
       <key>PATH</key>
       <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
   </dict>
   ```

2. **com.apple.provenance属性の削除**
   - DMG作成時に拡張属性を削除
   - しかし、macOSが自動的に再付与

3. **各種署名方法**
   - アドホック署名（--sign -）
   - 深い署名（--deep）
   - 署名の削除と再適用

## 📊 テスト結果まとめ

### 成功パターン
- ✅ Poetry環境直接パスでのビルド
- ✅ ターミナルからの起動
- ✅ 音声変換機能自体は正常動作

### 失敗パターン
- ❌ GUIダブルクリックでの起動
- ❌ DMG内からの直接実行
- ❌ LSEnvironmentによる環境変数設定

## 🎯 今後の対策案

### 短期的解決策
1. **起動スクリプトの作成**
   - アプリをラップするシェルスクリプト
   - 環境変数を明示的に設定してから起動

2. **アプリ内でのPoetry依存の除去**
   - gui_dark_mode.pyのフォールバック処理を修正
   - Poetry環境を前提としない実装に変更

### 長期的解決策
1. **完全なスタンドアロン化**
   - すべての依存関係をバンドル
   - 外部コマンドへの依存を排除

2. **開発者証明書の取得**
   - 正式な署名とnotarization
   - macOSセキュリティ制限の回避

## 📝 まとめ

- **技術的成功**: アプリ自体は正常に動作（ターミナル起動時）
- **配布の課題**: GUIクリック起動時の環境変数問題
- **DMG作成**: プロセス自体は確立済み、アプリの問題が残存

---

最終更新: 2025年6月22日