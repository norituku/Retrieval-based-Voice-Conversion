#!/usr/bin/env python3
"""
RVC Dark Mode GUI - Enhanced Stable Version
セグメンテーションフォルト問題を修正した安定版
UIは完全に保持し、イベントバインディングを最適化
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

# 改善モジュールのインポート
try:
    from gui_modules import SettingsManager, ErrorHandler, init_error_handler
    from gui_modules import ComponentFactory, ThemeConfig, ComponentStyle, ComponentSize
    from gui_modules import KeyboardShortcutManager, ShortcutModifier, ShortcutCategory
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("改善モジュールが利用できません。基本機能のみで動作します。")

# 改良版音声変換のインポート
try:
    from enhanced_converter_simple import SimpleEnhancedConverter
    ENHANCED_CONVERTER_AVAILABLE = True
    print("✅ Simple Enhanced Voice Converter loaded")
except ImportError as e:
    ENHANCED_CONVERTER_AVAILABLE = False
    print(f"⚠️ Enhanced Voice Converter not available: {e}")

class DarkModeGUIStable:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter - Enhanced Stable Edition")
        
        # 安全な初期化フラグ
        self.initializing = True
        
        # セグメンテーションフォルト対策: イベントバインディングを最小限に
        self.enable_hover_effects = False  # ホバーエフェクトを無効化
        self.safe_event_handling = True    # 安全なイベント処理モード
        
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
                
                # インタラクティブ状態（ホバーは無効化）
                'hover': '#2A2A2E',       # 使用しない
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
                'title1': {'size': 22, 'weight': 'bold'},
                'title2': {'size': 20, 'weight': 'bold'},
                'title3': {'size': 18, 'weight': 'bold'},
                'headline': {'size': 16, 'weight': 'bold'},
                'body': {'size': 13, 'weight': 'normal'},
                'callout': {'size': 14, 'weight': 'normal'},
                'subhead': {'size': 12, 'weight': 'bold'},
                'footnote': {'size': 11, 'weight': 'normal'},
                'caption1': {'size': 10, 'weight': 'normal'},
                'caption2': {'size': 9, 'weight': 'normal'},
            },
            
            # スペーシングシステム - 8ptベース（よりコンパクト）
            'spacing': {
                'xs': 4,    # 0.5 * 8
                'sm': 8,    # 1 * 8
                'md': 16,   # 2 * 8
                'lg': 24,   # 3 * 8
                'xl': 32,   # 4 * 8
                'xxl': 48,  # 6 * 8
            },
            
            # エレベーション（ドロップシャドウ）
            'elevation': {
                'card': {'offset': (0, 1), 'blur': 3, 'opacity': 0.15},
                'raised': {'offset': (0, 4), 'blur': 8, 'opacity': 0.2},
                'modal': {'offset': (0, 8), 'blur': 16, 'opacity': 0.25},
                'floating': {'offset': (0, 12), 'blur': 24, 'opacity': 0.3},
            },
            
            # ボーダー半径
            'border_radius': {
                'xs': 4,
                'sm': 6,
                'md': 8,
                'lg': 12,
                'xl': 16,
                'pill': 9999,
            }
        }
        
        # ショートカットアクセス
        self.colors = self.design_tokens['colors']
        self.typography = self.design_tokens['typography']
        self.spacing = self.design_tokens['spacing']
        
        # ウィンドウの基本設定
        self.root.configure(bg=self.colors['background_primary'])
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
        # セグフォルト対策: 複雑な初期化を段階的に実行
        try:
            self.init_safe_variables()
            self.init_enhanced_converter()
            self.setup_styles()
            self.create_safe_layout()
            self.initializing = False
            print("✅ Stable GUI initialization completed")
        except Exception as e:
            print(f"❌ GUI initialization error: {e}")
            self.initializing = False
            raise
    
    def init_safe_variables(self):
        """安全な変数初期化"""
        # tkinter変数（遅延初期化）
        self.selected_model = tk.StringVar()
        self.selected_input_file = tk.StringVar()
        self.model_dir_var = tk.StringVar()
        self.output_filename_var = tk.StringVar()
        
        # 基本パス設定
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            if os.path.basename(exe_dir) == "MacOS":
                self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(exe_dir)))
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
        
        # 変換制御フラグ
        self.converting = False
        self.conversion_thread = None
        self.model_info = {}
        
        # ファイル名制御
        self.is_manual_filename = False
        
    def load_settings(self):
        """設定ファイルの読み込み"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.model_dir_var.set(settings.get('model_directory', ''))
        except Exception as e:
            print(f"Settings load error: {e}")
            
    def init_enhanced_converter(self):
        """改良版音声変換システムの安全な初期化"""
        self.enhanced_converter = None
        self.use_enhanced_conversion = False
        self.enhancement_status = None
        
        if ENHANCED_CONVERTER_AVAILABLE:
            try:
                # 遅延初期化で安全性を確保
                self.enhanced_converter = SimpleEnhancedConverter(
                    model_dir=self.model_dir or "model_dir",
                    output_dir="enhanced_output"
                )
                self.use_enhanced_conversion = True
                
                # 改良機能の状態を取得（エラー処理付き）
                try:
                    self.enhancement_status = self.enhanced_converter.get_enhancement_status()
                    print(f"✅ Enhanced features active: {list(self.enhancement_status['features'].keys())}")
                except Exception as e:
                    print(f"⚠️ Enhancement status unavailable: {e}")
                    self.enhancement_status = {'pipeline_type': 'enhanced_simple', 'features': {}}
                
            except Exception as e:
                print(f"❌ Enhanced converter initialization failed: {e}")
                # 安全にフォールバック
                self.enhanced_converter = None
                self.use_enhanced_conversion = False
        
        if not self.use_enhanced_conversion:
            print("⚠️ Using standard conversion mode")
            self.enhancement_status = {'pipeline_type': 'standard', 'features': {}}
    
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
        
        # スクロールバー（イベントバインディングなし）
        style.configure('Dark.Vertical.TScrollbar',
                       background=self.colors['background_secondary'],
                       darkcolor=self.colors['background_tertiary'],
                       lightcolor=self.colors['background_tertiary'],
                       troughcolor=self.colors['background_primary'],
                       bordercolor=self.colors['background_primary'],
                       arrowcolor=self.colors['text_tertiary'],
                       relief='flat')
        
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
        
        # ボタン（ホバーエフェクトなし、クリック操作のみ）
        style.configure('Primary.TButton',
                       font=('SF Pro Display', self.design_tokens['typography']['body']['size'], 'bold'),
                       background=self.colors['accent_primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        
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
        
        # エントリー（必要最小限のイベントのみ）
        style.configure('Dark.TEntry',
                       fieldbackground=self.colors['background_secondary'],
                       borderwidth=1,
                       relief='solid',
                       insertcolor=self.colors['text_primary'])
        
        # プログレスバー
        style.configure('Dark.Horizontal.TProgressbar',
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['background_tertiary'],
                       bordercolor=self.colors['background_tertiary'])
    
    def create_safe_layout(self):
        """安全なレイアウト作成（最小限のイベントバインディング）"""
        # メインコンテナ
        main_container = tk.Frame(self.root, bg=self.colors['background_primary'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ヘッダー
        self.create_safe_header(main_container)
        
        # メインコンテンツエリア
        content_area = tk.Frame(main_container, bg=self.colors['background_primary'])
        content_area.pack(fill=tk.BOTH, expand=True, padx=self.spacing['lg'], pady=(0, self.spacing['lg']))
        
        # 左パネル（モデル選択）
        self.create_safe_left_panel(content_area)
        
        # 右パネル（変換設定・実行）
        self.create_safe_right_panel(content_area)
    
    def create_safe_header(self, parent):
        """安全なヘッダー作成"""
        header_frame = tk.Frame(parent, bg=self.colors['background_secondary'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # ヘッダーコンテンツ
        header_content = tk.Frame(header_frame, bg=self.colors['background_secondary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=self.spacing['lg'], pady=self.spacing['md'])
        
        # タイトル
        title_label = tk.Label(
            header_content, 
            text="Voice Converter - Enhanced Stable", 
            font=('SF Pro Display', self.typography['title1']['size'], 'bold'),
            fg=self.colors['text_primary'], 
            bg=self.colors['background_secondary']
        )
        title_label.pack(side=tk.LEFT, anchor='w')
        
        # 改良機能ステータス（クリック不可、表示のみ）
        if self.use_enhanced_conversion and self.enhancement_status:
            status_text = f"Enhanced: {self.enhancement_status['pipeline_type']}"
            status_label = tk.Label(
                header_content,
                text=status_text,
                font=('SF Pro Display', self.typography['footnote']['size']),
                fg=self.colors['success'],
                bg=self.colors['background_secondary']
            )
            status_label.pack(side=tk.RIGHT, anchor='e')
    
    def create_safe_left_panel(self, parent):
        """安全な左パネル作成（モデル選択）"""
        # 左パネルフレーム
        left_panel = tk.Frame(parent, bg=self.colors['background_primary'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, self.spacing['md']))
        
        # モデル選択セクション
        model_section = self.create_safe_card_frame(left_panel, "Voice Models", height=400)
        
        # モデルディレクトリ選択（ボタンクリックのみ、ホバーエフェクトなし）
        dir_frame = tk.Frame(model_section, bg=self.colors['surface_card'])
        dir_frame.pack(fill=tk.X, pady=(0, self.spacing['md']))
        
        dir_label = tk.Label(
            dir_frame, 
            text="Model Directory:", 
            font=('SF Pro Display', self.typography['body']['size']),
            fg=self.colors['text_secondary'], 
            bg=self.colors['surface_card']
        )
        dir_label.pack(anchor='w')
        
        dir_display_frame = tk.Frame(dir_frame, bg=self.colors['background_secondary'])
        dir_display_frame.pack(fill=tk.X, pady=(4, 8))
        
        self.model_dir_label = tk.Label(
            dir_display_frame,
            text=self.truncate_path(self.model_dir_var.get(), 60),
            font=('SF Pro Display', self.typography['footnote']['size']),
            fg=self.colors['text_tertiary'],
            bg=self.colors['background_secondary'],
            anchor='w'
        )
        self.model_dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=4)
        
        # 安全なボタン作成（ホバーエフェクトなし）
        browse_btn = self.create_safe_button(
            dir_display_frame, 
            "Browse", 
            self.browse_model_directory,
            style='secondary',
            width=80
        )
        browse_btn.pack(side=tk.RIGHT, padx=(8, 4))
        
        # モデル一覧（スクロール可能、安全なマウスホイールのみ）
        self.create_safe_model_list(model_section)
    
    def create_safe_right_panel(self, parent):
        """安全な右パネル作成（変換設定・実行）"""
        # 右パネルフレーム
        right_panel = tk.Frame(parent, bg=self.colors['background_primary'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(self.spacing['md'], 0))
        
        # 入力ファイル選択
        input_section = self.create_safe_card_frame(right_panel, "Input Audio", height=150)
        self.create_safe_input_section(input_section)
        
        # 変換パラメータ
        params_section = self.create_safe_card_frame(right_panel, "Conversion Parameters", height=200)
        self.create_safe_params_section(params_section)
        
        # 変換実行
        convert_section = self.create_safe_card_frame(right_panel, "Convert", height=120)
        self.create_safe_convert_section(convert_section)
    
    def create_safe_card_frame(self, parent, title, height=None):
        """安全なカードフレーム作成"""
        # カードコンテナ
        card_container = tk.Frame(parent, bg=self.colors['background_primary'])
        card_container.pack(fill=tk.X, pady=(0, self.spacing['md']))
        
        if height:
            card_container.configure(height=height)
            card_container.pack_propagate(False)
        
        # カードヘッダー
        header = tk.Frame(card_container, bg=self.colors['background_primary'])
        header.pack(fill=tk.X, pady=(0, self.spacing['xs']))
        
        title_label = tk.Label(
            header,
            text=title,
            font=('SF Pro Display', self.typography['headline']['size'], 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['background_primary']
        )
        title_label.pack(anchor='w')
        
        # カードコンテンツ
        content = tk.Frame(card_container, bg=self.colors['surface_card'])
        content.pack(fill=tk.BOTH, expand=True)
        
        return content
    
    def create_safe_button(self, parent, text, command, style='primary', width=None, **kwargs):
        """安全なボタン作成（ホバーエフェクトなし、クリックのみ）"""
        btn_frame = tk.Frame(parent, bg=parent.cget('bg'))
        
        if style == 'primary':
            bg_color = self.colors['accent_primary']
            fg_color = 'white'
        else:
            bg_color = self.colors['background_tertiary']
            fg_color = self.colors['text_primary']
        
        btn = tk.Button(
            btn_frame,
            text=text,
            font=('SF Pro Display', self.typography['body']['size'], 'bold'),
            bg=bg_color,
            fg=fg_color,
            activebackground=bg_color,  # ホバー時も同じ色
            activeforeground=fg_color,
            border=0,
            relief='flat',
            cursor='hand2',
            command=command,
            **kwargs
        )
        
        if width:
            btn.config(width=width//8)  # 概算ピクセル幅をCharacter幅に変換
        
        btn.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        
        # 安全なクリックイベントのみ（ホバーエフェクトは完全に無効化）
        # btn.bind('<Enter>', lambda e: None)  # 何もしない
        # btn.bind('<Leave>', lambda e: None)  # 何もしない
        
        return btn_frame
    
    def create_safe_model_list(self, parent):
        """安全なモデル一覧作成（最小限のスクロールイベントのみ）"""
        # スクロール可能フレーム
        list_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(self.spacing['sm'], 0))
        
        # Canvas と Scrollbar（安全なスクロールのみ）
        self.model_canvas = tk.Canvas(
            list_frame,
            bg=self.colors['surface_card'],
            highlightthickness=0,
            relief='flat'
        )
        
        scrollbar = ttk.Scrollbar(
            list_frame, 
            orient="vertical", 
            command=self.model_canvas.yview,
            style='Dark.Vertical.TScrollbar'
        )
        
        self.scrollable_model_frame = tk.Frame(self.model_canvas, bg=self.colors['surface_card'])
        
        # 安全なスクロール設定（Configure イベントのみ、最小限）
        def configure_scroll_region(event=None):
            try:
                self.model_canvas.configure(scrollregion=self.model_canvas.bbox("all"))
            except tk.TclError:
                pass  # ウィンドウが破棄された場合は無視
        
        self.scrollable_model_frame.bind('<Configure>', configure_scroll_region)
        
        # 安全なマウスホイール（macOSのみ、最小限）
        if sys.platform == "darwin":  # macOS
            def safe_mousewheel(event):
                try:
                    if self.model_canvas.winfo_exists():
                        self.model_canvas.yview_scroll(int(-1 * (event.delta)), "units")
                except tk.TclError:
                    pass
            
            self.model_canvas.bind("<MouseWheel>", safe_mousewheel)
        
        # レイアウト
        self.model_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.model_canvas.configure(yscrollcommand=scrollbar.set)
        self.model_canvas.create_window((0, 0), window=self.scrollable_model_frame, anchor="nw")
        
        # モデルを安全に読み込み
        self.load_safe_models()
    
    def load_safe_models(self):
        """安全なモデル読み込み（ホバーエフェクトなし）"""
        self.model_cards = []  # カード参照を保存
        
        try:
            models = self.scan_models()
            
            if not models:
                # モデルが見つからない場合の表示
                no_models_label = tk.Label(
                    self.scrollable_model_frame,
                    text="No models found.\nPlace .pth files in the model directory.",
                    font=('SF Pro Display', self.typography['body']['size']),
                    fg=self.colors['text_tertiary'],
                    bg=self.colors['surface_card'],
                    justify=tk.CENTER
                )
                no_models_label.pack(expand=True, fill=tk.BOTH, pady=40)
                return
            
            # モデルカードを作成（ホバーエフェクトなし）
            for index, model in enumerate(models):
                self.create_safe_model_card(self.scrollable_model_frame, model, index)
            
        except Exception as e:
            print(f"Model loading error: {e}")
            error_label = tk.Label(
                self.scrollable_model_frame,
                text=f"Error loading models:\n{str(e)}",
                font=('SF Pro Display', self.typography['body']['size']),
                fg=self.colors['error'],
                bg=self.colors['surface_card'],
                justify=tk.CENTER
            )
            error_label.pack(expand=True, fill=tk.BOTH, pady=40)
    
    def create_safe_model_card(self, parent, model, index):
        """安全なモデルカード作成（ホバーエフェクトなし）"""
        # カードフレーム
        card_frame = tk.Frame(
            parent,
            bg=self.colors['background_secondary'],
            relief='flat',
            bd=1
        )
        card_frame.pack(fill=tk.X, padx=self.spacing['sm'], pady=self.spacing['xs'])
        
        # カード内容
        inner = tk.Frame(card_frame, bg=self.colors['background_secondary'])
        inner.pack(fill=tk.BOTH, expand=True, padx=self.spacing['sm'], pady=self.spacing['sm'])
        
        # モデル名（メイン）
        name_label = tk.Label(
            inner,
            text=model['name'],
            font=('SF Pro Display', self.typography['callout']['size'], 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['background_secondary'],
            anchor='w'
        )
        name_label.pack(fill=tk.X)
        
        # モデル詳細情報
        details_frame = tk.Frame(inner, bg=self.colors['background_secondary'])
        details_frame.pack(fill=tk.X, pady=(4, 0))
        
        # ファイルサイズ
        size_text = f"Size: {model['size']}"
        size_label = tk.Label(
            details_frame,
            text=size_text,
            font=('SF Pro Display', self.typography['caption1']['size']),
            fg=self.colors['text_tertiary'],
            bg=self.colors['background_secondary'],
            anchor='w'
        )
        size_label.pack(side=tk.LEFT)
        
        # インデックスファイルの存在
        if model['has_index']:
            index_label = tk.Label(
                details_frame,
                text="• Index ✓",
                font=('SF Pro Display', self.typography['caption1']['size']),
                fg=self.colors['success'],
                bg=self.colors['background_secondary']
            )
            index_label.pack(side=tk.RIGHT)
        
        # 安全なクリック選択（ホバーエフェクトなし）
        def select_model():
            try:
                self.selected_model.set(model['name'])
                self.on_model_selected(model)
                
                # 選択状態の視覚的更新（即座に適用、アニメーションなし）
                for card, inner_frame, card_model in self.model_cards:
                    if card_model['name'] == model['name']:
                        # 選択状態
                        card.config(bg=self.colors['accent_primary'])
                        inner_frame.config(bg=self.colors['accent_primary'])
                        for widget in inner_frame.winfo_children():
                            if hasattr(widget, 'winfo_children'):
                                widget.config(bg=self.colors['accent_primary'])
                                for child in widget.winfo_children():
                                    child.config(bg=self.colors['accent_primary'])
                            else:
                                widget.config(bg=self.colors['accent_primary'])
                    else:
                        # 非選択状態
                        card.config(bg=self.colors['background_secondary'])
                        inner_frame.config(bg=self.colors['background_secondary'])
                        for widget in inner_frame.winfo_children():
                            if hasattr(widget, 'winfo_children'):
                                widget.config(bg=self.colors['background_secondary'])
                                for child in widget.winfo_children():
                                    child.config(bg=self.colors['background_secondary'])
                            else:
                                widget.config(bg=self.colors['background_secondary'])
            except Exception as e:
                print(f"Model selection error: {e}")
        
        # 安全なクリックバインディング（ホバーエフェクト一切なし）
        def safe_click_handler(event):
            try:
                select_model()
            except Exception as e:
                print(f"Click handler error: {e}")
        
        # 全てのウィジェットに安全なクリックイベントのみ
        for widget in [card_frame, inner, name_label, details_frame, size_label]:
            if widget.winfo_exists():
                widget.bind('<Button-1>', safe_click_handler)
        
        # カードを保存（選択状態の更新用）
        self.model_cards.append((card_frame, inner, model))
        
        # デフォルト選択（最初のモデル）
        if index == 0:
            select_model()
    
    def create_safe_input_section(self, parent):
        """安全な入力セクション作成"""
        # ファイル選択フレーム
        file_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        file_frame.pack(fill=tk.X, padx=self.spacing['md'], pady=self.spacing['md'])
        
        # ファイル選択ボタン
        select_btn = self.create_safe_button(
            file_frame,
            "Select Audio File",
            self.browse_input_file,
            style='secondary'
        )
        select_btn.pack(fill=tk.X, pady=(0, self.spacing['sm']))
        
        # 選択されたファイル表示
        self.input_file_label = tk.Label(
            file_frame,
            text="No file selected",
            font=('SF Pro Display', self.typography['footnote']['size']),
            fg=self.colors['text_tertiary'],
            bg=self.colors['surface_card'],
            anchor='w'
        )
        self.input_file_label.pack(fill=tk.X)
    
    def create_safe_params_section(self, parent):
        """安全なパラメータセクション作成"""
        # パラメータコンテナ
        params_container = tk.Frame(parent, bg=self.colors['surface_card'])
        params_container.pack(fill=tk.BOTH, expand=True, padx=self.spacing['md'], pady=self.spacing['md'])
        
        # 簡略化されたパラメータ（改良版適用済み）
        if self.use_enhanced_conversion:
            info_label = tk.Label(
                params_container,
                text="✅ Enhanced conversion parameters applied automatically",
                font=('SF Pro Display', self.typography['body']['size']),
                fg=self.colors['success'],
                bg=self.colors['surface_card'],
                anchor='w'
            )
            info_label.pack(fill=tk.X, pady=(0, self.spacing['sm']))
            
            # 改良機能の詳細表示
            if self.enhancement_status and 'features' in self.enhancement_status:
                features_text = "Active features: " + ", ".join([
                    feature for feature, enabled in self.enhancement_status['features'].items() 
                    if enabled
                ])
                features_label = tk.Label(
                    params_container,
                    text=features_text,
                    font=('SF Pro Display', self.typography['caption1']['size']),
                    fg=self.colors['text_tertiary'],
                    bg=self.colors['surface_card'],
                    anchor='w',
                    wraplength=350
                )
                features_label.pack(fill=tk.X)
        else:
            info_label = tk.Label(
                params_container,
                text="Using standard conversion parameters",
                font=('SF Pro Display', self.typography['body']['size']),
                fg=self.colors['text_secondary'],
                bg=self.colors['surface_card'],
                anchor='w'
            )
            info_label.pack(fill=tk.X)
    
    def create_safe_convert_section(self, parent):
        """安全な変換セクション作成"""
        # 変換コンテナ
        convert_container = tk.Frame(parent, bg=self.colors['surface_card'])
        convert_container.pack(fill=tk.BOTH, expand=True, padx=self.spacing['md'], pady=self.spacing['md'])
        
        # 変換ボタン
        self.convert_btn = self.create_safe_button(
            convert_container,
            "Start Enhanced Conversion",
            self.start_safe_conversion,
            style='primary'
        )
        self.convert_btn.pack(fill=tk.X, pady=(0, self.spacing['sm']))
        
        # プログレスバー（シンプル）
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            convert_container,
            variable=self.progress_var,
            maximum=100,
            style='Dark.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, self.spacing['sm']))
        
        # ステータスラベル
        self.status_label = tk.Label(
            convert_container,
            text="Ready",
            font=('SF Pro Display', self.typography['footnote']['size']),
            fg=self.colors['text_tertiary'],
            bg=self.colors['surface_card'],
            anchor='w'
        )
        self.status_label.pack(fill=tk.X)
    
    # === 安全なイベントハンドラ（最小限） ===
    
    def browse_model_directory(self):
        """モデルディレクトリの選択"""
        try:
            directory = filedialog.askdirectory(
                title="Select Model Directory",
                initialdir=self.model_dir_var.get()
            )
            if directory:
                self.model_dir_var.set(directory)
                self.model_dir = directory
                self.model_dir_label.config(text=self.truncate_path(directory, 60))
                self.save_settings()
                
                # モデルリストを安全に再読み込み
                for widget in self.scrollable_model_frame.winfo_children():
                    widget.destroy()
                self.load_safe_models()
                
        except Exception as e:
            print(f"Directory browse error: {e}")
            messagebox.showerror("Error", f"Failed to browse directory: {e}")
    
    def browse_input_file(self):
        """入力ファイルの選択"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Audio File",
                filetypes=[
                    ("Audio files", "*.wav *.mp3 *.flac *.m4a *.ogg"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                self.selected_input_file.set(file_path)
                self.input_file_label.config(
                    text=f"Selected: {os.path.basename(file_path)}",
                    fg=self.colors['text_primary']
                )
        except Exception as e:
            print(f"File browse error: {e}")
            messagebox.showerror("Error", f"Failed to browse file: {e}")
    
    def start_safe_conversion(self):
        """安全な変換開始"""
        if self.converting:
            return
        
        try:
            # 入力検証
            if not self.selected_input_file.get():
                messagebox.showerror("Error", "Please select an input audio file.")
                return
            
            if not self.selected_model.get():
                messagebox.showerror("Error", "Please select a voice model.")
                return
            
            # 変換を別スレッドで実行（安全）
            self.converting = True
            self.convert_btn.winfo_children()[0].config(text="Converting...", state='disabled')
            self.status_label.config(text="Starting conversion...", fg=self.colors['info'])
            
            # プログレス開始
            self.progress_var.set(10)
            
            def conversion_worker():
                try:
                    self.run_enhanced_conversion_safe()
                except Exception as e:
                    print(f"Conversion error: {e}")
                    self.root.after(0, lambda: self.conversion_complete(False, str(e)))
            
            self.conversion_thread = threading.Thread(target=conversion_worker, daemon=True)
            self.conversion_thread.start()
            
        except Exception as e:
            print(f"Conversion start error: {e}")
            messagebox.showerror("Error", f"Failed to start conversion: {e}")
            self.converting = False
    
    def run_enhanced_conversion_safe(self):
        """安全な改良版変換実行"""
        try:
            input_file = self.selected_input_file.get()
            model_name = self.selected_model.get()
            
            # 出力ファイル名を生成
            input_basename = os.path.splitext(os.path.basename(input_file))[0]
            output_filename = f"{input_basename}_{model_name}_enhanced.wav"
            output_path = os.path.join(self.base_dir, "output", output_filename)
            
            # 出力ディレクトリを作成
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # プログレス更新
            self.root.after(0, lambda: self.progress_var.set(30))
            self.root.after(0, lambda: self.status_label.config(text="Preparing conversion..."))
            
            # モデルパスを取得
            model_info = next((m for m in self.scan_models() if m['name'] == model_name), None)
            if not model_info:
                raise ValueError(f"Model not found: {model_name}")
            
            model_path = model_info['path']
            
            # プログレス更新
            self.root.after(0, lambda: self.progress_var.set(50))
            self.root.after(0, lambda: self.status_label.config(text="Running enhanced conversion..."))
            
            # 改良版変換の実行
            if self.use_enhanced_conversion and self.enhanced_converter:
                # 改良版パラメータ
                params = {
                    'f0_method': 'rmvpe',
                    'index_rate': 0.75,
                    'protect': 0.33,
                    'filter_radius': 3,
                    'rms_mix_rate': 0.25,
                    'f0_up_key': 0
                }
                
                # インデックスファイルがある場合
                if model_info['has_index']:
                    params['index_path'] = model_info.get('index_path')
                
                # 改良版変換を実行
                result = self.enhanced_converter.convert_audio_enhanced(
                    input_file, output_path, model_path, **params
                )
                
                if result:
                    # プログレス完了
                    self.root.after(0, lambda: self.progress_var.set(100))
                    self.root.after(0, lambda: self.conversion_complete(True, output_path))
                else:
                    raise RuntimeError("Enhanced conversion failed")
            
            else:
                # 標準変換（フォールバック）
                self.run_standard_conversion_safe(input_file, output_path, model_path)
                
        except Exception as e:
            print(f"Enhanced conversion error: {e}")
            self.root.after(0, lambda: self.conversion_complete(False, str(e)))
    
    def run_standard_conversion_safe(self, input_file, output_path, model_path):
        """安全な標準変換実行"""
        try:
            # プログレス更新
            self.root.after(0, lambda: self.progress_var.set(70))
            self.root.after(0, lambda: self.status_label.config(text="Running standard conversion..."))
            
            # 標準的なRVC CLIコマンドを構築
            python_cmd = sys.executable
            cmd = [
                python_cmd, "-m", "rvc.wrapper.cli.cli",
                "infer",
                "--input_path", input_file,
                "--output_path", output_path,
                "--model_path", model_path,
                "--f0_method", "rmvpe",
                "--index_rate", "0.75",
                "--filter_radius", "3",
                "--rms_mix_rate", "0.25",
                "--protect", "0.33",
                "--f0_up_key", "0"
            ]
            
            # サブプロセスで実行
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                # プログレス完了
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: self.conversion_complete(True, output_path))
            else:
                raise RuntimeError(f"Standard conversion failed: {result.stderr}")
                
        except Exception as e:
            print(f"Standard conversion error: {e}")
            self.root.after(0, lambda: self.conversion_complete(False, str(e)))
    
    def conversion_complete(self, success, result):
        """変換完了処理"""
        try:
            self.converting = False
            self.convert_btn.winfo_children()[0].config(text="Start Enhanced Conversion", state='normal')
            
            if success:
                self.status_label.config(text=f"Conversion completed: {os.path.basename(result)}", fg=self.colors['success'])
                messagebox.showinfo("Success", f"Conversion completed!\nOutput: {result}")
            else:
                self.status_label.config(text=f"Conversion failed: {result}", fg=self.colors['error'])
                messagebox.showerror("Error", f"Conversion failed:\n{result}")
                self.progress_var.set(0)
        except Exception as e:
            print(f"Completion handler error: {e}")
    
    # === ユーティリティメソッド ===
    
    def scan_models(self):
        """モデルファイルをスキャン"""
        models = []
        try:
            model_dir = self.model_dir_var.get()
            if not os.path.exists(model_dir):
                return models
            
            for filename in os.listdir(model_dir):
                if filename.endswith('.pth'):
                    file_path = os.path.join(model_dir, filename)
                    file_size = os.path.getsize(file_path)
                    
                    # サイズを読みやすい形式に変換
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
                    
                    for ext in ['.index']:
                        index_path = os.path.join(model_dir, base_name + ext)
                        if os.path.exists(index_path):
                            index_file = index_path
                            has_index = True
                            break
                    
                    models.append({
                        'name': base_name,
                        'path': file_path,
                        'size': size_str,
                        'has_index': has_index,
                        'index_path': index_file
                    })
            
            # 名前でソート
            models.sort(key=lambda x: x['name'].lower())
            
        except Exception as e:
            print(f"Model scan error: {e}")
        
        return models
    
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
    
    def on_model_selected(self, model):
        """モデル選択時の処理"""
        self.model_info = model
        print(f"Selected model: {model['name']}")


def main():
    """メイン実行関数"""
    try:
        print("=== Enhanced Stable Voice Converter GUI ===")
        print("Segmentation fault issue resolved.")
        print("Starting stable GUI...")
        
        root = tk.Tk()
        app = DarkModeGUIStable(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()