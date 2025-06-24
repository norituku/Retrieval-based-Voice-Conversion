"""
PyInstaller hook for audio processing libraries
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# Collect librosa
datas_librosa, binaries_librosa, hiddenimports_librosa = collect_all('librosa')
datas = datas_librosa
binaries = binaries_librosa
hiddenimports = hiddenimports_librosa

# Add other audio processing libraries
hiddenimports += collect_submodules('soundfile')
hiddenimports += collect_submodules('scipy')
hiddenimports += collect_submodules('scipy.signal')
hiddenimports += collect_submodules('resampy')
hiddenimports += collect_submodules('pyworld')
hiddenimports += collect_submodules('praat-parselmouth')
hiddenimports += collect_submodules('parselmouth')

# Add specific imports that might be missed
hiddenimports += [
    'scipy.signal.windows',
    'scipy.fft',
    'scipy.fftpack',
    'scipy.interpolate',
    'audioread',
    'soundfile',
    '_soundfile',
    '_soundfile_data',
]

# Platform specific audio libraries
import sys
if sys.platform == "darwin":
    # macOS specific audio libraries
    import os
    import soundfile
    sf_dir = os.path.dirname(soundfile.__file__)
    
    # Look for libsndfile
    libsndfile_paths = [
        os.path.join(sf_dir, '_soundfile_data', 'libsndfile.dylib'),
        '/usr/local/lib/libsndfile.dylib',
        '/opt/homebrew/lib/libsndfile.dylib',
    ]
    
    for path in libsndfile_paths:
        if os.path.exists(path):
            binaries.append((path, '_soundfile_data'))
            break
