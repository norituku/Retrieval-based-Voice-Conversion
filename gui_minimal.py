#!/usr/bin/env python3
"""
最小GUI - Voice Converter
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

class MinimalVoiceConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter - Minimal")
        self.root.geometry("800x600")
        
        # ライトテーマで開始（見やすくするため）
        self.root.configure(bg='#f0f0f0')
        
        # メインコンテナ
        main_container = tk.Frame(self.root, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title = tk.Label(main_container, 
                        text="Voice Converter", 
                        font=('Arial', 24, 'bold'),
                        bg='white')
        title.pack(pady=20)
        
        # ファイル選択セクション
        file_frame = tk.LabelFrame(main_container, 
                                  text="File Selection", 
                                  font=('Arial', 12, 'bold'),
                                  bg='white',
                                  padx=20, pady=20)
        file_frame.pack(fill=tk.X, pady=10)
        
        # Input File
        tk.Label(file_frame, text="Input File:", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.input_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.input_var, width=50).grid(row=0, column=1, pady=5)
        tk.Button(file_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output File
        tk.Label(file_frame, text="Output File:", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.output_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.output_var, width=50).grid(row=1, column=1, pady=5)
        tk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Settings
        settings_frame = tk.LabelFrame(main_container, 
                                      text="Settings", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=20, pady=20)
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Pitch
        tk.Label(settings_frame, text="Pitch (-12 to +12):", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.pitch_var = tk.IntVar(value=0)
        pitch_scale = tk.Scale(settings_frame, from_=-12, to=12, 
                              variable=self.pitch_var, 
                              orient=tk.HORIZONTAL,
                              length=300)
        pitch_scale.grid(row=0, column=1, pady=5)
        
        # Convert Button
        convert_btn = tk.Button(main_container, 
                               text="Convert", 
                               font=('Arial', 16, 'bold'),
                               bg='#4CAF50', 
                               fg='white',
                               padx=40, 
                               pady=10,
                               command=self.convert)
        convert_btn.pack(pady=20)
        
        # Status
        self.status_label = tk.Label(main_container, 
                                   text="Ready", 
                                   font=('Arial', 10),
                                   bg='white',
                                   fg='gray')
        self.status_label.pack()
        
    def browse_input(self):
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
        input_file = self.input_var.get()
        if input_file:
            base = os.path.splitext(input_file)[0]
            self.output_var.set(f"{base}_converted.wav")
    
    def convert(self):
        if not self.input_var.get():
            messagebox.showwarning("Warning", "Please select an input file")
            return
            
        if not self.output_var.get():
            messagebox.showwarning("Warning", "Please specify an output file")
            return
            
        # ここで実際の変換処理を行う
        self.status_label.config(text="Converting... (This is a demo)")
        self.root.after(2000, self.conversion_complete)
    
    def conversion_complete(self):
        self.status_label.config(text="Conversion completed! (Demo)")
        messagebox.showinfo("Success", "Voice conversion completed!\n(This is a demo version)")

def main():
    root = tk.Tk()
    app = MinimalVoiceConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
