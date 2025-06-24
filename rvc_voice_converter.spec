# -*- mode: python ; coding: utf-8 -*-
"""
RVC Voice Converter - PyInstaller Spec File
圧縮を無効化し、完全なスタンドアロンアプリケーションを作成
"""

import os
import sys
from pathlib import Path

# プロジェクトのベースディレクトリ
BASE_DIR = Path(SPECPATH)

# アプリケーション情報
APP_NAME = 'RVC Voice Converter Final'
BUNDLE_ID = 'com.rvc.voiceconverter'
VERSION = '2.0.0'

# Analysis設定
a = Analysis(
    ['gui_dark_mode.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=[
        # RVCモジュール全体をコピー
        ('rvc', 'rvc'),
        # モデルディレクトリ
        ('model_dir', 'model_dir'),
        # 設定ファイル
        ('gui_settings.json', '.'),
        ('rvc_config.py', '.'),
        ('run_inference.py', '.'),
        # アセット
        ('assets', 'assets'),
    ],
    hiddenimports=[
        # RVC関連
        'rvc',
        'rvc.wrapper',
        'rvc.wrapper.cli',
        'rvc.wrapper.cli.handler',
        'rvc.wrapper.cli.handler.infer',
        'rvc.modules',
        'rvc.modules.vc',
        'rvc.modules.vc.modules',
        'rvc.lib',
        'rvc.lib.audio',

        # 音声処理
        'librosa',
        'librosa.core',
        'librosa.feature',
        'librosa.effects',
        'librosa.filters',
        'librosa.decompose',
        'librosa.util',
        'soundfile',
        'audioread',
        'resampy',

        # 科学計算
        'numpy',
        'numpy.core',
        'numpy.core.multiarray',
        'scipy',
        'scipy.signal',
        'scipy.io',
        'scipy.io.wavfile',
        'scipy.fft',
        'scipy.interpolate',
        'numba',
        'numba.core',
        'numba.typed',

        # PyTorch
        'torch',
        'torch._C',
        'torch.nn',
        'torch.nn.functional',
        'torch.optim',
        'torch.utils',
        'torch.utils.data',
        'torch.backends',
        'torch.backends.mps',
        'torch.backends.cuda',
        'torchaudio',

        # その他
        'joblib',
        'sklearn',
        'sklearn.preprocessing',
        'sklearn.utils',
        'packaging',
        'pooch',
        'decorator',
        'audioread.ffdec',
        'audioread.macca',
        'audioread.gstdec',
        'audioread.maddec',
        'audioread.rawread',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'PIL',
        'IPython',
        'jupyter',
        'notebook',
        'pandas',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    # 圧縮を無効化
    noarchive=True,
)

# PYZアーカイブ（圧縮なし）
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
    # 圧縮レベルを0に設定（無圧縮）
    compress_level=0,
)

# EXE設定
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX圧縮を無効化
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.icns' if Path('assets/icon.icns').exists() else None,
)

# macOSアプリバンドル
app = BUNDLE(
    exe,
    name=f'{APP_NAME}.app',
    icon='assets/icon.icns' if Path('assets/icon.icns').exists() else None,
    bundle_identifier=BUNDLE_ID,
    version=VERSION,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': 'Voice Converter Application',
        'CFBundleIdentifier': BUNDLE_ID,
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.15.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'NSMicrophoneUsageDescription': 'Voice Converter needs access to microphone for audio processing.',
        'LSApplicationCategoryType': 'public.app-category.music',
    },
)
