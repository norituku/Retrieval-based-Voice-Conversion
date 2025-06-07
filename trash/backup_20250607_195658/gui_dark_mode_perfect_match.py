#!/usr/bin/env python3
"""
RVC Dark Mode GUI - Perfect Match Edition
オリジナルgui_dark_mode.pyと100%完全一致 + Enhanced機能 + セグフォルト対策
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
        
        # セグフォルト対策: 安全モード
        self.safe_mode = True
        
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
                'surface_sidebar': '#141416',  # オリジナルのサイドバー色
                
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
            
            # タイポグラフィ - SF Pro for macOS（オリジナルと同じ）
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
            
            # スペーシング - 超コンパクトグリッドシステム（オリジナルと同じ）
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
            
            # レイアウト（オリジナルと同じ）
            'layout': {
                'sidebar_width': 200,  # オリジナルの200px
                'min_window_width': 900,
                'min_window_height': 500,
                'toolbar_height': 35,
                'max_content_width': 650,  # メインコンテンツの最大幅
            }
        }
        
        self.colors = self.design_tokens['colors']
        
        # フォントファミリーの定義（オリジナルと同じ）
        self.fonts = {
            'family': 'SF Pro Display',
            'mono': 'SF Mono'
        }
        
        # 変数の初期化（オリジナルと同じ）
        self.model_info = {}
        self.selected_model = tk.StringVar()
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.output_filename_var = tk.StringVar()  
        self.is_manual_filename = False  
        self.model_dir_var = tk.StringVar()  
        self.pitch_var = tk.IntVar(value=0)
        self.f0_method_var = tk.StringVar(value="rmvpe")  
        self.index_rate_var = tk.DoubleVar(value=1.0)     
        self.filter_radius_var = tk.IntVar(value=3)       
        self.rms_mix_rate_var = tk.DoubleVar(value=0.25)  
        self.protect_var = tk.DoubleVar(value=0.33)       
        
        # 変換制御
        self.converting = False
        self.conversion_thread = None
        
        # アプリケーション設定
        self.setup_app_directories()
        
        # Enhanced Converter初期化
        self.init_enhanced_converter()
        
        # カスタムスタイル設定
        self.setup_styles()
        
        # ウィンドウ設定（オリジナルと同じ）
        self.setup_window()
        
        # UI構築（オリジナルと同じ）
        self.create_ui()
        
        # モデル読み込み
        self.load_models()
        
    def setup_app_directories(self):
        """アプリケーションディレクトリの設定（オリジナルと同じ）"""
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
        """カスタムスタイルの設定（オリジナルと同じ）"""
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
        
        # スクロールバー（ダーク）
        style.configure('Dark.Vertical.TScrollbar',
                       background=self.colors['background_secondary'],
                       darkcolor=self.colors['background_tertiary'],
                       lightcolor=self.colors['background_tertiary'],
                       troughcolor=self.colors['background_primary'],
                       bordercolor=self.colors['background_primary'],
                       arrowcolor=self.colors['text_tertiary'],
                       relief='flat')
        
        # プログレスバー（オリジナルと同じ）
        style.configure('TProgressbar',
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['background_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent_primary'],
                       darkcolor=self.colors['accent_primary'])
    
    def setup_window(self):
        """ウィンドウの設定（オリジナルと完全一致）"""
        self.root.configure(bg=self.colors['background_primary'])
        
        # アイコン設定（存在する場合）
        icon_path = os.path.join(self.base_dir, 'icon.png')
        if os.path.exists(icon_path):
            try:
                photo = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, photo)
            except:
                pass
        
        # 画面サイズを取得
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # ウィンドウサイズを画面サイズに応じて調整（オリジナルと同じ）
        window_width = min(self.design_tokens['layout']['min_window_width'], int(screen_width * 0.9))
        window_height = min(650, int(screen_height * 0.85))  # デフォルト高さを650に設定
        
        # 画面中央に配置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(850, 480)  # 最小サイズをさらに小さく設定
        
        # macOS用の設定（オリジナルと同じ）
        if sys.platform == "darwin":
            # スケーリングを調整
            try:
                current_scaling = self.root.tk.call('tk', 'scaling')
                if current_scaling > 1.5:
                    self.root.tk.call('tk', 'scaling', 1.5)
            except:
                pass
            # ダークモードを強制
            try:
                self.root.tk.call('::tk::unsupported::MacWindowStyle', 'style', self.root._w, 'dark')
            except:
                pass
                
    def create_ui(self):
        """メインUI構築（オリジナルと完全一致）"""
        # ナビゲーションバー
        self.create_navigation_bar()
        
        # メインコンテンツエリア
        self.main_content = tk.Frame(self.root, bg=self.colors['background_primary'])
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 2カラムレイアウト
        self.create_two_column_layout()
        
    def create_navigation_bar(self):
        """ナビゲーションバー（オリジナルと完全一致）"""
        nav_bar = tk.Frame(self.root, 
                          bg=self.colors['background_secondary'], 
                          height=self.design_tokens['layout']['toolbar_height'])
        nav_bar.pack(fill=tk.X)
        nav_bar.pack_propagate(False)
        
        # 左側：ロゴとタイトル
        left_frame = tk.Frame(nav_bar, bg=self.colors['background_secondary'])
        left_frame.pack(side=tk.LEFT, padx=self.design_tokens['spacing']['md'])
        
        # アプリアイコン
        icon_canvas = tk.Canvas(left_frame, width=28, height=28, 
                               bg=self.colors['background_secondary'], 
                               highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, pady=6)
        
        # グラデーション風アイコン
        self.draw_gradient_icon(icon_canvas)
        
        # タイトル
        title_label = tk.Label(left_frame, text="Voice Converter",
                              font=('SF Pro Display', 18, 'bold'),
                              bg=self.colors['background_secondary'],
                              fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=self.design_tokens['spacing']['sm'])
        
        # Enhanced表示（右側）
        if self.use_enhanced_conversion:
            enhanced_label = tk.Label(nav_bar,
                                    text="Enhanced Mode",
                                    font=(self.fonts['family'], 10),
                                    bg=self.colors['background_secondary'],
                                    fg=self.colors['success'])
            enhanced_label.pack(side=tk.RIGHT, padx=(10, self.design_tokens['spacing']['md']))
        
    def draw_gradient_icon(self, canvas):
        """グラデーションアイコンを描画（オリジナルと同じ）"""
        # 外側の円
        canvas.create_oval(2, 2, 26, 26, 
                          fill=self.colors['accent_primary'], 
                          outline='')
        # 内側の円
        canvas.create_oval(5, 5, 23, 23, 
                          fill=self.colors['accent_secondary'], 
                          outline='')
        # 波形アイコン
        canvas.create_text(14, 14, text="♪", 
                          fill="white", 
                          font=("Arial", 16, "bold"))
        
    def create_two_column_layout(self):
        """2カラムレイアウト（オリジナルと完全一致）"""
        # 左カラム（サイドバー）
        self.left_column = tk.Frame(self.main_content, 
                                   bg=self.colors['surface_sidebar'],
                                   width=self.design_tokens['layout']['sidebar_width'])
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.left_column.pack_propagate(False)
        
        # 右カラム（メインコンテンツ）
        self.right_column = tk.Frame(self.main_content, 
                                    bg=self.colors['background_primary'])
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 左カラムコンテンツ
        self.create_model_sidebar()
        
        # 右カラムコンテンツ
        self.create_main_content()

    def create_model_sidebar(self):
        """モデル選択サイドバー（オリジナルと完全一致）"""
        # ヘッダー
        header = tk.Frame(self.left_column, bg=self.colors['surface_sidebar'])
        header.pack(fill=tk.X, padx=self.design_tokens['spacing']['sm'], 
                   pady=self.design_tokens['spacing']['sm'])
        
        # タイトルと設定ボタンの行
        title_row = tk.Frame(header, bg=self.colors['surface_sidebar'])
        title_row.pack(fill=tk.X)
        
        tk.Label(title_row, text="Voice Models",
                font=('SF Pro Display', 16, 'bold'),
                bg=self.colors['surface_sidebar'],
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        # 設定ボタン
        settings_btn = self.create_button(title_row, "⚙", 
                                        self.open_model_settings, 
                                        style='Secondary')
        settings_btn.pack(side=tk.RIGHT)
        
        # モデルフォルダパス表示
        self.model_path_label = tk.Label(header, 
                            text=self.truncate_path(self.model_dir_var.get(), 30),
                            font=('SF Pro Mono', 9),
                            bg=self.colors['surface_sidebar'],
                            fg=self.colors['text_tertiary'])
        self.model_path_label.pack(anchor='w', pady=(2, 0))
        
        tk.Label(header, text="Select a model",
                font=('SF Pro Display', 11),
                bg=self.colors['surface_sidebar'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(2, 0))
        
        # 区切り線
        separator = tk.Frame(self.left_column, 
                           bg=self.colors['divider'], 
                           height=1)
        separator.pack(fill=tk.X, padx=self.design_tokens['spacing']['sm'])
        
        # モデルリスト用スクロール可能フレーム
        self.create_scrollable_model_list()
        
    def create_scrollable_model_list(self):
        """スクロール可能なモデルリスト（オリジナルと完全一致）"""
        # スクロールコンテナ
        scroll_container = tk.Frame(self.left_column, bg=self.colors['surface_sidebar'])
        scroll_container.pack(fill=tk.BOTH, expand=True, 
                             padx=self.design_tokens['spacing']['sm'],
                             pady=self.design_tokens['spacing']['sm'])
        
        # Canvas とスクロールバー
        canvas = tk.Canvas(scroll_container, 
                          bg=self.colors['surface_sidebar'],
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", 
                                 command=canvas.yview,
                                 style='Dark.Vertical.TScrollbar')
        
        self.model_frame = tk.Frame(canvas, bg=self.colors['surface_sidebar'])
        
        # スクロール設定（セーフモード）
        def safe_configure_scroll_region(event):
            try:
                canvas.configure(scrollregion=canvas.bbox("all"))
            except:
                pass
        
        self.model_frame.bind("<Configure>", safe_configure_scroll_region)
        
        canvas.create_window((0, 0), window=self.model_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # パッキング
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイールでスクロール（セーフモード）
        def safe_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        if not self.safe_mode:
            canvas.bind_all("<MouseWheel>", safe_mousewheel)
            # Linux用のマウスホイール
            canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
    def create_main_content(self):
        """メインコンテンツエリア（オリジナルと完全一致）"""
        # スクロール可能なキャンバスを作成
        self.canvas = tk.Canvas(self.right_column, 
                               bg=self.colors['background_primary'],
                               highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.right_column, orient="vertical", 
                                       command=self.canvas.yview,
                                       style='Dark.Vertical.TScrollbar')
        
        # スクロール可能フレーム
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['background_primary'])
        
        def safe_configure_scroll_region(event):
            try:
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except:
                pass
        
        self.scrollable_frame.bind("<Configure>", safe_configure_scroll_region)
        
        # コンテンツウィンドウを作成
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # キャンバスのサイズ変更時にコンテンツの幅を調整
        def configure_canvas_window(event):
            canvas_width = event.width
            # スクロール可能フレームの幅をキャンバスの幅に設定
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind('<Configure>', configure_canvas_window)
        
        # マウスホイールでスクロール（セーフモード）
        def safe_mousewheel(event):
            try:
                if self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
            
        # セーフモードでない場合のみマウスホイール
        if not self.safe_mode:
            # プラットフォーム別のマウスホイール設定
            if sys.platform == "darwin":  # macOS
                self.canvas.bind("<MouseWheel>", safe_mousewheel)
            else:  # Windows/Linux
                self.canvas.bind("<MouseWheel>", safe_mousewheel)
                self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
                self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # メインコンテンツコンテナ（超コンパクトなパディング）
        content_container = tk.Frame(self.scrollable_frame, bg=self.colors['background_primary'])
        content_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        
        # コンテンツセクション（オリジナルと同じ順序）
        self.create_title_section(content_container)
        self.create_input_section(content_container)
        self.create_settings_section(content_container)
        self.create_status_section(content_container)
        
    def create_title_section(self, parent):
        """タイトルセクション（オリジナルと完全一致）"""
        title_frame = tk.Frame(parent, bg=self.colors['background_primary'])
        title_frame.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # 1行にタイトルとサブタイトルを配置
        title_text = "Voice Converter - AI Voice Conversion"
        if self.use_enhanced_conversion:
            title_text += " (Enhanced)"
            
        tk.Label(title_frame, text=title_text,
                font=('SF Pro Display', 16, 'bold'),
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(anchor='center')
        
    def create_input_section(self, parent):
        """入力セクション（オリジナルと完全一致）"""
        # カードコンテナ
        input_card = self.create_card(parent, "Input & Convert")
        
        # 横並びレイアウト（重要：オリジナルは横並び）
        horizontal_layout = tk.Frame(input_card, bg=self.colors['surface_card'])
        horizontal_layout.pack(fill=tk.X)
        
        # 左側：ファイル選択
        left_section = tk.Frame(horizontal_layout, bg=self.colors['surface_card'])
        left_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, self.design_tokens['spacing']['xs']))
        
        browse_btn = self.create_button(left_section, "Choose Audio File", 
                                       self.browse_input, 
                                       style='Secondary')
        browse_btn.pack(fill=tk.X)
        
        # 選択されたファイル表示
        self.file_info_frame = tk.Frame(left_section, bg=self.colors['surface_card'])
        self.file_info_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xs'], 0))
        
        # 右側：変換ボタン（重要：オリジナルは右側に変換ボタン）
        right_section = tk.Frame(horizontal_layout, bg=self.colors['surface_card'])
        right_section.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # プライマリー変換ボタン
        convert_text = "Start\nConversion"
        if self.use_enhanced_conversion:
            convert_text = "Start Enhanced\nConversion"
            
        convert_btn = self.create_button(right_section, 
                                       convert_text, 
                                       self.start_conversion,
                                       style='Primary',
                                       width=120,
                                       height=50)
        convert_btn.pack()
        
    def create_settings_section(self, parent):
        """設定セクション（オリジナルと完全一致）"""
        settings_card = self.create_card(parent, "Settings")
        
        # 2カラムグリッドレイアウト（重要：オリジナルは2カラム）
        grid_container = tk.Frame(settings_card, bg=self.colors['surface_card'])
        grid_container.pack(fill=tk.X)
        
        # 左カラム：出力設定
        left_column = tk.Frame(grid_container, bg=self.colors['surface_card'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, self.design_tokens['spacing']['xs']))
        
        # 出力ディレクトリ設定（コンパクト）
        output_label = tk.Label(left_column, text="Output Directory",
                               font=('SF Pro Display', 11, 'bold'),
                               bg=self.colors['surface_card'],
                               fg=self.colors['text_secondary'])
        output_label.pack(anchor='w')
        
        # パス表示とブラウズボタン（横並び）
        path_container = tk.Frame(left_column, bg=self.colors['surface_card'])
        path_container.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # パス表示（小さく）
        self.output_path_frame = tk.Frame(path_container, 
                                         bg=self.colors['background_secondary'],
                                         relief='flat',
                                         height=28)
        self.output_path_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_path_frame.pack_propagate(False)
        
        # デフォルト出力パス
        default_output = os.path.join(os.path.expanduser("~"), "Desktop", "VoiceConverter_Output")
        self.output_var.set(default_output)
        
        self.output_path_label = tk.Label(self.output_path_frame, 
                                         text=self.truncate_path(self.output_var.get(), 35),
                                         font=('SF Pro Mono', 9),
                                         bg=self.colors['background_secondary'],
                                         fg=self.colors['text_primary'],
                                         anchor='w')
        self.output_path_label.place(relx=0.02, rely=0.5, anchor='w')
        
        # ブラウズボタン（小さく）
        browse_output_btn = self.create_button(path_container, "...", 
                                              self.browse_output, 
                                              style='Secondary')
        browse_output_btn.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['xxs'], 0))
        
        # 出力ファイル名設定
        filename_label = tk.Label(left_column, text="Output Filename",
                                font=('SF Pro Display', 10, 'bold'),
                                bg=self.colors['surface_card'],
                                fg=self.colors['text_secondary'])
        filename_label.pack(anchor='w', pady=(self.design_tokens['spacing']['xs'], 0))
        
        # ファイル名入力フィールド
        filename_container = tk.Frame(left_column, bg=self.colors['surface_card'])
        filename_container.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        self.filename_entry = tk.Entry(filename_container,
                                     textvariable=self.output_filename_var,
                                     font=('SF Pro Mono', 9),
                                     bg=self.colors['background_secondary'],
                                     fg=self.colors['text_primary'],
                                     relief='flat',
                                     bd=1)
        self.filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ユーザーの手動入力を検出（セーフモードでも有効）
        self.filename_entry.bind('<KeyRelease>', self.on_filename_change)
        self.filename_entry.bind('<FocusIn>', self.on_filename_focus)
        
        # ファイル名変更時のリアルタイム更新
        try:
            self.output_filename_var.trace_add('write', self.on_filename_var_change)
        except AttributeError:
            # 古いPythonバージョン用のフォールバック
            self.output_filename_var.trace('w', self.on_filename_var_change)
        
        # クリアボタン
        def clear_filename():
            self.output_filename_var.set("")
            self.is_manual_filename = False
            # クリア後に自動生成を試行
            self.auto_update_output_filename()
            
        clear_btn = tk.Label(filename_container, text="✕",
                           font=('SF Pro Display', 9),
                           bg=self.colors['surface_card'],
                           fg=self.colors['text_tertiary'],
                           cursor='hand2',
                           padx=5)
        clear_btn.pack(side=tk.RIGHT)
        clear_btn.bind('<Button-1>', lambda e: clear_filename())
        
        # 拡張子ラベル
        ext_label = tk.Label(filename_container, text=".wav",
                           font=('SF Pro Mono', 9),
                           bg=self.colors['surface_card'],
                           fg=self.colors['text_secondary'])
        ext_label.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['xxs'], 0))
        
        # 出力ファイル名プレビュー（1行）
        self.output_preview_label = tk.Label(left_column, 
                                           text="[Select input and model]",
                                           font=('SF Pro Mono', 7),
                                           bg=self.colors['surface_card'],
                                           fg=self.colors['text_tertiary'])
        self.output_preview_label.pack(anchor='w', pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # 右カラム：ピッチ設定（重要：オリジナルは右側にピッチ設定）
        right_column = tk.Frame(grid_container, bg=self.colors['surface_card'])
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # ピッチ設定（コンパクト版）
        self.create_compact_setting_control(right_column, "Pitch", self.pitch_var, 
                                          -12, 12, "semitones")
        
        # Enhanced機能の表示
        if self.use_enhanced_conversion:
            enhanced_info = tk.Label(right_column,
                                   text="Enhanced algorithms active",
                                   font=('SF Pro Display', 9),
                                   bg=self.colors['surface_card'],
                                   fg=self.colors['success'])
            enhanced_info.pack(anchor='w', pady=(self.design_tokens['spacing']['xs'], 0))

    def create_compact_setting_control(self, parent, label, variable, min_val, max_val, unit=""):
        """コンパクトな設定コントロール作成（オリジナルと完全一致）"""
        # ラベル
        label_text = tk.Label(parent, text=f"{label} Adjustment",
                            font=('SF Pro Display', 11, 'bold'),
                            bg=self.colors['surface_card'],
                            fg=self.colors['text_secondary'])
        label_text.pack(anchor='w')
        
        # 値とスライダーを横並びに
        control_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        control_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # 値表示（左側）
        def format_value():
            val = variable.get()
            if isinstance(variable, tk.DoubleVar):
                return f"{val:.2f}{unit}".strip()
            else:
                return f"{val}{unit}".strip()
        
        value_label = tk.Label(control_frame, 
                             text=format_value(),
                             font=('SF Pro Mono', 11, 'bold'),
                             bg=self.colors['surface_card'],
                             fg=self.colors['accent_primary'],
                             width=8)
        value_label.pack(side=tk.LEFT)
        
        # スライダー（右側）
        slider_frame = tk.Frame(control_frame, bg=self.colors['surface_card'])
        slider_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # 値の精度を決定
        if isinstance(variable, tk.DoubleVar):
            resolution = 0.01 if max_val <= 1 else 0.1
        else:
            resolution = 1
        
        # スライダー
        slider = tk.Scale(slider_frame, from_=min_val, to=max_val,
                         orient='horizontal',
                         variable=variable,
                         bg=self.colors['surface_card'],
                         fg=self.colors['text_primary'],
                         activebackground=self.colors['accent_primary'],
                         highlightthickness=0,
                         troughcolor=self.colors['background_tertiary'],
                         showvalue=False,
                         resolution=resolution,
                         width=10)
        slider.pack(fill=tk.X)
        
        # 値更新時のコールバック
        def update_value_label(*args):
            value_label.config(text=format_value())
        
        try:
            variable.trace_add('write', update_value_label)
        except AttributeError:
            variable.trace('w', update_value_label)
        
    def create_status_section(self, parent):
        """ステータスセクション（オリジナルと完全一致）"""
        # ステータスカード（初期は非表示）
        self.status_card = self.create_card(parent, "Conversion Status", visible=False)
        
        # プログレスバー
        self.progress = ttk.Progressbar(self.status_card, 
                                       orient=tk.HORIZONTAL,
                                       mode='determinate',
                                       style='TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # パーセンテージ表示フレーム
        progress_info = tk.Frame(self.status_card, bg=self.colors['surface_card'])
        progress_info.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # 現在のステージ情報
        self.current_stage_label = tk.Label(progress_info, 
                                          text="準備中...",
                                          font=('SF Pro Display', 12, 'bold'),
                                          bg=self.colors['surface_card'],
                                          fg=self.colors['text_primary'])
        self.current_stage_label.pack(side=tk.LEFT)
        
        # パーセンテージ（右側）
        self.percentage_label = tk.Label(progress_info, 
                                       text="0%",
                                       font=('SF Pro Display', 16, 'bold'),
                                       bg=self.colors['surface_card'],
                                       fg=self.colors['accent_primary'])
        self.percentage_label.pack(side=tk.RIGHT)
        
        # ステータス詳細
        self.status_label = tk.Label(self.status_card, 
                                   text="",
                                   font=('SF Pro Display', 10),
                                   bg=self.colors['surface_card'],
                                   fg=self.colors['text_secondary'],
                                   wraplength=500)
        self.status_label.pack(anchor='w', pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # ステージリスト（進捗を視覚的に表示）
        self.stages_frame = tk.Frame(self.status_card, bg=self.colors['surface_card'])
        self.stages_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xs'], 0))
        
        # 各ステージの表示を作成
        self.stage_indicators = self._create_stage_indicators()
        
        # ログエリアを追加
        self.create_log_section(parent)
    
    def _create_stage_indicators(self):
        """各ステージのインジケーターを作成（オリジナルと完全一致）"""
        stages = [
            ("初期化", "Init"),
            ("読込", "Load"),
            ("前処理", "Prep"),
            ("特徴抽出", "Extract"),
            ("変換", "Convert"),
            ("後処理", "Post"),
            ("保存", "Save")
        ]
        
        # 水平レイアウトコンテナ
        horizontal_container = tk.Frame(self.stages_frame, bg=self.colors['surface_card'])
        horizontal_container.pack(fill=tk.X)
        
        indicators = []
        for i, (stage_name, stage_short) in enumerate(stages):
            # 各ステージのコンテナ
            stage_container = tk.Frame(horizontal_container, bg=self.colors['surface_card'])
            stage_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                               padx=(0, self.design_tokens['spacing']['xxxs']) if i < len(stages)-1 else (0, 0))
            
            # 円形インジケーター（上部）
            indicator_canvas = tk.Canvas(stage_container, 
                                       width=20, height=20,
                                       bg=self.colors['surface_card'],
                                       highlightthickness=0)
            indicator_canvas.pack(pady=(0, self.design_tokens['spacing']['xxxs']))
            
            # 初期状態（グレー）
            circle = indicator_canvas.create_oval(3, 3, 17, 17,
                                                fill=self.colors['background_tertiary'],
                                                outline=self.colors['border_subtle'],
                                                width=1)
            
            # ステージ番号を中央に表示
            number_text = indicator_canvas.create_text(10, 10, text=str(i+1),
                                                     fill=self.colors['text_disabled'],
                                                     font=('SF Pro Display', 8, 'bold'))
            
            # ステージ名（下部）
            name_label = tk.Label(stage_container,
                                text=stage_name,
                                font=('SF Pro Display', 8, 'bold'),
                                bg=self.colors['surface_card'],
                                fg=self.colors['text_tertiary'])
            name_label.pack()
            
            indicators.append({
                'canvas': indicator_canvas,
                'circle': circle,
                'number_text': number_text,
                'name_label': name_label,
                'container': stage_container
            })
            
        return indicators
    
    def create_log_section(self, parent):
        """ログセクション（オリジナルと完全一致）"""
        log_card = self.create_card(parent, "Logs", visible=True)
        
        # ログテキストエリア用のフレーム
        log_frame = tk.Frame(log_card, bg=self.colors['background_tertiary'])
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # スクロールバー
        log_scrollbar = ttk.Scrollbar(log_frame, style='Dark.Vertical.TScrollbar')
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ログテキストエリア
        self.log_text = tk.Text(log_frame,
                               wrap=tk.WORD,
                               height=8,
                               bg=self.colors['background_tertiary'],
                               fg=self.colors['text_secondary'],
                               font=(self.fonts['mono'], 10),
                               relief=tk.FLAT,
                               padx=10,
                               pady=10,
                               yscrollcommand=log_scrollbar.set,
                               selectbackground=self.colors['accent_primary'],
                               selectforeground=self.colors['text_primary'])
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        log_scrollbar.config(command=self.log_text.yview)
        
        # 初期メッセージ
        self.log_text.insert(tk.END, "Voice Converter Ready.\n")
        if self.use_enhanced_conversion:
            self.log_text.insert(tk.END, "Enhanced algorithms loaded.\n")
        self.log_text.config(state=tk.NORMAL)  # 編集可能にしてコピーを許可
    
    def log_message(self, message, level="INFO"):
        """ログメッセージを追加（オリジナルと同じ）"""
        if not hasattr(self, 'log_text'):
            print(f"[{level}] {message}")
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)  # 最新のログまでスクロール
    
    def create_card(self, parent, title, visible=True):
        """カードUI要素を作成（オリジナルと完全一致）"""
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
        """カスタムボタンを作成（セーフモード対応）"""
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
        
        # セーフモード: クリックのみ
        if self.safe_mode:
            def safe_click(e):
                command()
            btn.bind('<Button-1>', safe_click)
        else:
            # 通常モード（オリジナルと同じホバーエフェクト）
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
    
    # === イベントハンドラ（オリジナルと同じ） ===
    
    def browse_input(self):
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
            self.display_file_info(file_path)
            
            # 入力ファイル選択時は自動的にファイル名を更新
            self.auto_update_output_filename()
            self.log_message(f"Selected input file: {os.path.basename(file_path)}")
    
    def display_file_info(self, file_path):
        """ファイル情報を表示"""
        # 既存の情報をクリア
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
        
        if file_path:
            # ファイル名
            filename = os.path.basename(file_path)
            name_label = tk.Label(self.file_info_frame,
                                text=f"📁 {filename}",
                                font=('SF Pro Display', 10, 'bold'),
                                bg=self.colors['surface_card'],
                                fg=self.colors['text_primary'],
                                anchor='w')
            name_label.pack(fill=tk.X)
            
            # ファイルサイズ
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 1024 * 1024:  # MB
                    size_text = f"{file_size / (1024 * 1024):.1f} MB"
                else:  # KB
                    size_text = f"{file_size / 1024:.1f} KB"
                
                size_label = tk.Label(self.file_info_frame,
                                    text=f"Size: {size_text}",
                                    font=('SF Pro Mono', 9),
                                    bg=self.colors['surface_card'],
                                    fg=self.colors['text_tertiary'],
                                    anchor='w')
                size_label.pack(fill=tk.X)
            except:
                pass
    
    def browse_output(self):
        """出力ディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_var.get()
        )
        if directory:
            self.output_var.set(directory)
            self.output_path_label.config(text=self.truncate_path(directory, 35))
            self.log_message(f"Output directory: {directory}")
    
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
            # サイドバーのパス表示を更新
            if hasattr(self, 'model_path_label'):
                self.model_path_label.config(text=self.truncate_path(self.model_dir, 30))
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
        """モデルファイルを読み込んで表示（サブディレクトリ対応）"""
        # 既存のモデル表示をクリア
        for widget in self.model_frame.winfo_children():
            widget.destroy()
            
        # モデルファイルをスキャン（再帰的検索）
        models = []
        model_dir = self.model_dir_var.get()
        
        self.log_message(f"Scanning model directory: {model_dir}")
        
        if os.path.exists(model_dir):
            # 再帰的にモデルファイルを検索
            for root, dirs, files in os.walk(model_dir):
                for filename in files:
                    if filename.endswith('.pth'):
                        file_path = os.path.join(root, filename)
                        try:
                            file_size = os.path.getsize(file_path)
                            
                            # サイズを読みやすい形式に
                            if file_size > 1024 * 1024 * 1024:  # GB
                                size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
                            elif file_size > 1024 * 1024:  # MB
                                size_str = f"{file_size / (1024 * 1024):.1f} MB"
                            else:  # KB
                                size_str = f"{file_size / 1024:.1f} KB"
                            
                            # モデル名（ディレクトリ名を含む）
                            relative_path = os.path.relpath(file_path, model_dir)
                            base_name = os.path.splitext(relative_path)[0]
                            display_name = os.path.splitext(filename)[0]
                            
                            # 同じディレクトリ内でインデックスファイルを検索
                            index_file = None
                            has_index = False
                            model_base = os.path.splitext(filename)[0]
                            
                            for idx_ext in ['.index', '.npy']:
                                idx_path = os.path.join(root, model_base + idx_ext)
                                if os.path.exists(idx_path):
                                    index_file = idx_path
                                    has_index = True
                                    break
                            
                            # サブディレクトリ名を表示名に含める（"/"を使わない）
                            if root != model_dir:
                                subdir = os.path.basename(root)
                                display_name = f"{subdir}_{display_name}"
                            
                            models.append({
                                'name': display_name,
                                'path': file_path,
                                'size': size_str,
                                'has_index': has_index,
                                'index_path': index_file
                            })
                            
                            self.log_message(f"Found model: {display_name}")
                            
                        except Exception as e:
                            self.log_message(f"Error processing {filename}: {e}", "ERROR")
        
        # モデルが見つからない場合
        if not models:
            no_models_label = tk.Label(self.model_frame,
                                     text="No models found.\nPlace .pth files in the model directory.",
                                     font=(self.fonts['family'], 12),
                                     bg=self.colors['surface_sidebar'],
                                     fg=self.colors['text_tertiary'],
                                     justify=tk.CENTER)
            no_models_label.pack(expand=True, fill=tk.BOTH, pady=40)
            return
        
        # モデルカードを作成
        for index, model in enumerate(sorted(models, key=lambda x: x['name'].lower())):
            self.create_model_card(self.model_frame, model, index)
    
    def create_model_card(self, parent, model, index):
        """モデルカードを作成（セーフモード対応）"""
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
        
        # 最初のモデルを自動選択
        if index == 0:
            select_model()
    
    def on_model_selected(self, model):
        """モデル選択時の処理"""
        self.model_info = model
        
        # モデル変更時は自動的にファイル名を更新
        self.auto_update_output_filename()
        self.log_message(f"Selected model: {model['name']}")
    
    def on_filename_change(self, event):
        """ファイル名入力フィールドでキーが離された時"""
        if self.filename_entry.get().strip():
            self.is_manual_filename = True
        self.update_output_preview()
    
    def on_filename_var_change(self, *args):
        """ファイル名変数が変更された時（リアルタイム更新）"""
        self.update_output_preview()
    
    def on_filename_manual_input(self, event):
        """ユーザーが手動でファイル名を入力した場合（レガシー）"""
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
    
    def auto_update_output_filename(self):
        """入力ファイルとモデル選択時に自動的に出力ファイル名を更新"""
        if not self.is_manual_filename and self.input_var.get() and self.selected_model.get():
            input_name = os.path.splitext(os.path.basename(self.input_var.get()))[0]
            model_name = self.selected_model.get()
            
            # Enhanced モードの場合は "_enhanced" を追加
            suffix = "_enhanced" if self.use_enhanced_conversion else ""
            auto_filename = f"{input_name}_{model_name}{suffix}"
            
            # 出力ファイル名フィールドを自動更新
            self.output_filename_var.set(auto_filename)
            self.log_message(f"Auto-generated filename: {auto_filename}.wav")
        
        # プレビューも更新
        self.update_output_preview()

    def update_output_preview(self):
        """出力ファイル名のプレビューを更新"""
        if hasattr(self, 'output_preview_label'):
            custom_filename = self.output_filename_var.get().strip()
            if custom_filename:
                # バリデーション
                invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
                has_invalid = any(char in custom_filename for char in invalid_chars)
                
                if has_invalid:
                    preview_text = f"❌ Invalid filename: {custom_filename}.wav"
                    color = self.colors['error']
                else:
                    if self.is_manual_filename:
                        preview_text = f"✓ {custom_filename}.wav (Manual)"
                        color = self.colors['success']
                    else:
                        preview_text = f"✓ {custom_filename}.wav (Auto)"
                        color = self.colors['info']
                    
                self.output_preview_label.config(text=preview_text, fg=color)
                return
            
            # ファイル名が空の場合
            if self.input_var.get() and self.selected_model.get():
                self.output_preview_label.config(text="[Click to auto-generate filename]", fg=self.colors['text_tertiary'])
            else:
                self.output_preview_label.config(text="[Select input and model]", fg=self.colors['text_tertiary'])
    
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
                suffix = "_enhanced" if self.use_enhanced_conversion else ""
                output_filename = f"{input_name}_{model_name}{suffix}.wav"
            
            output_path = os.path.join(self.output_var.get(), output_filename)
            
            # 出力ディレクトリを作成
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # プログレス更新
            self.update_progress(0, 10, "Initializing conversion...")
            
            # モデル情報を取得
            model_path = self.model_info['path']
            
            # 変換実行
            if self.use_enhanced_conversion and self.enhanced_converter:
                self.run_enhanced_conversion(input_file, output_path, model_path)
            else:
                self.run_standard_conversion(input_file, output_path, model_path)
            
            # 完了
            self.update_progress(6, 100, "Conversion completed!")
            time.sleep(0.5)
            
            # UIリセット
            self.root.after(0, self.conversion_complete, True, output_path)
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}", "ERROR")
            self.root.after(0, self.conversion_complete, False, str(e))
    
    def run_enhanced_conversion(self, input_file, output_path, model_path):
        """改良版変換処理"""
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
        
        # コマンド生成
        cmd = self.enhanced_converter.generate_enhanced_command(
            input_file, output_path, model_path, params
        )
        
        # サブプロセスで実行
        self.update_progress(3, 70, "Applying enhanced voice conversion...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.base_dir
        )
        
        if result.returncode == 0:
            self.update_progress(4, 90, "Finalizing enhanced output...")
            self.log_message("Enhanced conversion completed successfully!")
        else:
            raise RuntimeError(f"Enhanced conversion failed: {result.stderr}")
    
    def run_standard_conversion(self, input_file, output_path, model_path):
        """標準変換処理"""
        self.log_message("Starting standard voice conversion...")
        
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
        """プログレスバーとステージインジケーターを更新（オリジナルと同じ）"""
        if not hasattr(self, 'status_card'):
            return
            
        # 全体の進捗を計算（7ステージ）
        total_stages = 7
        stage_progress = (stage_index / total_stages) * 100
        current_stage_progress = (progress / 100) * (100 / total_stages)
        total_progress = stage_progress + current_stage_progress
        
        # UIを更新
        self.root.after(0, lambda: self._update_progress_ui(stage_index, total_progress, message))
        
    def _update_progress_ui(self, stage_index, total_progress, message):
        """UIスレッドでプログレスを更新（オリジナルと完全一致）"""
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
        
        # ステージインジケーターを更新（水平レイアウト版）
        if hasattr(self, 'stage_indicators'):
            for i, indicator in enumerate(self.stage_indicators):
                if i < stage_index:
                    # 完了したステージ（緑）
                    indicator['canvas'].itemconfig(indicator['circle'],
                                                 fill=self.colors['success'],
                                                 outline=self.colors['success'])
                    indicator['canvas'].itemconfig(indicator['number_text'],
                                                 fill='white')
                    indicator['name_label'].config(fg=self.colors['success'])
                elif i == stage_index:
                    # 現在のステージ（青）
                    indicator['canvas'].itemconfig(indicator['circle'],
                                                 fill=self.colors['accent_primary'],
                                                 outline=self.colors['accent_primary'])
                    indicator['canvas'].itemconfig(indicator['number_text'],
                                                 fill='white')
                    indicator['name_label'].config(fg=self.colors['accent_primary'])
                else:
                    # 未完了のステージ（グレー）
                    indicator['canvas'].itemconfig(indicator['circle'],
                                                 fill=self.colors['background_tertiary'],
                                                 outline=self.colors['border_subtle'])
                    indicator['canvas'].itemconfig(indicator['number_text'],
                                                 fill=self.colors['text_disabled'])
                    indicator['name_label'].config(fg=self.colors['text_tertiary'])
        
        # UIを更新
        self.root.update_idletasks()
    
    def conversion_complete(self, success, result):
        """変換完了時の処理"""
        self.converting = False
        
        # ステータスカードを非表示
        self.status_card.master.pack_forget()
        
        if success:
            self.log_message(f"Saved to: {result}", "SUCCESS")
            messagebox.showinfo("Success", f"Conversion completed!\nOutput saved to:\n{result}")
        else:
            self.log_message(f"Conversion failed: {result}", "ERROR")
            messagebox.showerror("Error", f"Conversion failed:\n{result}")
    
    def truncate_path(self, path, max_length=50):
        """長いパスを省略（オリジナルと同じ）"""
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


def main():
    """メイン実行関数"""
    try:
        print("=== Voice Converter Perfect Match GUI ===")
        print("100% exact UI reproduction + Enhanced features + Safe mode")
        
        root = tk.Tk()
        app = DarkModeGUI(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()