#!/usr/bin/env python3
"""
GUI診断スクリプト - 問題を段階的に特定
"""
import tkinter as tk
from tkinter import ttk
import sys

def test_basic_widgets():
    """基本的なウィジェットのテスト"""
    root = tk.Tk()
    root.title("Widget Test")
    root.geometry("800x600")
    
    print("=== Widget Test Started ===")
    
    # 1. 基本的なLabel
    print("1. Creating basic Label...")
    label1 = tk.Label(root, text="Test Label 1 - Plain")
    label1.pack(pady=5)
    print("   Label created and packed")
    
    # 2. 背景色付きLabel
    print("2. Creating Label with background...")
    label2 = tk.Label(root, text="Test Label 2 - With BG", bg='lightgray')
    label2.pack(pady=5)
    print("   Label with bg created")
    
    # 3. Frame内のLabel
    print("3. Creating Frame with Label...")
    frame1 = tk.Frame(root, bg='lightblue', width=300, height=50)
    frame1.pack(pady=5)
    frame1.pack_propagate(False)
    label3 = tk.Label(frame1, text="Test Label 3 - In Frame", bg='lightblue')
    label3.pack()
    print("   Frame and label created")
    
    # 4. TTK Label
    print("4. Creating TTK Label...")
    ttk_label = ttk.Label(root, text="TTK Label Test")
    ttk_label.pack(pady=5)
    print("   TTK label created")
    
    # 5. Entry widget
    print("5. Creating Entry widget...")
    entry = tk.Entry(root)
    entry.insert(0, "Entry widget test")
    entry.pack(pady=5)
    print("   Entry created")
    
    # 6. Listbox
    print("6. Creating Listbox...")
    listbox = tk.Listbox(root, height=5)
    for i in range(5):
        listbox.insert(tk.END, f"Item {i+1}")
    listbox.pack(pady=5)
    print("   Listbox created")
    
    # 7. Button
    print("7. Creating Button...")
    button = tk.Button(root, text="Test Button", command=lambda: print("Button clicked"))
    button.pack(pady=5)
    print("   Button created")
    
    # Info label
    info = tk.Label(root, text="すべてのウィジェットが表示されていますか？", 
                   font=('Arial', 14, 'bold'), fg='red')
    info.pack(pady=20)
    
    print("=== All widgets created ===")
    print("Starting mainloop...")
    
    root.mainloop()

def test_style_issue():
    """スタイルの問題をテスト"""
    root = tk.Tk()
    root.title("Style Test")
    root.geometry("600x400")
    
    # スタイルを作成
    style = ttk.Style()
    print(f"Available themes: {style.theme_names()}")
    print(f"Current theme: {style.theme_use()}")
    
    # デフォルトテーマでテスト
    frame1 = ttk.LabelFrame(root, text="Default Theme Test")
    frame1.pack(fill='x', padx=20, pady=10)
    
    ttk.Label(frame1, text="TTK Label in default theme").pack(pady=5)
    ttk.Button(frame1, text="TTK Button").pack(pady=5)
    
    # clamテーマでテスト
    style.theme_use('clam')
    frame2 = ttk.LabelFrame(root, text="Clam Theme Test")
    frame2.pack(fill='x', padx=20, pady=10)
    
    ttk.Label(frame2, text="TTK Label in clam theme").pack(pady=5)
    ttk.Button(frame2, text="TTK Button").pack(pady=5)
    
    # カスタムスタイル
    style.configure('Custom.TLabel', foreground='blue', background='yellow')
    custom_label = ttk.Label(root, text="Custom styled label", style='Custom.TLabel')
    custom_label.pack(pady=10)
    
    root.mainloop()

def test_pack_grid_issue():
    """PackとGridの混在問題をテスト"""
    root = tk.Tk()
    root.title("Layout Test")
    root.geometry("600x400")
    
    # Packのみ使用
    frame1 = tk.LabelFrame(root, text="Pack Layout", padx=20, pady=20)
    frame1.pack(fill='both', expand=True, padx=10, pady=10)
    
    tk.Label(frame1, text="Label 1 (pack)").pack()
    tk.Label(frame1, text="Label 2 (pack)").pack()
    tk.Button(frame1, text="Button (pack)").pack()
    
    # Gridのみ使用
    frame2 = tk.LabelFrame(root, text="Grid Layout", padx=20, pady=20)
    frame2.pack(fill='both', expand=True, padx=10, pady=10)
    
    tk.Label(frame2, text="Label 1 (grid)").grid(row=0, column=0)
    tk.Label(frame2, text="Label 2 (grid)").grid(row=1, column=0)
    tk.Button(frame2, text="Button (grid)").grid(row=2, column=0)
    
    root.mainloop()

def test_color_contrast():
    """色のコントラスト問題をテスト"""
    root = tk.Tk()
    root.title("Color Contrast Test")
    root.geometry("600x400")
    
    # 異なる背景色でテスト
    colors = [
        ('white', 'black'),
        ('black', 'white'),
        ('#1e1e1e', '#ffffff'),
        ('#2d2d2d', '#b0b0b0'),
        ('lightgray', 'black')
    ]
    
    for i, (bg, fg) in enumerate(colors):
        frame = tk.Frame(root, bg=bg, height=50)
        frame.pack(fill='x', padx=10, pady=5)
        frame.pack_propagate(False)
        
        label = tk.Label(frame, text=f"BG: {bg}, FG: {fg}", bg=bg, fg=fg)
        label.pack(expand=True)
    
    root.mainloop()

def main():
    print("GUI診断を開始します...")
    print(f"Python version: {sys.version}")
    print(f"Tkinter version: {tk.TkVersion}")
    
    while True:
        print("\n診断オプションを選択してください:")
        print("1. 基本的なウィジェットテスト")
        print("2. スタイル問題テスト")
        print("3. レイアウト問題テスト")
        print("4. 色のコントラストテスト")
        print("5. 終了")
        
        choice = input("選択 (1-5): ")
        
        if choice == '1':
            test_basic_widgets()
        elif choice == '2':
            test_style_issue()
        elif choice == '3':
            test_pack_grid_issue()
        elif choice == '4':
            test_color_contrast()
        elif choice == '5':
            break
        else:
            print("無効な選択です")

if __name__ == "__main__":
    main()
