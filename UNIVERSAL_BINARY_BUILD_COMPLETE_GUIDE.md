# 🌍 ユニバーサルバイナリ版 完全ビルドガイド

## 📋 概要

このガイドでは、RVC Voice ConverterのユニバーサルバイナリDMGを0から作成する手順を詳細に説明します。

## 🔧 前提環境

### 必須要件
- **OS**: macOS (Apple Silicon推奨)
- **Python**: 3.11.x（厳密にこのバージョンが必要）
- **Poetry**: 最新版
- **Xcode Command Line Tools**: インストール済み

### 確認コマンド
```bash
python3.11 --version  # Python 3.11.x
poetry --version       # Poetry確認
xcode-select --install # 必要に応じて
```

## 📁 必要ファイル一覧

### ビルドスクリプト（5個）
- `create_fixed_universal_dmg.py` - DMG作成
- `create_universal_binary.sh` - ユニバーサルバイナリ作成
- `fix_codesign.sh` - arm64版署名修復
- `fix_codesign_universal.sh` - ユニバーサル版署名修復
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

## 🚀 ステップ別ビルド手順

### Step 1: Poetry環境準備
```bash
# Python 3.11環境を強制設定
poetry env use python3.11

# 依存関係インストール（約5-10分）
poetry install

# 環境パス確認（後で使用）
poetry env info --path
# 出力例: /Users/username/Library/Caches/pypoetry/virtualenvs/rvc-xxxxx-py3.11
```

### Step 2: 環境確認
```bash
# Python版本確認
poetry run python --version

# 主要依存関係確認
poetry run python -c "import torch; print(f'PyTorch: {torch.__version__}'); import fairseq; print('fairseq: OK')"
```

### Step 3: PyInstaller arm64ビルド
```bash
# Poetry環境Python直接パスでビルド（重要！）
$(poetry env info --path)/bin/pyinstaller --clean --noconfirm rvc_minimal.spec
```

### Step 4: コード署名修復
```bash
# arm64版の署名修復
./fix_codesign.sh
```

### Step 5: ユニバーサルバイナリ作成
```bash
# Rosetta2対応版作成
./create_universal_binary.sh
```

### Step 6: ユニバーサル版署名修復
```bash
# ユニバーサル版の署名修復
./fix_codesign_universal.sh
```

### Step 7: DMG作成
```bash
# 最終DMG作成
python3 create_fixed_universal_dmg.py
```

## ✅ 成功時の出力

### 最終成果物
- `VoiceConverter-Universal-Fixed.dmg` (約2.7GB)
- `universal_build/VoiceConverter_universal.app` (Rosetta2対応)
- `universal_build/VoiceConverter_arm64.app` (arm64専用)

### 動作確認
```bash
# DMGマウント確認
open VoiceConverter-Universal-Fixed.dmg

# アプリ直接起動テスト
open universal_build/VoiceConverter_universal.app
```

## 🚨 トラブルシューティング

### よくあるエラーと解決方法

#### 1. PyTorchライブラリエラー
```
Failed to load dynlib/dll libtorch_global_deps.dylib
```
**解決**: `rvc_minimal.spec`でtorch/libを明示的に追加済み

#### 2. コード署名エラー
```
CODESIGNING 2 Invalid Page
```
**解決**: `fix_codesign.sh`で自動修復

#### 3. Poetry not foundエラー
```
Poetry not found. Please install Poetry first.
```
**解決**: Poetry環境直接パスでビルドすることで回避

#### 4. ファイル不足エラー
```
ERROR: Unable to find 'rvc_worker.py'
```
**解決**: 必要ファイルを復元して再ビルド

### 詳細診断
```bash
# アプリの直接実行でエラー確認
./dist/VoiceConverter.app/Contents/MacOS/VoiceConverter

# 署名確認
codesign -vv dist/VoiceConverter.app

# アーキテクチャ確認
file universal_build/VoiceConverter_universal.app/Contents/MacOS/VoiceConverter
```

## 🎯 パフォーマンス最適化

### ビルド時間短縮
- **SSD使用**: 高速ストレージでビルド
- **メモリ**: 16GB以上推奨
- **並列処理**: `--parallel`オプション利用

### 容量最適化
- **不要モジュール除外**: specファイルでexcludes設定
- **圧縮無効**: 安定性優先でnoarchive=True

## 📊 技術仕様

### アーキテクチャサポート
- **arm64**: Apple Silicon Mac（最高性能）
- **Rosetta2**: Intel Mac互換（翻訳動作）

### 対応OS
- **最小**: macOS 10.15 (Catalina)
- **推奨**: macOS 12.0 (Monterey) 以降

### 依存関係
- **PyTorch**: 2.1.x（2.6以降は非対応）
- **Python**: 3.11.x（3.12以降は非対応）
- **fairseq**: Git版必須

## 🔄 継続的ビルド

### 自動化スクリプト
```bash
#!/bin/bash
# build_universal.sh - ワンライナー自動ビルド

set -e
echo "🚀 ユニバーサルバイナリ自動ビルド開始"

poetry install
$(poetry env info --path)/bin/pyinstaller --clean --noconfirm rvc_minimal.spec
./fix_codesign.sh
./create_universal_binary.sh
./fix_codesign_universal.sh
python3 create_fixed_universal_dmg.py

echo "✅ ビルド完了: VoiceConverter-Universal-Fixed.dmg"
```

### CI/CD統合
- **GitHub Actions**: macOS runnerでビルド
- **成果物保存**: DMGを自動アップロード
- **テスト自動化**: 起動確認とバイナリ検証

## 📚 関連資料

- `UNIVERSAL_BINARY_QUICKSTART.md` - 5分クイックスタート
- `CLAUDE.md` - プロジェクト知見管理
- `rvc_minimal.spec` - PyInstaller詳細設定

---
**作成日**: 2025年6月24日  
**バージョン**: 1.0  
**対象**: RVC Voice Converter ユニバーサルバイナリ版