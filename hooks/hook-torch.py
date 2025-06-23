# PyInstaller hook for torch - RVC用完全版

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs
import os
import torch

# 必要なサブモジュールを収集
hiddenimports = [
    'torch',
    'torch._C',  # 最重要: C++拡張モジュール
    'torch._C._dynamo',
    'torch._C._distributed_c10d',
    'torch._C._distributed_rpc',
    'torch._C._distributed_autograd',
    'torch._C._nn',
    'torch._C._fft',
    'torch._C._linalg',
    'torch._C._nested',
    'torch._C._sparse',
    'torch._C._special',
    'torch.nn',
    'torch.nn.functional',
    'torch.nn.modules',
    'torch.nn.parameter',
    'torch.utils',
    'torch.utils.data',
    'torch._ops',
    'torch._utils',
    'torch.autograd',
    'torch.jit',
    'torch.onnx',
    'torch.backends',
    'torch.backends.mps',  # Apple Silicon用
    'torch._dynamo',
    'torch._inductor',
    # CUDA関連（macOSでも最小限のインポートエラー回避用）
    'torch.cuda',
    'torch.cuda._utils',
    'torch.cuda._lazy_init',
    'torch.cuda.random',
    'torch.cuda.sparse',
    'torch.cuda.profiler',
    'torch.cuda.nvtx',
]

# 除外するサブモジュール（重いが不要な部分のみ）
excludedimports = [
    'torch.testing',
    'torch.test',
    'torch.utils.benchmark',
    'torch.utils.bottleneck',
    'torch.utils.cpp_extension',
    'torch.utils.tensorboard',
    # 'torch.distributed',  # ← 削除：torch.nnが依存しているため
    'torch.backends.cuda',
    'torch.backends.cudnn',
    'torch.profiler',
    'torch.ao.quantization',
    'torch.fx',
    'torch.package',
    # 重い分散処理の実装部分のみ除外
    'torch.distributed.rpc',
    'torch.distributed.pipeline',
    'torch.distributed.optim',
    'torch.distributed.elastic',
    'torch.distributed.fsdp',
]

# PyTorchのデータファイルを収集
datas = collect_data_files('torch', include_py_files=False)

# 重要: torch._C のダイナミックライブラリを収集
binaries = collect_dynamic_libs('torch')

# 重要: torch/binディレクトリを明示的に追加（torch_shm_managerを含む）
torch_path = os.path.dirname(torch.__file__)
torch_bin_path = os.path.join(torch_path, 'bin')
if os.path.exists(torch_bin_path):
    # torch/binディレクトリ全体を追加
    datas.append((torch_bin_path, 'torch/bin'))

# その他の重要なファイル
torch_lib_path = os.path.join(torch_path, 'lib')
if os.path.exists(torch_lib_path):
    # torch/libディレクトリも追加（ダイナミックライブラリ用）
    datas.append((torch_lib_path, 'torch/lib')) 