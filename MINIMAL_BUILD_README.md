# Voice Converter 最小容量ビルドガイド

## 概要

PyInstaller 6.x (universal2) を使用して、gui_dark_mode.py を最小容量のスタンドアロンアプリにパッケージングする手順です。

## 特徴

- ✅ **Universal Binary**: Intel Mac & Apple Silicon 両対応
- ✅ **完全スタンドアロン**: Python/Poetry 不要
- ✅ **容量最適化**: 通常600MB → 300MB前後に削減
- ✅ **機能・見た目**: gui_dark_mode.py と完全同一

## ビルド手順

### 1. 事前準備

```bash
# Poetry環境の準備
poetry install
```

### 2. ワンコマンドビルド

```bash
./build_minimal_app.sh
```

これだけで最適化された VoiceConverter.app が生成されます！

## 容量削減の仕組み

### 除外されるもの
- テスト関連モジュール（pytest, unittest など）
- 開発ツール（setuptools, pip, wheel など）
- 不要なGUIツールキット（PyQt, wxPython など）
- ドキュメント・ヘッダファイル
- デバッグシンボル
- CUDA関連（macOSでは不要）

### 最適化技術
1. **選択的インポート**: 必要最小限のモジュールのみ同梱
2. **バイナリstrip**: デバッグシンボルを削除
3. **重複削除**: 同じライブラリの重複を排除
4. **バイトコード最適化**: Python最適化レベル2
5. **カスタムhook**: torch/numpyから不要部分を除外

## ファイル構成

```
.
├── rvc_minimal.spec        # PyInstaller設定（最適化済み）
├── build_minimal_app.sh    # ビルドスクリプト
├── hooks/                  # カスタムフック
│   ├── hook-torch.py      # PyTorch最小化
│   ├── hook-numpy.py      # NumPy最小化
│   └── runtime_hook.py    # ランタイム最適化
└── dist/
    └── VoiceConverter.app  # 生成されるアプリ
```

## トラブルシューティング

### モデルファイルが見つからない
実際のモデルファイル（hubert_base.pt, rmvpe.pt）をmodel_dir/に配置してください。

### ビルドエラー
```bash
# クリーンビルド
rm -rf build dist
./build_minimal_app.sh
```

### さらなる容量削減が必要な場合
1. アーキテクチャ別ビルド（Intel/ARM64を分離）
2. モデルファイルを別途ダウンロード方式に変更
3. 音声処理ライブラリの一部機能を削減

## 配布方法

生成された `dist/VoiceConverter.app` をそのまま配布、または：

```bash
# DMG作成（create-dmgが必要）
brew install create-dmg
./build_minimal_app.sh  # 自動的にDMGも作成されます
```

## 注意事項

- 初回起動時は署名警告が出る場合があります（右クリック→開くで回避）
- Apple Developer IDで署名すれば警告を完全回避できます
- モデルファイルのライセンスに注意してください 