# PyInstaller hook for torch - 最小サイズ版

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 必要最小限のサブモジュールのみ収集
hiddenimports = [
    'torch',
    'torch.nn',
    'torch.nn.functional',
    'torch.nn.modules',
    'torch.nn.parameter',
    'torch.utils',
    'torch.utils.data',
    'torch._C',
    'torch._ops',
    'torch._utils',
    'torch.autograd',
    'torch.jit',
    'torch.onnx',
]

# 除外するサブモジュール
excludedimports = [
    'torch.testing',
    'torch.test',
    'torch.utils.benchmark',
    'torch.utils.bottleneck',
    'torch.utils.cpp_extension',
    'torch.utils.tensorboard',
    'torch.distributed',
    'torch.multiprocessing',
    'torch.cuda',  # CUDAは不要
    'torch.backends.cuda',
    'torch.backends.cudnn',
    'torch.profiler',
    'torch.ao.quantization',
    'torch.fx',
    'torch.package',
]

# データファイルは最小限に
datas = [] 