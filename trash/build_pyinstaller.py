#!/usr/bin/env python3
"""
Voice Converter - PyInstaller Build Script for macOS
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class PyInstallerMacAppBuilder:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.app_name = "Voice Converter"
        self.main_script = "gui_dark_mode.py"
        
    def clean_build_dirs(self):
        """前回のビルドをクリーンアップ"""
        print("🧹 Cleaning previous builds...")
        dirs_to_clean = ['build', 'dist', '__pycache__']
        
        for dir_name in dirs_to_clean:
            dir_path = self.project_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   ✓ Removed {dir_name}")
    
    def create_spec_file(self):
        """PyInstaller spec ファイルを作成"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{self.main_script}'],
    pathex=[],
    binaries=[],
    datas=[
        ('model_dir', 'model_dir'),
        ('rvc', 'rvc'),
        ('gui_settings.json', '.'),
        ('README.md', '.'),
        ('LICENSE', '.')
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'wave',
        'struct',
        'tempfile',
        'shutil',
        'platform',
        'traceback',
        'logging',
        'json',
        'subprocess',
        'threading',
        'pathlib',
        'datetime',
        'os',
        'sys',
        'math',
        'time'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    a.zipfiles,
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
    }},
)
'''
        
        spec_file = self.project_dir / f"{self.app_name}.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        print(f"   ✓ Created {spec_file}")
        return spec_file
    
    def build_app(self):
        """PyInstallerでアプリをビルド"""
        print("\n🏗️  Building macOS app with PyInstaller...")
        
        spec_file = self.create_spec_file()
        
        cmd = [
            sys.executable,
            '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            str(spec_file)
        ]
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.project_dir)
        
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Build completed successfully!")
                return True
            else:
                print("   ❌ Build failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
                
        except Exception as e:
            print(f"   ❌ Build error: {e}")
            return False
    
    def run(self):
        """ビルドプロセスを実行"""
        print("🚀 Voice Converter - PyInstaller Build Script")
        print("=" * 50)
        
        self.clean_build_dirs()
        
        if self.build_app():
            app_path = self.project_dir / 'dist' / f'{self.app_name}.app'
            if app_path.exists():
                print(f"\n✨ App successfully built at: {app_path}")
                print(f"\n📦 To create DMG, run:")
                print(f'   hdiutil create -volname "{self.app_name}" -srcfolder "{app_path}" -ov -format UDZO "{self.app_name}.dmg"')
            else:
                print("\n❌ App bundle not found!")
        else:
            print("\n❌ Build failed!")
            sys.exit(1)

if __name__ == "__main__":
    builder = PyInstallerMacAppBuilder()
    builder.run()
