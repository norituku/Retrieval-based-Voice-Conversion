#!/bin/bash
set -e

echo "=== Voice Converter ユニバーサルバイナリビルドスクリプト ==="

# カラー出力
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Poetry環境の確認
echo -e "${YELLOW}Step 1: Poetry環境の確認${NC}"
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry がインストールされていません${NC}"
    exit 1
fi

VENV_PATH=$(poetry env info --path)
if [ -z "$VENV_PATH" ]; then
    echo -e "${RED}Poetry仮想環境が見つかりません。先に 'poetry install' を実行してください${NC}"
    exit 1
fi

source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✓ Poetry環境をアクティベート: $VENV_PATH${NC}"

# PyInstallerのインストール
echo -e "\n${YELLOW}Step 2: PyInstallerの準備${NC}"
pip install -q pyinstaller==6.*
echo -e "${GREEN}✓ PyInstaller 6.x をインストール${NC}"

# 必須ファイルの確認
echo -e "\n${YELLOW}Step 3: 必須ファイルの確認${NC}"
mkdir -p model_dir
if [ ! -f model_dir/hubert_base.pt ]; then
    echo "dummy" > model_dir/hubert_base.pt
    echo -e "${YELLOW}  警告: hubert_base.pt が見つかりません（ダミーファイルを作成）${NC}"
fi
if [ ! -f model_dir/rmvpe.pt ]; then
    echo "dummy" > model_dir/rmvpe.pt
    echo -e "${YELLOW}  警告: rmvpe.pt が見つかりません（ダミーファイルを作成）${NC}"
fi

# 現在のアーキテクチャでビルド
echo -e "\n${YELLOW}Step 4: 現在のアーキテクチャ ($(arch)) でビルド${NC}"
rm -rf build dist 2>/dev/null || true
pyinstaller --clean --noconfirm rvc_minimal.spec

# ビルド結果の確認
if [ ! -d "dist/VoiceConverter.app" ]; then
    echo -e "${RED}ビルドに失敗しました${NC}"
    exit 1
fi

# バイナリアーキテクチャの確認
ARCH=$(lipo -info "dist/VoiceConverter.app/Contents/MacOS/VoiceConverter" | awk '{print $NF}')
echo -e "${GREEN}✓ ビルド完了: $ARCH${NC}"

# Intel版のダウンロードまたは別環境でのビルドが必要な場合の説明
echo -e "\n${YELLOW}注意: 完全なユニバーサルバイナリを作成するには:${NC}"
echo -e "1. Intel Mac環境で同じビルドを実行"
echo -e "2. 両方のバイナリを lipo コマンドで結合:"
echo -e "   ${GREEN}lipo -create -output VoiceConverter_universal VoiceConverter_arm64 VoiceConverter_x86_64${NC}"

# 不要ファイルの削除（容量削減）
echo -e "\n${YELLOW}Step 5: 不要ファイルの削除${NC}"
APP_PATH="dist/VoiceConverter.app"
CONTENTS="$APP_PATH/Contents"

# 削除対象
REMOVE_PATTERNS=(
    "*/test_*"
    "*/testing/*"
    "*/include/*"
    "*/cmake/*"
    "*/share/doc/*"
    "*/share/man/*"
    "*.dSYM"
    "*_debug.dylib"
    "__pycache__"
    "*.pyc"
    "*.pyo"
    "*.md"
    "*.rst"
    "*.txt"
    "LICENSE*"
    "NOTICE*"
    "*-config"
    "*.h"
    "*.hpp"
)

for pattern in "${REMOVE_PATTERNS[@]}"; do
    find "$CONTENTS" -name "$pattern" -type f -delete 2>/dev/null || true
    find "$CONTENTS" -name "$pattern" -type d -exec rm -rf {} + 2>/dev/null || true
done

echo -e "${GREEN}✓ 不要ファイルを削除${NC}"

# バイナリのstrip
echo -e "\n${YELLOW}Step 6: バイナリの最適化${NC}"
find "$CONTENTS" -name "*.dylib" -type f -exec strip -x {} \; 2>/dev/null || true
find "$CONTENTS" -name "*.so" -type f -exec strip -x {} \; 2>/dev/null || true
strip -x "$CONTENTS/MacOS/VoiceConverter" 2>/dev/null || true

echo -e "${GREEN}✓ デバッグシンボルを削除${NC}"

# アプリサイズの確認
echo -e "\n${YELLOW}最終サイズ確認${NC}"
APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
echo -e "${GREEN}✓ アプリサイズ: $APP_SIZE${NC}"

# ユニバーサルバイナリ作成のための追加手順
echo -e "\n${YELLOW}=== ユニバーサルバイナリ作成手順 ===${NC}"
echo -e "現在は ${GREEN}$ARCH${NC} 版のみです。"
echo -e "\n完全なユニバーサルバイナリ作成には:"
echo -e "1. Intel Macまたは Rosetta 2 環境で同じビルドを実行"
echo -e "2. 作成された2つの.appを結合:"
echo ""
echo -e "${GREEN}# 例: 両アーキテクチャのバイナリを結合${NC}"
echo -e "mkdir -p universal_build"
echo -e "cp -R dist/VoiceConverter.app universal_build/VoiceConverter_universal.app"
echo -e "lipo -create -output universal_build/VoiceConverter_universal.app/Contents/MacOS/VoiceConverter \\"
echo -e "     dist_arm64/VoiceConverter.app/Contents/MacOS/VoiceConverter \\"
echo -e "     dist_x86_64/VoiceConverter.app/Contents/MacOS/VoiceConverter"
echo ""
echo -e "# すべての.dylibと.soファイルも同様に結合が必要"
echo ""

echo -e "\n${GREEN}=== ビルド完了！ ===${NC}"
echo -e "アプリ: ${GREEN}$APP_PATH${NC} (${ARCH})"
echo -e "サイズ: ${GREEN}$APP_SIZE${NC}" 