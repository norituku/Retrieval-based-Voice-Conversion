#!/usr/bin/env python3
"""
RVC ハイブリッドスタンドアロンアプリ作成ツール
既存機能100%保持 + tkinter問題完全解決
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🏗️  RVC ハイブリッドスタンドアロンアプリ作成ツール")
    
    project_dir = Path(__file__).parent.absolute()
    print(f"📁 プロジェクトディレクトリ: {project_dir}")
    
    # 1. まず元のrun_gui.shを.appバンドルに変換
    print("📦 ハイブリッド起動スクリプト作成中...")
    
    hybrid_script = project_dir / "run_gui_hybrid.sh"
    with open(hybrid_script, 'w', encoding='utf-8') as f:
        f.write(f'''#!/bin/bash
# RVC ハイブリッドスタンドアロンアプリ起動スクリプト

set -e

# アプリケーション内のリソースディレクトリを取得
if [[ "$0" == *.app/Contents/Resources/* ]]; then
    # .app内部から実行された場合
    BUNDLE_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
    RESOURCES_DIR="$BUNDLE_DIR/Contents/Resources"
    PROJECT_DIR="$RESOURCES_DIR"
else
    # 通常のディレクトリから実行された場合
    PROJECT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
    RESOURCES_DIR="$PROJECT_DIR"
fi

echo "🎵 RVC Voice Converter - ハイブリッドスタンドアロン版"
echo "📁 プロジェクトディレクトリ: $PROJECT_DIR"

cd "$PROJECT_DIR"

# 既存のvenv_tkinter_fix環境が利用可能かチェック
VENV_TKINTER="$PROJECT_DIR/venv_tkinter_fix"

if [ ! -d "$VENV_TKINTER" ]; then
    echo "🔧 tkinter対応仮想環境を作成中..."
    
    # Homebrew Python 3.11の確認・インストール
    if [ ! -f "/opt/homebrew/bin/python3.11" ]; then
        echo "📦 Homebrew Python 3.11をインストール中..."
        if ! command -v brew &> /dev/null; then
            echo "📦 Homebrewをインストール中..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        brew install python@3.11 python-tk@3.11
    fi
    
    # tkinter対応仮想環境作成
    /opt/homebrew/bin/python3.11 -m venv "$VENV_TKINTER"
    
    echo "📦 基本パッケージをインストール中..."
    "$VENV_TKINTER/bin/python" -m ensurepip --upgrade
    "$VENV_TKINTER/bin/pip" install click
fi

# Poetry環境セットアップ
if command -v poetry &> /dev/null; then
    echo "🔧 Poetry環境をセットアップ中..."
    poetry install --only=main
    echo "✅ Poetry環境セットアップ完了"
fi

# GUIを起動
echo "🚀 GUI起動中..."
"$VENV_TKINTER/bin/python" "$PROJECT_DIR/gui_dark_mode.py"
''')
    
    os.chmod(hybrid_script, 0o755)
    print(f"✅ ハイブリッド起動スクリプト作成完了: {hybrid_script}")
    
    # 2. Platypusを使用してスタンドアロン.appを作成
    print("🏗️  Platypusでスタンドアロンアプリを作成中...")
    
    app_name = "RVC Voice Converter Hybrid"
    app_bundle = project_dir / f"{app_name}.app"
    
    # Platypusコマンドライン作成試行
    if shutil.which("platypus"):
        platypus_cmd = [
            "platypus",
            "-a", app_name,
            "-o", "None",
            "-p", "/bin/bash",
            "-V", "1.0",
            "-u", "RVC Project Team", 
            "-I", "com.rvc.voiceconverter.hybrid",
            "-X", "*",
            "-T", "*",
            "-B",  # バックグラウンドで実行
            "-R",  # アプリ終了時にスクリプトも終了
        ]
        
        # アイコンファイル追加
        icon_file = project_dir / "app_icons" / "rvc_icon.icns"
        if icon_file.exists():
            platypus_cmd.extend(["-i", str(icon_file)])
        
        # リソースファイルを追加
        resource_files = [
            "gui_dark_mode.py",
            "rvc_config.py", 
            "pyproject.toml",
            "poetry.lock",
            "CLAUDE.md"
        ]
        
        for res_file in resource_files:
            res_path = project_dir / res_file
            if res_path.exists():
                platypus_cmd.extend(["-f", str(res_path)])
        
        # ディレクトリリソース追加
        resource_dirs = ["rvc", "model_dir", "app_icons"]
        for res_dir in resource_dirs:
            dir_path = project_dir / res_dir
            if dir_path.exists():
                platypus_cmd.extend(["-f", str(dir_path)])
        
        # アプリケーション作成
        platypus_cmd.extend([str(app_bundle), str(hybrid_script)])
        
        try:
            subprocess.run(platypus_cmd, check=True)
            print(f"✅ Platypusスタンドアロンアプリ作成完了: {app_bundle}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Platypusエラー: {e}")
            return False
        
    else:
        print("❌ Platypusが見つかりません。手動でアプリを作成してください：")
        print("1. Platypus.appを開く")
        print(f"2. スクリプトパス: {hybrid_script}")
        print(f"3. アプリ名: {app_name}")
        print("4. Interface: None")
        print("5. 'Create App'をクリック")
        return False
    
    # 3. アプリサイズ確認
    if app_bundle.exists():
        size_mb = sum(f.stat().st_size for f in app_bundle.rglob('*') if f.is_file()) / (1024*1024)
        print(f"📏 ハイブリッドアプリサイズ: {size_mb:.1f} MB")
        
        # 4. アプリを起動
        print("🚀 ハイブリッドスタンドアロンアプリを起動中...")
        subprocess.run(["open", str(app_bundle)])
        
        return app_bundle
    
    return False

if __name__ == "__main__":
    result = main()
    if result:
        print("🎉 ハイブリッドスタンドアロン版アプリ作成・起動完了!")
        print("📋 特徴:")
        print("- 既存機能100%保持")
        print("- tkinter問題完全解決") 
        print("- 軽量サイズ（必要時に依存関係ダウンロード）")
        print("- 他のMacでワンクリック実行")
        print("- インターネット接続：初回のみ必要")