#!/usr/bin/env python3
"""
Voice Converter - Advanced Nuitka Build Script for macOS
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class MacAppBuilder:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.app_name = "Voice Converter"
        self.bundle_id = "com.rvc.voiceconverter"
        self.version = "1.0.0"
        self.main_script = "gui_dark_mode.py"
        
    def clean_build_dirs(self):
        """前回のビルドをクリーンアップ"""
        print("🧹 Cleaning previous builds...")
        dirs_to_clean = ['build', 'dist', f'{self.app_name}.build', f'{self.app_name}.dist']
        
        for dir_name in dirs_to_clean:
            dir_path = self.project_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   ✓ Removed {dir_name}")
    
    def check_dependencies(self):
        """必要な依存関係をチェック"""
        print("🔍 Checking dependencies...")
        
        try:
            import nuitka
            try:
                version = nuitka.__version__
            except AttributeError:
                # Nuitkaのバージョンが取得できない場合
                version = "unknown"
            print(f"   ✓ Nuitka found: {version}")
        except ImportError:
            print("   ❌ Nuitka not found. Install with: pip install nuitka")
            return False
            
        try:
            import tkinter
            print("   ✓ Tkinter available")
        except ImportError:
            print("   ❌ Tkinter not available")
            return False
            
        return True
    
    def build_nuitka_command(self):
        """Nuitkaコマンドを構築"""
        cmd = [
            sys.executable, '-m', 'nuitka',
            '--standalone',
            '--macos-create-app-bundle',
            f'--macos-app-name={self.app_name}',
            f'--macos-app-version={self.version}',
            '--macos-app-mode=gui',
            
            # Plugins
            '--enable-plugin=tk-inter',
            '--enable-plugin=multiprocessing',
            
            # Include data directories (only existing ones)
            '--include-data-dir=model_dir=model_dir',
            '--include-data-dir=rvc=rvc',
            '--include-data-dir=samples=samples',
            
            # Include data files
            '--include-data-file=gui_settings.json=gui_settings.json',
            '--include-data-file=README.md=README.md',
            '--include-data-file=LICENSE=LICENSE',
            
            # Include Python modules
            '--include-module=tkinter',
            '--include-module=tkinter.ttk',
            '--include-module=tkinter.filedialog',
            '--include-module=tkinter.messagebox',
            '--include-module=json',
            '--include-module=subprocess',
            '--include-module=threading',
            '--include-module=pathlib',
            '--include-module=datetime',
            '--include-module=os',
            '--include-module=sys',
            '--include-module=math',
            '--include-module=time',
            '--include-module=wave',
            '--include-module=struct',
            '--include-module=tempfile',
            '--include-module=shutil',
            '--include-module=platform',
            '--include-module=traceback',
            '--include-module=logging',
            
            # Output options
            '--output-dir=dist',
            '--remove-output',
            '--static-libpython=no',
            
            # Progress options
            '--show-progress',
            '--show-memory',
            '--assume-yes-for-downloads',
            
            # Optimization
            '--lto=no',  # LTOを無効にして安定性を向上
            
            self.main_script
        ]
        
        return cmd
    
    def create_custom_info_plist(self, app_bundle_path):
        """カスタムInfo.plistを作成"""
        print("📝 Creating custom Info.plist...")
        
        info_plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>Voice Converter</string>
    <key>CFBundleExecutable</key>
    <string>gui_dark_mode</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.rvc.voiceconverter</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Voice Converter</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024 RVC Project. All rights reserved.</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.music</string>
    <key>NSMicrophoneUsageDescription</key>
    <string>Voice Converter needs access to your microphone for voice input.</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Audio Files</string>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
            <key>LSItemContentTypes</key>
            <array>
                <string>public.audio</string>
                <string>public.mp3</string>
                <string>public.wav</string>
                <string>public.aiff-audio</string>
                <string>public.aifc-audio</string>
            </array>
        </dict>
    </array>
</dict>
</plist>'''
        
        info_plist_path = app_bundle_path / 'Contents' / 'Info.plist'
        with open(info_plist_path, 'w', encoding='utf-8') as f:
            f.write(info_plist_content)
        
        print(f"   ✓ Info.plist created at {info_plist_path}")
    
    def build_app(self):
        """アプリをビルド"""
        print(f"🚀 Building {self.app_name}...")
        
        if not self.check_dependencies():
            return False
        
        self.clean_build_dirs()
        
        cmd = self.build_nuitka_command()
        print("📋 Running Nuitka command:")
        print(f"   {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_dir, check=True)
            print("✅ Nuitka build completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Nuitka build failed with exit code {e.returncode}")
            return False
    
    def post_build_setup(self):
        """ビルド後の設定"""
        # Nuitkaは元のスクリプト名でアプリバンドルを作成する
        actual_app_name = "gui_dark_mode.app"
        app_bundle_path = self.project_dir / 'dist' / actual_app_name
        target_app_path = self.project_dir / 'dist' / f'{self.app_name}.app'
        
        if not app_bundle_path.exists():
            print(f"❌ App bundle not found at {app_bundle_path}!")
            print("Available files in dist:")
            import os
            for item in os.listdir(self.project_dir / 'dist'):
                print(f"  - {item}")
            return False
        
        print("🔧 Post-build setup...")
        
        # アプリバンドルの名前を変更
        if actual_app_name != f'{self.app_name}.app':
            if target_app_path.exists():
                shutil.rmtree(target_app_path)
            shutil.move(str(app_bundle_path), str(target_app_path))
            app_bundle_path = target_app_path
            print(f"   ✓ Renamed app bundle to '{self.app_name}.app'")
        
        # カスタムInfo.plistを作成
        self.create_custom_info_plist(app_bundle_path)
        
        # アイコンファイルが存在する場合はコピー
        icon_path = self.project_dir / 'icon.icns'
        if icon_path.exists():
            resources_dir = app_bundle_path / 'Contents' / 'Resources'
            resources_dir.mkdir(exist_ok=True)
            shutil.copy2(icon_path, resources_dir / 'icon.icns')
            print("   ✓ App icon copied")
        
        print(f"✅ App bundle created: {app_bundle_path}")
        print(f"   To run: open '{app_bundle_path}'")
        
        return True

def main():
    """メイン関数"""
    print("🎵 Voice Converter - macOS App Builder")
    print("=" * 50)
    
    builder = MacAppBuilder()
    
    if builder.build_app():
        if builder.post_build_setup():
            print("\n🎉 Build completed successfully!")
            print(f"Your app is ready at: dist/{builder.app_name}.app")
        else:
            print("\n❌ Post-build setup failed!")
            sys.exit(1)
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()