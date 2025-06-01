#!/usr/bin/env python3
"""
UIコンポーネント・ファクトリーパターン
再利用可能で統一されたUIコンポーネントの提供
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, Union, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class ComponentStyle(Enum):
    """コンポーネントスタイルの定義"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    GHOST = "ghost"
    MINIMAL = "minimal"

class ComponentSize(Enum):
    """コンポーネントサイズの定義"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "xl"

@dataclass
class ThemeConfig:
    """テーマ設定"""
    colors: Dict[str, str]
    typography: Dict[str, Dict[str, Union[int, str]]]
    spacing: Dict[str, int]
    radius: Dict[str, int]
    layout: Dict[str, int]

class ComponentFactory:
    """UIコンポーネントファクトリークラス"""
    
    def __init__(self, theme_config: ThemeConfig):
        """
        ファクトリーの初期化
        
        Args:
            theme_config: テーマ設定
        """
        self.theme = theme_config
        self._setup_styles()
    
    def _setup_styles(self):
        """TTKスタイルの設定"""
        self.style = ttk.Style()
        
        # スタイル定義の辞書
        self.button_styles = {
            ComponentStyle.PRIMARY: {
                'bg': self.theme.colors['accent_primary'],
                'fg': 'white',
                'active_bg': self.theme.colors['accent_secondary'],
                'active_fg': 'white'
            },
            ComponentStyle.SECONDARY: {
                'bg': self.theme.colors['background_tertiary'],
                'fg': self.theme.colors['text_primary'],
                'active_bg': self.theme.colors['background_elevated'],
                'active_fg': self.theme.colors['text_primary']
            },
            ComponentStyle.SUCCESS: {
                'bg': self.theme.colors['success'],
                'fg': 'white',
                'active_bg': '#45D574',
                'active_fg': 'white'
            },
            ComponentStyle.WARNING: {
                'bg': self.theme.colors['warning'],
                'fg': '#1A1A1C',
                'active_bg': '#E6C035',
                'active_fg': '#1A1A1C'
            },
            ComponentStyle.ERROR: {
                'bg': self.theme.colors['error'],
                'fg': 'white',
                'active_bg': '#E55555',
                'active_fg': 'white'
            },
            ComponentStyle.GHOST: {
                'bg': 'transparent',
                'fg': self.theme.colors['text_secondary'],
                'active_bg': self.theme.colors['hover'],
                'active_fg': self.theme.colors['text_primary']
            }
        }
        
        self.size_configs = {
            ComponentSize.SMALL: {
                'font_size': self.theme.typography['caption1']['size'],
                'padding_x': self.theme.spacing['sm'],
                'padding_y': self.theme.spacing['xs'],
                'height': 28
            },
            ComponentSize.MEDIUM: {
                'font_size': self.theme.typography['body']['size'],
                'padding_x': self.theme.spacing['md'],
                'padding_y': self.theme.spacing['sm'],
                'height': 36
            },
            ComponentSize.LARGE: {
                'font_size': self.theme.typography['headline']['size'],
                'padding_x': self.theme.spacing['lg'],
                'padding_y': self.theme.spacing['md'],
                'height': 44
            },
            ComponentSize.EXTRA_LARGE: {
                'font_size': self.theme.typography['title3']['size'],
                'padding_x': self.theme.spacing['xl'],
                'padding_y': self.theme.spacing['lg'],
                'height': 52
            }
        }
    
    def create_button(self, parent: tk.Widget, text: str, command: Callable = None,
                     style: ComponentStyle = ComponentStyle.PRIMARY,
                     size: ComponentSize = ComponentSize.MEDIUM,
                     width: Optional[int] = None, disabled: bool = False,
                     icon: Optional[str] = None, **kwargs) -> tk.Button:
        """
        統一されたボタンの作成
        
        Args:
            parent: 親ウィジェット
            text: ボタンテキスト
            command: クリック時のコマンド
            style: ボタンスタイル
            size: ボタンサイズ
            width: カスタム幅
            disabled: 無効状態
            icon: アイコン文字
            **kwargs: 追加の設定
            
        Returns:
            作成されたボタン
        """
        # スタイル設定を取得
        style_config = self.button_styles[style]
        size_config = self.size_configs[size]
        
        # アイコンとテキストの結合
        display_text = f"{icon} {text}" if icon else text
        
        # ボタンの作成
        button = tk.Button(
            parent,
            text=display_text,
            command=command,
            font=('Arial', size_config['font_size'], 'normal'),
            bg=style_config['bg'],
            fg=style_config['fg'],
            activebackground=style_config['active_bg'],
            activeforeground=style_config['active_fg'],
            relief='flat',
            bd=0,
            padx=size_config['padding_x'],
            pady=size_config['padding_y'],
            cursor='hand2' if not disabled else 'arrow',
            state='disabled' if disabled else 'normal',
            **kwargs
        )
        
        if width:
            button.config(width=width)
        
        # ホバーエフェクトの追加
        self._add_hover_effect(button, style_config)
        
        return button
    
    def create_input(self, parent: tk.Widget, textvariable: tk.StringVar = None,
                    placeholder: str = "", size: ComponentSize = ComponentSize.MEDIUM,
                    disabled: bool = False, password: bool = False,
                    validation: Optional[Callable] = None, **kwargs) -> tk.Entry:
        """
        統一された入力フィールドの作成
        
        Args:
            parent: 親ウィジェット
            textvariable: テキスト変数
            placeholder: プレースホルダーテキスト
            size: サイズ
            disabled: 無効状態
            password: パスワードフィールド
            validation: 入力検証関数
            **kwargs: 追加の設定
            
        Returns:
            作成された入力フィールド
        """
        size_config = self.size_configs[size]
        
        # 入力フィールドの作成
        entry = tk.Entry(
            parent,
            textvariable=textvariable,
            font=('Arial', size_config['font_size']),
            bg=self.theme.colors['background_tertiary'],
            fg=self.theme.colors['text_primary'],
            insertbackground=self.theme.colors['text_primary'],
            relief='flat',
            bd=size_config['padding_y'],
            show='*' if password else '',
            state='disabled' if disabled else 'normal',
            **kwargs
        )
        
        # プレースホルダーの実装
        if placeholder:
            self._add_placeholder(entry, placeholder)
        
        # 入力検証の追加
        if validation:
            self._add_validation(entry, validation)
        
        # フォーカスエフェクトの追加
        self._add_focus_effect(entry)
        
        return entry
    
    def create_label(self, parent: tk.Widget, text: str,
                    style: ComponentStyle = ComponentStyle.PRIMARY,
                    size: ComponentSize = ComponentSize.MEDIUM,
                    weight: str = 'normal', **kwargs) -> tk.Label:
        """
        統一されたラベルの作成
        
        Args:
            parent: 親ウィジェット
            text: ラベルテキスト
            style: ラベルスタイル
            size: サイズ
            weight: フォント重み
            **kwargs: 追加の設定
            
        Returns:
            作成されたラベル
        """
        size_config = self.size_configs[size]
        
        # テキスト色の決定
        if style == ComponentStyle.PRIMARY:
            fg_color = self.theme.colors['text_primary']
        elif style == ComponentStyle.SECONDARY:
            fg_color = self.theme.colors['text_secondary']
        elif style == ComponentStyle.SUCCESS:
            fg_color = self.theme.colors['success']
        elif style == ComponentStyle.WARNING:
            fg_color = self.theme.colors['warning']
        elif style == ComponentStyle.ERROR:
            fg_color = self.theme.colors['error']
        else:
            fg_color = self.theme.colors['text_primary']
        
        label = tk.Label(
            parent,
            text=text,
            font=('Arial', size_config['font_size'], weight),
            bg=parent.cget('bg') if hasattr(parent, 'cget') else self.theme.colors['background_primary'],
            fg=fg_color,
            **kwargs
        )
        
        return label
    
    def create_card(self, parent: tk.Widget, title: str = "",
                   padding: int = None, elevated: bool = True,
                   **kwargs) -> tk.Frame:
        """
        カードコンポーネントの作成
        
        Args:
            parent: 親ウィジェット
            title: カードタイトル
            padding: パディング
            elevated: 立体効果
            **kwargs: 追加の設定
            
        Returns:
            カードフレーム
        """
        if padding is None:
            padding = self.theme.spacing['lg']
        
        # カードコンテナ
        card_container = tk.Frame(
            parent,
            bg=self.theme.colors['surface_card'] if elevated else self.theme.colors['background_secondary'],
            relief='flat',
            bd=0,
            **kwargs
        )
        
        # タイトルがある場合
        if title:
            title_label = self.create_label(
                card_container,
                title,
                style=ComponentStyle.PRIMARY,
                size=ComponentSize.MEDIUM,
                weight='bold'
            )
            title_label.pack(anchor='w', padx=padding, pady=(padding, padding//2))
        
        # コンテンツエリア
        content_frame = tk.Frame(
            card_container,
            bg=card_container.cget('bg')
        )
        content_frame.pack(fill='both', expand=True, padx=padding, pady=(0, padding))
        
        # カードの参照をコンテンツフレームに保存
        content_frame.card_container = card_container
        
        return content_frame
    
    def create_slider(self, parent: tk.Widget, variable: Union[tk.IntVar, tk.DoubleVar],
                     min_val: float, max_val: float, label: str = "",
                     show_value: bool = True, orientation: str = 'horizontal',
                     **kwargs) -> tk.Frame:
        """
        カスタムスライダーの作成
        
        Args:
            parent: 親ウィジェット
            variable: 値変数
            min_val: 最小値
            max_val: 最大値
            label: ラベル
            show_value: 値表示
            orientation: 向き
            **kwargs: 追加の設定
            
        Returns:
            スライダーコンテナ
        """
        slider_frame = tk.Frame(parent, bg=parent.cget('bg'))
        
        # ラベルと値表示
        if label or show_value:
            header_frame = tk.Frame(slider_frame, bg=slider_frame.cget('bg'))
            header_frame.pack(fill='x', pady=(0, self.theme.spacing['xs']))
            
            if label:
                label_widget = self.create_label(
                    header_frame, label,
                    style=ComponentStyle.SECONDARY,
                    size=ComponentSize.SMALL
                )
                label_widget.pack(side='left')
            
            if show_value:
                value_label = self.create_label(
                    header_frame,
                    str(variable.get()),
                    style=ComponentStyle.PRIMARY,
                    size=ComponentSize.SMALL,
                    weight='bold'
                )
                value_label.pack(side='right')
                
                # 値が変更されたときのコールバック
                def update_value_label(*args):
                    if isinstance(variable, tk.DoubleVar):
                        value_label.config(text=f"{variable.get():.2f}")
                    else:
                        value_label.config(text=str(variable.get()))
                
                variable.trace('w', update_value_label)
        
        # カスタムスライダーの実装
        canvas = tk.Canvas(
            slider_frame,
            height=6 if orientation == 'horizontal' else 200,
            bg=slider_frame.cget('bg'),
            highlightthickness=0
        )
        canvas.pack(fill='x' if orientation == 'horizontal' else 'y', 
                   padx=self.theme.spacing['xs'])
        
        # スライダーの描画と操作
        self._setup_slider_canvas(canvas, variable, min_val, max_val, orientation)
        
        return slider_frame
    
    def create_dropdown(self, parent: tk.Widget, textvariable: tk.StringVar,
                       values: List[str], size: ComponentSize = ComponentSize.MEDIUM,
                       **kwargs) -> ttk.Combobox:
        """
        ドロップダウンの作成
        
        Args:
            parent: 親ウィジェット
            textvariable: テキスト変数
            values: 選択肢
            size: サイズ
            **kwargs: 追加の設定
            
        Returns:
            作成されたCombobox
        """
        size_config = self.size_configs[size]
        
        # カスタムComboboxスタイルの設定
        style_name = 'Custom.TCombobox'
        self.style.configure(
            style_name,
            fieldbackground=self.theme.colors['background_tertiary'],
            background=self.theme.colors['background_tertiary'],
            foreground=self.theme.colors['text_primary'],
            selectbackground=self.theme.colors['accent_primary'],
            selectforeground='white',
            borderwidth=0,
            relief='flat'
        )
        
        combo = ttk.Combobox(
            parent,
            textvariable=textvariable,
            values=values,
            state='readonly',
            style=style_name,
            font=('Arial', size_config['font_size']),
            **kwargs
        )
        
        return combo
    
    def create_progress_bar(self, parent: tk.Widget, mode: str = 'determinate',
                           length: int = 200, **kwargs) -> tk.Frame:
        """
        カスタムプログレスバーの作成
        
        Args:
            parent: 親ウィジェット
            mode: モード（determinate/indeterminate）
            length: 長さ
            **kwargs: 追加の設定
            
        Returns:
            プログレスバーコンテナ
        """
        progress_frame = tk.Frame(parent, bg=parent.cget('bg'))
        
        # プログレスバーCanvas
        canvas = tk.Canvas(
            progress_frame,
            height=4,
            width=length,
            bg=parent.cget('bg'),
            highlightthickness=0
        )
        canvas.pack(fill='x')
        
        # 背景とプログレス描画
        def draw_progress(progress: float = 0.0):
            canvas.delete("all")
            width = canvas.winfo_width()
            height = 4
            
            if width <= 1:
                return
            
            # 背景
            canvas.create_rectangle(
                0, 0, width, height,
                fill=self.theme.colors['background_tertiary'],
                outline=""
            )
            
            # プログレス
            if progress > 0:
                progress_width = int(width * min(progress, 1.0))
                canvas.create_rectangle(
                    0, 0, progress_width, height,
                    fill=self.theme.colors['accent_primary'],
                    outline=""
                )
        
        # 初期描画
        canvas.after(100, lambda: draw_progress(0))
        
        # プログレスバーのインターフェース
        progress_frame.set_progress = draw_progress
        
        return progress_frame
    
    def create_tooltip(self, widget: tk.Widget, text: str, delay: int = 500):
        """
        ツールチップの追加
        
        Args:
            widget: 対象ウィジェット
            text: ツールチップテキスト
            delay: 表示遅延（ミリ秒）
        """
        tooltip = ToolTip(widget, text, delay, self.theme)
        return tooltip
    
    def _add_hover_effect(self, button: tk.Button, style_config: Dict[str, str]):
        """ボタンのホバーエフェクト追加"""
        def on_enter(e):
            if button.cget('state') != 'disabled':
                button.config(bg=style_config['active_bg'])
        
        def on_leave(e):
            if button.cget('state') != 'disabled':
                button.config(bg=style_config['bg'])
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def _add_placeholder(self, entry: tk.Entry, placeholder: str):
        """入力フィールドのプレースホルダー追加"""
        placeholder_color = self.theme.colors['text_disabled']
        normal_color = self.theme.colors['text_primary']
        
        def on_focus_in(event):
            if entry.cget('fg') == placeholder_color:
                entry.delete(0, 'end')
                entry.config(fg=normal_color)
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=placeholder_color)
        
        # 初期プレースホルダー設定
        entry.insert(0, placeholder)
        entry.config(fg=placeholder_color)
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
    
    def _add_validation(self, entry: tk.Entry, validation_func: Callable):
        """入力検証の追加"""
        def validate(*args):
            value = entry.get()
            is_valid = validation_func(value)
            
            if is_valid:
                entry.config(bg=self.theme.colors['background_tertiary'])
            else:
                entry.config(bg=self.theme.colors['error'])
        
        entry.bind('<KeyRelease>', validate)
        entry.bind('<FocusOut>', validate)
    
    def _add_focus_effect(self, entry: tk.Entry):
        """入力フィールドのフォーカスエフェクト追加"""
        normal_bg = self.theme.colors['background_tertiary']
        focus_bg = self.theme.colors['background_elevated']
        
        def on_focus_in(event):
            entry.config(bg=focus_bg)
        
        def on_focus_out(event):
            entry.config(bg=normal_bg)
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
    
    def _setup_slider_canvas(self, canvas: tk.Canvas, variable: Union[tk.IntVar, tk.DoubleVar],
                           min_val: float, max_val: float, orientation: str):
        """スライダーCanvasのセットアップ"""
        def draw_slider():
            canvas.delete("all")
            
            if orientation == 'horizontal':
                width = canvas.winfo_width()
                height = 6
                track_y = height // 2
                
                if width <= 1:
                    return
                
                # トラック描画
                canvas.create_rectangle(
                    0, track_y-2, width, track_y+2,
                    fill=self.theme.colors['background_tertiary'],
                    outline=""
                )
                
                # 進捗描画
                progress = (variable.get() - min_val) / (max_val - min_val)
                progress_width = int(width * progress)
                if progress_width > 0:
                    canvas.create_rectangle(
                        0, track_y-2, progress_width, track_y+2,
                        fill=self.theme.colors['accent_primary'],
                        outline=""
                    )
                
                # ハンドル描画
                handle_x = progress_width
                handle_radius = 8
                canvas.create_oval(
                    handle_x-handle_radius, track_y-handle_radius,
                    handle_x+handle_radius, track_y+handle_radius,
                    fill=self.theme.colors['accent_primary'],
                    outline=""
                )
        
        def on_click(event):
            if orientation == 'horizontal':
                width = canvas.winfo_width()
                if width <= 1:
                    return
                
                progress = event.x / width
                progress = max(0, min(1, progress))
                
                new_value = min_val + (max_val - min_val) * progress
                
                if isinstance(variable, tk.IntVar):
                    variable.set(int(new_value))
                else:
                    variable.set(round(new_value, 2))
                
                draw_slider()
        
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<B1-Motion>", on_click)
        canvas.bind("<Configure>", lambda e: draw_slider())
        
        # 初期描画
        canvas.after(100, draw_slider)

class ToolTip:
    """ツールチップクラス"""
    
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500, theme: ThemeConfig = None):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.theme = theme
        self.tooltip_window = None
        self.timer_id = None
        
        # イベントバインド
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event=None):
        """マウス進入時"""
        self.schedule_tooltip()
    
    def on_leave(self, event=None):
        """マウス離脱時"""
        self.cancel_tooltip()
        self.hide_tooltip()
    
    def on_motion(self, event=None):
        """マウス移動時"""
        self.cancel_tooltip()
        self.schedule_tooltip()
    
    def schedule_tooltip(self):
        """ツールチップ表示のスケジュール"""
        self.cancel_tooltip()
        self.timer_id = self.widget.after(self.delay, self.show_tooltip)
    
    def cancel_tooltip(self):
        """ツールチップ表示のキャンセル"""
        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
            self.timer_id = None
    
    def show_tooltip(self):
        """ツールチップの表示"""
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        
        if self.theme:
            bg_color = self.theme.colors['surface_popover']
            fg_color = self.theme.colors['text_primary']
            font_size = self.theme.typography['caption1']['size']
        else:
            bg_color = '#2A2A2E'
            fg_color = '#FFFFFF'
            font_size = 9
        
        label = tk.Label(
            tw,
            text=self.text,
            justify='left',
            background=bg_color,
            foreground=fg_color,
            relief='solid',
            borderwidth=1,
            font=('Arial', font_size, 'normal'),
            padx=8,
            pady=4
        )
        label.pack()
        
        tw.wm_geometry(f"+{x}+{y}")
    
    def hide_tooltip(self):
        """ツールチップの非表示"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# 使用例
