#!/usr/bin/env python3
"""
RVC GUI 一発実行スクリプト (Python版)
使用方法: python run_gui.py
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🎵 RVC GUI 起動スクリプト (Python版)")
    
    project_dir = Path(__file__).parent.absolute()
    venv_tkinter = project_dir / "venv_tkinter_fix"
    
    print(f"📁 プロジェクトディレクトリ: {project_dir}")
    
    # 1. Homebrew Python 3.11の確認
    homebrew_python = "/opt/homebrew/bin/python3.11"
    if not os.path.exists(homebrew_python):
        print("❌ Homebrew Python 3.11が見つかりません")
        print("   以下のコマンドでインストールしてください:")
        print("   brew install python@3.11 python-tk@3.11")
        sys.exit(1)
    
    # 2. tkinter対応の仮想環境作成
    if not venv_tkinter.exists():
        print("🔧 tkinter対応仮想環境を作成中...")
        subprocess.run([homebrew_python, "-m", "venv", str(venv_tkinter)], check=True)
        
        python_path = venv_tkinter / "bin" / "python"
        print("📦 pipとclickをインストール中...")
        subprocess.run([str(python_path), "-m", "ensurepip", "--upgrade"], check=True)
        subprocess.run([str(python_path), "-m", "pip", "install", "click"], check=True)
    
    # 3. Poetry環境のチェック
    print("🔧 Poetry環境をチェック中...")
    try:
        result = subprocess.run(["poetry", "check", "--lock"], 
                              capture_output=True, text=True, cwd=str(project_dir))
        if result.returncode != 0:
            print("📦 Poetry依存関係をインストール中...")
            subprocess.run(["poetry", "install"], check=True, cwd=str(project_dir))
    except FileNotFoundError:
        print("❌ Poetryが見つかりません。以下のコマンドでインストールしてください:")
        print("   curl -sSL https://install.python-poetry.org | python3 -")
        sys.exit(1)
    
    # 4. GUIを起動
    print("🚀 GUI起動中...")
    print("⚠️  初回起動時は時間がかかる場合があります")
    
    python_path = venv_tkinter / "bin" / "python"
    gui_path = project_dir / "gui_dark_mode.py"
    
    try:
        subprocess.run([str(python_path), str(gui_path)], check=True)
    except KeyboardInterrupt:
        print("\n👋 GUI終了")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()