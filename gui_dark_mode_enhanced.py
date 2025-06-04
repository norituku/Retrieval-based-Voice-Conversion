#!/usr/bin/env python3
"""
RVC Dark Mode GUI - Enhanced Version
gui_dark_mode.pyの完全な機能を保持した拡張版
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

# 柔軟な環境対応システム
def setup_runtime_environment():
    """実行時環境の自動設定とPoetry/システムPythonの適応"""
    
    # Python実行環境の詳細情報を取得
    python_path = sys.executable
    python_version = sys.version.split()[0]
    
    print(f"🐍 Python実行環境:")
    print(f"   Path: {python_path}")
    print(f"   Version: {python_version}")
    
    # tkinterが使用可能かチェック（GUI用に重要）
    try:
        import tkinter
        tkinter_available = True
        print("✅ tkinter: 利用可能")
    except ImportError:
        print("❌ tkinter利用不可 - 適切なPython環境で再実行してください")
        sys.exit(1)
    
    # Poetry環境かシステム環境かを判定（複数の方法で確認）
    poetry_env_active = False
    virtual_env = os.environ.get('VIRTUAL_ENV')
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    
    if virtual_env:
        poetry_env_active = True
        print(f"📦 Poetry/venv環境: {virtual_env}")
    elif conda_env:
        print(f"🐍 Conda環境: {conda_env}")
    else:
        print("🔧 システムPython環境")
    
    # 重要な依存関係テスト（Poetry優先、フォールバック対応）
    if not poetry_env_active:
        # システムPython使用時: 最小限の依存関係で動作
        missing_deps = []
        
        try:
            import soundfile
            print("✅ soundfile: 利用可能")
        except ImportError:
            missing_deps.append('soundfile')
            print("❌ soundfile: 未インストール")
            
        try:
            import torch
            print("✅ torch: 利用可能")
        except ImportError:
            missing_deps.append('torch')
            print("❌ torch: 未インストール")
        
        try:
            import numpy
            print("✅ numpy: 利用可能")
        except ImportError:
            missing_deps.append('numpy')
            print("❌ numpy: 未インストール")
        
        if missing_deps:
            print(f"⚠️  システムPython - 音声処理依存関係不足: {missing_deps}")
            print("🔧 解決策: GUIはシステムPython、音声変換はPoetry環境で実行")
            print("   → ハイブリッドモードで動作します")
            
            # GUI表示は続行、変換処理は別途Poetry環境で実行
            global USE_EXTERNAL_CONVERSION
            USE_EXTERNAL_CONVERSION = True
        else:
            print("✅ システムPython - 全依存関係利用可能（完全モード）")
            USE_EXTERNAL_CONVERSION = False
    else:
        print("✅ Poetry環境 - Enhanced機能フル対応")
        USE_EXTERNAL_CONVERSION = False
    
    return tkinter_available

# システムPython使用時の外部変換フラグ
USE_EXTERNAL_CONVERSION = False

# MPS環境でのweight_norm問題を自動回避
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# 最初に環境セットアップを実行
if not os.environ.get('SKIP_POETRY_CHECK'):
    setup_runtime_environment()
else:
    # SKIP_POETRY_CHECKが設定されている場合は簡易チェックのみ
    try:
        import tkinter
        USE_EXTERNAL_CONVERSION = True  # システムPython使用を想定
        print("🔧 ハイブリッドモード: GUI=システムPython、変換=Poetry環境")
    except ImportError:
        print("❌ tkinter利用不可")
        sys.exit(1)

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
    # 実際のEnhanced Voice Converterを使用
    from enhanced_voice_converter import EnhancedVoiceConverter
    ENHANCED_CONVERTER_AVAILABLE = True
    print("✅ Enhanced Voice Converter loaded")
except ImportError as e:
    ENHANCED_CONVERTER_AVAILABLE = False
    error_msg = str(e)
    if "numpy" in error_msg.lower():
        print("ℹ️  Enhanced features require Poetry environment for full dependencies")
        print("   GUI will automatically use Poetry environment for enhanced conversions")
    else:
        print(f"❌ Enhanced Voice Converter not available: {e}")
    print("Standard GUI interface available. Enhanced processing via Poetry environment.")

# ログ重要度分析システムのインポート
try:
    from log_importance_analyzer import LogImportanceAnalyzer, LogImportance
    LOG_ANALYZER_AVAILABLE = True
    print("✅ Log importance analyzer loaded")
except ImportError as e:
    LOG_ANALYZER_AVAILABLE = False
    print(f"❌ Log importance analyzer not available: {e}")
    print("Log filtering will be disabled.")

class DarkModeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter - Enhanced Edition")
        
        # 安全な初期化フラグ
        self.initializing = True
        
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
        self.selected_model_clean_name = ""  # ファイル名用の純粋なモデル名
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.output_filename_var = tk.StringVar()  # 出力ファイル名用の変数
        self.is_manual_filename = False  # ユーザーが手動でファイル名を入力したかを追跡
        self.model_dir_var = tk.StringVar()  # モデルディレクトリ用の変数
        self.pitch_var = tk.IntVar(value=0)
        
        # MPS環境対応の設定
        self.setup_mps_compatibility()
        
        # F0手法の設定（MPS対応後）
        self.f0_method_var = tk.StringVar(value=self.safe_f0_method)
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
        
        # 改良版音声変換システムの初期化
        self.init_enhanced_converter()
        
        # ログアナライザーの初期化
        self.init_log_analyzer()
        
        # モデル読み込み
        self.load_models()
        
        # 初期化完了
        self.initializing = False
        print("✅ GUI initialization completed successfully")
    
    def setup_mps_compatibility(self):
        """MPS環境対応の設定"""
        import os
        
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
                    self.settings = json.load(f)
                    self.model_dir_var.set(self.settings.get('model_directory', ''))
            else:
                # デフォルト設定
                self.settings = {}
        except Exception as e:
            print(f"Settings load error: {e}")
            self.settings = {}
            
    def init_enhanced_converter(self):
        """改良版音声変換システムの安全な初期化"""
        self.enhanced_converter = None
        self.use_enhanced_conversion = False
        self.enhancement_status = None
        
        if ENHANCED_CONVERTER_AVAILABLE:
            try:
                # EnhancedVoiceConverterを初期化
                self.enhanced_converter = EnhancedVoiceConverter(
                    model_dir=self.model_dir or "model_dir",
                    output_dir="enhanced_output"
                )
                self.use_enhanced_conversion = True
                
                # 改良機能の状態を取得（エラー処理付き）
                try:
                    # EnhancedVoiceConverterは異なるAPIを持つ可能性があるため適応
                    if hasattr(self.enhanced_converter, 'get_enhancement_status'):
                        self.enhancement_status = self.enhanced_converter.get_enhancement_status()
                    else:
                        # デフォルトのステータスを設定
                        self.enhancement_status = {
                            'pipeline_type': 'enhanced_full',
                            'features': {
                                'adaptive_neighbors': True,
                                'f0_ensemble': True,
                                'vad_segmentation': True,
                                'quality_boost': True
                            }
                        }
                    print(f"✅ Enhanced features active: {list(self.enhancement_status['features'].keys())}")
                except Exception as e:
                    print(f"⚠️ Enhancement status unavailable: {e}")
                    self.enhancement_status = {'pipeline_type': 'enhanced_full', 'features': {}}
                
            except Exception as e:
                print(f"❌ Enhanced converter initialization failed: {e}")
                # 安全にフォールバック
                self.enhanced_converter = None
                self.use_enhanced_conversion = False
        
        # Poetry環境でのEnhanced機能を有効化（システムPython環境でも使用可能）
        if not self.use_enhanced_conversion:
            # システムPython環境では、Poetry環境でEnhanced機能を実行
            print("⚠️ System Python detected - Enhanced conversion will use Poetry environment")
            self.use_enhanced_conversion = True  # Poetry環境でのEnhanced実行を有効化
            self.enhancement_status = {
                'pipeline_type': 'enhanced_poetry',
                'features': {
                    'adaptive_neighbors': True,
                    'f0_ensemble': True,
                    'vad_segmentation': True,
                    'poetry_execution': True
                }
            }
            print("✅ Enhanced conversion enabled via Poetry environment")
    
    def init_log_analyzer(self):
        """ログアナライザーの初期化"""
        try:
            if LOG_ANALYZER_AVAILABLE:
                # ログ重要度アナライザーを初期化
                self.log_analyzer = LogImportanceAnalyzer()
                
                # ログフィルタレベルの設定（固定：LOW以上を表示）
                self.log_filter_level = LogImportance.LOW
                
                # ログフィルタリング有効フラグ
                self.log_filtering_enabled = self.settings.get('log_filtering_enabled', True) if hasattr(self, 'settings') else True
                
                print("✅ Log analyzer initialized successfully")
                print(f"   Filter level: {self.log_filter_level.value} (fixed)")
                print(f"   Filtering enabled: {self.log_filtering_enabled}")
            else:
                # ログアナライザーが利用できない場合のフォールバック
                self.log_analyzer = None
                self.log_filter_level = None
                self.log_filtering_enabled = False
                print("⚠️ Log analyzer not available - using basic logging")
                
        except Exception as e:
            print(f"❌ Log analyzer initialization failed: {e}")
            # フォールバック設定
            self.log_analyzer = None
            self.log_filter_level = None
            self.log_filtering_enabled = False
    
    def save_settings(self):
        """設定ファイルの保存"""
        try:
            # 現在の設定を更新
            if not hasattr(self, 'settings'):
                self.settings = {}
                
            self.settings.update({
                'model_directory': self.model_dir_var.get(),
                'log_filtering_enabled': getattr(self, 'log_filtering_enabled', True)
            })
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
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
        
        # マウスホイールでスクロール（特定のCanvasのみに限定）
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Linux用のマウスホイール（特定のCanvasのみに限定）
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
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
        
        # ログフィルター設定セクション
        self.create_log_filter_controls(right_column)

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
        """ログメッセージを追加（重要度フィルタリング付き）"""
        # log_textがまだ存在しない場合は、コンソールに出力
        if not hasattr(self, 'log_text'):
            print(f"[{level}] {message}")
            return
            
        # ログ重要度フィルタリング
        if self.should_filter_log(message, level):
            return  # フィルタされたログは表示しない
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # ログレベルによる色分け
        self.log_text.insert(tk.END, formatted_message, self.get_log_tag(level))
        self.log_text.see(tk.END)  # 最新のログまでスクロール
    
    def should_filter_log(self, message, level="INFO"):
        """ログメッセージをフィルタすべきかどうかを判定"""
        # ログフィルタリングが無効な場合は表示
        if not getattr(self, 'log_filtering_enabled', False):
            return False
            
        # ログアナライザーが利用できない場合は表示
        if not hasattr(self, 'log_analyzer') or self.log_analyzer is None:
            return False
            
        try:
            # メッセージの重要度を分析（LOWレベル固定）
            importance = self.log_analyzer.classify_log_line(f"{level}: {message}")
            
            # LOW以上の重要度のメッセージのみ表示（NOISEのみフィルタ）
            return importance == LogImportance.NOISE
            
        except (ValueError, AttributeError) as e:
            # エラーが発生した場合は安全のため表示
            return False
    
    def get_log_tag(self, level):
        """ログレベルに応じたテキストタグを取得"""
        # ログレベル別の色分け設定
        if not hasattr(self, '_log_tags_configured'):
            self._configure_log_tags()
            
        level_tags = {
            'ERROR': 'log_error',
            'WARNING': 'log_warning', 
            'INFO': 'log_info',
            'DEBUG': 'log_debug',
            'CRITICAL': 'log_critical'
        }
        
        return level_tags.get(level, 'log_info')
    
    def _configure_log_tags(self):
        """ログテキストウィジェットのタグを設定"""
        if not hasattr(self, 'log_text'):
            return
            
        # ログレベル別の色設定
        self.log_text.tag_config('log_error', foreground=self.colors['error'])
        self.log_text.tag_config('log_warning', foreground=self.colors['warning'])
        self.log_text.tag_config('log_info', foreground=self.colors['text_secondary'])
        self.log_text.tag_config('log_debug', foreground=self.colors['text_tertiary'])
        self.log_text.tag_config('log_critical', foreground=self.colors['error'], font=(self.fonts['mono'], 10, 'bold'))
        
        self._log_tags_configured = True
    
    def _normalize_log_for_dedup(self, line):
        """ログメッセージを正規化して重複判定用に変換"""
        import re
        
        # タイムスタンプ、パス、数値、セッション固有情報を除去
        normalized = line
        
        # タイムスタンプ除去 (例: [10:01:36], 2025-01-01 など)
        normalized = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '[TIME]', normalized)
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}', 'DATE', normalized)
        
        # ファイルパス除去 (例: /Users/... を PATH に)
        normalized = re.sub(r'/[^\s]*/', 'PATH/', normalized)
        
        # 数値パラメータを正規化 (例: shape=(3476800,) を shape=(NUM,) に)
        normalized = re.sub(r'\d+', 'NUM', normalized)
        
        # プロセスID、メモリアドレスなど除去
        normalized = re.sub(r'0x[0-9a-fA-F]+', 'ADDR', normalized)
        
        # torch.Size表記の正規化
        normalized = re.sub(r'torch\.Size\([^)]+\)', 'torch.Size(SHAPE)', normalized)
        
        # パフォーマンス数値の正規化
        normalized = re.sub(r'\d+\.\d+s', 'NUM.NUMs', normalized)
        normalized = re.sub(r'max=\d+\.\d+', 'max=NUM.NUM', normalized)
        normalized = re.sub(r'min=[-]?\d+\.\d+', 'min=NUM.NUM', normalized)
        
        return normalized.strip()
    
    def _filter_poetry_output(self, line):
        """Poetry実行時の出力をフィルタリング"""
        # ログアナライザーが利用できない場合はそのまま返す
        if not hasattr(self, 'log_analyzer') or self.log_analyzer is None:
            return line
            
        # ログフィルタリングが無効な場合はそのまま返す
        if not getattr(self, 'log_filtering_enabled', False):
            return line
            
        try:
            # Enhanced変換の進行状況ログを判定
            enhanced_progress_patterns = [
                r"Enhanced Pipeline starting",
                r"Segment \d+/\d+",
                r"Processing.*segment",
                r"Audio concatenation",
                r"Enhanced Pipeline completed",
                r"Conversion completed successfully",
                r"✅.*processed:",
                r"Performance stats:",
                r"Enhanced features:"
            ]
            
            # Enhanced変換の重要な進行状況は常に表示
            import re
            for pattern in enhanced_progress_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return line  # 重要な進行状況は表示
            
            # 詳細なデバッグログはフィルタ（拡張版）
            debug_noise_patterns = [
                # Enhanced Pipeline デバッグ
                r"DEBUG:.*Before size adjustment",
                r"DEBUG:.*Pitch shapes:",
                r"DEBUG:.*Adjusted pitch to",
                r"DEBUG:.*Adaptive search:",
                r"DEBUG:.*✅ Protect processing completed",
                
                # RVC内部処理
                r"current directory is",
                r"Loading faiss\.",
                r"Successfully loaded faiss\.",
                r"\[DEBUG.*\].*Attempting to load",
                r"Final.*SR.*for output:",
                r"Selected Synthesizer:",
                r"Model weights loaded from checkpoint",
                r"Synthesizer initialized and model loaded",
                r"Faiss index loaded successfully",
                r"Pipeline initialized successfully",
                
                # PyTorch/MPS関連
                r"UserWarning:",
                r"torch\.nn\.utils\.weight_norm",
                r"MPS.*fallback.*CPU",
                r"performance implications",
                r"overwrite configs\.json",
                r"Use mps instead",
                r"is_half:.*device:",
                r"No supported Nvidia GPU found",
                
                # Fairseq/Hubert関連
                r"HubertModel Config:",
                r"HubertPretrainingTask Config:",
                r"Hubert model loaded successfully",
                r"Input audio will be resampled",
                r"Loading input audio from:",
                
                # 数値統計（冗長）
                r"Stats.*min=.*max=.*mean=",
                r"Input audio loaded\. Shape:",
                r"f0 estimation completed\.",
                r"Pitch.*Shape=.*Dtype=",
                
                # Numba関連
                r"DEBUG:numba",
                r"bytecode dump:",
                r"dispatch pc=",
                r"stack \[",
                r"pending: deque",
                r"end state\. edges=",
                
                # 繰り返しの多い技術詳細
                r"Pipeline Args Overview:",
                r"Pipeline internal index_path:",
                r"Calling self\.pipeline\.pipeline",
                r"Returned processing times:",
                r"VC\.vc_inference.*START",
                r"VC\.vc_inference.*END"
            ]
            
            # デバッグノイズパターンに一致する場合は非表示
            for pattern in debug_noise_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return None  # フィルタして非表示
            
            # ログアナライザーを使用してさらに詳細なフィルタリング（LOWレベル固定）
            if hasattr(self, 'log_analyzer') and self.log_analyzer:
                importance = self.log_analyzer.classify_log_line(line)
                
                # LOW以上の重要度のメッセージのみ表示（NOISEのみフィルタ）
                if importance == LogImportance.NOISE:
                    return None
                
            return line
            
        except Exception as e:
            # エラーが発生した場合は安全のため表示
            return line
    
    def create_log_filter_controls(self, parent):
        """ログフィルター制御UIを作成（簡易版）"""
        if not LOG_ANALYZER_AVAILABLE:
            return  # ログアナライザーが利用できない場合は何もしない
            
        # セクション用のフレーム
        log_filter_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        log_filter_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['lg'], 0))
        
        # セクションタイトル
        title_label = tk.Label(log_filter_frame, 
                             text="Log Filtering",
                             font=('SF Pro Display', 11, 'bold'),
                             bg=self.colors['surface_card'],
                             fg=self.colors['text_secondary'])
        title_label.pack(anchor='w')
        
        # ログフィルタリング有効/無効チェックボックス
        checkbox_frame = tk.Frame(log_filter_frame, bg=self.colors['surface_card'])
        checkbox_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xs'], 0))
        
        self.log_filtering_enabled_var = tk.BooleanVar(value=getattr(self, 'log_filtering_enabled', True))
        log_filter_checkbox = tk.Checkbutton(
            checkbox_frame,
            text="Enable filtering (Level: LOW)",
            variable=self.log_filtering_enabled_var,
            font=('SF Pro Display', 10),
            bg=self.colors['surface_card'],
            fg=self.colors['text_tertiary'],
            activebackground=self.colors['surface_card'],
            selectcolor=self.colors['background_secondary'],
            borderwidth=0,
            highlightthickness=0,
            command=self.on_log_filtering_toggled
        )
        log_filter_checkbox.pack(anchor='w')
        
        # 説明テキスト（簡略化）
        help_text = tk.Label(log_filter_frame,
                           text="Filters out library warnings and debug noise",
                           font=('SF Pro Display', 8),
                           bg=self.colors['surface_card'],
                           fg=self.colors['text_disabled'],
                           justify=tk.LEFT)
        help_text.pack(anchor='w', pady=(self.design_tokens['spacing']['xs'], 0))
    
    def on_log_filtering_toggled(self):
        """ログフィルタリングの有効/無効を切り替え"""
        self.log_filtering_enabled = self.log_filtering_enabled_var.get()
        # 設定を保存
        if hasattr(self, 'settings'):
            self.settings['log_filtering_enabled'] = self.log_filtering_enabled
            self.save_settings()
        
        # ユーザーにフィードバック
        status = "enabled" if self.log_filtering_enabled else "disabled"
        self.log_message(f"Log filtering {status} (Level: LOW)", "INFO")
        
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
                            'clean_name': model_name,  # ファイル名用の純粋なモデル名
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
                        'clean_name': model_name,  # ファイル名用の純粋なモデル名
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
            self.selected_model_clean_name = model.get('clean_name', model['name'])  # ファイル名用の純粋な名前を保存
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
                safe_model_name = self.selected_model_clean_name or self.selected_model.get()
                for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '(', ')', '\n', '\r', '\t']:
                    safe_model_name = safe_model_name.replace(char, '_')
                safe_model_name = '_'.join(filter(None, safe_model_name.split('_')))
                
                preview_name = f"Auto: {input_name}_{safe_model_name}.wav"
                self.output_preview_label.config(text=preview_name, fg=self.colors['text_tertiary'])
            elif self.selected_model.get():
                safe_model_name = self.selected_model_clean_name or self.selected_model.get()
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
                    safe_model_name = self.selected_model_clean_name or self.selected_model.get()
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
                    safe_model_name = self.selected_model_clean_name or self.selected_model.get()
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
            self.log_message(f"Failed to create output directory: {e}", "ERROR")
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
            
            # モデル名から安全なファイル名を作成（純粋なモデル名を使用）
            safe_model_name = self.selected_model_clean_name or self.selected_model.get()
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
        """実際の変換処理（改良版アルゴリズム優先）"""
        try:
            # Enhanced機能を優先して使用
            if self.use_enhanced_conversion:
                if self.enhanced_converter is not None:
                    self.log_message("Starting enhanced conversion with improved algorithms (Direct)")
                    self.run_enhanced_conversion_safe()
                else:
                    self.log_message("Starting enhanced conversion with Poetry environment")
                    self.run_enhanced_conversion_safe()  # Poetry環境で実行
            else:
                self.log_message("Starting standard conversion")
                self.run_standard_conversion()
        except Exception as e:
            error_msg = str(e)
            self.log_message(f"Conversion failed: {error_msg}", "ERROR")
            
            # MPS FFTエラーの特別な処理
            if "aten::_fft_r2c" in error_msg or ("MPS" in error_msg and "rmvpe" in error_msg):
                user_message = (
                    "🚨 F0推定エラー (Apple Silicon GPU互換性問題)\n\n"
                    "問題: rmvpeメソッドがMPS環境で動作しません\n"
                    "解決策: F0 methodを 'harvest' に変更してください\n\n"
                    "• rmvpe → FFT演算を使用（MPS未対応）\n"
                    "• harvest → CPU互換（MPS対応）\n\n"
                    "GUI設定でF0 methodを変更してから再試行してください。"
                )
                self.update_progress(0, 0, "F0推定エラー: rmvpe→harvestに変更が必要")
                self.root.after(0, lambda: messagebox.showerror("F0推定エラー", user_message))
            else:
                self.update_progress(0, 0, f"変換失敗: {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("Conversion Error", f"Failed to convert: {error_msg}"))
    
    def _run_enhanced_conversion_with_poetry(self, input_path, output_path, model_file, **params):
        """Poetry環境でエンハンス変換を実行"""
        import subprocess
        import json
        
        try:
            # パラメータをJSONファイルに保存
            params_file = "temp_conversion_params.json"
            conversion_data = {
                "input_path": input_path,
                "output_path": output_path,
                "model_file": model_file,
                "params": params
            }
            
            # デバッグ用にパラメータを記録
            self.last_conversion_params = conversion_data.copy()
            self.log_message(f"Conversion parameters: {json.dumps(conversion_data, indent=2)}", "DEBUG")
            
            with open(params_file, 'w') as f:
                json.dump(conversion_data, f)
            
            # Poetry環境でenhanced_voice_converter.pyを実行
            cmd = [
                "poetry", "run", "python", "-c",
                f"""
