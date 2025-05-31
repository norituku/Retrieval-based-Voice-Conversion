#!/usr/bin/env python3
"""
RVC Dark Mode GUI - コンパクト版
全ての要素をウィンドウ内に収めた最適化バージョン
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
        
        # ダークモードデザイントークン（コンパクト版）
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
            
            # タイポグラフィ - コンパクト版
            'typography': {
                'large_title': {'size': 22, 'weight': 'normal'},
                'title1': {'size': 18, 'weight': 'normal'},
                'title2': {'size': 15, 'weight': 'normal'},
                'title3': {'size': 13, 'weight': 'normal'},
                'headline': {'size': 12, 'weight': 'bold'},
                'body': {'size': 11, 'weight': 'normal'},
                'body_bold': {'size': 11, 'weight': 'bold'},
                'callout': {'size': 10, 'weight': 'normal'},
                'subheadline': {'size': 10, 'weight': 'normal'},
                'footnote': {'size': 9, 'weight': 'normal'},
                'caption1': {'size': 8, 'weight': 'normal'},
                'caption2': {'size': 8, 'weight': 'normal'},
            },
            
            # スペーシング - コンパクトな1ptグリッドシステム
            'spacing': {
                'xxxs': 1,
                'xxs': 2,
                'xs': 3,
                'sm': 4,
                'md': 6,
                'lg': 8,
                'xl': 10,
                'xxl': 12,
                'xxxl': 14,
                'xxxxl': 16,
            },
            
            # コーナー半径
            'radius': {
                'tiny': 2,
                'small': 3,
                'medium': 4,
                'large': 6,
                'extra_large': 8,
                'round': 999,
            },
            
            # レイアウト（コンパクト版）
            'layout': {
                'sidebar_width': 220,
                'min_window_width': 900,
                'min_window_height': 550,
                'toolbar_height': 36,
                'max_content_width': 600,
            }
        }
        
        self.colors = self.design_tokens['colors']
        
        # フォントファミリーの定義
        self.fonts = {
            'family': 'SF Pro Display',
            'mono': 'SF Mono'
        }
        
        # アプリケーション設定（高品質設定で固定）
        self.setup_app_directories()
        self.model_info = {}
        self.selected_model = tk.StringVar()
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.pitch_var = tk.IntVar(value=0)
        self.f0_method_var = tk.StringVar(value="rmvpe")  # 最高品質
        self.index_rate_var = tk.DoubleVar(value=1.0)     # 最大インデックス使用
        self.filter_radius_var = tk.IntVar(value=3)       # 推奨値
        self.rms_mix_rate_var = tk.DoubleVar(value=0.25)  # 推奨値
        self.protect_var = tk.DoubleVar(value=0.33)       # 推奨値
        
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
            
        self.model_dir = os.path.join(self.base_dir, "model_dir")
        self.config_dir = os.path.join(self.base_dir, "configs")
        
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
        
        # スクロールバー（より細く）
        style.configure('Dark.Vertical.TScrollbar',
                       background=self.colors['background_secondary'],
                       darkcolor=self.colors['background_tertiary'],
                       lightcolor=self.colors['background_tertiary'],
                       troughcolor=self.colors['background_primary'],
                       bordercolor=self.colors['background_primary'],
                       arrowcolor=self.colors['text_tertiary'],
                       relief='flat',
                       width=10)
        
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
        
        # プログレスバー（高さを小さく）
        style.configure('Dark.Horizontal.TProgressbar',
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['background_tertiary'],
                       bordercolor=self.colors['background_tertiary'],
                       lightcolor=self.colors['accent_primary'],
                       darkcolor=self.colors['accent_primary'],
                       thickness=6)
        
    def setup_window(self):
        """ウィンドウの基本設定"""
        # 背景色
        self.root.configure(bg=self.colors['background_primary'])
        
        # 画面サイズを取得
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # ウィンドウサイズを画面サイズに応じて調整
        window_width = min(self.design_tokens['layout']['min_window_width'], int(screen_width * 0.8))
        window_height = min(self.design_tokens['layout']['min_window_height'], int(screen_height * 0.8))
        
        # 画面中央に配置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(850, 500)
        
        # macOS用の設定
        if sys.platform == "darwin":
            # スケーリングを調整
            try:
                current_scaling = self.root.tk.call('tk', 'scaling')
                if current_scaling > 1.5:
                    self.root.tk.call('tk', 'scaling', 1.3)
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
        icon_canvas = tk.Canvas(left_frame, width=24, height=24, 
                               bg=self.colors['background_secondary'], 
                               highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, pady=6)
        
        # グラデーション風アイコン
        self.draw_gradient_icon(icon_canvas)
        
        # タイトル
        title_label = tk.Label(left_frame, text="Voice Converter",
                              font=('SF Pro Display', 15, 'bold'),
                              bg=self.colors['background_secondary'],
                              fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=self.design_tokens['spacing']['sm'])
        
    def draw_gradient_icon(self, canvas):
        """グラデーションアイコンを描画"""
        # 外側の円
        canvas.create_oval(2, 2, 22, 22, 
                          fill=self.colors['accent_primary'], 
                          outline='')
        # 内側の円
        canvas.create_oval(4, 4, 20, 20, 
                          fill=self.colors['accent_secondary'], 
                          outline='')
        # 波形アイコン
        canvas.create_text(12, 12, text="♪", 
                          fill="white", 
                          font=("Arial", 14, "bold"))
        
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
        
        tk.Label(header, text="Voice Models",
                font=('SF Pro Display', 14, 'bold'),
                bg=self.colors['surface_sidebar'],
                fg=self.colors['text_primary']).pack(anchor='w')
        
        tk.Label(header, text="Select a model",
                font=('SF Pro Display', 10),
                bg=self.colors['surface_sidebar'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(1, 0))
        
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
                             padx=self.design_tokens['spacing']['xs'],
                             pady=self.design_tokens['spacing']['xs'])
        
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
        """メインコンテンツエリア（スクロールなし、固定レイアウト）"""
        # メインコンテンツコンテナ
        content_container = tk.Frame(self.right_column, bg=self.colors['background_primary'])
        content_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        
        # 上部コンテンツ（入力と設定）
        top_content = tk.Frame(content_container, bg=self.colors['background_primary'])
        top_content.pack(fill=tk.X)
        
        # 入力セクション
        self.create_input_section(top_content)
        
        # 設定セクション
        self.create_settings_section(top_content)
        
        # 変換ボタン
        self.create_conversion_button(top_content)
        
        # 下部コンテンツ（ステータスとログ）
        bottom_content = tk.Frame(content_container, bg=self.colors['background_primary'])
        bottom_content.pack(fill=tk.BOTH, expand=True)
        
        # ステータスセクション
        self.create_status_section(bottom_content)
        
        # ログセクション（残りのスペースを使用）
        self.create_log_section(bottom_content)
        
    def create_input_section(self, parent):
        """入力セクション（コンパクト版）"""
        # カードコンテナ
        input_card = self.create_card(parent, "Input Audio")
        
        # ファイル選択エリア
        file_area = tk.Frame(input_card, bg=self.colors['surface_card'])
        file_area.pack(fill=tk.X)
        
        # 左側：ボタン
        browse_btn = self.create_button(file_area, "Choose File", 
                                       self.browse_input, 
                                       style='Primary',
                                       compact=True)
        browse_btn.pack(side=tk.LEFT)
        
        # 右側：選択されたファイル情報
        self.file_info_frame = tk.Frame(file_area, bg=self.colors['surface_card'])
        self.file_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, 
                                 padx=(self.design_tokens['spacing']['md'], 0))
        
    def create_settings_section(self, parent):
        """設定セクション（コンパクト版）"""
        settings_card = self.create_card(parent, "Settings")
        
        # 2カラムレイアウト
        settings_grid = tk.Frame(settings_card, bg=self.colors['surface_card'])
        settings_grid.pack(fill=tk.X)
        
        # 左カラム：出力設定
        left_col = tk.Frame(settings_grid, bg=self.colors['surface_card'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 出力ディレクトリ設定
        output_frame = tk.Frame(left_col, bg=self.colors['surface_card'])
        output_frame.pack(fill=tk.X)
        
        # ラベル
        output_label = tk.Label(output_frame, text="Output Directory",
                               font=('SF Pro Display', 11, 'bold'),
                               bg=self.colors['surface_card'],
                               fg=self.colors['text_secondary'])
        output_label.pack(anchor='w', pady=(0, 2))
        
        # パス表示とブラウズボタンのコンテナ
        path_container = tk.Frame(output_frame, bg=self.colors['surface_card'])
        path_container.pack(fill=tk.X)
        
        # パス表示（コンパクト）
        self.output_path_frame = tk.Frame(path_container, 
                                         bg=self.colors['background_secondary'],
                                         relief='flat',
                                         height=28)
        self.output_path_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_path_frame.pack_propagate(False)
        
        path_inner = tk.Frame(self.output_path_frame, bg=self.colors['background_secondary'])
        path_inner.place(relx=0, rely=0.5, anchor='w', x=6)
        
        # デフォルト出力パス
        default_output = os.path.join(os.path.expanduser("~"), "Desktop", "VoiceConverter_Output")
        self.output_var.set(default_output)
        
        self.output_path_label = tk.Label(path_inner, 
                                         text=self.truncate_path(self.output_var.get(), 40),
                                         font=('SF Pro Mono', 10),
                                         bg=self.colors['background_secondary'],
                                         fg=self.colors['text_primary'],
                                         anchor='w')
        self.output_path_label.pack(fill=tk.X)
        
        # ブラウズボタン（コンパクト）
        browse_output_btn = self.create_button(path_container, "...", 
                                              self.browse_output, 
                                              style='Secondary',
                                              compact=True)
        browse_output_btn.pack(side=tk.RIGHT, padx=(4, 0))
        
        # 出力ファイル名プレビュー
        self.output_preview_label = tk.Label(output_frame, 
                                           text="",
                                           font=('SF Pro Mono', 9),
                                           bg=self.colors['surface_card'],
                                           fg=self.colors['text_tertiary'])
        self.output_preview_label.pack(anchor='w', pady=(2, 0))
        
        # 右カラム：ピッチ設定
        right_col = tk.Frame(settings_grid, bg=self.colors['surface_card'])
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(self.design_tokens['spacing']['lg'], 0))
        
        # ピッチ設定
        self.create_compact_setting_control(right_col, "Pitch", self.pitch_var, 
                                          -12, 12, 0, "semitones")
        
    def create_compact_setting_control(self, parent, label, variable, min_val, max_val, row, unit=""):
        """コンパクトな設定コントロール"""
        # コンテナフレーム
        control_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        control_frame.pack(fill=tk.X)
        
        # ラベルと値を横並びに
        header_frame = tk.Frame(control_frame, bg=self.colors['surface_card'])
        header_frame.pack(fill=tk.X)
        
        # ラベル
        label_text = tk.Label(header_frame, text=label,
                            font=('SF Pro Display', 11, 'bold'),
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
        
        value_label = tk.Label(header_frame, 
                             text=format_value(),
                             font=('SF Pro Mono', 11, 'bold'),
                             bg=self.colors['surface_card'],
                             fg=self.colors['accent_primary'])
        value_label.pack(side=tk.RIGHT)
        
        # スライダー（コンパクト）
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
                         width=10,
                         sliderlength=15)
        slider.pack(fill=tk.X)
        
        # 値更新時のコールバック
        def update_value_label(*args):
            value_label.config(text=format_value())
        
        variable.trace('w', update_value_label)
        
    def create_conversion_button(self, parent):
        """変換ボタンセクション（コンパクト）"""
        button_frame = tk.Frame(parent, bg=self.colors['background_primary'])
        button_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['md'], self.design_tokens['spacing']['sm']))
        
        # ボタンコンテナ（中央配置）
        button_container = tk.Frame(button_frame, bg=self.colors['background_primary'])
        button_container.pack()
        
        # プライマリー変換ボタン
        convert_btn = self.create_button(button_container, 
                                       "Start Conversion", 
                                       self.start_conversion,
                                       style='Primary',
                                       width=160,
                                       height=32)
        convert_btn.pack()
        
    def create_status_section(self, parent):
        """ステータスセクション（コンパクト版）"""
        # ステータスカード用のコンテナを作成
        self.status_container = tk.Frame(parent, bg=self.colors['background_primary'])
        self.status_container.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['sm']))
        
        # 初期状態では非表示
        self.status_card = self.create_card(self.status_container, "Processing Status", visible=False)
        
        # プログレスバーとパーセンテージ
        progress_container = tk.Frame(self.status_card, bg=self.colors['surface_card'])
        progress_container.pack(fill=tk.X)
        
        # プログレスバー
        self.progress = ttk.Progressbar(progress_container, 
                                      mode='determinate',
                                      maximum=100,
                                      style='Dark.Horizontal.TProgressbar')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # パーセンテージラベル
        self.percentage_label = tk.Label(progress_container, 
                                       text="0%",
                                       font=('SF Pro Display', 11, 'bold'),
                                       bg=self.colors['surface_card'],
                                       fg=self.colors['accent_primary'])
        self.percentage_label.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['sm'], 0))
        
        # ステータステキスト
        self.status_label = tk.Label(self.status_card, 
                                   text="",
                                   font=('SF Pro Display', 10),
                                   bg=self.colors['surface_card'],
                                   fg=self.colors['text_secondary'],
                                   wraplength=400)
        self.status_label.pack(anchor='w', pady=(self.design_tokens['spacing']['xs'], 0))
    
    def create_log_section(self, parent):
        """ログセクション（コンパクト版）"""
        log_card = self.create_card(parent, "Console", fill_expand=True)
        
        # ログテキストエリア用のフレーム
        log_frame = tk.Frame(log_card, bg=self.colors['background_tertiary'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # スクロールバー
        log_scrollbar = ttk.Scrollbar(log_frame, style='Dark.Vertical.TScrollbar')
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ログテキストエリア（高さを小さく）
        self.log_text = tk.Text(log_frame,
                               wrap=tk.WORD,
                               height=6,  # 高さを削減
                               bg=self.colors['background_tertiary'],
                               fg=self.colors['text_secondary'],
                               font=(self.fonts['mono'], 9),
                               relief=tk.FLAT,
                               padx=8,
                               pady=6,
                               yscrollcommand=log_scrollbar.set,
                               selectbackground=self.colors['accent_primary'],
                               selectforeground=self.colors['text_primary'])
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        log_scrollbar.config(command=self.log_text.yview)
        
        # 初期メッセージ
        self.log_text.insert(tk.END, "Voice Converter Ready.\n")
        self.log_text.config(state=tk.NORMAL)
    
    def log_message(self, message, level="INFO"):
        """ログメッセージを追加"""
        if not hasattr(self, 'log_text'):
            print(f"[{level}] {message}")
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
    def update_progress(self, stage_index, progress, message):
        """プログレスバーを更新（シンプル版）"""
        if not hasattr(self, 'status_card'):
            return
            
        # 全体の進捗を計算（7ステージ）
        total_stages = 7
        stage_progress = (stage_index / total_stages) * 100
        current_stage_progress = (progress / 100) * (100 / total_stages)
        total_progress = stage_progress + current_stage_progress
        
        # UIを更新
        self.root.after(0, lambda: self._update_progress_ui(total_progress, message))
        
    def _update_progress_ui(self, total_progress, message):
        """UIスレッドでプログレスを更新"""
        # ステータスカードを表示
        if not self.status_card.winfo_viewable():
            self.status_card.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['sm']))
        
        # プログレスバーを更新
        self.progress['value'] = total_progress
        self.percentage_label.config(text=f"{int(total_progress)}%")
        
        # ステータステキストを更新
        self.status_label.config(text=message)
        
        # UIを更新
        self.root.update_idletasks()
        
    def create_card(self, parent, title, visible=True, fill_expand=False):
        """カードUI要素を作成（コンパクト版）"""
        card = tk.Frame(parent, 
                       bg=self.colors['surface_card'],
                       relief='flat')
        if visible:
            if fill_expand:
                card.pack(fill=tk.BOTH, expand=True, pady=(0, self.design_tokens['spacing']['sm']))
            else:
                card.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['sm']))
        
        # カード内部のパディング（コンパクト）
        inner = tk.Frame(card, bg=self.colors['surface_card'])
        inner.pack(fill=tk.BOTH, expand=True, 
                  padx=self.design_tokens['spacing']['sm'],
                  pady=self.design_tokens['spacing']['sm'])
        
        # タイトル
        if title:
            title_label = tk.Label(inner, text=title,
                                 font=('SF Pro Display', 12, 'bold'),
                                 bg=self.colors['surface_card'],
                                 fg=self.colors['text_primary'])
            title_label.pack(anchor='w', pady=(0, self.design_tokens['spacing']['xs']))
            
            # 区切り線
            separator = tk.Frame(inner, 
                               bg=self.colors['divider'], 
                               height=1)
            separator.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        return inner
        
    def create_button(self, parent, text, command, style='Primary', width=None, height=None, compact=False):
        """カスタムボタンを作成（コンパクト版）"""
        btn_frame = tk.Frame(parent, bg=parent['bg'])
        
        if style == 'Primary':
            bg_color = self.colors['accent_primary']
            fg_color = 'white'
            hover_color = '#4A8FEF'
            active_color = '#3A7FDF'
            font_style = ('SF Pro Display', 11, 'bold')
        else:
            bg_color = self.colors['background_tertiary']
            fg_color = self.colors['text_primary']
            hover_color = self.colors['background_elevated']
            active_color = self.colors['background_secondary']
            font_style = ('SF Pro Display', 10, 'normal')
            
        btn = tk.Label(btn_frame, text=text,
                      font=font_style,
                      bg=bg_color,
                      fg=fg_color,
                      cursor='hand2')
        
        # サイズ設定
        if compact:
            btn.config(padx=8, pady=3)
        elif width and height:
            btn.config(padx=12, pady=6)
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
            self.root.after(100, lambda: btn.config(bg=bg_color))
            command()
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', on_click)
        
        return btn_frame
    
    def truncate_path(self, path, max_length=40):
        """長いパスを省略"""
        if len(path) <= max_length:
            return path
        
        parts = path.split(os.sep)
        if len(parts) <= 3:
            return path
            
        # ホームディレクトリを~に置換
        home = os.path.expanduser("~")
        if path.startswith(home):
            path = "~" + path[len(home):]
            
        if len(path) <= max_length:
            return path
            
        # 最初と最後を残して中間を省略
        filename = os.path.basename(path)
        if len(filename) > max_length - 10:
            # ファイル名自体が長い場合
            name, ext = os.path.splitext(filename)
            if len(name) > 20:
                filename = name[:20] + "..." + ext
                
        dirname = os.path.dirname(path)
        parts = dirname.split(os.sep)
        
        if len(parts) > 3:
            result = os.sep.join(parts[:2]) + os.sep + "..." + os.sep + parts[-1] + os.sep + filename
        else:
            result = dirname + os.sep + filename
            
        return result if len(result) <= max_length else "..." + result[-(max_length-3):]
    
    def load_models(self):
        """モデルをロード"""
        if not os.path.exists(self.model_dir):
            self.log_message("Model directory not found. Creating it...", "WARNING")
            os.makedirs(self.model_dir)
            return
            
        # モデルを検索（番号付きディレクトリまたは.pthファイル）
        models_found = []
        
        # 番号付きディレクトリ内の.onnxファイルを検索
        for item in os.listdir(self.model_dir):
            item_path = os.path.join(self.model_dir, item)
            
            # 番号付きディレクトリの場合
            if os.path.isdir(item_path) and item.isdigit():
                # ディレクトリ内の.onnxファイルを検索
                for file in os.listdir(item_path):
                    if file.endswith('.onnx'):
                        model_name = os.path.splitext(file)[0]
                        models_found.append({
                            'name': model_name,
                            'file': file,
                            'path': os.path.join(item_path, file),
                            'dir': item
                        })
                        break  # 各ディレクトリから最初の.onnxファイルのみ
            
            # 直接配置された.pthファイルの場合
            elif item.endswith('.pth') and not item in ['hubert_base.pt', 'rmvpe.pt']:
                model_name = os.path.splitext(item)[0]
                models_found.append({
                    'name': model_name,
                    'file': item,
                    'path': item_path,
                    'dir': None
                })
                
        if not models_found:
            self.log_message("No models found in model_dir", "WARNING")
            # サンプルモデルカードを作成
            self.create_model_card("No models available", None)
            return
            
        # 各モデルのカードを作成
        for model in sorted(models_found, key=lambda x: x['name']):
            model_name = model['name']
            self.model_info[model_name] = {
                'file': model['file'],
                'path': model['path'],
                'dir': model['dir']
            }
            
            # params.jsonファイルを確認（onnxモデルの場合）
            if model['dir']:
                params_path = os.path.join(self.model_dir, model['dir'], 'params.json')
                if os.path.exists(params_path):
                    self.model_info[model_name]['params'] = params_path
                    self.log_message(f"Found params for {model_name}", "INFO")
            
            # indexファイルを検索（pthモデルの場合）
            else:
                index_files = [f for f in os.listdir(self.model_dir) 
                             if f.startswith(model_name) and f.endswith('.index')]
                if index_files:
                    self.model_info[model_name]['index'] = os.path.join(self.model_dir, index_files[0])
                    self.log_message(f"Found index for {model_name}: {index_files[0]}", "INFO")
                
            self.create_model_card(model_name, model_name)
            
        self.log_message(f"Loaded {len(models_found)} models", "INFO")
        
    def create_model_card(self, name, value):
        """モデルカードを作成（コンパクト版）"""
        card = tk.Frame(self.model_frame, 
                       bg=self.colors['surface_card'],
                       relief='flat')
        card.pack(fill=tk.X, padx=self.design_tokens['spacing']['xs'], 
                 pady=self.design_tokens['spacing']['xs'])
        
        # カード内部
        inner = tk.Frame(card, bg=self.colors['surface_card'])
        inner.pack(fill=tk.BOTH, expand=True, 
                  padx=self.design_tokens['spacing']['sm'],
                  pady=self.design_tokens['spacing']['sm'])
        
        # ラジオボタン（valueがNoneでない場合のみ）
        if value is not None:
            radio = tk.Radiobutton(inner, 
                                 text=name,
                                 variable=self.selected_model,
                                 value=value,
                                 bg=self.colors['surface_card'],
                                 fg=self.colors['text_primary'],
                                 activebackground=self.colors['surface_card'],
                                 activeforeground=self.colors['accent_primary'],
                                 selectcolor=self.colors['surface_card'],
                                 font=('SF Pro Display', 11),
                                 command=self.on_model_selected)
            radio.pack(anchor='w')
        else:
            # モデルがない場合のメッセージ
            label = tk.Label(inner, text=name,
                           font=('SF Pro Display', 11),
                           bg=self.colors['surface_card'],
                           fg=self.colors['text_tertiary'])
            label.pack(anchor='w')
        
        # ホバーエフェクト
        def on_enter(e):
            card.config(bg=self.colors['hover'])
            inner.config(bg=self.colors['hover'])
            if value is not None:
                radio.config(bg=self.colors['hover'], activebackground=self.colors['hover'])
            else:
                label.config(bg=self.colors['hover'])
            
        def on_leave(e):
            card.config(bg=self.colors['surface_card'])
            inner.config(bg=self.colors['surface_card'])
            if value is not None:
                radio.config(bg=self.colors['surface_card'], activebackground=self.colors['surface_card'])
            else:
                label.config(bg=self.colors['surface_card'])
        
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        
    def browse_input(self):
        """入力ファイルを選択"""
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.input_var.set(filename)
            self.update_file_info(filename)
            self.update_output_preview()
            self.log_message(f"Selected input: {os.path.basename(filename)}", "INFO")
            
    def update_file_info(self, filepath):
        """ファイル情報を更新"""
        # 既存の情報をクリア
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
            
        # ファイル名
        filename = os.path.basename(filepath)
        name_label = tk.Label(self.file_info_frame, 
                            text=self.truncate_path(filename, 30),
                            font=('SF Pro Display', 11, 'bold'),
                            bg=self.colors['surface_card'],
                            fg=self.colors['text_primary'])
        name_label.pack(anchor='w')
        
        # ファイルサイズ
        try:
            size = os.path.getsize(filepath)
            size_str = self.format_file_size(size)
            size_label = tk.Label(self.file_info_frame, 
                                text=f"Size: {size_str}",
                                font=('SF Pro Display', 9),
                                bg=self.colors['surface_card'],
                                fg=self.colors['text_secondary'])
            size_label.pack(anchor='w')
        except:
            pass
            
    def format_file_size(self, size):
        """ファイルサイズをフォーマット"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
        
    def browse_output(self):
        """出力ディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_var.get()
        )
        
        if directory:
            self.output_var.set(directory)
            self.output_path_label.config(text=self.truncate_path(directory, 40))
            self.update_output_preview()
            self.log_message(f"Output directory: {directory}", "INFO")
            
    def on_model_selected(self):
        """モデル選択時の処理"""
        self.update_output_preview()
        self.log_message(f"Selected model: {self.selected_model.get()}", "INFO")
        
    def update_output_preview(self):
        """出力ファイル名のプレビューを更新"""
        if self.input_var.get() and self.selected_model.get():
            input_name = os.path.splitext(os.path.basename(self.input_var.get()))[0]
            model_name = self.selected_model.get()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            output_filename = f"{input_name}_{model_name}_{timestamp}.wav"
            output_path = os.path.join(self.output_var.get(), output_filename)
            
            preview_text = f"Output: {self.truncate_path(output_filename, 50)}"
            self.output_preview_label.config(text=preview_text, fg=self.colors['text_primary'])
        else:
            self.output_preview_label.config(text="", fg=self.colors['text_tertiary'])
            
    def start_conversion(self):
        """音声変換を開始"""
        # 入力チェック
        if not self.input_var.get():
            messagebox.showwarning("Warning", "Please select an input audio file.")
            return
            
        if not self.selected_model.get():
            messagebox.showwarning("Warning", "Please select a voice model.")
            return
            
        # 出力ディレクトリ作成
        os.makedirs(self.output_var.get(), exist_ok=True)
        
        # 変換処理を別スレッドで実行
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
        
    def run_conversion(self):
        """変換処理を実行"""
        try:
            # UIの初期化
            self.root.after(0, lambda: self.update_progress(0, 0, "初期化中..."))
            self.log_message("Starting voice conversion...", "INFO")
            
            # モデル情報取得
            model_name = self.selected_model.get()
            model_info = self.model_info.get(model_name)
            
            if not model_info:
                raise ValueError(f"Model {model_name} not found")
                
            # 出力ファイルパス生成
            input_name = os.path.splitext(os.path.basename(self.input_var.get()))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{input_name}_{model_name}_{timestamp}.wav"
            output_path = os.path.join(self.output_var.get(), output_filename)
            
            # RVCコマンド構築
            if USE_HARDCODED_PATH:
                cmd = [POETRY_PYTHON_PATH, "-m", RVC_MODULE]
            else:
                cmd = ["python", "-m", "rvc_cli"]
                
            cmd.extend([
                "infer",
                "-m", model_info['path'],
                "-i", self.input_var.get(),
                "-o", output_path,
                "-pit", str(self.pitch_var.get()),
                "-fm", self.f0_method_var.get(),
                "-ir", str(self.index_rate_var.get()),
                "-fr", str(self.filter_radius_var.get()),
                "-rms", str(self.rms_mix_rate_var.get()),
                "-pro", str(self.protect_var.get())
            ])
            
            # indexファイルがある場合
            if model_info.get('index'):
                cmd.extend(["-index", model_info['index']])
                
            self.log_message(f"Command: {' '.join(cmd)}", "DEBUG")
            
            # プロセス実行
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 出力を監視
            stage_patterns = {
                "Loading model": (1, "モデルを読み込んでいます"),
                "Processing audio": (2, "音声を処理しています"),
                "Extracting features": (3, "特徴を抽出しています"),
                "Converting voice": (4, "音声を変換しています"),
                "Post-processing": (5, "後処理を実行しています"),
                "Saving output": (6, "ファイルを保存しています")
            }
            
            current_stage = 0
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                    
                if line:
                    line = line.strip()
                    self.log_message(line, "PROCESS")
                    
                    # ステージ検出
                    for pattern, (stage, message) in stage_patterns.items():
                        if pattern in line:
                            current_stage = stage
                            self.root.after(0, lambda s=stage, m=message: 
                                          self.update_progress(s, 0, m))
                            
                    # プログレス検出
                    if "%" in line:
                        try:
                            import re
                            match = re.search(r'(\d+)%', line)
                            if match:
                                percent = int(match.group(1))
                                self.root.after(0, lambda s=current_stage, p=percent: 
                                              self.update_progress(s, p, line))
                        except:
                            pass
                            
            # プロセス完了待ち
            return_code = process.wait()
            
            if return_code == 0:
                self.root.after(0, lambda: self.update_progress(6, 100, "変換完了！"))
                self.log_message(f"Conversion completed: {output_filename}", "SUCCESS")
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"Voice conversion completed!\n\nOutput: {output_filename}"))
            else:
                stderr = process.stderr.read()
                raise RuntimeError(f"Conversion failed with code {return_code}\n{stderr}")
                
        except Exception as e:
            self.log_message(f"Error: {str(e)}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror("Error", 
                f"Conversion failed:\n{str(e)}"))
        finally:
            # UIをリセット
            self.root.after(1000, lambda: self.reset_ui())
            
    def reset_ui(self):
        """UIをリセット"""
        self.progress['value'] = 0
        self.percentage_label.config(text="0%")
        self.status_label.config(text="")
        # ステータスカードを非表示にする
        self.status_card.pack_forget()

def main():
    root = tk.Tk()
    app = DarkModeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
