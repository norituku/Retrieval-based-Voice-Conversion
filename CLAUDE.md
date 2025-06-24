# Retrieval-based Voice Conversion ― CLAUDE 設定

## 📚 知見管理システム

このプロジェクトでは以下のファイルで知見を体系的に管理しています：

### `.claude/context.md`
- プロジェクトの背景、目的、制約条件
- 技術スタック選定理由
- ビジネス要件や技術的制約

### `.claude/project-knowledge.md`
- 実装パターンや設計決定の知見
- アーキテクチャの選択理由（ADR）
- 避けるべきパターンやアンチパターン

### `.claude/project-improvements.md`
- 過去の試行錯誤の記録
- 失敗した実装とその原因
- 改善プロセスと結果

### `.claude/debug-log.md`
- 重要なトラブルシューティング記録
- エラー解決プロセス
- 緊急時復旧手順

### `.claude/common-patterns.md`
- 頻繁に使用するコマンドパターン
- 定型的な実装テンプレート
- 緊急時診断チェックリスト

**重要**: 新しい実装や重要な決定を行った際は、該当するファイルを更新してください。

## 🔨 最重要ルール - 新しいルールの追加プロセス

ユーザーから今回限りではなく常に対応が必要だと思われる指示を受けた場合：

1. 「これを標準のルールにしますか？」と質問する
2. YESの回答を得た場合、CLAUDE.mdに追加ルールとして記載する
3. 以降は標準ルールとして常に適用する

このプロセスにより、プロジェクトのルールを継続的に改善していきます。

## 🎯 RVC音声変換環境構築の重要知見

### 環境構築の必須要件
1. **Python バージョン**: 必ずPython 3.11を使用（3.12以降はfairseqで問題発生）
2. **PyTorch バージョン**: 2.1.x系のみ使用（`torch = "~2.1.0"`）
   - 2.6以降はweights_only=Trueがデフォルトとなりfairseqで問題発生
3. **fairseq**: PyPI版ではなくGit版を使用
   ```toml
   fairseq = {git = "https://github.com/Tps-F/fairseq.git", branch="main"}
   ```

### GUI実行環境の設定
1. **Poetry環境**: `poetry env use python3.11`で3.11環境を強制
2. **rvc_config.py**: Poetry環境のPythonパスを正確に設定
3. **Hubertモデルパス**: `--hubert_model_path`パラメータが必須
4. **インデックスファイル**: 破損したfaissインデックスは自動スキップ

### トラブルシューティング履歴
- **問題**: PyTorch 2.6のweights_only問題でHubertモデル読み込み失敗
- **解決**: PyTorch 2.1.xダウングレード
- **問題**: faissインデックスファイル(\x93NUM形式)読み込みエラー  
- **解決**: NumPy形式ファイル検出時の自動スキップ機能追加
- **問題**: GUI起動しない（Tkinter環境問題）
- **解決**: Poetry環境でのTkinter動作確認とバックグラウンド実行

### 実行コマンド
```bash
# 環境構築
poetry env use python3.11
poetry install

# GUI実行
poetry run python gui_dark_mode.py
```

**⚠️ 重要**: この環境設定は音声変換の成功に必須です。バージョンを変更する場合は事前にテストが必要です。

## 🚀 スタンドアロンアプリ配布の重要知見

### PyInstaller 6.x による配布可能アプリ作成
1. **アーキテクチャ対応**: arm64専用ビルドで997MBの完全動作アプリを実現
2. **PyTorchライブラリ問題**: `libtorch_global_deps.dylib`の収集漏れがメイン原因
   - **解決**: specファイルでtorch/lib全体を明示的に追加
   - **回避**: runtime_hookでのtorchインポートを削除（循環参照防止）
3. **コード署名問題**: PyInstallerのstrip処理後に署名が破損
   - **解決**: `fix_codesign.sh`で署名削除→再適用の自動化
   - **要件**: ad-hoc署名による`CODESIGNING 2 Invalid Page`エラーの解決
4. **容量最適化**: 不要モジュール除外により854MB→997MB（PyTorch完全版）

### 🎯 必須: Poetry環境でのPyInstallerビルド方法

