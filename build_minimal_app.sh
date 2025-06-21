#!/bin/bash
set -e

echo "=== Voice Converter 最小容量ビルドスクリプト ==="

# カラー出力
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Poetry環境の確認とアクティベート
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

# 2. PyInstallerのインストール確認
echo -e "\n${YELLOW}Step 2: PyInstallerの準備${NC}"
pip install -q pyinstaller==6.*
echo -e "${GREEN}✓ PyInstaller 6.x をインストール${NC}"

# 3. 一時的なモデルファイルのダミー作成（ビルド時のみ）
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

# 4. クリーンビルド
echo -e "\n${YELLOW}Step 4: クリーンビルド実行${NC}"
rm -rf build dist 2>/dev/null || true
pyinstaller --clean --noconfirm rvc_minimal.spec

# 5. 不要ファイルの削除（さらなる容量削減）
echo -e "\n${YELLOW}Step 5: 不要ファイルの削除${NC}"
APP_PATH="dist/VoiceConverter.app"
CONTENTS="$APP_PATH/Contents"
FRAMEWORKS="$CONTENTS/Frameworks"
RESOURCES="$CONTENTS/Resources"

# 削除対象
REMOVE_PATTERNS=(
    # PyTorchの不要部分
    "*/test_*"
    "*/testing/*"
    "*/include/*"
    "*/cmake/*"
    "*/share/doc/*"
    "*/share/man/*"
    
    # デバッグシンボル
    "*.dSYM"
    "*_debug.dylib"
    
    # キャッシュ
    "__pycache__"
    "*.pyc"
    "*.pyo"
    
    # ドキュメント
    "*.md"
    "*.rst"
    "*.txt"
    "LICENSE*"
    "NOTICE*"
    
    # 開発ツール
    "*-config"
    "*.h"
    "*.hpp"
)

for pattern in "${REMOVE_PATTERNS[@]}"; do
    find "$CONTENTS" -name "$pattern" -type f -delete 2>/dev/null || true
    find "$CONTENTS" -name "$pattern" -type d -exec rm -rf {} + 2>/dev/null || true
done

echo -e "${GREEN}✓ 不要ファイルを削除${NC}"

# 6. バイナリのstrip（デバッグシンボル削除）
echo -e "\n${YELLOW}Step 6: バイナリの最適化${NC}"
find "$CONTENTS" -name "*.dylib" -type f -exec strip -x {} \; 2>/dev/null || true
find "$CONTENTS" -name "*.so" -type f -exec strip -x {} \; 2>/dev/null || true
strip -x "$CONTENTS/MacOS/VoiceConverter" 2>/dev/null || true

echo -e "${GREEN}✓ デバッグシンボルを削除${NC}"

# 7. 重複ライブラリのチェックと削除
echo -e "\n${YELLOW}Step 7: 重複ライブラリの削除${NC}"
declare -A lib_map
while IFS= read -r -d '' file; do
    basename=$(basename "$file")
    if [[ -n "${lib_map[$basename]}" ]]; then
        # 重複発見 - サイズを比較して大きい方を残す
        existing="${lib_map[$basename]}"
        if [[ $(stat -f%z "$file") -gt $(stat -f%z "$existing") ]]; then
            rm -f "$existing"
            lib_map[$basename]="$file"
            echo "  重複削除: $existing"
        else
            rm -f "$file"
            echo "  重複削除: $file"
        fi
    else
        lib_map[$basename]="$file"
    fi
done < <(find "$CONTENTS" -name "*.dylib" -o -name "*.so" -print0)

# 8. アプリサイズの計算と表示
echo -e "\n${YELLOW}Step 8: 最終サイズ確認${NC}"
APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
echo -e "${GREEN}✓ アプリサイズ: $APP_SIZE${NC}"

# サイズ内訳を表示
echo -e "\n${YELLOW}サイズ内訳:${NC}"
echo "Frameworks: $(du -sh "$FRAMEWORKS" 2>/dev/null | cut -f1 || echo "N/A")"
echo "Resources:  $(du -sh "$RESOURCES" 2>/dev/null | cut -f1 || echo "N/A")"
echo "MacOS:      $(du -sh "$CONTENTS/MacOS" 2>/dev/null | cut -f1 || echo "N/A")"

# 9. DMG作成（オプション）
echo -e "\n${YELLOW}Step 9: DMG作成${NC}"
if command -v create-dmg &> /dev/null; then
    DMG_NAME="VoiceConverter_minimal.dmg"
    rm -f "$DMG_NAME"
    
    create-dmg \
        --volname "Voice Converter" \
        --volicon "app_icons/rvc_icon.icns" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "VoiceConverter.app" 150 185 \
        --app-drop-link 450 185 \
        --hide-extension "VoiceConverter.app" \
        --format UDZO \
        --hdiutil-quiet \
        "$DMG_NAME" \
        "$APP_PATH"
    
    DMG_SIZE=$(du -h "$DMG_NAME" | cut -f1)
    echo -e "${GREEN}✓ DMG作成完了: $DMG_NAME (サイズ: $DMG_SIZE)${NC}"
else
    echo -e "${YELLOW}  create-dmg がインストールされていません。DMG作成をスキップ${NC}"
fi

echo -e "\n${GREEN}=== ビルド完了！ ===${NC}"
echo -e "アプリ: ${GREEN}$APP_PATH${NC}"
echo -e "サイズ: ${GREEN}$APP_SIZE${NC}" 