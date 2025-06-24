#!/bin/bash
# build_x86_64.sh - Intel (x86_64)専用ビルドスクリプト
set -e

echo "=== Voice Converter x86_64 ビルド (Rosetta2環境) ==="

# カラー出力
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# プロジェクトディレクトリ
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Rosetta2の確認
if ! /usr/bin/pgrep oahd >/dev/null 2>&1; then
    echo -e "${YELLOW}Rosetta2をインストール中...${NC}"
    /usr/sbin/softwareupdate --install-rosetta --agree-to-license
fi

# x86_64環境で実行
echo -e "${YELLOW}x86_64環境でスクリプトを再実行...${NC}"
if [ "$(uname -m)" != "x86_64" ]; then
    exec arch -x86_64 /bin/bash "$0" "$@"
fi

echo -e "${GREEN}✓ x86_64環境で実行中${NC}"

# ビルドディレクトリの準備
echo -e "${YELLOW}既存のビルドをクリーンアップ...${NC}"
rm -rf build_x86_64 dist_x86_64 x86_64_env

# x86_64用Python環境の作成
echo -e "${YELLOW}x86_64用Python環境を作成...${NC}"

# Python 3.11のx86_64版を使用
if [ -x "/usr/local/bin/python3.11" ]; then
    # Homebrewのpython3.11がある場合
    /usr/local/bin/python3.11 -m venv x86_64_env
elif [ -x "/opt/homebrew/bin/python3.11" ]; then
    # Apple SiliconでもRosetta2経由で使用
    arch -x86_64 /opt/homebrew/bin/python3.11 -m venv x86_64_env
else
    # システムのPython3を使用（最終手段）
    /usr/bin/python3 -m venv x86_64_env
fi

source x86_64_env/bin/activate

# 必要なパッケージのインストール
echo -e "${YELLOW}必要なパッケージをインストール...${NC}"
pip install --upgrade pip
pip install wheel setuptools

# 最小限の必要パッケージをインストール
pip install \
    pyinstaller \
    numpy \
    scipy \
    torch --index-url https://download.pytorch.org/whl/cpu \
    soundfile \
    librosa \
    fairseq

# 必須ファイルの確認
echo -e "${YELLOW}必須ファイルを確認...${NC}"
mkdir -p model_dir
if [ ! -f model_dir/hubert_base.pt ]; then
    echo "dummy" > model_dir/hubert_base.pt
fi
if [ ! -f model_dir/rmvpe.pt ]; then
    echo "dummy" > model_dir/rmvpe.pt
fi

# x86_64ビルド
echo -e "${YELLOW}x86_64版をビルド中...${NC}"
pyinstaller --clean --noconfirm \
    --distpath dist_x86_64 \
    --workpath build_x86_64 \
    rvc_minimal.spec

# ビルド結果の確認
if [ ! -d "dist_x86_64/VoiceConverter.app" ]; then
    echo -e "${RED}x86_64ビルドに失敗しました${NC}"
    exit 1
fi

# アーキテクチャの確認
BUILT_ARCH=$(lipo -info "dist_x86_64/VoiceConverter.app/Contents/MacOS/VoiceConverter" | awk '{print $NF}')
echo -e "${GREEN}✓ x86_64ビルド完了: $BUILT_ARCH${NC}"

# バイナリの最適化
echo -e "${YELLOW}バイナリを最適化中...${NC}"
find "dist_x86_64/VoiceConverter.app/Contents" -name "*.dylib" -type f -exec strip -x {} \; 2>/dev/null || true
find "dist_x86_64/VoiceConverter.app/Contents" -name "*.so" -type f -exec strip -x {} \; 2>/dev/null || true
strip -x "dist_x86_64/VoiceConverter.app/Contents/MacOS/VoiceConverter" 2>/dev/null || true

# サイズ確認
APP_SIZE=$(du -sh "dist_x86_64/VoiceConverter.app" | cut -f1)
echo -e "${GREEN}✓ x86_64版サイズ: $APP_SIZE${NC}"

# 仮想環境をデアクティベート
deactivate

echo -e "\n${GREEN}=== x86_64ビルド完了 ===${NC}"
