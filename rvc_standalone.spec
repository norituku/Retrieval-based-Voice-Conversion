# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# プロジェクトルート
project_root = Path.cwd()

# メインスクリプト（完全独立版）
main_script = "rvc_standalone_app.py"

# データファイル
datas = [
    ('rvc', 'rvc'),
    ('model_dir', 'model_dir'),
    ('app_icons', 'app_icons'),
]

# 隠しインポート（完全独立版用）
hiddenimports = [
    # RVC関連
    'rvc',
    'rvc.configs',
    'rvc.configs.config',
    'rvc.modules',
    'rvc.modules.vc',
    'rvc.modules.vc.modules',
    'rvc.modules.vc.pipeline',
    'rvc.modules.vc.utils',
    'rvc.lib',
    'rvc.lib.audio',
    'rvc.lib.infer_pack',
    'rvc.lib.infer_pack.models',
    'rvc.wrapper',
    'rvc.wrapper.cli',
    'rvc.wrapper.cli.cli',
    'rvc.wrapper.cli.handler',
    'rvc.wrapper.cli.handler.infer',
    
    # 音声処理
    'torch',
    'torchaudio',
    'numpy',
    'librosa',
    'scipy',
    'scipy.signal',
    'soundfile',
    'resampy',
    'pyworld',
    'parselmouth',
    'crepe',
    'faiss',
    
    # PyQt5
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    
    # その他必須
    'sklearn',
    'ffmpeg',
    'pydub',
    'click',
    'click.testing',
    'dotenv',
    'pathlib',
    'json',
    'logging',
    'threading',
    'queue',
    'subprocess',
    '_cffi_backend',
    'cffi',
]

# 除外モジュール（Poetry関連を除外）
excludes = [
    'test',
    'tests',
    'testing',
    'unittest',
    'pdb',
    'poetry',
    'poetry.core',
    'pip',
    'setuptools',
    'wheel',
]

# フックパス
hookspath = ['hooks']

# ランタイムフック（存在する場合）
runtime_hooks = []
runtime_hook_path = project_root / 'hooks' / 'runtime_hook.py'
if runtime_hook_path.exists():
    runtime_hooks = [str(runtime_hook_path)]

block_cipher = None

a = Analysis(
    [main_script],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=hookspath,
    runtime_hooks=runtime_hooks,
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
    name='RVCStandalone',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # GUIアプリケーション
    target_arch='arm64',  # M1/M2 Mac用
    codesign_identity='-',  # アドホック署名
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='RVCStandalone',
)

app = BUNDLE(
    coll,
    name='RVCStandalone.app',
    icon='app_icons/rvc_icon.icns',
    bundle_identifier='com.rvc.standalone',
    version='1.0.0',
    info_plist={
        'LSEnvironment': {
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin'
        },
        'NSHighResolutionCapable': True,
        'NSMicrophoneUsageDescription': 'RVC needs access to audio files for voice conversion.',
        'CFBundleDisplayName': 'RVC Standalone',
        'CFBundleShortVersionString': '1.0.0',
    },
) 