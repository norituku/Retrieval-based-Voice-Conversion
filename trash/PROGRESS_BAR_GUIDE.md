# Dark Mode GUI with Progress Bar - 実行手順

## セットアップ完了確認

以下のコマンドで、必要なファイルが揃っているか確認できます：

```bash
python3 check_and_run_gui.py
```

## GUIの起動方法

### 方法1: 直接実行
```bash
python3 gui_dark_mode.py
```

### 方法2: シェルスクリプト
```bash
./run_dark_mode_gui.sh
```

### 方法3: Poetry環境で実行（推奨）
```bash
poetry run python3 gui_dark_mode.py
```

## 使用手順

1. **GUIを起動**
   - ダークモードのウィンドウが開きます

2. **モデルを選択**
   - ドロップダウンメニューから使用するモデルを選択
   - 例: "tire", "KAZUMA"

3. **入力ファイルを選択**
   - "Browse"ボタンをクリック
   - 変換したい音声ファイルを選択

4. **変換設定**（オプション）
   - Transpose: ピッチ調整（-12〜+12）
   - Index Rate: 特徴検索率（0.0〜1.0）
   - その他の詳細設定も可能

5. **変換開始**
   - "Convert"ボタンをクリック
   - **プログレスバーウィンドウが自動的に表示されます**

## プログレスバーの表示

変換中は以下の情報が表示されます：

- 🎵 **Voice Conversion** タイトル
- **処理段階の説明** （例：「特徴を抽出しています...」）
- **プログレスバー** （青色、完了時は緑色）
- **パーセンテージ** （大きな数字で表示）

### 処理段階：
1. **初期化** (5%)
2. **データ読み込み** (10%)
3. **前処理** (20%)
4. **特徴抽出** (30%)
5. **モデル推論** (25%)
6. **後処理** (8%)
7. **出力保存** (2%)

## トラブルシューティング

### エラー: AttributeError
すでに修正済みです。最新のgui_dark_mode.pyを使用してください。

### エラー: ModuleNotFoundError
```bash
# Poetry環境を使用
poetry install
poetry run python3 gui_dark_mode.py
```

### プログレスバーが表示されない
1. progress_integration.pyが存在するか確認
2. utils/progress_tracker.pyが存在するか確認
3. 修正を再適用：
   ```bash
   python3 create_fixed_gui.py
   ```

## ファイル構成

```
必須ファイル：
- gui_dark_mode.py           # メインGUI（修正済み）
- progress_integration.py    # プログレスバー統合
- utils/progress_tracker.py  # 進捗追跡システム
- ui/progress_bar_dark_mode.py # UIコンポーネント

ツール：
- create_fixed_gui.py       # GUI修正スクリプト
- check_and_run_gui.py      # 動作確認スクリプト
- run_dark_mode_gui.sh      # 実行用シェルスクリプト
```

## 完了！

これで、Voice Conversion処理中にリアルタイムでプログレスバーが表示されるようになりました。