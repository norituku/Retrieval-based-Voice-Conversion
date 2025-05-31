# Voice Converter フォルダ整理レポート

## 整理実施日
2025年5月31日

## 整理内容

### 🗑️ trashフォルダに移動したファイル（60ファイル/ディレクトリ）

#### 1. テストファイル（8個）
- test_audio.py
- test_fixed_gui.py
- test_gui_progress.py
- test_m4a.py
- test_progress.py
- test_rvc_command.py
- test_rvc_progress.py
- test_output.wav

#### 2. 重複・古いGUIファイル（6個）
- gui_dark_mode_compact.py
- gui_dark_mode_fixed_progress.py
- gui_dark_mode_original.py
- gui_dark_mode_progress.py
- voice_converter_dark.py
- gui_dark_mode.py.backup_20250528_002152

#### 3. 一時的な修正・パッチファイル（14個）
- apply_progress_patch.py
- check_and_run_gui.py
- copy_test_file.py
- create_app_bundle.py
- create_fixed_gui.py
- debug_rvc.py
- fix_conversion.py
- fix_gui_errors.py
- fix_progress_integration.py
- progress_integration_patch.py
- progress_integration.py
- run_conversion_fixed.py
- run_conversion_patch.py
- simple_fix_progress.py
- integrate_progress.py

#### 4. 古い・重複スクリプト（11個）
- run_gui.py
- run_voice_converter.py
- VoiceConverter.py
- run_compact_gui.sh
- run_converter.sh
- run_dark_mode_progress.sh
- run_gui_unified.sh
- run_gui.sh
- run_standalone.sh
- start_gui_poetry.sh
- rvc_progress_wrapper.py

#### 5. 重複ビルドスクリプト（3個）
- build_simple.py
- simple_nuitka_build.py
- build_nuitka_app.py

#### 6. 不要なドキュメント（3個）
- README_GUI_PROGRESS.md
- PROGRESS_BAR_GUIDE.md
- progress_integration_guide.md

#### 7. 開発関連ディレクトリ（12個）
- gui/（未使用GUIディレクトリ）
- utils/（ユーティリティディレクトリ）
- build_env/（ビルド用仮想環境）
- venv_build/（仮想環境）
- docs/（ドキュメントディレクトリ）
- samples/（サンプルディレクトリ）
- .github/（GitHub設定）
- .qodo/（Qodo設定）
- __pycache__/（Python キャッシュ）
- Voice Converter (M4A).app/（古いアプリ）
- ui/（未使用ディレクトリ）
- VoiceConverterMac/（Swiftプロジェクト）

#### 8. API・Docker関連（3個）
- api-request.sh
- assets-download.sh
- docker-run.sh
- Dockerfile
- .dockerignore
- .env-docker

## 📁 残された主要ファイル（17個）

### コアファイル
- gui_dark_mode.py - メインGUIアプリケーション
- run_inference.py - 音声変換実行スクリプト
- rvc_config.py - RVC設定

### ビルドシステム
- build_advanced.py - 推奨ビルドスクリプト
- build_mac_app.sh - シェルスクリプト版
- nuitka_config.py - Nuitka設定
- setup_nuitka.sh - Nuitkaセットアップ

### 実行スクリプト
- run_dark_mode_gui.sh - 開発用GUI起動
- start_gui.sh - シンプルな起動スクリプト

### 設定・ドキュメント
- pyproject.toml - Poetry依存関係
- poetry.lock - 依存関係ロック
- gui_settings.json - GUI設定
- README.md - メインドキュメント
- BUILD_MAC_APP.md - ビルドガイド
- LICENSE - ライセンス

### その他
- Dockerfile - Docker設定
- docker-run.sh - Docker実行
- api-request.sh - API テスト
- assets-download.sh - アセットダウンロード
- setup.sh - 初期セットアップ

## 📊 整理結果

- 整理前: 約77ファイル/ディレクトリ  
- 整理後: 17ファイル（主要ファイルのみ）
- 削減率: 約78%

## ✅ メリット

1. プロジェクト構造が明確になった
2. 重複ファイルが削除され、メンテナンスが容易に
3. 開発に必要な最小限のファイルのみが残された
4. ビルドシステムが統一された（build_advanced.pyを推奨）

## 🔄 復元方法

必要に応じて、trashフォルダから特定のファイルを復元できます：
```bash
mv trash/<filename> .
```

完全に削除する場合：
```bash
rm -rf trash/
```