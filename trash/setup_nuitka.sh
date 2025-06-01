#!/bin/bash
# Nuitka セットアップスクリプト

echo "🔧 Setting up Nuitka for Voice Converter build..."

# 仮想環境が有効かチェック
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider using one."
fi

# Nuitkaをインストール
echo "📦 Installing Nuitka..."
pip install nuitka

# macOS開発ツールの確認
echo "🔍 Checking macOS development tools..."
if xcode-select -p &> /dev/null; then
    echo "✅ Xcode command line tools found"
else
    echo "❌ Xcode command line tools not found"
    echo "   Please install with: xcode-select --install"
    exit 1
fi

# Pythonバージョンの確認
echo "🐍 Python version: $(python --version)"

# 必要なパッケージをインストール
echo "📦 Installing additional dependencies..."
pip install --upgrade setuptools wheel

echo "✅ Nuitka setup completed!"
echo ""
echo "🚀 To build the app, run:"
echo "   ./build_advanced.py"
echo "   or"
echo "   ./build_mac_app.sh"