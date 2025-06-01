# プリセット管理機能ガイド

## 概要

Retrieval-based Voice Conversion (RVC) のプリセット管理機能は、音声変換パラメータの保存、共有、インポート/エクスポートを可能にする拡張機能です。

## 主要機能

### 1. プリセット管理

プリセットを使用することで、お気に入りの音声変換設定を保存し、簡単に再利用できます。

#### プリセット作成
```python
from voice_converter_enhanced_cli import VoiceConverterEnhancedCLI

cli = VoiceConverterEnhancedCLI()
cli.create_preset(
    name="マイカスタムプリセット",
    description="特定の用途向けカスタム設定",
    pitch=2,
    f0_method="harvest",
    index_rate=0.9,
    filter_radius=3,
    rms_mix_rate=0.25,
    protect=0.33
)
```

#### プリセット一覧表示
```python
presets = cli.list_presets()
for preset in presets:
    print(f"{preset['name']}: {preset['description']}")
```

### 2. プリセットのエクスポート/インポート

#### エクスポート
```python
from preset_manager import PresetManager

manager = PresetManager()
manager.export_presets("my_presets.json")
```

#### インポート
```python
manager.import_presets("shared_presets.json", merge=True)
```

### 3. サンプルプリセット

以下のサンプルプリセットが提供されています：

| プリセット名 | 用途 | 特徴 |
|------------|------|------|
| ボーカル専用高品質 | 歌声変換 | F0: mangio-crepe, Index: 1.0 |
| スピーチ最適化 | 話し声変換 | F0: harvest, Index: 0.9 |
| 低CPU使用 | 高速処理 | F0: harvest, Index: 0.6 |

### 4. プリセット形式

プリセットは以下のJSON形式で管理されます：

```json
{
  "name": "プリセット名",
  "description": "プリセットの説明",
  "params": {
    "pitch": 0,
    "f0_method": "harvest",
    "index_rate": 0.85,
    "filter_radius": 2,
    "rms_mix_rate": 0.2,
    "protect": 0.3
  },
  "is_default": false,
  "metadata": {
    "created_date": "2025-06-01T12:00:00",
    "category": "vocal",
    "author": "username"
  }
}
```

## 使用例

### CLI での使用

```bash
# プリセット一覧表示
python voice_converter_enhanced_cli.py --list-presets

# プリセットを使用して変換
python voice_converter_enhanced_cli.py -i input.wav -o output.wav -m model_name --preset "ボーカル専用高品質"

# プリセットエクスポート
python preset_manager.py export my_presets.json

# プリセットインポート
python preset_manager.py import shared_presets.json
```

### Python コードでの使用

```python
from voice_converter_enhanced_cli import VoiceConverterEnhancedCLI

cli = VoiceConverterEnhancedCLI()

# プリセットを使用して変換
cli.convert_with_preset(
    input_file="input.wav",
    output_file="output.wav",
    model_name="model_name",
    preset_name="ボーカル専用高品質"
)
```

## プリセット共有

### 共有用プリセットの作成

```python
from preset_manager import PresetManager

manager = PresetManager()
manager.create_shareable_preset(
    name="コミュニティプリセット",
    description="共有用のカスタム設定",
    params={...},
    author="your_name",
    tags=["vocal", "high-quality"]
)
```

### プリセットの検証

インポート前にプリセットファイルを検証：

```python
validation = manager.validate_preset_file("downloaded_preset.json")
if validation['valid']:
    manager.import_presets("downloaded_preset.json")
else:
    print(f"検証エラー: {validation['errors']}")
```

## ベストプラクティス

1. **命名規則**: プリセット名は用途を明確に示すものにする
2. **説明の追加**: 各プリセットには詳細な説明を含める
3. **カテゴリー分類**: vocal, speech, performance などのカテゴリーを使用
4. **バックアップ**: 重要なプリセットは定期的にエクスポート
5. **テスト**: 新しいプリセットは小さなサンプルでテスト

## トラブルシューティング

### プリセットが見つからない場合
```python
# 設定ファイルの再読み込み
cli.settings.reload_settings()
presets = cli.list_presets()
```

### プリセットの削除
```python
cli.delete_preset("不要なプリセット名")
```

### 設定のリセット
```python
# デフォルト設定に戻す
cli.reset_to_defaults()
```

## 高度な機能

### バッチ処理でのプリセット使用
```python
from batch_converter import BatchConverterCLI

batch = BatchConverterCLI()
batch.process_directory(
    input_dir="input_folder",
    output_dir="output_folder",
    model_name="model_name",
    preset_name="低CPU使用"
)
```

### プリセットのマージ
```python
# 複数のプリセットファイルをマージ
manager.merge_preset_files(
    ["presets1.json", "presets2.json"],
    "merged_presets.json"
)
```

## まとめ

プリセット管理機能により、RVCの音声変換設定を効率的に管理し、チーム間で共有することが可能になります。この機能を活用することで、一貫性のある高品質な音声変換を実現できます。