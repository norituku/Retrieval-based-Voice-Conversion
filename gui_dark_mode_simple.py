#!/usr/bin/env python3
"""
gui_dark_mode.py - simplified structure for PyTorch initialization
"""
import os
import sys
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import subprocess
import threading
import math
import time
from pathlib import Path
from datetime import datetime

# PyInstaller環境でPyTorch環境セットアップ
if hasattr(sys, '_MEIPASS'):
    # pytorch_env_helperをインポート（存在する場合）
    try:
        from pytorch_env_helper import setup_pytorch_environment, import_torch_with_fix
        setup_pytorch_environment()
        print("✅ PyTorch環境セットアップ完了")
    except ImportError:
        print("⚠️ pytorch_env_helper not found, using fallback")
        pass

# RVC設定をインポート（存在する場合）
try:
    from rvc_config import POETRY_PYTHON_PATH, RVC_MODULE, get_poetry_python, get_rvc_command
    USE_HARDCODED_PATH = True
except ImportError:
    USE_HARDCODED_PATH = False
    RVC_MODULE = "rvc.wrapper.cli.cli"

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

    def create_ui(self):
        """メインUI構築"""
        # シンプルなラベル
        label = tk.Label(self.root, text="Voice Converter", 
                        font=('SF Pro Display', 24), 
                        bg=self.colors['background_primary'],
                        fg=self.colors['text_primary'])
        label.pack(pady=20)

    def load_models(self):
        """モデルの読み込み（簡略版）"""
        pass

    def log_message(self, message, level="INFO"):
        """ログメッセージ（簡略版）"""
        print(f"[{level}] {message}")

    def _run_rvc_direct(self, index_file, project_dir):
        """PyInstaller環境でRVCを直接実行（簡略版）"""
        # 必要なモジュールを関数の最初で確実にインポート
        import os
        import sys
        
        # PyTorchの初期化
        try:
            # pytorch_env_helperを使用
            try:
                from pytorch_env_helper import import_torch_with_fix
                torch = import_torch_with_fix()
                self.log_message("✅ pytorch_env_helperでPyTorch初期化成功")
            except ImportError:
                # フォールバック：通常のインポート
                self.log_message("pytorch_env_helper not found, using standard import")
                import torch
            
            self.log_message(f"PyTorch version: {torch.__version__}")
            self.log_message(f"PyTorch _C module: {hasattr(torch, '_C')}")
            
            # PyInstaller環境での診断
            if hasattr(sys, '_MEIPASS'):
                self.log_message("PyInstaller環境検出")
                if hasattr(torch, '_C'):
                    self.log_message("✅ torch._C モジュール存在確認")
                else:
                    self.log_message("❌ torch._C モジュールが見つかりません")
                    raise RuntimeError("torch._Cモジュールが初期化されていません")
                    
        except Exception as e:
            self.log_message(f"❌ PyTorch初期化エラー: {e}")
            import traceback
            self.log_message(f"スタックトレース: {traceback.format_exc()}")
            raise
        
        # RVC実行処理
        try:
            self.log_message("=== _run_rvc_direct関数実行 ===")
            
            # RVCモジュールのインポート
            from rvc.modules.vc.modules import VC
            from rvc.configs.config import Config
            import soundfile as sf
            from pathlib import Path
            
            self.log_message("RVCモジュールのインポート成功")
            
            # 以下、実際の処理...
            
        except Exception as e:
            self.log_message(f"RVC実行エラー: {str(e)}", "ERROR")
            import traceback
            self.log_message(f"詳細: {traceback.format_exc()}", "ERROR")
            raise

def main():
    root = tk.Tk()
    app = DarkModeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