**正しいビルド方法:**
```bash
# Poetry環境パス確認
poetry env info --path

# 直接パスでPyInstaller実行（必須）
/Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11/bin/pyinstaller --clean --noconfirm rvc_minimal.spec

# コード署名修復
./fix_codesign.sh

# アプリ起動
open dist/VoiceConverter.app
```

**重要**: Poetry環境のPython直接パスを使用することで、スタンドアロンアプリ内でのPoetry呼び出しエラーを完全に回避できます。

### 🚨 DMG作成時の重要注意事項

**絶対ルール**: DMG作成時のアプリコピーは `shutil.copytree()` を使わず `cp -pRP` を使用する

```python
# ❌ 絶対禁止（バイナリ破損の原因）
shutil.copytree(app_path, app_dest)

# ✅ 必須の方法（権限・リンク保持）
subprocess.run(["cp", "-pRP", str(app_path), str(app_dest)], check=True)
```

**理由**: shutil.copytree()はバイナリファイルや実行権限を破損させ、DMG内のアプリで「Poetry not found」エラーが発生する。

### 🚨 絶対に忘れてはいけない重要事実

**現状:**
- ✅ スタンドアロンアプリ: 完璧に動作、Poetryエラーなし
- ✅ ユニバーサル版アプリ: 完璧に動作、Poetryエラーなし  
- ❌ DMG内のアプリ: Poetryエラー発生

**結論:** アプリ自体は完璧。DMG作成プロセスのみが問題。

### 🌍 ユニバーサルバイナリ（Rosetta2対応版）作成方法

**実用的アプローチ:**
```bash
# ユニバーサルバイナリ作成スクリプトを実行
./create_universal_binary.sh

# コード署名を適用
cd universal_build && ./fix_codesign_universal.sh

# 起動テスト
open VoiceConverter_universal.app
```

**結果:**
- **VoiceConverter_universal.app**: Rosetta2対応（Apple Silicon + Intel Mac両対応）
- **VoiceConverter_arm64.app**: arm64専用（最適パフォーマンス）
- **サイズ**: 約2.5GB（arm64版のみだが全Mac対応）

**技術的詳細:**
- Info.plistでLSArchitecturePriorityを設定（arm64優先、x86_64対応）
- LSMinimumSystemVersionを10.15に設定
- Rosetta2によりIntel Macでもネイティブ動作
- 初回起動時のみ翻訳処理で若干の遅延あり

**✅ 検証済み動作環境:**
- Apple Silicon Mac: ネイティブ動作、最適パフォーマンス、音声変換成功
- Intel Mac (Rosetta2): 翻訳動作、実用的パフォーマンス、音声変換成功
- 全ての環境でPoetryエラーなし（Poetry直接パスビルド効果）

## 📋 開発ルール

1. パッケージ管理
   - **RVCプロジェクト**: `poetry` のみを使用（依存関係の複雑さのため）
   - **その他プロジェクト**: `uv` を使用し、`pip` は絶対に使わない
   - インストール方法：`poetry install` / `poetry add package`
   - ツールの実行：`poetry run tool`
   - 環境管理：`poetry env use python3.11`

2. コード品質
   - すべてのコードに型ヒントを必須とする
   - パブリックAPIには必ずドキュメンテーション文字列（docstring）を付ける
   - 関数は集中して小さく保つこと
   - 既存のパターンを正確に踏襲すること
   - 行の最大長は88文字まで

3. テスト要件
   - テストフレームワーク：`poetry run pytest`
   - 非同期テストは `asyncio` ではなく `anyio` を使用
   - カバレッジはエッジケースやエラーも含めてテストすること
   - 新機能には必ずテストを追加すること
   - バグ修正にはユニットテストを追加すること

1. Ruff
   - フォーマット実行：`poetry run ruff format .`
   - チェック実行：`poetry run ruff check .`
   - 修正実行：`poetry run ruff check . --fix`
   - 重要な指摘内容：
     - 行の長さ（88文字）
     - インポートのソート（I001）
     - 未使用のインポート
   - 行の折り返し：
     - 文字列は括弧を使う
     - 関数呼び出しは複数行にして適切にインデント
     - インポート文は複数行に分ける

