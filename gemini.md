# Retrieval-based Voice Conversion ― Gemini 設定

## 📚 知見管理システム

このプロジェクトでは以下のファイルで知見を体系的に管理しています：

- **.claude/context.md**: プロジェクトの背景、目的、制約条件
- **.claude/project-knowledge.md**: 実装パターンや設計決定の知見
- **.claude/project-improvements.md**: 過去の試行錯誤の記録
- **.claude/debug-log.md**: 重要なトラブルシューティング記録
- **.claude/common-patterns.md**: 頻繁に使用するコマンドパターン

**重要**: 新しい実装や重要な決定を行った際は、該当するファイルを更新してください。

## 🎯 RVC音声変換環境構築の重要知見

### 環境構築の必須要件
1. **Python バージョン**: 必ずPython 3.11を使用 (`poetry env use python3.11`)
2. **PyTorch バージョン**: `~2.1.0` を使用
3. **fairseq**: Git版を使用 (`{git = "https://github.com/Tps-F/fairseq.git", branch="main"}`)

### 実行コマンド
```bash
# 環境構築
poetry env use python3.11
poetry install

# GUI実行
poetry run python gui_dark_mode.py
```

## 🚀 スタンドアロンアプリ配布の重要知見

### PyInstallerビルド
- **ビルドコマンド**: Poetry環境のPythonを直接パスで指定して実行します。
  ```bash
  /Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11/bin/pyinstaller --clean --noconfirm rvc_minimal.spec
  ```
- **コード署名修復**: ビルド後に `fix_codesign.sh` を実行します。
  ```bash
  ./fix_codesign.sh
  ```

### DMG作成
- **絶対ルール**: アプリのコピーには `cp -pRP` を使用します。`shutil.copytree()` はバイナリを破損させるため**絶対に使用禁止**です。
  ```python
  # ✅ 必須の方法
  subprocess.run(["cp", "-pRP", str(app_path), str(app_dest)], check=True)
  ```

### ユニバーサルバイナリ作成
- **作成スクリプト**: `./create_universal_binary.sh`
- **コード署名**: `cd universal_build && ./fix_codesign_universal.sh`

## 📋 開発ルール

1.  **パッケージ管理**:
    - **RVCプロジェクト**: `poetry` のみを使用します。
    - **その他**: `uv` を使用し、`pip` は使いません。
2.  **コード品質**:
    - 型ヒント必須、docstring推奨。
    - 関数は小さく、既存パターンを踏襲。
    - 行長は88文字まで。
3.  **静的解析**:
    - **フォーマット**: `poetry run ruff format .`
    - **チェック/修正**: `poetry run ruff check . --fix`
    - **型チェック**: `poetry run pyright`
4.  **テスト**:
    - `poetry run pytest` で実行。
    - 非同期テストは `anyio` を使用。

## # important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
