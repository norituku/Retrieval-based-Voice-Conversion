#!/usr/bin/env python3
"""
RVC Dark Mode GUI - 改善版（レイアウト最適化）
ウィンドウサイズとスクロール機能を改善したバージョン
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
import time

# RVC設定をインポート（存在する場合）
try:
    from rvc_config import POETRY_PYTHON_PATH, RVC_MODULE
    USE_HARDCODED_PATH = True
except ImportError:
    USE_HARDCODED_PATH = False

class DarkModeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter")
        
        # ダークモードデザイントークン（改善版）
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
        
        # アプリケーション設定
        self.setup_app_directories()
        
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
        
    def setup_styles(self):
        """カスタムttkスタイルの設定"""
        style = ttk.Style()
        
        # ダークテーマベース
        style.theme_use('default')
        
        # 背景色
        style.configure('.', 
                       background=self.colors['background_primary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       relief='flat')
        
        # スクロールバー
        style.configure('Dark.Vertical.TScrollbar',
                       background=self.colors['background_secondary'],
                       darkcolor=self.colors['background_tertiary'],
                       lightcolor=self.colors['background_tertiary'],
                       troughcolor=self.colors['background_primary'],
                       bordercolor=self.colors['background_primary'],
                       arrowcolor=self.colors['text_tertiary'],
                       relief='flat')
        
        style.map('Dark.Vertical.TScrollbar',
                 background=[('active', self.colors['background_elevated']),
                           ('pressed', self.colors['accent_primary'])])
        
        # ラベル
        style.configure('Title.TLabel',
                       font=('SF Pro Display', self.design_tokens['typography']['title1']['size']),
                       foreground=self.colors['text_primary'])
        
        style.configure('Heading.TLabel',
                       font=('SF Pro Display', self.design_tokens['typography']['headline']['size'], 'bold'),
                       foreground=self.colors['text_primary'])
        
        style.configure('Body.TLabel',
                       font=('SF Pro Display', self.design_tokens['typography']['body']['size']),
                       foreground=self.colors['text_secondary'])
        
        # ボタン
        style.configure('Primary.TButton',
                       font=('SF Pro Display', self.design_tokens['typography']['body']['size'], 'bold'),
                       background=self.colors['accent_primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       lightcolor=self.colors['accent_primary'],
                       darkcolor=self.colors['accent_primary'])
        
        style.map('Primary.TButton',
                 background=[('active', '#4A8FEF'), ('pressed', '#3A7FDF')])
        
        style.configure('Secondary.TButton',
                       font=('SF Pro Display', self.design_tokens['typography']['body']['size']),
                       background=self.colors['background_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid')
        
        # フレーム
        style.configure('Card.TFrame',
                       background=self.colors['surface_card'],
                       relief='flat',
                       borderwidth=1)
        
        # エントリー
        style.configure('Dark.TEntry',
                       fieldbackground=self.colors['background_secondary'],
                       borderwidth=1,
                       relief='solid',
                       insertcolor=self.colors['text_primary'])
        
        # プログレスバー
        style.configure('Dark.Horizontal.TProgressbar',
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['background_tertiary'],
                       bordercolor=self.colors['background_tertiary'],
                       lightcolor=self.colors['accent_primary'],
                       darkcolor=self.colors['accent_primary'])
        
    def setup_window(self):
        """ウィンドウの基本設定"""
        # 背景色
        self.root.configure(bg=self.colors['background_primary'])
        
        # 画面サイズを取得
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # ウィンドウサイズを画面サイズに応じて調整
        window_width = min(self.design_tokens['layout']['min_window_width'], int(screen_width * 0.9))
        window_height = min(650, int(screen_height * 0.85))  # デフォルト高さを650に設定
        
        # 画面中央に配置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(850, 480)  # 最小サイズをさらに小さく設定
        
        # macOS用の設定
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
        """メインUI構築"""
        # ナビゲーションバー
        self.create_navigation_bar()
        
        # メインコンテンツエリア
        self.main_content = tk.Frame(self.root, bg=self.colors['background_primary'])
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 2カラムレイアウト
        self.create_two_column_layout()
        
    def create_navigation_bar(self):
        """ナビゲーションバー"""
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
        
    def draw_gradient_icon(self, canvas):
        """グラデーションアイコンを描画"""
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
        """2カラムレイアウト"""
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
        """モデル選択サイドバー"""
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
        path_label = tk.Label(header, 
                            text=self.truncate_path(self.model_dir_var.get(), 30),
                            font=('SF Pro Mono', 9),
                            bg=self.colors['surface_sidebar'],
                            fg=self.colors['text_tertiary'])
        path_label.pack(anchor='w', pady=(2, 0))
        
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
        """スクロール可能なモデルリスト"""
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
        
        # スクロール設定
        self.model_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.model_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # パッキング
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイールでスクロール
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Linux用のマウスホイール
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
    def create_main_content(self):
        """メインコンテンツエリア"""
        # スクロール可能なキャンバスを作成
        self.canvas = tk.Canvas(self.right_column, 
                               bg=self.colors['background_primary'],
                               highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.right_column, orient="vertical", 
                                       command=self.canvas.yview,
                                       style='Dark.Vertical.TScrollbar')
        
        # スクロール可能フレーム
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['background_primary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # コンテンツウィンドウを作成
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # キャンバスのサイズ変更時にコンテンツの幅を調整
        def configure_canvas_window(event):
            canvas_width = event.width
            # スクロール可能フレームの幅をキャンバスの幅に設定
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind('<Configure>', configure_canvas_window)
        
        # マウスホイールでスクロール
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        # プラットフォーム別のマウスホイール設定
        if sys.platform == "darwin":  # macOS
            self.canvas.bind("<MouseWheel>", _on_mousewheel)
        else:  # Windows/Linux
            self.canvas.bind("<MouseWheel>", _on_mousewheel)
            self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
            self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # メインコンテンツコンテナ（超コンパクトなパディング）
        content_container = tk.Frame(self.scrollable_frame, bg=self.colors['background_primary'])
        content_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        
        # タイトルセクション
        self.create_title_section(content_container)
        
        # 入力セクション
        self.create_input_section(content_container)
        
        # 設定セクション
        self.create_settings_section(content_container)
        
        # ステータスセクション
        self.create_status_section(content_container)
        
    def create_title_section(self, parent):
        """タイトルセクション（コンパクト）"""
        title_frame = tk.Frame(parent, bg=self.colors['background_primary'])
        title_frame.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # 1行にタイトルとサブタイトルを配置
        tk.Label(title_frame, text="Voice Converter - AI Voice Conversion",
                font=('SF Pro Display', 16, 'bold'),
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(anchor='center')
        
    def create_input_section(self, parent):
        """入力セクション（横並び配置）"""
        # カードコンテナ
        input_card = self.create_card(parent, "Input & Convert")
        
        # 横並びレイアウト
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
        
        # 右側：変換ボタン
        right_section = tk.Frame(horizontal_layout, bg=self.colors['surface_card'])
        right_section.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # プライマリー変換ボタン
        convert_btn = self.create_button(right_section, 
                                       "Start\nConversion", 
                                       self.start_conversion,
                                       style='Primary',
                                       width=120,
                                       height=50)
        convert_btn.pack()
        
    def create_settings_section(self, parent):
        """設定セクション（横並び配置）"""
        settings_card = self.create_card(parent, "Settings")
        
        # 2カラムグリッドレイアウト
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
        
        # ユーザーの手動入力を検出
        self.filename_entry.bind('<KeyPress>', self.on_filename_manual_input)
        self.filename_entry.bind('<FocusIn>', self.on_filename_focus)
        
        # ファイル名変更時のバリデーション
        try:
            self.output_filename_var.trace_add('write', self.validate_filename)
        except AttributeError:
            # 古いPythonバージョン用のフォールバック
            self.output_filename_var.trace('w', self.validate_filename)
        
        # クリアボタン
        def clear_filename():
            self.output_filename_var.set("")
            self.is_manual_filename = False
            self.update_output_preview()
            
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
        
        # 右カラム：ピッチ設定
        right_column = tk.Frame(grid_container, bg=self.colors['surface_card'])
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # ピッチ設定（コンパクト版）
        self.create_compact_setting_control(right_column, "Pitch", self.pitch_var, 
                                          -12, 12, "semitones")

    def create_compact_setting_control(self, parent, label, variable, min_val, max_val, unit=""):
        """コンパクトな設定コントロール作成"""
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
        
    def create_setting_control(self, parent, label, variable, min_val, max_val, row, unit=""):
        """設定コントロール作成"""
        # コンテナフレーム
        control_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        control_frame.pack(fill=tk.X, pady=self.design_tokens['spacing']['xs'])
        
        # 上段：ラベルと値
        top_frame = tk.Frame(control_frame, bg=self.colors['surface_card'])
        top_frame.pack(fill=tk.X)
        
        # ラベル
        label_text = tk.Label(top_frame, text=label,
                            font=('SF Pro Display', 12),
                            bg=self.colors['surface_card'],
                            fg=self.colors['text_secondary'])
        label_text.pack(side=tk.LEFT)
        
        # 値表示
        def format_value():
            val = variable.get()
            if isinstance(variable, tk.DoubleVar):
                return f"{val:.2f} {unit}".strip()
            else:
                return f"{val} {unit}".strip()
        
        value_label = tk.Label(top_frame, 
                             text=format_value(),
                             font=('SF Pro Mono', 12, 'bold'),
                             bg=self.colors['surface_card'],
                             fg=self.colors['accent_primary'])
        value_label.pack(side=tk.RIGHT)
        
        # 下段：スライダー
        slider_frame = tk.Frame(control_frame, bg=self.colors['surface_card'])
        slider_frame.pack(fill=tk.X, pady=(2, 0))
        
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
                         width=12)
        slider.pack(fill=tk.X)
        
        # 値更新時のコールバック
        def update_value_label(*args):
            value_label.config(text=format_value())
        
        try:
            variable.trace_add('write', update_value_label)
        except AttributeError:
            variable.trace('w', update_value_label)
        
    def create_conversion_button(self, parent):
        """変換ボタンセクション"""
        button_frame = tk.Frame(parent, bg=self.colors['background_primary'])
        button_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['sm'], self.design_tokens['spacing']['xs']))
        
        # ボタンコンテナ（中央配置）
        button_container = tk.Frame(button_frame, bg=self.colors['background_primary'])
        button_container.pack()
        
        # プライマリー変換ボタン
        convert_btn = self.create_button(button_container, 
                                       "Start Conversion", 
                                       self.start_conversion,
                                       style='Primary',
                                       width=160,
                                       height=35)
        convert_btn.pack()
        
    def create_status_section(self, parent):
        """ステータスセクション"""
        # ステータスカード用のコンテナを作成
        self.status_container = tk.Frame(parent, bg=self.colors['background_primary'])
        self.status_container.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # 初期状態では非表示
        self.status_card = self.create_card(self.status_container, "Processing Status", visible=False)
        
        # プログレスバーコンテナ
        progress_container = tk.Frame(self.status_card, bg=self.colors['surface_card'])
        progress_container.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # パーセンテージラベル（右側）
        self.percentage_label = tk.Label(progress_container, 
                                       text="0%",
                                       font=('SF Pro Display', 14, 'bold'),
                                       bg=self.colors['surface_card'],
                                       fg=self.colors['accent_primary'])
        self.percentage_label.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['sm'], 0))
        
        # プログレスバー（確定的モード）
        self.progress = ttk.Progressbar(progress_container, 
                                      mode='determinate',
                                      maximum=100,
                                      style='Dark.Horizontal.TProgressbar')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ステージ情報コンテナ
        stage_info_container = tk.Frame(self.status_card, bg=self.colors['surface_card'])
        stage_info_container.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xs'], self.design_tokens['spacing']['xxs']))
        
        # 現在のステージ表示
        self.current_stage_label = tk.Label(stage_info_container, 
                                          text="",
                                          font=('SF Pro Display', 13, 'bold'),
                                          bg=self.colors['surface_card'],
                                          fg=self.colors['text_primary'])
        self.current_stage_label.pack(anchor='w')
        
        # ステータステキスト（詳細説明）
        self.status_label = tk.Label(stage_info_container, 
                                   text="",
                                   font=('SF Pro Display', 11),
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
        """各ステージのインジケーターを作成（水平配置）"""
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
        """ログセクション"""
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
        self.log_text.config(state=tk.NORMAL)  # 編集可能にしてコピーを許可
    
    def log_message(self, message, level="INFO"):
        """ログメッセージを追加"""
        # log_textがまだ存在しない場合は、コンソールに出力
        if not hasattr(self, 'log_text'):
            print(f"[{level}] {message}")
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)  # 最新のログまでスクロール
        
    def update_progress(self, stage_index, progress, message):
        """プログレスバーとステージインジケーターを更新"""
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
        """カスタムボタンを作成"""
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
        
        # ホバーエフェクト
        def on_enter(e):
            btn.config(bg=hover_color)
            
        def on_leave(e):
            btn.config(bg=bg_color)
            
        def on_click(e):
            btn.config(bg=active_color)
            # ウィジェットの存在確認とエラーハンドリングを追加
            def reset_color():
                try:
                    if btn.winfo_exists():
                        btn.config(bg=bg_color)
                except tk.TclError:
                    # ウィジェットが既に破棄されている場合は無視
                    pass
            
            # 親ウィンドウのafterメソッドを使用
            parent_window = btn.winfo_toplevel()
            try:
                parent_window.after(100, reset_color)
            except:
                # ウィンドウが破棄される場合に備えて
                pass
            
            # コマンドを実行
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
        settings_window.configure(bg='#0A0A0B')
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # ウィンドウを中央に配置
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() - settings_window.winfo_width()) // 2
        y = (settings_window.winfo_screenheight() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{x}+{y}")
        
        # メインフレーム
        main_frame = tk.Frame(settings_window, bg='#111113')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(main_frame, 
                              text="Model Directory Settings",
                              font=('SF Pro Display', 16, 'bold'),
                              bg='#111113',
                              fg='#FFFFFF')
        title_label.pack(pady=(0, 15))
        
        # 現在のパス表示
        current_frame = tk.Frame(main_frame, bg='#111113')
        current_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(current_frame, text="Current Model Directory:",
                font=('SF Pro Display', 12, 'bold'),
                bg='#111113',
                fg='#B8B8B8').pack(anchor='w')
        
        current_path_label = tk.Label(current_frame, 
                                     text=self.model_dir_var.get(),
                                     font=('SF Pro Mono', 10),
                                     bg='#111113',
                                     fg='#FFFFFF',
                                     wraplength=450)
        current_path_label.pack(anchor='w', pady=(5, 0))
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame, bg='#111113')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # フォルダ選択ボタン
        def browse_model_dir():
            try:
                new_dir = filedialog.askdirectory(
                    title="Select Model Directory",
                    initialdir=self.model_dir_var.get()
                )
                if new_dir:
                    self.model_dir_var.set(new_dir)
                    current_path_label.config(text=new_dir)
            except Exception as e:
                print(f"Error selecting directory: {e}")
        
        # ボタンコンテナフレーム
        buttons_container = tk.Frame(button_frame, bg='#111113')
        buttons_container.pack(fill=tk.X)
        
        # 左側のボタンフレーム
        left_btn_frame = tk.Frame(buttons_container, bg='#111113')
        left_btn_frame.pack(side=tk.LEFT)
        
        # Browse Folderボタン
        browse_btn = self.create_button(left_btn_frame, "Browse Folder", browse_model_dir, style='Secondary')
        browse_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 右側のボタンフレーム
        right_btn_frame = tk.Frame(buttons_container, bg='#111113')
        right_btn_frame.pack(side=tk.RIGHT)
        
        # キャンセル・OK ボタン
        def apply_settings():
            try:
                self.model_dir = self.model_dir_var.get()  # model_dirを更新
                self.save_settings()
                self.load_models()  # モデルを再読み込み
                # 簡単な通知
                self.log_message(f"Model directory updated: {self.model_dir_var.get()}")
                settings_window.destroy()
            except Exception as e:
                print(f"Error applying settings: {e}")
                settings_window.destroy()
            
        def cancel_settings():
            try:
                # 変更をリセット
                self.load_settings()
                settings_window.destroy()
            except Exception as e:
                print(f"Error canceling settings: {e}")
                settings_window.destroy()
        
        # Cancelボタン
        cancel_btn = self.create_button(right_btn_frame, "Cancel", cancel_settings, style='Secondary')
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Applyボタン
        ok_btn = self.create_button(right_btn_frame, "Apply", apply_settings, style='Primary')
        ok_btn.pack(side=tk.LEFT)
    
    def on_filename_manual_input(self, event):
        """ユーザーがキーボードで入力したことを検出"""
        # 特殊キー（矢印キー、Tab等）は無視
        if event.keysym not in ['Left', 'Right', 'Up', 'Down', 'Tab', 'Return', 'Escape']:
            self.is_manual_filename = True
            
    def on_filename_focus(self, event):
        """フィールドにフォーカスが当たった時の処理"""
        # フィールドが空の場合は手動入力フラグをリセット
        if not self.output_filename_var.get().strip():
            self.is_manual_filename = False
    
    def on_input_file_changed(self):
        """入力ファイルが変更された時の処理"""
        # 新しい入力ファイルが選択された場合、手動入力フラグをリセット
        self.is_manual_filename = False
        self.update_output_preview()
    
    def validate_filename(self, *args):
        """ファイル名のバリデーション"""
        filename = self.output_filename_var.get()
        
        # 不正な文字をチェック
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        has_invalid = any(char in filename for char in invalid_chars)
        
        # エントリの色を変更してバリデーション結果を表示
        if has_invalid or not filename.strip():
            self.filename_entry.config(bg='#4A2C2A')  # 薄い赤色
        else:
            self.filename_entry.config(bg=self.colors['background_secondary'])
            
        # プレビューを更新
        self.update_output_preview()
        
    def search_models_recursive(self, directory):
        """再帰的にモデルファイルを検索"""
        models = []
        
        if not os.path.exists(directory):
            return models
            
        for root, dirs, files in os.walk(directory):
            # params.jsonがある場合（構造化されたモデル）
            if 'params.json' in files:
                params_file = os.path.join(root, 'params.json')
                try:
                    with open(params_file, 'r', encoding='utf-8') as f:
                        params = json.load(f)
                    
                    # .pthファイルを探す
                    pth_files = [f for f in files if f.endswith('.pth')]
                    if pth_files:
                        model_file = pth_files[0]
                        
                        # インデックスファイルの確認
                        index_files = [f for f in files if f.endswith('.index')]
                        has_index = len(index_files) > 0
                        
                        model_name = params.get('name', os.path.basename(root))
                        relative_path = os.path.relpath(root, directory)
                        
                        models.append({
                            'name': f"{model_name} ({relative_path})" if relative_path != '.' else model_name,
                            'file': os.path.join(root, model_file),
                            'config': params_file,
                            'folder': os.path.basename(root),
                            'params': params,
                            'has_index': has_index,
                            'index_file': os.path.join(root, index_files[0]) if has_index else None,
                            'path': root
                        })
                        
                except Exception as e:
                    print(f"Error loading model from {root}: {e}")
            
            # 単体の.pthファイル（構造化されていないモデル）
            else:
                pth_files = [f for f in files if f.endswith('.pth') and not f.startswith(('hubert', 'rmvpe'))]
                for pth_file in pth_files:
                    model_name = os.path.splitext(pth_file)[0]
                    relative_path = os.path.relpath(root, directory)
                    
                    # 同じ名前のインデックスファイルがあるかチェック
                    index_file_name = f"{model_name}.index"
                    has_index = index_file_name in files
                    
                    full_name = f"{model_name} ({relative_path})" if relative_path != '.' else model_name
                    
                    models.append({
                        'name': full_name,
                        'file': os.path.join(root, pth_file),
                        'config': None,
                        'folder': None,
                        'params': {},
                        'has_index': has_index,
                        'index_file': os.path.join(root, index_file_name) if has_index else None,
                        'path': root
                    })
        
        return models

    def load_models(self):
        """モデルの読み込み（再帰的検索）"""
        # 既存のモデルカードをクリア
        if hasattr(self, 'model_cards'):
            for card_frame, inner, model in self.model_cards:
                card_frame.destroy()
            self.model_cards = []
            
        # モデルディレクトリから再帰的に検索
        self.model_dir = self.model_dir_var.get()
        self.log_message(f"Loading models from {self.model_dir} (recursive search)")
        
        models = self.search_models_recursive(self.model_dir)
        
        # 名前でソート
        models.sort(key=lambda x: x['name'].lower())
        
        # ログに総数を記録
        self.log_message(f"Total models found: {len(models)}")
        
        # モデルカードを作成
        for i, model in enumerate(models):
            self.create_model_card(model, i)
            
        if models:
            self.log_message(f"Models loaded successfully from {len(set(m['path'] for m in models))} directories")
                
    def create_model_card(self, model, index):
        """モデルカードUI"""
        card_frame = tk.Frame(self.model_frame, 
                            bg=self.colors['background_secondary'],
                            relief='flat')
        card_frame.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # 内部パディング
        inner = tk.Frame(card_frame, bg=self.colors['background_secondary'])
        inner.pack(fill=tk.BOTH, expand=True, 
                  padx=self.design_tokens['spacing']['xs'],
                  pady=self.design_tokens['spacing']['xs'])
        
        # モデル名
        name_label = tk.Label(inner, 
                             text=model['name'],
                             font=('SF Pro Display', 13, 'bold'),
                             bg=self.colors['background_secondary'],
                             fg=self.colors['text_primary'],
                             anchor='w')
        name_label.pack(fill=tk.X)
        
        # 追加情報（1行にまとめる）
        info_parts = []
        if model.get('params'):
            if 'sample_rate' in model['params']:
                info_parts.append(f"{model['params']['sample_rate']}Hz")
        
        # インデックスバッジ
        if model.get('has_index'):
            info_parts.append("✓ Index")
            
        info_label = None
        if info_parts:
            info_label = tk.Label(inner, 
                                text=' • '.join(info_parts),
                                font=('SF Pro Display', 10),
                                bg=self.colors['background_secondary'],
                                fg=self.colors['text_secondary'] if not model.get('has_index') else self.colors['success'])
            info_label.pack(anchor='w')
        
        # クリック可能にする
        def select_model():
            self.selected_model.set(model['name'])
            self.on_model_selected(model)
            # 選択状態の視覚的フィードバック
            self.update_model_selection(card_frame)
            
        # 全体をクリック可能に（利用可能なウィジェットのみ）
        clickable_widgets = [card_frame, inner, name_label]
        if info_label:
            clickable_widgets.append(info_label)
            
        for widget in clickable_widgets:
            widget.bind('<Button-1>', lambda e: select_model())
            widget.config(cursor='hand2')
        
        # ホバーエフェクト
        def on_enter(e):
            if self.selected_model.get() != model['name']:
                card_frame.config(bg=self.colors['background_tertiary'])
                inner.config(bg=self.colors['background_tertiary'])
                for widget in inner.winfo_children():
                    widget.config(bg=self.colors['background_tertiary'])
            
        def on_leave(e):
            if self.selected_model.get() != model['name']:
                card_frame.config(bg=self.colors['background_secondary'])
                inner.config(bg=self.colors['background_secondary'])
                for widget in inner.winfo_children():
                    widget.config(bg=self.colors['background_secondary'])
            
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
        
        # カードを保存（選択状態の更新用）
        if not hasattr(self, 'model_cards'):
            self.model_cards = []
        self.model_cards.append((card_frame, inner, model))
        
        # デフォルト選択
        if index == 0:
            select_model()
            
    def on_model_selected(self, model):
        """モデル選択時の処理"""
        self.model_info = model
        # 手動入力がない場合のみ、出力ファイル名を更新
        if not self.is_manual_filename:
            self.update_output_preview()
        else:
            # 手動入力がある場合はプレビューのみ更新
            self.update_output_preview()
        
    def update_output_preview(self):
        """出力ファイル名のプレビューを更新"""
        if hasattr(self, 'output_preview_label'):
            # カスタムファイル名が設定されている場合
            custom_filename = self.output_filename_var.get().strip()
            if custom_filename and self.is_manual_filename:
                # バリデーション結果に基づいてプレビュー色を変更
                invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
                has_invalid = any(char in custom_filename for char in invalid_chars)
                
                if has_invalid:
                    preview_text = f"❌ Invalid filename: {custom_filename}.wav"
                    color = self.colors['error']
                else:
                    preview_text = f"✓ {custom_filename}.wav"
                    color = self.colors['success']
                    
                self.output_preview_label.config(text=preview_text, fg=color)
                return  # 手動入力の場合はここで終了（自動上書きを防ぐ）
                
            # 自動生成プレビュー（入力ファイル名+モデル名ベース）
            elif self.input_var.get() and self.selected_model.get():
                input_name = os.path.splitext(os.path.basename(self.input_var.get()))[0]
                safe_model_name = self.selected_model.get()
                for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '(', ')', '\n', '\r', '\t']:
                    safe_model_name = safe_model_name.replace(char, '_')
                safe_model_name = '_'.join(filter(None, safe_model_name.split('_')))
                
                preview_name = f"Auto: {input_name}_{safe_model_name}.wav"
                self.output_preview_label.config(text=preview_name, fg=self.colors['text_tertiary'])
            elif self.selected_model.get():
                safe_model_name = self.selected_model.get()
                for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '(', ')', '\n', '\r', '\t']:
                    safe_model_name = safe_model_name.replace(char, '_')
                safe_model_name = '_'.join(filter(None, safe_model_name.split('_')))
                
                preview_name = f"Auto: {safe_model_name}.wav"
                self.output_preview_label.config(text=preview_name, fg=self.colors['text_tertiary'])
            else:
                self.output_preview_label.config(text="[Select input file and model first]", 
                                                fg=self.colors['text_tertiary'])
                
            # デフォルトファイル名を設定（手動入力がない場合のみ）
            if not self.is_manual_filename:
                if self.input_var.get() and self.selected_model.get():
                    input_name = os.path.splitext(os.path.basename(self.input_var.get()))[0]
                    safe_model_name = self.selected_model.get()
                    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '(', ')', '\n', '\r', '\t']:
                        safe_model_name = safe_model_name.replace(char, '_')
                    safe_model_name = '_'.join(filter(None, safe_model_name.split('_')))
                    
                    # 入力ファイル名+モデル名をデフォルトとして設定
                    suggested_name = f"{input_name}_{safe_model_name}"
                    self.output_filename_var.set(suggested_name)
                elif self.input_var.get() and not self.selected_model.get():
                    # 入力ファイルのみ選択されている場合
                    input_name = os.path.splitext(os.path.basename(self.input_var.get()))[0]
                    self.output_filename_var.set(input_name)
                elif not self.input_var.get() and self.selected_model.get():
                    # モデルのみ選択されている場合
                    safe_model_name = self.selected_model.get()
                    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '(', ')', '\n', '\r', '\t']:
                        safe_model_name = safe_model_name.replace(char, '_')
                    safe_model_name = '_'.join(filter(None, safe_model_name.split('_')))
                    self.output_filename_var.set(safe_model_name)
        
    def update_model_selection(self, selected_card):
        """モデル選択状態の視覚的更新"""
        if hasattr(self, 'model_cards'):
            for card_frame, inner, model in self.model_cards:
                if card_frame == selected_card:
                    # 選択されたカード
                    bg = self.colors['accent_primary']
                    card_frame.config(bg=bg)
                    inner.config(bg=bg)
                    for widget in inner.winfo_children():
                        widget.config(bg=bg)
                        if isinstance(widget, tk.Label):
                            # テキストカラーを白に
                            widget.config(fg='white')
                else:
                    # 選択されていないカード
                    bg = self.colors['background_secondary']
                    card_frame.config(bg=bg)
                    inner.config(bg=bg)
                    for widget in inner.winfo_children():
                        widget.config(bg=bg)
                        if isinstance(widget, tk.Label):
                            # 元のテキストカラーに戻す
                            if widget['font'][1] == 14:  # タイトル
                                widget.config(fg=self.colors['text_primary'])
                            elif widget['font'][1] == 10:  # サブテキスト
                                widget.config(fg=self.colors['text_secondary'])
                            elif widget['font'][1] == 9:  # ファイル名
                                widget.config(fg=self.colors['text_tertiary'])
        
    def browse_input(self):
        """入力ファイルの選択"""
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.m4a *.flac *.ogg *.aif *.aiff"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.input_var.set(filename)
            self.display_file_info(filename)
            # 入力ファイル変更時に出力ファイル名を更新
            self.on_input_file_changed()
            
    def display_file_info(self, filename):
        """選択されたファイル情報を表示"""
        # 既存の情報をクリア
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
            
        # ファイル情報表示
        info_container = tk.Frame(self.file_info_frame, 
                                bg=self.colors['background_tertiary'])
        info_container.pack(fill=tk.X)
        
        # パディング
        inner = tk.Frame(info_container, bg=self.colors['background_tertiary'])
        inner.pack(fill=tk.BOTH, expand=True, 
                  padx=self.design_tokens['spacing']['sm'],
                  pady=self.design_tokens['spacing']['xs'])
        
        # ファイル名とパスを1行で表示
        file_info = tk.Frame(inner, bg=self.colors['background_tertiary'])
        file_info.pack(fill=tk.X)
        
        # ファイル名
        file_name = os.path.basename(filename)
        name_label = tk.Label(file_info, text=file_name,
                            font=('SF Pro Display', 12, 'bold'),
                            bg=self.colors['background_tertiary'],
                            fg=self.colors['text_primary'])
        name_label.pack(side=tk.LEFT)
        
        # クリアボタン
        clear_btn = self.create_button(file_info, "×", 
                                     self.clear_input, 
                                     style='Secondary')
        clear_btn.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # 出力プレビューを更新
        self.update_output_preview()
        
    def browse_output(self):
        """出力ディレクトリの選択"""
        dirname = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_var.get() if self.output_var.get() else os.path.expanduser("~")
        )
        
        if dirname:
            self.output_var.set(dirname)
            self.output_path_label.config(text=self.truncate_path(dirname, 50))
            
    def clear_input(self):
        """入力をクリア"""
        self.input_var.set("")
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
        self.update_output_preview()
            
    def start_conversion(self):
        """変換処理の開始"""
        if not self.input_var.get():
            self.log_message("No input file selected", "WARNING")
            messagebox.showwarning("Warning", "Please select an input file")
            return
            
        if not self.selected_model.get():
            self.log_message("No model selected", "WARNING")  
            messagebox.showwarning("Warning", "Please select a voice model")
            return
        
        # ログに開始メッセージ
        self.log_message(f"Starting conversion with model: {self.selected_model.get()}")
            
        # 出力ディレクトリの確認と作成
        output_dir = self.output_var.get()
        if not output_dir:
            output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "VoiceConverter_Output")
            self.output_var.set(output_dir)
            
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            self.show_error_log(f"Failed to create output directory: {e}")
            return
            
        # 出力ファイル名の生成
        custom_filename = self.output_filename_var.get().strip()
        
        if custom_filename:
            # カスタムファイル名のバリデーション
            invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
            if any(char in custom_filename for char in invalid_chars):
                self.log_message("Invalid characters in filename", "ERROR")
                messagebox.showerror("Error", "Filename contains invalid characters: / \\ : * ? \" < > |")
                return
            output_filename = f"{custom_filename}.wav"
        else:
            # 自動生成ファイル名: {入力ファイル名}_{モデル名}.wav
            input_file = self.input_var.get()
            input_name = os.path.splitext(os.path.basename(input_file))[0]
            
            # モデル名から安全なファイル名を作成（特殊文字を除去）
            safe_model_name = self.selected_model.get()
            # ファイル名に使えない文字を置換
            for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '(', ')', '\n', '\r', '\t']:
                safe_model_name = safe_model_name.replace(char, '_')
            # 連続するアンダースコアを1つに
            safe_model_name = '_'.join(filter(None, safe_model_name.split('_')))
            
            output_filename = f"{input_name}_{safe_model_name}.wav"
        
        # ファイルが既に存在する場合は番号を追加
        output_path = os.path.join(output_dir, output_filename)
        counter = 1
        base_name = os.path.splitext(output_filename)[0]
        while os.path.exists(output_path):
            output_filename = f"{base_name}_{counter}.wav"
            output_path = os.path.join(output_dir, output_filename)
            counter += 1
        
        self.output_file_path = output_path
        
        # ステータスカードを表示
        self.status_card.master.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['md']))
        
        # プログレスバーをリセット
        self.progress['value'] = 0
        self.percentage_label.config(text="0%")
        self.current_stage_label.config(text="変換処理を開始しています...")
        self.status_label.config(text=f"出力先: {output_filename}")
        
        # 変換処理をバックグラウンドで実行
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
        
    def run_conversion(self):
        """実際の変換処理（内蔵プログレスバー使用）"""
        try:
            # 1. 初期化
            self.update_progress(0, 0, "プロジェクトとモデルの初期化中...")
            
            # プロジェクトディレクトリを確認
            project_dir = self.base_dir
            if project_dir.endswith('/Resources'):
                possible_dirs = [
                    "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion",
                    os.path.expanduser("~/Retrieval-based-Voice-Conversion"),
                ]
                for dir_path in possible_dirs:
                    if os.path.exists(os.path.join(dir_path, "pyproject.toml")):
                        project_dir = dir_path
                        break
            
            time.sleep(0.5)  # 視覚的フィードバックのため
            self.update_progress(0, 100, "初期化完了")
            
            # 2. データ読み込み
            self.update_progress(1, 0, "音声ファイルとモデルデータを読み込み中...")
            
            model_id = self.model_info.get('folder') or ''
            model_path = os.path.join(self.model_dir, model_id) if model_id else os.path.dirname(self.model_info['file'])
            
            index_file = self.model_info.get('index_file')
            if not index_file and os.path.exists(model_path):
                index_files = [f for f in os.listdir(model_path) if f.endswith('.index')]
                if index_files:
                    index_file = os.path.join(model_path, index_files[0])
            
            time.sleep(0.5)
            self.update_progress(1, 100, "データ読み込み完了")
            
            # 3. 前処理
            self.update_progress(2, 0, "音声データの前処理を開始...")
            
            hubert_path = os.path.join(self.model_dir, "hubert_base.pt")
            if not os.path.exists(hubert_path):
                alt_hubert = os.path.join(project_dir, "model_dir", "hubert_base.pt")
                if os.path.exists(alt_hubert):
                    hubert_path = alt_hubert
            
            poetry_available = subprocess.run(
                ["which", "poetry"],
                capture_output=True,
                text=True
            ).returncode == 0
            
            if poetry_available:
                # Poetryのパスを確認
                poetry_path = subprocess.run(
                    ["which", "poetry"],
                    capture_output=True,
                    text=True
                ).stdout.strip()
                self.log_message(f"Using Poetry at: {poetry_path}")
                
                # Poetry環境情報を取得
                try:
                    env_info = subprocess.run(
                        ["poetry", "env", "info", "--path"],
                        capture_output=True,
                        text=True,
                        cwd=project_dir
                    )
                    if env_info.returncode == 0:
                        self.log_message(f"Poetry env: {env_info.stdout.strip()}")
                except:
                    pass
                
                # ハードコーディングされたパスを使用（利用可能な場合）
                if USE_HARDCODED_PATH and os.path.exists(POETRY_PYTHON_PATH):
                    cmd_array = [
                        POETRY_PYTHON_PATH, "-m", RVC_MODULE, "infer",
                        "-m", self.model_info["file"],
                        "-i", self.input_var.get(),
                        "-o", self.output_file_path,
                        "-fu", str(self.pitch_var.get()),
                        "-fm", self.f0_method_var.get(),
                        "-ir", str(self.index_rate_var.get()),
                        "-fr", str(self.filter_radius_var.get()),
                        "-p", str(self.protect_var.get()),
                        "-rmr", str(self.rms_mix_rate_var.get())
                    ]
                    self.log_message(f"Using hardcoded Python path: {POETRY_PYTHON_PATH}")
                else:
                    # poetry runを使用してRVCを実行（依存関係が正しくインストールされている）
                    cmd_array = [
                        "poetry", "run", "rvc", "infer",
                        "-m", self.model_info["file"],
                        "-i", self.input_var.get(),
                        "-o", self.output_file_path,
                        "-fu", str(self.pitch_var.get()),
                        "-fm", self.f0_method_var.get(),
                        "-ir", str(self.index_rate_var.get()),
                        "-fr", str(self.filter_radius_var.get()),
                        "-p", str(self.protect_var.get()),
                        "-rmr", str(self.rms_mix_rate_var.get())
                    ]
                    self.log_message("Using poetry run for RVC execution")
                
                if index_file and os.path.exists(index_file):
                    cmd_array.extend(["-if", index_file])
                
                if os.path.exists(hubert_path):
                    cmd_array.extend(["--hubert_model_path", hubert_path])
                
                env = os.environ.copy()
                env['PYTHONPATH'] = project_dir
                env['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                env['rmvpe_root'] = os.path.join(
                    self.model_dir if os.path.exists(os.path.join(self.model_dir, 'rmvpe.pt')) 
                    else os.path.join(project_dir, 'model_dir')
                )
                # Conda環境変数をクリア
                env.pop('CONDA_DEFAULT_ENV', None)
                env.pop('CONDA_PREFIX', None)
                env.pop('CONDA_PYTHON_EXE', None)
                env.pop('CONDA_EXE', None)
                env.pop('CONDA_PROMPT_MODIFIER', None)
                env.pop('_CE_CONDA', None)
                env.pop('_CE_M', None)
                
                self.update_progress(2, 100, "前処理完了")
                
                # 4-6. RVC推論の実行
                self._run_rvc_with_progress(cmd_array, env, project_dir)
                
                # 7. 出力保存
                self.update_progress(6, 0, "変換結果を保存中...")
                time.sleep(0.5)
                self.update_progress(6, 100, "保存完了")
                
                self.root.after(0, lambda: self.conversion_complete())
                time.sleep(1.5)
            else:
                raise RuntimeError("Poetry not found. Please install Poetry first.")
                    
        except Exception as e:
            # エラーメッセージを直接キャプチャ
            error_msg = str(e)
            self.root.after(0, lambda: self.conversion_error(error_msg))



    def _run_rvc_with_progress(self, cmd_array, env, project_dir):
        """RVC推論をプログレス追跡しながら実行（内蔵プログレスバー使用）"""
        
        # ステージ3: 特徴抽出を開始
        self.update_progress(3, 0, "音声の特徴を抽出中...")
        
        process = subprocess.Popen(
            cmd_array,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env,
            cwd=project_dir
        )
        
        current_stage = 3  # 特徴抽出ステージ
        line_count = 0
        total_lines_estimate = 100  # 推定行数
        
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.strip()
                if line:
                    self.log_message(line)
                    line_count += 1
                    
                    # 行数に基づく進捗更新
                    stage_progress = min((line_count / total_lines_estimate) * 100, 100)
                    
                    # キーワードによる進捗とステージの推定
                    if "Loading" in line or "loading" in line:
                        self.update_progress(current_stage, 30, "モデルを読み込み中...")
                    elif "Extract" in line or "extract" in line:
                        if current_stage == 3:
                            self.update_progress(3, 70, "特徴抽出を実行中...")
                    elif "Process" in line or "process" in line:
                        if current_stage < 4:
                            # ステージ4: モデル推論に移行
                            self.update_progress(3, 100, "特徴抽出完了")
                            current_stage = 4
                            self.update_progress(4, 0, "AIモデルで音声を変換中...")
                        self.update_progress(4, 50, "音声変換を処理中...")
                    elif "Generate" in line or "generate" in line:
                        self.update_progress(4, 80, "音声を生成中...")
                    elif "Save" in line or "save" in line or "Write" in line or "write" in line:
                        if current_stage < 5:
                            # ステージ5: 後処理に移行
                            self.update_progress(4, 100, "音声変換完了")
                            current_stage = 5
                            self.update_progress(5, 0, "音質の最適化を実行中...")
                        self.update_progress(5, 90, "最適化処理中...")
                    
                    # 進捗の詳細表示
                    if line_count % 5 == 0:  # 5行ごとに更新
                        if current_stage == 3:
                            progress = min(stage_progress, 90)
                            self.update_progress(3, progress, f"特徴抽出中... ({line_count}行処理)")
                        elif current_stage == 4:
                            progress = min(stage_progress, 90)
                            self.update_progress(4, progress, f"音声変換中... ({line_count}行処理)")
                        elif current_stage == 5:
                            progress = min(stage_progress, 90)
                            self.update_progress(5, progress, f"後処理中... ({line_count}行処理)")
                        
        process.wait()
        
        # エラーチェック
        if process.returncode != 0:
            # エラー詳細を取得
            error_msg = f"RVC inference failed with return code: {process.returncode}"
            self.log_message(error_msg, "ERROR")
            raise RuntimeError(error_msg)
        
        # 処理完了を確認
        if current_stage == 3:
            self.update_progress(3, 100, "特徴抽出完了")
            self.update_progress(4, 100, "音声変換完了")
            self.update_progress(5, 100, "後処理完了")
        elif current_stage == 4:
            self.update_progress(4, 100, "音声変換完了")
            self.update_progress(5, 100, "後処理完了")
        elif current_stage == 5:
            self.update_progress(5, 100, "後処理完了")

    def conversion_error(self, error_msg):
        """変換エラー時の処理"""
        self.progress.stop()
        self.status_label.config(text="Conversion failed!")
        
        # エラーをログに表示
        self.log_message(error_msg, "ERROR")
        
        # エラーメッセージをコピー可能なウィンドウでも表示
        self.show_error_log(error_msg)
        
        self.root.after(2000, lambda: self.status_card.master.pack_forget())
    
    def show_error_log(self, error_msg):
        """エラーログをコピー可能なウィンドウで表示"""
        # エラーログウィンドウを作成
        error_window = tk.Toplevel(self.root)
        error_window.title("Error Log")
        error_window.geometry("800x400")
        error_window.configure(bg=self.colors['background_primary'])
        
        # ウィンドウのスタイリング
        style_frame = tk.Frame(error_window, bg=self.colors['background_secondary'], bd=0)
        style_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトルラベル
        title_label = tk.Label(style_frame, 
                              text="Error Details (You can copy this text)",
                              font=(self.fonts['family'], 14, 'bold'),
                              bg=self.colors['background_secondary'],
                              fg=self.colors['text_primary'])
        title_label.pack(pady=(0, 10))
        
        # テキストウィジェット（コピー可能）
        text_frame = tk.Frame(style_frame, bg=self.colors['background_tertiary'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(text_frame, style='Dark.Vertical.TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # テキストエリア
        error_text = tk.Text(text_frame,
                           wrap=tk.WORD,
                           bg=self.colors['background_tertiary'],
                           fg=self.colors['text_primary'],
                           font=(self.fonts['mono'], 11),
                           relief=tk.FLAT,
                           padx=15,
                           pady=15,
                           yscrollcommand=scrollbar.set,
                           selectbackground=self.colors['accent_primary'],
                           selectforeground=self.colors['text_primary'])
        error_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=error_text.yview)
        
        # エラーメッセージを挿入
        error_text.insert(tk.END, error_msg)
        error_text.config(state=tk.NORMAL)  # 編集可能にしてコピーを許可
        
        # 閉じるボタン
        close_button = tk.Button(style_frame,
                               text="Close",
                               font=(self.fonts['family'], 12),
                               bg=self.colors['accent_primary'],
                               fg=self.colors['text_primary'],
                               activebackground=self.colors['accent_secondary'],
                               activeforeground=self.colors['text_primary'],
                               relief=tk.FLAT,
                               padx=30,
                               pady=8,
                               command=error_window.destroy)
        close_button.pack(pady=(10, 0))
        
        # ウィンドウを最前面に
        error_window.lift()
        error_window.attributes('-topmost', True)
        error_window.after(100, lambda: error_window.attributes('-topmost', False))
        
    def conversion_complete(self):
        """変換完了時の処理"""
        self.progress.stop()
        self.status_label.config(text=f"✓ Conversion completed successfully!\n{os.path.basename(self.output_file_path)}",
                               fg=self.colors['success'])
        
        # 成功メッセージと開くオプション
        result = messagebox.askyesno("Success", 
                                    f"Voice conversion completed!\n\nFile saved as:\n{os.path.basename(self.output_file_path)}\n\nOpen output folder?",
                                    icon='info')
        
        if result:
            # 出力フォルダを開く
            output_dir = os.path.dirname(self.output_file_path)
            if sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", output_dir])
            elif sys.platform == "win32":  # Windows
                subprocess.Popen(["explorer", output_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", output_dir])
        
        # ステータスカードを隠す
        self.root.after(3000, lambda: self.status_card.master.pack_forget())


def main():
    root = tk.Tk()
    app = DarkModeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
