#!/usr/bin/env python3
"""
Voice Converter - PyInstaller Build Script (Python 3.11.9)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class PyInstallerBuilder:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.app_name = "Voice Converter"
        self.main_script = "gui_dark_mode.py"
        self.python_path = "/usr/local/bin/python3"
        
    def check_environment(self):
        """環境チェック"""
        print("🔍 Checking environment...")
        
        # Pythonバージョン確認
        result = subprocess.run([self.python_path, "--version"], 
                              capture_output=True, text=True)
        print(f"   Python: {result.stdout.strip()}")
        
        # PyInstallerの確認
        result = subprocess.run([self.python_path, "-m", "pip", "show", "pyinstaller"],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("   ❌ PyInstaller not found. Installing...")
            subprocess.run([self.python_path, "-m", "pip", "install", "pyinstaller"])
        else:
            print("   ✓ PyInstaller found")
            
    def clean_build(self):
        """ビルドディレクトリのクリーンアップ"""
        print("\n🧹 Cleaning previous builds...")
        dirs_to_clean = ['build', 'dist', '__pycache__']
        
        for dir_name in dirs_to_clean:
            dir_path = self.project_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   ✓ Removed {dir_name}")
                
    def create_spec_file(self):
        """PyInstaller specファイルを作成"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{self.main_script}'],
    pathex=['{self.project_dir}'],
    binaries=[],
    datas=[
        ('model_dir', 'model_dir'),
        ('rvc', 'rvc'),
        ('gui_settings.json', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
        ('rvc_config.py', '.')
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        '_tkinter',
        'rvc_config'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{self.app_name}',
)

app = BUNDLE(
    coll,
    name='{self.app_name}.app',
    icon=None,
    bundle_identifier='com.rvc.voiceconverter',
    info_plist={{
        'CFBundleName': '{self.app_name}',
        'CFBundleDisplayName': '{self.app_name}',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': '{self.app_name}',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.13',
    }},
)
'''
        
        spec_file = self.project_dir / f"{self.app_name}.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
            
        return spec_file
        
    def build_app(self):
        """アプリケーションをビルド"""
        print("\n🏗️  Building macOS app...")
        
        spec_file = self.create_spec_file()
        
        # PyInstallerを実行
        cmd = [
            self.python_path,
            "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Build completed successfully!")
            return True
        else:
            print("   ❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    def post_build(self):
        """ビルド後の処理"""
        app_path = self.project_dir / 'dist' / f'{self.app_name}.app'
        
        if app_path.exists():
            # Gatekeeperの属性を削除
            subprocess.run(["xattr", "-cr", str(app_path)])
            print(f"\n✨ App successfully built at: {app_path}")
            
            # DMG作成
            print("\n📦 Creating DMG...")
            dmg_name = f"{self.app_name} Python3.11.dmg"
            subprocess.run([
                "hdiutil", "create",
                "-volname", self.app_name,
                "-srcfolder", str(app_path),
                "-ov", "-format", "UDZO",
                dmg_name
            ])
            print(f"   ✅ DMG created: {dmg_name}")
            
    def run(self):
        """ビルドプロセスを実行"""
        print("🚀 Voice Converter PyInstaller Build (Python 3.11.9)")
        print("=" * 50)
        
        self.check_environment()
        self.clean_build()
        
        if self.build_app():
            self.post_build()
        else:
            print("\n❌ Build failed!")
            sys.exit(1)

if __name__ == "__main__":
    builder = PyInstallerBuilder()
    builder.run()
