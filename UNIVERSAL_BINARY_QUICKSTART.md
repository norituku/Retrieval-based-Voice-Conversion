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
./fix_codesign_universal.sh
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
./fix_codesign_universal.sh && \
python3 create_fixed_universal_dmg.py && \
echo "✅ 完成: VoiceConverter-Universal-Fixed.dmg"
```

## 📁 必要なファイル（完全最小構成）

🧹 **大規模整理完了！** ユニバーサルバイナリビルドに必要なファイルは以下のみです：

### スクリプトファイル（5個）
- `create_fixed_universal_dmg.py` - 環境非依存DMG作成
- `create_universal_binary.sh` - ユニバーサルバイナリ作成  
- `fix_codesign.sh` - arm64署名修復
- `fix_codesign_universal.sh` - ユニバーサル署名修復
- `rvc_worker.py` - PyInstaller要件

### 設定ファイル（5個）
- `rvc_minimal.spec` - PyInstaller設定
- `gui_dark_mode.py` - メインGUIアプリ
- `rvc_config.py` - RVC設定
- `pyproject.toml` - Poetry設定
- `poetry.lock` - 依存関係ロック

### 必須ディレクトリ（4個）
- `rvc/` - メインライブラリ
- `model_dir/` - モデル格納（構造のみ）
- `hooks/` - PyInstallerフック
- `app_icons/` - アプリアイコン

### ドキュメント（3個）
- `CLAUDE.md` - プロジェクト設定・知見管理
- `UNIVERSAL_BINARY_BUILD_COMPLETE_GUIDE.md` - 詳細ガイド
- `UNIVERSAL_BINARY_QUICKSTART.md` - クイックスタート（本ファイル）

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