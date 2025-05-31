# Voice Converter アプリ起動問題の解決方法

## 問題の原因
Nuitkaでビルドしたアプリケーションが起動しない原因は、Python環境にTkinterモジュールが正しくインストールされていないためです。

## 解決方法

### 方法1: シンプルアプリケーションバンドルを使用（推奨）

作成した`Voice Converter Simple.app`を使用してください：

1. **アプリケーションの起動**
   ```bash
   open "Voice Converter Simple.app"
   ```

2. **Applicationsフォルダへのインストール**
   ```bash
   cp -r "Voice Converter Simple.app" /Applications/
   ```

このアプリケーションは、システムのPython（/usr/bin/python3）を使用してGUIを起動します。

### 方法2: コマンドラインから起動

```bash
./launch_voice_converter.sh
```

または

```bash
./start_gui.sh
```

### 方法3: Poetry環境の修正（上級者向け）

1. **tkinter対応のPythonを再インストール**
   ```bash
   # tcl-tkのパスを確認
   brew --prefix tcl-tk
   
   # pyenvでPythonを再インストール
   export PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I/opt/homebrew/opt/tcl-tk/include' --with-tcltk-libs='-L/opt/homebrew/opt/tcl-tk/lib -ltcl9.0 -ltk9.0'"
   pyenv install 3.11.9
   
   # Poetry環境を再作成
   poetry env remove python
   poetry install
   ```

2. **Nuitkaで再ビルド**
   ```bash
   poetry run python build_advanced.py
   ```

## 現在利用可能なアプリケーション

### Voice Converter Simple.app
- **場所**: プロジェクトディレクトリ内
- **特徴**: システムPythonを使用、軽量
- **推奨**: 一般ユーザー向け

### 起動スクリプト
- `launch_voice_converter.sh` - システムPython使用
- `start_gui.sh` - macOS最適化済み

## トラブルシューティング

### 「開発元を検証できません」エラー
```bash
xattr -cr "/Applications/Voice Converter Simple.app"
```

### モジュールが見つからないエラー
システムPythonに必要なパッケージをインストール：
```bash
/usr/bin/python3 -m pip install --user PySimpleGUI
```

## 今後の改善案
1. Homebrewでインストール可能なフォーミュラの作成
2. 正式なコード署名と公証
3. 自動インストーラーの作成
