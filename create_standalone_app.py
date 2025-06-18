#!/usr/bin/env python3
"""
RVC スタンドアロンmacOSアプリ作成ツール (PyInstaller版)
使用方法: python create_standalone_app.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json

def main():
    print("🏗️  RVC スタンドアロンmacOSアプリ作成ツール (PyInstaller版)")
    
    project_dir = Path(__file__).parent.absolute()
    print(f"📁 プロジェクトディレクトリ: {project_dir}")
    
    # 1. 必要なツールの確認
    print("🔧 必要なツールを確認中...")
    
    # PyInstallerの確認・インストール
    try:
        import PyInstaller
    except ImportError:
        print("📦 PyInstallerをインストール中...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # 2. PyInstaller用設定ファイルの作成
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

project_dir = Path(r"{project_dir}")

# RVCライブラリのパスを追加
rvc_path = project_dir / "rvc"
added_files = [
    (str(rvc_path), "rvc"),
    (str(project_dir / "model_dir"), "model_dir"),
    (str(project_dir / "app_icons"), "app_icons"),
    (str(project_dir / "pyproject.toml"), "."),
    (str(project_dir / "poetry.lock"), "."),
    (str(project_dir / "rvc_config.py"), "."),
    (str(project_dir / "run_gui.sh"), "."),
]

# Poetryの仮想環境パスを取得（存在する場合）
venv_path = project_dir / ".venv"
if venv_path.exists():
    # 重要なPythonパッケージのみを追加
    site_packages = venv_path / "lib" / "python3.11" / "site-packages"
    if site_packages.exists():
        for pkg in ["torch", "torchaudio", "librosa", "soundfile", "fairseq"]:
            pkg_path = site_packages / pkg
            if pkg_path.exists():
                added_files.append((str(pkg_path), pkg))

a = Analysis(
    ['{project_dir / "gui_dark_mode.py"}'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'rvc',
        'rvc.wrapper.cli.cli',
        'torch',
        'torchaudio',
        'librosa',
        'soundfile',
        'fairseq',
        'numpy',
        'scipy',
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
    name='RVC_Voice_Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{project_dir / "app_icons" / "rvc_icon.icns"}',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RVC_Voice_Converter',
)

app = BUNDLE(
    coll,
    name='RVC Voice Converter.app',
    icon='{project_dir / "app_icons" / "rvc_icon.icns"}',
    bundle_identifier='com.rvc.voiceconverter',
    version='1.0.0',
    info_plist={{
        'CFBundleName': 'RVC Voice Converter',
        'CFBundleDisplayName': 'RVC Voice Converter',
        'CFBundleIdentifier': 'com.rvc.voiceconverter',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'RVCV',
        'LSMinimumSystemVersion': '10.15.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    }},
)
'''
    
    spec_file = project_dir / "RVC_Standalone.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"📝 PyInstaller設定ファイル作成: {spec_file}")
    
    # 3. PyInstallerでアプリケーション作成
    print("🏗️  スタンドアロンアプリケーションを作成中...")
    print("⚠️  注意: この処理には時間がかかります（15-30分程度）")
    
    try:
        subprocess.run([
            "pyinstaller",
            str(spec_file),
            "--clean",
            "--noconfirm"
        ], check=True, cwd=str(project_dir))
        
        app_path = project_dir / "dist" / "RVC Voice Converter.app"
        
        if app_path.exists():
            print(f"✅ スタンドアロンアプリ作成完了: {app_path}")
            
            # アプリサイズを表示
            size_mb = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file()) / (1024*1024)
            print(f"📏 アプリサイズ: {size_mb:.1f} MB")
            
            # DMG作成オプション
            create_dmg = input("DMGディスクイメージを作成しますか？ (y/N): ").strip().lower()
            if create_dmg in ['y', 'yes']:
                create_dmg_package(app_path, project_dir)
                
        else:
            print("❌ アプリケーション作成に失敗しました")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstallerエラー: {e}")
        return False
    
    print("🎉 スタンドアロンアプリ作成プロセス完了!")
    return True

def create_dmg_package(app_path: Path, project_dir: Path):
    """DMGディスクイメージを作成"""
    print("💿 DMGディスクイメージを作成中...")
    
    dmg_dir = project_dir / "dmg_standalone"
    dmg_dir.mkdir(exist_ok=True)
    
    # アプリをDMGディレクトリにコピー
    shutil.copytree(app_path, dmg_dir / app_path.name, dirs_exist_ok=True)
    
    # Applicationsへのシンボリックリンク
    applications_link = dmg_dir / "Applications"
    if applications_link.exists():
        applications_link.unlink()
    applications_link.symlink_to("/Applications")
    
    # README作成
    readme_content = '''RVC Voice Converter - スタンドアロン版

このバージョンはすべての依存関係が含まれたスタンドアロン版です。

インストール方法:
1. "RVC Voice Converter.app"をApplicationsフォルダにドラッグ&ドロップ
2. 初回起動時にセキュリティ警告が表示される場合があります
3. システム環境設定 → セキュリティとプライバシー → 一般 → "このまま開く"

特徴:
- インターネット接続不要
- 依存関係のインストール不要
- 即座に使用開始可能

注意事項:
- ファイルサイズが大きいため、ダウンロードに時間がかかる場合があります
- 一部のmacOSバージョンでは追加の設定が必要な場合があります

サポート: https://github.com/your-repo/Retrieval-based-Voice-Conversion
'''
    
    with open(dmg_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # DMG作成
    dmg_name = "RVC-Voice-Converter-Standalone-v1.0.dmg"
    try:
        subprocess.run([
            "hdiutil", "create",
            "-volname", "RVC Voice Converter Standalone",
            "-srcfolder", str(dmg_dir),
            "-ov",
            "-format", "UDZO",
            str(project_dir / dmg_name)
        ], check=True)
        
        print(f"✅ DMG作成完了: {dmg_name}")
        
        # 一時ディレクトリを削除
        shutil.rmtree(dmg_dir)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ DMG作成エラー: {e}")

if __name__ == "__main__":
    main()