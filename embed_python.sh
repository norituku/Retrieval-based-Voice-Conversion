#!/bin/bash
# embed_python.sh - Python環境を同梱する簡単スクリプト

set -e

echo "🐍 Python環境の同梱を開始します..."

# 1. 作業ディレクトリ
cd /Users/norikene_satoshi/Retrieval-based-Voice-Conversion

# 2. 既存のPython 3.11を探す
PYTHON_SOURCE=""
if [ -d "/Library/Frameworks/Python.framework/Versions/3.11" ]; then
    PYTHON_SOURCE="/Library/Frameworks/Python.framework/Versions/3.11"
elif [ -d "/usr/local/Cellar/python@3.11" ]; then
    PYTHON_SOURCE="/usr/local/Cellar/python@3.11/*/Frameworks/Python.framework/Versions/3.11"
else
    echo "❌ Python 3.11が見つかりません"
    exit 1
fi

echo "✅ Python found: $PYTHON_SOURCE"

# 3. 一時ディレクトリにコピー
echo "📦 Pythonをコピー中..."
rm -rf python_embed
mkdir -p python_embed
cp -R $PYTHON_SOURCE python_embed/Python3.11

# 4. 不要なファイルを削除（サイズ削減）
echo "🧹 クリーンアップ中..."
cd python_embed/Python3.11
rm -rf lib/python3.11/test
rm -rf lib/python3.11/idlelib  
rm -rf lib/python3.11/tkinter
rm -rf lib/python3.11/distutils
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 5. サイズ確認
SIZE=$(du -sh . | cut -f1)
echo "📊 Python環境のサイズ: $SIZE"

# 6. specファイルのバックアップと修正
cd ../..
cp rvc_minimal.spec rvc_minimal.spec.backup

# 7. 自動でspecファイルに追加
cat >> rvc_minimal.spec << 'EOF'

# === Python埋め込み設定 ===
# Pythonフレームワークを追加
import os
python_embed = 'python_embed/Python3.11'
if os.path.exists(python_embed):
    # バイナリとして追加
    a.binaries += [(
        'Python.framework/Versions/3.11/Python',
        os.path.join(python_embed, 'Python'),
        'BINARY'
    )]
    
    # ライブラリを追加
    a.datas += Tree(
        os.path.join(python_embed, 'lib/python3.11'),
        prefix='Python.framework/Versions/3.11/lib/python3.11'
    )
    
    # bin ディレクトリも追加
    if os.path.exists(os.path.join(python_embed, 'bin')):
        a.datas += Tree(
            os.path.join(python_embed, 'bin'),
            prefix='Python.framework/Versions/3.11/bin'
        )
EOF

# 8. rvc_config.pyの修正
echo "✏️ rvc_config.pyを修正中..."
cp rvc_config.py rvc_config.py.backup

# sedで関数の最初に埋め込みPythonチェックを追加
sed -i '' '/def get_poetry_python():/a\
    import sys\
    if getattr(sys, "frozen", False):\
        app_dir = os.path.dirname(os.path.dirname(sys.executable))\
        embedded = os.path.join(app_dir, "Frameworks/Python.framework/Versions/3.11/bin/python3")\
        if os.path.exists(embedded): return embedded\
' rvc_config.py

echo "✅ 準備完了！"
echo ""
echo "📌 次のステップ:"
echo "1. ビルド: pyinstaller --clean --noconfirm rvc_minimal.spec"
echo "2. テスト: open dist/VoiceConverter.app"
echo ""
echo "🔄 元に戻す場合:"
echo "   cp rvc_minimal.spec.backup rvc_minimal.spec"
echo "   cp rvc_config.py.backup rvc_config.py"
echo "   rm -rf python_embed"