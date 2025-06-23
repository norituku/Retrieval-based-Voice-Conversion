# PyInstaller hook for numpy - RVC用完全版

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# NumPyの全サブモジュールを収集（エラー回避のため）
hiddenimports = collect_submodules('numpy')

# 特に重要な内部モジュールを明示的に追加
hiddenimports += [
    'numpy.core._multiarray_umath',
    'numpy.core._multiarray_tests',  # これが不足していた
    'numpy.core._internal',
    'numpy.core._dtype',
    'numpy.core._dtype_ctypes',
    'numpy.core._methods',
    'numpy.core._add_newdocs',
    'numpy.core._add_newdocs_scalars',
    'numpy.core.function_base',
    'numpy.core.getlimits',
    'numpy.core.arrayprint',
    'numpy.core.defchararray',
    'numpy.core.records',
    'numpy.core.shape_base',
    'numpy.core.fromnumeric',
    'numpy.core.memmap',
    'numpy.core.numerictypes',
    'numpy.core.overrides',
    'numpy.core._ufunc_config',
    'numpy.core._string_helpers',
    'numpy.core._asarray',
    'numpy.core._exceptions',
    'numpy.core.umath',
    'numpy.core.multiarray',
    'numpy.lib.format',
    'numpy.lib.mixins',
    'numpy.lib.scimath',
    'numpy.compat.py3k',
]

# NumPyのデータファイルも含める
datas = collect_data_files('numpy')

# テスト関連は除外（サイズ削減のため）
excludedimports = [
    'numpy.testing',
    'numpy.tests',
    'numpy.distutils',
    'numpy.doc',
] 