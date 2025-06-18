# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

project_dir = Path(r"/Users/norikene_satoshi/Retrieval-based-Voice-Conversion")

# 全RVCファイルをバンドル（機能完全保持）
added_files = [
    (str(project_dir / "rvc"), "rvc"),
    (str(project_dir / "model_dir"), "model_dir"), 
    (str(project_dir / "app_icons"), "app_icons"),
    (str(project_dir / "pyproject.toml"), "."),
    (str(project_dir / "poetry.lock"), "."),
    (str(project_dir / "rvc_config.py"), "."),
    (str(project_dir / "run_gui.sh"), "."),
    (str(project_dir / "CLAUDE.md"), "."),
]

# tkinter用のシステムライブラリ追加
tkinter_binaries = []
tkinter_datas = []

# Homebrew tkinterライブラリの検出・追加
homebrew_paths = ["/opt/homebrew", "/usr/local"]
for hb_path in homebrew_paths:
    tcl_lib = f"{hb_path}/lib/libtcl8.6.dylib"
    tk_lib = f"{hb_path}/lib/libtk8.6.dylib"
    if os.path.exists(tcl_lib):
        tkinter_binaries.append((tcl_lib, "."))
    if os.path.exists(tk_lib):
        tkinter_binaries.append((tk_lib, "."))
    
    tcl_dir = f"{hb_path}/lib/tcl8.6"
    tk_dir = f"{hb_path}/lib/tk8.6"
    if os.path.exists(tcl_dir):
        tkinter_datas.append((tcl_dir, "tcl8.6"))
    if os.path.exists(tk_dir):
        tkinter_datas.append((tk_dir, "tk8.6"))

a = Analysis(
    ['/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/gui_dark_mode.py'],
    pathex=[str(project_dir)],
    binaries=tkinter_binaries,
    datas=added_files + tkinter_datas,
    hiddenimports=[
        # tkinter関連（完全サポート）
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        '_tkinter',
        'tkinter.font',
        'tkinter.constants',
        'tkinter.dnd',
        'tkinter.scrolledtext',
        'tkinter.simpledialog',
        'tkinter.colorchooser',
        
        # RVC関連（既存機能完全保持）
        'rvc',
        'rvc.wrapper',
        'rvc.wrapper.cli',
        'rvc.wrapper.cli.cli',
        'rvc.wrapper.cli.handler',
        'rvc.wrapper.cli.handler.infer',
        'rvc.wrapper.cli.handler.train',
        'rvc.wrapper.cli.handler.uvr5',
        'rvc.modules',
        'rvc.modules.vc',
        'rvc.modules.vc.modules',
        'rvc.modules.vc.pipeline',
        'rvc.modules.vc.utils',
        'rvc.modules.uvr5',
        'rvc.lib',
        'rvc.configs',
        
        # 音声処理ライブラリ（既存機能保持）
        'torch',
        'torchaudio',
        'librosa',
        'soundfile',
        'fairseq',
        'numpy',
        'scipy',
        
        # その他依存関係
        'subprocess',
        'threading',
        'json',
        'pathlib',
        'datetime',
        'time',
        'os',
        'sys',
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
    name='RVC_Complete_Standalone',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUIアプリとして実行
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
    name='RVC_Complete_Standalone',
)

app = BUNDLE(
    coll,
    name='RVC Voice Converter Complete.app',
    icon='/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/app_icons/rvc_icon.icns',
    bundle_identifier='com.rvc.voiceconverter.complete',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'RVC Voice Converter Complete',
        'CFBundleDisplayName': 'RVC Voice Converter Complete',
        'CFBundleIdentifier': 'com.rvc.voiceconverter.complete',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'RVCV',
        'LSMinimumSystemVersion': '10.15.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSEnvironment': {
            'TCL_LIBRARY': '@executable_path/../Resources/tcl8.6',
            'TK_LIBRARY': '@executable_path/../Resources/tk8.6',
        },
    },
)
