"""
ファイル選択コンポーネント
入力・出力ファイルの選択UI
"""
import tkinter as tk
from tkinter import filedialog
import os
try:
    from ..design_system import DesignTokens
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from design_system import DesignTokens


class FileSelector(tk.Frame):
    """ファイル選択コンポーネント"""
    
    def __init__(self, parent, title="ファイル", file_type="input", on_select=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.design_tokens = DesignTokens()
        self.colors = self.design_tokens.colors
        self.file_type = file_type
        self.on_select = on_select
        self.file_path = ""
        
        self.configure(bg=self.colors['surface_card'])
        self.create_widgets(title)
        
    def create_widgets(self, title):
        """ウィジェットを作成"""
        # タイトルラベル
        title_label = tk.Label(
            self, 
            text=title,
            font=('SF Pro Display', 11, 'bold'),
            bg=self.colors['surface_card'],
            fg=self.colors['text_secondary']
        )
        title_label.pack(anchor='w', pady=(0, 2))
        
        # ファイル選択エリア
        file_area = tk.Frame(self, bg=self.colors['surface_card'])
        file_area.pack(fill=tk.X)
        
        # 選択ボタン
        if self.file_type == "input":
            button_text = "音声ファイルを選択"
            button_command = self.select_input_file
        elif self.file_type == "output":
            button_text = "保存先を選択"
            button_command = self.select_output_directory
        else:
            button_text = "選択"
            button_command = self.select_file
            
        self.select_button = self.create_button(
            file_area, 
            button_text, 
            button_command,
            style='Primary' if self.file_type == "input" else 'Secondary'
        )
        self.select_button.pack(side=tk.LEFT)
        
        # ファイル情報フレーム
        self.file_info_frame = tk.Frame(file_area, bg=self.colors['surface_card'])
        self.file_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, 
                                  padx=(self.design_tokens.spacing['md'], 0))
        
        # ファイル名プレビュー
        if self.file_type == "output":
            self.preview_label = tk.Label(
                self,
                text="",
                font=('SF Pro Mono', 9),
                bg=self.colors['surface_card'],
                fg=self.colors['text_tertiary']
            )
            self.preview_label.pack(anchor='w', pady=(2, 0))
            
    def create_button(self, parent, text, command, style='Primary'):
        """カスタムボタンを作成"""
        btn_frame = tk.Frame(parent, bg=parent['bg'])
        
        if style == 'Primary':
            bg_color = self.colors['accent_primary']
            fg_color = 'white'
            hover_color = '#4A8FEF'
            active_color = '#3A7FDF'
            font_style = ('SF Pro Display', 12, 'bold')
        else:
            bg_color = self.colors['background_tertiary']
            fg_color = self.colors['text_primary']
            hover_color = self.colors['background_elevated']
            active_color = self.colors['background_secondary']
            font_style = ('SF Pro Display', 11, 'normal')
            
        btn = tk.Label(
            btn_frame, 
            text=text,
            font=font_style,
            bg=bg_color,
            fg=fg_color,
            cursor='hand2',
            padx=self.design_tokens.spacing['md'],
            pady=self.design_tokens.spacing['xs']
        )
        btn.pack(fill=tk.BOTH, expand=True)
        
        # ホバーエフェクト
        def on_enter(e):
            btn.config(bg=hover_color)
            
        def on_leave(e):
            btn.config(bg=bg_color)
            
        def on_click(e):
            btn.config(bg=active_color)
            btn.after(100, lambda: btn.config(bg=bg_color))
            command()
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', on_click)
        
        return btn_frame
        
    def select_input_file(self):
        """入力ファイルを選択"""
        filename = filedialog.askopenfilename(
            title="音声ファイルを選択",
            filetypes=[
                ("音声ファイル", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
                ("すべてのファイル", "*.*")
            ]
        )
        
        if filename:
            self.file_path = filename
            self.update_file_info(filename)
            if self.on_select:
                self.on_select(filename)
                
    def select_output_directory(self):
        """出力ディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="保存先ディレクトリを選択",
            initialdir=self.file_path if self.file_path else os.path.expanduser("~")
        )
        
        if directory:
            self.file_path = directory
            self.update_directory_info(directory)
            if self.on_select:
                self.on_select(directory)
                
    def select_file(self):
        """汎用ファイル選択"""
        filename = filedialog.askopenfilename(title="ファイルを選択")
        if filename:
            self.file_path = filename
            self.update_file_info(filename)
            if self.on_select:
                self.on_select(filename)
                
    def update_file_info(self, filepath):
        """ファイル情報を更新"""
        # 既存の情報をクリア
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
            
        # ファイル名
        filename = os.path.basename(filepath)
        name_label = tk.Label(
            self.file_info_frame, 
            text=self.truncate_path(filename, 30),
            font=('SF Pro Display', 11, 'bold'),
            bg=self.colors['surface_card'],
            fg=self.colors['text_primary']
        )
        name_label.pack(anchor='w')
        
        # ファイルサイズ
        try:
            size = os.path.getsize(filepath)
            size_str = self.format_file_size(size)
            size_label = tk.Label(
                self.file_info_frame, 
                text=f"サイズ: {size_str}",
                font=('SF Pro Display', 9),
                bg=self.colors['surface_card'],
                fg=self.colors['text_secondary']
            )
            size_label.pack(anchor='w')
        except:
            pass
            
    def update_directory_info(self, directory):
        """ディレクトリ情報を更新"""
        # 既存の情報をクリア
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
            
        # パス表示
        path_label = tk.Label(
            self.file_info_frame,
            text=self.truncate_path(directory, 40),
            font=('SF Pro Mono', 10),
            bg=self.colors['surface_card'],
            fg=self.colors['text_primary']
        )
        path_label.pack(anchor='w')
        
    def update_preview(self, text):
        """プレビューテキストを更新"""
        if hasattr(self, 'preview_label'):
            self.preview_label.config(text=text)
            
    def get_path(self):
        """選択されたパスを取得"""
        return self.file_path
        
    def set_path(self, path):
        """パスを設定"""
        self.file_path = path
        if os.path.isdir(path):
            self.update_directory_info(path)
        else:
            self.update_file_info(path)
            
    def truncate_path(self, path, max_length=40):
        """長いパスを省略"""
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length-3):]
        
    def format_file_size(self, size):
        """ファイルサイズをフォーマット"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"