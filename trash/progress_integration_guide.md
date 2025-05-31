# プログレスバー統合改善ガイド

## 概要
現在の実装では、`ProgressBarIntegration`により別ウィンドウが開きます。これを内蔵のステータスセクションのみを使用するように修正します。

## 現在の実装の問題点

1. `run_conversion`メソッドで既に`self.update_progress`を使用している
2. しかし、別途`ProgressBarIntegration`と`tracker`も使用している  
3. `ProcessingStage`への依存がある
4. 結果として、内蔵プログレスバーと別ウィンドウの両方が表示される

## 修正方法

### 1. 不要なインポートの削除（既に完了）
```python
# 削除済み
# from progress_integration import ProgressBarIntegration
# from utils.progress_tracker import ProcessingStage
```

### 2. run_conversionメソッドの修正が必要な箇所

現在のコード:
```python
# プログレスバーを作成
self.progress_integration = ProgressBarIntegration(self)
self.progress_integration.create_progress_window()
tracker = self.progress_integration.get_tracker()
```

修正後:
```python
# 内蔵プログレスバーを使用
# tracker関連のコードは削除
```

### 3. tracker使用箇所の置換

- `tracker.start_stage(ProcessingStage.INITIALIZATION)` → `self.update_progress(0, 0, "初期化中...")`
- `tracker.start_stage(ProcessingStage.DATA_LOADING)` → `self.update_progress(1, 0, "データ読み込み中...")`
- `tracker.start_stage(ProcessingStage.PREPROCESSING)` → `self.update_progress(2, 0, "前処理中...")`
- `tracker.complete_stage()` → 各ステージで100%に更新

### 4. _run_rvc_with_progressメソッド（既に修正済み）

- trackerパラメータを削除
- 内蔵のself.update_progressを使用
- より細かい進捗表示を実装

### 5. finallyブロックの修正

現在:
```python
finally:
    self.root.after(0, lambda: self.progress_integration.close() if self.progress_integration else None)
```

修正後:
```python
finally:
    # プログレスウィンドウのクローズは不要（内蔵プログレスバー使用）
    pass
```

## より細かい進捗表示の実装

### ステージの細分化

1. **初期化（0-14%）**
   - 0%: 開始
   - 5%: 環境チェック
   - 10%: モデル準備
   - 14%: 初期化完了

2. **データ読み込み（14-28%）**
   - 14%: ファイル読み込み開始
   - 20%: モデルデータ読み込み
   - 25%: インデックス確認
   - 28%: 読み込み完了

3. **前処理（28-42%）**
   - 28%: 前処理開始
   - 35%: パラメータ設定
   - 40%: 環境変数設定
   - 42%: 前処理完了

4. **特徴抽出（42-56%）**
   - 42%: 特徴抽出開始
   - 48%: 処理中
   - 54%: 抽出処理
   - 56%: 特徴抽出完了

5. **音声変換（56-70%）**
   - 56%: AIモデル実行開始
   - 62%: 変換処理中
   - 68%: 音声生成
   - 70%: 変換完了

6. **後処理（70-84%）**
   - 70%: 後処理開始
   - 77%: 音質最適化
   - 82%: フォーマット調整
   - 84%: 後処理完了

7. **保存（84-100%）**
   - 84%: 保存開始
   - 92%: ファイル書き込み
   - 98%: 検証
   - 100%: 完了

## 実装例

```python
def update_detailed_progress(self, stage, substep, message):
    """より細かい進捗更新"""
    # 各ステージの開始と終了パーセンテージ
    stage_ranges = [
        (0, 14),    # 初期化
        (14, 28),   # データ読み込み
        (28, 42),   # 前処理
        (42, 56),   # 特徴抽出
        (56, 70),   # 音声変換
        (70, 84),   # 後処理
        (84, 100)   # 保存
    ]
    
    if 0 <= stage < len(stage_ranges):
        start, end = stage_ranges[stage]
        range_size = end - start
        progress = start + (substep / 100) * range_size
        
        self.progress['value'] = progress
        self.percentage_label.config(text=f"{int(progress)}%")
        self.current_stage_label.config(text=message)
        self.root.update_idletasks()
```

## 使用方法

修正後は、変換処理中に：
- 別ウィンドウは開かない
- 内蔵の"Processing Status"セクションに進捗が表示される
- より細かい進捗が表示される（100分割）
- 各ステージの詳細な状態がリアルタイムで更新される
