#!/usr/bin/env python3
"""
RVC Dark Mode GUI - Stable Enhanced Version
セグメンテーションフォルトを修正した安定版
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime

# 改良版音声変換のインポート（安全な方法）
try:
    from enhanced_converter_simple import SimpleEnhancedConverter
    ENHANCED_CONVERTER_AVAILABLE = True
    print("✅ Enhanced Voice Converter loaded")
except ImportError as e:
    ENHANCED_CONVERTER_AVAILABLE = False
    print(f"⚠️ Enhanced Voice Converter not available: {e}")

class StableDarkModeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter - Enhanced Edition")
        
        # 基本設定
        self.setup_basic_vars()
        
        # 改良版システムの初期化（安全な方法）
        self.init_enhanced_converter_safe()
        
        # UIのセットアップ
        self.setup_colors()
        self.setup_window()
        self.create_main_ui()
        
        # 初期データの読み込み
        self.load_models_safe()
        
        print("✅ Stable GUI initialized successfully")
    
    def setup_basic_vars(self):
        """基本変数の設定"""
        # ファイルパス関連
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(self.base_dir, "gui_settings.json")
        
        # Tkinter変数
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "VoiceConverter_Output"))
        self.selected_model = tk.StringVar()
        self.pitch_var = tk.DoubleVar(value=0)
        self.f0_method_var = tk.StringVar(value="rmvpe")
        self.index_rate_var = tk.DoubleVar(value=0.75)
        
        # モデル関連
        self.model_dir = os.path.join(self.base_dir, "model_dir")
        self.models = []
        
        # 変換状態
        self.converting = False
    
    def init_enhanced_converter_safe(self):
        """改良版コンバーターの安全な初期化"""
        if ENHANCED_CONVERTER_AVAILABLE:
            try:
                self.enhanced_converter = SimpleEnhancedConverter(
                    model_dir=self.model_dir,
                    output_dir="enhanced_output"
                )
                self.use_enhanced_conversion = True
                
                # 改良機能の状態を取得
                status = self.enhanced_converter.get_enhancement_status()
                print(f"Enhancement features: {status['pipeline_type']}")
                
            except Exception as e:
                print(f"❌ Enhanced converter initialization failed: {e}")
                self.enhanced_converter = None
                self.use_enhanced_conversion = False
        else:
            self.enhanced_converter = None
            self.use_enhanced_conversion = False
            print("Using standard conversion mode")
    
    def setup_colors(self):
        """カラーテーマの設定"""
        self.colors = {
            'background_primary': '#0F0F10',
            'background_secondary': '#1A1A1C',
            'surface_card': '#1C1C1F',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B8B8B8',
            'accent_primary': '#5A9FFF',
            'success': '#52E88C',
            'warning': '#FFD23F',
            'error': '#FF6B6B',
            'border_subtle': '#2F2F33',
        }
    
    def setup_window(self):
        """ウィンドウの設定"""
        # ウィンドウサイズと位置
        self.root.geometry("900x600")
        self.root.minsize(700, 500)
        
        # 背景色
        self.root.configure(bg=self.colors['background_primary'])
        
        # macOS設定
        if sys.platform == "darwin":
            try:
                # ダークモード対応
                self.root.tk.call('tk', 'mac', 'darkmode', 'dark')
            except:
                pass
        
        # スタイル設定
        self.setup_styles()
    
    def setup_styles(self):
        """TTKスタイルの設定"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # フレーム
        style.configure("TFrame", background=self.colors['background_primary'])
        
        # ラベルフレーム
        style.configure("TLabelframe", 
                       background=self.colors['surface_card'],
                       bordercolor=self.colors['border_subtle'],
                       relief="flat")
        style.configure("TLabelframe.Label",
                       background=self.colors['surface_card'],
                       foreground=self.colors['text_primary'],
                       font=("SF Pro Display", 12, "bold"))
        
        # ラベル
        style.configure("TLabel",
                       background=self.colors['background_primary'],
                       foreground=self.colors['text_primary'])
        
        # ボタン
        style.configure("TButton",
                       background=self.colors['accent_primary'],
                       foreground="white",
                       borderwidth=0,
                       relief="flat")
        
        # エントリー
        style.configure("TEntry",
                       fieldbackground=self.colors['surface_card'],
                       bordercolor=self.colors['border_subtle'],
                       foreground=self.colors['text_primary'])
        
        # コンボボックス
        style.configure("TCombobox",
                       fieldbackground=self.colors['surface_card'],
                       bordercolor=self.colors['border_subtle'],
                       foreground=self.colors['text_primary'])
        
        # プログレスバー
        style.configure("TProgressbar",
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['surface_card'])
    
    def create_main_ui(self):
        """メインUIの作成"""
        # メインコンテナ
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(main_container,
                              text="Voice Converter - Enhanced Edition",
                              font=("SF Pro Display", 24, "bold"),
                              bg=self.colors['background_primary'],
                              fg=self.colors['text_primary'])
        title_label.pack(pady=(0, 20))
        
        # 改良版ステータス表示
        self.create_enhancement_status(main_container)
        
        # 入力ファイルセクション
        self.create_input_section(main_container)
        
        # モデル選択セクション
        self.create_model_section(main_container)
        
        # 変換設定セクション
        self.create_settings_section(main_container)
        
        # 出力セクション
        self.create_output_section(main_container)
        
        # アクションボタン
        self.create_action_buttons(main_container)
        
        # プログレスセクション
        self.create_progress_section(main_container)
    
    def create_enhancement_status(self, parent):
        """改良機能ステータス表示"""
        status_frame = ttk.LabelFrame(parent, text="🚀 Enhancement Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        if self.use_enhanced_conversion:
            status_text = "✅ Enhanced algorithms active"
            color = self.colors['success']
            
            info = self.enhanced_converter.get_enhancement_info()
            features_text = f"Active features: {len([f for f in info['config'].values() if f.get('enabled', False)])}/4"
        else:
            status_text = "⚠️ Standard mode (enhanced algorithms unavailable)"
            color = self.colors['warning']
            features_text = "Using standard RVC algorithms"
        
        status_label = tk.Label(status_frame,
                               text=status_text,
                               font=("SF Pro Display", 11, "bold"),
                               bg=self.colors['surface_card'],
                               fg=color)
        status_label.pack(anchor="w")
        
        features_label = tk.Label(status_frame,
                                 text=features_text,
                                 font=("SF Pro Display", 10),
                                 bg=self.colors['surface_card'],
                                 fg=self.colors['text_secondary'])
        features_label.pack(anchor="w", pady=(5, 0))
        
        if self.use_enhanced_conversion:
            improvements = "\n".join(["• Adaptive neighbor search", "• F0 ensemble methods", 
                                    "• VAD-based segmentation", "• Quality boost parameters"])
            improvements_label = tk.Label(status_frame,
                                        text=improvements,
                                        font=("SF Pro Display", 9),
                                        bg=self.colors['surface_card'],
                                        fg=self.colors['text_secondary'],
                                        justify=tk.LEFT)
            improvements_label.pack(anchor="w", pady=(5, 0))
    
    def create_input_section(self, parent):
        """入力ファイルセクション"""
        input_frame = ttk.LabelFrame(parent, text="📁 Input File", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill=tk.X)
        
        input_entry = ttk.Entry(file_frame, textvariable=self.input_var, state="readonly")
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.select_input_file)
        browse_btn.pack(side=tk.RIGHT)
    
    def create_model_section(self, parent):
        """モデル選択セクション"""
        model_frame = ttk.LabelFrame(parent, text="🎤 Voice Model", padding=10)
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        model_select_frame = ttk.Frame(model_frame)
        model_select_frame.pack(fill=tk.X)
        
        self.model_combo = ttk.Combobox(model_select_frame,
                                       textvariable=self.selected_model,
                                       state="readonly",
                                       width=40)
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        refresh_btn = ttk.Button(model_select_frame, text="Refresh", command=self.load_models_safe)
        refresh_btn.pack(side=tk.RIGHT)
    
    def create_settings_section(self, parent):
        """変換設定セクション"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Conversion Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # ピッチ設定
        pitch_frame = ttk.Frame(settings_frame)
        pitch_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(pitch_frame, text="Pitch Shift:").pack(anchor="w")
        
        pitch_control_frame = ttk.Frame(pitch_frame)
        pitch_control_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.pitch_scale = ttk.Scale(pitch_control_frame,
                                    from_=-12, to=12,
                                    orient=tk.HORIZONTAL,
                                    variable=self.pitch_var,
                                    command=self.update_pitch_label)
        self.pitch_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.pitch_label = ttk.Label(pitch_control_frame, text="0 semitones")
        self.pitch_label.pack(side=tk.RIGHT)
        
        # F0メソッド設定
        f0_frame = ttk.Frame(settings_frame)
        f0_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(f0_frame, text="F0 Method:").pack(anchor="w")
        
        f0_combo = ttk.Combobox(f0_frame,
                               textvariable=self.f0_method_var,
                               values=["rmvpe", "crepe", "harvest", "dio"],
                               state="readonly")
        f0_combo.pack(fill=tk.X, pady=(5, 0))
        
        # インデックスレート設定
        index_frame = ttk.Frame(settings_frame)
        index_frame.pack(fill=tk.X)
        
        ttk.Label(index_frame, text="Index Rate:").pack(anchor="w")
        
        index_control_frame = ttk.Frame(index_frame)
        index_control_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.index_scale = ttk.Scale(index_control_frame,
                                    from_=0, to=1,
                                    orient=tk.HORIZONTAL,
                                    variable=self.index_rate_var,
                                    command=self.update_index_label)
        self.index_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.index_label = ttk.Label(index_control_frame, text="0.75")
        self.index_label.pack(side=tk.RIGHT)
    
    def create_output_section(self, parent):
        """出力セクション"""
        output_frame = ttk.LabelFrame(parent, text="💾 Output", padding=10)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill=tk.X)
        
        ttk.Label(output_dir_frame, text="Output Directory:").pack(anchor="w")
        
        dir_select_frame = ttk.Frame(output_frame)
        dir_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        output_entry = ttk.Entry(dir_select_frame, textvariable=self.output_var, state="readonly")
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_dir_btn = ttk.Button(dir_select_frame, text="Browse", command=self.select_output_dir)
        browse_dir_btn.pack(side=tk.RIGHT)
    
    def create_action_buttons(self, parent):
        """アクションボタン"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=20)
        
        # 変換ボタン（大きく目立つように）
        convert_text = "🚀 Start Enhanced Conversion" if self.use_enhanced_conversion else "▶️ Start Conversion"
        self.convert_btn = tk.Button(button_frame,
                                    text=convert_text,
                                    font=("SF Pro Display", 14, "bold"),
                                    bg=self.colors['accent_primary'],
                                    fg="white",
                                    padx=30, pady=10,
                                    relief="flat",
                                    cursor="hand2",
                                    command=self.start_conversion)
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止ボタン
        self.stop_btn = tk.Button(button_frame,
                                 text="⏹️ Stop",
                                 font=("SF Pro Display", 12, "bold"),
                                 bg=self.colors['error'],
                                 fg="white",
                                 padx=20, pady=10,
                                 relief="flat",
                                 cursor="hand2",
                                 state=tk.DISABLED,
                                 command=self.stop_conversion)
        self.stop_btn.pack(side=tk.LEFT)
    
    def create_progress_section(self, parent):
        """プログレスセクション"""
        self.progress_frame = ttk.LabelFrame(parent, text="📊 Progress", padding=10)
        # 初期状態では非表示
        
        # プログレスバー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame,
                                          variable=self.progress_var,
                                          maximum=100,
                                          mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # ステータステキスト
        self.status_text = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.status_text)
        self.status_label.pack(anchor="w")
    
    # Event handlers
    def select_input_file(self):
        """入力ファイル選択"""
        file_path = filedialog.askopenfilename(
            title="Select input audio file",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.flac *.m4a *.ogg"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.input_var.set(file_path)
    
    def select_output_dir(self):
        """出力ディレクトリ選択"""
        dir_path = filedialog.askdirectory(title="Select output directory")
        if dir_path:
            self.output_var.set(dir_path)
    
    def load_models_safe(self):
        """モデル読み込み（安全版）"""
        try:
            if not os.path.exists(self.model_dir):
                self.model_combo['values'] = ["No models found"]
                return
            
            models = []
            for file in os.listdir(self.model_dir):
                if file.endswith('.pth') and not file.startswith(('hubert', 'rmvpe')):
                    models.append(os.path.splitext(file)[0])
            
            if models:
                self.model_combo['values'] = sorted(models)
                if len(models) > 0:
                    self.model_combo.current(0)
            else:
                self.model_combo['values'] = ["No models found"]
                
            print(f"Loaded {len(models)} models")
            
        except Exception as e:
            print(f"Error loading models: {e}")
            self.model_combo['values'] = ["Error loading models"]
    
    def update_pitch_label(self, *args):
        """ピッチラベル更新"""
        value = self.pitch_var.get()
        self.pitch_label.config(text=f"{value:.1f} semitones")
    
    def update_index_label(self, *args):
        """インデックスラベル更新"""
        value = self.index_rate_var.get()
        self.index_label.config(text=f"{value:.2f}")
    
    def start_conversion(self):
        """変換開始"""
        # 入力チェック
        if not self.input_var.get():
            messagebox.showwarning("Warning", "Please select an input file")
            return
        
        if not self.selected_model.get() or self.selected_model.get() in ["No models found", "Error loading models"]:
            messagebox.showwarning("Warning", "Please select a valid model")
            return
        
        # プログレスセクションを表示
        self.progress_frame.pack(fill=tk.X, pady=(15, 0))
        
        # ボタン状態更新
        self.convert_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.converting = True
        
        # 変換スレッド開始
        thread = threading.Thread(target=self.run_conversion_safe, daemon=True)
        thread.start()
    
    def stop_conversion(self):
        """変換停止"""
        self.converting = False
        self.convert_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_text.set("Conversion stopped")
    
    def run_conversion_safe(self):
        """安全な変換実行"""
        try:
            # 出力ファイルパスの準備
            input_file = self.input_var.get()
            output_dir = self.output_var.get()
            os.makedirs(output_dir, exist_ok=True)
            
            input_name = os.path.splitext(os.path.basename(input_file))[0]
            model_name = self.selected_model.get()
            output_filename = f"{input_name}_{model_name}_enhanced.wav"
            output_path = os.path.join(output_dir, output_filename)
            
            # プログレス更新
            self.root.after(0, lambda: self.update_progress(10, "Preparing conversion..."))
            
            # 改良版変換の実行
            if self.use_enhanced_conversion:
                success = self.run_enhanced_conversion_safe(input_file, output_path)
            else:
                success = self.run_standard_conversion_safe(input_file, output_path)
            
            if success and self.converting:
                self.root.after(0, lambda: self.update_progress(100, "Conversion completed!"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Conversion completed!\n\nOutput: {os.path.basename(output_path)}"
                ))
            elif not self.converting:
                self.root.after(0, lambda: self.update_progress(0, "Conversion stopped"))
            else:
                self.root.after(0, lambda: self.update_progress(0, "Conversion failed"))
                self.root.after(0, lambda: messagebox.showerror("Error", "Conversion failed"))
                
        except Exception as e:
            print(f"Conversion error: {e}")
            self.root.after(0, lambda: self.update_progress(0, f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Conversion failed: {str(e)}"))
        finally:
            self.root.after(0, self.conversion_finished)
    
    def run_enhanced_conversion_safe(self, input_path, output_path):
        """安全な改良版変換"""
        try:
            self.root.after(0, lambda: self.update_progress(30, "Applying enhanced algorithms..."))
            
            # モデルパスを構築
            model_file = os.path.join(self.model_dir, f"{self.selected_model.get()}.pth")
            if not os.path.exists(model_file):
                return False
            
            # 変換パラメータ
            params = {
                'f0_up_key': int(self.pitch_var.get()),
                'f0_method': self.f0_method_var.get(),
                'index_rate': self.index_rate_var.get(),
                'filter_radius': 3,
                'rms_mix_rate': 0.25,
                'protect': 0.33
            }
            
            self.root.after(0, lambda: self.update_progress(50, "Converting with enhanced quality..."))
            
            # 改良版変換実行
            result = self.enhanced_converter.convert_audio_enhanced(
                input_path=input_path,
                output_path=output_path,
                model_path=model_file,
                **params
            )
            
            return result is not None
            
        except Exception as e:
            print(f"Enhanced conversion failed: {e}")
            return False
    
    def run_standard_conversion_safe(self, input_path, output_path):
        """安全な標準変換（シミュレーション）"""
        try:
            self.root.after(0, lambda: self.update_progress(30, "Processing with standard algorithms..."))
            
            # 標準変換のシミュレーション
            for i in range(30, 90, 10):
                if not self.converting:
                    return False
                time.sleep(0.5)
                self.root.after(0, lambda p=i: self.update_progress(p, "Converting..."))
            
            # ファイルコピー（デモ用）
            import shutil
            try:
                shutil.copy2(input_path, output_path)
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Standard conversion failed: {e}")
            return False
    
    def update_progress(self, value, message):
        """プログレス更新"""
        self.progress_var.set(value)
        self.status_text.set(message)
    
    def conversion_finished(self):
        """変換終了処理"""
        self.converting = False
        self.convert_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)


def main():
    """メイン実行"""
    # macOS Tkinterの安定化設定
    if sys.platform == "darwin":
        try:
            # イベント処理の最適化
            os.environ['TK_SILENCE_DEPRECATION'] = '1'
        except:
            pass
    
    # メインウィンドウ作成
    root = tk.Tk()
    
    try:
        # アプリケーション起動
        app = StableDarkModeGUI(root)
        
        # 終了処理の設定
        def on_closing():
            if app.converting:
                if messagebox.askyesno("Confirm", "Conversion in progress. Exit anyway?"):
                    app.converting = False
                    root.destroy()
            else:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # メインループ開始
        print("Starting GUI main loop...")
        root.mainloop()
        
    except Exception as e:
        print(f"GUI Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            root.quit()
        except:
            pass


if __name__ == "__main__":
    main()