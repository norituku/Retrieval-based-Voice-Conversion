#!/usr/bin/env python3
"""
Voice Converter - Dark Mode GUI (段階的構築版)
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from pathlib import Path

class DarkModeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter - Dark Mode")
        
        # 基本的なダークカラー設定
        self.colors = {
            'bg_primary': '#1e1e1e',
            'bg_secondary': '#2d2d2d',
            'bg_tertiary': '#3c3c3c',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#0d7377',
            'accent_hover': '#14a085',
            'border': '#4a4a4a',
            'success': '#27ae60',
            'error': '#e74c3c'
        }
        
        # 変数の初期化
        self.init_variables()
        
        # ウィンドウ設定
        self.setup_window()
        
        # スタイル設定
        self.setup_styles()
        
        # UI構築
        self.create_ui()
        
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
        
        # ディレクトリ設定
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = os.path.join(self.base_dir, "model_dir")
        
    def setup_window(self):
        """ウィンドウの設定"""
        self.root.configure(bg=self.colors['bg_primary'])
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
    def setup_styles(self):
        """スタイルの設定"""
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
        
        # エントリー
        style.configure('Dark.TEntry',
                       fieldbackground=self.colors['bg_tertiary'],
                       borderwidth=1,
                       insertcolor=self.colors['text_primary'])
        
    def create_ui(self):
        """UIの構築"""
        # メインコンテナ
        main_container = ttk.Frame(self.root, style='Dark.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左側パネル（モデル選択）
        left_panel = ttk.Frame(main_container, style='Dark.TFrame', width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.create_model_panel(left_panel)
        
        # 右側パネル（メインコンテンツ）
        right_panel = ttk.Frame(main_container, style='Dark.TFrame')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_main_content(right_panel)
        
    def create_model_panel(self, parent):
        """モデル選択パネル"""
        # タイトル
        title_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(title_frame, 
                text="Voice Models",
                font=('Arial', 14, 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(pady=5)
        
        # モデルリスト
        list_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
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
            font=('Arial', 10),
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.model_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.model_listbox.yview)
        
        # モデルを読み込む
        self.load_models()
        
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
        
        # 変換設定セクション
        self.create_settings_section(scrollable_frame)
        
        # コントロールボタン
        self.create_control_section(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_file_section(self, parent):
        """ファイル選択セクション"""
        frame = ttk.LabelFrame(parent, text="File Input/Output", style='Dark.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Input File
        input_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="Input File:", 
                bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary'],
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
        output_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(output_frame, text="Output File:", 
                bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary'],
                width=12,
                anchor='w').pack(side=tk.LEFT)
        
        ttk.Entry(output_frame, 
                 textvariable=self.output_var,
                 style='Dark.TEntry').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(output_frame, 
                  text="Browse",
                  command=self.browse_output,
                  style='Accent.TButton').pack(side=tk.LEFT)
        
    def create_settings_section(self, parent):
        """変換設定セクション"""
        frame = ttk.LabelFrame(parent, text="Conversion Settings", style='Dark.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Pitch
        pitch_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        pitch_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(pitch_frame, text="Pitch:", 
                bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary'],
                width=12,
                anchor='w').pack(side=tk.LEFT)
        
        pitch_scale = tk.Scale(pitch_frame,
                              from_=-12, to=12,
                              orient=tk.HORIZONTAL,
                              variable=self.pitch_var,
                              bg=self.colors['bg_tertiary'],
                              fg=self.colors['text_primary'],
                              highlightthickness=0,
                              troughcolor=self.colors['bg_primary'])
        pitch_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.pitch_label = tk.Label(pitch_frame, 
                                   text="0",
                                   bg=self.colors['bg_secondary'], 
                                   fg=self.colors['text_primary'],
                                   width=4)
        self.pitch_label.pack(side=tk.LEFT)
        
        # ピッチ値の更新
        self.pitch_var.trace('w', lambda *args: self.pitch_label.config(text=str(self.pitch_var.get())))
        
    def create_control_section(self, parent):
        """コントロールセクション"""
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        frame.pack(fill=tk.X, padx=10, pady=20)
        
        # Convert Button
        self.convert_btn = tk.Button(frame,
                                    text="Convert",
                                    command=self.convert,
                                    bg=self.colors['accent'],
                                    fg='white',
                                    font=('Arial', 12, 'bold'),
                                    padx=30,
                                    pady=10,
                                    bd=0,
                                    activebackground=self.colors['accent_hover'],
                                    activeforeground='white')
        self.convert_btn.pack()
        
        # Status Label
        self.status_label = tk.Label(parent,
                                    text="Ready",
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_secondary'],
                                    font=('Arial', 10))
        self.status_label.pack(pady=5)
        
    def load_models(self):
        """モデルを読み込む"""
        try:
            if os.path.exists(self.model_dir):
                models = [d for d in os.listdir(self.model_dir) 
                         if os.path.isdir(os.path.join(self.model_dir, d)) and not d.startswith('.')]
                
                self.model_listbox.delete(0, tk.END)
                for model in sorted(models):
                    self.model_listbox.insert(tk.END, model)
                    
                if models:
                    self.model_listbox.selection_set(0)
                    self.selected_model.set(models[0])
                    
        except Exception as e:
            print(f"Error loading models: {e}")
    
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
    
    def auto_set_output(self):
        """出力ファイル名を自動設定"""
        input_file = self.input_var.get()
        if input_file:
            base = os.path.splitext(input_file)[0]
            model = self.selected_model.get() or "converted"
            self.output_var.set(f"{base}_{model}.wav")
    
    def convert(self):
        """変換処理"""
        if not self.input_var.get():
            messagebox.showwarning("Warning", "Please select an input file")
            return
            
        if not self.output_var.get():
            messagebox.showwarning("Warning", "Please specify an output file")
            return
            
        self.status_label.config(text="Converting...", fg=self.colors['accent'])
        self.convert_btn.config(state='disabled')
        
        # デモ用（実際の変換処理はここに実装）
        self.root.after(2000, self.conversion_complete)
    
    def conversion_complete(self):
        """変換完了"""
        self.status_label.config(text="Conversion completed!", fg=self.colors['success'])
        self.convert_btn.config(state='normal')
        messagebox.showinfo("Success", "Voice conversion completed!")

def main():
    root = tk.Tk()
    app = DarkModeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
