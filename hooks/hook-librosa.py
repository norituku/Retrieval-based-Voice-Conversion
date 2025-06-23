"""
PyInstaller Hook for librosa
librosaとその依存関係を正しく処理するためのフック
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files
import os

# librosaの完全な収集
datas, binaries, hiddenimports = collect_all('librosa')

# 追加のサブモジュール
hiddenimports += collect_submodules('librosa')

# lazy_loaderの特別な処理
hiddenimports += [
    'lazy_loader',
    'lazy_loader._load',
    'lazy_loader._stub',
]

# 重要な依存関係の明示的な追加
hiddenimports += [
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    'scipy',
    'scipy.signal',
    'scipy.fftpack',
    'scipy.special',
    'scipy.linalg',
    'numba',
    'numba.core',
    'numba.typed',
    'soundfile',
    'audioread',
    'audioread.ffdec',
    'audioread.macca',
    'audioread.gstdec',
    'audioread.rawread',
    'resampy',
    'pooch',
    'decorator',
    'joblib',
    'sklearn',
    'sklearn.utils',
    'sklearn.utils._typedefs',
    'sklearn.neighbors',
    'packaging',
    'msgpack',
    'soxr',
]

# libsndfileのバイナリを確実に含める
try:
    import soundfile
    sf_path = os.path.dirname(soundfile.__file__)

    # macOS用のdylib
    for lib_name in ['_soundfile.dylib', 'libsndfile.dylib', 'libsndfile.1.dylib']:
        lib_path = os.path.join(sf_path, lib_name)
        if os.path.exists(lib_path):
            binaries += [(lib_path, '.')]
except:
    pass

# NumPyのバイナリを確実に含める（アーキテクチャに注意）
try:
    import numpy
    np_path = os.path.dirname(numpy.__file__)

    # 重要なバイナリモジュール
    important_binaries = [
        'core/_multiarray_umath.cpython-*.so',
        'core/_multiarray_tests.cpython-*.so',
        'fft/_pocketfft_internal.cpython-*.so',
        'linalg/_umath_linalg.cpython-*.so',
        'random/_common.cpython-*.so',
        'random/_mt19937.cpython-*.so',
    ]

    for pattern in important_binaries:
        import glob
        for file_path in glob.glob(os.path.join(np_path, pattern)):
            if os.path.exists(file_path):
                rel_path = os.path.relpath(file_path, np_path)
                binaries += [(file_path, os.path.join('numpy', os.path.dirname(rel_path)))]
except:
    pass

# データファイルの追加
try:
    import librosa
    librosa_path = os.path.dirname(librosa.__file__)

    # example_dataなどのデータファイル
    example_data = os.path.join(librosa_path, 'util', 'example_data')
    if os.path.exists(example_data):
        datas += [(example_data, 'librosa/util')]
except:
    pass

# 環境変数の設定を推奨
print("Note: Set PYINSTALLER_COMPILE_BOOTLOADER=1 for better compatibility")
