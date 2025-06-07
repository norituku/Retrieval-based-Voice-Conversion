#!/usr/bin/env python3
"""
RVC Dark Mode GUI - 改善版（構造化・整理版）
セクション分割とコード整理を実装したバージョン
"""

# =============================================================================
# インポートセクション
# =============================================================================
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
import logging

# RVC設定をインポート（存在する場合）
try:
    from rvc_config import POETRY_PYTHON_PATH, RVC_MODULE
    USE_HARDCODED_PATH = True
except ImportError:
    USE_HARDCODED_PATH = False

# =============================================================================
# 定数定義セクション
# =============================================================================

# デザイントークン定数
DESIGN_TOKENS = {
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

# フォントファミリー定数
FONTS = {
    'family': 'Arial',
    'mono': 'Courier'
}

# デフォルト設定値
DEFAULT_SETTINGS = {
    'pitch': 0,
    'f0_method': 'rmvpe',
    'index_rate': 1.0,
    'filter_radius': 3,
    'rms_mix_rate': 0.25,
    'protect': 0.33
}

# ファイルダイアログ設定
AUDIO_FILE_TYPES = [
    ("Audio files", "*.mp3 *.wav *.flac *.m4a *.ogg *.opus *.aac"),
    ("All files", "*.*")
]

# ログレベル設定
LOG_LEVELS = {
    'DEBUG': {'color': '#808080', 'prefix': '[DEBUG]'},
    'INFO': {'color': '#B8B8B8', 'prefix': '[INFO]'},
    'WARNING': {'color': '#FFD23F', 'prefix': '[WARNING]'},
    'ERROR': {'color': '#FF6B6B', 'prefix': '[ERROR]'},
    'SUCCESS': {'color': '#52E88C', 'prefix': '[SUCCESS]'}
}

# =============================================================================
# ヘルパー関数セクション
# =============================================================================

def truncate_path(path, max_length=50):
    """パスを指定された長さに短縮"""
    if not path or len(path) <= max_length:
        return path
    
    path_obj = Path(path)
    name = path_obj.name
    
    if len(name) > max_length - 3:
        return f"...{name[-(max_length-3):]}"
    
    remaining_length = max_length - len(name) - 3
    parent_path = str(path_obj.parent)
    
    if remaining_length > 0:
        return f"...{parent_path[-remaining_length:]}/{name}"
    else:
        return f".../{name}"

def get_file_info(filepath):
    """ファイル情報を取得"""
    try:
        file_stats = os.stat(filepath)
        file_size = file_stats.st_size
        
        # ファイルサイズを人間が読みやすい形式に変換
        for unit in ['B', 'KB', 'MB', 'GB']:
            if file_size < 1024.0:
                size_str = f"{file_size:.1f} {unit}"
                break
            file_size /= 1024.0
        else:
            size_str = f"{file_size:.1f} TB"
        
        # ファイル拡張子を取得
        extension = os.path.splitext(filepath)[1].upper()
        if extension:
            extension = extension[1:]  # ドットを削除
        
        return {
            'size': size_str,
            'extension': extension,
            'name': os.path.basename(filepath)
        }
    except:
        return None

def create_gradient_icon(canvas, colors, size=40):
    """グラデーションアイコンを描画"""
    steps = 10
    for i in range(steps):
        color_ratio = i / (steps - 1)
        x1 = i * (size / steps)
        x2 = (i + 1) * (size / steps)
        
        # 色の補間
        r1 = int(colors[0][1:3], 16)
        g1 = int(colors[0][3:5], 16)
        b1 = int(colors[0][5:7], 16)
        
        r2 = int(colors[1][1:3], 16)
        g2 = int(colors[1][3:5], 16)
        b2 = int(colors[1][5:7], 16)
        
        r = int(r1 + (r2 - r1) * color_ratio)
        g = int(g1 + (g2 - g1) * color_ratio)
        b = int(b1 + (b2 - b1) * color_ratio)
        
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_rectangle(x1, 0, x2, size, fill=color, outline='')

# =============================================================================
# メインGUIクラス
# =============================================================================

class DarkModeGUI:
    """
    Voice Converter Dark Mode GUI
    機能別にセクション分割された改善版
    """
    
    # =========================================================================
    # 初期化・セットアップセクション
    # =========================================================================
    
    def __init__(self, root):
        """コンストラクタ"""
        logging.info("DarkModeGUI initialization started")
        
        self.root = root
        self.root.title("Voice Converter")
        
        # デザイントークンの設定
        self.design_tokens = DESIGN_TOKENS
        self.colors = self.design_tokens['colors']
        self.fonts = FONTS
        
        # 変数の初期化
        self._initialize_variables()
        
        # アプリケーション設定
        self._setup_application()
        
        # UI構築
        self.create_ui()
        
        # モデル読み込み
        self.load_models()
        
        logging.info("DarkModeGUI initialization completed")
    
    def _initialize_variables(self):
        """変数の初期化"""
        # モデル関連
        self.model_info = {}
        self.selected_model = tk.StringVar()
        self.model_dir_var = tk.StringVar()
        
        # ファイル関連
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.output_filename_var = tk.StringVar()
        self.is_manual_filename = False
        
        # 音声処理パラメータ
        self.pitch_var = tk.IntVar(value=DEFAULT_SETTINGS['pitch'])
        self.f0_method_var = tk.StringVar(value=DEFAULT_SETTINGS['f0_method'])
        self.index_rate_var = tk.DoubleVar(value=DEFAULT_SETTINGS['index_rate'])
        self.filter_radius_var = tk.IntVar(value=DEFAULT_SETTINGS['filter_radius'])
        self.rms_mix_rate_var = tk.DoubleVar(value=DEFAULT_SETTINGS['rms_mix_rate'])
        self.protect_var = tk.DoubleVar(value=DEFAULT_SETTINGS['protect'])
        
        # UI要素の参照
        self.model_cards = []
        self.selected_card = None
        self.progress_stages = []
        self.is_converting = False
    
    def _setup_application(self):
        """アプリケーションの初期設定"""
        self.setup_app_directories()
        self.setup_styles()
        self.setup_window()
        self._setup_logging()
    
    def _setup_logging(self):
        """ロギングシステムの設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
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
            
        # 必要なディレクトリを作成
        os.makedirs(default_model_dir, exist_ok=True)
    
    def load_settings(self):
        """設定ファイルの読み込み"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'model_directory' in settings:
                        self.model_dir_var.set(settings['model_directory'])
            except Exception as e:
                logging.error(f"Failed to load settings: {e}")
    
    def save_settings(self):
        """設定ファイルの保存"""
        settings = {
            'model_directory': self.model_dir_var.get(),
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
    
    def setup_styles(self):
        """TTKスタイルの設定"""
        self.style = ttk.Style()
        
        # ダークテーマの設定
        self.root.configure(bg=self.colors['background_primary'])
        
        # ボタンスタイル
        self.style.configure(
            'Primary.TButton',
            font=(self.fonts['family'], self.design_tokens['typography']['body']['size'], 'bold'),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map('Primary.TButton',
            background=[('active', self.colors['accent_primary']),
                       ('!active', self.colors['accent_primary'])],
            foreground=[('active', 'white'),
                       ('!active', 'white')]
        )
        
        # セカンダリボタン
        self.style.configure(
            'Secondary.TButton',
            font=(self.fonts['family'], self.design_tokens['typography']['body']['size']),
            relief='flat',
            borderwidth=1
        )
        
        # ラベルスタイル
        self.style.configure(
            'Heading.TLabel',
            font=(self.fonts['family'], self.design_tokens['typography']['headline']['size'], 'bold'),
            background=self.colors['background_primary'],
            foreground=self.colors['text_primary']
        )
        
        # Comboboxスタイル
        self.style.configure(
            'Dark.TCombobox',
            fieldbackground=self.colors['background_tertiary'],
            background=self.colors['background_tertiary'],
            foreground=self.colors['text_primary'],
            selectbackground=self.colors['accent_primary'],
            selectforeground='white',
            borderwidth=0,
            relief='flat'
        )
        
        # Scrollbarスタイル
        self.style.configure(
            'Dark.Vertical.TScrollbar',
            background=self.colors['background_secondary'],
            troughcolor=self.colors['background_secondary'],
            bordercolor=self.colors['background_secondary'],
            darkcolor=self.colors['background_tertiary'],
            lightcolor=self.colors['background_tertiary'],
            arrowcolor=self.colors['text_tertiary']
        )
    
    def setup_window(self):
        """ウィンドウの設定"""
        # ウィンドウサイズ
        window_width = self.design_tokens['layout']['min_window_width']
        window_height = self.design_tokens['layout']['min_window_height']
        self.root.minsize(window_width, window_height)
        
        # 画面中央に配置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # macOS用の設定
        if sys.platform == 'darwin':
            try:
                self.root.tk.call('tk', 'windowingsystem', 'aqua')
                # ダークモードを明示的に設定
                self.root.tk.call('::tk::unsupported::MacWindowStyle', 'style', 
                                self.root._w, 'dark', 'true')
            except:
                pass
    
    # =========================================================================
    # UI構築セクション
    # =========================================================================
    
    def create_ui(self):
        """メインUIの構築"""
        # ルートフレーム
        main_frame = tk.Frame(self.root, bg=self.colors['background_primary'])
        main_frame.pack(fill='both', expand=True)
        
        # ナビゲーションバー
        self.create_navigation_bar(main_frame)
        
        # コンテンツエリア
        content_frame = tk.Frame(main_frame, bg=self.colors['background_primary'])
        content_frame.pack(fill='both', expand=True)
        
        # 2カラムレイアウト
        self.create_two_column_layout(content_frame)
    
    def create_navigation_bar(self, parent):
        """ナビゲーションバーの作成"""
        nav_frame = tk.Frame(
            parent,
            bg=self.colors['background_secondary'],
            height=self.design_tokens['layout']['toolbar_height']
        )
        nav_frame.pack(fill='x', pady=(0, 1))
        nav_frame.pack_propagate(False)
        
        # ロゴエリア
        logo_frame = tk.Frame(nav_frame, bg=self.colors['background_secondary'])
        logo_frame.pack(side='left', padx=self.design_tokens['spacing']['lg'])
        
        # グラデーションアイコン
        icon_size = 24
        icon_canvas = tk.Canvas(
            logo_frame,
            width=icon_size,
            height=icon_size,
            bg=self.colors['background_secondary'],
            highlightthickness=0
        )
        icon_canvas.pack(side='left', pady=5)
        
        create_gradient_icon(
            icon_canvas,
            [self.colors['accent_primary'], self.colors['accent_secondary']],
            icon_size
        )
        
        # アプリ名
        app_name = tk.Label(
            logo_frame,
            text="Voice Converter",
            font=(self.fonts['family'], self.design_tokens['typography']['headline']['size'], 'bold'),
            bg=self.colors['background_secondary'],
            fg=self.colors['text_primary']
        )
        app_name.pack(side='left', padx=(self.design_tokens['spacing']['sm'], 0))
    
    def create_two_column_layout(self, parent):
        """2カラムレイアウトの作成"""
        # レイアウトコンテナ
        layout_container = tk.Frame(parent, bg=self.colors['background_primary'])
        layout_container.pack(fill='both', expand=True, padx=1)
        
        # サイドバー（モデル選択）
        self.create_model_sidebar(layout_container)
        
        # メインコンテンツ
        self.create_main_content(layout_container)
    
    def create_model_sidebar(self, parent):
        """モデル選択サイドバーの作成"""
        sidebar_frame = tk.Frame(
            parent,
            bg=self.colors['surface_sidebar'],
            width=self.design_tokens['layout']['sidebar_width']
        )
        sidebar_frame.pack(side='left', fill='y')
        sidebar_frame.pack_propagate(False)
        
        # サイドバーヘッダー
        header_frame = tk.Frame(sidebar_frame, bg=self.colors['surface_sidebar'])
        header_frame.pack(fill='x', padx=self.design_tokens['spacing']['md'], 
                         pady=self.design_tokens['spacing']['md'])
        
        models_label = tk.Label(
            header_frame,
            text="音声モデル",
            font=(self.fonts['family'], self.design_tokens['typography']['title3']['size'], 'bold'),
            bg=self.colors['surface_sidebar'],
            fg=self.colors['text_primary']
        )
        models_label.pack(side='left')
        
        # 設定ボタン
        settings_btn = self.create_button(
            header_frame,
            text="⚙",
            command=self.open_model_settings,
            style='icon',
            width=30,
            height=30
        )
        settings_btn.pack(side='right')
        
        # スクロール可能なモデルリスト
        self.create_scrollable_model_list(sidebar_frame)
    
    def create_scrollable_model_list(self, parent):
        """スクロール可能なモデルリストの作成"""
        # スクロールフレーム
        scroll_frame = tk.Frame(parent, bg=self.colors['surface_sidebar'])
        scroll_frame.pack(fill='both', expand=True, padx=self.design_tokens['spacing']['sm'])
        
        # Canvasとスクロールバー
        canvas = tk.Canvas(scroll_frame, bg=self.colors['surface_sidebar'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview, 
                                 style='Dark.Vertical.TScrollbar')
        
        self.model_list_frame = tk.Frame(canvas, bg=self.colors['surface_sidebar'])
        
        # Canvasウィンドウ
        canvas_window = canvas.create_window((0, 0), window=self.model_list_frame, anchor="nw")
        
        # スクロール設定
        def configure_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = event.width if event else canvas.winfo_width()
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        self.model_list_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # マウスホイール対応
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 配置
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_main_content(self, parent):
        """メインコンテンツエリアの作成"""
        # メインコンテンツコンテナ
        main_container = tk.Frame(parent, bg=self.colors['background_primary'])
        main_container.pack(side='left', fill='both', expand=True)
        
        # コンテンツをセンタリング
        content_frame = tk.Frame(main_container, bg=self.colors['background_primary'])
        content_frame.pack(expand=True, fill='both', padx=self.design_tokens['spacing']['xl'], 
                          pady=self.design_tokens['spacing']['xl'])
        
        # 最大幅の制限
        content_frame.configure(width=self.design_tokens['layout']['max_content_width'])
        content_frame.pack_propagate(False)
        
        # スクロール可能なコンテンツ
        self.create_scrollable_content(content_frame)
    
    def create_scrollable_content(self, parent):
        """スクロール可能なコンテンツエリアの作成"""
        # スクロールフレーム
        scroll_frame = tk.Frame(parent, bg=self.colors['background_primary'])
        scroll_frame.pack(fill='both', expand=True)
        
        # Canvasとスクロールバー
        canvas = tk.Canvas(scroll_frame, bg=self.colors['background_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview,
                                 style='Dark.Vertical.TScrollbar')
        
        content_inner = tk.Frame(canvas, bg=self.colors['background_primary'])
        
        # Canvasウィンドウ
        canvas_window = canvas.create_window((0, 0), window=content_inner, anchor="nw")
        
        # スクロール設定
        def configure_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = event.width if event else canvas.winfo_width()
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        content_inner.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 配置
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # コンテンツセクション
        self.create_title_section(content_inner)
        self.create_input_section(content_inner)
        self.create_settings_section(content_inner)
        self.create_conversion_button(content_inner)
        self.create_status_section(content_inner)
        self.create_log_section(content_inner)
    
    # =========================================================================
    # UIコンポーネント作成セクション
    # =========================================================================
    
    def create_title_section(self, parent):
        """タイトルセクションの作成"""
        title_frame = tk.Frame(parent, bg=self.colors['background_primary'])
        title_frame.pack(fill='x', pady=(0, self.design_tokens['spacing']['xl']))
        
        title_label = tk.Label(
            title_frame,
            text="AI音声変換を開始",
            font=(self.fonts['family'], self.design_tokens['typography']['title1']['size'], 'bold'),
            bg=self.colors['background_primary'],
            fg=self.colors['text_primary']
        )
        title_label.pack()
    
    def create_input_section(self, parent):
        """入力セクションの作成"""
        input_card = self.create_card(parent, "入力ファイル")
        
        # ファイル選択エリア
        file_frame = tk.Frame(input_card, bg=self.colors['surface_card'])
        file_frame.pack(fill='x', pady=(self.design_tokens['spacing']['sm'], 0))
        
        # 入力フィールド
        self.input_entry = tk.Entry(
            file_frame,
            textvariable=self.input_var,
            font=(self.fonts['family'], self.design_tokens['typography']['body']['size']),
            bg=self.colors['background_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=8
        )
        self.input_entry.pack(side='left', fill='x', expand=True)
        
        # ブラウズボタン
        browse_btn = self.create_button(
            file_frame,
            text="選択",
            command=self.browse_input,
            style='secondary',
            width=60
        )
        browse_btn.pack(side='left', padx=(self.design_tokens['spacing']['sm'], 0))
        
        # ファイル情報表示
        self.file_info_frame = tk.Frame(input_card, bg=self.colors['surface_card'])
        self.file_info_frame.pack(fill='x', pady=(self.design_tokens['spacing']['sm'], 0))
    
    def create_settings_section(self, parent):
        """設定セクションの作成"""
        settings_card = self.create_card(parent, "変換設定")
        
        # 設定グリッド
        settings_grid = tk.Frame(settings_card, bg=self.colors['surface_card'])
        settings_grid.pack(fill='x', pady=(self.design_tokens['spacing']['sm'], 0))
        
        # 2列レイアウト
        left_column = tk.Frame(settings_grid, bg=self.colors['surface_card'])
        left_column.pack(side='left', fill='both', expand=True, padx=(0, self.design_tokens['spacing']['md']))
        
        right_column = tk.Frame(settings_grid, bg=self.colors['surface_card'])
        right_column.pack(side='left', fill='both', expand=True)
        
        # 左列の設定
        self.create_compact_setting_control(
            left_column, "ピッチ", self.pitch_var, -12, 12, 
            "音程の調整 (半音単位)"
        )
        
        self.create_compact_setting_control(
            left_column, "特徴比率", self.index_rate_var, 0, 1, 
            "音声特徴の使用率", is_float=True
        )
        
        self.create_compact_setting_control(
            left_column, "呼吸保護", self.protect_var, 0, 0.5,
            "呼吸音の保護レベル", is_float=True
        )
        
        # 右列の設定
        # F0メソッド選択
        f0_frame = tk.Frame(right_column, bg=self.colors['surface_card'])
        f0_frame.pack(fill='x', pady=(0, self.design_tokens['spacing']['md']))
        
        f0_label = tk.Label(
            f0_frame,
            text="ピッチ抽出",
            font=(self.fonts['family'], self.design_tokens['typography']['subheadline']['size']),
            bg=self.colors['surface_card'],
            fg=self.colors['text_secondary']
        )
        f0_label.pack(anchor='w')
        
        f0_combo = ttk.Combobox(
            f0_frame,
            textvariable=self.f0_method_var,
            values=['rmvpe', 'mangio-crepe', 'crepe', 'harvest', 'dio'],
            state='readonly',
            style='Dark.TCombobox',
            font=(self.fonts['family'], self.design_tokens['typography']['body']['size'])
        )
        f0_combo.pack(fill='x', pady=(self.design_tokens['spacing']['xs'], 0))
        
        self.create_compact_setting_control(
            right_column, "メディアンフィルタ", self.filter_radius_var, 0, 7,
            "ノイズ除去の強度"
        )
        
        self.create_compact_setting_control(
            right_column, "ミックス率", self.rms_mix_rate_var, 0, 1,
            "入力音声の混合比率", is_float=True
        )
        
        # 高度な設定の折りたたみ（オプション）
        self.create_advanced_settings(settings_card)
    
    def create_advanced_settings(self, parent):
        """高度な設定の作成（折りたたみ可能）"""
        # 高度な設定トグル
        toggle_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        toggle_frame.pack(fill='x', pady=(self.design_tokens['spacing']['lg'], 0))
        
        self.advanced_expanded = tk.BooleanVar(value=False)
        toggle_btn = tk.Label(
            toggle_frame,
            text="▶ 高度な設定",
            font=(self.fonts['family'], self.design_tokens['typography']['callout']['size']),
            bg=self.colors['surface_card'],
            fg=self.colors['text_secondary'],
            cursor="hand2"
        )
        toggle_btn.pack(anchor='w')
        
        # 高度な設定フレーム（初期状態では非表示）
        self.advanced_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        
        def toggle_advanced():
            if self.advanced_expanded.get():
                self.advanced_expanded.set(False)
                toggle_btn.config(text="▶ 高度な設定")
                self.advanced_frame.pack_forget()
            else:
                self.advanced_expanded.set(True)
                toggle_btn.config(text="▼ 高度な設定")
                self.advanced_frame.pack(fill='x', pady=(self.design_tokens['spacing']['sm'], 0))
        
        toggle_btn.bind("<Button-1>", lambda e: toggle_advanced())
        
        # 高度な設定の内容
        # 出力ディレクトリ
        output_frame = tk.Frame(self.advanced_frame, bg=self.colors['surface_card'])
        output_frame.pack(fill='x', pady=(0, self.design_tokens['spacing']['sm']))
        
        output_label = tk.Label(
            output_frame,
            text="出力先",
            font=(self.fonts['family'], self.design_tokens['typography']['subheadline']['size']),
            bg=self.colors['surface_card'],
            fg=self.colors['text_secondary']
        )
        output_label.pack(anchor='w')
        
        output_entry_frame = tk.Frame(output_frame, bg=self.colors['surface_card'])
        output_entry_frame.pack(fill='x', pady=(self.design_tokens['spacing']['xs'], 0))
        
        self.output_entry = tk.Entry(
            output_entry_frame,
            textvariable=self.output_var,
            font=(self.fonts['family'], self.design_tokens['typography']['body']['size']),
            bg=self.colors['background_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=8
        )
        self.output_entry.pack(side='left', fill='x', expand=True)
        
        output_browse_btn = self.create_button(
            output_entry_frame,
            text="選択",
            command=self.browse_output,
            style='secondary',
            width=60
        )
        output_browse_btn.pack(side='left', padx=(self.design_tokens['spacing']['sm'], 0))
        
        # カスタムファイル名
        filename_frame = tk.Frame(self.advanced_frame, bg=self.colors['surface_card'])
        filename_frame.pack(fill='x')
        
        filename_label = tk.Label(
            filename_frame,
            text="出力ファイル名",
            font=(self.fonts['family'], self.design_tokens['typography']['subheadline']['size']),
            bg=self.colors['surface_card'],
            fg=self.colors['text_secondary']
        )
        filename_label.pack(anchor='w')
        
        self.filename_entry = tk.Entry(
            filename_frame,
            textvariable=self.output_filename_var,
            font=(self.fonts['family'], self.design_tokens['typography']['body']['size']),
            bg=self.colors['background_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=8
        )
        self.filename_entry.pack(fill='x', pady=(self.design_tokens['spacing']['xs'], 0))
        self.filename_entry.bind("<KeyRelease>", self.on_filename_manual_input)
        self.filename_entry.bind("<FocusIn>", self.on_filename_focus)
        
        # 出力プレビュー
        self.output_preview_label = tk.Label(
            filename_frame,
            text="",
            font=(self.fonts['family'], self.design_tokens['typography']['caption1']['size']),
            bg=self.colors['surface_card'],
            fg=self.colors['text_tertiary']
        )
        self.output_preview_label.pack(anchor='w', pady=(self.design_tokens['spacing']['xs'], 0))
    
    def create_compact_setting_control(self, parent, label_text, variable, min_val, max_val, 
                                     tooltip_text="", is_float=False):
        """コンパクトな設定コントロールの作成"""
        control_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        control_frame.pack(fill='x', pady=(0, self.design_tokens['spacing']['md']))
        
        # ラベルと値表示
        header_frame = tk.Frame(control_frame, bg=self.colors['surface_card'])
        header_frame.pack(fill='x')
        
        label = tk.Label(
            header_frame,
            text=label_text,
            font=(self.fonts['family'], self.design_tokens['typography']['subheadline']['size']),
            bg=self.colors['surface_card'],
            fg=self.colors['text_secondary']
        )
        label.pack(side='left')
        
        # 現在値表示
        value_label = tk.Label(
            header_frame,
            text=f"{variable.get():.2f}" if is_float else str(variable.get()),
            font=(self.fonts['family'], self.design_tokens['typography']['body_bold']['size'], 'bold'),
            bg=self.colors['surface_card'],
            fg=self.colors['accent_primary']
        )
        value_label.pack(side='right')
        
        # スライダー
        slider_frame = tk.Frame(control_frame, bg=self.colors['surface_card'])
        slider_frame.pack(fill='x', pady=(self.design_tokens['spacing']['xs'], 0))
        
        # カスタムスライダー
        slider_canvas = tk.Canvas(
            slider_frame,
            height=6,
            bg=self.colors['surface_card'],
            highlightthickness=0
        )
        slider_canvas.pack(fill='x', padx=self.design_tokens['spacing']['xs'])
        
        # スライダートラック
        def draw_slider():
            slider_canvas.delete("all")
            width = slider_canvas.winfo_width()
            if width <= 1:
                return
                
            # トラック描画
            track_y = 3
            slider_canvas.create_rectangle(
                0, track_y-2, width, track_y+2,
                fill=self.colors['background_tertiary'],
                outline=""
            )
            
            # 進捗描画
            progress = (variable.get() - min_val) / (max_val - min_val)
            progress_width = int(width * progress)
            if progress_width > 0:
                slider_canvas.create_rectangle(
                    0, track_y-2, progress_width, track_y+2,
                    fill=self.colors['accent_primary'],
                    outline=""
                )
            
            # ハンドル描画
            handle_x = progress_width
            handle_radius = 8
            slider_canvas.create_oval(
                handle_x-handle_radius, track_y-handle_radius,
                handle_x+handle_radius, track_y+handle_radius,
                fill=self.colors['accent_primary'],
                outline=""
            )
        
        # マウスイベント処理
        def on_slider_click(event):
            width = slider_canvas.winfo_width()
            if width <= 1:
                return
            progress = event.x / width
            progress = max(0, min(1, progress))
            
            if is_float:
                new_value = min_val + (max_val - min_val) * progress
                variable.set(round(new_value, 2))
                value_label.config(text=f"{new_value:.2f}")
            else:
                new_value = int(min_val + (max_val - min_val) * progress)
                variable.set(new_value)
                value_label.config(text=str(new_value))
            
            draw_slider()
        
        slider_canvas.bind("<Button-1>", on_slider_click)
        slider_canvas.bind("<B1-Motion>", on_slider_click)
        slider_canvas.bind("<Configure>", lambda e: draw_slider())
        
        # 初期描画
        self.root.after(100, draw_slider)
        
        # ツールチップ
        if tooltip_text:
            tooltip_label = tk.Label(
                control_frame,
                text=tooltip_text,
                font=(self.fonts['family'], self.design_tokens['typography']['caption2']['size']),
                bg=self.colors['surface_card'],
                fg=self.colors['text_tertiary']
            )
            tooltip_label.pack(anchor='w', pady=(self.design_tokens['spacing']['xs'], 0))
    
    def create_conversion_button(self, parent):
        """変換ボタンの作成"""
        button_frame = tk.Frame(parent, bg=self.colors['background_primary'])
        button_frame.pack(fill='x', pady=self.design_tokens['spacing']['xl'])
        
        self.convert_button = self.create_button(
            button_frame,
            text="音声変換を開始",
            command=self.start_conversion,
            style='primary',
            width=200,
            height=44
        )
        self.convert_button.pack()
    
    def create_status_section(self, parent):
        """ステータスセクションの作成"""
        self.status_card = self.create_card(parent, "変換状況", visible=False)
        
        # プログレス情報
        self.progress_frame = tk.Frame(self.status_card, bg=self.colors['surface_card'])
        self.progress_frame.pack(fill='x', pady=(self.design_tokens['spacing']['sm'], 0))
        
        # ステージインジケーター
        self.stage_frame = tk.Frame(self.progress_frame, bg=self.colors['surface_card'])
        self.stage_frame.pack(fill='x')
        
        # ステージの定義
        stages = [
            {"name": "準備中", "icon": "⚙️"},
            {"name": "モデル読込", "icon": "📂"},
            {"name": "音声処理", "icon": "🎵"},
            {"name": "変換中", "icon": "🔄"},
            {"name": "保存中", "icon": "💾"},
            {"name": "完了", "icon": "✅"}
        ]
        
        self._create_stage_indicators(stages)
        
        # 詳細メッセージ
        self.status_message = tk.Label(
            self.progress_frame,
            text="",
            font=(self.fonts['family'], self.design_tokens['typography']['callout']['size']),
            bg=self.colors['surface_card'],
            fg=self.colors['text_secondary']
        )
        self.status_message.pack(fill='x', pady=(self.design_tokens['spacing']['md'], 0))
        
        # プログレスバー
        self.progress_canvas = tk.Canvas(
            self.progress_frame,
            height=4,
            bg=self.colors['surface_card'],
            highlightthickness=0
        )
        self.progress_canvas.pack(fill='x', pady=(self.design_tokens['spacing']['sm'], 0))
    
    def _create_stage_indicators(self, stages):
        """ステージインジケーターの作成"""
        self.progress_stages = []
        
        for i, stage in enumerate(stages):
            stage_frame = tk.Frame(self.stage_frame, bg=self.colors['surface_card'])
            stage_frame.pack(side='left', expand=True, fill='x')
            
            # アイコンと名前
            icon_label = tk.Label(
                stage_frame,
                text=stage['icon'],
                font=(self.fonts['family'], 16),
                bg=self.colors['surface_card']
            )
            icon_label.pack()
            
            name_label = tk.Label(
                stage_frame,
                text=stage['name'],
                font=(self.fonts['family'], self.design_tokens['typography']['caption2']['size']),
                bg=self.colors['surface_card']
            )
            name_label.pack()
            
            # 接続線（最後のステージ以外）
            if i < len(stages) - 1:
                line_frame = tk.Frame(self.stage_frame, bg=self.colors['divider'], height=2)
                line_frame.pack(side='left', fill='x', expand=True, pady=(0, 20))
            
            self.progress_stages.append({
                'icon': icon_label,
                'name': name_label,
                'active': False
            })
    
    def create_log_section(self, parent):
        """ログセクションの作成"""
        self.log_card = self.create_card(parent, "処理ログ", visible=False)
        
        # ログテキストエリア
        log_frame = tk.Frame(self.log_card, bg=self.colors['surface_card'])
        log_frame.pack(fill='both', expand=True, pady=(self.design_tokens['spacing']['sm'], 0))
        
        # スクロール可能なテキストウィジェット
        self.log_text = tk.Text(
            log_frame,
            height=8,
            font=(self.fonts['mono'], self.design_tokens['typography']['footnote']['size']),
            bg=self.colors['background_tertiary'],
            fg=self.colors['text_secondary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            wrap='word',
            padx=self.design_tokens['spacing']['md'],
            pady=self.design_tokens['spacing']['sm']
        )
        self.log_text.pack(side='left', fill='both', expand=True)
        
        # スクロールバー
        log_scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview,
                                     style='Dark.Vertical.TScrollbar')
        log_scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # ログレベル用のタグ設定
        for level, config in LOG_LEVELS.items():
            self.log_text.tag_config(level, foreground=config['color'])
    
    # =========================================================================
    # ユーティリティメソッドセクション
    # =========================================================================
    
    def create_card(self, parent, title, visible=True):
        """再利用可能なカードコンポーネントの作成"""
        card_frame = tk.Frame(
            parent,
            bg=self.colors['surface_card'],
            relief='flat',
            bd=0
        )
        if visible:
            card_frame.pack(fill='x', pady=(0, self.design_tokens['spacing']['lg']))
        
        # カードタイトル
        if title:
            title_label = tk.Label(
                card_frame,
                text=title,
                font=(self.fonts['family'], self.design_tokens['typography']['headline']['size'], 'bold'),
                bg=self.colors['surface_card'],
                fg=self.colors['text_primary']
            )
            title_label.pack(anchor='w', padx=self.design_tokens['spacing']['lg'], 
                            pady=(self.design_tokens['spacing']['md'], self.design_tokens['spacing']['sm']))
        
        # カードコンテンツエリア
        content_frame = tk.Frame(
            card_frame,
            bg=self.colors['surface_card']
        )
        content_frame.pack(fill='both', expand=True, 
                          padx=self.design_tokens['spacing']['lg'],
                          pady=(0, self.design_tokens['spacing']['md']))
        
        return content_frame
    
    def create_button(self, parent, text, command, style='primary', width=None, height=None):
        """統一されたボタンの作成"""
        if style == 'primary':
            bg = self.colors['accent_primary']
            fg = 'white'
            active_bg = self.colors['accent_primary']
            font = (self.fonts['family'], self.design_tokens['typography']['body_bold']['size'], 'bold')
        elif style == 'secondary':
            bg = self.colors['background_tertiary']
            fg = self.colors['text_primary']
            active_bg = self.colors['background_elevated']
            font = (self.fonts['family'], self.design_tokens['typography']['body']['size'])
        elif style == 'icon':
            bg = self.colors['surface_card']
            fg = self.colors['text_secondary']
            active_bg = self.colors['hover']
            font = (self.fonts['family'], self.design_tokens['typography']['body']['size'])
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=font,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            relief='flat',
            bd=0,
            padx=self.design_tokens['spacing']['lg'],
            pady=self.design_tokens['spacing']['sm'],
            cursor='hand2'
        )
        
        if width:
            button.config(width=width)
        if height:
            button.config(height=height)
        
        # ホバーエフェクト
        def on_enter(e):
            if style == 'primary':
                button.config(bg=self.colors['accent_secondary'])
            else:
                button.config(bg=active_bg)
        
        def on_leave(e):
            button.config(bg=bg)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def log_message(self, message, level="INFO"):
        """ログメッセージの表示"""
        if hasattr(self, 'log_text'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_config = LOG_LEVELS.get(level, LOG_LEVELS['INFO'])
            
            log_entry = f"{timestamp} {log_config['prefix']} {message}\n"
            
            self.log_text.insert('end', log_entry, level)
            self.log_text.see('end')
            
        # ログカードを表示
        if hasattr(self, 'log_card') and not self.log_card.winfo_viewable():
            self.log_card.pack(fill='x', pady=(0, self.design_tokens['spacing']['lg']))
    
    def update_progress(self, stage_index, progress, message=""):
        """プログレスの更新"""
        if not hasattr(self, 'progress_stages'):
            return
        
        # UIスレッドで実行
        self.root.after(0, self._update_progress_ui, stage_index, progress, message)
    
    def _update_progress_ui(self, stage_index, progress, message):
        """プログレスUIの更新（UIスレッド）"""
        # ステータスカードを表示
        if not self.status_card.winfo_viewable():
            self.status_card.pack(fill='x', pady=(0, self.design_tokens['spacing']['lg']))
        
        # ステージインジケーターの更新
        for i, stage in enumerate(self.progress_stages):
            if i < stage_index:
                # 完了したステージ
                stage['icon'].config(fg=self.colors['success'])
                stage['name'].config(fg=self.colors['success'])
            elif i == stage_index:
                # 現在のステージ
                stage['icon'].config(fg=self.colors['accent_primary'])
                stage['name'].config(fg=self.colors['accent_primary'])
            else:
                # 未完了のステージ
                stage['icon'].config(fg=self.colors['text_disabled'])
                stage['name'].config(fg=self.colors['text_disabled'])
        
        # メッセージの更新
        if message:
            self.status_message.config(text=message)
        
        # プログレスバーの更新
        self._draw_progress_bar(progress)
    
    def _draw_progress_bar(self, progress):
        """プログレスバーの描画"""
        if not hasattr(self, 'progress_canvas'):
            return
        
        self.progress_canvas.delete("all")
        width = self.progress_canvas.winfo_width()
        height = 4
        
        if width <= 1:
            return
        
        # 背景
        self.progress_canvas.create_rectangle(
            0, 0, width, height,
            fill=self.colors['background_tertiary'],
            outline=""
        )
        
        # プログレス
        if progress > 0:
            progress_width = int(width * progress)
            self.progress_canvas.create_rectangle(
                0, 0, progress_width, height,
                fill=self.colors['accent_primary'],
                outline=""
            )
    
    # =========================================================================
    # イベントハンドラーセクション
    # =========================================================================
    
    def browse_input(self):
        """入力ファイルの選択"""
        filename = filedialog.askopenfilename(
            title="音声ファイルを選択",
            filetypes=AUDIO_FILE_TYPES,
            parent=self.root
        )
        
        if filename:
            self.input_var.set(filename)
            self.on_input_file_changed()
            self.display_file_info(filename)
            self.log_message(f"入力ファイルを選択: {os.path.basename(filename)}", "INFO")
    
    def browse_output(self):
        """出力ディレクトリの選択"""
        directory = filedialog.askdirectory(
            title="出力先フォルダを選択",
            parent=self.root
        )
        
        if directory:
            self.output_var.set(directory)
            self.update_output_preview()
            self.log_message(f"出力先を設定: {directory}", "INFO")
    
    def clear_input(self):
        """入力のクリア"""
        self.input_var.set("")
        self.output_filename_var.set("")
        self.is_manual_filename = False
        
        if hasattr(self, 'file_info_frame'):
            for widget in self.file_info_frame.winfo_children():
                widget.destroy()
        
        if hasattr(self, 'output_preview_label'):
            self.output_preview_label.config(text="")
    
    def on_input_file_changed(self):
        """入力ファイル変更時の処理"""
        if not self.is_manual_filename and self.input_var.get():
            input_path = Path(self.input_var.get())
            base_name = input_path.stem
            extension = input_path.suffix
            
            if self.selected_model.get():
                model_name = Path(self.selected_model.get()).stem
                suggested_name = f"{base_name}_{model_name}_converted{extension}"
            else:
                suggested_name = f"{base_name}_converted{extension}"
            
            self.output_filename_var.set(suggested_name)
            self.update_output_preview()
    
    def on_filename_manual_input(self, event):
        """ファイル名手動入力時の処理"""
        if event.keysym not in ['Up', 'Down', 'Left', 'Right', 'Tab']:
            self.is_manual_filename = True
        self.validate_filename()
    
    def on_filename_focus(self, event):
        """ファイル名入力フィールドフォーカス時の処理"""
        self.filename_entry.selection_range(0, 'end')
    
    def validate_filename(self, *args):
        """ファイル名の検証"""
        filename = self.output_filename_var.get()
        
        # 無効な文字のチェック
        invalid_chars = '<>:"|?*'
        if any(char in filename for char in invalid_chars):
            self.filename_entry.config(fg=self.colors['error'])
            self.output_preview_label.config(
                text="⚠️ ファイル名に使用できない文字が含まれています",
                fg=self.colors['error']
            )
            return False
        
        # 拡張子のチェック
        if filename and not os.path.splitext(filename)[1]:
            self.filename_entry.config(fg=self.colors['warning'])
            self.output_preview_label.config(
                text="⚠️ 拡張子を指定してください (例: .wav, .mp3)",
                fg=self.colors['warning']
            )
            return False
        
        self.filename_entry.config(fg=self.colors['text_primary'])
        self.update_output_preview()
        return True
    
    def update_output_preview(self):
        """出力ファイルパスのプレビュー更新"""
        if not hasattr(self, 'output_preview_label'):
            return
        
        output_dir = self.output_var.get() or os.path.dirname(self.input_var.get())
        filename = self.output_filename_var.get()
        
        if output_dir and filename:
            full_path = os.path.join(output_dir, filename)
            preview_text = f"出力: {truncate_path(full_path, 60)}"
            self.output_preview_label.config(text=preview_text, fg=self.colors['text_tertiary'])
    
    def display_file_info(self, filepath):
        """ファイル情報の表示"""
        # 既存の情報をクリア
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
        
        file_info = get_file_info(filepath)
        if file_info:
            info_text = f"📄 {file_info['name']} • {file_info['extension']} • {file_info['size']}"
            info_label = tk.Label(
                self.file_info_frame,
                text=info_text,
                font=(self.fonts['family'], self.design_tokens['typography']['callout']['size']),
                bg=self.colors['surface_card'],
                fg=self.colors['text_secondary']
            )
            info_label.pack(anchor='w')
    
    def on_model_selected(self, model):
        """モデル選択時の処理"""
        self.selected_model.set(model)
        self.on_input_file_changed()
        self.log_message(f"モデルを選択: {os.path.basename(model)}", "INFO")
    
    def open_model_settings(self):
        """モデル設定ダイアログの表示"""
        dialog = tk.Toplevel(self.root)
        dialog.title("モデル設定")
        dialog.configure(bg=self.colors['background_primary'])
        
        # ダイアログサイズと位置
        dialog_width = 500
        dialog_height = 300
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog_width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # macOS用の設定
        if sys.platform == 'darwin':
            try:
                dialog.tk.call('::tk::unsupported::MacWindowStyle', 'style', 
                             dialog._w, 'dark', 'true')
            except:
                pass
        
        # コンテンツ
        content_frame = tk.Frame(dialog, bg=self.colors['background_primary'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(
            content_frame,
            text="モデルディレクトリ設定",
            font=(self.fonts['family'], self.design_tokens['typography']['title3']['size'], 'bold'),
            bg=self.colors['background_primary'],
            fg=self.colors['text_primary']
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # 説明
        desc_label = tk.Label(
            content_frame,
            text="音声モデルが保存されているディレクトリを指定してください。",
            font=(self.fonts['family'], self.design_tokens['typography']['body']['size']),
            bg=self.colors['background_primary'],
            fg=self.colors['text_secondary']
        )
        desc_label.pack(anchor='w', pady=(0, 20))
        
        # 現在のパス表示
        current_frame = tk.Frame(content_frame, bg=self.colors['background_primary'])
        current_frame.pack(fill='x', pady=(0, 10))
        
        current_label = tk.Label(
            current_frame,
            text="現在のパス:",
            font=(self.fonts['family'], self.design_tokens['typography']['callout']['size']),
            bg=self.colors['background_primary'],
            fg=self.colors['text_secondary']
        )
        current_label.pack(side='left')
        
        path_label = tk.Label(
            current_frame,
            text=truncate_path(self.model_dir_var.get(), 40),
            font=(self.fonts['family'], self.design_tokens['typography']['callout']['size']),
            bg=self.colors['background_primary'],
            fg=self.colors['text_primary']
        )
        path_label.pack(side='left', padx=(5, 0))
        
        # 入力フィールド
        input_frame = tk.Frame(content_frame, bg=self.colors['background_primary'])
        input_frame.pack(fill='x', pady=(0, 20))
        
        path_entry = tk.Entry(
            input_frame,
            textvariable=self.model_dir_var,
            font=(self.fonts['family'], self.design_tokens['typography']['body']['size']),
            bg=self.colors['background_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=8
        )
        path_entry.pack(side='left', fill='x', expand=True)
        
        browse_btn = self.create_button(
            input_frame,
            text="参照",
            command=lambda: self._browse_model_directory(path_label),
            style='secondary',
            width=60
        )
        browse_btn.pack(side='left', padx=(10, 0))
        
        # ボタン
        button_frame = tk.Frame(content_frame, bg=self.colors['background_primary'])
        button_frame.pack(fill='x', pady=(20, 0))
        
        save_btn = self.create_button(
            button_frame,
            text="保存して再読み込み",
            command=lambda: self._save_model_settings(dialog),
            style='primary'
        )
        save_btn.pack(side='right')
        
        cancel_btn = self.create_button(
            button_frame,
            text="キャンセル",
            command=dialog.destroy,
            style='secondary'
        )
        cancel_btn.pack(side='right', padx=(0, 10))
    
    def _browse_model_directory(self, path_label):
        """モデルディレクトリの参照"""
        directory = filedialog.askdirectory(
            title="モデルディレクトリを選択",
            initialdir=self.model_dir_var.get(),
            parent=self.root
        )
        
        if directory:
            self.model_dir_var.set(directory)
            path_label.config(text=truncate_path(directory, 40))
    
    def _save_model_settings(self, dialog):
        """モデル設定の保存"""
        self.save_settings()
        self.load_models()
        dialog.destroy()
        self.log_message("モデル設定を保存しました", "SUCCESS")
    
    # =========================================================================
    # モデル管理セクション
    # =========================================================================
    
    def search_models_recursive(self, directory):
        """再帰的にモデルを検索"""
        models = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # 隠しディレクトリをスキップ
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # .pthファイルを探す
                pth_files = [f for f in files if f.endswith('.pth') and not f.startswith('.')]
                
                for pth_file in pth_files:
                    pth_path = os.path.join(root, pth_file)
                    model_name = os.path.splitext(pth_file)[0]
                    
                    # 対応する.indexファイルを探す
                    index_file = None
                    possible_index = os.path.join(root, f"{model_name}.index")
                    if os.path.exists(possible_index):
                        index_file = possible_index
                    else:
                        # 同じディレクトリ内の.indexファイルを探す
                        index_files = [f for f in files if f.endswith('.index')]
                        if index_files:
                            index_file = os.path.join(root, index_files[0])
                    
                    # モデル情報を追加
                    models.append({
                        'name': model_name,
                        'path': pth_path,
                        'index': index_file,
                        'directory': os.path.basename(root),
                        'size': os.path.getsize(pth_path)
                    })
        
        except Exception as e:
            logging.error(f"Error searching models in {directory}: {e}")
        
        return models
    
    def load_models(self):
        """モデルの読み込み"""
        # 既存のモデルカードをクリア
        for card in self.model_cards:
            card.destroy()
        self.model_cards.clear()
        self.model_info.clear()
        
        model_dir = self.model_dir_var.get()
        if not os.path.exists(model_dir):
            self.log_message(f"モデルディレクトリが見つかりません: {model_dir}", "WARNING")
            return
        
        # モデルを検索
        models = self.search_models_recursive(model_dir)
        
        if not models:
            # モデルが見つからない場合のメッセージ
            empty_label = tk.Label(
                self.model_list_frame,
                text="モデルが見つかりません\n\n⚙️ 設定からモデルディレクトリを\n指定してください",
                font=(self.fonts['family'], self.design_tokens['typography']['callout']['size']),
                bg=self.colors['surface_sidebar'],
                fg=self.colors['text_tertiary'],
                justify='center'
            )
            empty_label.pack(pady=20)
            return
        
        # モデルをソート（名前順）
        models.sort(key=lambda x: x['name'].lower())
        
        # モデルカードを作成
        for i, model in enumerate(models):
            self.model_info[model['path']] = model
            card = self.create_model_card(model, i)
            self.model_cards.append(card)
        
        self.log_message(f"{len(models)}個のモデルを読み込みました", "SUCCESS")
    
    def create_model_card(self, model, index):
        """モデルカードの作成"""
        card = tk.Frame(
            self.model_list_frame,
            bg=self.colors['background_secondary'],
            relief='flat',
            bd=0,
            cursor='hand2'
        )
        card.pack(fill='x', pady=(0, self.design_tokens['spacing']['sm']))
        
        # カード内のパディング用フレーム
        inner_frame = tk.Frame(
            card,
            bg=self.colors['background_secondary']
        )
        inner_frame.pack(fill='x', padx=self.design_tokens['spacing']['sm'], 
                        pady=self.design_tokens['spacing']['sm'])
        
        # モデル名
        name_label = tk.Label(
            inner_frame,
            text=model['name'],
            font=(self.fonts['family'], self.design_tokens['typography']['body_bold']['size'], 'bold'),
            bg=self.colors['background_secondary'],
            fg=self.colors['text_primary'],
            anchor='w'
        )
        name_label.pack(fill='x')
        
        # モデル情報
        info_text = f"{model['directory']}"
        if model['index']:
            info_text += " • Index ✓"
        
        info_label = tk.Label(
            inner_frame,
            text=info_text,
            font=(self.fonts['family'], self.design_tokens['typography']['caption1']['size']),
            bg=self.colors['background_secondary'],
            fg=self.colors['text_tertiary'],
            anchor='w'
        )
        info_label.pack(fill='x')
        
        # サイズ表示
        size_mb = model['size'] / (1024 * 1024)
        size_label = tk.Label(
            inner_frame,
            text=f"{size_mb:.1f} MB",
            font=(self.fonts['family'], self.design_tokens['typography']['caption2']['size']),
            bg=self.colors['background_secondary'],
            fg=self.colors['text_disabled'],
            anchor='w'
        )
        size_label.pack(fill='x')
        
        # カードのデータを保存
        card.model_path = model['path']
        card.model_info = model
        
        # クリックイベント
        def on_click(event):
            self.update_model_selection(card)
            self.on_model_selected(model['path'])
        
        card.bind("<Button-1>", on_click)
        for child in inner_frame.winfo_children():
            child.bind("<Button-1>", on_click)
        
        # ホバーエフェクト
        def on_enter(e):
            if card != self.selected_card:
                card.config(bg=self.colors['hover'])
                inner_frame.config(bg=self.colors['hover'])
                for child in inner_frame.winfo_children():
                    child.config(bg=self.colors['hover'])
        
        def on_leave(e):
            if card != self.selected_card:
                card.config(bg=self.colors['background_secondary'])
                inner_frame.config(bg=self.colors['background_secondary'])
                for child in inner_frame.winfo_children():
                    child.config(bg=self.colors['background_secondary'])
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        return card
    
    def update_model_selection(self, selected_card):
        """モデル選択の更新"""
        # 前の選択を解除
        if self.selected_card:
            self.selected_card.config(bg=self.colors['background_secondary'])
            inner = self.selected_card.winfo_children()[0]
            inner.config(bg=self.colors['background_secondary'])
            for child in inner.winfo_children():
                child.config(bg=self.colors['background_secondary'])
        
        # 新しい選択
        self.selected_card = selected_card
        selected_card.config(bg=self.colors['accent_primary'])
        inner = selected_card.winfo_children()[0]
        inner.config(bg=self.colors['accent_primary'])
        for child in inner.winfo_children():
            child.config(bg=self.colors['accent_primary'])
            if isinstance(child, tk.Label):
                child.config(fg='white')
    
    # =========================================================================
    # 音声変換処理セクション
    # =========================================================================
    
    def start_conversion(self):
        """変換処理の開始（バリデーション）"""
        # 入力チェック
        if not self.input_var.get():
            messagebox.showwarning("入力エラー", "音声ファイルを選択してください")
            return
        
        if not os.path.exists(self.input_var.get()):
            messagebox.showerror("エラー", "選択されたファイルが見つかりません")
            return
        
        if not self.selected_model.get():
            messagebox.showwarning("入力エラー", "音声モデルを選択してください")
            return
        
        # ファイル名の検証
        if not self.validate_filename():
            messagebox.showwarning("入力エラー", "有効なファイル名を入力してください")
            return
        
        # 既に変換中の場合
        if self.is_converting:
            messagebox.showinfo("情報", "既に変換処理が実行中です")
            return
        
        # 変換開始
        self.is_converting = True
        self.convert_button.config(state='disabled', text="変換中...")
        
        # ログをクリア
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, 'end')
        
        # ステータスカードとログカードを表示
        if hasattr(self, 'status_card') and not self.status_card.winfo_viewable():
            self.status_card.pack(fill='x', pady=(0, self.design_tokens['spacing']['lg']))
        if hasattr(self, 'log_card') and not self.log_card.winfo_viewable():
            self.log_card.pack(fill='x', pady=(0, self.design_tokens['spacing']['lg']))
        
        # 変換処理を別スレッドで実行
        conversion_thread = threading.Thread(target=self.run_conversion)
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def run_conversion(self):
        """実際の変換処理"""
        try:
            # パスの準備
            input_path = self.input_var.get()
            output_dir = self.output_var.get() or os.path.dirname(input_path)
            output_filename = self.output_filename_var.get()
            output_path = os.path.join(output_dir, output_filename)
            
            # モデル情報
            model_path = self.selected_model.get()
            model_info = self.model_info.get(model_path, {})
            index_path = model_info.get('index', '')
            
            # Hubert モデルのパス（仮定）
            hubert_path = os.path.join(self.base_dir, "hubert_base.pt")
            if not os.path.exists(hubert_path):
                # 代替パスを試す
                possible_paths = [
                    os.path.join(self.base_dir, "models", "hubert_base.pt"),
                    os.path.join(self.base_dir, "rvc", "models", "hubert_base.pt"),
                    os.path.join(os.path.dirname(model_path), "hubert_base.pt")
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        hubert_path = path
                        break
                else:
                    # Hubertモデルが見つからない場合は空文字列
                    hubert_path = ""
            
            self.log_message("変換処理を開始します", "INFO")
            self.log_message(f"入力: {os.path.basename(input_path)}", "INFO")
            self.log_message(f"モデル: {os.path.basename(model_path)}", "INFO")
            self.log_message(f"出力: {os.path.basename(output_path)}", "INFO")
            
            # RVCパラメータ
            params = {
                'f0up_key': self.pitch_var.get(),
                'filter_radius': self.filter_radius_var.get(),
                'index_rate': self.index_rate_var.get(),
                'rms_mix_rate': self.rms_mix_rate_var.get(),
                'protect': self.protect_var.get(),
                'hop_length': 128,
                'f0method': self.f0_method_var.get(),
                'split_audio': False,
                'f0autotune': False,
                'embedder_model': 'hubert',
                'embedder_model_custom': None,
                'formant_shift': 0,
                'sid': 0,
                'input_path': input_path,
                'output_path': output_path,
                'pth_path': model_path,
                'index_path': index_path,
                'hubert_path': hubert_path
            }
            
            # 変換実行
            self._run_rvc_with_progress(params)
            
        except Exception as e:
            error_msg = f"変換エラー: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.root.after(0, self.conversion_error, error_msg)
    
    def _run_rvc_with_progress(self, params):
        """プログレス付きでRVCを実行"""
        try:
            # プログレス更新
            self.update_progress(0, 0.1, "変換環境を準備中...")
            
            # Poetry環境のPythonパスを構築
            if USE_HARDCODED_PATH:
                python_path = POETRY_PYTHON_PATH
                rvc_module = RVC_MODULE
            else:
                # 環境から推測
                if sys.platform == 'darwin':
                    poetry_path = os.path.expanduser("~/Library/Application Support/pypoetry/venv/bin/python")
                else:
                    poetry_path = "poetry"
                
                python_path = poetry_path
                rvc_module = "rvc.wrapper.cli.cli"
            
            # コマンドライン引数の構築
            cmd = [
                python_path,
                "-m", rvc_module,
                "infer",
                "--input", params['input_path'],
                "--output", params['output_path'],
                "--model", params['pth_path'],
                "--pitch", str(params['f0up_key']),
                "--filter_radius", str(params['filter_radius']),
                "--index_rate", str(params['index_rate']),
                "--volume_envelope", str(params['rms_mix_rate']),
                "--protect", str(params['protect']),
                "--hop_length", str(params['hop_length']),
                "--f0_method", params['f0method'],
                "--embedder_model", params['embedder_model']
            ]
            
            # オプションパラメータ
            if params.get('index_path'):
                cmd.extend(["--index", params['index_path']])
            
            if params.get('hubert_path'):
                cmd.extend(["--embedder_model_custom", params['hubert_path']])
            
            if params.get('split_audio'):
                cmd.append("--split_audio")
            
            if params.get('f0autotune'):
                cmd.append("--autotune")
            
            if params.get('formant_shift'):
                cmd.extend(["--formant_shift", str(params['formant_shift'])])
            
            self.update_progress(1, 0.2, "モデルを読み込んでいます...")
            self.log_message(f"コマンド: {' '.join(cmd)}", "DEBUG")
            
            # プロセスを実行
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            self.update_progress(2, 0.3, "音声データを処理中...")
            
            # 出力を監視
            stage_progress = {
                "Loading": (2, 0.3),
                "Processing": (3, 0.6),
                "Converting": (3, 0.8),
                "Saving": (4, 0.9)
            }
            
            current_stage = 2
            current_progress = 0.3
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if line:
                    line = line.strip()
                    if line:
                        self.log_message(line, "INFO")
                        
                        # プログレス更新のキーワードを探す
                        for keyword, (stage, progress) in stage_progress.items():
                            if keyword.lower() in line.lower():
                                current_stage = stage
                                current_progress = progress
                                self.update_progress(stage, progress, line)
                                break
                        else:
                            # 進捗を少しずつ進める
                            if current_progress < 0.85:
                                current_progress += 0.05
                                self.update_progress(current_stage, current_progress, line)
            
            # エラー出力を取得
            stderr_output = process.stderr.read()
            if stderr_output:
                for line in stderr_output.split('\n'):
                    if line.strip():
                        self.log_message(line, "WARNING")
            
            # プロセスの終了コードを確認
            if process.returncode == 0:
                self.update_progress(5, 1.0, "変換が完了しました！")
                self.log_message(f"出力ファイル: {params['output_path']}", "SUCCESS")
                self.root.after(0, self.conversion_complete)
            else:
                raise Exception(f"変換プロセスがエラーコード {process.returncode} で終了しました")
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"RVC execution error: {error_msg}", exc_info=True)
            self.root.after(0, self.conversion_error, error_msg)
    
    def conversion_error(self, error_msg):
        """変換エラー時の処理"""
        self.is_converting = False
        self.convert_button.config(state='normal', text="音声変換を開始")
        
        self.log_message(error_msg, "ERROR")
        self.update_progress(0, 0, "エラーが発生しました")
        
        # エラーダイアログ
        messagebox.showerror("変換エラー", f"変換中にエラーが発生しました:\n\n{error_msg}")
    
    def conversion_complete(self):
        """変換完了時の処理"""
        self.is_converting = False
        self.convert_button.config(state='normal', text="音声変換を開始")
        
        # 完了メッセージ
        output_path = os.path.join(
            self.output_var.get() or os.path.dirname(self.input_var.get()),
            self.output_filename_var.get()
        )
        
        # 成功ダイアログ
        result = messagebox.askquestion(
            "変換完了",
            "音声変換が完了しました！\n\n出力ファイルを開きますか？",
            icon='info'
        )
        
        if result == 'yes':
            # ファイルを開く
            if sys.platform == 'darwin':
                subprocess.call(['open', output_path])
            elif sys.platform == 'win32':
                os.startfile(output_path)
            else:
                subprocess.call(['xdg-open', output_path])

# =============================================================================
# メイン実行セクション
# =============================================================================

def main():
    """アプリケーションのエントリーポイント"""
    root = tk.Tk()
    
    # アプリケーションアイコンの設定（もしあれば）
    try:
        if sys.platform == 'darwin':
            # macOS用のアイコン設定
            pass
        else:
            # その他のプラットフォーム
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
    except:
        pass
    
    # GUIの作成
    app = DarkModeGUI(root)
    
    # メインループの開始
    root.mainloop()

if __name__ == "__main__":
    main()