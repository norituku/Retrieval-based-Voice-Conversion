#!/bin/bash
set -e

echo "=== VoiceConverter コード署名修復スクリプト ==="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_PATH="dist/VoiceConverter.app"

if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}エラー: $APP_PATH が見つかりません${NC}"
    exit 1
fi

# 1. 既存の署名を削除
echo -e "${YELLOW}Step 1: 既存の署名を削除${NC}"
codesign --remove-signature "$APP_PATH" 2>/dev/null || true
find "$APP_PATH" -name "*.dylib" -o -name "*.so" -exec codesign --remove-signature {} \; 2>/dev/null || true
echo -e "${GREEN}✓ 署名を削除${NC}"

# 2. 拡張属性を削除（quarantine フラグなど）
echo -e "\n${YELLOW}Step 2: 拡張属性を削除${NC}"
find "$APP_PATH" -type f -exec xattr -c {} \; 2>/dev/null || true
echo -e "${GREEN}✓ 拡張属性を削除${NC}"

# 3. 個別ライブラリファイルに署名
echo -e "\n${YELLOW}Step 3: 全ライブラリファイルに個別署名${NC}"
# .soファイルに個別署名
find "$APP_PATH" -name "*.so" -exec codesign --force --sign - {} \; 2>/dev/null || true
# .dylibファイルに個別署名
find "$APP_PATH" -name "*.dylib" -exec codesign --force --sign - {} \; 2>/dev/null || true
# Python拡張モジュール(.cpython-311-darwin.so)に個別署名
find "$APP_PATH" -name "*.cpython-*-darwin.so" -exec codesign --force --sign - {} \; 2>/dev/null || true

# torch/libディレクトリ内のライブラリに個別署名（重要）
echo -e "${YELLOW}Step 3.1: torchライブラリディレクトリに個別署名${NC}"
if [ -d "$APP_PATH/Contents/Resources/torch/lib" ]; then
    find "$APP_PATH/Contents/Resources/torch/lib" -type f \( -name "*.dylib" -o -name "*.so" \) \
        -exec codesign --force --sign - {} \; 2>/dev/null || true
    echo -e "${GREEN}✓ torchライブラリ署名完了${NC}"
else
    echo -e "${YELLOW}⚠️  torch/libディレクトリが見つかりません${NC}"
fi

# torchディレクトリ全体のバイナリファイルに署名
if [ -d "$APP_PATH/Contents/Resources/torch" ]; then
    find "$APP_PATH/Contents/Resources/torch" -type f \( -name "*.dylib" -o -name "*.so" \) \
        -exec codesign --force --sign - {} \; 2>/dev/null || true
    echo -e "${GREEN}✓ torch全体署名完了${NC}"
fi

echo -e "${GREEN}✓ 個別ライブラリ署名完了${NC}"

# 4. ad-hoc署名を再適用（深層署名）
echo -e "\n${YELLOW}Step 4: ad-hoc署名を適用${NC}"
codesign --force --deep --sign - "$APP_PATH"
echo -e "${GREEN}✓ ad-hoc署名完了${NC}"

# 5. 署名の検証
echo -e "\n${YELLOW}Step 5: 署名を検証${NC}"
if codesign --verify --deep --verbose "$APP_PATH"; then
    echo -e "${GREEN}✓ 署名検証成功！${NC}"
else
    echo -e "${RED}署名検証失敗${NC}"
    exit 1
fi

# 6. Gatekeeperをバイパス（初回起動用）
echo -e "\n${YELLOW}Step 6: Gatekeeper属性を設定${NC}"
spctl --add "$APP_PATH" 2>/dev/null || true
echo -e "${GREEN}✓ Gatekeeper設定完了${NC}"

echo -e "\n${GREEN}=== 修復完了！ ===${NC}"
echo -e "アプリを起動するには:"
echo -e "1. Finderで ${GREEN}$APP_PATH${NC} を右クリック"
echo -e "2. \"開く\" を選択"
echo -e "3. 警告が出た場合は \"開く\" をクリック"
echo -e "\nまたは、ターミナルから直接起動:"
echo -e "${GREEN}open $APP_PATH${NC}" 