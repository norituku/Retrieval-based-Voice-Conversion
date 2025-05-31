"""
既存のDark Mode GUIにプログレスバーを統合するパッチ
"""

import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.progress_tracker import ProgressTracker, ProcessingStage, SubTaskTracker
from typing import Optional
import threading
import time


class ProgressBarIntegration:
    """Dark Mode GUIにプログレスバーを統合するためのクラス"""
    
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
        self.tracker = ProgressTracker()
        self.progress_window = None
        self.progress_bar = None
        self.progress_label = None
        self.percentage_label = None
        
        # トラッカーのコールバックを設定
        self.tracker.add_callback(self._update_progress)
        
    def create_progress_window(self):
        """プログレスウィンドウを作成"""
        import tkinter as tk
        from tkinter import ttk
        
        # モーダルウィンドウを作成
        self.progress_window = tk.Toplevel(self.parent_gui.root)
        self.progress_window.title("変換中...")
        self.progress_window.geometry("450x180")
        self.progress_window.resizable(False, False)
        
        # ダークモードスタイルを適用
        self.progress_window.configure(bg=self.parent_gui.design_tokens['colors']['background_primary'])
        
        # ウィンドウを中央に配置
        self.progress_window.update_idletasks()
        x = (self.progress_window.winfo_screenwidth() // 2) - 225
        y = (self.progress_window.winfo_screenheight() // 2) - 90
        self.progress_window.geometry(f"450x180+{x}+{y}")
        
        # モーダルにする
        self.progress_window.transient(self.parent_gui.root)
        self.progress_window.grab_set()
        
        # メインフレーム
        main_frame = tk.Frame(
            self.progress_window,
            bg=self.parent_gui.design_tokens['colors']['background_primary']
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # タイトル
        title_label = tk.Label(
            main_frame,
            text="🎵 Voice Conversion",
            font=("SF Pro Display", 16, "bold"),
            bg=self.parent_gui.design_tokens['colors']['background_primary'],
            fg=self.parent_gui.design_tokens['colors']['accent_primary']
        )
        title_label.pack(pady=(0, 15))
        
        # メッセージラベル
        self.progress_label = tk.Label(
            main_frame,
            text="準備中...",
            font=("SF Pro Text", 11),
            bg=self.parent_gui.design_tokens['colors']['background_primary'],
            fg=self.parent_gui.design_tokens['colors']['text_secondary']
        )
        self.progress_label.pack(pady=(0, 10))
        
        # カスタムプログレスバーフレーム
        progress_frame = tk.Frame(
            main_frame,
            height=30,
            bg=self.parent_gui.design_tokens['colors']['background_secondary']
        )
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        progress_frame.pack_propagate(False)
        
        # プログレスバーの塗りつぶし部分
        self.progress_bar = tk.Frame(
            progress_frame,
            bg=self.parent_gui.design_tokens['colors']['accent_primary']
        )
        self.progress_bar.place(x=0, y=0, relheight=1, width=0)
        
        # パーセンテージラベル
        self.percentage_label = tk.Label(
            main_frame,
            text="0%",
            font=("SF Pro Display", 20, "bold"),
            bg=self.parent_gui.design_tokens['colors']['background_primary'],
            fg=self.parent_gui.design_tokens['colors']['accent_primary']
        )
        self.percentage_label.pack()
        
        # ウィンドウが閉じられないようにする
        self.progress_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
    def _update_progress(self, progress: float, message: str):
        """プログレスバーを更新"""
        if self.progress_window and self.progress_window.winfo_exists():
            percentage = int(progress * 100)
            
            # UIスレッドで更新
            self.progress_window.after(0, self._update_ui, percentage, progress, message)
            
    def _update_ui(self, percentage: int, progress: float, message: str):
        """UIコンポーネントを更新"""
        if not self.progress_window or not self.progress_window.winfo_exists():
            return
            
        # プログレスバーの幅を更新
        if self.progress_bar.winfo_exists():
            bar_width = int(390 * progress)  # 450 - 60 (padding)
            self.progress_bar.place(width=bar_width)
            
            # 完了時は色を変更
            if percentage >= 100:
                self.progress_bar.configure(
                    bg=self.parent_gui.design_tokens['colors']['success']
                )
                self.percentage_label.configure(
                    fg=self.parent_gui.design_tokens['colors']['success']
                )
        
        # ラベルを更新
        if self.progress_label and self.progress_label.winfo_exists():
            self.progress_label.configure(text=message)
            
        if self.percentage_label and self.percentage_label.winfo_exists():
            self.percentage_label.configure(text=f"{percentage}%")
            
        self.progress_window.update_idletasks()
        
    def close(self):
        """プログレスウィンドウを閉じる"""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.grab_release()
            self.progress_window.destroy()
            self.progress_window = None
            
    def get_tracker(self) -> ProgressTracker:
        """ProgressTrackerインスタンスを取得"""
        return self.tracker