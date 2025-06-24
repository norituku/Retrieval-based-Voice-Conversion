# 🚀 RVC Voice Converter ユニバーサルバイナリ版 完全ビルドガイド

このドキュメントは、Poetry依存を完全に排除した環境非依存のユニバーサルバイナリ版DMGを0から作成するための完全ガイドです。

## 📋 必要なファイル一覧

### 1. コアアプリケーションファイル
- **`gui_dark_mode.py`** - メインGUIアプリケーション（直接インポート方式実装済み）
- **`rvc_config.py`** - RVC設定ファイル
- **`audio_processor_lite.py`** - 音声処理モジュール
- **`rvc/`** - RVCコアモジュールディレクトリ全体
- **`model_dir/`** - モデルファイルディレクトリ

### 2. PyInstallerビルド設定
- **`rvc_minimal.spec`** ⭐ - メインのPyInstallerスペックファイル
  - フック設定、バイナリ収集、除外モジュール定義
  - torch._C問題の解決策実装済み
  - fairseq/pdb問題の解決策実装済み

### 3. PyInstallerフック
- **`hooks/runtime_hook.py`** - ランタイム環境設定
  - MPS無効化、環境変数設定、ダミーpdb提供
- **`hooks/hook-torch.py`** - PyTorchモジュール収集
- **`hooks/hook-numpy.py`** - NumPy依存関係収集
- **`hooks/hook-librosa.py`** - librosa依存関係収集
- **`hooks/hook-fairseq.py`** - fairseq依存関係収集
- **`hooks/hook-soundfile.py`** - soundfile依存関係収集
- **`hooks/hook-cffi.py`** - CFFI依存関係収集

### 4. ビルドスクリプト
- **`fix_codesign.sh`** ⭐ - arm64アプリのコード署名修復
- **`create_universal_binary.sh`** ⭐ - ユニバーサルバイナリ作成
- **`fix_codesign_universal.sh`** ⭐ - ユニバーサルアプリのコード署名修復

### 5. DMG作成スクリプト
- **`create_fixed_universal_dmg.py`** ⭐ - 環境非依存DMG作成（cp -pRP使用）

### 6. Poetry依存関係
- **`pyproject.toml`** - プロジェクト依存関係定義
- **`poetry.lock`** - 依存関係のロックファイル

### 7. アプリリソース
- **`app_icons/`** - アプリケーションアイコン
  - `icon.icns` - macOS用アイコン
- **`Info_plist_template.txt`** - Info.plistテンプレート（Rosetta2対応設定含む）

## 🛠️ ビルド環境の準備

### 前提条件
- macOS 12.0以降（Apple Silicon推奨）
- Python 3.11（必須、3.12以降はfairseqで問題発生）
- Poetry インストール済み
- Xcode Command Line Tools インストール済み

### 環境構築手順

```bash
# 1. リポジトリクローン
git clone <repository_url>
cd Retrieval-based-Voice-Conversion

# 2. Python 3.11環境の設定
poetry env use python3.11

# 3. 依存関係インストール
poetry install

# 4. モデルファイルの配置
# model_dir/ に必要なモデルファイルを配置
```

## 📦 ビルド手順

### Step 1: PyInstallerでarm64アプリをビルド

```bash
# Poetry環境のPython直接パスを使用（重要！）
/Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11/bin/pyinstaller --clean --noconfirm rvc_minimal.spec

# ビルド時間: 約2-3分
# 出力: dist/VoiceConverter.app (約2.4GB)
```

### Step 2: コード署名修復

```bash
# ad-hoc署名を適用してGatekeeper問題を解決
./fix_codesign.sh

# 検証
codesign --verify --deep --verbose dist/VoiceConverter.app
```

### Step 3: ユニバーサルバイナリ作成

```bash
# arm64版をユニバーサル版に変換（Rosetta2対応）
./create_universal_binary.sh

# 出力:
# - universal_build/VoiceConverter_arm64.app (arm64専用)
# - universal_build/VoiceConverter_universal.app (Rosetta2対応)
```

### Step 4: ユニバーサルアプリの署名修復

```bash
cd universal_build
../fix_codesign_universal.sh
cd ..
```

### Step 5: 配布用DMG作成

```bash
# cp -pRPを使用してバイナリ破損を防止
python3 create_fixed_universal_dmg.py

# 出力: VoiceConverter-Universal-Fixed.dmg (約2.7GB)
```

## ✅ 動作確認

### DMGテスト
```bash
# DMGマウント
hdiutil attach VoiceConverter-Universal-Fixed.dmg

# アプリをApplicationsにコピー
cp -pRP "/Volumes/Voice Converter Universal/VoiceConverter.app" /Applications/

# DMGアンマウント
hdiutil detach "/Volumes/Voice Converter Universal"

# アプリ起動
open /Applications/VoiceConverter.app
```

### 確認項目
- [ ] アプリが起動する
- [ ] "Voice Converter Ready" が表示される
- [ ] モデルが正しくロードされる
- [ ] 音声変換が正常に動作する
- [ ] Poetryエラーが出ない

## 🔧 トラブルシューティング

### 問題1: Poetry not found エラー
**原因**: 古いバージョンのgui_dark_mode.pyを使用している
**解決**: 最新のコードで再ビルド

### 問題2: CODESIGNING 2 Invalid Page
**原因**: PyInstallerのstrip処理による署名破損
**解決**: fix_codesign.shを実行

### 問題3: アプリが起動しない（DMGから）
**原因**: dittoコマンドによるバイナリ破損
**解決**: create_fixed_universal_dmg.py（cp -pRP使用）を使用

### 問題4: torch._C not found
**原因**: PyTorchのC拡張モジュール収集漏れ
**解決**: rvc_minimal.specのbinaries設定確認

## 📝 重要な技術的詳細

### 環境非依存性の実現
1. **subprocess方式の廃止**: GUI内でRVCを直接インポート
2. **Poetry環境の排除**: PyInstallerバンドル内で完結
3. **システムPython非依存**: 外部Python不要

### コード署名戦略
1. **個別ライブラリ署名**: すべての.so/.dylibに署名
2. **深層署名**: --deep --forceで全体に適用
3. **Gatekeeper対応**: spctl --addで初回起動許可

### DMG作成の注意点
1. **cp -pRP必須**: 権限とシンボリックリンク保持
2. **ditto禁止**: バイナリ破損の原因
3. **圧縮設定**: zlib-level=9で最適化

## 🎯 最終チェックリスト

- [ ] Python 3.11を使用している
- [ ] Poetry環境が正しく設定されている
- [ ] すべての必要ファイルが存在する
- [ ] PyInstallerビルドが成功する
- [ ] コード署名が有効である
- [ ] DMGが正常に作成される
- [ ] Applications配置後も動作する
- [ ] Intel Mac（Rosetta2）でも動作確認済み

## 📚 関連ドキュメント

- `CLAUDE.md` - プロジェクト全体の知見管理
- `.claude/rvc-pyinstaller-progress.md` - PyInstaller問題解決の詳細履歴
- `MINIMAL_BUILD_README.md` - 最小構成ビルドの説明
- `DMG_CREATION_GUIDE.md` - DMG作成の詳細ガイド

---
最終更新: 2025年6月24日
作成者: Claude AI Assistant with 則兼智志