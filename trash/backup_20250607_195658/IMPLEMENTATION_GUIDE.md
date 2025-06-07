# 開発効率化システム実装ガイド

## 概要

現在のシンプルな構成を維持しながら効率的に拡張・修正するための開発方針を実装しました。このガイドでは、提案された8つの主要な改善点に基づいて作成されたモジュール群の使用方法を説明します。

## 作成されたファイル一覧

### 1. `gui_dark_mode_improved.py`
- **目的**: 論理的にセクション分割され、整理された改善版GUI
- **改善点**:
  - 明確なセクション分割（定数、ヘルパー関数、初期化、UI構築、イベント処理、音声変換など）
  - 統一された命名規則
  - 共通処理の抽出
  - コメントブロックによる機能分離

### 2. `settings_manager.py`
- **目的**: 構造化されたJSON設定ファイル管理
- **機能**:
  - 階層的設定管理（ドット記法対応）
  - プリセット機能
  - 設定のインポート/エクスポート
  - 最近使用したファイルの管理
  - 設定マイグレーション

### 3. `error_handler.py`
- **目的**: 統一エラーハンドリングとロギングシステム
- **機能**:
  - 階層的エラー処理（UIレベル、処理レベル、システムレベル）
  - ログローテーション
  - クラッシュレポート生成
  - エラー統計
  - UIコールバック機能

### 4. `ui_components.py`
- **目的**: 再利用可能なUIコンポーネント・ファクトリーパターン
- **機能**:
  - 統一されたボタン、入力フィールド、ラベル、カード作成
  - カスタムスライダー、プログレスバー
  - ツールチップ機能
  - テーマ対応デザインシステム

### 5. `keyboard_shortcuts.py`
- **目的**: キーボードショートカット管理とツールチップ
- **機能**:
  - プラットフォーム対応ショートカット（macOS/Windows）
  - カテゴリー別ショートカット管理
  - ショートカット一覧ダイアログ
  - 設定のインポート/エクスポート

## 実装手順

### ステップ1: 既存システムとの統合

現在の`gui_dark_mode.py`を段階的に改善していく手順：

#### 1.1 設定管理の統合

```python
# 既存のコードに追加
from settings_manager import SettingsManager

class DarkModeGUI:
    def __init__(self, root):
        self.root = root
        
        # 設定管理システムの初期化
        self.settings = SettingsManager("gui_settings.json")
        
        # 設定からパラメータを読み込み
        self.pitch_var = tk.IntVar(value=self.settings.get('audio_settings.default_params.pitch', 0))
        self.f0_method_var = tk.StringVar(value=self.settings.get('audio_settings.default_params.f0_method', 'rmvpe'))
        # ...その他のパラメータ
```

#### 1.2 エラーハンドリングの統合

```python
# 既存のコードに追加
from error_handler import init_error_handler, log_info, log_error, ErrorCategory

class DarkModeGUI:
    def __init__(self, root):
        # エラーハンドラーの初期化
        self.error_handler = init_error_handler("logs")
        
        # UIコールバックの登録
        self.error_handler.register_ui_callback(
            ErrorLevel.ERROR, 
            self.show_error_in_ui
        )
        
        log_info("DarkModeGUI initialized")
    
    def show_error_in_ui(self, log_entry):
        """UIでエラーを表示"""
        self.log_message(log_entry['message'], "ERROR")
    
    def start_conversion(self):
        try:
            # 変換処理
            log_info("Conversion started")
        except Exception as e:
            log_error("Conversion failed", category=ErrorCategory.PROCESSING_ERROR, exception=e)
```

#### 1.3 UIコンポーネントの統合

```python
# 既存のコードに追加
from ui_components import ComponentFactory, ThemeConfig, ComponentStyle, ComponentSize

class DarkModeGUI:
    def __init__(self, root):
        # テーマ設定
        theme_config = ThemeConfig(
            colors=self.colors,
            typography=self.design_tokens['typography'],
            spacing=self.design_tokens['spacing'],
            radius=self.design_tokens['radius'],
            layout=self.design_tokens['layout']
        )
        
        # コンポーネントファクトリーの作成
        self.component_factory = ComponentFactory(theme_config)
    
    def create_conversion_button(self, parent):
        """ファクトリーを使ったボタン作成"""
        self.convert_button = self.component_factory.create_button(
            parent,
            text="音声変換を開始",
            command=self.start_conversion,
            style=ComponentStyle.PRIMARY,
            size=ComponentSize.LARGE
        )
        
        # ツールチップの追加
        self.component_factory.create_tooltip(
            self.convert_button,
            "選択した音声ファイルをAI音声変換します"
        )
        
        self.convert_button.pack()
```

#### 1.4 キーボードショートカットの統合

