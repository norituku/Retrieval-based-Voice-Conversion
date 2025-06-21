# PyInstaller hook for numpy - 最小サイズ版

from PyInstaller.utils.hooks import collect_submodules

# 必要最小限のサブモジュールのみ
hiddenimports = [
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    'numpy.core.multiarray',
    'numpy.core.numeric',
    'numpy.linalg',
    'numpy.fft',
    'numpy.random',
]

# 除外するサブモジュール
excludedimports = [
    'numpy.testing',
    'numpy.tests',
    'numpy.f2py',
    'numpy.distutils',
    'numpy.doc',
    'numpy.matrixlib',
    'numpy.polynomial.tests',
    'numpy.random.tests',
    'numpy.core.tests',
    'numpy.lib.tests',
    'numpy.ma.tests',
] 