# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# プロジェクトルート
project_root = Path.cwd()

# メインスクリプト
main_script = "gui_dark_mode.py"

# データファイル
datas = [
    ('rvc', 'rvc'),
    ('model_dir', 'model_dir'),
]

# 隠しインポート
hiddenimports = [
    'rvc',
    'torch', 'torchaudio', 'numpy', 'librosa', 'scipy',
    'sklearn', 'faiss', 'pyworld', 'parselmouth', 'crepe',
    'resampy', 'ffmpeg-python', 'soundfile',
    'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
    'threading', 'queue', 'subprocess', 'json', 'logging'
]

# 除外モジュール
excludes = ['test', 'tests', 'testing', 'unittest', 'pdb']

block_cipher = None

a = Analysis(
    [main_script],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
    runtime_hooks=['hooks/runtime_hook.py'],
    excludes=excludes,
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
    name='VoiceConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch='arm64',
    codesign_identity=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='VoiceConverter',
)

app = BUNDLE(
    coll,
    name='VoiceConverter.app',
    icon='app_icons/rvc_icon.icns',
    bundle_identifier='com.rvc.voiceconverter',
    version='1.0.0',
    info_plist={
        'LSEnvironment': {
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
        },
        'NSHighResolutionCapable': True,
    },
)
# === PyInstaller自体のPython環境を最大活用 ===
# PyInstaller環境が既に完全なPython 3.11環境を含むため、
# 追加の埋め込みPythonは不要。sys.executableで実行時解決。
