#!/usr/bin/env python3
"""
RVC スタンドアロンmacOSアプリ作成ツール (修正版)
Homebrew Python使用でtkinter問題を解決
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🏗️  RVC スタンドアロンmacOSアプリ作成ツール (修正版)")
    
    project_dir = Path(__file__).parent.absolute()
    print(f"📁 プロジェクトディレクトリ: {project_dir}")
    
    # Homebrew Pythonを使用
    homebrew_python = "/opt/homebrew/bin/python3.11"
    if not os.path.exists(homebrew_python):
        print("❌ Homebrew Python 3.11が見つかりません")
        print("インストール: brew install python@3.11 python-tk@3.11")
        return False
    
    print(f"🐍 使用Python: {homebrew_python}")
    
    # 1. PyInstallerをHomebrew Pythonにインストール
    print("📦 PyInstallerをインストール中...")
    try:
        subprocess.run([homebrew_python, "-m", "pip", "install", "pyinstaller"], check=True)
    except subprocess.CalledProcessError:
        print("PyInstaller既にインストール済み")
    
    # 2. 必要なパッケージをインストール
    print("📦 必要パッケージをインストール中...")
    packages = ["torch", "torchaudio", "librosa", "soundfile", "numpy", "scipy"]
    for pkg in packages:
        try:
            subprocess.run([homebrew_python, "-m", "pip", "install", pkg], check=True)
        except subprocess.CalledProcessError:
            print(f"パッケージ {pkg} のインストールをスキップ")
    
    # 3. 簡単なPyInstaller specファイル作成
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{project_dir / "gui_dark_mode.py"}'],
    pathex=[str(Path("{project_dir}"))],
    binaries=[],
    datas=[
        (str(Path("{project_dir}") / "rvc"), "rvc"),
        (str(Path("{project_dir}") / "model_dir"), "model_dir"),
        (str(Path("{project_dir}") / "app_icons"), "app_icons"),
        (str(Path("{project_dir}") / "rvc_config.py"), "."),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog', 
        'tkinter.messagebox',
        '_tkinter',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RVC_Fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RVC_Fixed',
)

app = BUNDLE(
    coll,
    name='RVC Voice Converter Fixed.app',
    icon=None,
    bundle_identifier='com.rvc.voiceconverter.fixed',
    version='1.0.0',
)
'''
    
    spec_file = project_dir / "RVC_Fixed.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"📝 PyInstaller設定ファイル作成: {spec_file}")
    
    # 4. PyInstallerでアプリケーション作成
    print("🏗️  修正版スタンドアロンアプリケーション作成中...")
    
    try:
        subprocess.run([
            homebrew_python, "-m", "PyInstaller",
            str(spec_file),
            "--clean",
            "--noconfirm"
        ], check=True, cwd=str(project_dir))
        
        app_path = project_dir / "dist" / "RVC Voice Converter Fixed.app"
        
        if app_path.exists():
            print(f"✅ 修正版アプリ作成完了: {app_path}")
            return app_path
        else:
            print("❌ アプリケーション作成に失敗しました")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstallerエラー: {e}")
        return False

if __name__ == "__main__":
    result = main()
    if result:
        print("🚀 修正版アプリを起動中...")
        subprocess.run(["open", str(result)])