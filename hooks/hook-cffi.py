"""
PyInstaller hook for CFFI - macOS署名問題を解決
"""
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

# CFFFIの動的ライブラリとサブモジュールを明示的に収集
datas = []
binaries = []

# cffiサブモジュールを収集
hiddenimports = collect_submodules('cffi') + ['_cffi_backend']

# cffi関連バイナリを収集
try:
    binaries.extend(collect_dynamic_libs('cffi'))
except:
    pass