#!/usr/bin/env python3
"""
RVC GUI Wrapper - tkinter起動ラッパー
既存のgui_dark_mode.pyを呼び出すラッパー
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🎵 RVC Voice Converter - GUI Wrapper")
    
    # スクリプトの場所を取得
    if getattr(sys, 'frozen', False):
        # PyInstallerでパッケージされた場合
        app_dir = Path(sys._MEIPASS)
        project_dir = app_dir
    else:
        # 通常のPythonスクリプトとして実行された場合
        project_dir = Path(__file__).parent.absolute()
    
    print(f"📁 プロジェクトディレクトリ: {project_dir}")
    
    # tkinter環境の確認
    try:
        import tkinter
        print("✅ tkinter利用可能")
    except ImportError:
        print("❌ tkinterが利用できません")
        
        # venv_tkinter_fixの使用を試行
        venv_python = project_dir.parent / "venv_tkinter_fix" / "bin" / "python"
        if venv_python.exists():
            print(f"🔄 tkinter対応環境に切り替え: {venv_python}")
            gui_script = project_dir / "gui_dark_mode.py"
            if gui_script.exists():
                os.execv(str(venv_python), [str(venv_python), str(gui_script)])
            else:
                print(f"❌ GUIスクリプトが見つかりません: {gui_script}")
                return 1
        else:
            print("❌ tkinter対応環境が見つかりません")
            return 1
    
    # gui_dark_mode.pyを直接インポート・実行
    try:
        gui_script = project_dir / "gui_dark_mode.py"
        if gui_script.exists():
            # gui_dark_mode.pyを直接実行
            import sys
            old_argv = sys.argv
            sys.argv = [str(gui_script)]
            
            # パスにプロジェクトディレクトリを追加
            if str(project_dir) not in sys.path:
                sys.path.insert(0, str(project_dir))
            
            # gui_dark_mode.pyの内容を実行
            with open(gui_script, 'r', encoding='utf-8') as f:
                code = f.read()
            
            exec(code, {'__name__': '__main__', '__file__': str(gui_script)})
            
        else:
            print(f"❌ GUIスクリプトが見つかりません: {gui_script}")
            return 1
            
    except Exception as e:
        print(f"❌ GUI起動エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())