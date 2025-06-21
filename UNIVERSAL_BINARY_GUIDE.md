# Voice Converter ユニバーサルバイナリ作成ガイド

## 問題と解決方法

現在のPoetry環境のパッケージ（特にnumpy）が単一アーキテクチャ（arm64のみ）でインストールされているため、PyInstallerでuniversal2バイナリを直接作成できません。

## 解決方法

### 方法1: universal2対応Python環境の使用（推奨）

1. **Python.orgからuniversal2版Pythonをインストール**
   ```bash
   # https://www.python.org/downloads/ から
   # macOS 64-bit universal2 installer をダウンロード
   # 例: python-3.11.x-macos11.pkg
   ```

2. **新しい仮想環境を作成**
   ```bash
   # universal2 Pythonで仮想環境作成
   /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -m venv venv_universal
   source venv_universal/bin/activate
   
   # 必要なパッケージをインストール
   pip install --upgrade pip
   pip install numpy torch fairseq librosa soundfile
   pip install pyinstaller==6.*
   ```

3. **universal2ビルド実行**
   ```bash
   # rvc_minimal.specのtarget_archを'universal2'に戻す
   pyinstaller --clean --noconfirm rvc_minimal.spec
   ```

### 方法2: 現在の環境で単一アーキテクチャビルド（簡易版）

現在のarm64環境でそのままビルドする場合：

```bash
chmod +x build_universal_app.sh
./build_universal_app.sh
```

これにより、Apple Silicon専用の最適化されたアプリが作成されます。

### 方法3: 2つのアーキテクチャを手動結合（上級者向け）

1. **arm64版をビルド**（現在の環境）
   ```bash
   ./build_minimal_app.sh
   mv dist dist_arm64
   ```

2. **x86_64版をビルド**（Intel Macまたは別環境）
   ```bash
   # Intel Mac環境で同じ手順を実行
   ./build_minimal_app.sh
   mv dist dist_x86_64
   ```

3. **lipoで結合**
   ```bash
   # アプリケーションをコピー
   cp -R dist_arm64/VoiceConverter.app dist_universal/
   
   # メインバイナリを結合
   lipo -create \
     dist_arm64/VoiceConverter.app/Contents/MacOS/VoiceConverter \
     dist_x86_64/VoiceConverter.app/Contents/MacOS/VoiceConverter \
     -output dist_universal/VoiceConverter.app/Contents/MacOS/VoiceConverter
   
   # すべての.dylibと.soファイルも結合が必要
   find dist_arm64/VoiceConverter.app -name "*.dylib" -o -name "*.so" | while read file; do
     relative_path=${file#dist_arm64/VoiceConverter.app/}
     if [ -f "dist_x86_64/VoiceConverter.app/$relative_path" ]; then
       lipo -create \
         "$file" \
         "dist_x86_64/VoiceConverter.app/$relative_path" \
         -output "dist_universal/VoiceConverter.app/$relative_path"
     fi
   done
   ```

## 推奨事項

- **開発環境**: universal2版Pythonを使用（方法1）
- **CI/CD**: GitHub ActionsでIntel/ARM64を別々にビルドして結合
- **配布**: ユーザーのニーズに応じて単一アーキテクチャ版も提供

## トラブルシューティング

### "not a fat binary"エラー
単一アーキテクチャのパッケージが原因。universal2版パッケージをインストールするか、target_archをNoneまたは現在のアーキテクチャに設定。

### サイズが大きすぎる
universal2は2つのアーキテクチャを含むため、サイズは約1.5-2倍になります。必要に応じて単一アーキテクチャ版も提供。

### 署名エラー
universal2バイナリは両アーキテクチャに署名が必要。`codesign --deep --force`で再署名。 