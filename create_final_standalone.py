#!/usr/bin/env python3
"""
RVC 最終版スタンドアロンアプリ作成ツール
確実に動作するmacOSアプリケーションを作成
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 RVC 最終版スタンドアロンアプリ作成ツール")
    
    project_dir = Path(__file__).parent.absolute()
    print(f"📁 プロジェクトディレクトリ: {project_dir}")
    
    # 1. 最適なPython環境を使用
    print("🔧 最適なPython環境を確認中...")
    
    # venv_tkinter_fix環境を優先使用
    venv_python = project_dir / "venv_tkinter_fix" / "bin" / "python"
    if venv_python.exists():
        python_path = str(venv_python)
        print(f"✅ tkinter対応Python使用: {python_path}")
    else:
        # Homebrew Pythonをフォールバック
        homebrew_python = "/opt/homebrew/bin/python3.11"
        if os.path.exists(homebrew_python):
            python_path = homebrew_python
            print(f"✅ Homebrew Python使用: {python_path}")
        else:
            print("❌ 適切なPython環境が見つかりません")
            return False
    
    # 2. PyInstallerをインストール
    print("📦 PyInstallerをインストール中...")
    try:
        subprocess.run([python_path, "-m", "pip", "install", "pyinstaller"], 
                      check=True, capture_output=True)
        print("✅ PyInstallerインストール完了")
    except subprocess.CalledProcessError:
        print("📦 PyInstaller既にインストール済み")
    
    # 3. 必要な依存関係をインストール
    print("📦 依存関係をインストール中...")
    required_packages = [
        "torch", "torchaudio", "librosa", "soundfile", 
        "numpy", "scipy", "click", "fairseq"
    ]
    
    for package in required_packages:
        try:
            subprocess.run([python_path, "-c", f"import {package}"], 
                          check=True, capture_output=True)
            print(f"✅ {package} 利用可能")
        except subprocess.CalledProcessError:
            print(f"📦 {package} をインストール中...")
            try:
                subprocess.run([python_path, "-m", "pip", "install", package], 
                              check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print(f"⚠️ {package} インストールスキップ")
    
    # 4. アプリケーション作成スクリプトを作成
    print("📝 アプリケーション起動スクリプト作成中...")
    
    app_launcher = project_dir / "rvc_launcher.py"
    with open(app_launcher, 'w', encoding='utf-8') as f:
        f.write(f'''#!/usr/bin/env python3
"""
RVC Voice Converter - スタンドアロンアプリ起動ランチャー
"""

import os
import sys
from pathlib import Path

def main():
    try:
        # アプリケーションのリソースディレクトリを取得
        if getattr(sys, 'frozen', False):
            # PyInstallerでパッケージされた場合
            app_dir = Path(sys._MEIPASS)
        else:
            # 通常のPythonスクリプトの場合
            app_dir = Path(__file__).parent.absolute()
        
        # 環境変数設定
        os.environ['PYTHONPATH'] = str(app_dir)
        
        # gui_dark_mode.pyを直接実行
        gui_script = app_dir / "gui_dark_mode.py"
        if gui_script.exists():
            with open(gui_script, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 実行コンテキストを設定
            exec_globals = {{
                '__name__': '__main__',
                '__file__': str(gui_script),
                '__package__': None
            }}
            
            # パスを追加
            if str(app_dir) not in sys.path:
                sys.path.insert(0, str(app_dir))
            
            # GUIスクリプト実行
            exec(code, exec_globals)
        else:
            print(f"❌ GUIスクリプトが見つかりません: {{gui_script}}")
            return 1
            
    except Exception as e:
        print(f"❌ アプリケーション起動エラー: {{e}}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
''')
    
    print(f"✅ 起動ランチャー作成完了: {app_launcher}")
    
    # 5. PyInstaller設定ファイル作成
    print("📝 PyInstaller設定ファイル作成中...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

project_dir = Path(r"{project_dir}")

# データファイルを収集
datas = [
    (str(project_dir / "gui_dark_mode.py"), "."),
    (str(project_dir / "rvc_config.py"), "."),
    (str(project_dir / "rvc"), "rvc"),
    (str(project_dir / "model_dir"), "model_dir"),
    (str(project_dir / "app_icons"), "app_icons"),
    (str(project_dir / "pyproject.toml"), "."),
    (str(project_dir / "poetry.lock"), "."),
    (str(project_dir / "CLAUDE.md"), "."),
    (str(project_dir / "RVC使い方ガイド.txt"), "."),
]

# tkinter用ライブラリ（存在する場合のみ追加）
tkinter_binaries = []
if os.path.exists("/opt/homebrew/lib/libtcl8.6.dylib"):
    tkinter_binaries.append(("/opt/homebrew/lib/libtcl8.6.dylib", "."))
if os.path.exists("/opt/homebrew/lib/libtk8.6.dylib"):
    tkinter_binaries.append(("/opt/homebrew/lib/libtk8.6.dylib", "."))

a = Analysis(
    ['{app_launcher}'],
    pathex=[str(project_dir)],
    binaries=tkinter_binaries,
    datas=datas,
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
        '_tkinter', 'tkinter.font', 'tkinter.constants',
        'rvc', 'rvc.wrapper', 'rvc.wrapper.cli', 'rvc.modules',
        'subprocess', 'threading', 'json', 'pathlib', 'datetime', 'time',
        'numpy', 'scipy', 'torch', 'torchaudio', 'librosa', 'soundfile',
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
    name='RVC_Voice_Converter_Final',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{project_dir / "app_icons" / "rvc_icon.icns" if (project_dir / "app_icons" / "rvc_icon.icns").exists() else None}',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RVC_Voice_Converter_Final',
)

app = BUNDLE(
    coll,
    name='RVC Voice Converter Final.app',
    icon='{project_dir / "app_icons" / "rvc_icon.icns" if (project_dir / "app_icons" / "rvc_icon.icns").exists() else None}',
    bundle_identifier='com.rvc.voiceconverter.final',
    version='1.0.0',
    info_plist={{
        'CFBundleName': 'RVC Voice Converter Final',
        'CFBundleDisplayName': 'RVC Voice Converter Final',
        'CFBundleIdentifier': 'com.rvc.voiceconverter.final',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'RVCF',
        'LSMinimumSystemVersion': '10.15.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    }},
)
'''
    
    spec_file = project_dir / "RVC_Final.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ PyInstaller設定ファイル作成完了: {spec_file}")
    
    # 6. PyInstallerでアプリケーション作成
    print("🏗️  最終版スタンドアロンアプリケーション作成中...")
    print("⚠️  この処理には10-20分程度かかります")
    
    try:
        result = subprocess.run([
            python_path, "-m", "PyInstaller",
            str(spec_file),
            "--clean",
            "--noconfirm"
        ], cwd=str(project_dir), check=True, capture_output=True, text=True)
        
        print("✅ PyInstaller実行完了")
        
        app_path = project_dir / "dist" / "RVC Voice Converter Final.app"
        
        if app_path.exists():
            print(f"✅ 最終版スタンドアロンアプリ作成完了!")
            print(f"📱 アプリパス: {app_path}")
            
            # アプリサイズを表示
            size_mb = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file()) / (1024*1024)
            print(f"📏 アプリサイズ: {size_mb:.1f} MB")
            
            return app_path
        else:
            print("❌ アプリケーション作成に失敗しました")
            print("PyInstaller出力:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstallerエラー: {e}")
        if e.stdout:
            print("標準出力:", e.stdout)
        if e.stderr:
            print("エラー出力:", e.stderr)
        return False

if __name__ == "__main__":
    app_path = main()
    if app_path:
        print("\n🚀 最終版スタンドアロンアプリを起動中...")
        subprocess.run(["open", str(app_path)])