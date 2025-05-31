"""
モデル選択コンポーネント
音声変換モデルの選択UI
"""
import tkinter as tk
from tkinter import ttk
import os
import json
try:
    from ..design_system import DesignTokens
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from design_system import DesignTokens


class ModelSelector(tk.Frame):
    """モデル選択コンポーネント"""
    
    def __init__(self, parent, model_dir, on_select=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.design_tokens = DesignTokens()
        self.colors = self.design_tokens.colors
        self.model_dir = model_dir
        self.on_select = on_select
        self.model_info = {}
        self.selected_model = tk.StringVar()
        self.model_cards = []
        
        self.configure(bg=self.colors['surface_sidebar'])
        self.create_widgets()
        self.load_models()
        
    def create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダー
        header = tk.Frame(self, bg=self.colors['surface_sidebar'])
        header.pack(fill=tk.X, padx=self.design_tokens.spacing['sm'], 
                   pady=self.design_tokens.spacing['sm'])
        
        # タイトルと設定ボタンの行
        title_row = tk.Frame(header, bg=self.colors['surface_sidebar'])
        title_row.pack(fill=tk.X)
        
        tk.Label(
            title_row, 
            text="Voice Models",
            font=('SF Pro Display', 16, 'bold'),
            bg=self.colors['surface_sidebar'],
            fg=self.colors['text_primary']
        ).pack(side=tk.LEFT)
        
        # 設定ボタン
        settings_btn = self.create_icon_button(
            title_row, "⚙", 
            self.open_settings
        )
        settings_btn.pack(side=tk.RIGHT)
        
        # サブタイトル
        tk.Label(
            header, 
            text="使用するモデルを選択",
            font=('SF Pro Display', 11),
            bg=self.colors['surface_sidebar'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w', pady=(2, 0))
        
        # 区切り線
        separator = tk.Frame(
            self, 
            bg=self.colors['divider'], 
            height=1
        )
        separator.pack(fill=tk.X, padx=self.design_tokens.spacing['sm'])
        
        # スクロール可能なモデルリスト
        self.create_scrollable_list()
        
    def create_scrollable_list(self):
        """スクロール可能なリストを作成"""
        # スクロールコンテナ
        scroll_container = tk.Frame(self, bg=self.colors['surface_sidebar'])
        scroll_container.pack(fill=tk.BOTH, expand=True, 
                             padx=self.design_tokens.spacing['xs'],
                             pady=self.design_tokens.spacing['xs'])
        
        # Canvas とスクロールバー
        self.canvas = tk.Canvas(
            scroll_container, 
            bg=self.colors['surface_sidebar'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            scroll_container, 
            orient="vertical", 
            command=self.canvas.yview,
            style='Dark.Vertical.TScrollbar'
        )
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # スクロール可能フレーム
        self.model_frame = tk.Frame(self.canvas, bg=self.colors['surface_sidebar'])
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.model_frame, 
            anchor="nw"
        )
        
        self.model_frame.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Canvas のサイズ変更時にフレーム幅を調整
        def configure_canvas(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
            
        self.canvas.bind('<Configure>', configure_canvas)
        
        # マウスホイールバインド
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def create_icon_button(self, parent, icon, command):
        """アイコンボタンを作成"""
        btn_frame = tk.Frame(parent, bg=parent['bg'])
        
        btn = tk.Label(
            btn_frame,
            text=icon,
            font=('SF Pro Display', 14),
            bg=self.colors['surface_sidebar'],
            fg=self.colors['text_secondary'],
            cursor='hand2',
            padx=4,
            pady=2
        )
        btn.pack()
        
        def on_enter(e):
            btn.config(bg=self.colors['hover'])
            
        def on_leave(e):
            btn.config(bg=self.colors['surface_sidebar'])
            
        def on_click(e):
            command()
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', on_click)
        
        return btn_frame
        
    def load_models(self):
        """モデルを読み込み"""
        # 既存のモデルカードをクリア
        for card_frame, inner, model in self.model_cards:
            card_frame.destroy()
        self.model_cards = []
        self.model_info = {}
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            return
            
        # モデルディレクトリから再帰的に検索
        models = self.search_models_recursive(self.model_dir)
        
        # 名前でソート
        models.sort(key=lambda x: x['name'].lower())
        
        # モデルカードを作成
        for i, model in enumerate(models):
            self.create_model_card(model, i)
            
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
        
    def create_model_card(self, model, index):
        """モデルカードUI"""
        card_frame = tk.Frame(
            self.model_frame,
            bg=self.colors['surface_card'],
            relief='flat'
        )
        card_frame.pack(fill=tk.X, padx=self.design_tokens.spacing['xs'], 
                       pady=self.design_tokens.spacing['xs'])
        
        # カード内部
        inner = tk.Frame(card_frame, bg=self.colors['surface_card'])
        inner.pack(fill=tk.BOTH, expand=True, 
                  padx=self.design_tokens.spacing['sm'],
                  pady=self.design_tokens.spacing['sm'])
        
        # モデル名
        name_label = tk.Label(
            inner,
            text=model['name'],
            font=('SF Pro Display', 12, 'bold'),
            bg=self.colors['surface_card'],
            fg=self.colors['text_primary'],
            anchor='w'
        )
        name_label.pack(fill=tk.X)
        
        # メタ情報
        meta_frame = tk.Frame(inner, bg=self.colors['surface_card'])
        meta_frame.pack(fill=tk.X, pady=(2, 0))
        
        # インデックスバッジ
        if model['has_index']:
            index_badge = tk.Label(
                meta_frame,
                text="✓ Index",
                font=('SF Pro Display', 9, 'bold'),
                bg=self.colors['success'],
                fg='white',
                padx=6,
                pady=2
            )
            index_badge.pack(side=tk.LEFT)
            
        # params.jsonから追加情報
        if model.get('params', {}).get('description'):
            desc_label = tk.Label(
                inner,
                text=model['params']['description'],
                font=('SF Pro Display', 10),
                bg=self.colors['surface_card'],
                fg=self.colors['text_secondary'],
                anchor='w',
                wraplength=180
            )
            desc_label.pack(fill=tk.X, pady=(2, 0))
            
        # 選択状態の視覚的フィードバック
        def update_selection():
            is_selected = self.selected_model.get() == model['name']
            if is_selected:
                card_frame.config(bg=self.colors['accent_primary'])
                inner.config(bg=self.colors['accent_primary'])
                name_label.config(bg=self.colors['accent_primary'], fg='white')
                if model.get('params', {}).get('description'):
                    desc_label.config(bg=self.colors['accent_primary'], fg='white')
                meta_frame.config(bg=self.colors['accent_primary'])
            else:
                card_frame.config(bg=self.colors['surface_card'])
                inner.config(bg=self.colors['surface_card'])
                name_label.config(bg=self.colors['surface_card'], fg=self.colors['text_primary'])
                if model.get('params', {}).get('description'):
                    desc_label.config(bg=self.colors['surface_card'], fg=self.colors['text_secondary'])
                meta_frame.config(bg=self.colors['surface_card'])
                
        # クリックイベント
        def on_click(event=None):
            self.selected_model.set(model['name'])
            self.model_info[model['name']] = model
            
            # すべてのカードの選択状態を更新
            for card, _, _ in self.model_cards:
                card.event_generate('<Configure>')
                
            if self.on_select:
                self.on_select(model['name'])
                
        # ホバーエフェクト
        def on_enter(e):
            if self.selected_model.get() != model['name']:
                card_frame.config(bg=self.colors['hover'])
                inner.config(bg=self.colors['hover'])
                name_label.config(bg=self.colors['hover'])
                if model.get('params', {}).get('description'):
                    desc_label.config(bg=self.colors['hover'])
                meta_frame.config(bg=self.colors['hover'])
                
        def on_leave(e):
            update_selection()
            
        # イベントバインド
        for widget in [card_frame, inner, name_label, meta_frame]:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Configure>', lambda e: update_selection())
            
        self.model_cards.append((card_frame, inner, model))
        
        # 最初のモデルを自動選択
        if index == 0 and not self.selected_model.get():
            on_click()
            
    def get_selected_model(self):
        """選択されたモデル情報を取得"""
        model_name = self.selected_model.get()
        return self.model_info.get(model_name)
        
    def open_settings(self):
        """設定ダイアログを開く（実装は親クラスで）"""
        # 親ウィジェットを辿ってopen_model_settingsメソッドを探す
        widget = self.master
        while widget:
            if hasattr(widget, 'open_model_settings'):
                widget.open_model_settings()
                return
            widget = getattr(widget, 'master', None)
        
        # 見つからない場合はエラーメッセージ
        print("Error: open_model_settings method not found in parent widgets")