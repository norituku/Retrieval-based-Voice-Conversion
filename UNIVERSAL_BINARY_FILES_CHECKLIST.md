# 📋 ユニバーサルバイナリ版ビルド 必要ファイルチェックリスト

このファイルは、ユニバーサルバイナリ版をビルドするために必要なすべてのファイルのチェックリストです。

## ✅ 必須ファイル（存在必須）

### 📱 アプリケーションコア
```
□ gui_dark_mode.py                    # メインGUIアプリ（直接インポート方式）
□ rvc_config.py                       # RVC設定
□ audio_processor_lite.py             # 音声処理
□ rvc/                                # RVCコアモジュール
  □ rvc/__init__.py
  □ rvc/configs/config.py             # MPS無効化対応済み
  □ rvc/modules/vc/modules.py         # VC音声変換クラス
  □ rvc/modules/vc/pipeline.py        # ダミー実装削除済み
  □ rvc/modules/vc/enhanced_pipeline.py
  □ rvc/modules/vc/utils.py           # ダミー実装削除済み
  □ rvc/wrapper/cli/cli.py            # CLIインターフェース
  □ rvc/wrapper/cli/handler/infer.py  # 推論ハンドラー
```

### 📦 PyInstallerビルド設定
```
□ rvc_minimal.spec                     # メインspecファイル（⭐最重要）
  - runtime_hook設定
  - hiddenimports設定
  - binaries/datas設定
  - excludes設定
```

### 🪝 PyInstallerフック
```
□ hooks/runtime_hook.py                # ランタイム初期化
  - MPS無効化
  - 環境変数設定
  - ダミーpdb提供
□ hooks/hook-torch.py                  # PyTorch収集
□ hooks/hook-numpy.py                  # NumPy収集
□ hooks/hook-librosa.py                # librosa収集
□ hooks/hook-fairseq.py                # fairseq収集
□ hooks/hook-soundfile.py              # soundfile収集
□ hooks/hook-cffi.py                   # CFFI収集
```

### 🛠️ ビルドスクリプト
```
□ fix_codesign.sh                      # arm64署名修復（⭐必須）
□ create_universal_binary.sh           # ユニバーサル化（⭐必須）
□ fix_codesign_universal.sh            # ユニバーサル署名（⭐必須）
□ create_fixed_universal_dmg.py        # DMG作成（⭐必須）
```

### 📄 設定ファイル
```
□ pyproject.toml                       # Poetry依存定義
□ poetry.lock                          # 依存ロック
□ .python-version                      # Python 3.11指定
□ Info_plist_template.txt              # Rosetta2対応Info.plist
```

### 🎨 リソースファイル
```
□ app_icons/icon.icns                  # macOSアイコン
□ model_dir/                           # モデルファイル
  □ (各種.pthファイル)
  □ (各種.indexファイル)
```

## 📊 ファイルサイズ目安

| ファイル/ディレクトリ | サイズ目安 |
|---------------------|-----------|
| gui_dark_mode.py | 約125KB |
| rvc/ (全体) | 約5MB |
| model_dir/ | 約100MB-1GB |
| dist/VoiceConverter.app | 約2.4GB |
| VoiceConverter-Universal-Fixed.dmg | 約2.7GB |

## 🔍 ビルド前チェックコマンド

```bash
# 必須ファイル存在確認
echo "=== 必須ファイルチェック ==="
files=(
    "gui_dark_mode.py"
    "rvc_config.py"
    "audio_processor_lite.py"
    "rvc_minimal.spec"
    "hooks/runtime_hook.py"
    "fix_codesign.sh"
    "create_universal_binary.sh"
    "fix_codesign_universal.sh"
    "create_fixed_universal_dmg.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - 見つかりません！"
    fi
done

# Python版確認
echo -e "\n=== Python環境チェック ==="
poetry env info
python --version

# 依存関係確認
echo -e "\n=== 主要依存関係チェック ==="
poetry show torch | grep version
poetry show fairseq | grep version
```

## ⚠️ よくある問題と対処

### ファイルが見つからない場合

1. **hooks/ディレクトリがない**
   ```bash
   mkdir -p hooks
   # 各hookファイルを作成
   ```

2. **model_dir/がない**
   ```bash
   mkdir -p model_dir
   # モデルファイルをダウンロード/配置
   ```

3. **specファイルがない**
   ```bash
   # Git履歴から復元
   git checkout rvc_minimal.spec
   ```

## 📝 ビルド実行前の最終確認

```bash
# すべての必須ファイルが存在することを確認してから
# UNIVERSAL_BINARY_BUILD_COMPLETE_GUIDE.md の手順に従ってビルドを実行
```

---
作成日: 2025年6月24日
最終確認: ビルド成功、Poetry依存完全排除確認済み