# Voice Converter - Mac App ビルドガイド

このガイドでは、NuitkaToを使用してVoice ConverterをmacOSネイティブアプリケーションとしてパッケージングする方法を説明します。

## 必要条件

- macOS 10.13以降
- Python 3.8以降
- Xcode Command Line Tools
- conda環境またはvenv（推奨）

## セットアップ

### 1. 開発環境の準備

```bash
# Xcode Command Line Toolsをインストール（未インストールの場合）
xcode-select --install

# conda環境をアクティベート
conda activate rvc

# または、仮想環境を作成・アクティベート
python -m venv venv
source venv/bin/activate
```

### 2. Nuitkaのセットアップ

```bash
# セットアップスクリプトを実行
./setup_nuitka.sh
```

## ビルド方法

### 方法1: 高度なビルドスクリプト（推奨）

```bash
# 詳細なビルドスクリプトを実行
./build_advanced.py
```

### 方法2: シンプルなビルドスクリプト

```bash
# シンプルなビルドスクリプトを実行
./build_mac_app.sh
```

### 方法3: 手動でNuitkaを実行

```bash
python -m nuitka \
    --standalone \
    --macos-create-app-bundle \
    --macos-app-name="Voice Converter" \
    --macos-app-version="1.0.0" \
    --macos-app-mode=gui \
    --enable-plugin=tk-inter \
    --include-data-dir=configs=configs \
    --include-data-dir=model_dir=model_dir \
    --include-data-dir=rvc=rvc \
    --include-data-file=gui_settings.json=gui_settings.json \
    --output-dir=dist \
    --remove-output \
    --show-progress \
    gui_dark_mode.py
```

## ビルド成果物

ビルドが成功すると、以下のファイルが作成されます：

```
dist/
└── Voice Converter.app/
    ├── Contents/
    │   ├── Info.plist
    │   ├── MacOS/
    │   │   └── Voice Converter
    │   └── Resources/
    │       ├── configs/
    │       ├── model_dir/
    │       ├── rvc/
    │       └── gui_settings.json
```

## アプリの実行

```bash
# アプリを起動
open "dist/Voice Converter.app"

# または、ターミナルから直接実行
"dist/Voice Converter.app/Contents/MacOS/Voice Converter"
```

## 配布用の準備

### 1. コード署名（オプション）

```bash
# 開発者証明書でコード署名
codesign --force --deep --sign "Developer ID Application: Your Name" "dist/Voice Converter.app"

# 署名の確認
codesign --verify --verbose "dist/Voice Converter.app"
```

### 2. DMGファイルの作成（オプション）

```bash
# DMGファイルを作成
hdiutil create -volname "Voice Converter" -srcfolder "dist/Voice Converter.app" -ov -format UDZO "Voice Converter.dmg"
```

## トラブルシューティング

### よくある問題

1. **"Voice Converter.app" is damaged and can't be opened**
   - Gatekeeperの問題です。以下を実行：
   ```bash
   xattr -cr "dist/Voice Converter.app"
   ```

2. **tkinterが見つからない**
   - Pythonにtkinterが含まれていない場合があります：
   ```bash
   brew install python-tk
   ```

3. **ビルドが失敗する**
   - 依存関係を確認：
   ```bash
   pip install --upgrade nuitka setuptools wheel
   ```

4. **アプリが起動しない**
   - ターミナルから直接実行してエラーメッセージを確認：
   ```bash
   "dist/Voice Converter.app/Contents/MacOS/Voice Converter"
   ```

### デバッグ

詳細なログを見るには：

```bash
# デバッグモードでビルド
python -m nuitka --standalone --macos-create-app-bundle --show-progress --show-memory --verbose gui_dark_mode.py
```

## 設定ファイル

- `nuitka_config.py`: Nuitkaの設定
- `build_advanced.py`: 高度なビルドスクリプト
- `build_mac_app.sh`: シンプルなビルドスクリプト

## 注意事項

- 初回ビルドには時間がかかる場合があります（10-30分）
- macOS特有の依存関係が自動的に含まれます
- アプリサイズは200MB以上になる可能性があります