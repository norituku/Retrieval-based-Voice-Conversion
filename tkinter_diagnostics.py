#!/usr/bin/env python3
"""
tkinter診断スクリプト - macOSでのGUI表示問題を詳細分析
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def run_command(cmd, description=""):
    """コマンドを実行し結果を取得"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_python_environment():
    """Python環境の詳細情報を収集"""
    print("=== Python環境診断 ===")
    print(f"Python実行パス: {sys.executable}")
    print(f"Python版本: {sys.version}")
    print(f"プラットフォーム: {platform.platform()}")
    print(f"アーキテクチャ: {platform.architecture()}")
    
    # 環境変数
    print(f"\nVIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'None')}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'None')}")
    
    # pyenv情報
    stdout, stderr, code = run_command("pyenv version")
    if code == 0:
        print(f"pyenv版本: {stdout}")
    
    print(f"sys.path: {sys.path[:3]}...")  # 最初の3つだけ表示

def test_tkinter_import():
    """tkinterインポートテスト"""
    print("\n=== tkinterインポートテスト ===")
    
    try:
        import tkinter as tk
        print("✅ tkinter基本インポート成功")
        
        try:
            import tkinter.ttk as ttk
            print("✅ tkinter.ttk インポート成功")
        except ImportError as e:
            print(f"❌ tkinter.ttk インポート失敗: {e}")
            
        try:
            # 実際にウィンドウを作成してテスト
            root = tk.Tk()
            root.withdraw()  # ウィンドウを隠す
            print("✅ tkinter Tkウィンドウ作成成功")
            root.destroy()
        except Exception as e:
            print(f"❌ tkinter Tkウィンドウ作成失敗: {e}")
            
    except ImportError as e:
        print(f"❌ tkinter基本インポート失敗: {e}")
        return False
    
    return True

def check_display_environment():
    """ディスプレイ環境チェック"""
    print("\n=== ディスプレイ環境チェック ===")
    
    display = os.environ.get('DISPLAY')
    print(f"DISPLAY環境変数: {display if display else 'None'}")
    
    # macOS固有のチェック
    if platform.system() == "Darwin":
        print("macOSを検出")
        
        # Homebrewでインストールされたtkinter確認
        homebrew_paths = [
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3"
        ]
        
        for path in homebrew_paths:
            if os.path.exists(path):
                print(f"Homebrew Python発見: {path}")
                # このPythonでtkinterテスト
                stdout, stderr, code = run_command(f"{path} -c 'import tkinter; print(\"tkinter OK\")'")
                if code == 0:
                    print(f"  ✅ {path}: tkinter利用可能")
                else:
                    print(f"  ❌ {path}: tkinter不可 - {stderr}")

def find_working_python():
    """動作するPython環境を検索"""
    print("\n=== 動作するPython環境検索 ===")
    
    python_candidates = [
        "/System/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
        "/System/Library/Frameworks/Python.framework/Versions/3.10/bin/python3",
        "/System/Library/Frameworks/Python.framework/Versions/3.9/bin/python3",
        "/opt/homebrew/bin/python3",
        "/usr/local/bin/python3",
        "/usr/bin/python3",
        "python3"
    ]
    
    working_pythons = []
    
    for python_path in python_candidates:
        if python_path == "python3" or os.path.exists(python_path):
            # tkinterテスト
            test_cmd = f"{python_path} -c 'import tkinter; root=tkinter.Tk(); root.withdraw(); print(\"SUCCESS\"); root.destroy()'"
            stdout, stderr, code = run_command(test_cmd)
            
            if code == 0 and "SUCCESS" in stdout:
                print(f"✅ 動作確認: {python_path}")
                working_pythons.append(python_path)
                
                # 詳細情報取得
                version_cmd = f"{python_path} --version"
                version_stdout, _, _ = run_command(version_cmd)
                print(f"   版本: {version_stdout}")
            else:
                print(f"❌ 動作不可: {python_path}")
                if stderr:
                    print(f"   エラー: {stderr}")
    
    return working_pythons

def suggest_solutions(working_pythons):
    """解決策の提案"""
    print("\n=== 解決策の提案 ===")
    
    if working_pythons:
        print("🎉 動作するPython環境が見つかりました！")
        print(f"推奨Python: {working_pythons[0]}")
        
        print("\n💡 解決方法:")
        print(f"1. 以下のコマンドでGUIを起動:")
        print(f"   {working_pythons[0]} gui_dark_mode_enhanced.py")
        
        print(f"\n2. または、起動スクリプトを使用:")
        print(f"   ./launch_gui.sh")
        
    else:
        print("❌ 動作するPython環境が見つかりませんでした")
        print("\n💡 修復方法:")
        print("1. Homebrewでtkinter付きPythonをインストール:")
        print("   brew install python-tk")
        print("\n2. または、pyenvでPythonを再インストール:")
        print("   pyenv install --patch 3.11.9 < <(curl -sSL https://github.com/python/cpython/commit/8ea6353.patch)")

def main():
    """メイン診断プロセス"""
    print("🔍 RVC GUI tkinter診断開始\n")
    
    check_python_environment()
    tkinter_available = test_tkinter_import()
    check_display_environment()
    working_pythons = find_working_python()
    suggest_solutions(working_pythons)
    
    print(f"\n📊 診断完了")
    print(f"tkinter利用可能: {'Yes' if tkinter_available else 'No'}")
    print(f"動作するPython数: {len(working_pythons)}")

if __name__ == "__main__":
    main()