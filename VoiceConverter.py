#!/usr/bin/env python3
"""
Voice Converter - Desktop Application
警告を最小限に抑えた起動スクリプト
"""
import os
import sys
import subprocess

def set_macos_environment():
    """macOS固有の環境変数を設定"""
    if sys.platform == "darwin":
        env_vars = {
            'OBJC_DISABLE_INITIALIZE_FORK_SAFETY': 'YES',
            'PYOBJC_DISABLE_GIL_VALIDATION': '1',
            'TK_SILENCE_DEPRECATION': '1',
            'PYTHONWARNINGS': 'ignore',
            'NO_AT_BRIDGE': '1'  # アクセシビリティ警告を抑制
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value

def main():
    """アプリケーションのメインエントリーポイント"""
    # macOS環境設定
    set_macos_environment()
    
    # カレントディレクトリをスクリプトのディレクトリに設定
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        # サイレントモードでGUIを起動
        if sys.platform == "darwin":
            # macOSの場合、警告をフィルタリング
            cmd = [sys.executable, "gui_dark_mode.py"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 標準出力のみ表示（エラーは抑制）
            for line in process.stdout:
                if line.strip():
                    print(line.strip())
                    
        else:
            # 他のプラットフォームでは通常起動
            from gui_dark_mode import DarkModeGUI
            import tkinter as tk
            
            root = tk.Tk()
            app = DarkModeGUI(root)
            root.mainloop()
            
    except KeyboardInterrupt:
        print("\nアプリケーションを終了します。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