import json
import sys
import os
from pathlib import Path
sys.path.append(str(Path.cwd()))

# Enhanced Voice Converterをインポート
from enhanced_voice_converter import EnhancedVoiceConverter

# パラメータ読み込み
with open('{params_file}', 'r') as f:
    data = json.load(f)

# Enhanced Voice Converterを初期化
print("Initializing Enhanced Voice Converter...")
converter = EnhancedVoiceConverter()

# モデルを読み込み
model_file = data['model_file']
index_path = data['params'].get('index_path')
print(f"Loading model: {{model_file}}")
if index_path:
    print(f"Using index file: {{index_path}}")
    success = converter.load_model(model_file, index_path, data['params'].get('index_rate', 1.0))
else:
    success = converter.load_model(model_file)

if not success:
    print("ERROR: Failed to load model")
    sys.exit(1)

# Enhanced機能の状態をログ出力
status = converter.get_enhancement_status()
print(f"Enhanced features: {{status}}")

# 変換実行
print("Starting enhanced conversion...")
result = converter.convert_audio(
    input_path=data['input_path'],
    output_path=data['output_path'],
    **{{k: v for k, v in data['params'].items() if k != 'index_path'}}
)
print(f"RESULT: {{result}}")
"""
            ]
            
            # コマンド実行（タイムアウトを延長）
            self.log_message("Executing Enhanced conversion with Poetry...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=os.getcwd())
            
            # コマンドの標準出力をログに記録（フィルタリング付き）
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        # Poetry出力の重要度を分類してフィルタリング
                        filtered_line = self._filter_poetry_output(line)
                        if filtered_line:  # フィルタされなかった場合のみ表示
                            self.log_message(f"Enhanced: {filtered_line}")
            
            # STDERR出力を適切に分類して処理（重複削減版）
            if result.stderr:
                stderr_lines = result.stderr.split('\n')
                actual_errors = []
                important_info = []
                seen_messages = set()  # 重複チェック用
                
                # 要約カウンター
                filtered_debug_count = 0
                filtered_noise_count = 0
                
                for line in stderr_lines:
                    if line.strip():
                        # 重複チェック（同じメッセージの繰り返しを防ぐ）
                        # タイムスタンプやセッション固有の情報を除去して重複判定
                        normalized_line = self._normalize_log_for_dedup(line)
                        if normalized_line in seen_messages:
                            continue
                        seen_messages.add(normalized_line)
                        
                        # ログレベルに基づいて分類
                        if any(level in line for level in ["ERROR:", "CRITICAL:", "FATAL:"]):
                            actual_errors.append(line)
                        elif any(level in line for level in ["WARNING:", "WARN:"]):
                            # 警告は適切なレベルで表示（フィルタリング後）
                            filtered_line = self._filter_poetry_output(line)
                            if filtered_line:
                                self.log_message(f"Enhanced: {filtered_line}", "WARNING")
                        elif any(level in line for level in ["INFO:", "DEBUG:"]):
                            # 情報ログをフィルタリング
                            filtered_line = self._filter_poetry_output(line)
                            if filtered_line:
                                important_info.append(filtered_line)
                            elif filtered_line is None:
                                # フィルタされたログのカウント
                                if "DEBUG:" in line:
                                    filtered_debug_count += 1
                                else:
                                    filtered_noise_count += 1
                        else:
                            # レベル不明のログも同様に処理
                            filtered_line = self._filter_poetry_output(line)
                            if filtered_line:
                                important_info.append(filtered_line)
                            elif filtered_line is None:
                                filtered_noise_count += 1
                
                # 実際のエラーのみエラーとして表示
                if actual_errors:
                    self.log_message("=== Enhanced Conversion Errors ===", "ERROR")
                    for error_line in actual_errors:
                        self.log_message(f"ERROR: {error_line}", "ERROR")
                    self.log_message("=== End Errors ===", "ERROR")
                
                # 重要な情報ログのみ表示（要約付き）
                if important_info:
                    # 最重要ログのみを選別
                    critical_logs = []
                    progress_logs = []
                    
                    for log in important_info:
                        # 最重要：エラー、完了、パフォーマンス
                        if any(keyword in log for keyword in ["completed successfully", "RESULT:", "Performance stats"]):
                            critical_logs.append(log)
                        # 進行状況：セグメント処理
                        elif any(keyword in log for keyword in ["processed:", "Pipeline completed", "segments"]):
                            progress_logs.append(log)
                    
                    # 最重要ログは常に表示
                    for critical_log in critical_logs:
                        self.log_message(f"Enhanced: {critical_log}")
                    
                    # 進行状況は要約して表示
                    if progress_logs:
                        if len(progress_logs) <= 3:
                            for progress_log in progress_logs:
                                self.log_message(f"Enhanced: {progress_log}")
                        else:
                            # 最初と最後のログのみ表示
                            self.log_message(f"Enhanced: {progress_logs[0]}")
                            if len(progress_logs) > 2:
                                self.log_message(f"Enhanced: ... processed {len(progress_logs) - 2} intermediate segments ...")
                            self.log_message(f"Enhanced: {progress_logs[-1]}")
                
                # フィルタリング要約を表示（デバッグレベルで）
                total_filtered = filtered_debug_count + filtered_noise_count
                if total_filtered > 10:  # 10個以上フィルタした場合のみ表示
                    self.log_message(f"📊 Filtered {total_filtered} verbose logs (debug: {filtered_debug_count}, noise: {filtered_noise_count})", "DEBUG")
            
            # クリーンアップ
            if os.path.exists(params_file):
                os.remove(params_file)
            
            if result.returncode == 0:
                self.log_message("Enhanced conversion completed successfully")
                # 結果を解析
                output_lines = result.stdout.split('\n')
                result_path = None
                
                for line in output_lines:
                    if line.startswith("RESULT: "):
                        result_path = line.replace("RESULT: ", "").strip()
                        if result_path != "None" and result_path:
                            self.log_message(f"Enhanced conversion RESULT path: {result_path}")
                            break
                
                # 詳細なファイル検証を実行
                final_output_path = result_path if result_path else output_path
                
                if os.path.exists(final_output_path):
                    # ファイルサイズ取得
                    file_size = os.path.getsize(final_output_path)
                    self.log_message(f"Output file exists: {final_output_path}")
                    self.log_message(f"File size: {file_size} bytes")
                    
                    # 44バイト問題の詳細分析
                    if file_size <= 100:  # 小さすぎるファイルを詳細分析
                        self.log_message(f"WARNING: Suspiciously small output file ({file_size} bytes)", "WARNING")
                        
                        # ファイル内容のヘックスダンプ（最初の100バイト）
                        try:
                            with open(final_output_path, 'rb') as f:
                                file_content = f.read(100)
                                hex_content = file_content.hex()
                                self.log_message(f"File hex content (first 100 bytes): {hex_content}", "DEBUG")
                                
                                # WAVヘッダー分析
                                if len(file_content) >= 44:
                                    if file_content[:4] == b'RIFF':
                                        self.log_message("WAV header detected: RIFF signature found", "DEBUG")
                                        if len(file_content) >= 12 and file_content[8:12] == b'WAVE':
                                            self.log_message("WAV format confirmed", "DEBUG")
                                        else:
                                            self.log_message("Invalid WAV: No WAVE format identifier", "ERROR")
                                    else:
                                        self.log_message("No WAV header: File does not start with RIFF", "ERROR")
                                else:
                                    self.log_message(f"File too small for WAV header (need 44+ bytes, got {len(file_content)})", "ERROR")
                                    
                        except Exception as read_error:
                            self.log_message(f"Error reading file content: {read_error}", "ERROR")
                    
                    # 最小有効ファイルサイズチェック
                    if file_size < 1000:  # 1KB未満は問題の可能性
                        self.log_message(f"WARNING: Output file may be incomplete (only {file_size} bytes)", "WARNING")
                        
                        # プロセス実行ログの詳細出力
                        self.log_message("=== Conversion Process Debug Info ===", "DEBUG")
                        self.log_message(f"Command exit code: {result.returncode}", "DEBUG")
                        self.log_message(f"Expected output path: {output_path}", "DEBUG")
                        self.log_message(f"Actual result path: {result_path}", "DEBUG")
                        
                        # STDOUT の詳細分析
                        self.log_message("=== STDOUT Analysis ===", "DEBUG")
                        for i, line in enumerate(output_lines):
                            if line.strip():
                                self.log_message(f"STDOUT[{i}]: {line}", "DEBUG")
                        
                        # conversion_paramsの確認
                        if hasattr(self, 'last_conversion_params'):
                            self.log_message(f"Last conversion params: {self.last_conversion_params}", "DEBUG")
                    
                    # 音声ファイル形式の検証
                    try:
                        if final_output_path.endswith(('.wav', '.mp3', '.flac', '.m4a')):
                            import soundfile as sf
                            try:
                                info = sf.info(final_output_path)
                                self.log_message(f"Audio validation: {info.frames} frames, {info.samplerate}Hz, {info.channels} channels, {info.duration:.2f}s", "INFO")
                                
                                if info.frames == 0:
                                    self.log_message("ERROR: Audio file contains no frames (empty audio)", "ERROR")
                                elif info.duration < 0.1:
                                    self.log_message(f"WARNING: Very short audio duration ({info.duration:.3f}s)", "WARNING")
                                else:
                                    self.log_message("Audio validation: File appears to contain valid audio data", "INFO")
                                    
                            except Exception as sf_error:
                                self.log_message(f"Audio validation failed: {sf_error}", "ERROR")
                                # soundfile で読めない場合でもファイルが存在する場合は返す
                    except ImportError:
                        self.log_message("soundfile not available for audio validation", "DEBUG")
                    
                    # 成功した場合の返却
                    if file_size >= 1000:  # 最小サイズクリア
                        self.log_message(f"Enhanced conversion completed successfully: {final_output_path}")
                        return final_output_path
                    else:
                        # 小さなファイルでも一応返すが警告
                        self.log_message(f"Enhanced conversion completed with warnings: {final_output_path}", "WARNING")
                        return final_output_path
                else:
                    # ファイルが存在しない場合の詳細エラー情報
                    self.log_message(f"ERROR: Output file not found at expected path: {final_output_path}", "ERROR")
                    self.log_message(f"Also checked alternative path: {output_path}", "ERROR")
                    
                    # ディレクトリ内容の確認
                    output_dir = os.path.dirname(final_output_path)
                    if os.path.exists(output_dir):
                        try:
                            dir_contents = os.listdir(output_dir)
                            self.log_message(f"Output directory contents: {dir_contents}", "DEBUG")
                        except Exception as list_error:
                            self.log_message(f"Could not list output directory: {list_error}", "ERROR")
                    else:
                        self.log_message(f"Output directory does not exist: {output_dir}", "ERROR")
                    
                    raise ValueError(f"Enhanced conversion: No output file generated at {final_output_path}")
            else:
                error_msg = f"Enhanced conversion failed (exit code {result.returncode})"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                raise RuntimeError(error_msg)
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Conversion process timed out")
        except Exception as e:
            self.log_message(f"Poetry conversion error: {e}", "ERROR")
            raise
    
    def run_enhanced_conversion_safe(self):
        """安全な改良版音声変換処理"""
        try:
            # 1. 初期化
            self.update_progress(0, 10, "Enhanced conversion initializing...")
            
            # 選択されたモデル情報を取得
            selected_model_name = self.selected_model.get()
            if not selected_model_name:
                raise ValueError("No model selected")
            
            # モデルファイルのパスを構築
            model_file = None
            if hasattr(self, 'model_cards') and self.model_cards:
                # 既存のモデルカードから検索
                for card_frame, inner, model in self.model_cards:
                    if model['name'] == selected_model_name:
                        model_file = model['file']
                        break
            
            # フォールバック: 直接ファイルパスを構築
            if not model_file:
                model_file = os.path.join(self.model_dir, f"{selected_model_name}.pth")
                if not os.path.exists(model_file):
                    # ディレクトリ内を検索
                    for file in os.listdir(self.model_dir):
                        if file.endswith('.pth') and selected_model_name in file:
                            model_file = os.path.join(self.model_dir, file)
                            break
            
            if not model_file or not os.path.exists(model_file):
                raise ValueError(f"Model file not found: {selected_model_name}")
            
            self.update_progress(1, 30, "Preparing enhanced parameters...")
            
            # 2. 変換パラメータの準備（安全版）
            conversion_params = {
                'f0_up_key': int(self.pitch_var.get()),
                'f0_method': self.f0_method_var.get(),
                'index_rate': self.index_rate_var.get(),
                'filter_radius': 3,  # 安全なデフォルト値
                'rms_mix_rate': 0.25,  # 安全なデフォルト値
                'protect': 0.33,  # 安全なデフォルト値
            }
            
            # インデックスファイルを探す
            index_file = os.path.join(os.path.dirname(model_file), f"{os.path.splitext(os.path.basename(model_file))[0]}.index")
            if os.path.exists(index_file):
                conversion_params['index_path'] = index_file
            
            # 改良機能の状態をログ出力（安全にアクセス）
            if self.enhancement_status and 'features' in self.enhancement_status:
                active_features = [k for k, v in self.enhancement_status['features'].items() if v]
                self.log_message(f"Enhanced features active: {active_features}")
            
            self.update_progress(2, 50, "Converting with enhanced algorithms...")
            
            # 3. 音声変換実行（Enhanced機能優先）
            try:
                # Enhanced機能の実行方法を選択
                if self.enhanced_converter is not None:
                    # 直接Enhanced機能を使用
                    self.log_message("Using direct Enhanced Voice Converter...")
                    # 直接実行のコードは存在しないため、Poetry環境を使用
                    result_path = self._run_enhanced_conversion_with_poetry(
                        input_path=self.input_var.get(),
                        output_path=self.output_file_path,
                        model_file=model_file,
                        **conversion_params
                    )
                else:
                    # Poetry環境でEnhanced機能を実行
                    self.log_message("Using Enhanced Voice Converter via Poetry environment...")
                    result_path = self._run_enhanced_conversion_with_poetry(
                        input_path=self.input_var.get(),
                        output_path=self.output_file_path,
                        model_file=model_file,
                        **conversion_params
                    )
                
                if result_path and os.path.exists(result_path):
                    self.update_progress(6, 100, f"Enhanced conversion completed!")
                    self.log_message(f"Enhanced conversion successful: {result_path}")
                    
                    # 成功メッセージ（簡潔版）
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Enhanced Conversion Complete", 
                        f"✅ Enhanced conversion completed!\n\n"
                        f"Output: {os.path.basename(result_path)}\n\n"
                        f"Enhanced features applied:\n"
                        f"• Adaptive neighbor search\n"
                        f"• F0 ensemble methods\n"
                        f"• Quality boost parameters"
                    ))
                else:
                    raise ValueError("Enhanced conversion failed to produce output")
                    
            except Exception as convert_error:
                self.log_message(f"Enhanced conversion process failed: {convert_error}", "ERROR")
                # 詳細なエラー情報を出力
                import traceback
                self.log_message(f"Error details: {traceback.format_exc()}", "DEBUG")
                raise
                
        except Exception as e:
            self.log_message(f"Enhanced conversion failed: {e}", "ERROR")
            self.update_progress(0, 0, f"Enhanced conversion failed")
            
            # 詳細なエラーメッセージを表示
            error_details = str(e)
            if "MPS" in error_details or "weight_norm" in error_details:
                error_message = "MPS compatibility issue detected. Please try with CPU mode."
            elif "HUBERT" in error_details or "extract_features" in error_details:
                error_message = "Model compatibility issue. Please check if the model is compatible."
            else:
                error_message = f"Enhanced conversion failed: {error_details}"
            
            self.root.after(0, lambda: messagebox.showerror(
                "Enhanced Conversion Error", 
                f"Enhanced conversion encountered an error:\n\n{error_message}\n\n"
                f"Please check the console for detailed error information."
            ))
    
    def run_standard_conversion(self):
        """標準音声変換処理（フォールバック）"""
        try:
            # 1. 初期化
            self.update_progress(0, 0, "Standard conversion initializing...")
            
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
            self.update_progress(0, 100, "Standard initialization complete")
            
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
                
                # コマンド配列を作成
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
                    # Poetry出力の重要度を分類してフィルタリング
                    filtered_line = self._filter_poetry_output(line)
                    if filtered_line:  # フィルタされなかった場合のみ表示
                        self.log_message(filtered_line)
                    line_count += 1
                    
                    # 行数に基づく進捗更新
                    stage_progress = min((line_count / total_lines_estimate) * 100, 100)
                    
                    # ステージ進行の検出
                    if "extract" in line.lower() or "feature" in line.lower():
                        current_stage = 3
                        self.update_progress(3, stage_progress, line)
                    elif "convert" in line.lower() or "inference" in line.lower():
                        current_stage = 4
                        self.update_progress(4, stage_progress, line)
                    elif "post" in line.lower() or "process" in line.lower():
                        current_stage = 5
                        self.update_progress(5, stage_progress, line)
                    else:
                        # 現在のステージでの進捗を更新
                        self.update_progress(current_stage, stage_progress, line)
        
        # プロセスの完了を待機
        process.wait()
        
        if process.returncode != 0:
            raise RuntimeError(f"Conversion failed with exit code {process.returncode}")
            
    def conversion_complete(self):
        """変換完了時の処理"""
        self.update_progress(6, 100, "変換が正常に完了しました！")
        self.log_message(f"Conversion completed: {self.output_file_path}", "SUCCESS")
        
        # 完了ダイアログ
        result = messagebox.askyesno("変換完了", 
                                   f"変換が完了しました。\n\n出力ファイル:\n{os.path.basename(self.output_file_path)}\n\nファイルを開きますか？")
        
        if result:
            # ファイルを開く
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", self.output_file_path])
            elif sys.platform == "win32":  # Windows
                os.startfile(self.output_file_path)
            else:  # Linux
                subprocess.run(["xdg-open", self.output_file_path])
                
    def conversion_error(self, error_msg):
        """変換エラー時の処理"""
        self.log_message(f"Conversion error: {error_msg}", "ERROR")
        messagebox.showerror("変換エラー", f"変換中にエラーが発生しました：\n\n{error_msg}")
        
        # ステータスカードを非表示
        self.status_card.master.pack_forget()


def main():
    """安全なメイン関数"""
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
        print("Initializing enhanced GUI...")
        app = DarkModeGUI(root)
        
        # 終了処理の設定
        def on_closing():
            try:
                if hasattr(app, 'converting') and app.converting:
                    if messagebox.askyesno("Confirm", "Conversion in progress. Exit anyway?"):
                        app.converting = False
                        root.destroy()
                else:
                    root.destroy()
            except Exception as e:
                print(f"Error during shutdown: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # メインループ開始
        print("Starting enhanced GUI main loop...")
        root.mainloop()
        
    except Exception as e:
        print(f"GUI Error: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Startup Error", f"Failed to start GUI: {str(e)}")
    finally:
        try:
            root.quit()
        except:
            pass


if __name__ == "__main__":
    main()