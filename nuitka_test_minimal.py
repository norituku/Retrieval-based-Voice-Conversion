#!/usr/bin/env python3
"""
Nuitka最小互換性テスト
tkinterとシステム情報のみの軽量テスト
"""
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

def test_tkinter():
    """tkinter テスト"""
    try:
        import tkinter as tk
        # 基本ウィンドウの作成テスト
        root = tk.Tk()
        root.withdraw()  # ウィンドウを非表示
        root.destroy()
        return "✅ tkinter available"
    except ImportError:
        return "❌ tkinter not available"
    except Exception as e:
        return f"⚠️ tkinter error: {e}"

def test_standard_library():
    """標準ライブラリのテスト"""
    results = {}
    
    standard_libs = [
        'json',
        'pathlib', 
        'subprocess',
        'threading',
        'logging',
        'zipfile',
        'shutil',
        'tempfile'
    ]
    
    for lib in standard_libs:
        try:
            __import__(lib)
            results[lib] = "✅ OK"
        except ImportError:
            results[lib] = "❌ Not available"
        except Exception as e:
            results[lib] = f"⚠️ Error: {e}"
    
    return results

def main():
    """メイン関数"""
    print("🧪 Nuitka最小互換性テスト")
    print("=" * 50)
    
    # システム情報
    print("\n🖥️ システム情報:")
    for key, value in test_system_info().items():
        print(f"  {key}: {value}")
    
    # tkinter テスト
    print(f"\n🎨 GUI Framework: {test_tkinter()}")
    
    # 標準ライブラリテスト
    print("\n📚 標準ライブラリテスト:")
    std_results = test_standard_library()
    for lib_name, result in std_results.items():
        print(f"  {lib_name:12}: {result}")
    
    # サマリー
    success_count = sum(1 for r in std_results.values() if "✅" in r)
    total_count = len(std_results)
    
    print(f"\n📊 結果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("✅ 基本的なNuitka互換性は問題ありません")
        return True
    else:
        print("⚠️ 一部の標準ライブラリで問題が発生しました")
        return False

if __name__ == "__main__":
    main()