```python
# 既存のコードに追加
from keyboard_shortcuts import KeyboardShortcutManager

class DarkModeGUI:
    def __init__(self, root):
        # ショートカットマネージャーの初期化
        self.shortcut_manager = KeyboardShortcutManager(root)
        
        # コールバックの設定
        self.shortcut_manager.update_shortcut_callback("open_file", self.browse_input)
        self.shortcut_manager.update_shortcut_callback("save_settings", self.save_settings)
        self.shortcut_manager.update_shortcut_callback("start_conversion", self.start_conversion)
        self.shortcut_manager.update_shortcut_callback("clear_input", self.clear_input)
```

### ステップ2: プリセット機能の実装

```python
def create_preset_section(self, parent):
    """プリセット選択セクションの作成"""
    preset_card = self.component_factory.create_card(parent, "変換プリセット")
    
    # プリセット選択
    presets = self.settings.get('audio_settings.presets', [])
    preset_names = [p['name'] for p in presets]
    
    self.preset_var = tk.StringVar()
    preset_dropdown = self.component_factory.create_dropdown(
        preset_card,
        self.preset_var,
        preset_names
    )
    preset_dropdown.pack(fill='x', pady=2)
    preset_dropdown.bind('<<ComboboxSelected>>', self.on_preset_selected)
    
    # プリセット管理ボタン
    button_frame = tk.Frame(preset_card, bg=self.colors['surface_card'])
    button_frame.pack(fill='x', pady=(5, 0))
    
    self.component_factory.create_button(
        button_frame, "保存", self.save_current_preset,
        style=ComponentStyle.SECONDARY, size=ComponentSize.SMALL
    ).pack(side='left', padx=(0, 5))
    
    self.component_factory.create_button(
        button_frame, "削除", self.delete_current_preset,
        style=ComponentStyle.ERROR, size=ComponentSize.SMALL
    ).pack(side='left')

def on_preset_selected(self, event=None):
    """プリセット選択時の処理"""
    preset_name = self.preset_var.get()
    preset = self.settings.get_preset(preset_name)
    
    if preset:
        params = preset.get('params', {})
        self.pitch_var.set(params.get('pitch', 0))
        self.f0_method_var.set(params.get('f0_method', 'rmvpe'))
        self.index_rate_var.set(params.get('index_rate', 1.0))
        # ... その他のパラメータ
        
        log_info(f"Preset loaded: {preset_name}")

def save_current_preset(self):
    """現在の設定をプリセットとして保存"""
    # プリセット名の入力ダイアログ
    preset_name = tk.simpledialog.askstring(
        "プリセット保存",
        "プリセット名を入力してください:"
    )
    
    if preset_name:
        params = {
            'pitch': self.pitch_var.get(),
            'f0_method': self.f0_method_var.get(),
            'index_rate': self.index_rate_var.get(),
            'filter_radius': self.filter_radius_var.get(),
            'rms_mix_rate': self.rms_mix_rate_var.get(),
            'protect': self.protect_var.get()
        }
        
        if self.settings.add_preset(preset_name, "ユーザー作成", params):
            self.settings.save_settings()
            log_info(f"Preset saved: {preset_name}")
            messagebox.showinfo("成功", f"プリセット '{preset_name}' を保存しました")
        else:
            messagebox.showerror("エラー", "プリセットの保存に失敗しました")
```

### ステップ3: バッチ処理機能の実装

