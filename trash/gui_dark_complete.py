#!/usr/bin/env python3
"""
Voice Converter - Dark Mode GUI (完全版)
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import subprocess
import threading
from pathlib import Path

class DarkModeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter - Dark Mode")
        
        # ダークカラーパレット
        self.colors = {
            'bg_primary': '#1e1e1e',
            'bg_secondary': '#2d2d2d',
            'bg_tertiary': '#3c3c3c',
            'bg_elevated': '#4a4a4a',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'text_tertiary': '#808080',
            'accent': '#0d7377',
            'accent_hover': '#14a085',
            'accent_secondary': '#5DADE2',
            'border': '#4a4a4a',
            'success': '#27ae60',
            'error': '#e74c3c',
            'warning': '#f39c12'
        }
        
        # 変数の初期化
        self.init_variables()
        
        # ウィンドウ設定
        self.setup_window()
        
        # スタイル設定
        self.setup_styles()
        
        # UI構築
        self.create_ui()
        
        # モデル読み込み
        self.load_models()
        
    def init_variables(self):
        """変数の初期化"""
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.output_filename_var = tk.StringVar()
        self.pitch_var = tk.IntVar(value=0)
        self.f0_method_var = tk.StringVar(value="rmvpe")
        self.index_rate_var = tk.DoubleVar(value=1.0)
        self.filter_radius_var = tk.IntVar(value=3)
        self.rms_mix_rate_var = tk.DoubleVar(value=0.25)
        self.protect_var = tk.DoubleVar(value=0.33)
        self.selected_model = tk.StringVar()
        self.model_info = {}
        self.is_converting = False
        
        # ディレクトリ設定
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = os.path.join(self.base_dir, "model_dir")
        self.output_file_path = ""
        
    def setup_window(self):
        """ウィンドウの設定"""
        self.root.configure(bg=self.colors['bg_primary'])
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        
        # アイコン設定（オプション）
        # self.root.iconbitmap('icon.ico')
        
    def setup_styles(self):
        """TTKスタイルの設定"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 全体的なスタイル
        style.configure('.',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       bordercolor=self.colors['border'],
                       focuscolor='none')
        
        # フレーム
        style.configure('Dark.TFrame',
                       background=self.colors['bg_secondary'],
                       relief='flat')
        
        style.configure('Card.TFrame',
                       background=self.colors['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        # ラベルフレーム
        style.configure('Dark.TLabelframe',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       bordercolor=self.colors['border'])
        
        style.configure('Dark.TLabelframe.Label',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=('Arial', 11, 'bold'))
        
        # ボタン
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))
        
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_hover'])])
        
        style.configure('Secondary.TButton',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid')
        
        # エントリー
        style.configure('Dark.TEntry',
                       fieldbackground=self.colors['bg_tertiary'],
                       borderwidth=1,
                       insertcolor=self.colors['text_primary'])
        
        # プログレスバー
        style.configure('Dark.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_tertiary'],
                       bordercolor=self.colors['bg_tertiary'],
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])
        
    def create_ui(self):
        """UIの構築"""
        # ヘッダー
        self.create_header()
        
        # メインコンテナ
        main_container = ttk.Frame(self.root, style='Dark.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 左側パネル（モデル選択）
        left_panel = ttk.Frame(main_container, style='Dark.TFrame', width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.create_model_panel(left_panel)
        
        # 右側パネル（メインコンテンツ）
        right_panel = ttk.Frame(main_container, style='Dark.TFrame')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_main_content(right_panel)
        
    def create_header(self):
        """ヘッダーバー"""
        header = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=60)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        # タイトル
        title_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(title_frame,
                text="Voice Converter",
                font=('Arial', 20, 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(side=tk.LEFT, padx=10, pady=15)
        
        tk.Label(title_frame,
                text="Powered by RVC",
                font=('Arial', 10),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_secondary']).pack(side=tk.LEFT, pady=18)
        
    def create_model_panel(self, parent):
        """モデル選択パネル"""
        # パネルヘッダー
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame,
                text="Voice Models",
                font=('Arial', 14, 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(pady=10)
        
        # モデルディレクトリ表示
        dir_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(dir_frame,
                text=f"📁 {self.truncate_path(self.model_dir, 30)}",
                font=('Arial', 9),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_tertiary']).pack(padx=5)
        
        # モデルリスト
        list_frame = ttk.Frame(parent, style='Card.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # リストボックス
        self.model_listbox = tk.Listbox(
            list_frame,
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            selectbackground=self.colors['accent'],
            selectforeground='white',
            selectmode=tk.SINGLE,
            font=('Arial', 11),
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.model_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        scrollbar.config(command=self.model_listbox.yview)
        
        # モデル選択イベント
        self.model_listbox.bind('<<ListboxSelect>>', self.on_model_select)
        
        # リフレッシュボタン
        refresh_btn = ttk.Button(parent,
                                text="🔄 Refresh",
                                command=self.load_models,
                                style='Secondary.TButton')
        refresh_btn.pack(pady=10)
        
    def create_main_content(self, parent):
        """メインコンテンツ"""
        # スクロール可能なフレーム
        canvas = tk.Canvas(parent, bg=self.colors['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ファイル選択セクション
        self.create_file_section(scrollable_frame)
        
        # 基本設定セクション
        self.create_basic_settings_section(scrollable_frame)
        
        # 詳細設定セクション
        self.create_advanced_settings_section(scrollable_frame)
        
        # コントロールセクション
        self.create_control_section(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_file_section(self, parent):
        """ファイル選択セクション"""
        frame = ttk.LabelFrame(parent, text="📁 File Input/Output", style='Dark.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        inner_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        inner_frame.pack(fill=tk.BOTH, padx=15, pady=15)
        
        # Input File
        input_frame = tk.Frame(inner_frame, bg=self.colors['bg_secondary'])
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(input_frame,
                text="Input File:",
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                font=('Arial', 10),
                width=12,
                anchor='w').pack(side=tk.LEFT)
        
        ttk.Entry(input_frame,
                 textvariable=self.input_var,
                 style='Dark.TEntry').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(input_frame,
                  text="Browse",
                  command=self.browse_input,
                  style='Accent.TButton').pack(side=tk.LEFT)
        
        # Output File
        output_frame = tk.Frame(inner_frame, bg=self.colors['bg_secondary'])
        output_frame.pack(fill=tk.X)
        
        tk.Label(output_frame,
                text="Output File:",
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                font=('Arial', 10),
                width=12,
                anchor='w').pack(side=tk.LEFT)
        
        ttk.Entry(output_frame,
                 textvariable=self.output_var,
                 style='Dark.TEntry').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(output_frame,
                  text="Browse",
                  command=self.browse_output,
                  style='Accent.TButton').pack(side=tk.LEFT)
        
    def create_basic_settings_section(self, parent):
        """基本設定セクション"""
        frame = ttk.LabelFrame(parent, text="🎛️ Basic Settings", style='Dark.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        inner_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        inner_frame.pack(fill=tk.BOTH, padx=15, pady=15)
        
        # Pitch
        pitch_frame = tk.Frame(inner_frame, bg=self.colors['bg_secondary'])
        pitch_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(pitch_frame,
                text="Pitch:",
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                font=('Arial', 10),
                width=15,
                anchor='w').pack(side=tk.LEFT)
        
        pitch_scale = tk.Scale(pitch_frame,
                              from_=-12, to=12,
                              orient=tk.HORIZONTAL,
                              variable=self.pitch_var,
                              bg=self.colors['bg_tertiary'],
                              fg=self.colors['text_primary'],
                              highlightthickness=0,
                              troughcolor=self.colors['bg_primary'],
                              activebackground=self.colors['accent'])
        pitch_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.pitch_label = tk.Label(pitch_frame,
                                   text="0",
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['accent'],
                                   font=('Arial', 10, 'bold'),
                                   width=4)
        self.pitch_label.pack(side=tk.LEFT)
        
        self.pitch_var.trace('w', lambda *args: self.pitch_label.config(
            text=f"{self.pitch_var.get():+d}"))
        
        # F0 Method
        f0_frame = tk.Frame(inner_frame, bg=self.colors['bg_secondary'])
        f0_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(f0_frame,
                text="F0 Method:",
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                font=('Arial', 10),
                width=15,
                anchor='w').pack(side=tk.LEFT)
        
        f0_methods = ["rmvpe", "mangio-crepe", "crepe", "harvest", "dio"]
        self.f0_combo = ttk.Combobox(f0_frame,
                                    textvariable=self.f0_method_var,
                                    values=f0_methods,
                                    state='readonly',
                                    width=20)
        self.f0_combo.pack(side=tk.LEFT, padx=5)
        
    def create_advanced_settings_section(self, parent):
        """詳細設定セクション"""
        frame = ttk.LabelFrame(parent, text="⚙️ Advanced Settings", style='Dark.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 展開/折りたたみ機能
        self.advanced_expanded = tk.BooleanVar(value=False)
        
        header_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X)
        
        toggle_btn = tk.Button(header_frame,
                              text="▶ Show Advanced Settings",
                              command=self.toggle_advanced,
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_secondary'],
                              bd=0,
                              font=('Arial', 9),
                              activebackground=self.colors['bg_secondary'])
        toggle_btn.pack(anchor='w', padx=10, pady=5)
        
        self.toggle_btn = toggle_btn
        
        # 詳細設定コンテンツ
        self.advanced_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        
        # Index Rate
        self.create_slider_setting(self.advanced_frame, "Index Rate:", 
                                  self.index_rate_var, 0.0, 1.0, 0.05)
        
        # Filter Radius
        self.create_slider_setting(self.advanced_frame, "Filter Radius:", 
                                  self.filter_radius_var, 0, 7, 1)
        
        # RMS Mix Rate
        self.create_slider_setting(self.advanced_frame, "RMS Mix Rate:", 
                                  self.rms_mix_rate_var, 0.0, 1.0, 0.05)
        
        # Protect
        self.create_slider_setting(self.advanced_frame, "Protect:", 
                                  self.protect_var, 0.0, 0.5, 0.01)
        
    def create_slider_setting(self, parent, label, var, from_, to, resolution):
        """スライダー設定を作成"""
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(frame,
                text=label,
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                font=('Arial', 10),
                width=15,
                anchor='w').pack(side=tk.LEFT)
        
        scale = tk.Scale(frame,
                        from_=from_, to=to,
                        resolution=resolution,
                        orient=tk.HORIZONTAL,
                        variable=var,
                        bg=self.colors['bg_tertiary'],
                        fg=self.colors['text_primary'],
                        highlightthickness=0,
                        troughcolor=self.colors['bg_primary'],
                        activebackground=self.colors['accent'])
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        value_label = tk.Label(frame,
                              text=f"{var.get():.2f}",
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_secondary'],
                              font=('Arial', 9),
                              width=6)
        value_label.pack(side=tk.LEFT)
        
        var.trace('w', lambda *args: value_label.config(text=f"{var.get():.2f}"))
        
    def create_control_section(self, parent):
        """コントロールセクション"""
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        frame.pack(fill=tk.X, padx=10, pady=20)
        
        # プログレスバー
        self.progress = ttk.Progressbar(frame,
                                       style='Dark.Horizontal.TProgressbar',
                                       mode='indeterminate',
                                       length=400)
        self.progress.pack(pady=(0, 15))
        
        # コンバートボタン
        self.convert_btn = tk.Button(frame,
                                    text="🎵 Convert",
                                    command=self.convert,
                                    bg=self.colors['accent'],
                                    fg='white',
                                    font=('Arial', 14, 'bold'),
                                    padx=40,
                                    pady=12,
                                    bd=0,
                                    cursor='hand2',
                                    activebackground=self.colors['accent_hover'],
                                    activeforeground='white')
        self.convert_btn.pack()
        
        # ステータスラベル
        self.status_label = tk.Label(frame,
                                    text="Ready to convert",
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_secondary'],
                                    font=('Arial', 10))
        self.status_label.pack(pady=10)
        
    def toggle_advanced(self):
        """詳細設定の表示/非表示を切り替え"""
        if self.advanced_expanded.get():
            self.advanced_frame.pack_forget()
            self.toggle_btn.config(text="▶ Show Advanced Settings")
            self.advanced_expanded.set(False)
        else:
            self.advanced_frame.pack(fill=tk.X, pady=(0, 10))
            self.toggle_btn.config(text="▼ Hide Advanced Settings")
            self.advanced_expanded.set(True)
            
    def truncate_path(self, path, max_length):
        """パスを短縮表示"""
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length-3):]
        
    def on_model_select(self, event):
        """モデル選択時の処理"""
        selection = self.model_listbox.curselection()
        if selection:
            model_name = self.model_listbox.get(selection[0])
            self.selected_model.set(model_name)
            self.auto_set_output()
            
    def load_models(self):
        """モデルを読み込む"""
        try:
            self.model_listbox.delete(0, tk.END)
            
            if os.path.exists(self.model_dir):
                models = [d for d in os.listdir(self.model_dir) 
                         if os.path.isdir(os.path.join(self.model_dir, d)) 
                         and not d.startswith('.')]
                
                for model in sorted(models):
                    self.model_listbox.insert(tk.END, f" 🎤 {model}")
                    
                if models:
                    self.model_listbox.selection_set(0)
                    self.selected_model.set(models[0])
                    
                self.status_label.config(
                    text=f"Loaded {len(models)} models",
                    fg=self.colors['success'])
            else:
                self.status_label.config(
                    text="Model directory not found",
                    fg=self.colors['warning'])
                    
        except Exception as e:
            self.status_label.config(
                text=f"Error loading models: {str(e)}",
                fg=self.colors['error'])
            
    def browse_input(self):
        """入力ファイルを選択"""
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.m4a *.flac *.aac *.ogg *.aiff *.aif"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.input_var.set(filename)
            self.auto_set_output()
            self.status_label.config(
                text=f"Selected: {os.path.basename(filename)}",
                fg=self.colors['text_secondary'])
    
    def browse_output(self):
        """出力ファイルを選択"""
        filename = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".wav",
            filetypes=[
                ("WAV Files", "*.wav"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.output_var.set(filename)
            self.output_filename_var.set(os.path.basename(filename))
            
    def auto_set_output(self):
        """出力ファイル名を自動設定"""
        input_file = self.input_var.get()
        if input_file and self.selected_model.get():
            base = os.path.splitext(input_file)[0]
            model = self.selected_model.get().replace(" 🎤 ", "")
            output_file = f"{base}_{model}.wav"
            self.output_var.set(output_file)
            self.output_filename_var.set(os.path.basename(output_file))
            
    def convert(self):
        """変換処理"""
        if self.is_converting:
            return
            
        if not self.input_var.get():
            messagebox.showwarning("Warning", "Please select an input file")
            return
            
        if not self.selected_model.get():
            messagebox.showwarning("Warning", "Please select a voice model")
            return
            
        if not self.output_var.get():
            messagebox.showwarning("Warning", "Please specify an output file")
            return
            
        self.is_converting = True
        self.convert_btn.config(state='disabled', text="Converting...")
        self.progress.start(10)
        self.status_label.config(
            text="Processing... Please wait",
            fg=self.colors['accent'])
        
        # 実際の変換処理をスレッドで実行
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
        
    def run_conversion(self):
        """変換処理を実行（デモ）"""
        import time
        
        # ここに実際のRVC変換処理を実装
        # 今はデモとして2秒待機
        time.sleep(2)
        
        # UIを更新
        self.root.after(0, self.conversion_complete)
        
    def conversion_complete(self):
        """変換完了時の処理"""
        self.progress.stop()
        self.is_converting = False
        self.convert_btn.config(state='normal', text="🎵 Convert")
        self.status_label.config(
            text=f"✓ Conversion completed! Output: {os.path.basename(self.output_var.get())}",
            fg=self.colors['success'])
        
        # 成功メッセージ
        result = messagebox.askyesno(
            "Success", 
            f"Voice conversion completed!\n\nOutput file:\n{os.path.basename(self.output_var.get())}\n\nOpen output folder?",
            icon='info')
        
        if result:
            output_dir = os.path.dirname(self.output_var.get())
            if sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", output_dir])
            elif sys.platform == "win32":  # Windows
                subprocess.Popen(["explorer", output_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", output_dir])

def main():
    root = tk.Tk()
    app = DarkModeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
