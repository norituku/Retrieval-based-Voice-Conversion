#!/usr/bin/env python3
"""
RVC Dark Mode GUI - Enhanced Exact Edition
gui_dark_mode.pyの完全なUI再現版 + 改良機能 + セグフォルト対策
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import subprocess
import threading
import math
import time
from pathlib import Path
from datetime import datetime

# RVC設定をインポート（存在する場合）
try:
    from rvc_config import POETRY_PYTHON_PATH, RVC_MODULE
    USE_HARDCODED_PATH = True
except ImportError:
    USE_HARDCODED_PATH = False

# 改良版音声変換のインポート
try:
    from enhanced_converter_simple import SimpleEnhancedConverter
    ENHANCED_CONVERTER_AVAILABLE = True
    print("✅ Simple Enhanced Voice Converter loaded")
except ImportError as e:
    ENHANCED_CONVERTER_AVAILABLE = False
    print(f"⚠️ Enhanced Voice Converter not available: {e}")

class DarkModeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter")
        
        # セグフォルト対策: 安全モードフラグ
        self.safe_mode = True  # ホバーエフェクトを制限
        
        # ダークモードデザイントークン（オリジナルと完全一致）
        self.design_tokens = {
            # カラーパレット - 視認性を向上
            'colors': {
                # 背景階層
                'background_primary': '#0F0F10',    # わずかに青みがかった黒
                'background_secondary': '#1A1A1C',   # パネルとカード
                'background_tertiary': '#252528',    # 上昇したサーフェス
                'background_elevated': '#2F2F33',    # 最高の標高
                
                # サーフェスカラー
                'surface_card': '#1C1C1F',
                'surface_overlay': '#26262A',
                'surface_popover': '#2A2A2E',
                'surface_sidebar': '#141416',
                
                # テキストカラー（コントラストを改善）
                'text_primary': '#FFFFFF',
                'text_secondary': '#B8B8B8',
                'text_tertiary': '#808080',
                'text_disabled': '#505050',
                
                # ブランドカラー - 音楽/オーディオテーマ（より鮮やか）
                'accent_primary': '#5A9FFF',     # 明るい青
                'accent_secondary': '#8B6FFF',   # 紫
                'accent_tertiary': '#FF7A7A',    # コーラルレッド
                'accent_quaternary': '#5EDDD4',  # ティール
                
                # システムセマンティックカラー
                'success': '#52E88C',
                'warning': '#FFD23F',
                'error': '#FF6B6B',
                'info': '#6BB6FF',
                
                # インタラクティブ状態
                'hover': '#2A2A2E',
                'pressed': '#1F1F23',
                'focus': '#5A9FFF',
                'selection': '#5A9FFF33',
                
                # 分割線とボーダー
                'divider': '#2A2A2E',
                'border_subtle': '#2F2F33',
                'border_strong': '#505055',
            },
            
            # タイポグラフィ - SF Pro for macOS（よりコンパクト）
            'typography': {
                'large_title': {'size': 28, 'weight': 'normal'},
                'title1': {'size': 22, 'weight': 'normal'},
                'title2': {'size': 18, 'weight': 'normal'},
                'title3': {'size': 16, 'weight': 'normal'},
                'headline': {'size': 14, 'weight': 'bold'},
                'body': {'size': 13, 'weight': 'normal'},
                'body_bold': {'size': 13, 'weight': 'bold'},
                'callout': {'size': 12, 'weight': 'normal'},
                'subheadline': {'size': 11, 'weight': 'normal'},
                'footnote': {'size': 10, 'weight': 'normal'},
                'caption1': {'size': 9, 'weight': 'normal'},
                'caption2': {'size': 9, 'weight': 'normal'},
            },
            
            # スペーシング - 超コンパクトグリッドシステム
            'spacing': {
                'xxxs': 1,
                'xxs': 2,
                'xs': 3,
                'sm': 4,
                'md': 5,
                'lg': 6,
                'xl': 8,
                'xxl': 10,
                'xxxl': 12,
                'xxxxl': 16,
            },
            
            # コーナー半径
            'radius': {
                'tiny': 2,
                'small': 4,
                'medium': 6,
                'large': 8,
                'extra_large': 10,
                'round': 999,
            },
            
            # レイアウト（コンパクト設定）
            'layout': {
                'sidebar_width': 200,
                'min_window_width': 900,
                'min_window_height': 500,
                'toolbar_height': 35,
                'max_content_width': 650,  # メインコンテンツの最大幅
            }
        }
        
        self.colors = self.design_tokens['colors']
        
        # フォントファミリーの定義
        self.fonts = {
            'family': 'SF Pro Display',
            'mono': 'SF Mono'
        }
        
        # 変数の初期化（setup_app_directories()より前に実行）
        self.model_info = {}
        self.selected_model = tk.StringVar()
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.output_filename_var = tk.StringVar()  # 出力ファイル名用の変数
        self.is_manual_filename = False  # ユーザーが手動でファイル名を入力したかを追跡
        self.model_dir_var = tk.StringVar()  # モデルディレクトリ用の変数
        self.pitch_var = tk.IntVar(value=0)
        self.f0_method_var = tk.StringVar(value="rmvpe")  # 最高品質
        self.index_rate_var = tk.DoubleVar(value=1.0)     # 最大インデックス使用
        self.filter_radius_var = tk.IntVar(value=3)       # 推奨値
        self.rms_mix_rate_var = tk.DoubleVar(value=0.25)  # 推奨値
        self.protect_var = tk.DoubleVar(value=0.33)       # 推奨値
        
        # 変換制御
        self.converting = False
        self.conversion_thread = None
        
        # アプリケーション設定
        self.setup_app_directories()
        
        # Enhanced Converter初期化
        self.init_enhanced_converter()
        
        # カスタムスタイル設定
        self.setup_styles()
        
        # ウィンドウ設定
        self.setup_window()
        
        # UI構築
        self.create_ui()
        
        # モデル読み込み
        self.load_models()
        
    def setup_app_directories(self):
        """アプリケーションディレクトリの設定"""
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            if exe_dir.endswith('/MacOS'):
                self.base_dir = os.path.join(os.path.dirname(exe_dir), 'Resources')
            else:
                self.base_dir = exe_dir
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            
        # 設定ファイルの読み込み
        self.settings_file = os.path.join(self.base_dir, "gui_settings.json")
        self.load_settings()
        
        # デフォルトのモデルディレクトリ
        default_model_dir = os.path.join(self.base_dir, "model_dir")
        if not self.model_dir_var.get():
            self.model_dir_var.set(default_model_dir)
            
        self.model_dir = self.model_dir_var.get()
        self.config_dir = os.path.join(self.base_dir, "configs")
        
    def load_settings(self):
        """設定ファイルの読み込み"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.model_dir_var.set(settings.get('model_directory', ''))
        except Exception as e:
            print(f"Settings load error: {e}")
            
    def save_settings(self):
        """設定ファイルの保存"""
        try:
            settings = {
                'model_directory': self.model_dir_var.get()
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Settings save error: {e}")
    
    def init_enhanced_converter(self):
        """改良版音声変換システムの初期化"""
        self.enhanced_converter = None
        self.use_enhanced_conversion = False
        
        if ENHANCED_CONVERTER_AVAILABLE:
            try:
                self.enhanced_converter = SimpleEnhancedConverter(
                    model_dir=self.model_dir or "model_dir",
                    output_dir="enhanced_output"
                )
                self.use_enhanced_conversion = True
                print("✅ Enhanced conversion enabled")
            except Exception as e:
                print(f"❌ Enhanced converter initialization failed: {e}")
                self.use_enhanced_conversion = False
    
    def setup_styles(self):
        """カスタムスタイルの設定"""
        style = ttk.Style()
        
        # ダークテーマベース
        style.theme_use('clam')
        
        # 全体の設定
        style.configure('.',
                       background=self.colors['background_primary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       focuscolor='none')
        
        # フレーム
        style.configure('TFrame',
                       background=self.colors['background_primary'],
                       borderwidth=0)
        
        # ラベル
        style.configure('TLabel',
                       background=self.colors['background_primary'],
                       foreground=self.colors['text_primary'])
        
        # プログレスバー（オリジナルと同じ）
        style.configure('TProgressbar',
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['background_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent_primary'],
                       darkcolor=self.colors['accent_primary'])
    
    def setup_window(self):
        """ウィンドウの設定"""
        self.root.configure(bg=self.colors['background_primary'])
        
        # アイコン設定（存在する場合）
        icon_path = os.path.join(self.base_dir, 'icon.png')
        if os.path.exists(icon_path):
            try:
                photo = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, photo)
            except:
                pass
        
        # ウィンドウサイズとポジション
        window_width = 900
        window_height = 700
        
        # 画面中央に配置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.minsize(self.design_tokens['layout']['min_window_width'], 
                         self.design_tokens['layout']['min_window_height'])
    
    def create_ui(self):
        """メインUI構築（オリジナルのレイアウトを完全再現）"""
        # メインコンテナ
        main_container = tk.Frame(self.root, bg=self.colors['background_primary'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ツールバー（上部）
        self.create_toolbar(main_container)
        
        # コンテンツエリア
        content_area = tk.Frame(main_container, bg=self.colors['background_primary'])
        content_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 2カラムレイアウト
        # 左側: モデル選択
        left_column = tk.Frame(content_area, bg=self.colors['background_primary'], width=350)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        left_column.pack_propagate(False)
        
        # 右側: 変換設定
        right_column = tk.Frame(content_area, bg=self.colors['background_primary'])
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 左カラムコンテンツ
        self.create_model_section(left_column)
        
        # 右カラムコンテンツ
        self.create_conversion_section(right_column)
    
    def create_toolbar(self, parent):
        """ツールバー作成（オリジナルと同じ）"""
        toolbar = tk.Frame(parent, bg=self.colors['background_secondary'], 
                          height=self.design_tokens['layout']['toolbar_height'])
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        # ツールバー内容
        toolbar_content = tk.Frame(toolbar, bg=self.colors['background_secondary'])
        toolbar_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # タイトル
        title_label = tk.Label(toolbar_content, 
                             text="Voice Converter",
                             font=(self.fonts['family'], 16, 'bold'),
                             bg=self.colors['background_secondary'],
                             fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)
        
        # Enhanced状態表示
        if self.use_enhanced_conversion:
            enhanced_label = tk.Label(toolbar_content,
                                    text="Enhanced Mode",
                                    font=(self.fonts['family'], 10),
                                    bg=self.colors['background_secondary'],
                                    fg=self.colors['success'])
            enhanced_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_model_section(self, parent):
        """モデル選択セクション（左側）"""
        # モデル選択カード
        model_card = self.create_card(parent, "Voice Models")
        
        # モデルディレクトリ設定
        dir_frame = tk.Frame(model_card, bg=self.colors['surface_card'])
        dir_frame.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        dir_label = tk.Label(dir_frame, 
                           text="Model Directory",
                           font=(self.fonts['family'], 11),
                           bg=self.colors['surface_card'],
                           fg=self.colors['text_secondary'])
        dir_label.pack(anchor='w')
        
        dir_path_frame = tk.Frame(dir_frame, bg=self.colors['surface_card'])
        dir_path_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.model_dir_label = tk.Label(dir_path_frame,
                                      text=self.truncate_path(self.model_dir_var.get(), 40),
                                      font=(self.fonts['family'], 10),
                                      bg=self.colors['surface_card'],
                                      fg=self.colors['text_tertiary'])
        self.model_dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 設定ボタン（セーフモード）
        settings_btn = self.create_button(dir_path_frame, "⚙", self.open_model_settings, 
                                        style='Secondary', width=30, height=25)
        settings_btn.pack(side=tk.RIGHT)
        
        # モデル一覧（スクロール可能）
        list_frame = tk.Frame(model_card, bg=self.colors['surface_card'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(self.design_tokens['spacing']['xs'], 0))
        
        # スクロールバー設定
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas（オリジナルと同じ構造）
        self.model_canvas = tk.Canvas(list_frame, 
                                    bg=self.colors['surface_card'],
                                    highlightthickness=0,
                                    yscrollcommand=scrollbar.set)
        self.model_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.model_canvas.yview)
        
        # スクロール可能フレーム
        self.model_frame = tk.Frame(self.model_canvas, bg=self.colors['surface_card'])
        self.model_canvas_window = self.model_canvas.create_window((0, 0), 
                                                                  window=self.model_frame, 
                                                                  anchor="nw")
        
        # セーフなスクロール設定
        def safe_configure_scroll_region(event=None):
            try:
                self.model_canvas.configure(scrollregion=self.model_canvas.bbox("all"))
                canvas_width = self.model_canvas.winfo_width()
                self.model_canvas.itemconfig(self.model_canvas_window, width=canvas_width)
            except:
                pass
        
        self.model_frame.bind('<Configure>', safe_configure_scroll_region)
        self.model_canvas.bind('<Configure>', safe_configure_scroll_region)
        
        # マウスホイール（セーフモード）
        def safe_mousewheel(event):
            try:
                if self.model_canvas.winfo_exists():
                    if sys.platform == "darwin":
                        self.model_canvas.yview_scroll(int(-1*(event.delta)), "units")
                    else:
                        self.model_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        if sys.platform == "darwin":
            self.model_canvas.bind("<MouseWheel>", safe_mousewheel)
        else:
            self.model_canvas.bind("<MouseWheel>", safe_mousewheel)
            self.model_canvas.bind("<Button-4>", lambda e: self.model_canvas.yview_scroll(-1, "units"))
            self.model_canvas.bind("<Button-5>", lambda e: self.model_canvas.yview_scroll(1, "units"))
    
    def create_conversion_section(self, parent):
        """変換設定セクション（右側）"""
        # スクロール可能コンテナ
        scroll_container = tk.Frame(parent, bg=self.colors['background_primary'])
        scroll_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas設定
        canvas = tk.Canvas(scroll_container, 
                         bg=self.colors['background_primary'],
                         highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background_primary'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas_window(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(canvas_frame, width=canvas_width)
        
        scrollable_frame.bind('<Configure>', configure_canvas_window)
        canvas.bind('<Configure>', configure_canvas_window)
        
        # パック
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイール（セーフモード）
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        if sys.platform == "darwin":
            canvas.bind("<MouseWheel>", _on_mousewheel)
        else:
            canvas.bind("<MouseWheel>", _on_mousewheel)
            canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        # コンテンツ内容（オリジナルと同じ順序）
        # 1. 入力ファイル選択
        input_card = self.create_card(scrollable_frame, "Input Audio")
        self.create_input_section(input_card)
        
        # 2. 出力設定
        output_card = self.create_card(scrollable_frame, "Output Settings")
        self.create_output_section(output_card)
        
        # 3. 変換パラメータ
        params_card = self.create_card(scrollable_frame, "Conversion Parameters")
        self.create_params_section(params_card)
        
        # 4. 変換実行
        convert_card = self.create_card(scrollable_frame, "")
        self.create_convert_button(convert_card)
        
        # 5. ステータス（変換中のみ表示）
        self.status_card = self.create_card(scrollable_frame, "Conversion Status", visible=False)
        self.create_status_section(self.status_card)
        
        # 6. ログ
        log_card = self.create_card(scrollable_frame, "Log")
        self.create_log_section(log_card)
    
    def create_input_section(self, parent):
        """入力ファイル選択セクション"""
        # ファイル選択フレーム
        file_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        file_frame.pack(fill=tk.X)
        
        # ボタンと表示
        select_btn = self.create_button(file_frame, "Select Audio File", 
                                      self.browse_input_file, style='Secondary')
        select_btn.pack(fill=tk.X)
        
        # 選択されたファイル表示
        self.input_label = tk.Label(file_frame,
                                  text="No file selected",
                                  font=(self.fonts['family'], 10),
                                  bg=self.colors['surface_card'],
                                  fg=self.colors['text_tertiary'])
        self.input_label.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xs'], 0))
    
    def create_output_section(self, parent):
        """出力設定セクション"""
        # ファイル名入力
        filename_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        filename_frame.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        filename_label = tk.Label(filename_frame,
                                text="Output Filename (optional)",
                                font=(self.fonts['family'], 11),
                                bg=self.colors['surface_card'],
                                fg=self.colors['text_secondary'])
        filename_label.pack(anchor='w')
        
        # エントリーフレーム
        entry_frame = tk.Frame(filename_frame, bg=self.colors['surface_card'])
        entry_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.filename_entry = tk.Entry(entry_frame,
                                     textvariable=self.output_filename_var,
                                     font=(self.fonts['family'], 11),
                                     bg=self.colors['background_secondary'],
                                     fg=self.colors['text_primary'],
                                     insertbackground=self.colors['text_primary'],
                                     relief='flat',
                                     bd=0)
        self.filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # イベントバインディング（セーフモード）
        self.filename_entry.bind('<KeyPress>', self.on_filename_manual_input)
        self.filename_entry.bind('<FocusIn>', self.on_filename_focus)
        
        # クリアボタン
        clear_btn = tk.Label(entry_frame, text="✕",
                           font=(self.fonts['family'], 12),
                           bg=self.colors['surface_card'],
                           fg=self.colors['text_tertiary'],
                           cursor='hand2')
        clear_btn.pack(side=tk.RIGHT)
        
        def clear_filename():
            self.output_filename_var.set("")
            self.is_manual_filename = False
            self.update_output_preview()
        
        clear_btn.bind('<Button-1>', lambda e: clear_filename())
        
        # プレビュー
        self.output_preview_label = tk.Label(filename_frame,
                                           text="",
                                           font=(self.fonts['family'], 10),
                                           bg=self.colors['surface_card'],
                                           fg=self.colors['text_tertiary'])
        self.output_preview_label.pack(anchor='w', pady=(2, 0))
    
    def create_params_section(self, parent):
        """変換パラメータセクション"""
        if self.use_enhanced_conversion:
            # Enhanced mode表示
            info_frame = tk.Frame(parent, bg=self.colors['surface_card'])
            info_frame.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
            
            info_label = tk.Label(info_frame,
                                text="✓ Enhanced conversion parameters active",
                                font=(self.fonts['family'], 11),
                                bg=self.colors['surface_card'],
                                fg=self.colors['success'])
            info_label.pack(anchor='w')
            
            # 有効な機能リスト
            features = [
                "• Adaptive neighbor search (8-32)",
                "• F0 ensemble estimation", 
                "• VAD-based segmentation",
                "• Quality boost optimization"
            ]
            
            for feature in features:
                feat_label = tk.Label(info_frame,
                                    text=feature,
                                    font=(self.fonts['family'], 10),
                                    bg=self.colors['surface_card'],
                                    fg=self.colors['text_tertiary'])
                feat_label.pack(anchor='w', padx=(10, 0))
        else:
            # 通常モード
            note_label = tk.Label(parent,
                                text="Using standard conversion parameters",
                                font=(self.fonts['family'], 11),
                                bg=self.colors['surface_card'],
                                fg=self.colors['text_secondary'])
            note_label.pack(anchor='w')
    
    def create_convert_button(self, parent):
        """変換ボタン"""
        self.convert_btn = self.create_button(parent, 
                                            "Convert Voice" if not self.use_enhanced_conversion else "Convert Voice (Enhanced)",
                                            self.start_conversion,
                                            style='Primary')
        self.convert_btn.pack(fill=tk.X, pady=(10, 0))
    
    def create_status_section(self, parent):
        """ステータスセクション（変換中のみ表示）"""
        # プログレスバー
        self.progress = ttk.Progressbar(parent, 
                                       orient=tk.HORIZONTAL,
                                       mode='determinate',
                                       style='TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # ステータステキスト
        status_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        status_frame.pack(fill=tk.X)
        
        self.current_stage_label = tk.Label(status_frame,
                                          text="準備中...",
                                          font=(self.fonts['family'], 12, 'bold'),
                                          bg=self.colors['surface_card'],
                                          fg=self.colors['text_primary'])
        self.current_stage_label.pack(anchor='w')
        
        self.status_label = tk.Label(status_frame,
                                   text="",
                                   font=(self.fonts['family'], 10),
                                   bg=self.colors['surface_card'],
                                   fg=self.colors['text_secondary'])
        self.status_label.pack(anchor='w')
        
        # パーセンテージ
        self.percentage_label = tk.Label(status_frame,
                                       text="0%",
                                       font=(self.fonts['family'], 16, 'bold'),
                                       bg=self.colors['surface_card'],
                                       fg=self.colors['accent_primary'])
        self.percentage_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_log_section(self, parent):
        """ログセクション"""
        # ログテキストエリア
        log_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame,
                              height=8,
                              font=(self.fonts['mono'], 10),
                              bg=self.colors['background_secondary'],
                              fg=self.colors['text_secondary'],
                              relief='flat',
                              bd=0,
                              wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # スクロールバー
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical")
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)
        
        # 初期メッセージ
        self.log_text.insert(tk.END, "Voice Converter Ready.\n")
        self.log_text.config(state=tk.NORMAL)  # 編集可能にしてコピーを許可
    
    def log_message(self, message, level="INFO"):
        """ログメッセージを追加"""
        if not hasattr(self, 'log_text'):
            print(f"[{level}] {message}")
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)  # 最新のログまでスクロール
    
    def create_card(self, parent, title, visible=True):
        """カードUI要素を作成"""
        card = tk.Frame(parent, 
                       bg=self.colors['surface_card'],
                       relief='flat')
        if visible:
            card.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # カード内部のパディング（超コンパクト）
        inner = tk.Frame(card, bg=self.colors['surface_card'])
        inner.pack(fill=tk.BOTH, expand=True, 
                  padx=self.design_tokens['spacing']['xs'],
                  pady=self.design_tokens['spacing']['xs'])
        
        # タイトル
        if title:
            title_label = tk.Label(inner, text=title,
                                 font=('SF Pro Display', 13, 'bold'),
                                 bg=self.colors['surface_card'],
                                 fg=self.colors['text_primary'])
            title_label.pack(anchor='w', pady=(0, self.design_tokens['spacing']['xxs']))
            
            # 区切り線
            separator = tk.Frame(inner, 
                               bg=self.colors['divider'], 
                               height=1)
            separator.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xxs']))
        
        return inner
        
    def create_button(self, parent, text, command, style='Primary', width=None, height=None):
        """カスタムボタンを作成（セーフモード版）"""
        btn_frame = tk.Frame(parent, bg=parent['bg'])
        
        if style == 'Primary':
            bg_color = self.colors['accent_primary']
            fg_color = 'white'
            hover_color = '#4A8FEF'
            active_color = '#3A7FDF'
            font_style = ('SF Pro Display', 14, 'bold')
        else:
            bg_color = self.colors['background_tertiary']
            fg_color = self.colors['text_primary']
            hover_color = self.colors['background_elevated']
            active_color = self.colors['background_secondary']
            font_style = ('SF Pro Display', 13, 'normal')
            
        btn = tk.Label(btn_frame, text=text,
                      font=font_style,
                      bg=bg_color,
                      fg=fg_color,
                      cursor='hand2')
        
        # サイズ設定
        if width and height:
            btn.config(padx=15, pady=8)
            btn_frame.config(width=width, height=height)
            btn_frame.pack_propagate(False)
        else:
            btn.config(padx=self.design_tokens['spacing']['md'],
                      pady=self.design_tokens['spacing']['xs'])
            
        btn.pack(fill=tk.BOTH, expand=True)
        
        # セーフモード: 最小限のイベントハンドリング
        if self.safe_mode:
            # クリックのみ（ホバーエフェクトなし）
            def on_click(e):
                command()
            btn.bind('<Button-1>', on_click)
        else:
            # 通常モード（オリジナルと同じ）
            def on_enter(e):
                btn.config(bg=hover_color)
                
            def on_leave(e):
                btn.config(bg=bg_color)
                
            def on_click(e):
                btn.config(bg=active_color)
                # 安全なafter処理
                try:
                    parent_window = btn.winfo_toplevel()
                    parent_window.after(100, lambda: btn.config(bg=bg_color) if btn.winfo_exists() else None)
                except:
                    pass
                command()
                
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            btn.bind('<Button-1>', on_click)
        
        return btn_frame
    
    def truncate_path(self, path, max_length=50):
        """長いパスを省略"""
        if len(path) <= max_length:
            return path
        
        parts = path.split(os.sep)
        if len(parts) <= 3:
            return path
            
        # 最初と最後の部分を保持
        start = parts[0] + os.sep + parts[1]
        end = parts[-2] + os.sep + parts[-1]
        
        if len(start) + len(end) + 5 > max_length:
            # それでも長すぎる場合は最後の部分だけ
            return "..." + os.sep + parts[-1]
        
        return start + os.sep + "..." + os.sep + end
    
    def open_model_settings(self):
        """モデル設定ダイアログを開く"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Model Settings")
        settings_window.geometry("500x200")
        settings_window.configure(bg=self.colors['background_primary'])
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # ウィンドウを中央に配置
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() - settings_window.winfo_width()) // 2
        y = (settings_window.winfo_screenheight() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{x}+{y}")
        
        # メインフレーム
        main_frame = tk.Frame(settings_window, bg=self.colors['surface_card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(main_frame, 
                             text="Model Directory Settings",
                             font=(self.fonts['family'], 16, 'bold'),
                             bg=self.colors['surface_card'],
                             fg=self.colors['text_primary'])
        title_label.pack(anchor='w', pady=(0, 15))
        
        # ディレクトリ選択
        dir_frame = tk.Frame(main_frame, bg=self.colors['surface_card'])
        dir_frame.pack(fill=tk.X, pady=(0, 20))
        
        dir_label = tk.Label(dir_frame,
                           text="Model Directory:",
                           font=(self.fonts['family'], 12),
                           bg=self.colors['surface_card'],
                           fg=self.colors['text_secondary'])
        dir_label.pack(anchor='w', pady=(0, 5))
        
        # パスとブラウズボタン
        path_frame = tk.Frame(dir_frame, bg=self.colors['surface_card'])
        path_frame.pack(fill=tk.X)
        
        path_entry = tk.Entry(path_frame,
                            textvariable=self.model_dir_var,
                            font=(self.fonts['family'], 11),
                            bg=self.colors['background_secondary'],
                            fg=self.colors['text_primary'],
                            insertbackground=self.colors['text_primary'],
                            relief='flat')
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = self.create_button(path_frame, "Browse", 
                                      lambda: self.browse_model_directory(path_entry),
                                      style='Secondary', width=80, height=30)
        browse_btn.pack(side=tk.RIGHT)
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame, bg=self.colors['surface_card'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # キャンセルと保存ボタン
        cancel_btn = self.create_button(button_frame, "Cancel", 
                                      settings_window.destroy,
                                      style='Secondary', width=80, height=35)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        def save_and_close():
            self.save_settings()
            self.model_dir = self.model_dir_var.get()
            self.model_dir_label.config(text=self.truncate_path(self.model_dir, 40))
            self.load_models()
            settings_window.destroy()
            
        save_btn = self.create_button(button_frame, "Save", 
                                    save_and_close,
                                    style='Primary', width=80, height=35)
        save_btn.pack(side=tk.RIGHT)
    
    def browse_model_directory(self, entry_widget=None):
        """モデルディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="Select Model Directory",
            initialdir=self.model_dir_var.get()
        )
        if directory:
            self.model_dir_var.set(directory)
    
    def load_models(self):
        """モデルファイルを読み込んで表示"""
        # 既存のモデル表示をクリア
        for widget in self.model_frame.winfo_children():
            widget.destroy()
            
        # モデルファイルをスキャン
        models = []
        model_dir = self.model_dir_var.get()
        
        if os.path.exists(model_dir):
            for filename in os.listdir(model_dir):
                if filename.endswith('.pth'):
                    file_path = os.path.join(model_dir, filename)
                    file_size = os.path.getsize(file_path)
                    
                    # サイズを読みやすい形式に
                    if file_size > 1024 * 1024 * 1024:  # GB
                        size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
                    elif file_size > 1024 * 1024:  # MB
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    else:  # KB
                        size_str = f"{file_size / 1024:.1f} KB"
                    
                    # インデックスファイルの検索
                    base_name = os.path.splitext(filename)[0]
                    index_file = None
                    has_index = False
                    
                    # .index 拡張子で検索
                    for idx_ext in ['.index', '.npy']:
                        idx_path = os.path.join(model_dir, base_name + idx_ext)
                        if os.path.exists(idx_path):
                            index_file = idx_path
                            has_index = True
                            break
                    
                    models.append({
                        'name': base_name,
                        'path': file_path,
                        'size': size_str,
                        'has_index': has_index,
                        'index_path': index_file
                    })
        
        # モデルが見つからない場合
        if not models:
            no_models_label = tk.Label(self.model_frame,
                                     text="No models found.\nPlace .pth files in the model directory.",
                                     font=(self.fonts['family'], 12),
                                     bg=self.colors['surface_card'],
                                     fg=self.colors['text_tertiary'],
                                     justify=tk.CENTER)
            no_models_label.pack(expand=True, fill=tk.BOTH, pady=40)
            return
        
        # モデルカードを作成
        for index, model in enumerate(sorted(models, key=lambda x: x['name'].lower())):
            self.create_model_card(self.model_frame, model, index)
    
    def create_model_card(self, parent, model, index):
        """モデルカードを作成（セーフモード版）"""
        # カードフレーム
        card_frame = tk.Frame(parent, 
                            bg=self.colors['background_secondary'],
                            relief='flat')
        card_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 内部フレーム
        inner = tk.Frame(card_frame, bg=self.colors['background_secondary'])
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        
        # モデル名
        name_label = tk.Label(inner,
                            text=model['name'],
                            font=(self.fonts['family'], 12, 'bold'),
                            bg=self.colors['background_secondary'],
                            fg=self.colors['text_primary'],
                            anchor='w')
        name_label.pack(fill=tk.X)
        
        # 詳細情報
        info_frame = tk.Frame(inner, bg=self.colors['background_secondary'])
        info_frame.pack(fill=tk.X)
        
        # サイズ
        size_label = tk.Label(info_frame,
                            text=f"Size: {model['size']}",
                            font=(self.fonts['family'], 10),
                            bg=self.colors['background_secondary'],
                            fg=self.colors['text_tertiary'])
        size_label.pack(side=tk.LEFT)
        
        # インデックス
        if model['has_index']:
            index_label = tk.Label(info_frame,
                                 text=" • Index ✓",
                                 font=(self.fonts['family'], 10),
                                 bg=self.colors['background_secondary'],
                                 fg=self.colors['success'])
            index_label.pack(side=tk.LEFT)
        
        # 選択機能
        def select_model():
            self.selected_model.set(model['name'])
            self.on_model_selected(model)
            
            # 全カードの選択状態を更新
            for widget in parent.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.config(bg=self.colors['background_secondary'])
                    for child in widget.winfo_children():
                        if hasattr(child, 'config'):
                            child.config(bg=self.colors['background_secondary'])
                        for subchild in child.winfo_children():
                            if hasattr(subchild, 'config'):
                                subchild.config(bg=self.colors['background_secondary'])
            
            # 選択されたカードを強調
            card_frame.config(bg=self.colors['accent_primary'])
            inner.config(bg=self.colors['accent_primary'])
            for widget in inner.winfo_children():
                widget.config(bg=self.colors['accent_primary'])
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        child.config(bg=self.colors['accent_primary'])
        
        # クリックイベント（セーフモード）
        for widget in [card_frame, inner, name_label, info_frame, size_label]:
            widget.bind('<Button-1>', lambda e: select_model())
        
        # セーフモード: ホバーエフェクトは最小限に
        if not self.safe_mode:
            def on_enter(e):
                if self.selected_model.get() != model['name']:
                    card_frame.config(bg=self.colors['background_tertiary'])
                    
            def on_leave(e):
                if self.selected_model.get() != model['name']:
                    card_frame.config(bg=self.colors['background_secondary'])
                    
            card_frame.bind('<Enter>', on_enter)
            card_frame.bind('<Leave>', on_leave)
        
        # 最初のモデルを自動選択
        if index == 0:
            select_model()
    
    def on_model_selected(self, model):
        """モデル選択時の処理"""
        self.model_info = model
        self.update_output_preview()
        self.log_message(f"Selected model: {model['name']}")
    
    def browse_input_file(self):
        """入力ファイルを選択"""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.flac *.m4a *.ogg *.wma"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.input_var.set(file_path)
            self.input_label.config(text=os.path.basename(file_path),
                                  fg=self.colors['text_primary'])
            if not self.is_manual_filename:
                self.update_output_preview()
            self.log_message(f"Selected input file: {os.path.basename(file_path)}")
    
    def on_filename_manual_input(self, event):
        """ユーザーが手動でファイル名を入力した場合"""
        self.is_manual_filename = True
        self.update_output_preview()
    
    def on_filename_focus(self, event):
        """ファイル名入力欄にフォーカスが当たった時"""
        if not self.output_filename_var.get() and self.input_var.get():
            # デフォルト値を設定
            input_name = os.path.splitext(os.path.basename(self.input_var.get()))[0]
            model_name = self.selected_model.get()
            if model_name:
                default_name = f"{input_name}_{model_name}"
                self.output_filename_var.set(default_name)
                self.filename_entry.select_range(0, tk.END)
    
    def update_output_preview(self):
        """出力ファイル名のプレビューを更新"""
        if hasattr(self, 'output_preview_label'):
            custom_filename = self.output_filename_var.get().strip()
            if custom_filename and self.is_manual_filename:
                # バリデーション
                invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
                has_invalid = any(char in custom_filename for char in invalid_chars)
                
                if has_invalid:
                    preview_text = f"❌ Invalid filename: {custom_filename}.wav"
                    color = self.colors['error']
                else:
                    preview_text = f"✓ {custom_filename}.wav"
                    color = self.colors['success']
                    
                self.output_preview_label.config(text=preview_text, fg=color)
                return
            
            # 自動生成の場合
            if self.input_var.get() and self.selected_model.get():
                input_name = os.path.splitext(os.path.basename(self.input_var.get()))[0]
                model_name = self.selected_model.get()
                auto_name = f"{input_name}_{model_name}.wav"
                self.output_preview_label.config(
                    text=f"Output: {auto_name}",
                    fg=self.colors['text_tertiary']
                )
            else:
                self.output_preview_label.config(text="", fg=self.colors['text_tertiary'])
    
    def start_conversion(self):
        """変換を開始"""
        if self.converting:
            return
        
        # 入力検証
        if not self.input_var.get():
            messagebox.showerror("Error", "Please select an input audio file.")
            return
            
        if not self.selected_model.get():
            messagebox.showerror("Error", "Please select a voice model.")
            return
        
        # 変換開始
        self.converting = True
        self.convert_btn.winfo_children()[0].config(text="Converting...", state='disabled')
        
        # ステータスカードを表示
        self.status_card.master.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # 変換スレッドを開始
        self.conversion_thread = threading.Thread(target=self.run_conversion, daemon=True)
        self.conversion_thread.start()
    
    def run_conversion(self):
        """変換処理を実行（Enhanced対応）"""
        try:
            input_file = self.input_var.get()
            model_name = self.selected_model.get()
            
            # 出力ファイル名を決定
            if self.is_manual_filename and self.output_filename_var.get().strip():
                output_filename = self.output_filename_var.get().strip() + ".wav"
            else:
                input_name = os.path.splitext(os.path.basename(input_file))[0]
                output_filename = f"{input_name}_{model_name}.wav"
            
            output_path = os.path.join(self.base_dir, "output", output_filename)
            
            # 出力ディレクトリを作成
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # プログレス更新
            self.update_progress(0, 10, "Initializing conversion...")
            
            # モデル情報を取得
            model_path = self.model_info['path']
            
            # 変換実行
            if self.use_enhanced_conversion and self.enhanced_converter:
                # Enhanced変換
                self.log_message("Starting enhanced voice conversion...")
                self.update_progress(1, 30, "Loading enhanced audio...")
                
                # パラメータ設定
                params = {
                    'f0_method': self.f0_method_var.get(),
                    'index_rate': self.index_rate_var.get(),
                    'protect': self.protect_var.get(),
                    'filter_radius': self.filter_radius_var.get(),
                    'rms_mix_rate': self.rms_mix_rate_var.get(),
                    'f0_up_key': self.pitch_var.get()
                }
                
                if self.model_info.get('has_index') and self.model_info.get('index_path'):
                    params['index_path'] = self.model_info['index_path']
                
                # 変換実行
                self.update_progress(2, 50, "Processing with enhanced algorithms...")
                
                # コマンド生成（実際の処理用）
                cmd = self.enhanced_converter.generate_enhanced_command(
                    input_file, output_path, model_path, params
                )
                
                # サブプロセスで実行
                self.update_progress(3, 70, "Applying voice conversion...")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.base_dir
                )
                
                if result.returncode == 0:
                    self.update_progress(4, 90, "Finalizing output...")
                    self.log_message("Enhanced conversion completed successfully!")
                else:
                    raise RuntimeError(f"Conversion failed: {result.stderr}")
                    
            else:
                # 標準変換
                self.log_message("Starting standard voice conversion...")
                self.run_standard_conversion(input_file, output_path, model_path)
            
            # 完了
            self.update_progress(5, 100, "Conversion completed!")
            time.sleep(0.5)
            
            # UIリセット
            self.root.after(0, self.conversion_complete, True, output_path)
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}", "ERROR")
            self.root.after(0, self.conversion_complete, False, str(e))
    
    def run_standard_conversion(self, input_file, output_path, model_path):
        """標準変換処理"""
        # RVC CLIコマンドを構築
        python_cmd = sys.executable
        
        cmd = [
            python_cmd, "-m", "rvc.wrapper.cli.cli",
            "infer",
            "--input_path", input_file,
            "--output_path", output_path,
            "--model_path", model_path,
            "--f0_method", self.f0_method_var.get(),
            "--index_rate", str(self.index_rate_var.get()),
            "--filter_radius", str(self.filter_radius_var.get()),
            "--rms_mix_rate", str(self.rms_mix_rate_var.get()),
            "--protect", str(self.protect_var.get()),
            "--f0_up_key", str(self.pitch_var.get())
        ]
        
        # インデックスファイルがある場合
        if self.model_info.get('has_index') and self.model_info.get('index_path'):
            cmd.extend(["--index_file", self.model_info['index_path']])
        
        # 変換実行
        self.update_progress(2, 50, "Processing audio...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.base_dir
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Conversion failed: {result.stderr}")
            
        self.update_progress(4, 90, "Finalizing output...")
    
    def update_progress(self, stage_index, progress, message):
        """プログレスバーとステージインジケーターを更新"""
        if not hasattr(self, 'status_card'):
            return
            
        # UIを更新
        self.root.after(0, lambda: self._update_progress_ui(stage_index, progress, message))
        
    def _update_progress_ui(self, stage_index, total_progress, message):
        """UIスレッドでプログレスを更新"""
        # プログレスバーを更新
        self.progress['value'] = total_progress
        self.percentage_label.config(text=f"{int(total_progress)}%")
        
        # 現在のステージ情報を更新
        stage_names = [
            "初期化中...",
            "音声ファイルを読み込んでいます...",
            "音声データの前処理を実行中...",
            "音声の特徴を抽出しています...",
            "AIモデルで音声を変換中...",
            "音質の最適化を実行中...",
            "変換結果を保存しています..."
        ]
        
        if 0 <= stage_index < len(stage_names):
            self.current_stage_label.config(text=stage_names[stage_index])
            self.status_label.config(text=message)
        
        # UIを更新
        self.root.update_idletasks()
    
    def conversion_complete(self, success, result):
        """変換完了時の処理"""
        self.converting = False
        self.convert_btn.winfo_children()[0].config(
            text="Convert Voice" if not self.use_enhanced_conversion else "Convert Voice (Enhanced)",
            state='normal'
        )
        
        # ステータスカードを非表示
        self.status_card.master.pack_forget()
        
        if success:
            self.log_message(f"Saved to: {result}", "SUCCESS")
            messagebox.showinfo("Success", f"Conversion completed!\nOutput saved to:\n{result}")
        else:
            self.log_message(f"Conversion failed: {result}", "ERROR")
            messagebox.showerror("Error", f"Conversion failed:\n{result}")


def main():
    """メイン実行関数"""
    try:
        print("=== Voice Converter Enhanced Exact GUI ===")
        print("Starting GUI with exact UI reproduction...")
        
        root = tk.Tk()
        app = DarkModeGUI(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()