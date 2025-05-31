"""macOS specific fixes for Tkinter dialogs"""
import sys
import tkinter as tk
from tkinter import filedialog


def safe_file_dialog(title="Select File", filetypes=None, initialdir=None, mode='open'):
    """
    macOSでのNSOpenPanel警告を回避するためのファイルダイアログラッパー
    
    Args:
        title: ダイアログのタイトル
        filetypes: ファイルタイプのリスト (例: [("Audio Files", "*.wav *.mp3"), ("All Files", "*.*")])
        initialdir: 初期ディレクトリ
        mode: 'open' (ファイルを開く), 'save' (保存), 'directory' (ディレクトリ選択)
    
    Returns:
        選択されたファイルパス（キャンセルされた場合は空文字列）
    """
    if sys.platform == "darwin":
        # macOS向けの修正
        root = tk.Tk()
        root.withdraw()
        root.update()
        
        try:
            if mode == 'open':
                result = filedialog.askopenfilename(
                    title=title,
                    filetypes=filetypes or [],
                    initialdir=initialdir,
                    parent=root
                )
            elif mode == 'save':
                result = filedialog.asksaveasfilename(
                    title=title,
                    filetypes=filetypes or [],
                    initialdir=initialdir,
                    parent=root
                )
            elif mode == 'directory':
                result = filedialog.askdirectory(
                    title=title,
                    initialdir=initialdir,
                    parent=root
                )
            else:
                raise ValueError(f"Unknown mode: {mode}")
                
        finally:            root.destroy()
            
        return result
    else:
        # 他のプラットフォームでは通常のファイルダイアログを使用
        if mode == 'open':
            return filedialog.askopenfilename(
                title=title,
                filetypes=filetypes or [],
                initialdir=initialdir
            )
        elif mode == 'save':
            return filedialog.asksaveasfilename(
                title=title,
                filetypes=filetypes or [],
                initialdir=initialdir
            )
        elif mode == 'directory':
            return filedialog.askdirectory(
                title=title,
                initialdir=initialdir
            )
        else:
            raise ValueError(f"Unknown mode: {mode}")
