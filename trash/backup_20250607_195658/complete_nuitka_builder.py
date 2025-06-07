#!/usr/bin/env python3
"""
Complete RVC Nuitka Builder
完全版RVCアプリのNuitkaビルドシステム
"""
import subprocess
import sys
import os
import shutil
import time
from pathlib import Path

class CompleteNuitkaBuilder:
    """完全版Nuitkaビルダー"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.build_dir = self.project_root / "complete_build"
        self.output_dir = self.project_root / "dist_complete"
        
        # システムPython確認
        self.system_python = self.find_system_python()
        if not self.system_python:
            raise RuntimeError("システムPythonが見つかりません")
    
    def find_system_python(self):
        """システムPythonを検出"""
        candidates = [
            "/opt/homebrew/bin/python3",
            "/usr/bin/python3",
            "/usr/local/bin/python3"
        ]
        
        for python_path in candidates:
            if Path(python_path).exists():
                try:
                    # tkinter確認
                    result = subprocess.run([
                        python_path, "-c", "import tkinter; print('OK')"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ システムPython発見: {python_path}")
                        return python_path
                except:
                    continue
        
        return None
    
    def install_nuitka_system(self):
        """システムPython環境にNuitkaをインストール"""
        print("🔧 システムPython環境にNuitka準備中...")
        
        try:
            # pip確認
            result = subprocess.run([
                self.system_python, "-m", "pip", "--version"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ pipが利用できません")
                return False
            
            # Nuitka確認・インストール
            result = subprocess.run([
                self.system_python, "-c", "import nuitka; print('installed')"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("📦 Nuitkaインストール中...")
                install_result = subprocess.run([
                    self.system_python, "-m", "pip", "install", "nuitka"
                ], capture_output=True, text=True)
                
                if install_result.returncode != 0:
                    print(f"❌ Nuitkaインストール失敗: {install_result.stderr}")
                    return False
                else:
                    print("✅ Nuitkaインストール完了")
            else:
                print("✅ Nuitka既にインストール済み")
            
            return True
            
        except Exception as e:
            print(f"❌ システムPython Nuitka準備エラー: {e}")
            return False
    
    def create_standalone_gui(self):
        """完全独立版GUIファイルの作成"""
        print("📝 完全独立版GUIファイル作成中...")
        
        standalone_gui_content = '''#!/usr/bin/env python3
"""
RVC Voice Converter - Complete Standalone Edition
完全独立版音声変換アプリケーション
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import json
import time
from pathlib import Path

