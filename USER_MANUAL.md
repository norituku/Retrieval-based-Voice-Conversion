# RVC (Retrieval-based Voice Conversion) ユーザーマニュアル

## 目次

1. [はじめに](#はじめに)
2. [インストールと初期設定](#インストールと初期設定)
3. [基本的な使用方法](#基本的な使用方法)
4. [Enhanced CLI の使用方法](#enhanced-cli-の使用方法)
5. [プリセット機能](#プリセット機能)
6. [バッチ処理](#バッチ処理)
7. [GUI版の使用方法](#gui版の使用方法)
8. [トラブルシューティング](#トラブルシューティング)
9. [FAQ](#faq)

## はじめに

RVC (Retrieval-based Voice Conversion) は、高品質な音声変換を実現するオープンソースのフレームワークです。歌声や話し声を別の人の声に変換することができます。

### 主な機能

- **音声変換**: 入力音声を指定されたモデルの声に変換
- **プリセット管理**: よく使う設定を保存・共有
- **バッチ処理**: 複数ファイルの一括変換
- **GUI/CLI対応**: グラフィカルインターフェースとコマンドライン両方をサポート

### システム要件

- Python 3.8 以上
- macOS / Windows / Linux
- メモリ: 4GB以上推奨
- GPU: CUDA対応GPU推奨（CPU のみでも動作）

## インストールと初期設定

### 1. 基本セットアップ

```bash
# プロジェクトディレクトリで初期化
rvc init

# 環境設定ファイルの作成
rvc env create
```

### 2. モデルのダウンロード

```bash
# モデルダウンロード
rvc dlmodel

# カスタムディレクトリにダウンロード
rvc dlmodel /path/to/model/directory
```

### 3. 設定ファイルの編集

`.env` ファイルでモデルの場所を指定：

```bash
MODEL_DIR=/path/to/your/models
OUTPUT_DIR=/path/to/output
```

## 基本的な使用方法

### CLI を使った音声変換

```bash
# 基本的な変換
rvc infer -m model.pth -i input.wav -o output.wav

# パラメータを指定した変換
rvc infer -m model.pth -i input.wav -o output.wav \
  -fu 2 \           # ピッチを2半音上げる
  -fm rmvpe \       # F0抽出方法
  -ir 0.8 \         # インデックス率
  -fr 3 \           # フィルター半径
  -rmr 0.25 \       # RMS混合率
  -p 0.33           # 保護レベル
```

### パラメータの説明

| パラメータ | 説明 | デフォルト値 | 範囲 |
|------------|------|--------------|------|
| `-fu` | ピッチシフト（半音） | 0 | -24 ~ +24 |
| `-fm` | F0抽出方法 | rmvpe | pm, harvest, crepe, rmvpe |
| `-ir` | インデックス率 | 0.75 | 0.0 ~ 1.0 |
| `-fr` | フィルター半径 | 3 | 0 ~ 10 |
| `-rmr` | RMS混合率 | 0.25 | 0.0 ~ 1.0 |
| `-p` | 保護レベル | 0.33 | 0.0 ~ 0.5 |

## Enhanced CLI の使用方法

Enhanced CLI は拡張機能を提供するコマンドラインツールです。

### 起動方法

```bash
python voice_converter_enhanced_cli.py
```

### 主な機能

#### 1. 対話モード

```bash
# Enhanced CLI を起動
python voice_converter_enhanced_cli.py

# メニューから選択
1. 音声変換
2. プリセット管理
3. 設定管理
4. ヘルプ
```

#### 2. 直接実行

```bash
# プリセット一覧表示
python voice_converter_enhanced_cli.py --list-presets

# プリセットを使用した変換
python voice_converter_enhanced_cli.py \
  -i input.wav -o output.wav \
  -m model_name --preset "ボーカル専用高品質"
```

## プリセット機能

プリセット機能を使うと、よく使う設定を保存して簡単に再利用できます。

### プリセットの作成

```python
from voice_converter_enhanced_cli import VoiceConverterEnhancedCLI

cli = VoiceConverterEnhancedCLI()

# 新しいプリセットを作成
cli.create_preset(
    name="マイ設定",
    description="カスタム音声変換設定",
    pitch=2,
    f0_method="harvest",
    index_rate=0.9,
    filter_radius=3,
    rms_mix_rate=0.25,
    protect=0.3
)
```

### プリセットの使用

```bash
# コマンドラインから
python voice_converter_enhanced_cli.py \
  -i input.wav -o output.wav \
  -m model_name --preset "マイ設定"
```

### プリセットのエクスポート/インポート

```bash
# プリセットをファイルにエクスポート
python preset_manager.py export my_presets.json

# プリセットをファイルからインポート
python preset_manager.py import shared_presets.json
```

### 標準プリセット

| プリセット名 | 用途 | 特徴 |
|------------|------|------|
| 高品質（推奨） | 一般的な用途 | F0: rmvpe, 高品質設定 |
| ボーカル専用高品質 | 歌声変換 | F0: mangio-crepe, 高精度 |
| スピーチ最適化 | 話し声変換 | F0: harvest, 話し声に最適 |
| 低CPU使用 | 高速処理 | F0: harvest, 軽量設定 |

## バッチ処理

複数のファイルを一度に変換する機能です。

### バッチ処理の実行

```bash
# バッチコンバーターを起動
python batch_converter.py

# 設定例
- 入力ディレクトリ: ./input_files/
- 出力ディレクトリ: ./output_files/
- モデル: model_name
- プリセット: ボーカル専用高品質
```

### プログラムでのバッチ処理

```python
from batch_converter import BatchConverterCLI

# バッチコンバーターの初期化
batch = BatchConverterCLI()

# ディレクトリ処理
batch.process_directory(
    input_dir="./input",
    output_dir="./output", 
    model_name="model_name",
    preset_name="高品質（推奨）"
)
```

### バッチ処理の監視

```python
# プログレス表示付きバッチ処理
def progress_callback(current, total, filename):
    print(f"[{current}/{total}] Processing: {filename}")

batch.set_progress_callback(progress_callback)
```

## GUI版の使用方法

### GUI の起動

```bash
# ダークモード統合GUI（推奨）
python gui_dark_mode_improved.py

# 基本GUI
python gui_dark_mode.py
```

### GUI の主な機能

#### 1. ファイル選択
- **入力ファイル**: 変換したい音声ファイルを選択
- **出力ファイル**: 変換後のファイル保存先を指定
- **モデルファイル**: 使用する音声モデルを選択

#### 2. パラメータ設定
- **ピッチ**: スライダーで調整（-24 ~ +24半音）
- **F0抽出方法**: ドロップダウンで選択
- **その他設定**: 詳細パラメータの調整

#### 3. プリセット機能
- **プリセット選択**: ドロップダウンから選択
- **プリセット保存**: 現在の設定を新しいプリセットとして保存
- **プリセット管理**: 既存プリセットの編集・削除

#### 4. キーボードショートカット

| ショートカット | 機能 |
|----------------|------|
| `Cmd+O` / `Ctrl+O` | ファイルを開く |
| `Cmd+S` / `Ctrl+S` | 設定を保存 |
| `Cmd+Return` | 変換開始 |
| `Cmd+?` | ショートカット一覧 |

## トラブルシューティング

### よくある問題と解決方法

#### 1. "モデルが見つかりません" エラー

```bash
# 原因: モデルパスの設定が正しくない
# 解決方法:
1. .env ファイルでMODEL_DIRを確認
2. モデルファイルが実際に存在するか確認
3. ファイル権限を確認
```

#### 2. "メモリ不足" エラー

```bash
# 原因: システムメモリが不足
# 解決方法:
1. 他のアプリケーションを終了
2. バッチサイズを小さくする
3. より軽量な設定を使用
```

#### 3. 音声品質が低い

```bash
# 原因: パラメータ設定が適切でない
# 解決方法:
1. F0抽出方法を "rmvpe" に変更
2. インデックス率を 0.8-1.0 に設定
3. 適切なプリセットを使用
```

#### 4. 処理が遅い

```bash
# 原因: CPU負荷が高い設定
# 解決方法:
1. "低CPU使用" プリセットを使用
2. F0抽出方法を "harvest" に変更
3. バッチ処理の並列数を調整
```

### ログファイルの確認

```bash
# エラーログの場所
enhanced_cli_logs/rvc_gui_YYYYMMDD.log

# ログの確認
tail -f enhanced_cli_logs/rvc_gui_*.log
```

### 設定のリセット

```bash
# 設定を初期状態に戻す
rm enhanced_cli_settings.json
python voice_converter_enhanced_cli.py  # 初期設定が再作成される
```

## FAQ

### Q1: どのF0抽出方法を選べばよいですか？

**A:** 用途によって異なります：
- **rmvpe**: 最高品質、歌声に最適
- **mangio-crepe**: 高品質、安定性重視
- **harvest**: 高速、話し声に適している
- **crepe**: バランス型

### Q2: プリセットはどこに保存されますか？

**A:** `enhanced_cli_settings.json` ファイル内に保存されます。このファイルをバックアップすることで設定を保持できます。

### Q3: GPU が認識されません

**A:** 以下を確認してください：
1. CUDA が正しくインストールされているか
2. PyTorch が CUDA 対応版かどうか
3. GPU メモリが十分にあるか

### Q4: バッチ処理で一部のファイルが失敗します

**A:** 考えられる原因：
1. ファイル形式が対応していない
2. ファイルが破損している
3. ファイル名に特殊文字が含まれている

詳細はログファイルで確認してください。

### Q5: 音声変換に時間がかかりすぎます

**A:** 処理時間の目安：
- CPU: 1分の音声に5-10分
- GPU: 1分の音声に1-3分

「低CPU使用」プリセットで高速化できます。

### Q6: 変換後の音声がロボット的です

**A:** 以下を試してください：
1. F0抽出方法を "rmvpe" に変更
2. 保護レベルを下げる（0.1-0.2）
3. RMS混合率を調整（0.1-0.3）

### Q7: プリセットを他の人と共有できますか？

**A:** はい、以下の方法で共有できます：
```bash
# エクスポート
python preset_manager.py export shared_presets.json

# インポート
python preset_manager.py import shared_presets.json
```

### Q8: Enhanced CLI が起動しません

**A:** 以下を確認してください：
1. Python 3.8以上がインストールされているか
2. 必要なライブラリがインストールされているか
3. ファイル権限が正しく設定されているか

---

## サポート

### バグレポート
問題が発生した場合は、以下の情報を含めてレポートしてください：
- オペレーティングシステム
- Python バージョン
- エラーメッセージ
- 実行したコマンド
- ログファイルの内容

### 追加ドキュメント
- [プリセット管理ガイド](PRESET_MANAGER_GUIDE.md)
- [統合テストガイド](INTEGRATION_TEST_GUIDE.md)
- [実装ガイド](IMPLEMENTATION_GUIDE.md)

### コミュニティ
- GitHub Issues でバグレポートや機能要求
- Discord コミュニティで質問や議論

このマニュアルが RVC の使用に役立つことを願っています。より詳細な技術情報については、各ガイドドキュメントを参照してください。