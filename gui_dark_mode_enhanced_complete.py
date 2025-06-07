#!/usr/bin/env python3
"""
RVC Dark Mode GUI - 完全版（100%機能保持）
gui_dark_mode_enhanced.pyの全機能を100%保持したNuitka対応版
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
import re
from enum import Enum
from typing import Dict, List, Tuple

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

# ログ重要度分析システム（統合版）
class LogImportance(Enum):
    """ログ重要度レベル"""
    CRITICAL = "CRITICAL"    # 必須表示 - エラー、変換結果
    HIGH = "HIGH"           # 重要表示 - 開始/完了、モデル情報
    MEDIUM = "MEDIUM"       # オプション表示 - 詳細パラメータ
    LOW = "LOW"            # デバッグ表示 - 内部処理詳細
    NOISE = "NOISE"        # 非表示 - ライブラリ警告、DEBUG

class IntegratedLogAnalyzer:
    """統合版ログ重要度分析クラス"""
    
    def __init__(self):
        # 重要度分類ルール
        self.importance_rules = {
            # CRITICAL: エラーと最終結果
            LogImportance.CRITICAL: [
                r"❌.*[Ee]rror",
                r"🚨.*[Ff]ailed",
                r"❌.*[Ff]ailed",
                r"✅.*[Cc]omplete",
                r"🎉.*[Ss]uccess",
                r"📁.*[Oo]utput",
                r"💾.*[Ss]aved",
                r"✅.*変換完了",
                r"❌.*変換失敗",
                r"🎵.*生成完了"
            ],
            
            # HIGH: 重要な開始/完了情報
            LogImportance.HIGH: [
                r"🎤.*[Ss]tarting",
                r"🎵.*[Ll]oading",
                r"🔄.*[Pp]rocessing",
                r"📊.*[Pp]rogress",
                r"🎯.*[Cc]onverting",
                r"✅.*[Ll]oaded",
                r"🎤.*開始",
                r"🎵.*読み込み",
                r"🔄.*処理中",
                r"📊.*進捗",
                r"🎯.*変換中"
            ],
            
            # MEDIUM: 設定とパラメータ情報
            LogImportance.MEDIUM: [
                r"⚙️.*[Ss]etting",
                r"📋.*[Pp]arameter",
                r"🎛️.*[Cc]onfig",
                r"📝.*[Ff]ile.*selected",
                r"⚙️.*設定",
                r"📋.*パラメータ",
                r"🎛️.*設定値",
                r"📝.*ファイル選択"
            ],
            
            # LOW: デバッグと詳細情報
            LogImportance.LOW: [
                r"🔧.*[Dd]ebug",
                r"💡.*[Ii]nfo",
                r"📱.*[Ii]nitializ",
                r"🔍.*[Cc]hecking",
                r"🔧.*デバッグ",
                r"💡.*情報",
                r"📱.*初期化",
                r"🔍.*確認中"
            ],
            
            # NOISE: フィルタ対象
            LogImportance.NOISE: [
                r".*FutureWarning",
                r".*DeprecationWarning", 
                r".*UserWarning",
                r".*RuntimeWarning",
                r".*torch\.jit",
                r".*ffmpeg.*deprecated",
                r".*librosa.*",
                r".*DEBUG.*",
                r".*\[DEBUG\]",
                r".*numpy.*FutureWarning"
            ]
        }
    
    def classify_log_line(self, log_line: str) -> LogImportance:
        """ログ行を分類"""
        for importance, patterns in self.importance_rules.items():
            for pattern in patterns:
                if re.search(pattern, log_line, re.IGNORECASE):
                    return importance
        
        # デフォルトはMEDIUM
        return LogImportance.MEDIUM

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

class DarkModeGUIComplete:
    """完全版Dark Mode GUI - 100%機能保持"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter - Enhanced Edition (Complete)")
        
        # 安全な初期化フラグ
        self.initializing = True
        
        # Nuitka環境情報
        self.is_nuitka = is_nuitka_build()
        print(f"🏗️ 実行環境: {'Nuitka Build' if self.is_nuitka else 'Development'}")
        
        # 統合Enhanced Voice Converter初期化
        self.integrated_converter = IntegratedEnhancedConverter()
        
        # 統合ログアナライザー初期化
        self.log_analyzer = IntegratedLogAnalyzer()
        self.log_filtering_enabled = True  # デフォルトで有効
        
        # リソースパス設定（Nuitka対応）
        self.base_dir = get_resource_path("")
        self.model_dir = get_resource_path("model_dir")
        self.config_dir = get_resource_path("configs")
        self.settings_file = get_resource_path("gui_settings.json")
        
        print(f"📁 ベースディレクトリ: {self.base_dir}")
        print(f"📁 モデルディレクトリ: {self.model_dir}")
        
        # gui_dark_mode_enhanced.pyと完全同一のデザイントークン
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
        
        # フォントファミリーの定義
        self.fonts = {
            'family': 'SF Pro Display',
            'mono': 'SF Mono'
        }
        
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
        print("✅ 完全版GUI初期化完了")
    
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
                    # ログフィルタリング設定も復元
                    self.log_filtering_enabled = self.settings.get('log_filtering_enabled', True)
            else:
                # デフォルト設定
                self.settings = {'log_filtering_enabled': True}
                print(f"⚠️ 設定ファイルが見つかりません: {self.settings_file}")
        except Exception as e:
            print(f"❌ 設定読み込みエラー: {e}")
            self.settings = {'log_filtering_enabled': True}
    
    def save_settings(self):
        """設定ファイルの保存"""
        try:
            self.settings['log_filtering_enabled'] = getattr(self, 'log_filtering_enabled', True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 設定保存エラー: {e}")
    
    def setup_variables(self):
        """GUI変数の初期化（gui_dark_mode_enhanced.pyと同じ）"""
        # 変数の初期化
        self.model_info = {}
        self.selected_model = tk.StringVar()
        self.selected_model_clean_name = ""  # ファイル名用の純粋なモデル名
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.output_filename_var = tk.StringVar()  # 出力ファイル名用の変数
        self.is_manual_filename = False  # ユーザーが手動でファイル名を入力したかを追跡
        self.model_dir_var = tk.StringVar(value=self.model_dir)  # モデルディレクトリ用の変数
        self.pitch_var = tk.IntVar(value=0)
        
        # F0手法の設定（MPS対応後）
        self.f0_method_var = tk.StringVar(value=self.safe_f0_method)
        self.index_rate_var = tk.DoubleVar(value=1.0)     # 最大インデックス使用
        self.filter_radius_var = tk.IntVar(value=3)       # 推奨値
        self.rms_mix_rate_var = tk.DoubleVar(value=0.25)  # 推奨値
        self.protect_var = tk.DoubleVar(value=0.33)       # 推奨値
        
        # ログフィルタリング設定変数
        self.log_filtering_enabled_var = tk.BooleanVar(value=self.log_filtering_enabled)
        
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
        
        # Complete Edition表示
        env_label = tk.Label(right_frame, 
                            text=f"{'🏗️ Complete App' if self.is_nuitka else '🔧 Complete Dev'}",
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
    
    def create_title_section(self, parent):
        """タイトルセクション（gui_dark_mode_enhanced.pyと同じ）"""
        title_card = self.create_card(parent, "", visible=False)
        title_card.pack(pady=(0, self.design_tokens['spacing']['lg']))
        
        # メインタイトル
        title = tk.Label(title_card, text="🎤 Voice Converter",
                        font=('SF Pro Display', self.design_tokens['typography']['title1']['size'], 'bold'),
                        bg=self.colors['surface_card'],
                        fg=self.colors['text_primary'])
        title.pack(anchor='w')
        
        # サブタイトル
        subtitle = tk.Label(title_card, text="AI音声変換システム - 高品質な音声モデル変換",
                           font=('SF Pro Display', self.design_tokens['typography']['body']['size']),
                           bg=self.colors['surface_card'],
                           fg=self.colors['text_secondary'])
        subtitle.pack(anchor='w', pady=(2, 0))
    
    def create_input_section(self, parent):
        """入力セクション（gui_dark_mode_enhanced.pyと同じ）"""
        input_card = self.create_card(parent, "Audio Input")
        
        # ファイル選択エリア
        file_frame = tk.Frame(input_card, bg=self.colors['surface_card'])
        file_frame.pack(fill=tk.X)
        
        # ファイル選択ボタン
        select_button = self.create_button(file_frame, "🔘 Choose Audio File", 
                                          self.select_input_file, 
                                          style='Primary', width=15)
        select_button.pack(side=tk.LEFT)
        
        # ファイル情報表示
        self.file_info_label = tk.Label(file_frame, text="音声ファイルが選択されていません",
                                       font=('SF Pro Display', self.design_tokens['typography']['body']['size']),
                                       bg=self.colors['surface_card'],
                                       fg=self.colors['text_tertiary'])
        self.file_info_label.pack(side=tk.LEFT, padx=(self.design_tokens['spacing']['lg'], 0))
        
        # 変換ボタン
        convert_frame = tk.Frame(input_card, bg=self.colors['surface_card'])
        convert_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['lg'], 0))
        
        self.convert_button = self.create_button(convert_frame, "🚀 Start Conversion", 
                                                self.start_conversion,
                                                style='Primary', width=20)
        self.convert_button.pack(side=tk.LEFT)
        self.convert_button.config(state='disabled')  # 初期状態は無効
    
    def create_settings_section(self, parent):
        """設定セクション（gui_dark_mode_enhanced.pyと完全同一、ログフィルター含む）"""
        settings_card = self.create_card(parent, "Settings")
        
        # 2カラムグリッドレイアウト
        grid_container = tk.Frame(settings_card, bg=self.colors['surface_card'])
        grid_container.pack(fill=tk.X)
        
        # 左カラム：出力設定
        left_column = tk.Frame(grid_container, bg=self.colors['surface_card'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, self.design_tokens['spacing']['xs']))
        
        # モデルディレクトリ設定
        model_dir_label = tk.Label(left_column, text="Model Directory",
                                 font=('SF Pro Display', 11, 'bold'),
                                 bg=self.colors['surface_card'],
                                 fg=self.colors['text_secondary'])
        model_dir_label.pack(anchor='w')
        
        # モデルディレクトリパス表示とブラウズボタン
        model_path_container = tk.Frame(left_column, bg=self.colors['surface_card'])
        model_path_container.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # モデルディレクトリパス表示
        model_dir_display_text = self.model_dir if len(self.model_dir) < 25 else "..." + self.model_dir[-22:]
        self.model_dir_display = tk.Label(model_path_container, text=model_dir_display_text,
                                         font=('SF Pro Display', 9),
                                         bg=self.colors['background_tertiary'],
                                         fg=self.colors['text_tertiary'],
                                         padx=self.design_tokens['spacing']['xs'],
                                         pady=2,
                                         justify=tk.LEFT,
                                         anchor='w')
        self.model_dir_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # モデルディレクトリブラウズボタン
        model_browse_button = self.create_button(model_path_container, "📁", 
                                               self.browse_model_directory,
                                               style='Secondary', width=3, height=1)
        model_browse_button.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['xxs'], 0))
        
        # 出力ディレクトリ設定（コンパクト）
        output_label = tk.Label(left_column, text="Output Directory",
                               font=('SF Pro Display', 11, 'bold'),
                               bg=self.colors['surface_card'],
                               fg=self.colors['text_secondary'])
        output_label.pack(anchor='w', pady=(self.design_tokens['spacing']['lg'], 0))
        
        # パス表示とブラウズボタン（横並び）
        path_container = tk.Frame(left_column, bg=self.colors['surface_card'])
        path_container.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # 出力パス表示（短縮表示）
        self.output_path_display = tk.Label(path_container, text="output/",
                                           font=('SF Pro Display', 9),
                                           bg=self.colors['background_tertiary'],
                                           fg=self.colors['text_tertiary'],
                                           padx=self.design_tokens['spacing']['xs'],
                                           pady=2,
                                           justify=tk.LEFT,
                                           anchor='w')
        self.output_path_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ブラウズボタン（小さめ）
        browse_button = self.create_button(path_container, "📁", 
                                          self.browse_output_directory,
                                          style='Secondary', width=3, height=1)
        browse_button.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['xxs'], 0))
        
        # 出力ファイル名設定
        filename_label = tk.Label(left_column, text="Output Filename",
                                font=('SF Pro Display', 11, 'bold'),
                                bg=self.colors['surface_card'],
                                fg=self.colors['text_secondary'])
        filename_label.pack(anchor='w', pady=(self.design_tokens['spacing']['lg'], 0))
        
        # ファイル名入力
        filename_container = tk.Frame(left_column, bg=self.colors['surface_card'])
        filename_container.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        self.output_filename_entry = tk.Entry(filename_container,
                                            textvariable=self.output_filename_var,
                                            font=('SF Pro Display', 9),
                                            bg=self.colors['background_tertiary'],
                                            fg=self.colors['text_primary'],
                                            insertbackground=self.colors['text_primary'],
                                            relief=tk.FLAT,
                                            bd=0,
                                            highlightthickness=1,
                                            highlightcolor=self.colors['accent_primary'],
                                            highlightbackground=self.colors['border_subtle'])
        self.output_filename_entry.pack(fill=tk.X, ipady=3)
        
        # ファイル名自動生成の説明
        filename_help = tk.Label(left_column,
                               text="Leave empty for auto-generated filename",
                               font=('SF Pro Display', 8),
                               bg=self.colors['surface_card'],
                               fg=self.colors['text_disabled'])
        filename_help.pack(anchor='w', pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # ファイル名変更監視
        self.output_filename_var.trace_add('write', self.on_filename_changed)
        
        # 右カラム：ピッチ設定とログフィルター（ここが重要！）
        right_column = tk.Frame(grid_container, bg=self.colors['surface_card'])
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # ピッチ設定（コンパクト版）
        self.create_compact_setting_control(right_column, "Pitch", self.pitch_var, 
                                          -12, 12, "semitones")
        
        # ログフィルター設定セクション（ここが復活させる重要な部分！）
        self.create_log_filter_controls(right_column)
    
    def create_compact_setting_control(self, parent, label, variable, min_val, max_val, unit=""):
        """コンパクトな設定コントロール作成（gui_dark_mode_enhanced.pyと同じ）"""
        # ラベル
        label_text = tk.Label(parent, text=f"{label} Adjustment",
                            font=('SF Pro Display', 11, 'bold'),
                            bg=self.colors['surface_card'],
                            fg=self.colors['text_secondary'])
        label_text.pack(anchor='w')
        
        # 値とスライダーを横並びに
        control_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        control_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xxs'], 0))
        
        # 現在値表示
        value_label = tk.Label(control_frame, text=f"{variable.get()} {unit}",
                             font=('SF Pro Display', 9),
                             bg=self.colors['background_tertiary'],
                             fg=self.colors['text_secondary'],
                             padx=self.design_tokens['spacing']['xs'],
                             pady=1,
                             width=8)
        value_label.pack(side=tk.LEFT)
        
        # スライダー
        if isinstance(variable, tk.DoubleVar):
            resolution = 0.01
        else:
            resolution = 1
            
        slider = tk.Scale(control_frame,
                         from_=min_val, to=max_val,
                         resolution=resolution,
                         orient=tk.HORIZONTAL,
                         variable=variable,
                         bg=self.colors['surface_card'],
                         fg=self.colors['text_secondary'],
                         highlightthickness=0,
                         troughcolor=self.colors['background_tertiary'],
                         activebackground=self.colors['accent_primary'],
                         relief=tk.FLAT,
                         length=80,  # 短めに設定
                         width=12,
                         showvalue=0)  # 値は別途表示するので非表示
        slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # 値更新コールバック
        def update_label(*args):
            value_label.config(text=f"{variable.get()} {unit}")
        
        # Python 3.13対応のtrace設定
        try:
            variable.trace_add('write', update_label)
        except AttributeError:
            # Python 3.12以前
            variable.trace('w', update_label)
    
    def create_log_filter_controls(self, parent):
        """ログフィルター制御UIを作成（gui_dark_mode_enhanced.pyと完全同一）"""
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
        """ログフィルタリングの有効/無効を切り替え（gui_dark_mode_enhanced.pyと同じ）"""
        self.log_filtering_enabled = self.log_filtering_enabled_var.get()
        # 設定を保存
        self.settings['log_filtering_enabled'] = self.log_filtering_enabled
        self.save_settings()
        
        # ユーザーにフィードバック
        status = "enabled" if self.log_filtering_enabled else "disabled"
        self.log_message(f"Log filtering {status} (Level: LOW)", "INFO")
    
    def create_status_section(self, parent):
        """ステータスセクション（gui_dark_mode_enhanced.pyと同じ）"""
        self.status_card = self.create_card(parent, "Status")
        
        # ステータス表示エリア
        status_container = tk.Frame(self.status_card, bg=self.colors['surface_card'])
        status_container.pack(fill=tk.X)
        
        # ステータスアイコンとテキスト
        status_info_frame = tk.Frame(status_container, bg=self.colors['surface_card'])
        status_info_frame.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # ステータスアイコン
        self.status_icon = tk.Label(status_info_frame, text="💡",
                                   font=('Apple Color Emoji', 16),
                                   bg=self.colors['surface_card'])
        self.status_icon.pack(side=tk.LEFT)
        
        # ステータステキスト
        self.status_label = tk.Label(status_info_frame, text="Ready to convert",
                                    font=('SF Pro Display', self.design_tokens['typography']['body']['size']),
                                    bg=self.colors['surface_card'],
                                    fg=self.colors['text_secondary'])
        self.status_label.pack(side=tk.LEFT, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # プログレスバー
        progress_frame = tk.Frame(status_container, bg=self.colors['surface_card'])
        progress_frame.pack(fill=tk.X, pady=(self.design_tokens['spacing']['xs'], 0))
        
        self.progress = ttk.Progressbar(progress_frame, style='Dark.Horizontal.TProgressbar', length=300)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # パーセンテージ表示
        self.percentage_label = tk.Label(progress_frame, text="0%",
                                        font=('SF Pro Display', self.design_tokens['typography']['caption1']['size']),
                                        bg=self.colors['surface_card'],
                                        fg=self.colors['text_tertiary'],
                                        width=4)
        self.percentage_label.pack(side=tk.RIGHT, padx=(self.design_tokens['spacing']['xs'], 0))
        
        # 現在のステージ表示
        self.current_stage_label = tk.Label(status_container, text="",
                                          font=('SF Pro Display', self.design_tokens['typography']['caption1']['size']),
                                          bg=self.colors['surface_card'],
                                          fg=self.colors['text_tertiary'])
        self.current_stage_label.pack(anchor='w', pady=(self.design_tokens['spacing']['xs'], 0))
    
    def create_log_section(self, parent):
        """ログセクション（gui_dark_mode_enhanced.pyと同じ）"""
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
        self.log_text.insert(tk.END, "Voice Converter Ready (Complete Edition).\n")
        self.log_text.config(state=tk.NORMAL)  # 編集可能にしてコピーを許可
        
        # ログタグの設定
        self._configure_log_tags()
    
    def log_message(self, message, level="INFO"):
        """ログメッセージを追加（完全版フィルタリング付き）"""
        # log_textがまだ存在しない場合は、コンソールに出力
        if not hasattr(self, 'log_text'):
            print(f"[{level}] {message}")
            return
            
        # ログ重要度フィルタリング（完全版）
        if self.should_filter_log(message, level):
            return  # フィルタされたログは表示しない
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # ログレベルによる色分け
        self.log_text.insert(tk.END, formatted_message, self.get_log_tag(level))
        self.log_text.see(tk.END)  # 最新のログまでスクロール
    
    def should_filter_log(self, message, level="INFO"):
        """ログメッセージをフィルタすべきかどうかを判定（完全版）"""
        # ログフィルタリングが無効な場合は表示
        if not getattr(self, 'log_filtering_enabled', False):
            return False
            
        try:
            # メッセージの重要度を分析（統合版ログアナライザー使用）
            importance = self.log_analyzer.classify_log_line(f"{level}: {message}")
            
            # LOW以上の重要度のメッセージのみ表示（NOISEのみフィルタ）
            return importance == LogImportance.NOISE
            
        except (ValueError, AttributeError) as e:
            # エラーが発生した場合は安全のため表示
            return False
    
    def get_log_tag(self, level):
        """ログレベルに応じたテキストタグを取得（gui_dark_mode_enhanced.pyと同じ）"""
        level_tags = {
            'ERROR': 'log_error',
            'WARNING': 'log_warning', 
            'INFO': 'log_info',
            'DEBUG': 'log_debug',
            'CRITICAL': 'log_critical'
        }
        
        return level_tags.get(level, 'log_info')
    
    def _configure_log_tags(self):
        """ログテキストウィジェットのタグを設定（gui_dark_mode_enhanced.pyと同じ）"""
        if not hasattr(self, 'log_text'):
            return
            
        # ログレベル別の色設定
        self.log_text.tag_config('log_error', foreground=self.colors['error'])
        self.log_text.tag_config('log_warning', foreground=self.colors['warning'])
        self.log_text.tag_config('log_info', foreground=self.colors['text_secondary'])
        self.log_text.tag_config('log_debug', foreground=self.colors['text_tertiary'])
        self.log_text.tag_config('log_critical', foreground=self.colors['error'], font=(self.fonts['mono'], 10, 'bold'))
    
    def create_card(self, parent, title, visible=True):
        """カードウィジェット作成（gui_dark_mode_enhanced.pyと同じ）"""
        # カードコンテナ
        card_container = tk.Frame(parent, bg=self.colors['background_primary'])
        card_container.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['lg']))
        
        if title and visible:
            # カードタイトル
            title_label = tk.Label(card_container, text=title,
                                  font=('SF Pro Display', self.design_tokens['typography']['headline']['size'], 'bold'),
                                  bg=self.colors['background_primary'],
                                  fg=self.colors['text_primary'])
            title_label.pack(anchor='w', pady=(0, self.design_tokens['spacing']['xs']))
        
        # カード本体
        card = tk.Frame(card_container, 
                       bg=self.colors['surface_card'],
                       relief=tk.FLAT,
                       bd=0)
        card.pack(fill=tk.X, padx=0)
        
        # カード内部パディング
        card_content = tk.Frame(card, bg=self.colors['surface_card'])
        card_content.pack(fill=tk.X, padx=self.design_tokens['spacing']['lg'], 
                         pady=self.design_tokens['spacing']['lg'])
        
        return card_content
    
    def create_button(self, parent, text, command, style='Primary', width=None, height=None):
        """ボタンウィジェット作成（gui_dark_mode_enhanced.pyと同じ）"""
        # スタイルに応じた色設定
        style_config = {
            'Primary': {
                'bg': self.colors['accent_primary'],
                'fg': 'white',
                'active_bg': self.colors['accent_secondary']
            },
            'Secondary': {
                'bg': self.colors['background_tertiary'],
                'fg': self.colors['text_primary'],
                'active_bg': self.colors['background_elevated']
            },
            'Success': {
                'bg': self.colors['success'],
                'fg': 'white',
                'active_bg': self.colors['success']
            },
            'Warning': {
                'bg': self.colors['warning'],
                'fg': 'black',
                'active_bg': self.colors['warning']
            },
            'Error': {
                'bg': self.colors['error'],
                'fg': 'white',
                'active_bg': self.colors['error']
            }
        }
        
        config = style_config.get(style, style_config['Primary'])
        
        button = tk.Button(parent,
                          text=text,
                          command=command,
                          font=('SF Pro Display', self.design_tokens['typography']['body']['size'], 'bold'),
                          bg=config['bg'],
                          fg=config['fg'],
                          activebackground=config['active_bg'],
                          activeforeground=config['fg'],
                          relief=tk.FLAT,
                          borderwidth=0,
                          padx=self.design_tokens['spacing']['lg'],
                          pady=self.design_tokens['spacing']['xs'],
                          cursor='hand2')
        
        if width:
            button.config(width=width)
        if height:
            button.config(height=height)
        
        # ホバーエフェクト
        def on_enter(event):
            button.config(bg=config['active_bg'])
        
        def on_leave(event):
            button.config(bg=config['bg'])
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def load_models_internal(self):
        """モデル読み込み（内部実装版）"""
        try:
            if self.integrated_converter.available:
                # Enhanced Converterを使用してモデル一覧取得
                models = self.integrated_converter.list_available_models()
                if models:
                    self.display_models(models)
                    self.log_message(f"Enhanced models loaded: {len(models)}", "INFO")
                else:
                    self.log_message("No enhanced models found", "WARNING")
                    # フォールバック: 通常のモデル検索
                    self.load_models_fallback()
            else:
                # フォールバック: 通常のモデル検索
                self.load_models_fallback()
        except Exception as e:
            self.log_message(f"Model loading error: {e}", "ERROR")
            self.load_models_fallback()
    
    def load_models_fallback(self):
        """フォールバックモデル読み込み（改善版）"""
        try:
            model_files = []
            models_found = []
            
            if os.path.exists(self.model_dir):
                # サブディレクトリも含めて検索
                for root, dirs, files in os.walk(self.model_dir):
                    for file in files:
                        if file.endswith('.pth'):
                            file_path = os.path.join(root, file)
                            model_name = file.replace('.pth', '')
                            
                            # インデックスファイルの確認
                            index_file = file.replace('.pth', '.index')
                            index_path = os.path.join(root, index_file)
                            has_index = os.path.exists(index_path)
                            
                            # ファイルサイズ取得
                            try:
                                file_size_bytes = os.path.getsize(file_path)
                                file_size = f"{file_size_bytes / (1024*1024):.1f}MB"
                            except:
                                file_size = "Unknown"
                            
                            model_info = {
                                'name': model_name,
                                'file_path': file_path,
                                'index_path': index_path if has_index else None,
                                'has_index': has_index,
                                'file_size': file_size
                            }
                            models_found.append(model_info)
                            model_files.append(file)
            
            if models_found:
                self.display_models_fallback_improved(models_found)
                self.log_message(f"Models loaded: {len(models_found)}", "INFO")
                for model in models_found:
                    index_status = "✅ Index" if model['has_index'] else "❌ No Index"
                    self.log_message(f"  {model['name']} ({model['file_size']}) - {index_status}", "INFO")
            else:
                self.log_message("No .pth models found in model directory", "WARNING")
                self.log_message(f"Searched directory: {self.model_dir}", "INFO")
        except Exception as e:
            self.log_message(f"Model loading error: {e}", "ERROR")
    
    def display_models(self, models):
        """Enhancedモデルの表示"""
        # 既存のモデルカードをクリア
        for widget in self.model_scrollable_frame.winfo_children():
            widget.destroy()
        
        for i, model in enumerate(models):
            self.create_model_card(model, i)
    
    def display_models_fallback_improved(self, models_found):
        """改善版フォールバックモデルの表示"""
        # 既存のモデルカードをクリア
        for widget in self.model_scrollable_frame.winfo_children():
            widget.destroy()
        
        for i, model_info in enumerate(models_found):
            self.create_model_card(model_info, i)
    
    def display_models_fallback(self, model_files):
        """フォールバックモデルの表示（旧版互換）"""
        # 既存のモデルカードをクリア
        for widget in self.model_scrollable_frame.winfo_children():
            widget.destroy()
        
        for i, model_file in enumerate(model_files):
            # 簡易モデル情報
            model_info = {
                'name': model_file.replace('.pth', ''),
                'file_path': os.path.join(self.model_dir, model_file),
                'has_index': False  # 簡易版では検索しない
            }
            self.create_model_card(model_info, i)
    
    def create_model_card(self, model, index):
        """モデルカード作成（gui_dark_mode_enhanced.pyと同じ）"""
        # モデルカード
        card = tk.Frame(self.model_scrollable_frame, 
                       bg=self.colors['surface_overlay'],
                       relief=tk.FLAT, bd=1,
                       highlightbackground=self.colors['border_subtle'],
                       highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['xs']))
        
        # カード内部
        card_content = tk.Frame(card, bg=self.colors['surface_overlay'])
        card_content.pack(fill=tk.X, padx=self.design_tokens['spacing']['xs'], 
                         pady=self.design_tokens['spacing']['xs'])
        
        # モデル名（トランケート）
        model_name = model.get('name', 'Unknown Model')
        if len(model_name) > 18:
            display_name = model_name[:15] + "..."
        else:
            display_name = model_name
        
        name_label = tk.Label(card_content, text=display_name,
                             font=('SF Pro Display', self.design_tokens['typography']['body_bold']['size'], 'bold'),
                             bg=self.colors['surface_overlay'],
                             fg=self.colors['text_primary'])
        name_label.pack(anchor='w')
        
        # インデックス状況とファイルサイズ
        info_frame = tk.Frame(card_content, bg=self.colors['surface_overlay'])
        info_frame.pack(fill=tk.X, pady=(2, 0))
        
        # インデックス表示
        has_index = model.get('has_index', False)
        index_icon = "✅" if has_index else "❌"
        index_text = "Index" if has_index else "No Index"
        
        index_label = tk.Label(info_frame, text=f"{index_icon} {index_text}",
                              font=('SF Pro Display', self.design_tokens['typography']['caption1']['size']),
                              bg=self.colors['surface_overlay'],
                              fg=self.colors['success'] if has_index else self.colors['text_tertiary'])
        index_label.pack(side=tk.LEFT)
        
        # ファイルサイズ
        file_size = model.get('file_size', 'Unknown')
        if file_size != 'Unknown':
            size_label = tk.Label(info_frame, text=file_size,
                                 font=('SF Pro Display', self.design_tokens['typography']['caption1']['size']),
                                 bg=self.colors['surface_overlay'],
                                 fg=self.colors['text_tertiary'])
            size_label.pack(side=tk.RIGHT)
        
        # クリックでモデル選択
        def select_model(event=None):
            # 他のカードの選択を解除
            for child in self.model_scrollable_frame.winfo_children():
                child.config(bg=self.colors['surface_overlay'])
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Frame):
                        subchild.config(bg=self.colors['surface_overlay'])
                        for subsubchild in subchild.winfo_children():
                            if isinstance(subsubchild, tk.Label):
                                subsubchild.config(bg=self.colors['surface_overlay'])
            
            # 選択されたカードをハイライト
            card.config(bg=self.colors['accent_primary'])
            card_content.config(bg=self.colors['accent_primary'])
            name_label.config(bg=self.colors['accent_primary'])
            info_frame.config(bg=self.colors['accent_primary'])
            index_label.config(bg=self.colors['accent_primary'])
            if file_size != 'Unknown':
                size_label.config(bg=self.colors['accent_primary'])
            
            # モデル情報を保存
            self.selected_model.set(model_name)
            self.selected_model_clean_name = model_name
            self.model_info[model_name] = model
            
            self.log_message(f"Model selected: {model_name}", "INFO")
            
            # ファイルが選択されていればボタンを有効化
            if self.input_var.get():
                self.convert_button.config(state='normal')
            
            # ファイル名自動生成（ユーザーが手動入力していない場合）
            if not self.is_manual_filename:
                self.generate_output_filename()
        
        # ホバーエフェクト
        def on_enter(event):
            if card['bg'] != self.colors['accent_primary']:
                card.config(bg=self.colors['hover'])
                card_content.config(bg=self.colors['hover'])
                name_label.config(bg=self.colors['hover'])
                info_frame.config(bg=self.colors['hover'])
                index_label.config(bg=self.colors['hover'])
                if file_size != 'Unknown':
                    size_label.config(bg=self.colors['hover'])
        
        def on_leave(event):
            if card['bg'] != self.colors['accent_primary']:
                card.config(bg=self.colors['surface_overlay'])
                card_content.config(bg=self.colors['surface_overlay'])
                name_label.config(bg=self.colors['surface_overlay'])
                info_frame.config(bg=self.colors['surface_overlay'])
                index_label.config(bg=self.colors['surface_overlay'])
                if file_size != 'Unknown':
                    size_label.config(bg=self.colors['surface_overlay'])
        
        # イベントバインド
        for widget in [card, card_content, name_label, info_frame, index_label]:
            widget.bind("<Button-1>", select_model)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.config(cursor='hand2')
        
        if file_size != 'Unknown':
            size_label.bind("<Button-1>", select_model)
            size_label.bind("<Enter>", on_enter)
            size_label.bind("<Leave>", on_leave)
            size_label.config(cursor='hand2')
    
    # UI イベントハンドラー
    def select_input_file(self):
        """入力ファイル選択"""
        file_types = [
            ("Audio files", "*.wav *.mp3 *.flac *.m4a *.ogg"),
            ("WAV files", "*.wav"),
            ("MP3 files", "*.mp3"),
            ("FLAC files", "*.flac"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=file_types,
            initialdir=os.path.expanduser("~/Desktop")
        )
        
        if filename:
            self.input_var.set(filename)
            # ファイル情報を表示
            file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
            file_name = os.path.basename(filename)
            self.file_info_label.config(text=f"📄 {file_name} ({file_size:.1f} MB)")
            
            # モデルが選択されていればボタンを有効化
            if self.selected_model.get():
                self.convert_button.config(state='normal')
            
            self.log_message(f"Audio file selected: {file_name}", "INFO")
            
            # ファイル名自動生成（ユーザーが手動入力していない場合）
            if not self.is_manual_filename:
                self.generate_output_filename()
    
    def browse_model_directory(self):
        """モデルディレクトリ選択"""
        directory = filedialog.askdirectory(
            title="Select Model Directory",
            initialdir=self.model_dir
        )
        
        if directory:
            self.model_dir = directory
            self.model_dir_var.set(directory)
            
            # パス表示を更新（短縮表示）
            if len(directory) > 25:
                display_path = "..." + directory[-22:]
            else:
                display_path = directory
            self.model_dir_display.config(text=display_path)
            
            # 設定保存
            self.settings['model_directory'] = directory
            self.save_settings()
            
            self.log_message(f"Model directory updated: {os.path.basename(directory)}", "INFO")
            
            # モデルリストを再読み込み
            self.load_models_internal()
    
    def browse_output_directory(self):
        """出力ディレクトリ選択"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=os.path.expanduser("~/Desktop")
        )
        
        if directory:
            self.output_var.set(directory)
            # パス表示を更新（短縮表示）
            if len(directory) > 25:
                display_path = "..." + directory[-22:]
            else:
                display_path = directory
            self.output_path_display.config(text=display_path)
            
            self.log_message(f"Output directory: {directory}", "INFO")
    
    def on_filename_changed(self, *args):
        """出力ファイル名が変更された時の処理"""
        current_filename = self.output_filename_var.get().strip()
        if current_filename:
            self.is_manual_filename = True
        else:
            self.is_manual_filename = False
            # 空の場合は自動生成
            self.generate_output_filename()
    
    def generate_output_filename(self):
        """出力ファイル名の自動生成"""
        if self.is_manual_filename:
            return  # ユーザーが手動入力している場合は生成しない
        
        input_file = self.input_var.get()
        model_name = self.selected_model_clean_name or self.selected_model.get()
        
        if input_file and model_name:
            # 入力ファイル名（拡張子なし）
            input_basename = os.path.splitext(os.path.basename(input_file))[0]
            
            # モデル名をファイル名に適した形に変換
            safe_model_name = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_model_name = safe_model_name.replace(' ', '_')
            
            # ファイル名生成: 入力ファイル名_モデル名_converted
            generated_filename = f"{input_basename}_{safe_model_name}_converted.wav"
            
            # 手動入力フラグを一時的に無効にして設定
            was_manual = self.is_manual_filename
            self.is_manual_filename = True
            self.output_filename_var.set(generated_filename)
            self.is_manual_filename = was_manual
    
    def start_conversion(self):
        """音声変換開始（内部実装版）"""
        if self.conversion_in_progress:
            self.log_message("Conversion already in progress", "WARNING")
            return
        
        if not self.input_var.get():
            messagebox.showerror("Error", "Please select an input audio file")
            return
        
        if not self.selected_model.get():
            messagebox.showerror("Error", "Please select a voice model")
            return
        
        # 変換スレッドを開始
        self.conversion_in_progress = True
        self.convert_button.config(state='disabled')
        
        conversion_thread = threading.Thread(target=self._run_conversion_internal)
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def _run_conversion_internal(self):
        """内部音声変換実行"""
        try:
            input_path = self.input_var.get()
            model_name = self.selected_model.get()
            
            # 出力パス生成
            if self.output_var.get():
                output_dir = self.output_var.get()
            else:
                output_dir = get_resource_path("output")
                os.makedirs(output_dir, exist_ok=True)
            
            # 出力ファイル名（ユーザー指定または自動生成）
            custom_filename = self.output_filename_var.get().strip()
            if custom_filename:
                # ユーザー指定ファイル名を使用
                if not custom_filename.endswith('.wav'):
                    custom_filename += '.wav'
                output_filename = custom_filename
            else:
                # フォールバック：自動生成
                input_filename = os.path.splitext(os.path.basename(input_path))[0]
                safe_model_name = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                output_filename = f"{input_filename}_{safe_model_name}_converted.wav"
            
            output_path = os.path.join(output_dir, output_filename)
            
            # 入力ファイル名（ログ用）
            input_display_name = os.path.splitext(os.path.basename(input_path))[0]
            
            self.log_message(f"Starting conversion: {input_display_name}", "INFO")
            self.log_message(f"Using model: {model_name}", "INFO")
            self.log_message(f"Output file: {output_filename}", "INFO")
            
            # パラメータ設定
            params = {
                'f0_method': self.f0_method_var.get(),
                'pitch': self.pitch_var.get(),
                'index_rate': self.index_rate_var.get(),
                'filter_radius': self.filter_radius_var.get(),
                'rms_mix_rate': self.rms_mix_rate_var.get(),
                'protect': self.protect_var.get()
            }
            
            # Enhanced Converterで変換
            if self.integrated_converter.available:
                self.update_progress(0, 0, "Starting enhanced conversion...")
                
                # モデル読み込み
                model_info = self.model_info.get(model_name, {})
                model_path = model_info.get('file_path', '')
                index_path = model_info.get('index_path', None)
                
                if model_path and os.path.exists(model_path):
                    self.update_progress(1, 50, "Loading model...")
                    load_success = self.integrated_converter.load_model(model_path, index_path)
                    
                    if load_success:
                        self.update_progress(2, 0, "Converting audio...")
                        result = self.integrated_converter.convert_audio_internal(
                            input_path, output_path, **params
                        )
                        
                        if result and os.path.exists(output_path):
                            self.update_progress(6, 100, "Conversion completed!")
                            self.log_message(f"✅ Conversion completed: {output_filename}", "INFO")
                            
                            # 成功時の処理
                            success_path = output_path
                            self.root.after(0, lambda: self._conversion_success(success_path))
                        else:
                            raise Exception("Enhanced conversion failed")
                    else:
                        raise Exception("Model loading failed")
                else:
                    raise Exception(f"Model file not found: {model_path}")
            else:
                # フォールバック変換
                self.log_message("Using fallback conversion", "WARNING")
                raise Exception("Enhanced converter not available")
                
        except Exception as e:
            error_msg = str(e)
            self.log_message(f"❌ Conversion failed: {error_msg}", "ERROR")
            self.root.after(0, lambda: self._conversion_error(error_msg))
        finally:
            self.conversion_in_progress = False
            self.root.after(0, lambda: self.convert_button.config(state='normal'))
    
    def _conversion_success(self, output_path):
        """変換成功時の処理"""
        self.status_icon.config(text="✅")
        self.status_label.config(text="Conversion completed successfully!")
        messagebox.showinfo("Success", f"Conversion completed!\nOutput: {os.path.basename(output_path)}")
        
        # ファイルを開く（macOS）
        if sys.platform == "darwin":
            try:
                import subprocess
                subprocess.run(["open", os.path.dirname(output_path)])
            except:
                pass
    
    def _conversion_error(self, error_msg):
        """変換エラー時の処理"""
        self.status_icon.config(text="❌")
        self.status_label.config(text="Conversion failed")
        self.progress['value'] = 0
        self.percentage_label.config(text="0%")
        messagebox.showerror("Error", f"Conversion failed:\n{error_msg}")
    
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

# メイン実行部分
def main():
    """メイン関数"""
    root = tk.Tk()
    app = DarkModeGUIComplete(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n✅ Voice Converter Complete Edition terminated gracefully")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()