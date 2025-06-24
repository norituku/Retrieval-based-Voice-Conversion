#!/usr/bin/env python3
"""
RVC Voice Converter - スタンドアロンアプリ起動ランチャー
"""

import os
import sys
from pathlib import Path

def main():
    try:
        # アプリケーションのリソースディレクトリを取得
        if getattr(sys, 'frozen', False):
            # PyInstallerでパッケージされた場合
            app_dir = Path(sys._MEIPASS)
        else:
            # 通常のPythonスクリプトの場合
            app_dir = Path(__file__).parent.absolute()
        
        # 環境変数設定
        os.environ['PYTHONPATH'] = str(app_dir)
        
        # gui_dark_mode.pyを直接実行
        gui_script = app_dir / "gui_dark_mode.py"
        if gui_script.exists():
            with open(gui_script, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 実行コンテキストを設定
            exec_globals = {
                '__name__': '__main__',
                '__file__': str(gui_script),
                '__package__': None
            }
            
            # パスを追加
            if str(app_dir) not in sys.path:
                sys.path.insert(0, str(app_dir))
            
            # GUIスクリプト実行
            exec(code, exec_globals)
        else:
            print(f"❌ GUIスクリプトが見つかりません: {gui_script}")
            return 1
            
    except Exception as e:
        print(f"❌ アプリケーション起動エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
