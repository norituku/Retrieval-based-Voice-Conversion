# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/gui_dark_mode.py'],
    pathex=[str(Path("/Users/norikene_satoshi/Retrieval-based-Voice-Conversion"))],
    binaries=[],
    datas=[
        (str(Path("/Users/norikene_satoshi/Retrieval-based-Voice-Conversion") / "rvc"), "rvc"),
        (str(Path("/Users/norikene_satoshi/Retrieval-based-Voice-Conversion") / "model_dir"), "model_dir"),
        (str(Path("/Users/norikene_satoshi/Retrieval-based-Voice-Conversion") / "app_icons"), "app_icons"),
        (str(Path("/Users/norikene_satoshi/Retrieval-based-Voice-Conversion") / "rvc_config.py"), "."),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog', 
        'tkinter.messagebox',
        '_tkinter',
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
