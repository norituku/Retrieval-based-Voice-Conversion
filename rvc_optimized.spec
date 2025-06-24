# -*- mode: python ; coding: utf-8 -*-
"""
RVC Voice Converter - 最適化版PyInstaller設定
librosaのzlib圧縮エラーを回避するための設定
"""

import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# プロジェクトのベースディレクトリ
BASE_DIR = Path(SPECPATH)

# 分析用のメインスクリプト
main_script = str(BASE_DIR / 'standalone_build.py')

# 必要なデータファイルとバイナリの収集
datas = []
binaries = []
hiddenimports = []

# 基本的なデータファイル
datas += [
    (str(BASE_DIR / 'gui_settings.json'), '.'),
    (str(BASE_DIR / 'model_dir'), 'model_dir'),
    (str(BASE_DIR / 'rvc'), 'rvc'),
]

# アイコンファイル（存在する場合）
icon_path = BASE_DIR / 'assets' / 'icon.icns'
if not icon_path.exists():
    icon_path = None

# librosaとその依存関係を特別に処理
# librosaを非圧縮で含める
print("Collecting librosa and dependencies...")

# 1. librosaの完全収集（圧縮を避ける）
librosa_datas, librosa_binaries, librosa_hiddenimports = collect_all('librosa')
datas += librosa_datas
binaries += librosa_binaries
hiddenimports += librosa_hiddenimports

# 2. 重要な依存関係の収集
critical_packages = [
    'numpy',
    'scipy',
    'numba',
    'soundfile',
    'audioread',
    'resampy',
    'pooch',
    'decorator',
    'joblib',
    'lazy_loader',
    'soxr',
    'msgpack',
]

for package in critical_packages:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
    except Exception as e:
        print(f"Warning: Could not collect {package}: {e}")

# 3. 追加の隠しインポート
hiddenimports += [
    'sklearn',
    'sklearn.utils',
    'sklearn.utils._typedefs',
    'sklearn.neighbors',
    'sklearn.neighbors._binary_tree',
    'sklearn.neighbors._partition_nodes',
    'librosa.core',
    'librosa.core.audio',
    'librosa.core.convert',
    'librosa.core.notation',
    'librosa.core.pitch',
    'librosa.core.spectrum',
    'librosa.core.fft',
    'librosa.core.constantq',
    'librosa.util',
    'librosa.util.decorators',
    'librosa.util.exceptions',
    'librosa.util.utils',
    'librosa.feature',
    'librosa.effects',
    'librosa.filters',
    'librosa.onset',
    'librosa.beat',
    'librosa.decompose',
    'librosa.segment',
    'librosa.sequence',
    '_cffi_backend',
    'soundfile._soundfile',
]

# PyTorch関連（必要な場合）
try:
    import torch
    torch_datas, torch_binaries, torch_hiddenimports = collect_all('torch')
    datas += torch_datas
    binaries += torch_binaries
    hiddenimports += torch_hiddenimports
except:
    print("PyTorch not found, skipping...")

# 分析設定
a = Analysis(
    [main_script],
    pathex=[str(BASE_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'setuptools',
        'wheel',
        'pip',
    ],
    noarchive=True,  # アーカイブを作成しない（圧縮エラーを回避）
    optimize=0,  # 最適化を無効化
)

# PYZアーカイブ（圧縮レベルを調整）
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
    compress_level=0,  # 圧縮を無効化
)

# 実行ファイル
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RVC Voice Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX圧縮を無効化
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path else None,
)

# macOSアプリバンドル
app = BUNDLE(
    exe,
    name='RVC Voice Converter.app',
    icon=str(icon_path) if icon_path else None,
    bundle_identifier='com.rvc.voiceconverter',
    info_plist={
        'CFBundleName': 'RVC Voice Converter',
        'CFBundleDisplayName': 'RVC Voice Converter',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.15',
        'NSMicrophoneUsageDescription': 'Voice Converterは音声処理のためにマイクへのアクセスが必要です。',
    },
)
