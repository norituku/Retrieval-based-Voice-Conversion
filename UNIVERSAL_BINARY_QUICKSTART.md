# 🚀 ユニバーサルバイナリ版 クイックスタートガイド

5分でユニバーサルバイナリ版DMGを作成するための最速手順です。

## 📋 前提条件
- macOS (Apple Silicon推奨)
- Python 3.11
- Poetry インストール済み
- このリポジトリをクローン済み

## 🏃‍♂️ 最速ビルド手順

### 1️⃣ 環境準備（初回のみ）
```bash
# Python 3.11環境を設定
poetry env use python3.11

# 依存関係インストール（約5分）
poetry install
```

### 2️⃣ Poetry環境パス確認
```bash
# このパスをメモしておく（後で使用）
poetry env info --path
# 例: /Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11
```

### 3️⃣ アプリビルド（約2-3分）
```bash
# Poetry環境のPython直接パスでPyInstaller実行（重要！）
$(poetry env info --path)/bin/pyinstaller --clean --noconfirm rvc_minimal.spec

# コード署名修復
./fix_codesign.sh
```

### 4️⃣ ユニバーサルバイナリ作成（約1分）
```bash
# Rosetta2対応版作成
./create_universal_binary.sh

# ユニバーサル版の署名修復
cd universal_build && ../fix_codesign_universal.sh && cd ..
```

### 5️⃣ DMG作成（約1分）
```bash
# 最終的な配布用DMG作成
python3 create_fixed_universal_dmg.py
```

## ✅ 完成！

**出力ファイル**: `VoiceConverter-Universal-Fixed.dmg` (約2.7GB)

### インストール方法
1. DMGファイルをダブルクリック
2. VoiceConverter.appをApplicationsフォルダにドラッグ
3. Applicationsから起動（初回は右クリック→開く）

## 🎯 動作確認
- ✅ Apple Silicon Mac: ネイティブ動作
- ✅ Intel Mac: Rosetta2経由で動作
- ✅ Poetry不要: 完全スタンドアロン
- ✅ 音声変換: 正常動作

## ⚡ ワンライナー版（上級者向け）

```bash
# すべてを一度に実行（約10分）
poetry install && \
$(poetry env info --path)/bin/pyinstaller --clean --noconfirm rvc_minimal.spec && \
./fix_codesign.sh && \
./create_universal_binary.sh && \
cd universal_build && ../fix_codesign_universal.sh && cd .. && \
python3 create_fixed_universal_dmg.py && \
echo "✅ 完成: VoiceConverter-Universal-Fixed.dmg"
```

## 🆘 困ったときは

### Poetry not found エラー
→ 古いビルドを使用している。上記手順で再ビルド。

### アプリが起動しない
→ Applicationsフォルダから右クリック→開く

### その他の問題
→ `UNIVERSAL_BINARY_BUILD_COMPLETE_GUIDE.md` を参照

---
最速所要時間: 約10-15分
最終更新: 2025年6月24日