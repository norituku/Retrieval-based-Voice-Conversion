"""
ダークモード対応のTkinterプログレスバーUI実装
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Optional, Dict
from ..utils.progress_tracker import ProgressTracker


class DarkModeProgressBar:
    """
    ダークモード対応のプログレスバーウィンドウ
    """
    
    # ダークモードのカラーパレット
    DARK_COLORS = {
        'bg': '#1e1e1e',
        'fg': '#ffffff',
        'progress_bg': '#3a3a3a',
        'progress_fill': '#00d4ff',
        'progress_fill_complete': '#4caf50',
        'label_fg': '#e0e0e0',
        'percentage_fg': '#00d4ff',
        'border': '#4a4a4a'
    }
    
    # ライトモードのカラーパレット
    LIGHT_COLORS = {
        'bg': '#ffffff',
        'fg': '#000000',
        'progress_bg': '#e0e0e0',
        'progress_fill': '#2196f3',
        'progress_fill_complete': '#4caf50',
        'label_fg': '#666666',
        'percentage_fg': '#2196f3',
        'border': '#cccccc'
    }
    
    def __init__(self, title: str = "処理中", width: int = 450, height: int = 180, dark_mode: bool = True):
        self.dark_mode = dark_mode
        self.colors = self.DARK_COLORS if dark_mode else self.LIGHT_COLORS
        self.width = width
        self.height = height
        
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        
        # ダークモード背景色設定
        self.root.configure(bg=self.colors['bg'])
        
        # ウィンドウを中央に配置
        self.center_window()
        
        self._setup_ui()
        self._setup_styles()
        
    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.width // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
    def _setup_ui(self):
        """UIコンポーネントの設定"""
        # メインフレーム
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトルラベル
        self.title_label = tk.Label(
            main_frame,
            text="Voice Conversion",
            font=("Arial", 14, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        self.title_label.pack(pady=(0, 15))
        
        # メッセージラベル
        self.message_label = tk.Label(
            main_frame,
            text="準備中...",
            font=("Arial", 10),
            bg=self.colors['bg'],
            fg=self.colors['label_fg']
        )
        self.message_label.pack(pady=(0, 10))
        
        # カスタムプログレスバーフレーム
        self.progress_frame = tk.Frame(
            main_frame,
            height=30,
            bg=self.colors['progress_bg'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.progress_frame.pack_propagate(False)
        
        # プログレスバーの塗りつぶし部分
        self.progress_fill = tk.Frame(
            self.progress_frame,
            bg=self.colors['progress_fill']
        )
        self.progress_fill.place(x=0, y=0, relheight=1, width=0)
        
        # パーセンテージラベル
        self.percentage_label = tk.Label(
            main_frame,
            text="0%",
            font=("Arial", 16, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['percentage_fg']
        )
        self.percentage_label.pack(pady=(0, 5))
        
        # 詳細情報フレーム
        details_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        details_frame.pack(fill=tk.X)
        
        # 経過時間ラベル
        self.time_label = tk.Label(
            details_frame,
            text="経過時間: 0:00",
            font=("Arial", 9),
            bg=self.colors['bg'],
            fg=self.colors['label_fg']
        )
        self.time_label.pack(side=tk.LEFT)
        
        # 残り時間ラベル
        self.eta_label = tk.Label(
            details_frame,
            text="残り時間: 計算中...",
            font=("Arial", 9),
            bg=self.colors['bg'],
            fg=self.colors['label_fg']
        )
        self.eta_label.pack(side=tk.RIGHT)
        
    def _setup_styles(self):
        """スタイルの設定"""
        style = ttk.Style()
        
        if self.dark_mode:
            style.theme_use('clam')
            
            # ダークモード用のスタイル設定
            style.configure(
                "dark.Horizontal.TProgressbar",
                background=self.colors['progress_fill'],
                troughcolor=self.colors['progress_bg'],
                bordercolor=self.colors['border'],
                lightcolor=self.colors['progress_fill'],
                darkcolor=self.colors['progress_fill'],
                borderwidth=1,
                relief="flat"
            )
            
    def update_progress(self, progress: float, message: str):
        """
        プログレスバーを更新
        progress: 0.0～1.0の値
        message: 表示するメッセージ
        """
        percentage = int(progress * 100)
        
        # UIスレッドで更新
        self.root.after(0, self._update_ui, percentage, progress, message)
        
    def _update_ui(self, percentage: int, progress: float, message: str):
        """UIコンポーネントを更新（UIスレッドで実行）"""
        # プログレスバーの幅を更新
        bar_width = int(self.progress_frame.winfo_width() * progress)
        self.progress_fill.place(width=bar_width)
        
        # 完了時は色を変更
        if percentage >= 100:
            self.progress_fill.configure(bg=self.colors['progress_fill_complete'])
            self.percentage_label.configure(fg=self.colors['progress_fill_complete'])
        
        # ラベルを更新
        self.percentage_label.configure(text=f"{percentage}%")
        self.message_label.configure(text=message)
        
        # 時間の更新（実装は省略）
        # self.update_time_labels()
        
        self.root.update_idletasks()
        
    def toggle_dark_mode(self):
        """ダークモードの切り替え"""
        self.dark_mode = not self.dark_mode
        self.colors = self.DARK_COLORS if self.dark_mode else self.LIGHT_COLORS
        
        # 背景色を更新
        self.root.configure(bg=self.colors['bg'])
        
        # 各コンポーネントの色を更新
        for widget in [self.title_label, self.message_label, self.percentage_label, 
                      self.time_label, self.eta_label]:
            widget.configure(bg=self.colors['bg'])
            
        self.title_label.configure(fg=self.colors['fg'])
        self.message_label.configure(fg=self.colors['label_fg'])
        self.percentage_label.configure(fg=self.colors['percentage_fg'])
        self.time_label.configure(fg=self.colors['label_fg'])
        self.eta_label.configure(fg=self.colors['label_fg'])
        
        self.progress_frame.configure(bg=self.colors['progress_bg'])
        self.progress_fill.configure(bg=self.colors['progress_fill'])
        
    def close(self):
        """ウィンドウを閉じる"""
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """メインループを開始"""
        self.root.mainloop()


class DarkModeProgressManager:
    """
    ダークモードプログレスバーとトラッカーを統合管理するクラス
    """
    
    def __init__(self, title: str = "Voice Conversion 処理中", dark_mode: bool = True):
        self.tracker = ProgressTracker()
        self.window: Optional[DarkModeProgressBar] = None
        self.title = title
        self.dark_mode = dark_mode
        self._ui_thread: Optional[threading.Thread] = None
        self.start_time = None
        
    def start(self):
        """プログレスバーウィンドウを開始"""
        import time
        self.start_time = time.time()
        
        def run_window():
            self.window = DarkModeProgressBar(self.title, dark_mode=self.dark_mode)
            # トラッカーのコールバックを設定
            self.tracker.add_callback(self.window.update_progress)
            self.window.run()
            
        self._ui_thread = threading.Thread(target=run_window, daemon=True)
        self._ui_thread.start()
        
        # ウィンドウが初期化されるまで待機
        time.sleep(0.5)
        
    def stop(self):
        """プログレスバーウィンドウを停止"""
        if self.window:
            self.window.root.after(0, self.window.close)
            
    def get_tracker(self) -> ProgressTracker:
        """ProgressTrackerインスタンスを取得"""
        return self.tracker
        
    def toggle_dark_mode(self):
        """ダークモードの切り替え"""
        if self.window:
            self.window.root.after(0, self.window.toggle_dark_mode)