def demo_components():
    """コンポーネントのデモ"""
    # テーマ設定
    theme_config = ThemeConfig(
        colors={
            'background_primary': '#0F0F10',
            'background_secondary': '#1A1A1C',
            'background_tertiary': '#252528',
            'background_elevated': '#2F2F33',
            'surface_card': '#1C1C1F',
            'surface_popover': '#2A2A2E',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B8B8B8',
            'text_disabled': '#505050',
            'accent_primary': '#5A9FFF',
            'accent_secondary': '#8B6FFF',
            'success': '#52E88C',
            'warning': '#FFD23F',
            'error': '#FF6B6B',
            'hover': '#2A2A2E'
        },
        typography={
            'caption1': {'size': 9},
            'body': {'size': 13},
            'headline': {'size': 14},
            'title3': {'size': 16}
        },
        spacing={
            'xs': 3, 'sm': 4, 'md': 5, 'lg': 6, 'xl': 8
        },
        radius={
            'small': 4, 'medium': 6, 'large': 8
        },
        layout={}
    )
    
    # デモウィンドウ
    root = tk.Tk()
    root.title("UI Components Demo")
    root.configure(bg=theme_config.colors['background_primary'])
    root.geometry("600x800")
    
    # ファクトリー作成
    factory = ComponentFactory(theme_config)
    
    # スクロール可能フレーム
    canvas = tk.Canvas(root, bg=theme_config.colors['background_primary'])
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=theme_config.colors['background_primary'])
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # コンポーネントのデモ
    
    # ボタンセクション
    button_card = factory.create_card(scrollable_frame, "ボタン")
    button_card.card_container.pack(fill='x', padx=10, pady=5)
    
    factory.create_button(
        button_card, "Primary Button", 
        style=ComponentStyle.PRIMARY, size=ComponentSize.MEDIUM
    ).pack(side='left', padx=5)
    
    factory.create_button(
        button_card, "Secondary", 
        style=ComponentStyle.SECONDARY, size=ComponentSize.SMALL
    ).pack(side='left', padx=5)
    
    factory.create_button(
        button_card, "Success", 
        style=ComponentStyle.SUCCESS, size=ComponentSize.LARGE
    ).pack(side='left', padx=5)
    
    # 入力フィールドセクション
    input_card = factory.create_card(scrollable_frame, "入力フィールド")
    input_card.card_container.pack(fill='x', padx=10, pady=5)
    
    input_var = tk.StringVar()
    factory.create_input(
        input_card, input_var, placeholder="ファイルパスを入力..."
    ).pack(fill='x', pady=2)
    
    # スライダーセクション
    slider_card = factory.create_card(scrollable_frame, "スライダー")
    slider_card.card_container.pack(fill='x', padx=10, pady=5)
    
    slider_var = tk.DoubleVar(value=0.5)
    factory.create_slider(
        slider_card, slider_var, 0, 1, "音量", show_value=True
    ).pack(fill='x', pady=2)
    
    # ドロップダウンセクション
    dropdown_card = factory.create_card(scrollable_frame, "ドロップダウン")
    dropdown_card.card_container.pack(fill='x', padx=10, pady=5)
    
    dropdown_var = tk.StringVar()
    factory.create_dropdown(
        dropdown_card, dropdown_var, ["rmvpe", "harvest", "crepe"]
    ).pack(fill='x', pady=2)
    
    # プログレスバーセクション
    progress_card = factory.create_card(scrollable_frame, "プログレスバー")
    progress_card.card_container.pack(fill='x', padx=10, pady=5)
    
    progress_bar = factory.create_progress_bar(progress_card)
    progress_bar.pack(fill='x', pady=2)
    
    # プログレスバーのテスト
    import threading
    import time
    
    def update_progress():
        for i in range(101):
            progress_bar.set_progress(i / 100.0)
            time.sleep(0.05)
            if i == 100:
                time.sleep(1)
                progress_bar.set_progress(0)
    
    threading.Thread(target=update_progress, daemon=True).start()
    
    # ツールチップのテスト
    test_button = factory.create_button(
        scrollable_frame, "ツールチップテスト",
        style=ComponentStyle.INFO
    )
    test_button.pack(padx=10, pady=10)
    factory.create_tooltip(test_button, "これはツールチップのテストです")
    
    # レイアウト
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    root.mainloop()

if __name__ == "__main__":
    demo_components()