class RVCCompleteApp:
    """完全版RVC音声変換アプリケーション"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 RVC Voice Converter - Complete Edition")
        self.root.geometry("1200x800")
        
        # ダークモードスタイル
        self.setup_style()
        self.setup_ui()
        
        # Poetry環境パス
        self.poetry_available = self.check_poetry_environment()
        
    def check_poetry_environment(self):
        """Poetry環境の確認"""
        try:
            result = subprocess.run(['poetry', '--version'], 
                                   capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def setup_style(self):
        """ダークモードスタイル設定"""
        self.colors = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d',
            'surface': '#3d3d3d',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#007acc',
            'success': '#4CAF50',
            'warning': '#ff9800',
            'error': '#f44336'
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        # tkinterスタイル設定
        style = ttk.Style()
        style.theme_use('default')
        
        # ダークモード設定
        style.configure('TLabel', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'])
        style.configure('TFrame',
                       background=self.colors['bg_primary'])
        style.configure('TButton',
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'])
    
    def setup_ui(self):
        """UI構築"""
        # メインコンテナ
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title = tk.Label(main_frame,
                        text="🎤 RVC Voice Converter - Complete Edition",
                        font=('Arial', 20, 'bold'),
                        bg=self.colors['bg_primary'],
                        fg=self.colors['text_primary'])
        title.pack(pady=(0, 20))
        
        # ステータス
        self.status_frame = tk.Frame(main_frame, bg=self.colors['surface'])
        self.status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = tk.Label(self.status_frame,
                                    text=f"Poetry環境: {'✅ 利用可能' if self.poetry_available else '❌ 利用不可'}",
                                    font=('Arial', 12),
                                    bg=self.colors['surface'],
                                    fg=self.colors['success'] if self.poetry_available else self.colors['error'])
        self.status_label.pack(pady=10)
        
        # ファイル選択
        self.setup_file_section(main_frame)
        
        # 変換設定
        self.setup_settings_section(main_frame)
        
        # 変換ボタン
        self.setup_conversion_section(main_frame)
        
        # ログ表示
        self.setup_log_section(main_frame)
    
    def setup_file_section(self, parent):
        """ファイル選択セクション"""
        file_frame = tk.LabelFrame(parent,
                                  text="ファイル選択",
                                  font=('Arial', 14, 'bold'),
                                  bg=self.colors['bg_primary'],
                                  fg=self.colors['text_primary'])
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 入力ファイル
        input_frame = tk.Frame(file_frame, bg=self.colors['bg_primary'])
        input_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(input_frame, text="入力音声ファイル:",
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=('Arial', 12)).pack(anchor='w')
        
        input_entry_frame = tk.Frame(input_frame, bg=self.colors['bg_primary'])
        input_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.input_var = tk.StringVar()
        input_entry = tk.Entry(input_entry_frame,
                              textvariable=self.input_var,
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_primary'],
                              font=('Arial', 11),
                              insertbackground=self.colors['text_primary'])
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        input_btn = tk.Button(input_entry_frame,
                             text="参照",
                             command=self.browse_input,
                             bg=self.colors['accent'],
                             fg='white',
                             font=('Arial', 11))
        input_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 出力ディレクトリ
        output_frame = tk.Frame(file_frame, bg=self.colors['bg_primary'])
        output_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(output_frame, text="出力ディレクトリ:",
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=('Arial', 12)).pack(anchor='w')
        
        output_entry_frame = tk.Frame(output_frame, bg=self.colors['bg_primary'])
        output_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_var = tk.StringVar(value="enhanced_output")
        output_entry = tk.Entry(output_entry_frame,
                               textvariable=self.output_var,
                               bg=self.colors['bg_secondary'],
                               fg=self.colors['text_primary'],
                               font=('Arial', 11),
                               insertbackground=self.colors['text_primary'])
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        output_btn = tk.Button(output_entry_frame,
                              text="参照",
                              command=self.browse_output,
                              bg=self.colors['accent'],
                              fg='white',
                              font=('Arial', 11))
        output_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    def setup_settings_section(self, parent):
        """変換設定セクション"""
        settings_frame = tk.LabelFrame(parent,
                                      text="変換設定",
                                      font=('Arial', 14, 'bold'),
                                      bg=self.colors['bg_primary'],
                                      fg=self.colors['text_primary'])
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 設定グリッド
        grid_frame = tk.Frame(settings_frame, bg=self.colors['bg_primary'])
        grid_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # ピッチシフト
        pitch_frame = tk.Frame(grid_frame, bg=self.colors['bg_primary'])
        pitch_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(pitch_frame, text="ピッチシフト:",
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=('Arial', 12)).pack(side=tk.LEFT)
        
        self.pitch_var = tk.IntVar(value=0)
        pitch_scale = tk.Scale(pitch_frame, from_=-12, to=12,
                              variable=self.pitch_var,
                              orient=tk.HORIZONTAL,
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_primary'],
                              highlightthickness=0,
                              length=300)
        pitch_scale.pack(side=tk.RIGHT)
    
    def setup_conversion_section(self, parent):
        """変換セクション"""
        conv_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        conv_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 変換ボタン
        self.convert_btn = tk.Button(conv_frame,
                                    text="🎤 音声変換開始",
                                    command=self.start_conversion,
                                    bg=self.colors['success'],
                                    fg='white',
                                    font=('Arial', 16, 'bold'),
                                    padx=40, pady=15)
        self.convert_btn.pack()
        
        # プログレスバー
        self.progress = ttk.Progressbar(conv_frame,
                                       mode='indeterminate',
                                       length=500)
        self.progress.pack(pady=(15, 0))
        
        # プログレステキスト
        self.progress_text = tk.Label(conv_frame,
                                     text="",
                                     bg=self.colors['bg_primary'],
                                     fg=self.colors['text_secondary'],
                                     font=('Arial', 11))
        self.progress_text.pack(pady=(5, 0))
    
    def setup_log_section(self, parent):
        """ログセクション"""
        log_frame = tk.LabelFrame(parent,
                                 text="変換ログ",
                                 font=('Arial', 14, 'bold'),
                                 bg=self.colors['bg_primary'],
                                 fg=self.colors['text_primary'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # ログテキスト
        log_container = tk.Frame(log_frame, bg=self.colors['bg_primary'])
        log_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.log_text = tk.Text(log_container,
                               bg=self.colors['bg_secondary'],
                               fg=self.colors['text_primary'],
                               font=('Courier', 10),
                               wrap=tk.WORD,
                               insertbackground=self.colors['text_primary'])
        
        log_scroll = tk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scroll.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def browse_input(self):
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
            self.log(f"📁 入力ファイル選択: {Path(filename).name}")
    
    def browse_output(self):
        """出力ディレクトリ選択"""
        dirname = filedialog.askdirectory(title="出力ディレクトリを選択")
        if dirname:
            self.output_var.set(dirname)
            self.log(f"📁 出力ディレクトリ選択: {dirname}")
    
    def log(self, message):
        """ログメッセージ追加"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\\n"
        
        def update():
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, update)
        else:
            update()
    
    def start_conversion(self):
        """音声変換開始"""
        input_file = self.input_var.get()
        output_dir = self.output_var.get()
        
        if not input_file:
            messagebox.showwarning("警告", "入力ファイルを選択してください")
            return
        
        if not Path(input_file).exists():
            messagebox.showerror("エラー", "入力ファイルが見つかりません")
            return
        
        if not output_dir:
            messagebox.showwarning("警告", "出力ディレクトリを指定してください")
            return
        
        if not self.poetry_available:
            messagebox.showerror("エラー", "Poetry環境が利用できません")
            return
        
        # UI更新
        self.convert_btn.config(state='disabled', text="🔄 変換中...")
        self.progress.start()
        self.progress_text.config(text="音声変換を実行中...")
        
        # 変換スレッド開始
        def conversion_thread():
            try:
                # 出力ファイル名生成
                input_path = Path(input_file)
                output_path = Path(output_dir) / f"{input_path.stem}_converted.wav"
                
                self.log("🎤 Enhanced Voice Converter音声変換開始")
                self.log(f"   入力: {input_path.name}")
                self.log(f"   出力: {output_path.name}")
                self.log(f"   ピッチ: {self.pitch_var.get()}")
                
                # Poetry環境での変換実行
                conversion_script = f'''
from enhanced_voice_converter import EnhancedVoiceConverter
from pathlib import Path

try:
    # Enhanced Voice Converter初期化
    converter = EnhancedVoiceConverter()
    
    # 利用可能なモデル確認
    models = converter.list_available_models()
    if not models:
        print("ERROR: No models available")
        exit(1)
    
    # 最初のモデルを使用
    model = models[0]
    print(f"SUCCESS: Using model: {{model['name']}}")
    
    # モデルロード
    load_result = converter.load_model(model['path'], model.get('index_path'))
    if not load_result:
        print(f"ERROR: Failed to load model")
        exit(1)
    
    print("SUCCESS: Model loaded successfully")
    
    # 音声変換実行
    result = converter.convert_audio(
        input_path="{input_file}",
        output_path="{output_path}",
        f0_up_key={self.pitch_var.get()},
        index_rate=0.7,
        protect=0.33,
        f0_method="harvest"
    )
    
    print(f"SUCCESS: Conversion completed: {{result}}")
    
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
    exit(1)
'''
                
                # Poetry環境で実行
                cmd = ['poetry', 'run', 'python', '-c', conversion_script]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
                
                if result.returncode == 0:
                    # 成功
                    if output_path.exists():
                        size_mb = output_path.stat().st_size / 1024 / 1024
                        self.log(f"✅ 変換完了! ({size_mb:.1f}MB)")
                        self.log(f"📁 出力: {output_path}")
                        
                        self.root.after(0, lambda: messagebox.showinfo(
                            "変換完了",
                            f"音声変換が完了しました!\\n\\n"
                            f"出力ファイル: {output_path.name}\\n"
                            f"サイズ: {size_mb:.1f}MB"
                        ))
                    else:
                        self.log("⚠️ 変換完了しましたが、出力ファイルが見つかりません")
                else:
                    # エラー
                    error_msg = result.stderr or result.stdout
                    self.log(f"❌ 変換エラー: {error_msg}")
                    self.root.after(0, lambda: messagebox.showerror(
                        "変換エラー",
                        f"音声変換に失敗しました\\n\\n{error_msg}"
                    ))
                
            except Exception as e:
                self.log(f"❌ 変換例外: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "システムエラー",
                    f"変換中にエラーが発生しました\\n\\n{e}"
                ))
            
            finally:
                # UI復元
                self.root.after(0, lambda: self.convert_btn.config(state='normal', text="🎤 音声変換開始"))
                self.root.after(0, self.progress.stop)
                self.root.after(0, lambda: self.progress_text.config(text=""))
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()

