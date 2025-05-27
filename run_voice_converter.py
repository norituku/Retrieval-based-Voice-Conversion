#!/usr/bin/env python3
"""
RVC GUI起動スクリプト - 警告抑制版
macOS固有の警告を抑制してGUIを起動
"""
import os
import sys
import warnings

# Python警告を抑制
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# macOS固有の環境変数設定
if sys.platform == "darwin":
    # NSOpenPanel警告を抑制
    os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
    # IMK警告を抑制
    os.environ['PYOBJC_DISABLE_GIL_VALIDATION'] = '1'
    # その他のmacOS警告を抑制
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

# 標準エラー出力をフィルタリング（オプション）
class ErrorFilter:
    def __init__(self, stream):
        self.stream = stream
        self.suppress_patterns = [
            "NSOpenPanel",
            "IMKCFRunLoopWakeUpReliable",
            "The class",
            "error messaging the mach port"
        ]
    
    def write(self, data):
        # 抑制パターンに一致しない場合のみ出力
        if not any(pattern in data for pattern in self.suppress_patterns):
            self.stream.write(data)
    
    def flush(self):
        self.stream.flush()
    
    def __getattr__(self, attr):
        return getattr(self.stream, attr)

# 警告フィルタを適用（コメントアウトして無効化可能）
# sys.stderr = ErrorFilter(sys.stderr)

if __name__ == "__main__":
    # GUIをインポートして起動
    try:
        import tkinter as tk
        from gui_dark_mode import DarkModeGUI
        
        print("Voice Converter GUIを起動しています...")
        print("注意: macOSの警告が表示される場合がありますが、動作に影響はありません。")
        print("")
        
        root = tk.Tk()
        app = DarkModeGUI(root)
        root.mainloop()
        
    except ImportError as e:
        print(f"エラー: 必要なモジュールが見つかりません: {e}")
        print("tkinterがインストールされているか確認してください。")
    except Exception as e:
        print(f"エラー: {e}")
        print("詳細なエラー情報:")
        import traceback
        traceback.print_exc()
