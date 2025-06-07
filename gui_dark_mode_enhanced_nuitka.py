#!/usr/bin/env python3
"""
RVC Dark Mode GUI - Nuitka互換版
gui_dark_mode_enhanced.pyの全機能を保持しつつ、Nuitka化可能な統合版
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import threading
import math
import time
from pathlib import Path
from datetime import datetime

# Nuitka環境判定
def is_nuitka_build():
    """Nuitkaビルド環境かどうかを判定"""
    return getattr(sys, 'frozen', False)

# リソースパス解決（Nuitka対応）
def get_resource_path(relative_path):
    """リソースファイルの絶対パス取得（Nuitka対応）"""
    if is_nuitka_build():
        # Nuitkaビルド時のパス解決
        base_path = os.path.dirname(sys.executable)
        if base_path.endswith('/MacOS'):
            # macOSアプリバンドル内の場合
            base_path = os.path.join(os.path.dirname(base_path), 'Resources')
    else:
        # 開発時のパス解決
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# 統合版Enhanced Voice Converter（subprocess排除）
class IntegratedEnhancedConverter:
    """外部プロセス依存を排除した統合版Enhanced Voice Converter"""
    
    def __init__(self):
        self.available = False
        self.converter = None
        self.error_message = None
        
        try:
            # 直接インポート（Nuitkaで事前バンドル済み）
            from enhanced_voice_converter import EnhancedVoiceConverter
            self.converter = EnhancedVoiceConverter()
            self.available = True
            print("✅ Enhanced Voice Converter統合完了")
        except ImportError as e:
            self.error_message = f"Enhanced Voice Converter統合失敗: {e}"
            print(f"❌ {self.error_message}")
        except Exception as e:
            self.error_message = f"Enhanced Voice Converter初期化エラー: {e}"
            print(f"❌ {self.error_message}")
    
    def list_available_models(self):
        """モデル一覧取得（内部実装）"""
        if not self.available:
            return []
        
        try:
            return self.converter.list_available_models()
        except Exception as e:
            print(f"❌ モデル一覧取得エラー: {e}")
            return []
    
    def load_model(self, model_path, index_path=None):
        """モデル読み込み（内部実装）"""
        if not self.available:
            return False
        
        try:
            return self.converter.load_model(model_path, index_path)
        except Exception as e:
            print(f"❌ モデル読み込みエラー: {e}")
            return False
    
    def convert_audio_internal(self, input_path, output_path, **params):
        """音声変換（内部実装、subprocess排除）"""
        if not self.available:
            raise RuntimeError(f"Enhanced Voice Converter利用不可: {self.error_message}")
        
        try:
            result = self.converter.convert_audio(
                input_path=input_path,
                output_path=output_path,
                **params
            )
            return result
        except Exception as e:
            raise RuntimeError(f"音声変換エラー: {e}")

# MPS環境での互換性設定
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

class DarkModeGUINuitka:
    """Nuitka互換版Dark Mode GUI - 全機能保持"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter - Enhanced Edition (Nuitka)")
        
        # 安全な初期化フラグ
        self.initializing = True
        
        # Nuitka環境情報
        self.is_nuitka = is_nuitka_build()
        print(f"🏗️ 実行環境: {'Nuitka Build' if self.is_nuitka else 'Development'}")
        
        # 統合Enhanced Voice Converter初期化
        self.integrated_converter = IntegratedEnhancedConverter()
        
        # リソースパス設定（Nuitka対応）
        self.base_dir = get_resource_path("")
        self.model_dir = get_resource_path("model_dir")
        self.config_dir = get_resource_path("configs")
        self.settings_file = get_resource_path("gui_settings.json")
        
        print(f"📁 ベースディレクトリ: {self.base_dir}")
        print(f"📁 モデルディレクトリ: {self.model_dir}")
        
        # gui_dark_mode_enhanced.pyと同じデザイントークン
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
                'selection': '#5A9FFF',
                
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
                'max_card_width': 500,
                'content_max_width': 800,
            },
            
            # アニメーション
            'animation': {
                'duration_fast': 150,
                'duration_normal': 250,
                'duration_slow': 350,
                'easing': 'ease-out',
            },
        }
        
        # カラーエイリアス（後方互換性）
        self.colors = self.design_tokens['colors']
        
        # MPS環境対応
        self.setup_mps_compatibility()
        
        # 設定とディレクトリの初期化
        self.setup_app_directories()
        
        # GUI変数の初期化
        self.setup_variables()
        
        # UI構築（gui_dark_mode_enhanced.pyと同じ構造）
        self.setup_styles()
        self.setup_window()
        self.create_ui()
        
        # モデル読み込み（内部実装版）
        self.load_models_internal()
        
        # 初期化完了
        self.initializing = False
        print("✅ Nuitka互換GUI初期化完了")
    
    def setup_mps_compatibility(self):
        """MPS環境対応の設定（gui_dark_mode_enhanced.pyと同じ）"""
        # MPS fallback設定を有効化
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        print("🔧 MPS fallback enabled for better compatibility")
        
        # MPS環境の検出
        self.is_mps_available = False
        try:
            import torch
            if torch.backends.mps.is_available():
                self.is_mps_available = True
                print("⚠️  MPS detected - using CPU-compatible F0 methods")
        except:
            pass
        
        # F0手法の設定（基本的にrmvpeを使用）
        self.safe_f0_method = "rmvpe"  # 基本的には高品質なrmvpeを使用
        
        if self.is_mps_available:
            print(f"⚠️  MPS environment detected - rmvpe may fail due to FFT limitations")
            print(f"💡 If conversion fails, please manually change F0 method to 'harvest'")
        else:
            print(f"🎯 F0 method set to: {self.safe_f0_method} (high quality)")
    
    def setup_app_directories(self):
        """アプリケーションディレクトリの設定（Nuitka対応）"""
        # 設定ファイルの読み込み
        self.load_settings()
        
        # デフォルトのモデルディレクトリ
        if not hasattr(self, 'model_dir_var') or not self.model_dir_var.get():
            if hasattr(self, 'model_dir_var'):
                self.model_dir_var.set(self.model_dir)
        
        print(f"📁 モデルディレクトリ: {self.model_dir}")
        print(f"📁 設定ファイル: {self.settings_file}")
    
    def load_settings(self):
        """設定ファイルの読み込み"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                    if hasattr(self, 'model_dir_var'):
                        self.model_dir_var.set(self.settings.get('model_directory', self.model_dir))
            else:
                # デフォルト設定
                self.settings = {}
                print(f"⚠️ 設定ファイルが見つかりません: {self.settings_file}")
        except Exception as e:
            print(f"❌ 設定読み込みエラー: {e}")
            self.settings = {}
    
    def setup_variables(self):
        """GUI変数の初期化（gui_dark_mode_enhanced.pyと同じ）"""
        # ファイル選択
        self.input_var = tk.StringVar()
        self.output_directory_var = tk.StringVar(value="enhanced_output")
        
        # モデル選択
        self.model_dir_var = tk.StringVar(value=self.model_dir)
        self.selected_model = tk.StringVar()
        self.model_info = {}
        self.models = []
        
        # パラメータ設定
        self.pitch_var = tk.DoubleVar(value=0.0)
        self.index_var = tk.DoubleVar(value=0.7)
        self.protect_var = tk.DoubleVar(value=0.33)
        self.rms_mix_var = tk.DoubleVar(value=0.25)
        self.filter_radius_var = tk.IntVar(value=3)
        self.resample_var = tk.IntVar(value=0)
        self.f0_method_var = tk.StringVar(value=self.safe_f0_method)
        
        # UI状態
        self.conversion_in_progress = False
        self.last_update_time = time.time()
        
        # Enhanced機能設定
        self.use_enhanced_conversion = self.integrated_converter.available
        
        print(f"🎛️ Enhanced変換機能: {'有効' if self.use_enhanced_conversion else '無効'}")
    
    def setup_styles(self):
        """スタイル設定（gui_dark_mode_enhanced.pyと同じ）"""
        style = ttk.Style()
        
        # プログレスバー設定
        style.configure('Dark.Horizontal.TProgressbar',
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['background_tertiary'],
                       bordercolor=self.colors['background_tertiary'],
                       lightcolor=self.colors['accent_primary'],
                       darkcolor=self.colors['accent_primary'])
        
        # スクロールバー設定
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
    
    def setup_window(self):
        """ウィンドウの基本設定（gui_dark_mode_enhanced.pyと同じ）"""
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
        """メインUI構築（gui_dark_mode_enhanced.pyと同じ構造）"""
        # ナビゲーションバー
        self.create_navigation_bar()
        
        # メインコンテンツエリア
        self.main_content = tk.Frame(self.root, bg=self.colors['background_primary'])
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 2カラムレイアウト
        self.create_two_column_layout()
    
    def create_navigation_bar(self):
        """ナビゲーションバー（gui_dark_mode_enhanced.pyと同じ）"""
        nav_bar = tk.Frame(self.root, 
                          bg=self.colors['background_secondary'], 
                          height=self.design_tokens['layout']['toolbar_height'])
        nav_bar.pack(fill=tk.X)
        nav_bar.pack_propagate(False)
        
        # 左側：ロゴとタイトル
        left_frame = tk.Frame(nav_bar, bg=self.colors['background_secondary'])
        left_frame.pack(side=tk.LEFT, padx=self.design_tokens['spacing']['lg'])
        
        # アプリアイコン
        icon_canvas = tk.Canvas(left_frame, width=24, height=24, 
                               bg=self.colors['background_secondary'], 
                               highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, pady=(self.design_tokens['spacing']['xs'], 0))
        
        # グラデーション風アイコン
        self.draw_gradient_icon(icon_canvas)
        
        # タイトル
        title_label = tk.Label(left_frame, text="Voice Converter",
                              font=('SF Pro Display', self.design_tokens['typography']['title2']['size'], 'bold'),
                              bg=self.colors['background_secondary'],
                              fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # Enhanced表示
        if self.use_enhanced_conversion:
            enhanced_badge = tk.Label(left_frame, text="Enhanced",
                                    font=('SF Pro Display', self.design_tokens['typography']['caption1']['size'], 'bold'),
                                    bg=self.colors['accent_primary'],
                                    fg='white',
                                    padx=self.design_tokens['spacing']['xs'],
                                    pady=1)
            enhanced_badge.pack(side=tk.LEFT, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # 右側：システム情報
        right_frame = tk.Frame(nav_bar, bg=self.colors['background_secondary'])
        right_frame.pack(side=tk.RIGHT, padx=self.design_tokens['spacing']['lg'])
        
        # Nuitka環境表示
        env_label = tk.Label(right_frame, 
                            text=f"{'🏗️ Nuitka Build' if self.is_nuitka else '🔧 Development'}",
                            font=('SF Pro Display', self.design_tokens['typography']['caption1']['size']),
                            bg=self.colors['background_secondary'],
                            fg=self.colors['text_tertiary'])
        env_label.pack(side=tk.RIGHT)
    
    def draw_gradient_icon(self, canvas):
        """グラデーションアイコンを描画（gui_dark_mode_enhanced.pyと同じ）"""
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
                          font=("Arial", 12, "bold"))
    
    def create_two_column_layout(self):
        """2カラムレイアウト（gui_dark_mode_enhanced.pyと同じ）"""
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
        """モデル選択サイドバー（gui_dark_mode_enhanced.pyと同じ）"""
        # ヘッダー
        header = tk.Frame(self.left_column, bg=self.colors['surface_sidebar'])
        header.pack(fill=tk.X, padx=self.design_tokens['spacing']['sm'], 
                   pady=self.design_tokens['spacing']['sm'])
        
        # タイトル
        title = tk.Label(header, text="🎵 Voice Models",
                        font=('SF Pro Display', self.design_tokens['typography']['headline']['size'], 'bold'),
                        bg=self.colors['surface_sidebar'],
                        fg=self.colors['text_primary'])
        title.pack(anchor='w')
        
        # 説明
        desc = tk.Label(header, text="音声変換に使用するモデルを選択",
                       font=('SF Pro Display', self.design_tokens['typography']['caption1']['size']),
                       bg=self.colors['surface_sidebar'],
                       fg=self.colors['text_tertiary'])
        desc.pack(anchor='w', pady=(2, 0))
        
        # スクロール可能なモデルリスト
        self.create_scrollable_model_list()
    
    def create_scrollable_model_list(self):
        """スクロール可能なモデルリスト（gui_dark_mode_enhanced.pyと同じ）"""
        # モデルリストコンテナ
        list_container = tk.Frame(self.left_column, bg=self.colors['surface_sidebar'])
        list_container.pack(fill=tk.BOTH, expand=True, 
                          padx=self.design_tokens['spacing']['sm'])
        
        # キャンバスとスクロールバー
        self.model_canvas = tk.Canvas(list_container, 
                                     bg=self.colors['surface_sidebar'],
                                     highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", 
                                command=self.model_canvas.yview,
                                style='Dark.Vertical.TScrollbar')
        
        # スクロール可能フレーム
        self.model_scrollable_frame = tk.Frame(self.model_canvas, 
                                             bg=self.colors['surface_sidebar'])
        
        # バインド設定
        self.model_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.model_canvas.configure(scrollregion=self.model_canvas.bbox("all"))
        )
        
        self.model_canvas.create_window((0, 0), window=self.model_scrollable_frame, anchor="nw")
        self.model_canvas.configure(yscrollcommand=scrollbar.set)
        
        # パック
        self.model_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイール対応
        def on_mousewheel(event):
            self.model_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.model_canvas.bind("<MouseWheel>", on_mousewheel)
    
    def create_main_content(self):
        """メインコンテンツエリア（gui_dark_mode_enhanced.pyと同じ構造）"""
        # スクロール可能なメインエリア
        main_canvas = tk.Canvas(self.right_column, bg=self.colors['background_primary'])
        main_scrollbar = ttk.Scrollbar(self.right_column, orient="vertical", command=main_canvas.yview,
                                     style='Dark.Vertical.TScrollbar')
        scrollable_main = tk.Frame(main_canvas, bg=self.colors['background_primary'])
        
        scrollable_main.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_main, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # コンテンツコンテナ（最大幅制限付き）
        content_container = tk.Frame(scrollable_main, bg=self.colors['background_primary'])
        content_container.pack(expand=True, padx=self.design_tokens['spacing']['lg'])
        
        # コンテンツセクション（gui_dark_mode_enhanced.pyと同じ順序）
        self.create_title_section(content_container)
        self.create_input_section(content_container)
        self.create_settings_section(content_container)
        self.create_status_section(content_container)
        self.create_log_section(content_container)
        
        # マウスホイール対応
        def on_main_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind("<MouseWheel>", on_main_mousewheel)
    
    def load_models_internal(self):
        """モデル読み込み（内部実装版、subprocess排除）"""
        def load_thread():
            try:
                if self.integrated_converter.available:
                    self.log_message("🔄 モデル読み込み中...")
                    models = self.integrated_converter.list_available_models()
                    
                    if models:
                        self.models = models
                        self.log_message(f"✅ {len(models)}個のモデルを検出")
                        self.root.after(0, self.update_models_ui)
                    else:
                        self.log_message("⚠️ モデルが見つかりません")
                        self.root.after(0, self.show_no_models)
                else:
                    error_msg = self.integrated_converter.error_message or "Unknown error"
                    self.log_message(f"❌ Enhanced Voice Converter利用不可: {error_msg}")
                    self.root.after(0, lambda: self.show_error(f"Enhanced Voice Converter利用不可\n{error_msg}"))
            except Exception as e:
                self.log_message(f"❌ モデル読み込み失敗: {e}")
                self.root.after(0, lambda: self.show_error(f"モデル読み込み失敗\n{e}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def log_message(self, message, level="INFO"):
        """ログメッセージ追加（gui_dark_mode_enhanced.pyと同じ）"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # コンソール出力
        print(f"[{timestamp}] {level}: {message}")
        
        # GUI更新
        def update_log():
            if hasattr(self, 'log_text'):
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)
                
                # ログ行数制限（パフォーマンス対策）
                line_count = int(self.log_text.index('end-1c').split('.')[0])
                if line_count > 1000:
                    self.log_text.delete('1.0', '100.0')
        
        # メインスレッドで実行
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, update_log)
        else:
            update_log()
    
    def show_error(self, message):
        """エラー表示（仮実装）"""
        messagebox.showerror("エラー", message)
    
    def show_no_models(self):
        """モデル無し表示（仮実装）"""
        messagebox.showwarning("警告", "モデルが見つかりません")
    
    def update_models_ui(self):
        """モデルUI更新（gui_dark_mode_enhanced.pyと同じ構造、内部実装版）"""
        # 既存のモデルカードをクリア
        for widget in self.model_scrollable_frame.winfo_children():
            widget.destroy()
        
        # モデルが存在しない場合
        if not self.models:
            no_models_label = tk.Label(self.model_scrollable_frame,
                                      text="モデルが見つかりません\n\nmodel_dirフォルダに.pthファイルを\n配置してください",
                                      font=('SF Pro Display', self.design_tokens['typography']['body']['size']),
                                      bg=self.colors['surface_sidebar'],
                                      fg=self.colors['text_tertiary'],
                                      justify='center')
            no_models_label.pack(expand=True, pady=40)
            return
        
        # モデルカードを作成
        for i, model in enumerate(self.models):
            self.create_model_card(model, i)
        
        # ステータス更新
        self.update_status("✅ システム準備完了", "success")
        self.log_message(f"🎵 {len(self.models)}個のモデルを表示しました")
    
    def create_model_card(self, model, index):
        """モデルカード作成（gui_dark_mode_enhanced.pyと同じスタイル）"""
        # カードフレーム
        card_frame = tk.Frame(self.model_scrollable_frame, 
                            bg=self.colors['background_secondary'],
                            relief='flat',
                            bd=1,
                            cursor='hand2')
        card_frame.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xxs']), 
                       padx=self.design_tokens['spacing']['xxs'])
        
        # 内部パディング
        inner = tk.Frame(card_frame, bg=self.colors['background_secondary'])
        inner.pack(fill=tk.BOTH, expand=True, 
                  padx=self.design_tokens['spacing']['sm'], 
                  pady=self.design_tokens['spacing']['xs'])
        
        # モデル名（上部）
        name_label = tk.Label(inner, 
                             text=model.get('name', 'Unknown Model'),
                             font=('SF Pro Display', self.design_tokens['typography']['body_bold']['size'], 'bold'),
                             bg=self.colors['background_secondary'],
                             fg=self.colors['text_primary'],
                             anchor='w')
        name_label.pack(fill=tk.X)
        
        # 詳細情報（下部）
        details_frame = tk.Frame(inner, bg=self.colors['background_secondary'])
        details_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # インデックス情報
        has_index = model.get('has_index', False)
        index_text = "✓ Index" if has_index else "❌ No Index"
        index_color = self.colors['success'] if has_index else self.colors['error']
        
        index_label = tk.Label(details_frame,
                              text=index_text,
                              font=('SF Pro Display', self.design_tokens['typography']['caption1']['size']),
                              bg=self.colors['background_secondary'],
                              fg=index_color)
        index_label.pack(side=tk.LEFT)
        
        # ファイルサイズ（右端）
        if 'path' in model and os.path.exists(model['path']):
            try:
                size_mb = os.path.getsize(model['path']) / 1024**2
                size_text = f"{size_mb:.0f}MB"
            except:
                size_text = "??MB"
        else:
            size_text = "??MB"
        
        size_label = tk.Label(details_frame,
                             text=size_text,
                             font=('SF Pro Display', self.design_tokens['typography']['caption1']['size']),
                             bg=self.colors['background_secondary'],
                             fg=self.colors['text_tertiary'])
        size_label.pack(side=tk.RIGHT)
        
        # クリック選択機能
        def select_model():
            self.selected_model.set(model.get('name', ''))
            self.model_info = model
            self.update_model_selection(card_frame)
            self.log_message(f"📋 モデル選択: {model.get('name', 'Unknown')}")
        
        # 全体をクリック可能に
        clickable_widgets = [card_frame, inner, name_label, details_frame, index_label, size_label]
        for widget in clickable_widgets:
            widget.bind('<Button-1>', lambda e: select_model())
            widget.config(cursor='hand2')
        
        # ホバーエフェクト
        def on_enter(e):
            if not hasattr(self, 'selected_card') or self.selected_card != card_frame:
                card_frame.config(bg=self.colors['background_tertiary'])
                inner.config(bg=self.colors['background_tertiary'])
                name_label.config(bg=self.colors['background_tertiary'])
                details_frame.config(bg=self.colors['background_tertiary'])
                index_label.config(bg=self.colors['background_tertiary'])
                size_label.config(bg=self.colors['background_tertiary'])
        
        def on_leave(e):
            if not hasattr(self, 'selected_card') or self.selected_card != card_frame:
                card_frame.config(bg=self.colors['background_secondary'])
                inner.config(bg=self.colors['background_secondary'])
                name_label.config(bg=self.colors['background_secondary'])
                details_frame.config(bg=self.colors['background_secondary'])
                index_label.config(bg=self.colors['background_secondary'])
                size_label.config(bg=self.colors['background_secondary'])
        
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
        
        # デフォルト選択（最初のモデル）
        if index == 0:
            select_model()
        
        return card_frame
    
    def update_model_selection(self, selected_card):
        """モデル選択状態の視覚的更新（gui_dark_mode_enhanced.pyと同じ）"""
        # 前の選択をクリア
        if hasattr(self, 'selected_card') and self.selected_card:
            self.selected_card.config(bg=self.colors['background_secondary'])
            # 子ウィジェットも更新
            for child in self.selected_card.winfo_children():
                self.reset_widget_bg(child, self.colors['background_secondary'])
        
        # 新しい選択を強調表示
        if selected_card:
            selected_card.config(bg=self.colors['accent_primary'])
            # 子ウィジェットも更新
            for child in selected_card.winfo_children():
                self.reset_widget_bg(child, self.colors['accent_primary'])
            self.selected_card = selected_card
    
    def reset_widget_bg(self, widget, bg_color):
        """ウィジェットの背景色を再帰的に設定"""
        try:
            widget.config(bg=bg_color)
        except:
            pass
        
        # 子ウィジェットも再帰的に処理
        for child in widget.winfo_children():
            self.reset_widget_bg(child, bg_color)
    
    def browse_input(self):
        """入力ファイル選択（gui_dark_mode_enhanced.pyと同じ）"""
        filename = filedialog.askopenfilename(
            title="音声ファイルを選択",
            filetypes=[
                ("音声ファイル", "*.wav *.mp3 *.m4a *.flac *.ogg *.aac"),
                ("WAVファイル", "*.wav"),
                ("MP3ファイル", "*.mp3"),
                ("全てのファイル", "*.*")
            ]
        )
        
        if filename:
            self.input_var.set(filename)
            self.update_file_info(filename)
            self.log_message(f"📁 入力ファイル選択: {os.path.basename(filename)}")
    
    def update_file_info(self, filename):
        """選択されたファイル情報の表示更新"""
        # 既存の情報をクリア
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
        
        if not filename:
            return
        
        try:
            # ファイル情報取得
            file_path = Path(filename)
            file_size = file_path.stat().st_size / 1024**2  # MB
            file_name = file_path.name
            
            # ファイル名表示（省略）
            if len(file_name) > 30:
                display_name = file_name[:27] + "..."
            else:
                display_name = file_name
            
            name_label = tk.Label(self.file_info_frame,
                                 text=f"📄 {display_name}",
                                 font=('SF Pro Display', 10),
                                 bg=self.colors['surface_card'],
                                 fg=self.colors['text_primary'],
                                 anchor='w')
            name_label.pack(fill=tk.X)
            
            # ファイルサイズと形式
            file_ext = file_path.suffix.upper().replace('.', '')
            size_text = f"{file_ext} • {file_size:.1f}MB"
            
            size_label = tk.Label(self.file_info_frame,
                                 text=size_text,
                                 font=('SF Pro Display', 9),
                                 bg=self.colors['surface_card'],
                                 fg=self.colors['text_tertiary'],
                                 anchor='w')
            size_label.pack(fill=tk.X)
            
        except Exception as e:
            error_label = tk.Label(self.file_info_frame,
                                  text=f"❌ ファイル情報取得エラー: {e}",
                                  font=('SF Pro Display', 9),
                                  bg=self.colors['surface_card'],
                                  fg=self.colors['error'],
                                  anchor='w')
            error_label.pack(fill=tk.X)
    
    def browse_output(self):
        """出力ディレクトリ選択（gui_dark_mode_enhanced.pyと同じ）"""
        dirname = filedialog.askdirectory(
            title="出力ディレクトリを選択",
            initialdir=os.path.expanduser("~/Desktop")
        )
        
        if dirname:
            self.output_directory_var.set(dirname)
            # パス表示を更新
            self.output_path_label.config(text=self.truncate_path(dirname, 35))
            self.log_message(f"📁 出力ディレクトリ選択: {os.path.basename(dirname)}")
    
    def start_conversion(self):
        """音声変換開始（内部実装版、subprocess排除）"""
        if self.conversion_in_progress:
            self.show_error("変換が既に実行中です")
            return
        
        # 入力検証
        if not self.input_var.get():
            self.show_error("入力ファイルを選択してください")
            return
        
        if not os.path.exists(self.input_var.get()):
            self.show_error("入力ファイルが見つかりません")
            return
        
        if not self.selected_model.get():
            self.show_error("音声モデルを選択してください")
            return
        
        if not self.integrated_converter.available:
            self.show_error(f"Enhanced Voice Converter利用不可\n{self.integrated_converter.error_message}")
            return
        
        # 変換開始
        self.conversion_in_progress = True
        self.convert_button.config(state='disabled', text="変換中...")
        self.progress_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['sm'], 0))
        self.progress_bar.start()
        self.progress_text.config(text="音声変換を実行中...")
        
        self.log_message("🎤 音声変換を開始します")
        
        def conversion_thread():
            try:
                # 出力ファイルパス生成
                input_path = Path(self.input_var.get())
                output_dir = Path(self.output_directory_var.get())
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # clean_name取得
                model_name = self.model_info.get('name', 'unknown')
                clean_name = self.model_info.get('clean_name', model_name)
                
                output_filename = f"{input_path.stem}_converted_{clean_name}.wav"
                output_path = output_dir / output_filename
                
                self.log_message(f"📝 変換パラメータ:")
                self.log_message(f"   入力: {input_path.name}")
                self.log_message(f"   出力: {output_filename}")
                self.log_message(f"   モデル: {model_name}")
                self.log_message(f"   ピッチ: {self.pitch_var.get()}")
                self.log_message(f"   インデックス: {self.index_var.get()}")
                self.log_message(f"   保護: {self.protect_var.get()}")
                
                # モデルロード（必要に応じて）
                if not self.integrated_converter.load_model(
                    self.model_info.get('path'),
                    self.model_info.get('index_path')
                ):
                    raise RuntimeError("モデルの読み込みに失敗しました")
                
                self.log_message("🔄 音声変換実行中...")
                
                # 音声変換実行（内部実装）
                result = self.integrated_converter.convert_audio_internal(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    f0_up_key=int(self.pitch_var.get()),
                    index_rate=self.index_var.get(),
                    protect=self.protect_var.get(),
                    f0_method=self.f0_method_var.get(),
                    filter_radius=self.filter_radius_var.get(),
                    rms_mix_rate=self.rms_mix_var.get(),
                    resample_sr=self.resample_var.get()
                )
                
                # 結果確認
                if output_path.exists():
                    size_mb = output_path.stat().st_size / 1024**2
                    self.log_message(f"✅ 変換完了! ({size_mb:.1f}MB)")
                    self.log_message(f"📁 出力: {output_path}")
                    
                    # 成功メッセージ
                    self.root.after(0, lambda: messagebox.showinfo(
                        "変換完了",
                        f"音声変換が完了しました!\n\n"
                        f"出力ファイル: {output_filename}\n"
                        f"サイズ: {size_mb:.1f}MB"
                    ))
                else:
                    raise RuntimeError("出力ファイルが生成されませんでした")
                
            except Exception as e:
                error_msg = str(e)
                self.log_message(f"❌ 変換エラー: {error_msg}")
                self.root.after(0, lambda: self.show_error(f"音声変換に失敗しました\n\n{error_msg}"))
            
            finally:
                # UI復元
                self.conversion_in_progress = False
                self.root.after(0, lambda: self.convert_button.config(state='normal', text="Start\nConversion"))
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self.progress_frame.pack_forget())
                self.root.after(0, lambda: self.progress_text.config(text=""))
        
        # バックグラウンドで実行
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def update_status(self, message, status_type="info"):
        """ステータス更新（gui_dark_mode_enhanced.pyと同じ）"""
        # アイコンと色の設定
        if status_type == "success":
            icon = "✅"
            color = self.colors['success']
        elif status_type == "error":
            icon = "❌"
            color = self.colors['error']
        elif status_type == "warning":
            icon = "⚠️"
            color = self.colors['warning']
        else:  # info
            icon = "ℹ️"
            color = self.colors['info']
        
        self.status_icon.config(text=icon)
        self.status_text.config(text=message, fg=color)
    
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
        self.convert_button = self.create_button(right_section, 
                                       "Start\nConversion", 
                                       self.start_conversion,
                                       style='Primary',
                                       width=120,
                                       height=50)
        self.convert_button.pack()
    
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
        self.output_directory_var.set(default_output)
        
        self.output_path_label = tk.Label(self.output_path_frame, 
                                         text=self.truncate_path(self.output_directory_var.get(), 35),
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
        
        # 右カラム：音声パラメータ
        right_column = tk.Frame(grid_container, bg=self.colors['surface_card'])
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # ピッチ調整（コンパクト）
        self.create_compact_setting_control(right_column, "Pitch", self.pitch_var, -12, 12, "")
        
        # インデックス比率（コンパクト）
        self.create_compact_setting_control(right_column, "Index", self.index_var, 0.0, 1.0, "")
        
        # 音質保護（コンパクト）
        self.create_compact_setting_control(right_column, "Protect", self.protect_var, 0.0, 0.5, "")
    
    def create_compact_setting_control(self, parent, label, variable, min_val, max_val, unit=""):
        """コンパクト設定コントロール（gui_dark_mode_enhanced.pyと同じ）"""
        container = tk.Frame(parent, bg=self.colors['surface_card'])
        container.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xxs']))
        
        # ラベルと値を同じ行に
        header = tk.Frame(container, bg=self.colors['surface_card'])
        header.pack(fill=tk.X)
        
        # ラベル（左）
        label_widget = tk.Label(header, text=label,
                               font=('SF Pro Display', 10, 'bold'),
                               bg=self.colors['surface_card'],
                               fg=self.colors['text_secondary'])
        label_widget.pack(side=tk.LEFT)
        
        # 値表示（右）
        value_label = tk.Label(header, text=f"{variable.get():.2f}{unit}",
                              font=('SF Pro Mono', 10),
                              bg=self.colors['surface_card'],
                              fg=self.colors['text_primary'])
        value_label.pack(side=tk.RIGHT)
        
        # スライダー（コンパクト）
        slider = tk.Scale(container,
                         from_=min_val, to=max_val,
                         orient=tk.HORIZONTAL,
                         variable=variable,
                         resolution=0.01 if isinstance(min_val, float) else 1,
                         showvalue=False,
                         bg=self.colors['surface_card'],
                         fg=self.colors['text_primary'],
                         activebackground=self.colors['accent_primary'],
                         highlightthickness=0,
                         relief='flat',
                         length=150,
                         sliderlength=15)
        slider.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # 値更新コールバック
        def update_value(*args):
            value_label.config(text=f"{variable.get():.2f}{unit}")
        
        # Python 3.13対応のtrace
        try:
            variable.trace_add('write', update_value)
        except AttributeError:
            # 古いPythonバージョン対応
            variable.trace('w', update_value)
        
        return container
    
    def create_status_section(self, parent):
        """ステータスセクション（gui_dark_mode_enhanced.pyと同じ）"""
        # ステータスカード
        status_card = self.create_card(parent, "Status")
        
        # ステータス表示エリア
        status_container = tk.Frame(status_card, bg=self.colors['surface_card'])
        status_container.pack(fill=tk.X)
        
        # メインステータス
        self.status_frame = tk.Frame(status_container, bg=self.colors['surface_card'])
        self.status_frame.pack(fill=tk.X)
        
        self.status_icon = tk.Label(self.status_frame, text="🔄",
                                   font=('SF Pro Display', 16),
                                   bg=self.colors['surface_card'],
                                   fg=self.colors['text_primary'])
        self.status_icon.pack(side=tk.LEFT, padx=(0, self.design_tokens['spacing']['xs']))
        
        self.status_text = tk.Label(self.status_frame, text="システム初期化中...",
                                   font=('SF Pro Display', 13),
                                   bg=self.colors['surface_card'],
                                   fg=self.colors['text_primary'])
        self.status_text.pack(side=tk.LEFT)
        
        # プログレスバー（隠し状態で開始）
        self.progress_frame = tk.Frame(status_container, bg=self.colors['surface_card'])
        
        self.progress_bar = ttk.Progressbar(self.progress_frame,
                                          mode='indeterminate',
                                          length=400,
                                          style='Dark.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=(self.design_tokens['spacing']['sm'], 0))
        
        # 進捗テキスト
        self.progress_text = tk.Label(self.progress_frame, text="",
                                     font=('SF Pro Display', 10),
                                     bg=self.colors['surface_card'],
                                     fg=self.colors['text_tertiary'])
        self.progress_text.pack(pady=(self.design_tokens['spacing']['xxs'], 0))
    
    def create_log_section(self, parent):
        """ログセクション（gui_dark_mode_enhanced.pyと同じ）"""
        # ログカード
        self.create_card(parent, "Conversion Log")
        log_card = self.create_card(parent, "Conversion Log")
        
        # ログ表示エリア
        log_container = tk.Frame(log_card, bg=self.colors['surface_card'])
        log_container.pack(fill=tk.BOTH, expand=True)
        
        # ログテキストエリア
        self.log_text = tk.Text(log_container,
                               bg=self.colors['background_secondary'],
                               fg=self.colors['text_primary'],
                               font=('SF Pro Mono', 9),
                               wrap=tk.WORD,
                               height=8,
                               relief='flat',
                               borderwidth=0,
                               selectbackground=self.colors['selection'],
                               insertbackground=self.colors['text_primary'])
        
        # ログスクロールバー
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview,
                                    style='Dark.Vertical.TScrollbar')
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # パック
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ログ初期メッセージ
        self.log_message("🎤 Voice Converter - Nuitka Edition 起動")
        self.log_message(f"🏗️ 実行環境: {'Nuitka Build' if self.is_nuitka else 'Development'}")
        self.log_message(f"💻 プラットフォーム: {sys.platform}")
    
    # ヘルパーメソッド
    def create_card(self, parent, title, visible=True):
        """カードウィジェットの作成（gui_dark_mode_enhanced.pyと同じ）"""
        # カードコンテナ
        card_container = tk.Frame(parent, bg=self.colors['background_primary'])
        if visible:
            card_container.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['sm']))
        
        # カードヘッダー
        header = tk.Frame(card_container, bg=self.colors['background_primary'])
        header.pack(fill=tk.X, padx=self.design_tokens['spacing']['sm'])
        
        header_label = tk.Label(header, text=title,
                               font=('SF Pro Display', self.design_tokens['typography']['callout']['size'], 'bold'),
                               bg=self.colors['background_primary'],
                               fg=self.colors['text_secondary'])
        header_label.pack(side=tk.LEFT, pady=(self.design_tokens['spacing']['xs'], self.design_tokens['spacing']['xxs']))
        
        # カードボディ
        card = tk.Frame(card_container, bg=self.colors['surface_card'],
                       relief='flat', bd=0)
        card.pack(fill=tk.X, padx=self.design_tokens['spacing']['sm'])
        
        # 内部パディング
        padded_card = tk.Frame(card, bg=self.colors['surface_card'])
        padded_card.pack(fill=tk.BOTH, expand=True, 
                        padx=self.design_tokens['spacing']['md'], 
                        pady=self.design_tokens['spacing']['md'])
        
        return padded_card
    
    def create_button(self, parent, text, command, style='Primary', width=None, height=None):
        """ボタン作成（gui_dark_mode_enhanced.pyと同じ）"""
        if style == 'Primary':
            bg_color = self.colors['accent_primary']
            fg_color = 'white'
            hover_color = '#4A8FEF'
        else:  # Secondary
            bg_color = self.colors['background_tertiary']
            fg_color = self.colors['text_primary']
            hover_color = self.colors['background_elevated']
        
        button = tk.Button(parent,
                          text=text,
                          command=command,
                          bg=bg_color,
                          fg=fg_color,
                          font=('SF Pro Display', 11, 'bold'),
                          relief='flat',
                          borderwidth=0,
                          padx=12,
                          pady=6,
                          cursor='hand2')
        
        if width:
            button.config(width=width)
        if height:
            button.config(height=height)
        
        # ホバーエフェクト
        def on_enter(e):
            button.config(bg=hover_color)
        def on_leave(e):
            button.config(bg=bg_color)
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        return button
    
    def truncate_path(self, path, max_length):
        """パス文字列の省略表示（gui_dark_mode_enhanced.pyと同じ）"""
        if len(path) <= max_length:
            return path
        
        # パスの最初と最後を残して中間を省略
        if '/' in path:
            parts = path.split('/')
            if len(parts) > 2:
                return f"{parts[0]}/.../{parts[-1]}"
        
        return f"{path[:max_length-3]}..."

def main():
    """メイン実行関数"""
    root = tk.Tk()
    app = DarkModeGUINuitka(root)
    root.mainloop()

if __name__ == "__main__":
    main()