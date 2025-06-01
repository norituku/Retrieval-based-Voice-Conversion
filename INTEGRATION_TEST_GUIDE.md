# 統合テストツールガイド

## 概要

統合テストツール (`integration_tester.py`) は、RVC のGUI版とCLI版の互換性を検証し、システム全体の整合性を確保するための自動テストツールです。

## テスト項目

### 1. Enhanced CLI 可用性テスト
Enhanced CLI の基本機能が正常に動作することを確認します。

- モデル一覧の取得
- プリセット一覧の取得
- 基本的な初期化処理

### 2. 設定ファイル形式テスト
`enhanced_cli_settings.json` の形式が正しいことを検証します。

- 必須フィールドの存在確認
- プリセット形式の検証
- JSON構造の整合性チェック

### 3. プリセット互換性テスト
プリセットの作成、取得、削除が正常に動作することを確認します。

- 新規プリセットの作成
- プリセット一覧への反映確認
- プリセットのクリーンアップ

### 4. 設定永続化テスト
設定変更が正しく保存され、再読み込みされることを検証します。

- 設定値の変更
- ファイルへの保存
- 新規インスタンスでの読み込み確認

### 5. インポート/エクスポート互換性テスト
プリセットマネージャーのインポート/エクスポート機能を検証します。

- プリセットのエクスポート
- エクスポートファイルの検証
- ファイル形式の確認

### 6. バッチ処理統合テスト
バッチ処理機能との統合を確認します。

- Enhanced モードの可用性
- ディレクトリスキャン機能
- ファイル検出の正確性

### 7. エラーハンドリング統合テスト
エラーログシステムが正常に動作することを確認します。

- ログディレクトリの存在
- ログファイルの生成
- ログフォーマットの確認

## 使用方法

### 基本的な実行

```bash
python integration_tester.py
```

### 実行結果の例

```
🧪 Running Integration Tests
==================================================
✅ PASS Enhanced CLI Availability
      Found 2 models, 8 presets
✅ PASS Settings File Format
      Valid format with 8/8 valid presets
✅ PASS Preset Compatibility
      Preset creation and retrieval working
✅ PASS Settings Persistence
      Settings correctly persisted (pitch: 0 -> 1)
✅ PASS Import/Export Compatibility
      Export and validation successful
✅ PASS Batch Processing Integration
      Batch processing available, found 5 test files
✅ PASS Error Handling Integration
      Error handling active, 2 log files found

📊 Integration Test Results
==================================================
Tests passed: 7/7
Success rate: 100.0%
🎉 All integration tests passed!

📄 Detailed report saved to: integration_test_report.json
```

## テスト結果レポート

テスト実行後、`integration_test_report.json` ファイルが生成されます：

```json
{
  "timestamp": "2025-06-01T19:08:45.621719",
  "summary": {
    "total_tests": 7,
    "passed": 7,
    "failed": 0,
    "success_rate": 100.0
  },
  "results": [
    {
      "test": "Enhanced CLI Availability",
      "result": true,
      "details": "Found 2 models, 8 presets",
      "timestamp": "2025-06-01T19:08:45.616158"
    }
    // ... 他のテスト結果
  ]
}
```

## カスタムテストの追加

### 新しいテストメソッドの作成

```python
def test_custom_feature(self, cli):
    """カスタム機能のテスト"""
    try:
        # テストロジックを実装
        result = cli.some_custom_method()
        
        if result:
            self.log_test(
                "Custom Feature Test",
                True,
                "Custom feature working correctly"
            )
            return True
        else:
            self.log_test(
                "Custom Feature Test",
                False,
                "Custom feature failed"
            )
            return False
            
    except Exception as e:
        self.log_test(
            "Custom Feature Test",
            False,
            f"Error: {e}"
        )
        return False
```

### テストの登録

`run_all_tests` メソッドに新しいテストを追加：

```python
def run_all_tests(self):
    # ... 既存のテスト
    self.test_custom_feature(cli)
    # ...
```

## トラブルシューティング

### テストが失敗する場合

1. **依存関係の確認**
   ```bash
   # 必要なモジュールがインストールされているか確認
   python -c "import voice_converter_enhanced_cli"
   ```

2. **設定ファイルの確認**
   ```bash
   # 設定ファイルが存在し、正しい形式か確認
   cat enhanced_cli_settings.json | jq .
   ```

3. **ログファイルの確認**
   ```bash
   # エラーログを確認
   ls -la enhanced_cli_logs/
   tail -n 50 enhanced_cli_logs/*.log
   ```

### 一般的なエラーと対処法

| エラー | 原因 | 対処法 |
|-------|------|--------|
| ModuleNotFoundError | 必要なモジュールが不足 | `pip install -r requirements.txt` |
| FileNotFoundError | 設定ファイルが存在しない | Enhanced CLI を一度実行して初期化 |
| PermissionError | ファイル権限の問題 | ファイル権限を確認・修正 |
| JSONDecodeError | 設定ファイルの破損 | 設定ファイルをバックアップから復元 |

## CI/CD への統合

### GitHub Actions の例

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run integration tests
      run: |
        python integration_tester.py
    
    - name: Upload test results
      uses: actions/upload-artifact@v2
      if: always()
      with:
        name: test-results
        path: integration_test_report.json
```

## ベストプラクティス

1. **定期的な実行**: 開発中は定期的にテストを実行
2. **新機能追加時**: 新機能を追加したら対応するテストも追加
3. **エラー時の対応**: テスト失敗時は原因を特定し、修正後に再実行
4. **レポートの保存**: テスト結果レポートは履歴として保存
5. **環境の一貫性**: テスト環境と本番環境の一貫性を保つ

## まとめ

統合テストツールは、RVC システムの品質を保証する重要なツールです。定期的な実行により、GUI版とCLI版の互換性を維持し、ユーザーに一貫した体験を提供できます。