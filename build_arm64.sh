#!/bin/bash
# build_arm64.sh - ARM64専用ビルドスクリプト
set -e

echo "=== Voice Converter ARM64 ビルド ==="

# カラー出力
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# プロジェクトディレクトリ
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# ビルドディレクトリの準備
echo -e "${YELLOW}既存のビルドをクリーンアップ...${NC}"
rm -rf build_arm64 dist_arm64

# Poetry環境の確認と有効化
echo -e "${YELLOW}Poetry環境を確認...${NC}"
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetryがインストールされていません${NC}"
    exit 1
fi

VENV_PATH=$(poetry env info --path)
if [ -z "$VENV_PATH" ]; then
    echo -e "${RED}Poetry環境が見つかりません${NC}"
    exit 1
fi

source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✓ Poetry環境をアクティベート${NC}"

# アーキテクチャの確認
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    echo -e "${RED}警告: 現在のアーキテクチャは $ARCH です。ARM64環境で実行してください。${NC}"
fi

# PyInstallerのインストール
pip install -q pyinstaller==6.*

# 必須ファイルの確認
echo -e "${YELLOW}必須ファイルを確認...${NC}"
mkdir -p model_dir
if [ ! -f model_dir/hubert_base.pt ]; then
    echo "dummy" > model_dir/hubert_base.pt
fi
if [ ! -f model_dir/rmvpe.pt ]; then
    echo "dummy" > model_dir/rmvpe.pt
fi

# ARM64ビルド
echo -e "${YELLOW}ARM64版をビルド中...${NC}"
pyinstaller --clean --noconfirm \
    --distpath dist_arm64 \
    --workpath build_arm64 \
    rvc_minimal.spec

# ビルド結果の確認
if [ ! -d "dist_arm64/VoiceConverter.app" ]; then
    echo -e "${RED}ARM64ビルドに失敗しました${NC}"
    exit 1
fi

# アーキテクチャの確認
BUILT_ARCH=$(lipo -info "dist_arm64/VoiceConverter.app/Contents/MacOS/VoiceConverter" | awk '{print $NF}')
echo -e "${GREEN}✓ ARM64ビルド完了: $BUILT_ARCH${NC}"

# バイナリの最適化
echo -e "${YELLOW}バイナリを最適化中...${NC}"
find "dist_arm64/VoiceConverter.app/Contents" -name "*.dylib" -type f -exec strip -x {} \; 2>/dev/null || true
find "dist_arm64/VoiceConverter.app/Contents" -name "*.so" -type f -exec strip -x {} \; 2>/dev/null || true
strip -x "dist_arm64/VoiceConverter.app/Contents/MacOS/VoiceConverter" 2>/dev/null || true

# サイズ確認
APP_SIZE=$(du -sh "dist_arm64/VoiceConverter.app" | cut -f1)
echo -e "${GREEN}✓ ARM64版サイズ: $APP_SIZE${NC}"

echo -e "\n${GREEN}=== ARM64ビルド完了 ===${NC}"