2. 型チェック
   - ツール：`poetry run pyright`
   - 要件：
     - Optional型には明示的なNoneチェックを入れる
     - 文字列の型は狭めて扱う
     - バージョン警告はチェックが通れば無視してよい

3. Pre-commit
   - 設定ファイル：`.pre-commit-config.yaml`
   - 実行タイミング：gitコミット時
   - 使用ツール：Prettier（YAML/JSON用）、Ruff（Python用）
   - Ruffの更新方法：
     - PyPIのバージョンを確認する
     - 設定ファイルのリビジョンを更新する
     - まず設定ファイルをコミットする

## 🔧 PyInstaller スタンドアロンアプリ配布のトラブルシューティング

### 頻出エラーと解決方法
- **問題**: `CODESIGNING 2 Invalid Page` でアプリ起動時にクラッシュ
- **解決**: `codesign --remove-signature` → `codesign --force --deep --sign -` の順で再署名
- **問題**: `Failed to load dynlib/dll libtorch_global_deps.dylib`
- **解決**: specファイルに `(torch/lib, 'torch/lib')` を datas に明示的追加
- **問題**: Poetry環境でuniversal2ビルドが `not a fat binary` エラー
- **解決**: `target_arch=None` で現在アーキテクチャビルド後、必要に応じてlipo結合
- **検証方法**: `./dist/App.app/Contents/MacOS/App` で直接実行してエラー確認

### 成功パターン
- **ファイル構成**: `rvc_minimal.spec` + `hooks/` + `fix_codesign.sh`
- **ビルド手順**: Poetry環境Python直接パス実行 → `./fix_codesign.sh`
- **最終成果**: 997MB の完全動作arm64アプリ（Python環境不要）

## 🚀 Ultra Think技術 - 問題解決ベストプラクティス

### 1. 段階的問題解決アプローチ
   - **症状の正確な把握**: 詳細ログとタイミング測定を必須とする
   - **根本原因の特定**: 表面的でなく根源的な原因分析を行う
   - **最適解の実装**: 応急処置でなく恒久的解決を目指す
   - **自動診断の確立**: 同類問題の予防システムを構築する
   - **知見の体系化**: 再現可能な解決手法を確立する

### 2. デバッグとエラー処理
   - **早期終了問題**: 実行時間が期待値以下の場合は異常とみなす
   - **スコープ問題**: 局所的importを避け、グローバルスコープを優先する
   - **診断ファイル生成**: debug_cmd.txt、error_report.txtを自動生成する
   - **段階別プログレス**: 処理の各段階でプログレス表示と状態確認を行う
   - **環境変数確認**: 重要な環境変数の存在と値を必ず確認する

### 3. PyInstaller対応パターン
   - **リソースパス取得**: sys._MEIPASSとsys.executableの両方に対応
   - **動的パス追加**: bundle_dir内のライブラリを自動検出・追加
   - **環境変数設定**: バンドル内リソースを環境変数で適切に設定
   - **拡張属性除去**: macOSでのcom.apple.provenance問題を自動解決
   - **依存関係確認**: 必要なライブラリの存在と動作を実行前に確認

### 4. エラー特定と修正パターン
   - **CLI引数エラー**: 実装仕様と照合し、存在しないオプションを排除
   - **モジュールスコープ競合**: 局所importを削除し、グローバルimportに統一
   - **ファイル形式問題**: ffmpeg等による自動変換機能を実装
   - **権限問題**: 代替ディレクトリへのフォールバック機能を実装
   - **プロセス管理**: subprocess.communicate()による確実な出力取得

### 5. 品質保証プロセス
   - **段階的テスト**: 各機能を段階的に検証し、問題箇所を特定
   - **自動診断機能**: エラー発生時の自動原因分析とレポート生成
   - **完全性確認**: 出力ファイルの存在、サイズ、内容を多角的に検証
   - **環境非依存**: Poetry環境等に依存しない完全独立動作を実現
   - **再現性保証**: 同一エラーの再発防止と解決手法の標準化

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.