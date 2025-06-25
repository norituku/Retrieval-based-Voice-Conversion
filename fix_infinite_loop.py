#\!/usr/bin/env python3
"""
無限ループ起動問題を修正するスクリプト
"""
import os
import sys
import subprocess
from pathlib import Path

def fix_gui_dark_mode():
    """gui_dark_mode.pyに無限ループ防止コードを追加"""
    gui_file = Path("gui_dark_mode.py")
    
    # ファイルを読み込む
    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # multiprocessing.freeze_support()が含まれているか確認
    if "multiprocessing.freeze_support()" not in content:
        print("🔧 無限ループ防止コードを追加中...")
        
        # import文の後に追加するコード
        freeze_support_code = """
# PyInstaller無限ループ防止
import multiprocessing
if sys.platform == 'darwin':
    multiprocessing.set_start_method('spawn', force=True)
"""
        
        # main関数の最初に追加するコード
        main_guard_code = """def main():
    # PyInstaller環境での無限ループ防止
    if hasattr(sys, 'frozen'):
        multiprocessing.freeze_support()
        
        # 既に起動しているかチェック
        import psutil
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'VoiceConverter' and proc.info['pid'] \!= current_pid:
                print("既に起動しています")
                sys.exit(0)
"""
        
        # import部分の後に追加
        import_end = content.find('\nclass DarkModeGUI:')
        if import_end > 0:
            content = content[:import_end] + freeze_support_code + content[import_end:]
        
        # main関数を修正
        if "def main():" in content:
            content = content.replace("def main():", main_guard_code)
        
        # if __name__ == "__main__":部分を修正
        content = content.replace(
            'if __name__ == "__main__":\n    main()',
            '''if __name__ == "__main__":
    if sys.platform == 'darwin' and hasattr(sys, 'frozen'):
        # PyInstallerで凍結されたアプリの場合
        multiprocessing.freeze_support()
    main()'''
        )
        
        # ファイルを書き戻す
        with open(gui_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 無限ループ防止コード追加完了")
        return True
    else:
        print("✅ 既に無限ループ防止コードが含まれています")
        return False

def fix_rvc_minimal_spec():
    """specファイルに無限ループ防止設定を追加"""
    spec_file = Path("rvc_minimal.spec")
    
    with open(spec_file, 'r') as f:
        content = f.read()
    
    if "multiprocessing_fork=False" not in content:
        print("🔧 specファイルを修正中...")
        
        # EXE部分を修正
        content = content.replace(
            "bootloader_ignore_signals=False,",
            "bootloader_ignore_signals=False,\n    multiprocessing_fork=False,  # 無限ループ防止"
        )
        
        with open(spec_file, 'w') as f:
            f.write(content)
        
        print("✅ specファイル修正完了")
        return True
    
    return False

if __name__ == "__main__":
    print("🛠️ PyInstaller無限ループ問題修正スクリプト")
    print()
    
    # psutilが必要
    try:
        import psutil
    except ImportError:
        print("📦 psutilをインストール中...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)
    
    # 修正を適用
    gui_fixed = fix_gui_dark_mode()
    spec_fixed = fix_rvc_minimal_spec()
    
    if gui_fixed or spec_fixed:
        print("\n✅ 修正完了！")
        print("次のステップ:")
        print("1. 既存のビルドを削除: rm -rf dist build*")
        print("2. 再ビルド: pyinstaller --clean --noconfirm rvc_minimal.spec")
        print("3. コード署名修復: ./fix_codesign.sh")
    else:
        print("\n✅ 既に修正済みです")
