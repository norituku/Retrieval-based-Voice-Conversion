# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

project_dir = Path(r"/Users/norikene_satoshi/Retrieval-based-Voice-Conversion")

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
    ['/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/gui_dark_mode.py'],
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
    hooksconfig={},
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
    icon='/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/app_icons/rvc_icon.icns',
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
    icon='/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/app_icons/rvc_icon.icns',
    bundle_identifier='com.rvc.voiceconverter',
    version='1.0.0',
    info_plist={
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
    },
)
