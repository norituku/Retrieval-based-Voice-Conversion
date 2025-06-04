#!/usr/bin/env python3
"""
Nuitka互換性テスト用最小アプリ
基本的なGUI機能とライブラリインポートの確認
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
import platform
from pathlib import Path

def test_basic_libraries():
    """基本ライブラリのインポートテスト"""
    results = {}
    
    # 重要なライブラリのテスト
    libraries = [
        ('numpy', 'numpy'),
        ('torch', 'torch'),
        ('librosa', 'librosa'),
        ('soundfile', 'soundfile'),
        ('scipy', 'scipy'),
        ('rvc', 'rvc.configs.config'),
    ]
    
    for name, import_path in libraries:
        try:
            __import__(import_path)
            results[name] = "✅ OK"
        except ImportError as e:
            results[name] = f"❌ Error: {e}"
        except Exception as e:
            results[name] = f"⚠️  Warning: {e}"
    
    return results

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

class NuitkaTestApp:
    """Nuitkaテスト用GUIアプリ"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nuitka互換性テスト - RVC")
        self.root.geometry("800x600")
        
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
        self.run_initial_tests()
    
    def setup_ui(self):
        """UI のセットアップ"""
        # メインフレーム
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タイトル
        title_label = tk.Label(main_frame, 
                              text="🧪 Nuitka互換性テスト",
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
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, 
                                height=8,
                                bg=self.colors['entry_bg'],
                                fg=self.colors['fg'],
                                font=('Courier', 10))
        self.info_text.pack(fill=tk.X, padx=10, pady=10)
        
        # ライブラリテストセクション
        lib_frame = tk.LabelFrame(main_frame,
                                 text="ライブラリインポートテスト",
                                 font=('Arial', 12, 'bold'),
                                 bg=self.colors['bg'],
                                 fg=self.colors['fg'])
        lib_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.lib_text = tk.Text(lib_frame,
                               bg=self.colors['entry_bg'],
                               fg=self.colors['fg'],
                               font=('Courier', 10))
        self.lib_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X)
        
        # テスト再実行ボタン
        test_btn = tk.Button(button_frame,
                            text="🔄 テスト再実行",
                            command=self.run_tests,
                            bg=self.colors['button_bg'],
                            fg=self.colors['fg'],
                            font=('Arial', 10),
                            padx=20)
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # ファイル選択テスト
        file_btn = tk.Button(button_frame,
                            text="📁 ファイル選択テスト",
                            command=self.test_file_dialog,
                            bg=self.colors['button_bg'],
                            fg=self.colors['fg'],
                            font=('Arial', 10),
                            padx=20)
        file_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 終了ボタン
        quit_btn = tk.Button(button_frame,
                            text="❌ 終了",
                            command=self.root.quit,
                            bg=self.colors['error'],
                            fg=self.colors['fg'],
                            font=('Arial', 10),
                            padx=20)
        quit_btn.pack(side=tk.RIGHT)
    
    def run_initial_tests(self):
        """初期テストの実行"""
        self.run_tests()
    
    def run_tests(self):
        """全テストの実行"""
        # システム情報の表示
        self.info_text.delete(1.0, tk.END)
        system_info = test_system_info()
        
        for key, value in system_info.items():
            self.info_text.insert(tk.END, f"{key}:\n  {value}\n\n")
        
        # ライブラリテストの実行
        self.lib_text.delete(1.0, tk.END)
        self.lib_text.insert(tk.END, "🔍 ライブラリインポートテスト実行中...\n\n")
        self.root.update()
        
        lib_results = test_basic_libraries()
        
        self.lib_text.delete(1.0, tk.END)
        self.lib_text.insert(tk.END, "📚 ライブラリインポート結果:\n")
        self.lib_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for lib_name, result in lib_results.items():
            self.lib_text.insert(tk.END, f"{lib_name:15}: {result}\n")
        
        # 成功/失敗カウント
        success_count = sum(1 for r in lib_results.values() if "✅" in r)
        total_count = len(lib_results)
        
        self.lib_text.insert(tk.END, f"\n📊 結果サマリー: {success_count}/{total_count} 成功\n")
        
        if success_count == total_count:
            self.lib_text.insert(tk.END, "\n🎉 全てのライブラリが正常にインポートされました！")
        else:
            self.lib_text.insert(tk.END, "\n⚠️  一部のライブラリでエラーが発生しました")
    
    def test_file_dialog(self):
        """ファイルダイアログのテスト"""
        try:
            filename = filedialog.askopenfilename(
                title="テストファイル選択",
                filetypes=[
                    ("音声ファイル", "*.wav *.mp3 *.m4a *.flac"),
                    ("全てのファイル", "*.*")
                ]
            )
            
            if filename:
                messagebox.showinfo("成功", f"ファイルが選択されました:\n{filename}")
            else:
                messagebox.showinfo("キャンセル", "ファイル選択がキャンセルされました")
                
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルダイアログエラー:\n{e}")
    
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
    print("🚀 Nuitka互換性テストアプリを起動中...")
    
    # コマンドライン引数での基本テスト
    if "--cli-only" in sys.argv:
        print("\n📋 CLIモードでテスト実行:")
        
        # システム情報
        print("\n🖥️  システム情報:")
        for key, value in test_system_info().items():
            print(f"  {key}: {value}")
        
        # ライブラリテスト
        print("\n📚 ライブラリテスト:")
        for lib_name, result in test_basic_libraries().items():
            print(f"  {lib_name}: {result}")
        
        return
    
    # GUI モード
    app = NuitkaTestApp()
    app.run()

if __name__ == "__main__":
    main()