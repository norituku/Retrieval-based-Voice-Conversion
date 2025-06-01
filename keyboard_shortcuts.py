#!/usr/bin/env python3
"""
キーボードショートカットシステム
統一されたキーボードショートカット管理とツールチップ機能
"""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, Callable, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import sys
import json
from pathlib import Path

class ShortcutModifier(Enum):
    """修飾キーの定義"""
    CTRL = "Control"
    CMD = "Command"  # macOS
    ALT = "Alt"
    SHIFT = "Shift"
    OPTION = "Option"  # macOS

class ShortcutCategory(Enum):
    """ショートカットカテゴリー"""
    FILE = "file"
    EDIT = "edit"
    VIEW = "view"
    CONVERSION = "conversion"
    NAVIGATION = "navigation"
    DEBUG = "debug"

@dataclass
class Shortcut:
    """ショートカット定義"""
    key: str
    modifiers: List[ShortcutModifier]
    callback: Callable
    description: str
    category: ShortcutCategory
    enabled: bool = True

class KeyboardShortcutManager:
    """キーボードショートカット管理システム"""
    
    def __init__(self, root: tk.Tk):
        """
        ショートカットマネージャーの初期化
        
        Args:
            root: ルートウィンドウ
        """
        self.root = root
        self.shortcuts: Dict[str, Shortcut] = {}
        self.key_bindings: Dict[str, str] = {}  # キーバインド文字列からショートカットIDへのマッピング
        
        # プラットフォーム固有の設定
        self.is_macos = sys.platform == 'darwin'
        self.primary_modifier = ShortcutModifier.CMD if self.is_macos else ShortcutModifier.CTRL
        
        # デフォルトショートカットの登録
        self._register_default_shortcuts()
        
        # グローバルキーハンドラーの設定
        self._setup_global_key_handler()
    
    def _register_default_shortcuts(self):
        """デフォルトショートカットの登録"""
        # ファイル操作
        self.register_shortcut(
            "open_file", "o", [self.primary_modifier],
            self._placeholder_callback, "ファイルを開く",
            ShortcutCategory.FILE
        )
        
        self.register_shortcut(
            "save_settings", "s", [self.primary_modifier],
            self._placeholder_callback, "設定を保存",
            ShortcutCategory.FILE
        )
        
        self.register_shortcut(
            "quit", "q", [self.primary_modifier],
            self._quit_application, "アプリケーションを終了",
            ShortcutCategory.FILE
        )
        
        # 変換操作
        self.register_shortcut(
            "start_conversion", "Return", [self.primary_modifier],
            self._placeholder_callback, "音声変換を開始",
            ShortcutCategory.CONVERSION
        )
        
        self.register_shortcut(
            "stop_conversion", "Escape", [],
            self._placeholder_callback, "変換を停止",
            ShortcutCategory.CONVERSION
        )
        
        # 編集操作
        self.register_shortcut(
            "clear_input", "Delete", [self.primary_modifier],
            self._placeholder_callback, "入力をクリア",
            ShortcutCategory.EDIT
        )
        
        self.register_shortcut(
            "reset_settings", "r", [self.primary_modifier, ShortcutModifier.SHIFT],
            self._placeholder_callback, "設定をリセット",
            ShortcutCategory.EDIT
        )
        
        # ナビゲーション
        self.register_shortcut(
            "next_model", "Tab", [],
            self._placeholder_callback, "次のモデルを選択",
            ShortcutCategory.NAVIGATION
        )
        
        self.register_shortcut(
            "previous_model", "Tab", [ShortcutModifier.SHIFT],
            self._placeholder_callback, "前のモデルを選択",
            ShortcutCategory.NAVIGATION
        )
        
        # ビュー操作
        self.register_shortcut(
            "toggle_advanced", "a", [self.primary_modifier],
            self._placeholder_callback, "高度な設定を切り替え",
            ShortcutCategory.VIEW
        )
        
        self.register_shortcut(
            "show_shortcuts", "question", [self.primary_modifier],
            self.show_shortcuts_dialog, "ショートカット一覧を表示",
            ShortcutCategory.VIEW
        )
        
        # デバッグ
        self.register_shortcut(
            "show_logs", "l", [self.primary_modifier, ShortcutModifier.SHIFT],
            self._placeholder_callback, "ログを表示",
            ShortcutCategory.DEBUG
        )
        
        self.register_shortcut(
            "reload_models", "F5", [],
            self._placeholder_callback, "モデルを再読み込み",
            ShortcutCategory.DEBUG
        )
    
    def register_shortcut(self, shortcut_id: str, key: str, 
                         modifiers: List[ShortcutModifier],
                         callback: Callable, description: str,
                         category: ShortcutCategory, enabled: bool = True):
        """
        ショートカットの登録
        
        Args:
            shortcut_id: ショートカットID
            key: キー
            modifiers: 修飾キー
            callback: コールバック関数
            description: 説明
            category: カテゴリー
            enabled: 有効/無効
        """
        shortcut = Shortcut(key, modifiers, callback, description, category, enabled)
        self.shortcuts[shortcut_id] = shortcut
        
        # キーバインド文字列を生成
        key_binding = self._create_key_binding_string(key, modifiers)
        self.key_bindings[key_binding] = shortcut_id
        
        # Tkinterにキーバインドを登録
        if enabled:
            self.root.bind_all(key_binding, lambda event, sid=shortcut_id: self._handle_shortcut(sid, event))
    
    def unregister_shortcut(self, shortcut_id: str):
        """
        ショートカットの登録解除
        
        Args:
            shortcut_id: ショートカットID
        """
        if shortcut_id in self.shortcuts:
            shortcut = self.shortcuts[shortcut_id]
            key_binding = self._create_key_binding_string(shortcut.key, shortcut.modifiers)
            
            # Tkinterのキーバインドを解除
            self.root.unbind_all(key_binding)
            
            # 内部データから削除
            del self.shortcuts[shortcut_id]
            if key_binding in self.key_bindings:
                del self.key_bindings[key_binding]
    
    def update_shortcut_callback(self, shortcut_id: str, callback: Callable):
        """
        ショートカットのコールバック更新
        
        Args:
            shortcut_id: ショートカットID
            callback: 新しいコールバック関数
        """
        if shortcut_id in self.shortcuts:
            self.shortcuts[shortcut_id].callback = callback
    
    def enable_shortcut(self, shortcut_id: str):
        """ショートカットの有効化"""
        if shortcut_id in self.shortcuts:
            shortcut = self.shortcuts[shortcut_id]
            if not shortcut.enabled:
                shortcut.enabled = True
                key_binding = self._create_key_binding_string(shortcut.key, shortcut.modifiers)
                self.root.bind_all(key_binding, lambda event, sid=shortcut_id: self._handle_shortcut(sid, event))
    
    def disable_shortcut(self, shortcut_id: str):
        """ショートカットの無効化"""
        if shortcut_id in self.shortcuts:
            shortcut = self.shortcuts[shortcut_id]
            if shortcut.enabled:
                shortcut.enabled = False
                key_binding = self._create_key_binding_string(shortcut.key, shortcut.modifiers)
                self.root.unbind_all(key_binding)
    
    def _create_key_binding_string(self, key: str, modifiers: List[ShortcutModifier]) -> str:
        """キーバインド文字列の生成"""
        modifier_strings = []
        
        for modifier in modifiers:
            if modifier == ShortcutModifier.CTRL:
                modifier_strings.append("Control")
            elif modifier == ShortcutModifier.CMD and self.is_macos:
                modifier_strings.append("Command")
            elif modifier == ShortcutModifier.CMD and not self.is_macos:
                modifier_strings.append("Control")  # WindowsではCtrlに変換
            elif modifier == ShortcutModifier.ALT:
                modifier_strings.append("Alt")
            elif modifier == ShortcutModifier.SHIFT:
                modifier_strings.append("Shift")
            elif modifier == ShortcutModifier.OPTION and self.is_macos:
                modifier_strings.append("Option")
        
        # キーバインド文字列の構築
        if modifier_strings:
            return f"<{'-'.join(modifier_strings)}-{key}>"
        else:
            return f"<{key}>"
    
    def _handle_shortcut(self, shortcut_id: str, event: tk.Event):
        """ショートカット処理"""
        if shortcut_id in self.shortcuts:
            shortcut = self.shortcuts[shortcut_id]
            if shortcut.enabled and shortcut.callback:
                try:
                    shortcut.callback()
                    return "break"  # イベントの伝播を停止
                except Exception as e:
                    messagebox.showerror("ショートカットエラー", f"ショートカット '{shortcut_id}' の実行中にエラーが発生しました:\n{str(e)}")
    
    def _setup_global_key_handler(self):
        """グローバルキーハンドラーの設定"""
        # 特殊キーの処理
        def handle_function_keys(event):
            # F1-F12キーの処理
            if event.keysym.startswith('F') and event.keysym[1:].isdigit():
                # F1はヘルプ、F5は更新など
                if event.keysym == 'F1':
                    self.show_shortcuts_dialog()
                    return "break"
        
        self.root.bind_all("<Key>", handle_function_keys)
    
    def show_shortcuts_dialog(self):
        """ショートカット一覧ダイアログの表示"""
        dialog = ShortcutDialog(self.root, self.shortcuts, self.is_macos)
        dialog.show()
    
    def get_shortcuts_by_category(self, category: ShortcutCategory) -> Dict[str, Shortcut]:
        """カテゴリー別ショートカット取得"""
        return {
            shortcut_id: shortcut 
            for shortcut_id, shortcut in self.shortcuts.items() 
            if shortcut.category == category
        }
    
    def get_shortcut_display_string(self, shortcut_id: str) -> str:
        """ショートカットの表示文字列取得"""
        if shortcut_id not in self.shortcuts:
            return ""
        
        shortcut = self.shortcuts[shortcut_id]
        modifier_strings = []
        
        for modifier in shortcut.modifiers:
            if modifier == ShortcutModifier.CTRL:
                modifier_strings.append("Ctrl" if not self.is_macos else "⌃")
            elif modifier == ShortcutModifier.CMD:
                modifier_strings.append("⌘" if self.is_macos else "Ctrl")
            elif modifier == ShortcutModifier.ALT:
                modifier_strings.append("Alt" if not self.is_macos else "⌥")
            elif modifier == ShortcutModifier.SHIFT:
                modifier_strings.append("Shift" if not self.is_macos else "⇧")
            elif modifier == ShortcutModifier.OPTION:
                modifier_strings.append("⌥" if self.is_macos else "Alt")
        
        # キー名の表示用変換
        key_display = shortcut.key
        key_mapping = {
            "Return": "Enter",
            "BackSpace": "Backspace",
            "Delete": "Del",
            "Escape": "Esc",
            "question": "?",
            "space": "Space"
        }
        
        if key_display in key_mapping:
            key_display = key_mapping[key_display]
        
        if modifier_strings:
            return f"{'+'.join(modifier_strings)}+{key_display}"
        else:
            return key_display
    
    def export_shortcuts(self, file_path: str) -> bool:
        """ショートカット設定のエクスポート"""
        try:
            export_data = {
                "version": "1.0.0",
                "platform": "macos" if self.is_macos else "windows",
                "shortcuts": {}
            }
            
            for shortcut_id, shortcut in self.shortcuts.items():
                export_data["shortcuts"][shortcut_id] = {
                    "key": shortcut.key,
                    "modifiers": [m.value for m in shortcut.modifiers],
                    "description": shortcut.description,
                    "category": shortcut.category.value,
                    "enabled": shortcut.enabled
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def import_shortcuts(self, file_path: str) -> bool:
        """ショートカット設定のインポート"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            shortcuts_data = import_data.get("shortcuts", {})
            
            for shortcut_id, data in shortcuts_data.items():
                if shortcut_id in self.shortcuts:
                    # 既存のショートカットのキーバインドを更新
                    modifiers = [ShortcutModifier(m) for m in data.get("modifiers", [])]
                    
                    # 一旦解除してから再登録
                    self.unregister_shortcut(shortcut_id)
                    
                    shortcut = self.shortcuts.get(shortcut_id)
                    if shortcut:
                        self.register_shortcut(
                            shortcut_id,
                            data.get("key", shortcut.key),
                            modifiers,
                            shortcut.callback,
                            data.get("description", shortcut.description),
                            ShortcutCategory(data.get("category", shortcut.category.value)),
                            data.get("enabled", True)
                        )
            
            return True
        except Exception:
            return False
    
    def _placeholder_callback(self):
        """プレースホルダーコールバック"""
        pass
    
    def _quit_application(self):
        """アプリケーション終了"""
        if messagebox.askokcancel("終了確認", "アプリケーションを終了しますか？"):
            self.root.quit()

class ShortcutDialog:
    """ショートカット一覧ダイアログ"""
    
    def __init__(self, parent: tk.Widget, shortcuts: Dict[str, Shortcut], is_macos: bool):
        self.parent = parent
        self.shortcuts = shortcuts
        self.is_macos = is_macos
        self.dialog = None
    
    def show(self):
        """ダイアログの表示"""
        if self.dialog:
            self.dialog.focus()
            return
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("キーボードショートカット")
        self.dialog.configure(bg='#1A1A1C')
        
        # ダイアログサイズと位置
        dialog_width = 600
        dialog_height = 500
        x = self.parent.winfo_x() + (self.parent.winfo_width() - dialog_width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # macOS用の設定
        if self.is_macos:
            try:
                self.dialog.tk.call('::tk::unsupported::MacWindowStyle', 'style', 
                                  self.dialog._w, 'dark', 'true')
            except:
                pass
        
        # コンテンツの作成
        self._create_content()
        
        # 終了時のクリーンアップ
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # モーダルダイアログにする
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # フォーカスを設定
        self.dialog.focus()
    
    def _create_content(self):
        """ダイアログコンテンツの作成"""
        # ヘッダー
        header_frame = tk.Frame(self.dialog, bg='#1A1A1C')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            header_frame,
            text="キーボードショートカット一覧",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1C',
            fg='#FFFFFF'
        )
        title_label.pack(anchor='w')
        
        # スクロール可能なコンテンツエリア
        content_frame = tk.Frame(self.dialog, bg='#1A1A1C')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Canvas とスクロールバー
        canvas = tk.Canvas(content_frame, bg='#1A1A1C', highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_content = tk.Frame(canvas, bg='#1A1A1C')
        
        scrollable_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # カテゴリー別にショートカットを表示
        categories = {}
        for shortcut_id, shortcut in self.shortcuts.items():
            category = shortcut.category
            if category not in categories:
                categories[category] = []
            categories[category].append((shortcut_id, shortcut))
        
        # カテゴリー名の日本語化
        category_names = {
            ShortcutCategory.FILE: "ファイル",
            ShortcutCategory.EDIT: "編集",
            ShortcutCategory.VIEW: "表示",
            ShortcutCategory.CONVERSION: "変換",
            ShortcutCategory.NAVIGATION: "ナビゲーション",
            ShortcutCategory.DEBUG: "デバッグ"
        }
        
        for category, shortcuts_list in categories.items():
            # カテゴリーヘッダー
            category_frame = tk.Frame(scrollable_content, bg='#252528')
            category_frame.pack(fill='x', pady=(10, 0))
            
            category_label = tk.Label(
                category_frame,
                text=category_names.get(category, category.value),
                font=('Arial', 14, 'bold'),
                bg='#252528',
                fg='#5A9FFF',
                padx=15,
                pady=8
            )
            category_label.pack(anchor='w')
            
            # ショートカット一覧
            for shortcut_id, shortcut in shortcuts_list:
                if shortcut.enabled:
                    self._create_shortcut_item(scrollable_content, shortcut_id, shortcut)
        
        # レイアウト
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 閉じるボタン
        button_frame = tk.Frame(self.dialog, bg='#1A1A1C')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        close_button = tk.Button(
            button_frame,
            text="閉じる",
            command=self._on_close,
            font=('Arial', 12),
            bg='#5A9FFF',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        close_button.pack(side='right')
    
    def _create_shortcut_item(self, parent: tk.Widget, shortcut_id: str, shortcut: Shortcut):
        """ショートカットアイテムの作成"""
        item_frame = tk.Frame(parent, bg='#1C1C1F')
        item_frame.pack(fill='x', padx=5, pady=2)
        
        # 左側: 説明
        desc_label = tk.Label(
            item_frame,
            text=shortcut.description,
            font=('Arial', 11),
            bg='#1C1C1F',
            fg='#FFFFFF',
            anchor='w'
        )
        desc_label.pack(side='left', fill='x', expand=True, padx=(15, 10), pady=8)
        
        # 右側: キーボードショートカット
        shortcut_display = self._get_shortcut_display_string(shortcut)
        shortcut_label = tk.Label(
            item_frame,
            text=shortcut_display,
            font=('Arial', 10, 'bold'),
            bg='#2F2F33',
            fg='#B8B8B8',
            padx=8,
            pady=4,
            relief='solid',
            bd=1
        )
        shortcut_label.pack(side='right', padx=(10, 15), pady=8)
    
    def _get_shortcut_display_string(self, shortcut: Shortcut) -> str:
        """ショートカットの表示文字列を取得"""
        modifier_strings = []
        
        for modifier in shortcut.modifiers:
            if modifier == ShortcutModifier.CTRL:
                modifier_strings.append("Ctrl" if not self.is_macos else "⌃")
            elif modifier == ShortcutModifier.CMD:
                modifier_strings.append("⌘" if self.is_macos else "Ctrl")
            elif modifier == ShortcutModifier.ALT:
                modifier_strings.append("Alt" if not self.is_macos else "⌥")
            elif modifier == ShortcutModifier.SHIFT:
                modifier_strings.append("Shift" if not self.is_macos else "⇧")
            elif modifier == ShortcutModifier.OPTION:
                modifier_strings.append("⌥" if self.is_macos else "Alt")
        
        # キー名の変換
        key_display = shortcut.key
        key_mapping = {
            "Return": "Enter",
            "BackSpace": "Backspace",
            "Delete": "Del",
            "Escape": "Esc",
            "question": "?",
            "space": "Space"
        }
        
        if key_display in key_mapping:
            key_display = key_mapping[key_display]
        
        if modifier_strings:
            return f"{' + '.join(modifier_strings)} + {key_display}"
        else:
            return key_display
    
    def _on_close(self):
        """ダイアログクローズ時の処理"""
        self.dialog.grab_release()
        self.dialog.destroy()
        self.dialog = None

# 使用例とテスト
def demo_shortcuts():
    """キーボードショートカットのデモ"""
    root = tk.Tk()
    root.title("Keyboard Shortcuts Demo")
    root.configure(bg='#1A1A1C')
    root.geometry("400x300")
    
    # ショートカットマネージャーの作成
    shortcut_manager = KeyboardShortcutManager(root)
    
    # テスト用のコールバック関数
    def test_open_file():
        messagebox.showinfo("テスト", "ファイルを開く機能が呼び出されました")
    
    def test_save_settings():
        messagebox.showinfo("テスト", "設定保存機能が呼び出されました")
    
    def test_start_conversion():
        messagebox.showinfo("テスト", "音声変換が開始されました")
    
    # コールバックの更新
    shortcut_manager.update_shortcut_callback("open_file", test_open_file)
    shortcut_manager.update_shortcut_callback("save_settings", test_save_settings)
    shortcut_manager.update_shortcut_callback("start_conversion", test_start_conversion)
    
    # UI作成
    info_label = tk.Label(
        root,
        text="キーボードショートカットのテスト\n\n"
             "Cmd+O (Ctrl+O): ファイルを開く\n"
             "Cmd+S (Ctrl+S): 設定を保存\n"
             "Cmd+Enter: 変換開始\n"
             "Cmd+? (Ctrl+?): ショートカット一覧\n"
             "Cmd+Q (Ctrl+Q): 終了",
        font=('Arial', 12),
        bg='#1A1A1C',
        fg='#FFFFFF',
        justify='left'
    )
    info_label.pack(padx=20, pady=20)
    
    # ショートカット一覧表示ボタン
    shortcuts_button = tk.Button(
        root,
        text="ショートカット一覧を表示",
        command=shortcut_manager.show_shortcuts_dialog,
        font=('Arial', 12),
        bg='#5A9FFF',
        fg='white',
        relief='flat',
        padx=20,
        pady=10,
        cursor='hand2'
    )
    shortcuts_button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    demo_shortcuts()