# 🎵 RVC Voice Converter - 完全独立版 (Ultra Think)

## 🚀 特徴

**完全環境非依存**:
- ✅ Poetry環境不要
- ✅ プロジェクトディレクトリ不要  
- ✅ 外部依存関係ゼロ
- ✅ ワンクリック実行可能
- ✅ 他環境への配布が簡単

**技術的特徴**:
- RVCライブラリ完全バンドル
- PyInstaller単一ファイル化
- 全依存関係内蔵
- 高度な音声変換機能

## 📦 配布パッケージ

```
dist/
├── RVC Voice Converter Standalone.app     # macOSアプリケーションバンドル
├── RVC_Voice_Converter_Standalone_macOS.zip  # 配布用ZIPアーカイブ
└── RVC Voice Converter Standalone         # 実行ファイル（直接実行用）
```

## 🚀 インストール方法

### 他のMacでも即座に動作

1. **ZIPファイルをダウンロード**
   - `RVC_Voice_Converter_Standalone_macOS.zip`

2. **解凍してApplicationsフォルダに移動**
   ```bash
   # ZIPを解凍
   unzip RVC_Voice_Converter_Standalone_macOS.zip
   
   # Applicationsフォルダに移動
   mv "RVC Voice Converter Standalone.app" /Applications/
   ```

3. **起動**
   - Launchpadから起動
   - または Finder → Applications から起動

### ⚠️ セキュリティ設定

初回起動時にmacOSセキュリティ警告が表示される場合:
1. システム設定 → プライバシーとセキュリティ
2. "このまま開く"をクリック

## 📋 必要なファイル

アプリケーション自体は完全独立ですが、音声変換には以下が必要:

### model_dir ディレクトリ
以下のいずれかの場所に配置：
- `~/Desktop/model_dir/`
- `~/Documents/model_dir/`
- `~/Library/Application Support/RVC/model_dir/`

### 必須ファイル
```
model_dir/
├── hubert_base.pt              # HuBERTモデル（必須）
├── rmvpe.pt                    # RMVPEモデル（必須）
└── [voice_models]/             # 音声変換モデル
    ├── model_name.pth          # 音声モデル
    └── model_name.index        # インデックスファイル（推奨）
```

## 🎛️ 使用方法

1. **アプリケーション起動**
2. **モデル選択**: 自動検出されたモデルから選択
3. **音声ファイル選択**: 変換したい音声ファイルを選択
4. **パラメータ調整**: ピッチ、インデックス比率等を調整
5. **変換実行**: "音声変換開始 (完全独立版)"ボタンをクリック

## 🔧 技術仕様

### 動作環境
- **macOS**: 10.15 Catalina以降
- **アーキテクチャ**: Intel & Apple Silicon対応
- **メモリ**: 最低4GB推奨
- **外部依存**: なし

### 内蔵ライブラリ
- PyQt5 (GUI)
- PyTorch (機械学習)
- soundfile, librosa (音声処理)
- numpy (数値計算)
- RVC完全ライブラリ

### 対応音声フォーマット
- WAV, MP3, FLAC, M4A, AIFF, MP4, OGG

## 🚀 配布方法

### 他のMacユーザーに配布
1. `RVC_Voice_Converter_Standalone_macOS.zip`をコピー
2. 受取人が解凍してApplicationsフォルダに移動
3. 即座に使用可能（環境構築不要）

### クラウドストレージ配布
- Google Drive, Dropbox, OneDrive等に`.zip`ファイルをアップロード
- 共有リンクを送信するだけ

## ⚠️ トラブルシューティング

### よくある問題

1. **"開発元を確認できません"エラー**
   - Control+クリック → "開く"
   - システム設定 → プライバシーとセキュリティで許可

2. **モデルが見つからない**
   - model_dirディレクトリの場所を確認
   - hubert_base.pt, rmvpe.ptの存在を確認

3. **アプリが起動しない**
   - macOSバージョンを確認（10.15以降）
   - ターミナルから直接実行してエラーログを確認

## 💡 主な利点

### 従来版との比較
| 項目 | 従来版 | 完全独立版 |
|------|--------|------------|
| Poetry環境 | 必要 | 不要 |
| プロジェクトソース | 必要 | 不要 |
| 配布の容易さ | 困難 | 簡単 |
| 他環境動作 | 環境構築必要 | ワンクリック |
| ファイルサイズ | 小 | 大（完全バンドル）|

### Ultra Think最適化
- 環境検出ロジック完全削除
- RVCライブラリ直接統合
- Poetry依存関係ゼロ
- 配布最適化設計

---

🎉 **RVC Voice Converter 完全独立版**  
Ultra Think技術で実現した究極の環境非依存音声変換アプリ

Created with ❤️ by Ultra Think Technology
