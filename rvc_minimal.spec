# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path
import platform

# プロジェクトルート
project_root = Path.cwd()

# メインスクリプト
main_script = "gui_dark_mode.py"

# データファイル
datas = [
    ('rvc', 'rvc'),
    ('model_dir', 'model_dir'),
    ('rvc_worker.py', '.'),
]

# PyTorchライブラリを含める
import torch
torch_path = Path(torch.__file__).parent
torch_lib = torch_path / 'lib'
if torch_lib.exists():
    datas.append((str(torch_lib), 'torch/lib'))

# torch._Cバイナリを明示的に含める（シンボリックリンク問題対策）
try:
    import torch._C
    if hasattr(torch._C, '__file__') and torch._C.__file__:
        torch_c_path = torch._C.__file__
        datas.append((torch_c_path, 'torch'))
        print(f"[spec] torch._C binary explicitly added: {torch_c_path}")
except Exception as e:
    print(f"[spec] Warning: Could not add torch._C: {e}")

# 隠しインポート
hiddenimports = [
    'rvc',
    'rvc.configs.config', 'rvc.modules.vc.modules',
    # torchモジュール全体の完全収集
    'torch', 'torch._C', 'torch._C._fft', 'torch._C._linalg', 'torch._C._nn',
    'torch.distributed', 'torch.distributed.distributed_c10d', 'torch.distributed.rpc',
    'torch.backends', 'torch.backends.cuda', 'torch.backends.cudnn',
    'torch.testing', 'torch.package', 'torch.package.importer',
    'torch.nn', 'torch.nn.functional', 'torch.nn.modules',
    'torch.optim', 'torch.autograd', 'torch.utils', 'torch.utils.data',
    'torch.jit', 'torch.fx', 'torch.overrides',
    'torchaudio', 'numpy', 'librosa', 'scipy',
    'sklearn', 'faiss', 'pyworld', 'parselmouth', 'crepe',
    'resampy', 'ffmpeg-python', 'soundfile',
    # fairseq関連モジュール（音声変換に必要）
    'fairseq', 'fairseq.checkpoint_utils', 'fairseq.dataclass',
    'fairseq.dataclass.configs', 'fairseq.distributed',
    'fairseq.models', 'fairseq.modules', 'fairseq.tasks',
    'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
    'threading', 'queue', 'subprocess', 'json', 'logging',
    'unittest', 'unittest.mock',  # Python標準ライブラリ（PyTorchのtorch._guards依存）
    '_cffi_backend', 'cffi',
    # soundfile依存関係
    '_soundfile', '_soundfile_data',
    # その他の欠落している可能性のあるモジュール
    'click', 'click.testing', 'dotenv',
    # parselmouth関連（F0推定に必須）
    'praat_parselmouth', 'parselmouth._parselmouth',
    # pdb関連（fairseqが必要とする）
    'pdb', 'bdb', 'cmd',
]

# 除外モジュール（torchは除外しない）
excludes = ['test', 'tests', 'testing']  # pdbは除外しない（fairseqが必要とするため）

block_cipher = None

# libsndfileライブラリを探して含める
binaries = []

# parselmouthのC拡張を収集
try:
    import praat_parselmouth
    parselmouth_path = Path(praat_parselmouth.__file__).parent
    # parselmouthの.soファイルを収集
    for so_file in parselmouth_path.glob('*.so'):
        binaries.append((str(so_file), 'praat_parselmouth'))
    for dylib_file in parselmouth_path.glob('*.dylib'):
        binaries.append((str(dylib_file), 'praat_parselmouth'))
except ImportError:
    print("[spec] Warning: praat_parselmouth not found for binary collection")

# macOSでlibsndfileを探す
if platform.system() == 'Darwin':
    import subprocess
    try:
        # Homebrewからlibsndfileのパスを取得
        result = subprocess.run(['brew', '--prefix', 'libsndfile'],
                               capture_output=True, text=True)
        if result.returncode == 0:
            libsndfile_prefix = result.stdout.strip()
            libsndfile_path = f"{libsndfile_prefix}/lib/libsndfile.dylib"
            if os.path.exists(libsndfile_path):
                binaries.append((libsndfile_path, '.'))
    except:
        pass

a = Analysis(
    [main_script],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
    runtime_hooks=['hooks/runtime_hook.py'],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,  # アーカイブ圧縮を無効化（zlib破損エラー対策）
    # torchモジュールを確実に収集（pyzは使わずpyのみ）
    module_collection_mode={
        'torch': 'py',  # pyファイルとして収集（pyzアーカイブは使わない）
        'torch.*': 'py',  # すべてのtorchサブモジュールも同様
        'librosa': 'py',  # librosaも非圧縮で収集
        'librosa.*': 'py',  # librosaサブモジュールも同様
        'soundfile': 'py',  # soundfileも非圧縮
        'scipy': 'py',  # scipyも非圧縮（大きなモジュール）
        'scipy.*': 'py',
        'numpy': 'py',  # numpyも非圧縮
        'numpy.*': 'py',
    },
)

# PYZ圧縮を完全に無効化
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
    compress_level=0  # 圧縮レベル0 = 無圧縮
)

# UPX圧縮を無効化（Apple Siliconと互換性問題あり）
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
    codesign_identity='-',
    # 無限ループ防止
    argv_emulation=False,
    disable_windowed_traceback=False,
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
        'LSMultipleInstancesProhibited': True,  # 複数インスタンス禁止
        'LSUIElement': False,  # ドックに表示
    },
)
# === PyInstaller自体のPython環境を最大活用 ===
# PyInstaller環境が既に完全なPython 3.11環境を含むため、
# 追加の埋め込みPythonは不要。sys.executableで実行時解決。
