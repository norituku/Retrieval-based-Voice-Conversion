#!/usr/bin/env python3
"""
GUI Debug版 - セグメンテーションフォルトのデバッグ
"""
import os
import sys
import tkinter as tk
from tkinter import ttk
import traceback

print("=== GUI Debug Mode ===")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")

# 段階的インポートテスト
print("\n1. Basic imports...")
try:
    import json
    import threading
    import time
    from pathlib import Path
    from datetime import datetime
    print("✅ Basic imports successful")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")
    sys.exit(1)

print("\n2. Testing enhanced converter...")
try:
    from enhanced_converter_simple import SimpleEnhancedConverter
    print("✅ Enhanced converter import successful")
    
    # 初期化テスト
    converter = SimpleEnhancedConverter()
    status = converter.get_enhancement_status()
    print(f"✅ Enhanced converter initialization successful: {status['pipeline_type']}")
except Exception as e:
    print(f"❌ Enhanced converter failed: {e}")
    traceback.print_exc()

print("\n3. Testing GUI modules...")
try:
    from gui_modules import SettingsManager, ErrorHandler
    print("✅ GUI modules import successful")
    
    # 初期化テスト
    settings = SettingsManager("debug_settings.json")
    print("✅ Settings manager initialization successful")
except Exception as e:
    print(f"❌ GUI modules failed: {e}")
    traceback.print_exc()

print("\n4. Testing basic Tkinter...")
try:
    root = tk.Tk()
    root.title("Debug Window")
    root.geometry("300x200")
    
    label = tk.Label(root, text="Debug Test")
    label.pack(pady=20)
    
    button = tk.Button(root, text="Close", command=root.quit)
    button.pack(pady=10)
    
    print("✅ Basic Tkinter window created")
    
    # 短時間表示してから閉じる
    root.after(2000, root.quit)  # 2秒後に閉じる
    root.mainloop()
    root.destroy()
    
    print("✅ Basic Tkinter test completed successfully")
    
except Exception as e:
    print(f"❌ Basic Tkinter failed: {e}")
    traceback.print_exc()

print("\n5. Testing complex Tkinter...")
try:
    root = tk.Tk()
    root.title("Complex Debug Window")
    root.geometry("400x300")
    
    # フレーム作成
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 複数のウィジェット
    label = ttk.Label(main_frame, text="Complex Tkinter Test")
    label.pack(pady=5)
    
    entry = ttk.Entry(main_frame)
    entry.pack(pady=5)
    
    combo = ttk.Combobox(main_frame, values=["Option 1", "Option 2", "Option 3"])
    combo.pack(pady=5)
    
    progress = ttk.Progressbar(main_frame, value=50)
    progress.pack(pady=5, fill=tk.X)
    
    button = ttk.Button(main_frame, text="Close", command=root.quit)
    button.pack(pady=10)
    
    print("✅ Complex Tkinter widgets created")
    
    # 短時間表示してから閉じる
    root.after(3000, root.quit)  # 3秒後に閉じる
    root.mainloop()
    root.destroy()
    
    print("✅ Complex Tkinter test completed successfully")
    
except Exception as e:
    print(f"❌ Complex Tkinter failed: {e}")
    traceback.print_exc()

print("\n6. Testing minimal enhanced GUI...")
try:
    class MinimalEnhancedGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("Minimal Enhanced GUI")
            self.root.geometry("500x400")
            
            # 改良版コンバーターの初期化
            try:
                self.enhanced_converter = SimpleEnhancedConverter()
                self.use_enhanced = True
                print("✅ Enhanced converter initialized in GUI")
            except:
                self.enhanced_converter = None
                self.use_enhanced = False
                print("⚠️ Enhanced converter disabled in GUI")
            
            # シンプルなUI
            main_frame = ttk.Frame(root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            title_label = ttk.Label(main_frame, text="Minimal Enhanced Voice Converter", 
                                  font=("Arial", 16, "bold"))
            title_label.pack(pady=10)
            
            status_text = "Enhanced Mode: ON" if self.use_enhanced else "Enhanced Mode: OFF"
            status_label = ttk.Label(main_frame, text=status_text)
            status_label.pack(pady=5)
            
            if self.use_enhanced:
                enhancement_status = self.enhanced_converter.get_enhancement_status()
                features_text = f"Features: {list(enhancement_status['features'].keys())}"
                features_label = ttk.Label(main_frame, text=features_text)
                features_label.pack(pady=5)
            
            close_button = ttk.Button(main_frame, text="Close", command=root.quit)
            close_button.pack(pady=20)
    
    root = tk.Tk()
    app = MinimalEnhancedGUI(root)
    
    print("✅ Minimal enhanced GUI created")
    
    # 短時間表示してから閉じる
    root.after(4000, root.quit)  # 4秒後に閉じる
    root.mainloop()
    root.destroy()
    
    print("✅ Minimal enhanced GUI test completed successfully")
    
except Exception as e:
    print(f"❌ Minimal enhanced GUI failed: {e}")
    traceback.print_exc()

print("\n=== Debug Complete ===")
print("All tests passed. The issue might be in the full GUI implementation.")
print("Check for:")
print("- Memory leaks in large GUI components")
print("- Circular references in event handlers")
print("- Threading issues with Tkinter")
print("- macOS-specific Tkinter issues")