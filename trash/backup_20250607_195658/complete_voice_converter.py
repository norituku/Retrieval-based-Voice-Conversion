#!/usr/bin/env python3
"""
Complete Voice Converter
完全版RVC音声変換システム（GUI統合版）
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from pathlib import Path
import subprocess
import time

class CompleteVoiceConverter:
    """完全版音声変換アプリケーション"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 RVC Voice Converter - Complete Edition")
        self.root.geometry("1000x700")
        
        # ダークモードカラーパレット
        self.colors = {
            'background_primary': '#1a1a1a',
            'background_secondary': '#2d2d2d',
            'surface_card': '#3d3d3d',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent_primary': '#007acc',
            'success': '#4CAF50',
            'warning': '#ff9800',
            'error': '#f44336'
        }
        
        self.root.configure(bg=self.colors['background_primary'])
        
        # 変換システム初期化フラグ
        self.converter_ready = False
        self.conversion_in_progress = False
        
        self.setup_ui()
        self.init_converter_system()
    
    def setup_ui(self):
        """UI構築"""
        # メインコンテナ
        main_container = tk.Frame(self.root, bg=self.colors['background_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(main_container,
                              text="🎤 RVC Voice Converter - Complete Edition",
                              font=('Arial', 18, 'bold'),
                              bg=self.colors['background_primary'],
                              fg=self.colors['text_primary'])
        title_label.pack(pady=(0, 20))
        
        # ステータス表示
        self.setup_status_section(main_container)
        
        # ファイル選択セクション
        self.setup_file_section(main_container)
        
        # モデル選択セクション
        self.setup_model_section(main_container)
        
        # 変換設定セクション
        self.setup_conversion_settings(main_container)
        
        # 変換ボタンとプログレス
        self.setup_conversion_controls(main_container)
        
        # ログ表示
        self.setup_log_section(main_container)
    
    def setup_status_section(self, parent):
        """ステータス表示セクション"""
        status_frame = tk.LabelFrame(parent,
                                    text="システムステータス",
                                    font=('Arial', 12, 'bold'),
                                    bg=self.colors['background_primary'],
                                    fg=self.colors['text_primary'])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_text = tk.Label(status_frame,
                                   text="🔄 システム初期化中...",
                                   font=('Arial', 10),
                                   bg=self.colors['background_primary'],
                                   fg=self.colors['warning'])
        self.status_text.pack(pady=10)
    
    def setup_file_section(self, parent):
        """ファイル選択セクション"""
        file_frame = tk.LabelFrame(parent,
                                  text="ファイル選択",
                                  font=('Arial', 12, 'bold'),
                                  bg=self.colors['background_primary'],
                                  fg=self.colors['text_primary'])
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 入力ファイル
        input_frame = tk.Frame(file_frame, bg=self.colors['background_primary'])
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="入力音声ファイル:",
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(anchor='w')
        
        input_entry_frame = tk.Frame(input_frame, bg=self.colors['background_primary'])
        input_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.input_var = tk.StringVar()
        input_entry = tk.Entry(input_entry_frame,
                              textvariable=self.input_var,
                              bg=self.colors['background_secondary'],
                              fg=self.colors['text_primary'],
                              font=('Arial', 10))
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        input_button = tk.Button(input_entry_frame,
                                text="参照",
                                command=self.browse_input_file,
                                bg=self.colors['accent_primary'],
                                fg='white',
                                font=('Arial', 9))
        input_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 出力ディレクトリ
        output_frame = tk.Frame(file_frame, bg=self.colors['background_primary'])
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(output_frame, text="出力ディレクトリ:",
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(anchor='w')
        
        output_entry_frame = tk.Frame(output_frame, bg=self.colors['background_primary'])
        output_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_var = tk.StringVar()
        self.output_var.set("enhanced_output")  # デフォルト値
        output_entry = tk.Entry(output_entry_frame,
                               textvariable=self.output_var,
                               bg=self.colors['background_secondary'],
                               fg=self.colors['text_primary'],
                               font=('Arial', 10))
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        output_button = tk.Button(output_entry_frame,
                                 text="参照",
                                 command=self.browse_output_dir,
                                 bg=self.colors['accent_primary'],
                                 fg='white',
                                 font=('Arial', 9))
        output_button.pack(side=tk.RIGHT, padx=(5, 0))
    
    def setup_model_section(self, parent):
        """モデル選択セクション"""
        model_frame = tk.LabelFrame(parent,
                                   text="音声モデル選択",
                                   font=('Arial', 12, 'bold'),
                                   bg=self.colors['background_primary'],
                                   fg=self.colors['text_primary'])
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        # モデル選択コンボボックス
        model_select_frame = tk.Frame(model_frame, bg=self.colors['background_primary'])
        model_select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(model_select_frame, text="使用モデル:",
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(anchor='w')
        
        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(model_select_frame,
                                          textvariable=self.model_var,
                                          font=('Arial', 10),
                                          state="readonly")
        self.model_combobox.pack(fill=tk.X, pady=(5, 0))
        
        # モデル更新ボタン
        refresh_button = tk.Button(model_select_frame,
                                  text="モデル一覧更新",
                                  command=self.refresh_models,
                                  bg=self.colors['surface_card'],
                                  fg=self.colors['text_primary'],
                                  font=('Arial', 9))
        refresh_button.pack(pady=(5, 0))
    
    def setup_conversion_settings(self, parent):
        """変換設定セクション"""
        settings_frame = tk.LabelFrame(parent,
                                      text="変換設定",
                                      font=('Arial', 12, 'bold'),
                                      bg=self.colors['background_primary'],
                                      fg=self.colors['text_primary'])
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 設定項目フレーム
        settings_grid = tk.Frame(settings_frame, bg=self.colors['background_primary'])
        settings_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # ピッチシフト
        pitch_frame = tk.Frame(settings_grid, bg=self.colors['background_primary'])
        pitch_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(pitch_frame, text="ピッチシフト:",
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        self.pitch_var = tk.IntVar(value=0)
        pitch_scale = tk.Scale(pitch_frame, from_=-12, to=12,
                              variable=self.pitch_var,
                              orient=tk.HORIZONTAL,
                              bg=self.colors['background_secondary'],
                              fg=self.colors['text_primary'],
                              highlightthickness=0)
        pitch_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # インデックス比率
        index_frame = tk.Frame(settings_grid, bg=self.colors['background_primary'])
        index_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(index_frame, text="インデックス比率:",
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        self.index_var = tk.DoubleVar(value=0.7)
        index_scale = tk.Scale(index_frame, from_=0.0, to=1.0,
                              resolution=0.1,
                              variable=self.index_var,
                              orient=tk.HORIZONTAL,
                              bg=self.colors['background_secondary'],
                              fg=self.colors['text_primary'],
                              highlightthickness=0)
        index_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 保護レベル
        protect_frame = tk.Frame(settings_grid, bg=self.colors['background_primary'])
        protect_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(protect_frame, text="保護レベル:",
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        self.protect_var = tk.DoubleVar(value=0.33)
        protect_scale = tk.Scale(protect_frame, from_=0.0, to=1.0,
                                resolution=0.1,
                                variable=self.protect_var,
                                orient=tk.HORIZONTAL,
                                bg=self.colors['background_secondary'],
                                fg=self.colors['text_primary'],
                                highlightthickness=0)
        protect_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
    
    def setup_conversion_controls(self, parent):
        """変換コントロールセクション"""
        control_frame = tk.Frame(parent, bg=self.colors['background_primary'])
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 変換ボタン
        self.convert_button = tk.Button(control_frame,
                                       text="🎤 音声変換開始",
                                       command=self.start_conversion,
                                       bg=self.colors['success'],
                                       fg='white',
                                       font=('Arial', 14, 'bold'),
                                       padx=30, pady=10)
        self.convert_button.pack()
        
        # プログレスバー
        self.progress = ttk.Progressbar(control_frame,
                                       mode='indeterminate',
                                       length=400)
        self.progress.pack(pady=(10, 0))
        
        # 進捗テキスト
        self.progress_text = tk.Label(control_frame,
                                     text="",
                                     font=('Arial', 10),
                                     bg=self.colors['background_primary'],
                                     fg=self.colors['text_secondary'])
        self.progress_text.pack(pady=(5, 0))
    
    def setup_log_section(self, parent):
        """ログ表示セクション"""
        log_frame = tk.LabelFrame(parent,
                                 text="変換ログ",
                                 font=('Arial', 12, 'bold'),
                                 bg=self.colors['background_primary'],
                                 fg=self.colors['text_primary'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # ログテキストとスクロールバー
        log_container = tk.Frame(log_frame, bg=self.colors['background_primary'])
        log_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(log_container,
                               bg=self.colors['background_secondary'],
                               fg=self.colors['text_primary'],
                               font=('Courier', 9),
                               wrap=tk.WORD,
                               height=8)
        
        log_scrollbar = tk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def init_converter_system(self):
        """変換システム初期化"""
        def init_thread():
            try:
                self.log_message("🔄 Enhanced Voice Converterシステム初期化中...")
                
                # Poetry環境確認
                result = subprocess.run(['poetry', '--version'], 
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_message("✅ Poetry環境確認完了")
                else:
                    self.log_message("❌ Poetry環境が見つかりません")
                    self.update_status("❌ Poetry環境エラー", self.colors['error'])
                    return
                
                # Enhanced Voice Converterテスト
                test_cmd = [
                    'poetry', 'run', 'python', '-c',
                    '''
from enhanced_voice_converter import EnhancedVoiceConverter
converter = EnhancedVoiceConverter()
models = converter.list_available_models()
print(f"MODELS:{len(models)}")
for i, model in enumerate(models):
    print(f"MODEL_{i}:{model['name']}:{model['path']}")
'''
                ]
                
                result = subprocess.run(test_cmd, capture_output=True, text=True, cwd=os.getcwd())
                
                if result.returncode == 0:
                    self.log_message("✅ Enhanced Voice Converter初期化完了")
                    
                    # モデル情報解析
                    self.available_models = []
                    for line in result.stdout.split('\\n'):
                        if line.startswith('MODEL_'):
                            parts = line.split(':', 2)
                            if len(parts) == 3:
                                model_name = parts[1]
                                model_path = parts[2]
                                self.available_models.append({
                                    'name': model_name,
                                    'path': model_path
                                })
                    
                    self.log_message(f"✅ {len(self.available_models)}個のモデルを検出")
                    
                    # UI更新
                    self.root.after(0, self.update_models_ui)
                    self.root.after(0, lambda: self.update_status("✅ システム準備完了", self.colors['success']))
                    
                    self.converter_ready = True
                    
                else:
                    error_msg = result.stderr or result.stdout
                    self.log_message(f"❌ 初期化エラー: {error_msg}")
                    self.root.after(0, lambda: self.update_status("❌ 初期化失敗", self.colors['error']))
                    
            except Exception as e:
                self.log_message(f"❌ 初期化例外: {e}")
                self.root.after(0, lambda: self.update_status("❌ 初期化例外", self.colors['error']))
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def update_models_ui(self):
        """モデル選択UIの更新"""
        model_names = [model['name'] for model in self.available_models]
        self.model_combobox['values'] = model_names
        if model_names:
            self.model_combobox.current(0)
    
    def update_status(self, message, color):
        """ステータス更新"""
        self.status_text.config(text=message, fg=color)
    
    def log_message(self, message):
        """ログメッセージ追加"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\\n"
        
        def update_log():
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, update_log)
        else:
            update_log()
    
    def browse_input_file(self):
        """入力ファイル選択"""
        filename = filedialog.askopenfilename(
            title="音声ファイルを選択",
            filetypes=[
                ("音声ファイル", "*.wav *.mp3 *.m4a *.flac *.ogg"),
                ("全てのファイル", "*.*")
            ]
        )
        if filename:
            self.input_var.set(filename)
            self.log_message(f"📁 入力ファイル選択: {Path(filename).name}")
    
    def browse_output_dir(self):
        """出力ディレクトリ選択"""
        dirname = filedialog.askdirectory(title="出力ディレクトリを選択")
        if dirname:
            self.output_var.set(dirname)
            self.log_message(f"📁 出力ディレクトリ選択: {dirname}")
    
    def refresh_models(self):
        """モデル一覧更新"""
        if not self.converter_ready:
            messagebox.showwarning("警告", "システムがまだ初期化されていません")
            return
        
        self.log_message("🔄 モデル一覧を更新中...")
        self.init_converter_system()
    
    def start_conversion(self):
        """音声変換開始"""
        if not self.converter_ready:
            messagebox.showwarning("警告", "システムがまだ初期化されていません")
            return
        
        if self.conversion_in_progress:
            messagebox.showwarning("警告", "変換が既に実行中です")
            return
        
        # 入力検証
        input_file = self.input_var.get()
        output_dir = self.output_var.get()
        model_name = self.model_var.get()
        
        if not input_file:
            messagebox.showwarning("警告", "入力ファイルを選択してください")
            return
        
        if not Path(input_file).exists():
            messagebox.showerror("エラー", "入力ファイルが見つかりません")
            return
        
        if not output_dir:
            messagebox.showwarning("警告", "出力ディレクトリを指定してください")
            return
        
        if not model_name:
            messagebox.showwarning("警告", "音声モデルを選択してください")
            return
        
        # 変換開始
        self.conversion_in_progress = True
        self.convert_button.config(state='disabled', text="🔄 変換中...")
        self.progress.start()
        self.progress_text.config(text="音声変換を実行中...")
        
        def conversion_thread():
            try:
                # 出力ファイル名生成
                input_path = Path(input_file)
                output_path = Path(output_dir) / f"{input_path.stem}_converted_{model_name}.wav"
                
                self.log_message(f"🎤 音声変換開始:")
                self.log_message(f"   入力: {input_path.name}")
                self.log_message(f"   出力: {output_path.name}")
                self.log_message(f"   モデル: {model_name}")
                self.log_message(f"   ピッチ: {self.pitch_var.get()}")
                
                # 変換パラメータ
                params = {
                    'f0_up_key': self.pitch_var.get(),
                    'index_rate': self.index_var.get(),
                    'protect': self.protect_var.get(),
                    'f0_method': 'harvest',  # MPS環境での安定性
                    'filter_radius': 3,
                    'rms_mix_rate': 0.25
                }
                
                # Enhanced Voice Converter実行
                conversion_cmd = [
                    'poetry', 'run', 'python', '-c',
                    f'''
from enhanced_voice_converter import EnhancedVoiceConverter
import json

# パラメータ
input_path = "{input_file}"
output_path = "{output_path}"
model_name = "{model_name}"
params = {json.dumps(params)}

try:
    # 変換実行
    converter = EnhancedVoiceConverter()
    
    # モデル情報取得
    models = converter.list_available_models()
    selected_model = None
    for model in models:
        if model["name"] == model_name:
            selected_model = model
            break
    
    if not selected_model:
        print(f"ERROR: Model not found: {{model_name}}")
        exit(1)
    
    # モデルロード
    load_result = converter.load_model(selected_model["path"], selected_model.get("index_path"))
    if not load_result:
        print(f"ERROR: Failed to load model: {{selected_model['path']}}")
        exit(1)
    
    print(f"SUCCESS: Model loaded: {{selected_model['name']}}")
    
    # 変換実行
    result = converter.convert_audio(
        input_path=input_path,
        output_path=output_path,
        **params
    )
    
    print(f"SUCCESS: Conversion completed: {{result}}")
    
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
    exit(1)
'''
                ]
                
                # 変換実行
                result = subprocess.run(conversion_cmd, 
                                       capture_output=True, text=True, 
                                       cwd=os.getcwd())
                
                if result.returncode == 0:
                    # 成功処理
                    if output_path.exists():
                        size_mb = output_path.stat().st_size / 1024 / 1024
                        self.log_message(f"✅ 変換完了! ({size_mb:.1f}MB)")
                        self.log_message(f"📁 出力ファイル: {output_path}")
                        
                        # 完了メッセージ
                        self.root.after(0, lambda: messagebox.showinfo(
                            "変換完了", 
                            f"音声変換が完了しました!\\n\\n"
                            f"出力ファイル: {output_path.name}\\n"
                            f"サイズ: {size_mb:.1f}MB"
                        ))
                    else:
                        self.log_message("⚠️ 変換は完了しましたが、出力ファイルが見つかりません")
                else:
                    # エラー処理
                    error_msg = result.stderr or result.stdout
                    self.log_message(f"❌ 変換エラー: {error_msg}")
                    self.root.after(0, lambda: messagebox.showerror(
                        "変換エラー", 
                        f"音声変換に失敗しました\\n\\n{error_msg}"
                    ))
                
            except Exception as e:
                self.log_message(f"❌ 変換例外: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "システムエラー", 
                    f"変換中にエラーが発生しました\\n\\n{e}"
                ))
            
            finally:
                # UI復元
                self.conversion_in_progress = False
                self.root.after(0, lambda: self.convert_button.config(state='normal', text="🎤 音声変換開始"))
                self.root.after(0, self.progress.stop)
                self.root.after(0, lambda: self.progress_text.config(text=""))
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()

def main():
    """メイン関数"""
    app = CompleteVoiceConverter()
    app.run()

if __name__ == "__main__":
    main()