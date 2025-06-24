# hook-soundfile.py
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# soundfileのデータファイルとダイナミックライブラリを収集
datas = collect_data_files('soundfile')
binaries = collect_dynamic_libs('soundfile')

# _soundfileモジュールも確実に含める
hiddenimports = ['_soundfile', '_soundfile_data'] 