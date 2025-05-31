"""
プログレスバーコンポーネント
7ステージの進捗を表示する統合プログレスバー
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
try:
    from ..design_system import DesignTokens
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from design_system import DesignTokens


class ProgressBar(tk.Frame):
    """7ステージプログレスバーコンポーネント"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.design_tokens = DesignTokens()
        self.colors = self.design_tokens.colors
        
        # ステージ定義
        self.stages = [
            "初期化中...",
            "音声ファイルを読み込んでいます...",
            "音声データの前処理を実行中...",
            "音声の特徴を抽出中...",
            "AIモデルで音声を変換中...",
            "音質の最適化を実行中...",
            "変換結果を保存しています..."
        ]
        
        self.current_stage = 0
        self.configure(bg=self.colors['surface_card'])
        self.create_widgets()
        self.hide()
        
    def create_widgets(self):
        """ウィジェットを作成"""
        # プログレスバーとパーセンテージ
        progress_container = tk.Frame(self, bg=self.colors['surface_card'])
        progress_container.pack(fill=tk.X)
        
        # プログレスバー
        self.progress = ttk.Progressbar(
            progress_container, 
            mode='determinate',
            maximum=100,
            style='Dark.Horizontal.TProgressbar'
        )
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # パーセンテージラベル
        self.percentage_label = tk.Label(
            progress_container, 
            text="0%",
            font=('SF Pro Display', 11, 'bold'),
            bg=self.colors['surface_card'],
            fg=self.colors['accent_primary']
        )
        self.percentage_label.pack(side=tk.RIGHT, padx=(self.design_tokens.spacing['sm'], 0))
        
        # ステータステキスト
        self.status_label = tk.Label(
            self, 
            text="",
            font=('SF Pro Display', 10),
            bg=self.colors['surface_card'],
            fg=self.colors['text_secondary'],
            wraplength=400
        )
        self.status_label.pack(anchor='w', pady=(self.design_tokens.spacing['xs'], 0))
        
        # ステージ情報
        self.stage_label = tk.Label(
            self, 
            text="",
            font=('SF Pro Display', 11, 'bold'),
            bg=self.colors['surface_card'],
            fg=self.colors['text_primary']
        )
        self.stage_label.pack(anchor='w', pady=(self.design_tokens.spacing['xs'], 0))
        
    def update_progress(self, stage_index, progress, message):
        """プログレスバーを更新"""
        if not self.winfo_viewable():
            self.show()
            
        # 全体の進捗を計算（7ステージ）
        total_stages = len(self.stages)
        stage_progress = (stage_index / total_stages) * 100
        current_stage_progress = (progress / 100) * (100 / total_stages)
        total_progress = stage_progress + current_stage_progress
        
        # UIを更新
        self.progress['value'] = total_progress
        self.percentage_label.config(text=f"{int(total_progress)}%")
        
        # ステージ情報を更新
        if 0 <= stage_index < len(self.stages):
            self.stage_label.config(text=self.stages[stage_index])
            self.status_label.config(text=message)
            
        # ログメッセージを生成
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # UIを強制更新
        self.update_idletasks()
        
        return log_message
        
    def show(self):
        """プログレスバーを表示"""
        self.pack(fill=tk.X, pady=(0, self.design_tokens.spacing['sm']))
        
    def hide(self):
        """プログレスバーを非表示"""
        self.pack_forget()
        
    def reset(self):
        """プログレスバーをリセット"""
        self.progress['value'] = 0
        self.percentage_label.config(text="0%")
        self.status_label.config(text="")
        self.stage_label.config(text="")
        self.hide()