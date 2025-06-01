#!/usr/bin/env python3
"""
Voice Converter - Simple Dark GUI (tkinterのみ使用)
"""
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
from pathlib import Path

class SimpleDarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter")
        self.root.geometry("1000x700")
        
        # シンプルなカラー設定
        self.bg_color = '#1a1a1a'
        self.fg_color = '#ffffff'
        self.button_color = '#0d7377'
        self.entry_bg = '#2d2d2d'
        
        # ウィンドウの背景色
        self.root.configure(bg=self.bg_color)
        
        # 変数の初期化
        self.init_variables()
        
        # UI構築
        self.create_ui()
        
        # モデル読み込み
        self.load_models()
        
    def init_variables(self):
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.selected_model = tk.StringVar()
        self.pitch_value = tk.IntVar(value=0)
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = os.path.join(self.base_dir, "model_dir")
        
    def create_ui(self):
        # メインコンテナ
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title = tk.Label(main_frame, 
                        text="Voice Converter", 
                        font=('Arial', 24, 'bold'),
                        bg=self.bg_color, 
                        fg=self.fg_color)
        title.pack(pady=(0, 20))
        
        # 2カラムレイアウト
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左カラム - モデル選択
        left_frame = tk.Frame(content_frame, bg=self.bg_color, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_frame.pack_propagate(False)
        
        self.create_model_section(left_frame)
        
        # 右カラム - メイン設定
        right_frame = tk.Frame(content_frame, bg=self.bg_color)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_main_section(right_frame)
        
    def create_model_section(self, parent):
        # モデルセクションタイトル
        model_title = tk.Label(parent, 
                              text="Voice Models", 
                              font=('Arial', 16, 'bold'),
                              bg=self.bg_color, 
                              fg=self.fg_color)
        model_title.pack(pady=(0, 10))
        
        # モデルリストボックスフレーム
        list_frame = tk.Frame(parent, bg=self.entry_bg)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # スクロールバー
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # リストボックス
        self.model_listbox = tk.Listbox(
            list_frame,
            bg=self.entry_bg,
            fg=self.fg_color,
            selectbackground=self.button_color,
            selectforeground='white',
            font=('Arial', 11),
            bd=0,
            highlightthickness=1,
            highlightbackground='#444444',
            highlightcolor='#666666',
            yscrollcommand=scrollbar.set
        )
        self.model_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.model_listbox.yview)
        
        # モデル選択イベント
        self.model_listbox.bind('<<ListboxSelect>>', self.on_model_select)
        
        # リフレッシュボタン
        refresh_btn = tk.Button(parent,
                               text="Refresh Models",
                               command=self.load_models,
                               bg=self.entry_bg,
                               fg=self.fg_color,
                               activebackground='#3d3d3d',
                               activeforeground=self.fg_color,
                               bd=1,
                               pady=5)
        refresh_btn.pack(pady=10, fill=tk.X)
        
    def create_main_section(self, parent):
        # ファイル選択セクション
        file_section = tk.LabelFrame(parent, 
                                   text=" File Input/Output ",
                                   bg=self.bg_color,
                                   fg=self.fg_color,
                                   font=('Arial', 12, 'bold'),
                                   bd=1,
                                   relief=tk.SOLID)
        file_section.pack(fill=tk.X, pady=(0, 20))
        
        # Input File
        input_frame = tk.Frame(file_section, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        tk.Label(input_frame, 
                text="Input File:", 
                bg=self.bg_color, 
                fg=self.fg_color,
                width=12,
                anchor='w').pack(side=tk.LEFT)
        
        input_entry = tk.Entry(input_frame,
                              textvariable=self.input_file,
                              bg=self.entry_bg,
                              fg=self.fg_color,
                              insertbackground=self.fg_color,
                              bd=1,
                              relief=tk.SOLID)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(input_frame,
                 text="Browse",
                 command=self.browse_input,
                 bg=self.button_color,
                 fg='white',
                 activebackground='#14a085',
                 activeforeground='white',
                 bd=0,
                 padx=15,
                 pady=3).pack(side=tk.LEFT)
        
        # Output File
        output_frame = tk.Frame(file_section, bg=self.bg_color)
        output_frame.pack(fill=tk.X, padx=15, pady=(5, 15))
        
        tk.Label(output_frame, 
                text="Output File:", 
                bg=self.bg_color, 
                fg=self.fg_color,
                width=12,
                anchor='w').pack(side=tk.LEFT)
        
        output_entry = tk.Entry(output_frame,
                               textvariable=self.output_file,
                               bg=self.entry_bg,
                               fg=self.fg_color,
                               insertbackground=self.fg_color,
                               bd=1,
                               relief=tk.SOLID)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(output_frame,
                 text="Browse",
                 command=self.browse_output,
                 bg=self.button_color,
                 fg='white',
                 activebackground='#14a085',
                 activeforeground='white',
                 bd=0,
                 padx=15,
                 pady=3).pack(side=tk.LEFT)
        
        # 設定セクション
        settings_section = tk.LabelFrame(parent, 
                                       text=" Conversion Settings ",
                                       bg=self.bg_color,
                                       fg=self.fg_color,
                                       font=('Arial', 12, 'bold'),
                                       bd=1,
                                       relief=tk.SOLID)
        settings_section.pack(fill=tk.X, pady=(0, 20))
        
        # Pitch設定
        pitch_frame = tk.Frame(settings_section, bg=self.bg_color)
        pitch_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(pitch_frame, 
                text="Pitch:", 
                bg=self.bg_color, 
                fg=self.fg_color,
                width=12,
                anchor='w').pack(side=tk.LEFT)
        
        self.pitch_scale = tk.Scale(pitch_frame,
                                   from_=-12, to=12,
                                   orient=tk.HORIZONTAL,
                                   variable=self.pitch_value,
                                   bg=self.bg_color,
                                   fg=self.fg_color,
                                   highlightthickness=0,
                                   troughcolor=self.entry_bg,
                                   activebackground=self.button_color)
        self.pitch_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.pitch_label = tk.Label(pitch_frame, 
                                   text="0", 
                                   bg=self.bg_color, 
                                   fg=self.button_color,
                                   font=('Arial', 12, 'bold'),
                                   width=4)
        self.pitch_label.pack(side=tk.LEFT)
        
        self.pitch_value.trace('w', lambda *args: self.pitch_label.config(
            text=f"{self.pitch_value.get():+d}"))
        
        # コントロールセクション
        control_frame = tk.Frame(parent, bg=self.bg_color)
        control_frame.pack(fill=tk.X)
        
        # プログレスバー代替（シンプルなラベル）
        self.status_label = tk.Label(control_frame,
                                    text="Ready to convert",
                                    bg=self.bg_color,
                                    fg='#999999',
                                    font=('Arial', 11))
        self.status_label.pack(pady=(0, 10))
        
        # コンバートボタン
        self.convert_btn = tk.Button(control_frame,
                                    text="CONVERT",
                                    command=self.convert,
                                    bg=self.button_color,
                                    fg='white',
                                    font=('Arial', 16, 'bold'),
                                    activebackground='#14a085',
                                    activeforeground='white',
                                    bd=0,
                                    padx=40,
                                    pady=12,
                                    cursor='hand2')
        self.convert_btn.pack()
        
    def on_model_select(self, event):
        selection = self.model_listbox.curselection()
        if selection:
            model_name = self.model_listbox.get(selection[0])
            self.selected_model.set(model_name)
            self.auto_set_output()
            
    def load_models(self):
        self.model_listbox.delete(0, tk.END)
        
        if os.path.exists(self.model_dir):
            models = [d for d in os.listdir(self.model_dir) 
                     if os.path.isdir(os.path.join(self.model_dir, d)) 
                     and not d.startswith('.')]
            
            for model in sorted(models):
                self.model_listbox.insert(tk.END, model)
                
            if models:
                self.model_listbox.selection_set(0)
                self.selected_model.set(models[0])
                
            self.status_label.config(text=f"Loaded {len(models)} models")
        else:
            self.status_label.config(text="Model directory not found")
            
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.m4a *.flac *.aac *.ogg *.aiff *.aif"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            self.auto_set_output()
            
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".wav",
            filetypes=[
                ("WAV Files", "*.wav"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.output_file.set(filename)
            
    def auto_set_output(self):
        input_path = self.input_file.get()
        if input_path and self.selected_model.get():
            base = os.path.splitext(input_path)[0]
            model = self.selected_model.get()
            self.output_file.set(f"{base}_{model}.wav")
            
    def convert(self):
        if not self.input_file.get():
            messagebox.showwarning("Warning", "Please select an input file")
            return
            
        if not self.selected_model.get():
            messagebox.showwarning("Warning", "Please select a voice model")
            return
            
        if not self.output_file.get():
            messagebox.showwarning("Warning", "Please specify an output file")
            return
            
        self.convert_btn.config(state='disabled', text="CONVERTING...")
        self.status_label.config(text="Processing... Please wait", fg=self.button_color)
        
        # デモ用の変換処理
        self.root.after(2000, self.conversion_complete)
        
    def conversion_complete(self):
        self.convert_btn.config(state='normal', text="CONVERT")
        self.status_label.config(text="Conversion completed!", fg='#27ae60')
        
        result = messagebox.askyesno(
            "Success", 
            f"Voice conversion completed!\n\nOutput file:\n{os.path.basename(self.output_file.get())}\n\nOpen output folder?")
        
        if result:
            output_dir = os.path.dirname(self.output_file.get())
            if sys.platform == "darwin":
                subprocess.Popen(["open", output_dir])

def main():
    root = tk.Tk()
    app = SimpleDarkGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
