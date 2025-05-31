# RVC Dark Mode GUI with Progress Bar

Voice Conversion処理の進捗をリアルタイムで表示する、ダークモード対応GUIです。

## 特徴

- **統合されたプログレスバー**: 変換処理の各段階をリアルタイムで表示
- **ダークモードUI**: 目に優しいモダンなダークテーマ
- **詳細な進捗表示**: 
  - 初期化 (5%)
  - データ読み込み (10%)
  - 前処理 (20%)
  - 特徴抽出 (30%)
  - モデル推論 (25%)
  - 後処理 (8%)
  - 出力保存 (2%)

## インストール

### 1. プログレスバー機能の統合

すでに統合済みの場合はスキップしてください：

```bash
python3 apply_progress_patch.py
```

### 2. 依存関係の確認

```bash
# Poetry環境の確認
poetry install

# または必要なパッケージを個別にインストール
pip install numpy tkinter
```

## 使用方法

### GUIの起動

```bash
# 通常の起動
python3 gui_dark_mode.py

# またはシェルスクリプトを使用
./run_dark_mode_gui.sh

# テストスクリプト
python3 test_gui_progress.py
```

### 使用手順

1. **GUIを起動**
   - ダークモードのウィンドウが開きます

2. **モデルを選択**
   - ドロップダウンから使用するモデルを選択

3. **入力ファイルを選択**
   - "Browse"ボタンをクリックして音声ファイルを選択

4. **出力設定**
   - 出力ファイル名を設定（自動生成も可能）

5. **パラメータ調整**（オプション）
   - Transpose: ピッチシフト
   - Index Rate: 特徴検索の強度
   - その他の詳細設定

6. **変換開始**
   - "Convert"ボタンをクリック
   - プログレスバーが表示され、進捗が確認できます

## プログレスバーの表示内容

変換中は以下の情報が表示されます：

- **プログレスバー**: 視覚的な進捗表示（0-100%）
- **パーセンテージ**: 数値での進捗表示
- **処理段階**: 現在実行中の処理内容
- **ログ出力**: 詳細な処理ログ（メインウィンドウ）

## トラブルシューティング

### プログレスバーが表示されない

1. `progress_integration.py`が存在するか確認
2. `utils/progress_tracker.py`が存在するか確認
3. パッチが正しく適用されているか確認：
   ```bash
   python3 apply_progress_patch.py
   ```

### ModuleNotFoundError

Poetry環境内で実行してください：
```bash
poetry run python3 gui_dark_mode.py
```

### Tkinterエラー

macOS:
```bash
brew install python-tk
```

Ubuntu/Debian:
```bash
sudo apt-get install python3-tk
```

## ファイル構成

```
Retrieval-based-Voice-Conversion/
├── gui_dark_mode.py              # メインGUI（プログレスバー統合済み）
├── progress_integration.py       # プログレスバー統合モジュール
├── apply_progress_patch.py      # 統合パッチスクリプト
├── utils/
│   └── progress_tracker.py      # 進捗追跡システム
├── ui/
│   └── progress_bar_dark_mode.py # ダークモードプログレスバーUI
└── test_gui_progress.py         # テストスクリプト
```

## カスタマイズ

### プログレスバーの色を変更

`progress_integration.py`の`create_progress_window`メソッド内：

```python
# プログレスバーの色
self.progress_bar = tk.Frame(
    progress_frame,
    bg=self.parent_gui.design_tokens['colors']['accent_primary']  # この色を変更
)

# 完了時の色
if percentage >= 100:
    self.progress_bar.configure(
        bg=self.parent_gui.design_tokens['colors']['success']  # この色を変更
    )
```

### 処理段階の重みを調整

`utils/progress_tracker.py`の`__init__`メソッド内：

```python
self.stages = {
    ProcessingStage.INITIALIZATION: StageInfo("初期化", 0.05, "..."),
    ProcessingStage.DATA_LOADING: StageInfo("データ読み込み", 0.10, "..."),
    # 各段階の重み（第2引数）を調整
}
```

## 注意事項

- 初回実行時は依存関係のインストールに時間がかかる場合があります
- 大きな音声ファイルの処理には時間がかかります
- プログレスバーは推定値であり、実際の処理時間は異なる場合があります

## ライセンス

MIT License