#!/bin/bash
# Voice Converter 依存関係インストールスクリプト

echo "========================================="
echo "Voice Converter Setup"
echo "========================================="
echo ""

# Python3の確認
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed."
    echo "Please install Python 3.10 or later."
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

echo "Installing required packages..."
echo "This may take several minutes..."
echo ""

# 基本的な依存関係をインストール
python3 -m pip install --upgrade pip

# 必要なパッケージをインストール（最小限）
echo "Installing audio processing libraries..."
python3 -m pip install --user soundfile librosa scipy numpy

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "To run the Voice Converter:"
echo "  ./run_dark_mode_gui.sh"
echo ""
echo "If you encounter any issues, please install the full dependencies:"
echo "  python3 -m pip install -r requirements_minimal.txt"
echo ""
