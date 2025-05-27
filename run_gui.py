#!/usr/bin/env python3
"""
RVC GUI起動スクリプト - エラー修正版
"""
import os
import sys

# Pythonの警告を抑制（NSOpenPanelの警告を非表示にする）
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# macOSのNSOpenPanel警告を抑制
if sys.platform == "darwin":
    os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

# GUIを起動
if __name__ == "__main__":
    # TkinterをインポートしてGUIを起動
    import tkinter as tk
    from gui_dark_mode import DarkModeGUI
    
    root = tk.Tk()
    app = DarkModeGUI(root)
    root.mainloop()
