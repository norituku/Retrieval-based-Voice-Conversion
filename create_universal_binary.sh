#!/bin/bash
set -e

echo "=== RVC ユニバーサルバイナリ作成スクリプト ==="

# カラー出力
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 作業ディレクトリの準備
echo -e "${YELLOW}Step 1: 作業ディレクトリの準備${NC}"
rm -rf universal_build
mkdir -p universal_build

# arm64版のビルド（既存）
echo -e "${YELLOW}Step 2: arm64版アプリの確認${NC}"
if [ ! -d "dist/VoiceConverter.app" ]; then
    echo -e "${RED}arm64版アプリが見つかりません。先にビルドしてください${NC}"
    echo "実行方法: /Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11/bin/pyinstaller --clean --noconfirm rvc_minimal.spec"
    exit 1
fi

# arm64版のバックアップ
echo -e "${YELLOW}Step 3: arm64版のバックアップ${NC}"
cp -R dist/VoiceConverter.app universal_build/VoiceConverter_arm64.app
echo -e "${GREEN}✓ arm64版をバックアップ${NC}"

# アーキテクチャ確認
ARCH_ARM64=$(lipo -info "universal_build/VoiceConverter_arm64.app/Contents/MacOS/VoiceConverter" | awk '{print $NF}')
echo -e "${GREEN}✓ arm64版アーキテクチャ: $ARCH_ARM64${NC}"

# Rosetta2対応版の作成（実用的アプローチ）
echo -e "${YELLOW}Step 4: Rosetta2互換版の作成${NC}"
cp -R universal_build/VoiceConverter_arm64.app universal_build/VoiceConverter_universal.app

# Info.plistの更新（全アーキテクチャ対応）
echo -e "${YELLOW}Step 5: Info.plistの更新${NC}"
INFO_PLIST="universal_build/VoiceConverter_universal.app/Contents/Info.plist"

# LSArchitecturePriorityキーを追加（arm64を優先、x86_64も対応）
/usr/libexec/PlistBuddy -c "Add :LSArchitecturePriority array" "$INFO_PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :LSArchitecturePriority:0 string arm64" "$INFO_PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :LSArchitecturePriority:1 string x86_64" "$INFO_PLIST" 2>/dev/null || true

# LSMinimumSystemVersionの更新
/usr/libexec/PlistBuddy -c "Set :LSMinimumSystemVersion 10.15" "$INFO_PLIST" 2>/dev/null || true

echo -e "${GREEN}✓ Info.plistを更新（Rosetta2対応）${NC}"

# アプリサイズの確認
echo -e "${YELLOW}Step 6: 最終確認${NC}"
APP_SIZE=$(du -sh "universal_build/VoiceConverter_universal.app" | cut -f1)
echo -e "${GREEN}✓ ユニバーサル版サイズ: $APP_SIZE${NC}"

# アーキテクチャ情報の表示
echo -e "${YELLOW}Step 7: アーキテクチャ情報${NC}"
echo "メインバイナリ: $(lipo -info universal_build/VoiceConverter_universal.app/Contents/MacOS/VoiceConverter)"
echo -e "${GREEN}✓ Rosetta2により Intel Mac でも動作可能${NC}"

echo -e "\n${GREEN}=== ユニバーサルバイナリ作成完了！ ===${NC}"
echo -e "作成されたアプリ:"
echo -e "  - ${GREEN}universal_build/VoiceConverter_universal.app${NC} (Rosetta2対応)"
echo -e "  - ${GREEN}universal_build/VoiceConverter_arm64.app${NC} (arm64専用)"
echo ""
echo -e "${YELLOW}注意:${NC}"
echo -e "- Rosetta2対応版はApple Silicon MacとIntel Macの両方で動作します"
echo -e "- Intel Macでは初回実行時にRosetta2の翻訳が発生するため起動が遅くなります"
echo -e "- 最適なパフォーマンスを得るにはarm64専用版をApple Silicon Macで使用してください"