def main():
    """メイン関数"""
    app = RVCCompleteApp()
    app.run()

if __name__ == "__main__":
    main()
'''
        
        standalone_path = self.project_root / "rvc_complete_standalone.py"
        with open(standalone_path, 'w', encoding='utf-8') as f:
            f.write(standalone_gui_content)
        
        print(f"✅ 完全独立版GUIファイル作成: {standalone_path}")
        return standalone_path
    
    def build_complete_app(self, gui_file):
        """完全版アプリのNuitkaビルド"""
        print("🔧 完全版RVCアプリNuitkaビルド開始...")
        
        # 出力ディレクトリ準備
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir()
        
        # Nuitkaコマンド構築
        nuitka_cmd = [
            self.system_python, "-m", "nuitka",
            "--standalone",
            "--macos-create-app-bundle",
            f"--output-dir={self.output_dir}",
            "--include-data-dir=model_dir=model_dir",
            "--include-data-dir=enhanced_output=enhanced_output",
            "--include-data-files=enhanced_voice_converter.py=enhanced_voice_converter.py",
            "--include-data-files=rvc=rvc",
            "--include-data-files=pyproject.toml=pyproject.toml",
            "--include-data-files=poetry.lock=poetry.lock",
            "--macos-app-name=RVC Voice Converter Complete",
            "--macos-app-version=1.0.0",
            "--macos-app-protected-resource=microphone:RVC音声変換のためマイクアクセス",
            "--no-source-listing",
            "--remove-output",
            str(gui_file)
        ]
        
        print(f"📝 Nuitkaコマンド: {' '.join(nuitka_cmd[:5])}...")
        
        # ビルド実行
        start_time = time.time()
        result = subprocess.run(nuitka_cmd, capture_output=True, text=True)
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"✅ Nuitkaビルド成功! (実行時間: {end_time - start_time:.1f}秒)")
            
            # 生成されたアプリの確認
            app_path = self.output_dir / "RVC Voice Converter Complete.app"
            if app_path.exists():
                print(f"📱 完全版アプリ生成: {app_path}")
                
                # アプリサイズ確認
                try:
                    size_result = subprocess.run(['du', '-sh', str(app_path)], 
                                                capture_output=True, text=True)
                    if size_result.returncode == 0:
                        app_size = size_result.stdout.split()[0]
                        print(f"📊 アプリサイズ: {app_size}")
                except:
                    pass
                
                return app_path
            else:
                print(f"❌ 完全版アプリが見つかりません")
                return None
        else:
            print(f"❌ Nuitkaビルド失敗:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return None
    
    def create_complete_dmg(self, app_path):
        """完全版DMGの作成"""
        if not app_path or not app_path.exists():
            print("❌ アプリパスが無効なため、DMG作成をスキップ")
            return None
        
        print("💿 完全版DMG作成中...")
        
        dmg_name = "RVC_Voice_Converter_Complete.dmg"
        dmg_path = self.project_root / dmg_name
        
        # 既存DMGを削除
        if dmg_path.exists():
            dmg_path.unlink()
        
        try:
            # 一時ディレクトリ作成
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # アプリをコピー
                temp_app = temp_path / app_path.name
                shutil.copytree(app_path, temp_app)
                
                # Applicationsリンク作成
                applications_link = temp_path / "Applications"
                applications_link.symlink_to("/Applications")
                
                # README作成
                readme_content = f"""RVC Voice Converter Complete Edition

インストール手順:
1. {app_path.name} を Applications フォルダにドラッグ&ドロップ
2. アプリケーションフォルダから起動
3. 初回起動時はセキュリティ設定で許可が必要な場合があります

特徴:
- Enhanced Voice Converter統合
- PyTorch、librosa、fairseq完全対応
- ダークモードGUI
- Apple Silicon MPS最適化

注意:
- Poetry環境が必要です（音声変換処理用）
- モデルファイルは自動検出されます

© 2024 RVC Voice Converter Complete Edition
"""
                readme_path = temp_path / "README.txt"
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                
                # DMG作成
                create_cmd = [
                    "hdiutil", "create",
                    "-srcfolder", str(temp_path),
                    "-volname", "RVC Voice Converter Complete",
                    "-fs", "HFS+",
                    "-format", "UDZO",
                    "-imagekey", "zlib-level=9",
                    str(dmg_path)
                ]
                
                result = subprocess.run(create_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ 完全版DMG作成完了: {dmg_path}")
                    
                    # DMGサイズ確認
                    if dmg_path.exists():
                        size_mb = dmg_path.stat().st_size / 1024 / 1024
                        print(f"📊 DMGサイズ: {size_mb:.1f}MB")
                    
                    return dmg_path
                else:
                    print(f"❌ DMG作成失敗: {result.stderr}")
                    return None
                    
        except Exception as e:
            print(f"❌ DMG作成エラー: {e}")
            return None
    
    def build_complete_edition(self):
        """完全版ビルドプロセス"""
        print("🚀 RVC Voice Converter Complete Edition ビルド開始")
        print("=" * 70)
        
        steps = [
            ("システムPython Nuitka準備", self.install_nuitka_system),
            ("完全独立版GUI作成", self.create_standalone_gui),
        ]
        
        results = {}
        gui_file = None
        
        for step_name, step_func in steps:
            print(f"\\n{'='*20} {step_name} {'='*20}")
            
            try:
                result = step_func()
                
                if step_name == "完全独立版GUI作成":
                    gui_file = result
                    result = gui_file is not None
                
                results[step_name] = result
                
                if result:
                    print(f"✅ {step_name}: 成功")
                else:
                    print(f"❌ {step_name}: 失敗")
                    break
                    
            except Exception as e:
                print(f"❌ {step_name}: エラー - {e}")
                results[step_name] = False
                break
        
        # Nuitkaビルド実行
        if gui_file and all(results.values()):
            print(f"\\n{'='*20} 完全版Nuitkaビルド {'='*20}")
            
            try:
                app_path = self.build_complete_app(gui_file)
                results["Nuitkaビルド"] = app_path is not None
                
                if app_path:
                    print(f"✅ Nuitkaビルド: 成功")
                    
                    # DMG作成
                    print(f"\\n{'='*20} 完全版DMG作成 {'='*20}")
                    dmg_path = self.create_complete_dmg(app_path)
                    results["DMG作成"] = dmg_path is not None
                    
                    if dmg_path:
                        print(f"✅ DMG作成: 成功")
                    else:
                        print(f"❌ DMG作成: 失敗")
                        
                else:
                    print(f"❌ Nuitkaビルド: 失敗")
                    
            except Exception as e:
                print(f"❌ Nuitkaビルド: エラー - {e}")
                results["Nuitkaビルド"] = False
        
        # 最終結果
        print(f"\\n📊 完全版ビルド結果:")
        print("=" * 70)
        
        success_count = sum(results.values())
        total_count = len(results)
        
        for step_name, result in results.items():
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"  {step_name:25}: {status}")
        
        print(f"\\n総合結果: {success_count}/{total_count} 成功")
        
        if success_count == total_count:
            print(f"🎉 RVC Voice Converter Complete Edition ビルド完了！")
            print(f"📱 完全版アプリ: dist_complete/")
            print(f"💿 配布用DMG: RVC_Voice_Converter_Complete.dmg")
        else:
            print(f"⚠️ 一部ステップが失敗しました")
        
        return success_count == total_count

def main():
    """メイン実行関数"""
    try:
        builder = CompleteNuitkaBuilder()
        success = builder.build_complete_edition()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ ビルダー初期化エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()