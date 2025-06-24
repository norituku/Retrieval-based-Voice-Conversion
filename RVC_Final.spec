# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

project_dir = Path(r"/Users/norikene_satoshi/Retrieval-based-Voice-Conversion")

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
]

# 存在するファイルのみ追加
optional_files = [
    "rvc_worker.py",
    "rvc_standalone_app.py",
    "RVC使い方ガイド.txt"
]

for file_name in optional_files:
    file_path = project_dir / file_name
    if file_path.exists():
        datas.append((str(file_path), "."))

# tkinter用ライブラリ（存在する場合のみ追加）
tkinter_binaries = []
if os.path.exists("/opt/homebrew/lib/libtcl8.6.dylib"):
    tkinter_binaries.append(("/opt/homebrew/lib/libtcl8.6.dylib", "."))
if os.path.exists("/opt/homebrew/lib/libtk8.6.dylib"):
    tkinter_binaries.append(("/opt/homebrew/lib/libtk8.6.dylib", "."))

# PyTorchバイナリファイルを収集
pytorch_binaries = []
try:
    import torch
    torch_path = Path(torch.__file__).parent
    
    # libtorch_python.dylibなどの重要なバイナリを検索
    for pattern in ['*.dylib', '*.so']:
        for lib_file in torch_path.glob(f"**/{pattern}"):
            if lib_file.is_file():
                rel_path = lib_file.relative_to(torch_path.parent)
                pytorch_binaries.append((str(lib_file), str(rel_path.parent)))
                
except Exception as e:
    print(f"Warning: Failed to collect PyTorch binaries: {e}")

# Faissバイナリファイルを収集
faiss_binaries = []
try:
    import faiss
    faiss_path = Path(faiss.__file__).parent
    
    # faissのバイナリファイルを検索
    for pattern in ['*.dylib', '*.so']:
        for lib_file in faiss_path.glob(f"**/{pattern}"):
            if lib_file.is_file():
                rel_path = lib_file.relative_to(faiss_path.parent)
                faiss_binaries.append((str(lib_file), str(rel_path.parent)))
                
except Exception as e:
    print(f"Warning: Failed to collect Faiss binaries: {e}")

# PyAVバイナリファイルを収集
pyav_binaries = []
try:
    import av
    av_path = Path(av.__file__).parent
    
    # PyAVのバイナリファイルを検索
    for pattern in ['*.dylib', '*.so']:
        for lib_file in av_path.glob(f"**/{pattern}"):
            if lib_file.is_file():
                rel_path = lib_file.relative_to(av_path.parent)
                pyav_binaries.append((str(lib_file), str(rel_path.parent)))
                
except Exception as e:
    print(f"Warning: Failed to collect PyAV binaries: {e}")

# すべてのバイナリを結合
all_binaries = tkinter_binaries + pytorch_binaries + faiss_binaries + pyav_binaries

a = Analysis(
    ['/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/rvc_launcher.py'],
    pathex=[str(project_dir)],
    binaries=all_binaries,
    datas=datas,
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
        '_tkinter', 'tkinter.font', 'tkinter.constants',
        'rvc', 'rvc.wrapper', 'rvc.wrapper.cli', 'rvc.modules',
        'subprocess', 'threading', 'json', 'pathlib', 'datetime', 'time',
        'numpy', 'scipy', 'torch', 'torchaudio', 'librosa', 'soundfile',
        # PyTorch C拡張モジュール
        'torch._C',
        'torch._C._dynamo',
        'torch._C._profiler',
        'torch._C._autograd',
        'torch._C._nn',
        'torch._C._te',
        'torch._C._lazy',
        'torch._C._nvfuser',
        'torch._dynamo.eval_frame',
        'torch._dynamo.guards',
        'torch._dynamo.utils',
        'torch._inductor',
        'torch._inductor.codecache',
        # Faiss関連
        'faiss',
        'faiss._swigfaiss',
        'faiss.swigfaiss',
        'faiss.loader',
        # その他RVC依存関係
        'pyworld',
        'parselmouth',
        'crepe',
        'resampy',
        'audioread',
        'joblib',
        'threadpoolctl',
        # PyAV関連
        'av',
        'av.video',
        'av.audio',
        'av.container',
        'av.codec',
        'av.format',
        'av.stream',
        'av.filter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 問題のあるモジュールを一時的に除外
        'librosa.core',
        'librosa.util',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# librosaを個別に処理
import site
site_packages = site.getsitepackages()[0]
librosa_path = Path(site_packages) / 'librosa'
if librosa_path.exists():
    a.datas.append((str(librosa_path), 'librosa'))

pyz = PYZ(a.pure, a.zipped_data, cipher=None, compress_level=0)  # 圧縮を無効化

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
    name='RVC_Voice_Converter_Final',
)

app = BUNDLE(
    coll,
    name='RVC Voice Converter Final.app',
    icon='/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/app_icons/rvc_icon.icns',
    bundle_identifier='com.rvc.voiceconverter.final',
    version='1.0.0',
    info_plist={
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
    },
)
