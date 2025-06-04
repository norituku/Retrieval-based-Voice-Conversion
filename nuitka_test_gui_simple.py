#!/usr/bin/env python3
"""
Nuitka GUI互換性テスト（依存関係なし版）
純粋なtkinterとシステム情報のみの軽量GUIテスト
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
import platform
from pathlib import Path

def test_system_info():
    """システム情報の収集"""
    return {
        'Python Version': sys.version,
        'Platform': platform.platform(),
        'Architecture': platform.machine(),
        'Executable Path': sys.executable,
        'Current Directory': os.getcwd(),
        'macOS Version': platform.mac_ver()[0] if sys.platform == 'darwin' else 'N/A'
    }

class SimpleNuitkaGUI:
    """シンプルなNuitka GUI テストアプリ"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧪 Nuitka GUI互換性テスト")
        self.root.geometry("700x500")
        
        # ダークモード風の色設定
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'button_bg': '#404040',
            'entry_bg': '#404040',
            'success': '#4CAF50',
            'error': '#f44336',
            'warning': '#ff9800'
        }
        
        self.setup_ui()
        self.load_system_info()
    
    def setup_ui(self):
        """UI のセットアップ"""
        # メインフレーム
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タイトル
        title_label = tk.Label(main_frame, 
                              text="🧪 Nuitka GUI互換性テスト",
                              font=('Arial', 18, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['fg'])
        title_label.pack(pady=(0, 20))
        
        # システム情報セクション
        info_frame = tk.LabelFrame(main_frame, 
                                  text="システム情報",
                                  font=('Arial', 12, 'bold'),
                                  bg=self.colors['bg'],
                                  fg=self.colors['fg'])
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, 
                                height=15,
                                bg=self.colors['entry_bg'],
                                fg=self.colors['fg'],
                                font=('Courier', 10))
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X)
        
        # ファイルダイアログテストボタン
        file_btn = tk.Button(button_frame,
                            text="📁 ファイルダイアログテスト",
                            command=self.test_file_dialog,
                            bg=self.colors['button_bg'],
                            fg=self.colors['fg'],
                            font=('Arial', 10),
                            padx=20)
        file_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # メッセージボックステストボタン
        msg_btn = tk.Button(button_frame,
                           text="💬 メッセージボックステスト",
                           command=self.test_message_box,
                           bg=self.colors['button_bg'],
                           fg=self.colors['fg'],
                           font=('Arial', 10),
                           padx=20)
        msg_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 終了ボタン
        quit_btn = tk.Button(button_frame,
                            text="❌ 終了",
                            command=self.root.quit,
                            bg=self.colors['error'],
                            fg=self.colors['fg'],
                            font=('Arial', 10),
                            padx=20)
        quit_btn.pack(side=tk.RIGHT)
    
    def load_system_info(self):
        """システム情報の読み込みと表示"""
        self.info_text.delete(1.0, tk.END)
        
        # Nuitka検証結果
        self.info_text.insert(tk.END, "🎯 Nuitka GUI テスト結果\n")
        self.info_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # システム情報
        self.info_text.insert(tk.END, "🖥️ システム情報:\n")
        system_info = test_system_info()
        for key, value in system_info.items():
            self.info_text.insert(tk.END, f"  {key}:\n    {value}\n\n")
        
        # Nuitka固有情報
        self.info_text.insert(tk.END, "🔧 Nuitka固有情報:\n")
        
        # 実行可能ファイルのパス分析
        exe_path = sys.executable
        if "nuitka" in exe_path.lower() or "dist" in exe_path:
            self.info_text.insert(tk.END, "  ✅ Nuitkaでビルドされたバイナリで実行中\n")
        else:
            self.info_text.insert(tk.END, "  ⚠️ 通常のPythonインタープリターで実行中\n")
        
        self.info_text.insert(tk.END, f"  実行パス: {exe_path}\n\n")
        
        # tkinter テスト
        self.info_text.insert(tk.END, "🎨 GUI フレームワークテスト:\n")
        try:
            # tkinter基本機能テスト
            test_window = tk.Toplevel()
            test_window.withdraw()  # 非表示
            test_window.destroy()
            self.info_text.insert(tk.END, "  ✅ tkinter基本機能: OK\n")
            
            # ttk テスト
            test_widget = ttk.Label(self.root, text="test")
            test_widget.destroy()
            self.info_text.insert(tk.END, "  ✅ ttk ウィジェット: OK\n")
            
        except Exception as e:
            self.info_text.insert(tk.END, f"  ❌ GUI テストエラー: {e}\n")
        
        # ファイルシステムテスト
        self.info_text.insert(tk.END, "\n📁 ファイルシステムテスト:\n")
        try:
            # 現在のディレクトリの読み取り
            current_dir = Path.cwd()
            file_count = len(list(current_dir.iterdir()))
            self.info_text.insert(tk.END, f"  ✅ ディレクトリ読み取り: {file_count} ファイル\n")
            
            # 一時ファイルの作成
            import tempfile
            with tempfile.NamedTemporaryFile() as tmp:
                self.info_text.insert(tk.END, f"  ✅ 一時ファイル作成: OK\n")
                
        except Exception as e:
            self.info_text.insert(tk.END, f"  ❌ ファイルシステムエラー: {e}\n")
        
        self.info_text.insert(tk.END, "\n🎉 Nuitka GUI互換性テスト完了!")
    
    def test_file_dialog(self):
        """ファイルダイアログのテスト"""
        try:
            filename = filedialog.askopenfilename(
                title="Nuitka ファイルダイアログテスト",
                filetypes=[
                    ("テキストファイル", "*.txt *.py *.md"),
                    ("全てのファイル", "*.*")
                ]
            )
            
            if filename:
                file_path = Path(filename)
                size = file_path.stat().st_size
                messagebox.showinfo("成功", 
                    f"ファイルが選択されました:\n"
                    f"ファイル: {file_path.name}\n"
                    f"サイズ: {size:,} bytes\n"
                    f"パス: {filename}")
            else:
                messagebox.showinfo("キャンセル", "ファイル選択がキャンセルされました")
                
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルダイアログエラー:\n{e}")
    
    def test_message_box(self):
        """メッセージボックスのテスト"""
        try:
            # 確認ダイアログ
            result = messagebox.askyesno("確認", "Nuitkaでビルドされたアプリケーションは正常に動作していますか？")
            
            if result:
                messagebox.showinfo("素晴らしい！", 
                    "🎉 Nuitka GUI ビルドが成功しました！\n\n"
                    "これで以下が確認できました:\n"
                    "✅ tkinter GUI の動作\n"
                    "✅ ファイルダイアログ\n"
                    "✅ メッセージボックス\n"
                    "✅ システム情報取得\n\n"
                    "次のステップ: RVCアプリケーションのビルドに進めます。")
            else:
                messagebox.showwarning("調査が必要", 
                    "何らかの問題が発生している可能性があります。\n"
                    "ログを確認して問題を特定してください。")
                
        except Exception as e:
            messagebox.showerror("エラー", f"メッセージボックスエラー:\n{e}")
    
    def run(self):
        """アプリケーションの実行"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("アプリケーションが中断されました")
        except Exception as e:
            print(f"アプリケーションエラー: {e}")

def main():
    """メイン関数"""
    print("🚀 Nuitka GUI互換性テストアプリを起動中...")
    
    # GUI モード
    app = SimpleNuitkaGUI()
    app.run()

if __name__ == "__main__":
    main()