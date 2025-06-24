#!/bin/bash
# merge_universal.sh - ユニバーサルバイナリ結合スクリプト
set -e

echo "=== Voice Converter ユニバーサルバイナリ結合 ==="

# カラー出力
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# プロジェクトディレクトリ
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# ARM64版の確認
if [ ! -d "dist_arm64/VoiceConverter.app" ]; then
    echo -e "${RED}ARM64版が見つかりません。先に build_arm64.sh を実行してください。${NC}"
    exit 1
fi

# x86_64版の確認
if [ ! -d "dist_x86_64/VoiceConverter.app" ]; then
    echo -e "${RED}x86_64版が見つかりません。先に build_x86_64.sh を実行してください。${NC}"
    exit 1
fi

# ユニバーサル版のディレクトリ準備
echo -e "${YELLOW}ユニバーサル版ディレクトリを準備...${NC}"
rm -rf dist_universal
mkdir -p dist_universal

# ARM64版をベースとしてコピー
echo -e "${YELLOW}ARM64版をベースとしてコピー...${NC}"
cp -R dist_arm64/VoiceConverter.app dist_universal/

# メインバイナリの結合
echo -e "${YELLOW}メインバイナリを結合...${NC}"
lipo -create \
    dist_arm64/VoiceConverter.app/Contents/MacOS/VoiceConverter \
    dist_x86_64/VoiceConverter.app/Contents/MacOS/VoiceConverter \
    -output dist_universal/VoiceConverter.app/Contents/MacOS/VoiceConverter

echo -e "${GREEN}✓ メインバイナリを結合${NC}"

# すべての.dylibファイルを結合
echo -e "${YELLOW}動的ライブラリを結合...${NC}"
find dist_arm64/VoiceConverter.app -name "*.dylib" | while read arm64_lib; do
    relative_path=${arm64_lib#dist_arm64/VoiceConverter.app/}
    x86_64_lib="dist_x86_64/VoiceConverter.app/$relative_path"
    universal_lib="dist_universal/VoiceConverter.app/$relative_path"
    
    if [ -f "$x86_64_lib" ]; then
        echo -n "  結合: $(basename "$arm64_lib")... "
        lipo -create "$arm64_lib" "$x86_64_lib" -output "$universal_lib" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}OK${NC}"
        else
            # 結合できない場合はARM64版をコピー
            cp "$arm64_lib" "$universal_lib"
            echo -e "${YELLOW}ARM64のみ${NC}"
        fi
    fi
done

# すべての.soファイルを結合
echo -e "${YELLOW}Python拡張モジュールを結合...${NC}"
find dist_arm64/VoiceConverter.app -name "*.so" | while read arm64_so; do
    relative_path=${arm64_so#dist_arm64/VoiceConverter.app/}
    x86_64_so="dist_x86_64/VoiceConverter.app/$relative_path"
    universal_so="dist_universal/VoiceConverter.app/$relative_path"
    
    if [ -f "$x86_64_so" ]; then
        echo -n "  結合: $(basename "$arm64_so")... "
        lipo -create "$arm64_so" "$x86_64_so" -output "$universal_so" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}OK${NC}"
        else
            # 結合できない場合はARM64版をコピー
            cp "$arm64_so" "$universal_so"
            echo -e "${YELLOW}ARM64のみ${NC}"
        fi
    fi
done

# コード署名
echo -e "${YELLOW}コード署名を実行...${NC}"
codesign --force --deep -s - dist_universal/VoiceConverter.app

# アーキテクチャの確認
echo -e "${YELLOW}結合結果を確認...${NC}"
UNIVERSAL_ARCH=$(lipo -info "dist_universal/VoiceConverter.app/Contents/MacOS/VoiceConverter")
echo -e "${GREEN}✓ $UNIVERSAL_ARCH${NC}"

# サイズ確認
APP_SIZE=$(du -sh "dist_universal/VoiceConverter.app" | cut -f1)
echo -e "${GREEN}✓ ユニバーサル版サイズ: $APP_SIZE${NC}"

# DMG作成オプション
echo -e "\n${YELLOW}DMGを作成しますか？ (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}DMGを作成中...${NC}"
    
    # 既存のDMGを削除
    rm -f VoiceConverter-Universal.dmg
    
    # DMG作成
    hdiutil create -volname "Voice Converter" \
        -srcfolder dist_universal/VoiceConverter.app \
        -ov -format UDZO \
        VoiceConverter-Universal.dmg
    
    echo -e "${GREEN}✓ DMG作成完了: VoiceConverter-Universal.dmg${NC}"
fi

echo -e "\n${GREEN}=== ユニバーサルバイナリ作成完了！ ===${NC}"
echo -e "アプリ: ${GREEN}dist_universal/VoiceConverter.app${NC}"
echo -e "対応: ${GREEN}Intel Mac & Apple Silicon Mac${NC}"
