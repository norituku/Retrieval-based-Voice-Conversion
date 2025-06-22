#!/bin/bash
set -e

echo "=== PyTorchライブラリ修復スクリプト ==="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_PATH="dist/VoiceConverter.app"
TORCH_LIB_DIR="$APP_PATH/Contents/Frameworks/torch/lib"

# Poetry環境のパスを取得
VENV_PATH=$(poetry env info --path)
SOURCE_TORCH_LIB="$VENV_PATH/lib/python3.11/site-packages/torch/lib"

if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}エラー: $APP_PATH が見つかりません${NC}"
    echo "ビルドが完了するまでお待ちください..."
    exit 1
fi

# torch/libディレクトリを作成
echo -e "${YELLOW}Step 1: torch/libディレクトリを作成${NC}"
mkdir -p "$TORCH_LIB_DIR"
echo -e "${GREEN}✓ ディレクトリ作成完了${NC}"

# PyTorchライブラリをコピー
echo -e "\n${YELLOW}Step 2: PyTorchライブラリをコピー${NC}"
if [ -d "$SOURCE_TORCH_LIB" ]; then
    cp -r "$SOURCE_TORCH_LIB"/* "$TORCH_LIB_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✓ ライブラリコピー完了${NC}"
else
    echo -e "${RED}警告: Poetry環境のtorch/libが見つかりません${NC}"
fi

# 署名を再適用
echo -e "\n${YELLOW}Step 3: 署名を再適用${NC}"
find "$APP_PATH" -name "*.dylib" -o -name "*.so" -exec codesign --remove-signature {} \; 2>/dev/null || true
codesign --force --deep --sign - "$APP_PATH"
echo -e "${GREEN}✓ 署名完了${NC}"

# ファイルの存在確認
echo -e "\n${YELLOW}Step 4: 必須ファイルの確認${NC}"
if [ -f "$TORCH_LIB_DIR/libtorch_global_deps.dylib" ]; then
    echo -e "${GREEN}✓ libtorch_global_deps.dylib が存在します${NC}"
else
    echo -e "${RED}✗ libtorch_global_deps.dylib が見つかりません${NC}"
fi

echo -e "\n${GREEN}=== 修復完了！ ===${NC}"
echo -e "アプリを起動: ${GREEN}open $APP_PATH${NC}" 