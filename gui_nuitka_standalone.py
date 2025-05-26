#!/usr/bin/env python3
"""
RVC Modern Flat Design GUI - 最新のフラットデザイン規格準拠
Material Design 3、Apple Human Interface Guidelines、
Fluent Design Systemの要素を取り入れた現代的なUI
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import subprocess
import threading
import shutil
from pathlib import Path
import time
from datetime import datetime

class ModernFlatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RVC Voice Converter")
        
        # システムダークモード検出（macOS）
        self.is_dark_mode = self.detect_system_theme()
        
        # デザイントークン（Material Design 3 + Apple HIG準拠）
        self.design_tokens = {
            # 色彩システム
            'colors': {
                'light': {
                    # Primary colors  
                    'background': '#FFFFFF',
                    'surface': '#F8F9FA',
                    'surface_variant': '#F0F1F3',
                    'surface_tint': '#E8E9EC',
                    
                    # Semantic colors
                    'primary': '#2563EB',  # 鮮やかな青
                    'primary_variant': '#1D4ED8',
                    'secondary': '#7C3AED',
                    'tertiary': '#DC2626',
                    
                    # Text colors
                    'on_background': '#000000',
                    'on_surface': '#111827',
                    'on_surface_variant': '#374151',
                    'on_surface_disabled': '#9CA3AF',
                    
                    # System colors
                    'success': '#10B981',
                    'warning': '#F59E0B',
                    'error': '#EF4444',
                    'info': '#3B82F6',
                    
                    # Elevation
                    'elevation_1': '#FAFAFA',
                    'elevation_2': '#F5F5F5',
                    'elevation_3': '#F0F0F0',
                    
                    # Borders
                    'border': '#E5E7EB',
                    'border_variant': '#D1D5DB',
                    'divider': '#E5E7EB',
                },
                'dark': {
                    # Primary colors
                    'background': '#0F0F0F',
                    'surface': '#1A1A1A',
                    'surface_variant': '#232323',
                    'surface_tint': '#2D2D2D',
                    
                    # Semantic colors
                    'primary': '#60A5FA',  # 明るい青
                    'primary_variant': '#3B82F6',
                    'secondary': '#A78BFA',
                    'tertiary': '#F87171',
                    
                    # Text colors
                    'on_background': '#FFFFFF',
                    'on_surface': '#F9FAFB',
                    'on_surface_variant': '#E5E7EB',
                    'on_surface_disabled': '#6B7280',
                    
                    # System colors
                    'success': '#34D399',
                    'warning': '#FBBF24',
                    'error': '#F87171',
                    'info': '#60A5FA',
                    
                    # Elevation
                    'elevation_1': '#262626',
                    'elevation_2': '#404040',
                    'elevation_3': '#525252',
                    
                    # Borders
                    'border': '#404040',
                    'border_variant': '#525252',
                    'divider': '#404040',
                }
            },
            
            # タイポグラフィ（SF Pro Display / Helvetica Neue）
            'typography': {
                'h1': {'size': 34, 'weight': 'normal'},
                'h2': {'size': 28, 'weight': 'normal'},
                'h3': {'size': 20, 'weight': 'normal'},
                'body_large': {'size': 17, 'weight': 'normal'},
                'body': {'size': 15, 'weight': 'normal'},
                'body_small': {'size': 13, 'weight': 'normal'},
                'caption': {'size': 11, 'weight': 'normal'},
                'button': {'size': 15, 'weight': 'bold'},
            },
            
            # スペーシング（8dpグリッドシステム）
            'spacing': {
                'xs': 4,
                'sm': 8,
                'md': 16,
                'lg': 24,
                'xl': 32,
                'xxl': 48,
            },
            
            # コーナー半径
            'radius': {
                'none': 0,
                'sm': 6,
                'md': 10,
                'lg': 16,
                'xl': 20,
                'full': 999,
            },
            
            # アニメーション
            'animation': {
                'fast': 200,
                'normal': 300,
                'slow': 500,
            }
        }
        
        # 現在のテーマカラーを設定
        self.theme = 'dark' if self.is_dark_mode else 'light'
        self.colors = self.design_tokens['colors'][self.theme]
        
        # アプリケーション設定
        self.setup_app_directories()
        self.model_info = {}
        self.selected_model = tk.StringVar()
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.pitch_var = tk.IntVar(value=0)
        
        # 高品質設定
        self.quality_params = {
            "f0method": "rmvpe",
            "index_rate": 1.0,
            "filter_radius": 7,
            "protect": 0.33,
            "rms_mix_rate": 0.0,
        }
        
        # ウィンドウ設定
        self.setup_window()
        
        # UI構築
        self.create_ui()
        
        # モデル読み込み
        self.load_models()
        
    def detect_system_theme(self):
        """システムのダークモードを検出"""
        if sys.platform == "darwin":
            try:
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            except:
                return False
        return False
        
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
        
    def setup_window(self):
        """ウィンドウの基本設定"""
        # 背景色
        self.root.configure(bg=self.colors['background'])
        
        # ウィンドウサイズ（より大きく）
        window_width = 1200
        window_height = 800
        
        # 画面中央に配置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(880, 600)
        
        # macOS用の設定
        if sys.platform == "darwin":
            self.root.tk.call('tk', 'scaling', 2.0)
            
    def create_ui(self):
        """メインUI構築"""
        # ナビゲーションバー
        self.create_navigation_bar()
        
        # メインコンテンツエリア
        self.main_content = tk.Frame(self.root, bg=self.colors['background'])
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 2カラムレイアウト
        self.create_two_column_layout()
        
    def create_navigation_bar(self):
        """ナビゲーションバー"""
        nav_bar = tk.Frame(self.root, bg=self.colors['surface'], height=56)
        nav_bar.pack(fill=tk.X)
        nav_bar.pack_propagate(False)
        
        # 左側：ロゴとタイトル
        left_frame = tk.Frame(nav_bar, bg=self.colors['surface'])
        left_frame.pack(side=tk.LEFT, padx=self.design_tokens['spacing']['lg'])
        
        # アプリアイコン（より目立つデザイン）
        icon_canvas = tk.Canvas(left_frame, width=36, height=36, 
                               bg=self.colors['surface'], highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, pady=14)
        
        # グラデーション風アイコン
        icon_canvas.create_oval(2, 2, 34, 34, fill=self.colors['primary'], outline='')
        icon_canvas.create_oval(4, 4, 32, 32, fill=self.colors['primary_variant'], outline='')
        icon_canvas.create_text(18, 18, text="🎵", fill="white", 
                               font=("SF Pro Display", 20))
        
        # タイトル（大きく見やすく）
        title_label = tk.Label(left_frame, text="Voice Converter",
                              font=("SF Pro Display", 22, "bold"),
                              bg=self.colors['surface'],
                              fg=self.colors['on_surface'])
        title_label.pack(side=tk.LEFT, padx=self.design_tokens['spacing']['sm'])
        
        # 右側：アクションボタン
        right_frame = tk.Frame(nav_bar, bg=self.colors['surface'])
        right_frame.pack(side=tk.RIGHT, padx=self.design_tokens['spacing']['lg'])
        
        # テーマ切り替えボタン
        self.theme_button = self.create_icon_button(
            right_frame, 
            "☀" if self.theme == 'dark' else "☾",
            self.toggle_theme
        )
        self.theme_button.pack(side=tk.RIGHT, pady=16)
        
    def create_two_column_layout(self):
        """2カラムレイアウト"""
        # 左カラム（モデル選択）- より広く
        self.left_column = tk.Frame(self.main_content, 
                                   bg=self.colors['surface_variant'],
                                   width=380)
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.left_column.pack_propagate(False)
        
        # 右カラム（メインコンテンツ）
        self.right_column = tk.Frame(self.main_content, 
                                    bg=self.colors['background'])
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 左カラムコンテンツ
        self.create_model_sidebar()
        
        # 右カラムコンテンツ
        self.create_main_content()
        
    def create_model_sidebar(self):
        """モデル選択サイドバー"""
        # ヘッダー
        header = tk.Frame(self.left_column, bg=self.colors['surface_variant'])
        header.pack(fill=tk.X, padx=self.design_tokens['spacing']['md'], 
                   pady=self.design_tokens['spacing']['md'])
        
        tk.Label(header, text="モデル",
                font=("SF Pro Display", 20, "bold"),
                bg=self.colors['surface_variant'],
                fg=self.colors['on_surface']).pack(anchor='w')
        
        tk.Label(header, text="使用する音声モデルを選択",
                font=("SF Pro Display", 14),
                bg=self.colors['surface_variant'],
                fg=self.colors['on_surface_variant']).pack(anchor='w', pady=(4, 0))
        
        # スクロール可能なモデルリスト
        self.model_scroll_frame = self.create_scrollable_frame(self.left_column)
        
    def create_main_content(self):
        """メインコンテンツエリア"""
        # パディング用フレーム
        content_padding = tk.Frame(self.right_column, bg=self.colors['background'])
        content_padding.pack(fill=tk.BOTH, expand=True, 
                           padx=self.design_tokens['spacing']['xl'],
                           pady=self.design_tokens['spacing']['lg'])
        
        # ファイル入力セクション
        self.create_file_section(content_padding)
        
        # 設定セクション
        self.create_settings_section(content_padding)
        
        # アクションセクション
        self.create_action_section(content_padding)
        
    def create_file_section(self, parent):
        """ファイル入力セクション"""
        section = self.create_card(parent, "ファイル")
        section.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['md']))
        
        # 入力ファイル
        self.create_file_input(section, "入力", "音声ファイルを選択", 
                              self.select_input_file, self.input_var)
        
        # セパレーター
        separator = tk.Frame(section, bg=self.colors['divider'], height=1)
        separator.pack(fill=tk.X, pady=self.design_tokens['spacing']['md'])
        
        # 出力ファイル
        self.output_section = tk.Frame(section, bg=self.colors['surface'])
        
    def create_settings_section(self, parent):
        """設定セクション"""
        section = self.create_card(parent, "設定")
        section.pack(fill=tk.X, pady=(0, self.design_tokens['spacing']['md']))
        
        # ピッチ調整
        self.create_slider_control(section, "ピッチ", "声の高さを調整", 
                                  self.pitch_var, -12, 12, "半音")
        
    def create_action_section(self, parent):
        """アクションセクション"""
        section = tk.Frame(parent, bg=self.colors['background'])
        section.pack(fill=tk.X, pady=self.design_tokens['spacing']['lg'])
        
        # 変換ボタン（より大きく、目立つデザイン）
        button_frame = tk.Frame(section, bg=self.colors['background'])
        button_frame.pack(pady=(8, 0))
        
        # グリーンベースの目立つボタン
        self.convert_button = tk.Button(
            button_frame, 
            text="変換を開始",
            command=self.start_conversion,
            font=("SF Pro Display", 16, "bold"),
            bg="#10B981",  # エメラルドグリーン
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=40, pady=16,
            cursor='hand2',
            activebackground="#059669",
            activeforeground="#FFFFFF",
            bd=0
        )
        self.convert_button.pack()
        
        # ホバー効果
        def on_enter(e):
            self.convert_button.config(bg="#059669")  # より濃いグリーン
        
        def on_leave(e):
            self.convert_button.config(bg="#10B981")
        
        self.convert_button.bind("<Enter>", on_enter)
        self.convert_button.bind("<Leave>", on_leave)
        
        # プログレス表示（初期非表示）
        self.progress_frame = tk.Frame(section, bg=self.colors['background'])
        
        # リニアプログレスバー
        self.create_progress_indicator(self.progress_frame)
        
    def create_card(self, parent, title):
        """カードコンポーネント"""
        card = tk.Frame(parent, bg=self.colors['surface'],
                       relief=tk.FLAT)
        card.pack(fill=tk.X)
        
        # カード内のパディング
        inner = tk.Frame(card, bg=self.colors['surface'])
        inner.pack(fill=tk.BOTH, expand=True, 
                  padx=self.design_tokens['spacing']['lg'],
                  pady=self.design_tokens['spacing']['lg'])
        
        # タイトル
        if title:
            title_label = tk.Label(inner, text=title,
                                 font=("SF Pro Display", 17, "bold"),
                                 bg=self.colors['surface'],
                                 fg=self.colors['on_surface'])
            title_label.pack(anchor='w', pady=(0, self.design_tokens['spacing']['md']))
        
        return inner
        
    def create_file_input(self, parent, label, placeholder, command, var):
        """ファイル入力コンポーネント"""
        container = tk.Frame(parent, bg=self.colors['surface'])
        container.pack(fill=tk.X, pady=self.design_tokens['spacing']['sm'])
        
        # ラベル
        tk.Label(container, text=label,
                font=("SF Pro Display", 13),
                bg=self.colors['surface'],
                fg=self.colors['on_surface_variant']).pack(anchor='w')
        
        # 入力フィールド（より見やすく）
        field_frame = tk.Frame(container, bg=self.colors['surface_tint'],
                              relief=tk.FLAT, borderwidth=1)
        field_frame.pack(fill=tk.X, pady=(6, 0))
        
        # 枠線を追加
        field_frame.config(highlightbackground=self.colors['border'],
                          highlightthickness=1)
        
        # ファイルアイコン
        icon_label = tk.Label(field_frame, text="📁",
                            font=("SF Pro Display", 18),
                            bg=self.colors['surface_tint'],
                            fg=self.colors['on_surface_variant'])
        icon_label.pack(side=tk.LEFT, padx=(14, 10))
        
        # プレースホルダー/値表示
        self.create_placeholder_label(field_frame, var, placeholder)
        
        # 選択ボタン（コントラストの高い配色）
        select_btn = tk.Button(field_frame, 
                             text="選択",
                             command=command,
                             font=("SF Pro Display", 14, "bold"),
                             bg="#3B82F6",  # 明るい青
                             fg="#FFFFFF",
                             relief=tk.FLAT,
                             padx=20, pady=8,
                             cursor='hand2',
                             activebackground="#2563EB",
                             activeforeground="#FFFFFF",
                             bd=0)
        select_btn.pack(side=tk.RIGHT, padx=12, pady=8)
        
        # ホバー効果
        def on_enter(e):
            select_btn.config(bg="#2563EB")  # より濃い青
        
        def on_leave(e):
            select_btn.config(bg="#3B82F6")
        
        select_btn.bind("<Enter>", on_enter)
        select_btn.bind("<Leave>", on_leave)
        
        return container
        
    def create_placeholder_label(self, parent, var, placeholder):
        """プレースホルダー付きラベル"""
        label = tk.Label(parent, 
                        font=("SF Pro Display", 15),
                        bg=self.colors['surface_tint'],
                        anchor='w')
        label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=14)
        
        def update_label(*args):
            if var.get():
                label.config(text=var.get(), fg=self.colors['on_surface'])
            else:
                label.config(text=placeholder, fg=self.colors['on_surface_disabled'])
        
        var.trace_add('write', update_label)
        update_label()  # 初期化
        
        return label
        
    def create_slider_control(self, parent, label, description, var, min_val, max_val, unit):
        """スライダーコントロール"""
        container = tk.Frame(parent, bg=self.colors['surface'])
        container.pack(fill=tk.X, pady=self.design_tokens['spacing']['md'])
        
        # ヘッダー
        header_frame = tk.Frame(container, bg=self.colors['surface'])
        header_frame.pack(fill=tk.X)
        
        # ラベルと値
        label_frame = tk.Frame(header_frame, bg=self.colors['surface'])
        label_frame.pack(side=tk.LEFT)
        
        tk.Label(label_frame, text=label,
                font=("SF Pro Display", 15, "bold"),
                bg=self.colors['surface'],
                fg=self.colors['on_surface']).pack(anchor='w')
        
        if description:
            tk.Label(label_frame, text=description,
                    font=("SF Pro Display", 12),
                    bg=self.colors['surface'],
                    fg=self.colors['on_surface_variant']).pack(anchor='w')
        
        # 値表示
        value_label = tk.Label(header_frame, 
                             text=f"{var.get()}{unit}",
                             font=("SF Pro Display", 15, "bold"),
                             bg=self.colors['surface'],
                             fg=self.colors['primary'])
        value_label.pack(side=tk.RIGHT)
        
        # スライダー
        slider_frame = tk.Frame(container, bg=self.colors['surface'])
        slider_frame.pack(fill=tk.X, pady=(12, 0))
        
        # カスタムスライダー（見やすく）
        slider = ttk.Scale(slider_frame, from_=min_val, to=max_val,
                          variable=var, orient=tk.HORIZONTAL)
        slider.pack(fill=tk.X)
        
        # スタイル設定
        style = ttk.Style()
        style.configure("Flat.Horizontal.TScale",
                       background=self.colors['surface'],
                       troughcolor=self.colors['surface_tint'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        slider.configure(style="Flat.Horizontal.TScale")
        
        # 値の更新
        def update_value(*args):
            value_label.config(text=f"{int(var.get())}{unit}")
        
        var.trace_add('write', update_value)
        
        return container
        
    def create_icon_button(self, parent, icon, command):
        """アイコンボタン"""
        button = tk.Button(parent, text=icon, command=command,
                          font=("SF Pro Display", 16),
                          bg=self.colors['surface'],
                          fg=self.colors['on_surface_variant'],
                          relief=tk.FLAT,
                          width=3, height=1,
                          cursor='hand2')
        
        def on_enter(e):
            button.config(bg=self.colors['surface_tint'])
        
        def on_leave(e):
            button.config(bg=self.colors['surface'])
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
        
    def create_scrollable_frame(self, parent):
        """スクロール可能フレーム"""
        # Canvas
        canvas = tk.Canvas(parent, bg=self.colors['surface_variant'],
                          highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # スクロール可能フレーム
        scrollable_frame = tk.Frame(canvas, bg=self.colors['surface_variant'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # マウスホイール
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        return scrollable_frame
        
    def create_progress_indicator(self, parent):
        """プログレスインジケーター"""
        # プログレスコンテナ
        container = tk.Frame(parent, bg=self.colors['background'])
        container.pack(pady=self.design_tokens['spacing']['lg'])
        
        # ステータステキスト
        self.status_label = tk.Label(container, text="",
                                   font=("SF Pro Display", 14),
                                   bg=self.colors['background'],
                                   fg=self.colors['on_surface_variant'])
        self.status_label.pack()
        
        # プログレスバー
        progress_bg = tk.Frame(container, bg=self.colors['surface_tint'], height=4)
        progress_bg.pack(fill=tk.X, pady=(8, 0))
        
        self.progress_bar = tk.Frame(progress_bg, bg=self.colors['primary'], height=4)
        self.progress_bar.place(x=0, y=0, relwidth=0, relheight=1)
        
        return container
        
    def load_models(self):
        """モデルを読み込み"""
        # モデルリストをクリア
        for widget in self.model_scroll_frame.winfo_children():
            widget.destroy()
            
        if not os.path.exists(self.model_dir):
            # エラー表示
            self.show_no_models_message()
            return
            
        # モデルを検索
        models = []
        for item in os.listdir(self.model_dir):
            item_path = os.path.join(self.model_dir, item)
            if os.path.isdir(item_path):
                model_info = self.get_model_info(item, item_path)
                if model_info:
                    models.append((item, model_info))
                    
        if not models:
            self.show_no_models_message()
            return
            
        # モデルカードを作成
        for i, (model_id, model_info) in enumerate(models):
            self.create_model_card(self.model_scroll_frame, model_id, model_info, i)
            
        # 最初のモデルを選択
        if models:
            self.selected_model.set(models[0][0])
            
    def show_no_models_message(self):
        """モデルがない場合のメッセージ"""
        msg_frame = tk.Frame(self.model_scroll_frame, 
                           bg=self.colors['surface_variant'])
        msg_frame.pack(fill=tk.BOTH, expand=True, pady=32)
        
        tk.Label(msg_frame, text="モデルが見つかりません",
                font=("SF Pro Display", 14),
                bg=self.colors['surface_variant'],
                fg=self.colors['on_surface_variant']).pack()
                
    def get_model_info(self, model_id, model_path):
        """モデル情報を取得"""
        info = {
            'id': model_id,
            'name': f'モデル {model_id}',
            'description': '',
            'has_index': False,
            'model_file': None
        }
        
        # params.jsonを読み込み
        params_file = os.path.join(model_path, 'params.json')
        if os.path.exists(params_file):
            try:
                with open(params_file, 'r', encoding='utf-8') as f:
                    params = json.load(f)
                    info['name'] = params.get('name', info['name'])
                    info['description'] = params.get('description', '')
            except:
                pass
        
        # ファイルチェック
        for file in os.listdir(model_path):
            if file.endswith('.pth'):
                info['model_file'] = file
            elif file.endswith('.index'):
                info['has_index'] = True
        
        if not info['model_file']:
            return None
            
        self.model_info[model_id] = info
        return info
        
    def create_model_card(self, parent, model_id, model_info, index):
        """モデルカード"""
        # カードフレーム
        card_frame = tk.Frame(parent, bg=self.colors['surface_variant'])
        card_frame.pack(fill=tk.X, padx=self.design_tokens['spacing']['md'],
                       pady=(0, self.design_tokens['spacing']['sm']))
        
        card = tk.Frame(card_frame, bg=self.colors['surface'])
        card.pack(fill=tk.X)
        
        # 選択状態チェック
        is_selected = self.selected_model.get() == model_id
        if is_selected:
            card.config(bg=self.colors['primary'])
            
        # カード内容
        inner = tk.Frame(card, bg=card['bg'])
        inner.pack(fill=tk.X, padx=16, pady=12)
        
        # モデル名（大きく表示）
        name_color = "#FFFFFF" if is_selected else self.colors['on_surface']
        name_label = tk.Label(inner, text=model_info['name'],
                            font=("SF Pro Display", 16, "bold"),
                            bg=inner['bg'], fg=name_color)
        name_label.pack(anchor='w')
        
        # バッジ
        if model_info['has_index']:
            badge_frame = tk.Frame(inner, bg=inner['bg'])
            badge_frame.pack(anchor='w', pady=(4, 0))
            
            badge = tk.Label(badge_frame, text="✓ インデックス",
                           font=("SF Pro Display", 11, "bold"),
                           bg=self.colors['success'] if not is_selected else "#FFFFFF",
                           fg="#FFFFFF" if not is_selected else self.colors['success'],
                           padx=10, pady=3)
            badge.pack(side=tk.LEFT)
        
        # クリックイベント
        def on_click(event=None):
            self.selected_model.set(model_id)
            self.load_models()  # 再描画
            
        for widget in [card, inner, name_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", lambda e: card.config(bg=self.colors['surface_tint']))
            widget.bind("<Leave>", lambda e: card.config(bg=self.colors['primary'] if self.selected_model.get() == model_id else self.colors['surface']))
            
    def select_input_file(self):
        """入力ファイル選択"""
        filename = filedialog.askopenfilename(
            title="音声ファイルを選択",
            filetypes=[
                ("音声ファイル", "*.wav *.mp3 *.m4a *.flac *.ogg"),
                ("すべてのファイル", "*.*")
            ]
        )
        if filename:
            # ファイル名表示
            display_name = os.path.basename(filename)
            if len(display_name) > 40:
                display_name = display_name[:37] + "..."
            self.input_var.set(display_name)
            self.input_file_path = filename
            
            # 出力ファイルセクションを表示
            if not self.output_section.winfo_manager():
                self.output_section.pack(fill=tk.X)
                self.create_file_input(self.output_section, "出力", 
                                     "保存先を指定", 
                                     self.select_output_file, 
                                     self.output_var)
            
            # 出力ファイルを自動生成
            base = os.path.splitext(os.path.basename(filename))[0]
            output = os.path.join(
                os.path.dirname(filename),
                f"{base}_RVC.wav"
            )
            output_display = os.path.basename(output)
            if len(output_display) > 40:
                output_display = output_display[:37] + "..."
            self.output_var.set(output_display)
            self.output_file_path = output
            
            # 成功フィードバック
            self.show_toast("ファイルを選択しました", "success")
            
    def select_output_file(self):
        """出力ファイル選択"""
        filename = filedialog.asksaveasfilename(
            title="保存先を指定",
            defaultextension=".wav",
            filetypes=[
                ("WAVファイル", "*.wav"),
                ("すべてのファイル", "*.*")
            ]
        )
        if filename:
            display_name = os.path.basename(filename)
            if len(display_name) > 40:
                display_name = display_name[:37] + "..."
            self.output_var.set(display_name)
            self.output_file_path = filename
            
            self.show_toast("保存先を設定しました", "success")
            
    def toggle_theme(self):
        """テーマ切り替え"""
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.colors = self.design_tokens['colors'][self.theme]
        
        # UIを再構築
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_ui()
        self.load_models()
        
        # ボタンアイコンを更新
        self.theme_button.config(text="☀" if self.theme == 'dark' else "☾")
        
    def show_toast(self, message, type="info"):
        """トースト通知"""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        
        # 色設定
        colors = {
            'success': self.colors['success'],
            'error': self.colors['error'],
            'warning': self.colors['warning'],
            'info': self.colors['info']
        }
        
        bg_color = colors.get(type, colors['info'])
        
        # トーストフレーム
        frame = tk.Frame(toast, bg=bg_color)
        frame.pack()
        
        # メッセージ
        msg_label = tk.Label(frame, text=message,
                           font=("SF Pro Display", 14),
                           bg=bg_color, fg="white",
                           padx=24, pady=12)
        msg_label.pack()
        
        # 位置設定
        toast.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - toast.winfo_width()) // 2
        y = self.root.winfo_y() + 80
        toast.geometry(f"+{x}+{y}")
        
        # 自動で閉じる
        toast.after(2000, toast.destroy)
        
    def start_conversion(self):
        """変換開始"""
        # 入力チェック
        if not self.selected_model.get():
            self.show_toast("モデルを選択してください", "warning")
            return
            
        if not hasattr(self, 'input_file_path') or not self.input_file_path:
            self.show_toast("入力ファイルを選択してください", "warning")
            return
            
        # UI更新
        self.convert_button.config(state='disabled', bg="#9CA3AF", fg="#FFFFFF")
        self.progress_frame.pack(fill=tk.X, pady=self.design_tokens['spacing']['lg'])
        
        # 変換スレッド開始
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
        
    def run_conversion(self):
        """変換処理実行"""
        try:
            # プログレス更新
            self.update_progress(0.1, "準備中...")
            
            # モデル情報取得
            model_id = self.selected_model.get()
            model_info = self.model_info.get(model_id)
            
            if not model_info:
                raise Exception("モデル情報が見つかりません")
                
            # パス設定
            model_path = os.path.join(self.model_dir, model_id)
            pth_files = [f for f in os.listdir(model_path) if f.endswith('.pth')]
            if not pth_files:
                raise Exception("モデルファイルが見つかりません")
                
            model_file = os.path.join(model_path, pth_files[0])
            
            # インデックスファイル
            index_files = [f for f in os.listdir(model_path) if f.endswith('.index')]
            index_file = os.path.join(model_path, index_files[0]) if index_files else None
            
            # Hubertモデル
            hubert_path = os.path.join(self.model_dir, "hubert_base.pt")
            if not os.path.exists(hubert_path):
                raise Exception("Hubertモデルが見つかりません")
                
            self.update_progress(0.3, "音声を処理中...")
            
            # プロジェクトディレクトリ
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
                        
            self.update_progress(0.5, "変換を実行中...")
            
            # CLIコマンド
            cmd = [
                f'cd "{project_dir}"',
                "&&",
                "poetry", "run", "rvc", "infer",
                "-m", f'"{model_file}"',
                "-i", f'"{self.input_file_path}"',
                "-o", f'"{self.output_file_path}"',
                "-fu", str(self.pitch_var.get()),
                "-fm", self.quality_params["f0method"],
                "-ir", str(self.quality_params["index_rate"]),
                "-fr", str(self.quality_params["filter_radius"]),
                "-p", str(self.quality_params["protect"]),
                "-rmr", str(self.quality_params["rms_mix_rate"])
            ]
            
            if index_file:
                cmd.extend(["-if", f'"{index_file}"'])
                
            cmd.extend(["--hubert_model_path", f'"{hubert_path}"'])
            
            # 実行
            shell_cmd = " ".join(cmd)
            env = os.environ.copy()
            env['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            
            self.update_progress(0.7, "音声を変換中...")
            
            result = subprocess.run(
                shell_cmd,
                shell=True,
                capture_output=True,
                text=True,
                env=env
            )
            
            self.update_progress(0.9, "最終処理中...")
            
            # 結果確認
            if result.returncode == 0 and os.path.exists(self.output_file_path):
                self.update_progress(1.0, "完了！")
                self.root.after(0, self.conversion_complete)
            else:
                error_msg = result.stderr if result.stderr else "変換に失敗しました"
                raise Exception(error_msg)
                
        except Exception as e:
            self.root.after(0, lambda: self.show_toast(str(e), "error"))
        finally:
            self.root.after(1000, self.reset_ui)
            
    def update_progress(self, value, message):
        """プログレス更新"""
        self.root.after(0, lambda: self.status_label.config(text=message))
        self.root.after(0, lambda: self.progress_bar.place(relwidth=value))
        
    def conversion_complete(self):
        """変換完了処理"""
        self.show_toast("変換が完了しました！", "success")
        
        if sys.platform == "darwin":
            result = messagebox.askyesno(
                "完了",
                "変換が完了しました。ファイルを開きますか？"
            )
            if result:
                subprocess.run(["open", "-R", self.output_file_path])
                
    def reset_ui(self):
        """UIリセット"""
        self.convert_button.config(state='normal', bg="#10B981")
        self.progress_frame.pack_forget()
        self.progress_bar.place(relwidth=0)
        self.status_label.config(text="")

def main():
    root = tk.Tk()
    
    # macOSでの高DPI対応
    if sys.platform == "darwin":
        root.tk.call('tk', 'scaling', 2.0)
    
    app = ModernFlatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
