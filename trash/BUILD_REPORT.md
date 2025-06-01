# Voice Converter ビルドレポート

## ビルド日時
2025年5月31日 21:00 JST

## ビルド環境
- macOS: 15.5
- Python: 3.11.9
- Poetry: 2.1.3
- Nuitka: 2.7.3
- Xcode Command Line Tools: Clang 17.0.0

## ビルド成果物

### 1. macOSアプリケーションバンドル
- パス: `dist/Voice Converter.app`
- サイズ: 3.3GB
- 実行ファイル: `dist/Voice Converter.app/Contents/MacOS/gui_dark_mode`

### 2. DMGインストーラー
- ファイル名: `Voice Converter.dmg`
- 形式: UDZO (圧縮読み取り専用)

## 実行手順

### アプリケーションの起動
```bash
# Finderから
open "dist/Voice Converter.app"

# ターミナルから
"dist/Voice Converter.app/Contents/MacOS/gui_dark_mode"
```

### DMGからのインストール
1. `Voice Converter.dmg`をダブルクリック
2. `Voice Converter.app`をApplicationsフォルダにドラッグ

## 技術的詳細

### ビルドプロセス
1. Nuitkaによるスタンドアロンバイナリ生成
2. macOSアプリバンドル形式でのパッケージング
3. 必要なリソースファイルの同梱
   - モデルファイル (`model_dir/`)
   - 設定ファイル (`gui_settings.json`)
   - コアライブラリ (`rvc/`)

### 含まれる機能
- ダークモードGUI (PySimpleGUI)
- 音声変換エンジン (VITS ベース)
- 複数音声フォーマット対応 (WAV, MP3, M4A, AIF/AIFF等)
- リアルタイムプログレス表示

## 既知の問題と対処法

### Gatekeeper警告
初回起動時に「開発元を検証できません」という警告が出る場合：
```bash
xattr -cr "/Applications/Voice Converter.app"
```

### コード署名
Apple Developer IDを持っている場合は、以下でコード署名可能：
```bash
codesign --force --deep --sign "Developer ID Application: Your Name" "dist/Voice Converter.app"
```

## 今後の改善点
1. アプリケーションサイズの最適化（現在3.3GB）
2. 自動アップデート機能の実装
3. Apple公証（Notarization）対応
4. より詳細なエラーハンドリング

## 開発コミット履歴
- `f0bbad5` - build_advanced.pyのTkinter依存性を緩和
- `0dac59d` - プロジェクト構造を大幅整理
- `4ee034f` - Nuitkaによるネイティブmacアプリビルドシステムを実装
- `6876704` - AIF/AIFF音声ファイル形式サポートを追加