```python
def create_batch_processing_section(self, parent):
    """バッチ処理セクションの作成"""
    if not self.settings.get('advanced.experimental.enable_batch_processing', False):
        return
    
    batch_card = self.component_factory.create_card(parent, "バッチ処理")
    
    # ファイルリスト
    self.batch_files = []
    
    # ファイル追加ボタン
    self.component_factory.create_button(
        batch_card, "ファイル追加", self.add_batch_files,
        style=ComponentStyle.SECONDARY
    ).pack(pady=2)
    
    # ファイルリスト表示
    self.batch_listbox = tk.Listbox(
        batch_card,
        bg=self.colors['background_tertiary'],
        fg=self.colors['text_primary'],
        selectbackground=self.colors['accent_primary']
    )
    self.batch_listbox.pack(fill='both', expand=True, pady=2)
    
    # バッチ変換ボタン
    self.component_factory.create_button(
        batch_card, "バッチ変換開始", self.start_batch_conversion,
        style=ComponentStyle.PRIMARY
    ).pack(pady=2)

def add_batch_files(self):
    """バッチ処理用ファイルの追加"""
    files = filedialog.askopenfilenames(
        title="バッチ処理用ファイルを選択",
        filetypes=[("Audio files", "*.mp3 *.wav *.flac *.m4a *.ogg *.opus *.aac")]
    )
    
    for file_path in files:
        if file_path not in self.batch_files:
            self.batch_files.append(file_path)
            self.batch_listbox.insert('end', os.path.basename(file_path))
    
    log_info(f"Added {len(files)} files to batch queue")

def start_batch_conversion(self):
    """バッチ変換の開始"""
    if not self.batch_files:
        messagebox.showwarning("警告", "変換するファイルが選択されていません")
        return
    
    if not self.selected_model.get():
        messagebox.showwarning("警告", "音声モデルを選択してください")
        return
    
    # バッチ変換を別スレッドで実行
    thread = threading.Thread(target=self._run_batch_conversion)
    thread.daemon = True
    thread.start()

def _run_batch_conversion(self):
    """バッチ変換の実行"""
    total_files = len(self.batch_files)
    
    for i, input_file in enumerate(self.batch_files):
        try:
            log_info(f"Processing file {i+1}/{total_files}: {os.path.basename(input_file)}")
            
            # プログレス更新
            progress = i / total_files
            self.update_progress(0, progress, f"ファイル {i+1}/{total_files} を処理中...")
            
            # ファイル固有の出力パスを生成
            output_dir = self.output_var.get() or os.path.dirname(input_file)
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            model_name = os.path.splitext(os.path.basename(self.selected_model.get()))[0]
            output_file = os.path.join(output_dir, f"{base_name}_{model_name}_converted.wav")
            
            # 個別ファイルの変換実行
            self._convert_single_file(input_file, output_file)
            
        except Exception as e:
            log_error(f"Batch conversion failed for {input_file}", 
                     category=ErrorCategory.PROCESSING_ERROR, exception=e)
    
    # バッチ変換完了
    self.update_progress(5, 1.0, "バッチ変換が完了しました！")
    log_info("Batch conversion completed")
```

### ステップ4: 高度な機能の実装

#### 4.1 設定バックアップ・復元

```python
def create_settings_menu(self):
    """設定メニューの作成"""
    menubar = tk.Menu(self.root)
    self.root.config(menu=menubar)
    
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="設定", menu=settings_menu)
    
    settings_menu.add_command(label="設定をエクスポート", command=self.export_settings)
    settings_menu.add_command(label="設定をインポート", command=self.import_settings)
    settings_menu.add_separator()
    settings_menu.add_command(label="設定をリセット", command=self.reset_settings)

def export_settings(self):
    """設定のエクスポート"""
    file_path = filedialog.asksaveasfilename(
        title="設定ファイルを保存",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )
    
    if file_path:
        export_data = {
            "settings": self.settings.settings,
            "shortcuts": {}
        }
        
        # ショートカット設定も含める
        self.shortcut_manager.export_shortcuts(file_path + "_shortcuts.json")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", "設定をエクスポートしました")
            log_info(f"Settings exported to {file_path}")
        except Exception as e:
            log_error("Settings export failed", exception=e)
            messagebox.showerror("エラー", "設定のエクスポートに失敗しました")

def import_settings(self):
    """設定のインポート"""
    file_path = filedialog.askopenfilename(
        title="設定ファイルを選択",
        filetypes=[("JSON files", "*.json")]
    )
    
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 設定の復元
            if "settings" in import_data:
                self.settings.settings = import_data["settings"]
                self.settings.save_settings()
                
                # UIの更新
                self._update_ui_from_settings()
                
                messagebox.showinfo("成功", "設定をインポートしました")
                log_info(f"Settings imported from {file_path}")
                
        except Exception as e:
            log_error("Settings import failed", exception=e)
            messagebox.showerror("エラー", "設定のインポートに失敗しました")
```

## 使用上の注意点

### 1. 段階的導入

- 一度にすべての機能を導入せず、段階的に実装することを推奨
- まず設定管理システムから始めて、エラーハンドリング、UIコンポーネントの順で導入

### 2. 既存コードとの互換性

- 既存の`gui_dark_mode.py`の動作を維持しながら改善
- 新機能は無効にできるオプション設定を提供

### 3. パフォーマンス考慮

- UIレスポンシブネスを維持するため、重い処理は別スレッドで実行
- ログ出力頻度を調整して性能への影響を最小化

### 4. エラー処理

- 新機能でエラーが発生しても、既存機能に影響を与えないよう設計
- フォールバック機能を提供

## 今後の拡張指針

### 1. プラグインアーキテクチャ
- 音声処理エンジンを切り替え可能に
- サードパーティモデルの対応

### 2. クラウド連携
- 設定の同期
- オンラインモデルの利用

### 3. 高度なUI機能
- テーマカスタマイゼーション
- レイアウトの保存・復元
- ワークスペース機能

### 4. AI機能の強化
- 自動パラメータ調整
- 品質評価システム
- リアルタイム変換

## まとめ

この実装ガイドに従って段階的に機能を追加することで、現在のシンプルな構成を維持しながら、拡張性と保守性に優れたシステムに発展させることができます。各モジュールは独立性を保ちながら連携するよう設計されているため、必要に応じて個別に導入・カスタマイズが可能です。