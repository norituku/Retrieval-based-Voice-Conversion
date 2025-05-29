"""
リファクタリング済みメインGUIアプリケーション
モジュール化されたコンポーネントを使用
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import json
import subprocess
from datetime import datetime

# パッケージのルートを取得
package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

try:
    # 相対インポート
    from .design_system import DesignTokens
    from .components import ProgressBar, FileSelector, ModelSelector
    from .managers import RVCManager
except ImportError:
    # 絶対インポート（モジュールとして実行される場合）
    from gui.design_system import DesignTokens
    from gui.components import ProgressBar, FileSelector, ModelSelector
    from gui.managers import RVCManager


class DarkModeGUI:
    """リファクタリング済みダークモードGUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Converter")
        
        # デザインシステム
        self.design_tokens = DesignTokens()
        self.colors = self.design_tokens.colors
        
        # 変数の初期化（setup_app_directories()より前に実行）
        self.model_info = {}
        self.selected_model = tk.StringVar()
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.output_filename_var = tk.StringVar()
        self.model_dir_var = tk.StringVar()
        self.pitch_var = tk.IntVar(value=0)
        
        # アプリケーション設定
        self.setup_app_directories()
        
        # 高品質パラメータ
        self.f0_method_var = tk.StringVar(value="rmvpe")
        self.index_rate_var = tk.DoubleVar(value=1.0)
        self.filter_radius_var = tk.IntVar(value=7)
        self.rms_mix_rate_var = tk.DoubleVar(value=0.0)
        self.protect_var = tk.DoubleVar(value=0.33)
        
        # RVCマネージャー
        self.rvc_manager = RVCManager(
            self.base_dir,
            self.model_dir_var.get() or os.path.join(self.base_dir, "model_dir")
        )
        
        # カスタムスタイル設定
        self.setup_styles()
        
        # ウィンドウ設定
        self.setup_window()
        
        # UI構築
        self.create_ui()
        
        # 初期化完了ログ
        self.log_message("Voice Converter Ready.", "INFO")
        
    def setup_app_directories(self):
        """アプリケーションディレクトリの設定"""
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            if exe_dir.endswith('/MacOS'):
                self.base_dir = os.path.join(os.path.dirname(exe_dir), 'Resources')
            else:
                self.base_dir = exe_dir
        else:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # 設定ファイルの読み込み
        self.settings_file = os.path.join(self.base_dir, "gui_settings.json")
        self.load_settings()
        
        # デフォルトのモデルディレクトリ
        default_model_dir = os.path.join(self.base_dir, "model_dir")
        if not self.model_dir_var.get():
            self.model_dir_var.set(default_model_dir)
            
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
        style.theme_use('default')
        
        # スクロールバー
        style.configure('Dark.Vertical.TScrollbar',
                       background=self.colors['background_secondary'],
                       darkcolor=self.colors['background_tertiary'],
                       lightcolor=self.colors['background_tertiary'],
                       troughcolor=self.colors['background_primary'],
                       bordercolor=self.colors['background_primary'],
                       arrowcolor=self.colors['text_tertiary'],
                       relief='flat',
                       width=10)
        
        # プログレスバー
        style.configure('Dark.Horizontal.TProgressbar',
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['background_tertiary'],
                       bordercolor=self.colors['background_tertiary'],
                       lightcolor=self.colors['accent_primary'],
                       darkcolor=self.colors['accent_primary'],
                       thickness=6)
                       
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.configure(bg=self.colors['background_primary'])
        
        # 画面サイズを取得
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # ウィンドウサイズを画面サイズに応じて調整
        window_width = min(self.design_tokens.layout['min_window_width'], int(screen_width * 0.9))
        window_height = min(650, int(screen_height * 0.85))
        
        # 画面中央に配置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(850, 480)
        
        # macOS用の設定
        if sys.platform == "darwin":
            try:
                self.root.tk.call('::tk::unsupported::MacWindowStyle', 'style', self.root._w, 'dark')
            except:
                pass
                
    def create_ui(self):
        """UI構築"""
        # ナビゲーションバー
        self.create_navigation_bar()
        
        # メインコンテンツエリア
        self.main_content = tk.Frame(self.root, bg=self.colors['background_primary'])
        self.main_content.pack(fill=tk.BOTH, expand=True)
        
        # 2カラムレイアウト
        self.create_two_column_layout()
        
    def create_navigation_bar(self):
        """ナビゲーションバー"""
        nav_bar = tk.Frame(self.root, bg=self.colors['background_secondary'], height=40)
        nav_bar.pack(fill=tk.X)
        nav_bar.pack_propagate(False)
        
        # 左側：ロゴとタイトル
        left_frame = tk.Frame(nav_bar, bg=self.colors['background_secondary'])
        left_frame.pack(side=tk.LEFT, padx=self.design_tokens.spacing['md'])
        
        # アプリアイコン
        icon_canvas = tk.Canvas(left_frame, width=24, height=24, 
                               bg=self.colors['background_secondary'], 
                               highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, pady=8)
        
        # グラデーション風アイコン
        icon_canvas.create_oval(2, 2, 22, 22, 
                              fill=self.colors['accent_primary'], 
                              outline='')
        icon_canvas.create_oval(4, 4, 20, 20, 
                              fill=self.colors['accent_secondary'], 
                              outline='')
        icon_canvas.create_text(12, 12, text="♪", 
                              fill="white", 
                              font=("Arial", 14, "bold"))
        
        # タイトル
        title_label = tk.Label(left_frame, text="Voice Converter",
                              font=('SF Pro Display', 15, 'bold'),
                              bg=self.colors['background_secondary'],
                              fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=self.design_tokens.spacing['sm'])
        
    def create_two_column_layout(self):
        """2カラムレイアウト"""
        # 左カラム（サイドバー）
        self.left_column = tk.Frame(self.main_content, 
                                   bg=self.colors['surface_sidebar'],
                                   width=self.design_tokens.layout['sidebar_width'])
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.left_column.pack_propagate(False)
        
        # 右カラム（メインコンテンツ）
        self.right_column = tk.Frame(self.main_content, 
                                    bg=self.colors['background_primary'])
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # サイドバー：モデル選択
        self.model_selector = ModelSelector(
            self.left_column,
            self.model_dir_var.get(),
            on_select=self.on_model_selected
        )
        self.model_selector.pack(fill=tk.BOTH, expand=True)
        
        # メインコンテンツ
        self.create_main_content()
        
    def create_main_content(self):
        """メインコンテンツエリア"""
        content_container = tk.Frame(self.right_column, bg=self.colors['background_primary'])
        content_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        
        # タイトルセクション
        self.create_title_section(content_container)
        
        # 入力セクション
        self.create_input_section(content_container)
        
        # 設定セクション
        self.create_settings_section(content_container)
        
        # ステータス・ログセクション
        self.create_status_section(content_container)
        
    def create_title_section(self, parent):
        """タイトルセクション"""
        title_frame = tk.Frame(parent, bg=self.colors['background_primary'])
        title_frame.pack(fill=tk.X, pady=(0, self.design_tokens.spacing['xs']))
        
        tk.Label(title_frame, text="Voice Converter - AI Voice Conversion",
                font=('SF Pro Display', 16, 'bold'),
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(anchor='center')
                
    def create_input_section(self, parent):
        """入力セクション"""
        input_card = self.create_card(parent, "Input & Convert")
        
        # 横並びレイアウト
        horizontal_layout = tk.Frame(input_card, bg=self.colors['surface_card'])
        horizontal_layout.pack(fill=tk.X)
        
        # 左側：ファイル選択
        left_section = tk.Frame(horizontal_layout, bg=self.colors['surface_card'])
        left_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                         padx=(0, self.design_tokens.spacing['xs']))
        
        self.input_selector = FileSelector(
            left_section,
            title="Input Audio",
            file_type="input",
            on_select=self.on_input_selected
        )
        self.input_selector.pack(fill=tk.X)
        
        # 右側：変換ボタン
        right_section = tk.Frame(horizontal_layout, bg=self.colors['surface_card'])
        right_section.pack(side=tk.RIGHT, padx=(self.design_tokens.spacing['xs'], 0))
        
        convert_btn = self.create_button(right_section, 
                                       "Start\nConversion", 
                                       self.start_conversion,
                                       style='Primary',
                                       width=120,
                                       height=50)
        convert_btn.pack()
        
    def create_settings_section(self, parent):
        """設定セクション"""
        settings_card = self.create_card(parent, "Settings")
        
        # 2カラムグリッドレイアウト
        grid_container = tk.Frame(settings_card, bg=self.colors['surface_card'])
        grid_container.pack(fill=tk.X)
        
        # 左カラム：出力設定
        left_column = tk.Frame(grid_container, bg=self.colors['surface_card'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                        padx=(0, self.design_tokens.spacing['xs']))
        
        self.output_selector = FileSelector(
            left_column,
            title="Output Directory",
            file_type="output",
            on_select=self.on_output_selected
        )
        self.output_selector.pack(fill=tk.X)
        
        # 出力ファイル名プレビュー
        self.output_preview_label = tk.Label(
            left_column,
            text="",
            font=('SF Pro Mono', 9),
            bg=self.colors['surface_card'],
            fg=self.colors['text_tertiary']
        )
        self.output_preview_label.pack(anchor='w', pady=(2, 0))
        
        # 右カラム：ピッチ設定
        right_column = tk.Frame(grid_container, bg=self.colors['surface_card'])
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, 
                         padx=(self.design_tokens.spacing['xs'], 0))
        
        self.create_compact_setting_control(right_column, "Pitch", self.pitch_var, 
                                          -12, 12, 0, "semitones")
        
    def create_status_section(self, parent):
        """ステータスセクション"""
        # プログレスバー
        self.progress_bar = ProgressBar(parent)
        
        # ログセクション
        log_card = self.create_card(parent, "Console", fill_expand=True)
        
        log_frame = tk.Frame(log_card, bg=self.colors['background_tertiary'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_frame, style='Dark.Vertical.TScrollbar')
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame,
                               wrap=tk.WORD,
                               height=6,
                               bg=self.colors['background_tertiary'],
                               fg=self.colors['text_secondary'],
                               font=(self.design_tokens.fonts['mono'], 9),
                               relief=tk.FLAT,
                               padx=8,
                               pady=6,
                               yscrollcommand=log_scrollbar.set,
                               selectbackground=self.colors['accent_primary'],
                               selectforeground=self.colors['text_primary'])
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        log_scrollbar.config(command=self.log_text.yview)
        
    def create_card(self, parent, title, visible=True, fill_expand=False):
        """カードUI要素を作成"""
        card = tk.Frame(parent, 
                       bg=self.colors['surface_card'],
                       relief='flat')
        if visible:
            if fill_expand:
                card.pack(fill=tk.BOTH, expand=True, 
                         pady=(0, self.design_tokens.spacing['sm']))
            else:
                card.pack(fill=tk.X, pady=(0, self.design_tokens.spacing['sm']))
        
        inner = tk.Frame(card, bg=self.colors['surface_card'])
        inner.pack(fill=tk.BOTH, expand=True, 
                  padx=self.design_tokens.spacing['sm'],
                  pady=self.design_tokens.spacing['sm'])
        
        if title:
            title_label = tk.Label(inner, text=title,
                                 font=('SF Pro Display', 12, 'bold'),
                                 bg=self.colors['surface_card'],
                                 fg=self.colors['text_primary'])
            title_label.pack(anchor='w', pady=(0, self.design_tokens.spacing['xs']))
            
            separator = tk.Frame(inner, 
                               bg=self.colors['divider'], 
                               height=1)
            separator.pack(fill=tk.X, pady=(0, self.design_tokens.spacing['xs']))
        
        return inner
        
    def create_button(self, parent, text, command, style='Primary', width=None, height=None):
        """カスタムボタンを作成"""
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
        
        if width and height:
            btn.config(padx=12, pady=6)
            btn_frame.config(width=width, height=height)
            btn_frame.pack_propagate(False)
        else:
            btn.config(padx=self.design_tokens.spacing['md'],
                      pady=self.design_tokens.spacing['xs'])
            
        btn.pack(fill=tk.BOTH, expand=True)
        
        # ホバーエフェクト
        def on_enter(e):
            btn.config(bg=hover_color)
            
        def on_leave(e):
            btn.config(bg=bg_color)
            
        def on_click(e):
            btn.config(bg=active_color)
            btn.after(100, lambda: btn.config(bg=bg_color))
            command()
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', on_click)
        
        return btn_frame
        
    def create_compact_setting_control(self, parent, label, variable, min_val, max_val, row, unit=""):
        """コンパクトな設定コントロール"""
        control_frame = tk.Frame(parent, bg=self.colors['surface_card'])
        control_frame.pack(fill=tk.X)
        
        header_frame = tk.Frame(control_frame, bg=self.colors['surface_card'])
        header_frame.pack(fill=tk.X)
        
        label_text = tk.Label(header_frame, text=label,
                            font=('SF Pro Display', 11, 'bold'),
                            bg=self.colors['surface_card'],
                            fg=self.colors['text_secondary'])
        label_text.pack(side=tk.LEFT)
        
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
        
        # スライダー
        slider_frame = tk.Frame(control_frame, bg=self.colors['surface_card'])
        slider_frame.pack(fill=tk.X, pady=(2, 0))
        
        if isinstance(variable, tk.DoubleVar):
            resolution = 0.01 if max_val <= 1 else 0.1
        else:
            resolution = 1
            
        slider = tk.Scale(slider_frame,
                         from_=min_val,
                         to=max_val,
                         orient=tk.HORIZONTAL,
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
        
        def update_value_label(*args):
            value_label.config(text=format_value())
        
        variable.trace('w', update_value_label)
        
    def on_model_selected(self, model_name):
        """モデル選択時の処理"""
        self.selected_model.set(model_name)
        self.log_message(f"Selected model: {model_name}", "INFO")
        self.update_output_preview()
        
    def on_input_selected(self, file_path):
        """入力ファイル選択時の処理"""
        self.input_var.set(file_path)
        self.log_message(f"Selected input: {os.path.basename(file_path)}", "INFO")
        
        # デフォルト出力ディレクトリを設定
        default_output = os.path.join(os.path.dirname(file_path), "VoiceConverter_Output")
        self.output_selector.set_path(default_output)
        self.output_var.set(default_output)
        self.update_output_preview()
        
    def on_output_selected(self, directory):
        """出力ディレクトリ選択時の処理"""
        self.output_var.set(directory)
        self.log_message(f"Output directory: {directory}", "INFO")
        
    def update_output_preview(self):
        """出力ファイル名のプレビューを更新"""
        if not hasattr(self, 'output_preview_label'):
            return
            
        if self.input_var.get() and self.selected_model.get():
            try:
                selected_model = self.model_selector.get_selected_model()
                if selected_model:
                    preview_filename = self.rvc_manager.generate_output_filename(
                        self.input_var.get(),
                        selected_model['name'],
                        self.output_filename_var.get() or None
                    )
                    self.output_preview_label.config(
                        text=f"Output: {preview_filename}",
                        fg=self.colors['text_primary']
                    )
                else:
                    self.output_preview_label.config(
                        text="[Select model first]",
                        fg=self.colors['text_tertiary']
                    )
            except Exception as e:
                self.output_preview_label.config(
                    text=f"Error: {str(e)}",
                    fg=self.colors['error']
                )
        else:
            self.output_preview_label.config(
                text="[Select input file and model first]",
                fg=self.colors['text_tertiary']
            )
        
    def start_conversion(self):
        """音声変換を開始"""
        # 入力チェック
        if not self.input_var.get():
            messagebox.showwarning("Warning", "Please select an input audio file.")
            return
            
        selected_model = self.model_selector.get_selected_model()
        if not selected_model:
            messagebox.showwarning("Warning", "Please select a voice model.")
            return
            
        # 出力ディレクトリ作成
        os.makedirs(self.output_var.get(), exist_ok=True)
        
        # 出力ファイル名生成
        output_filename = self.rvc_manager.generate_output_filename(
            self.input_var.get(),
            selected_model['name'],
            self.output_filename_var.get() or None
        )
        output_path = os.path.join(self.output_var.get(), output_filename)
        
        # 変換開始
        self.log_message("Starting conversion...", "INFO")
        
        def progress_callback(stage, progress, message):
            log_msg = self.progress_bar.update_progress(stage, progress, message)
            self.log_message_raw(log_msg)
            
        # RVCマネージャーで変換実行
        thread = self.rvc_manager.run_with_progress(
            selected_model,
            self.input_var.get(),
            output_path,
            progress_callback=progress_callback,
            pitch=self.pitch_var.get(),
            f0method=self.f0_method_var.get(),
            index_rate=self.index_rate_var.get(),
            filter_radius=self.filter_radius_var.get(),
            rms_mix_rate=self.rms_mix_rate_var.get(),
            protect=self.protect_var.get()
        )
        
        def check_completion():
            if thread.is_alive():
                self.root.after(100, check_completion)
            else:
                # 変換完了処理
                if os.path.exists(output_path):
                    self.log_message(f"Conversion completed: {output_filename}", "SUCCESS")
                    messagebox.showinfo("Success", 
                        f"Voice conversion completed!\n\nOutput: {output_filename}")
                    
                    # macOSの場合、Finderで表示するか確認
                    if sys.platform == "darwin":
                        result_open = messagebox.askyesno(
                            "Open File",
                            "Would you like to open the output file in Finder?"
                        )
                        if result_open:
                            subprocess.run(["open", "-R", output_path])
                else:
                    self.log_message("Conversion failed", "ERROR")
                    messagebox.showerror("Error", "Conversion failed")
                    
                # UIリセット
                self.root.after(1000, lambda: self.progress_bar.reset())
                
        check_completion()
        
    def open_model_settings(self):
        """モデル設定ダイアログを開く"""
        # 簡素化された設定ダイアログ
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Model Settings")
        settings_window.geometry("400x150")
        settings_window.configure(bg=self.colors['background_primary'])
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 中央配置
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() - settings_window.winfo_width()) // 2
        y = (settings_window.winfo_screenheight() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{x}+{y}")
        
        messagebox.showinfo("Info", "Model settings functionality will be implemented in the next iteration.")
        settings_window.destroy()
        
    def log_message(self, message, level="INFO"):
        """ログメッセージを追加"""
        if not hasattr(self, 'log_text'):
            print(f"[{level}] {message}")
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
    def log_message_raw(self, message):
        """生ログメッセージを追加（タイムスタンプなし）"""
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)


def main():
    """メイン関数"""
    # macOS警告を抑制
    if sys.platform == "darwin":
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
    
    root = tk.Tk()
    app = DarkModeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()