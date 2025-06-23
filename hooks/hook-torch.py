# PyInstaller hook for torch - RVC用完全版

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs
import os
import torch

# 必要なサブモジュールを収集
# 注意: torch._Cサブモジュール（_dynamo, _nn等）はC++拡張内部の属性であり、
# Pythonモジュールとして存在しないため、hidden importsでは収集不可能
hiddenimports = [
    'torch',
    'torch._C',  # 最重要: C++拡張モジュール本体のみ
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
    # 分散処理基盤（torch.nnが依存）
    'torch.distributed',
    'torch.distributed.distributed_c10d',
    'torch.distributed._backend',
    'torch.distributed.constants',
    'torch.distributed.device_mesh',
    'torch.distributed.launcher',
    'torch.distributed.nn',
    'torch.distributed.tensor',
    'torch.distributed.utils',
    # RPC関連（torch._jit_internalが依存）
    'torch.distributed.rpc',
    'torch.distributed.rpc._testing',
    'torch.distributed.rpc.api',
    'torch.distributed.rpc.backend_registry',
    'torch.distributed.rpc.constants',
    'torch.distributed.rpc.functions',
    'torch.distributed.rpc.internal',
    'torch.distributed.rpc.options',
    'torch.distributed.rpc.rref_proxy',
    'torch.distributed.rpc.server_process_global_profiler',
    'torch.distributed.rpc.utils',
    'torch.distributed.rpc.worker_info',
    # CUDA関連（macOSでも最小限のインポートエラー回避用）
    'torch.cuda',
    'torch.cuda._utils',
    'torch.cuda._lazy_init',
    'torch.cuda.random',
    'torch.cuda.sparse',
    'torch.cuda.profiler',
    'torch.cuda.nvtx',
    # Testing関連（torch.autograd.gradcheckが依存）
    'torch.testing',
    'torch.testing._internal',
    # Package関連（torch._jit_internalが依存）
    'torch.package',
    'torch.package._mangling',
    'torch.package._package_pickler',
    'torch.package._package_unpickler',
    # JIT関連（内部依存関係を事前に含める）
    'torch._jit_internal',
    'torch.jit._script',
    'torch.jit._trace',
    'torch.jit._fuser',
    # FX関連（潜在的依存関係を事前に含める）
    'torch.fx.graph',
    'torch.fx.node',
    'torch.fx.proxy',
    'torch.fx.interpreter',
    # AO関連（潜在的依存関係を事前に含める）
    'torch.ao.nn',
    'torch.ao.nn.intrinsic',
    'torch.ao.nn.qat',
    'torch.ao.nn.quantized',
    # Backends関連（循環インポート回避のため明示的に含める）
    'torch.backends',
    'torch.backends.cuda',
    'torch.backends.cudnn',
    'torch.backends.mps',
    'torch.backends.mkl',
    'torch.backends.mkldnn',
    'torch.backends.openmp',
    'torch.backends.opt_einsum',
    'torch.backends.quantized',
    'torch.backends.xnnpack',
    # Profiler関連（循環インポート回避のため明示的に含める）
    'torch.profiler',
    'torch.profiler.profiler',
    'torch.profiler.utils',
    # Python標準ライブラリ（PyTorchが依存）
    'unittest',
    'unittest.mock',
    'unittest.util',
    'unittest.case',
    'unittest.result',
    'unittest.suite',
    'unittest.loader',
    'unittest.main',
    'unittest.runner',
    'unittest.signals',
    # Export関連（torch.export.__init__が依存）
    'torch.export',
    'torch.export.dynamic_shapes',
    'torch.export.graph_signature',
    # Guards関連（torch._guardsが依存）
    'torch._guards',
    'torch.fx.experimental',
    'torch.fx.experimental.symbolic_shapes',
]

# 除外するサブモジュール（循環インポート回避のため最小限）
excludedimports = [
    'torch.test',  # テスト実行のみ除外
    'torch.utils.benchmark',  # ベンチマーク機能のみ除外
    'torch.utils.bottleneck',  # デバッグツールのみ除外
    'torch.utils.cpp_extension',  # C++拡張ビルドツールのみ除外
    'torch.utils.tensorboard',  # TensorBoard統合のみ除外
    # 'torch.distributed',  # ← 削除：torch.nnが依存しているため
    # 'torch.backends.cuda',  # ← コメントアウト：循環インポート回避のため含める
    # 'torch.backends.cudnn',  # ← コメントアウト：循環インポート回避のため含める
    # 'torch.profiler',  # ← コメントアウト：循環インポート回避のため含める
    # 'torch.ao.quantization',  # ← コメントアウト：潜在的依存のため含める
    # 'torch.fx',  # ← コメントアウト：潜在的依存のため含める
    # 'torch.package',  # ← コメントアウト：torch._jit_internalが依存
    # 重い分散処理の実装部分のみ除外
    # 'torch.distributed.rpc',  # ← コメントアウト：torch._jit_internalが依存
    'torch.distributed.pipeline',  # パイプライン並列のみ除外
    'torch.distributed.optim',  # 分散最適化のみ除外
    'torch.distributed.elastic',  # エラスティック訓練のみ除外
    'torch.distributed.fsdp',  # FSDP（Fully Sharded Data Parallel）のみ除外
]

# PyTorchのデータファイルを収集
datas = collect_data_files('torch', include_py_files=False)

# 重要: torch._C と関連するダイナミックライブラリを収集
binaries = collect_dynamic_libs('torch')

# torch._Cとその依存関係を正しい場所に配置するための追加処理
torch_path = os.path.dirname(torch.__file__)

# torch/libディレクトリのすべてのdylibファイルを明示的に追加
torch_lib_path = os.path.join(torch_path, 'lib')
if os.path.exists(torch_lib_path):
    # libディレクトリの内容をtorch/lib以下に配置（重要）
    import glob
    for lib_file in glob.glob(os.path.join(torch_lib_path, '*.dylib')):
        # ファイル名を取得
        lib_name = os.path.basename(lib_file)
        # torch/libディレクトリに配置するよう指定
        binaries.append((lib_file, 'torch/lib'))

# _C.*.soファイルを明示的に追加
import glob
c_extensions = glob.glob(os.path.join(torch_path, '_C*.so'))
for c_ext in c_extensions:
    # torch/ディレクトリ直下に配置
    binaries.append((c_ext, 'torch'))

# torch/binディレクトリを明示的に追加（torch_shm_managerを含む）
torch_bin_path = os.path.join(torch_path, 'bin')
if os.path.exists(torch_bin_path):
    datas.append((torch_bin_path, 'torch/bin'))

# torch/libディレクトリ全体もデータとして追加（ダイナミックライブラリ用）
if os.path.exists(torch_lib_path):
    datas.append((torch_lib_path, 'torch/lib'))

# torch依存ライブラリをtorch/lib配下に手動配置
torch_libs = []
for binary_src, binary_dest in binaries:
    # torchライブラリをtorch/lib配下に再配置
    if 'torch' in binary_src and binary_dest == '.':
        torch_libs.append((binary_src, 'torch/lib'))
    else:
        torch_libs.append((binary_src, binary_dest))

# 修正されたbinariesリストで置き換え
binaries = torch_libs

# 重要: torch._Cモジュールの確実な収集を保証
# torch._Cは単一のバイナリファイル（.so/.dylib）として実装されている
try:
    import torch._C
    # _Cモジュールのパスを直接取得
    if hasattr(torch._C, '__file__') and torch._C.__file__:
        c_module_path = torch._C.__file__
        print(f"[hook-torch] Found torch._C at: {c_module_path}")
        
        # 重要: torch._CをResourcesディレクトリのtorch/下に直接配置（シンボリックリンクを避ける）
        # binariesではなくdatasとして追加することで、正しい場所に配置
        datas.append((c_module_path, 'torch'))
        print(f"[hook-torch] torch._C added as data file to torch/ directory")
        
        # また、binariesとしても追加（二重保険）
        binaries.append((c_module_path, 'torch'))
        print(f"[hook-torch] torch._C also added as binary to torch/ directory")
        
        # torch/_Cディレクトリの確認（存在する場合）
        c_module_dir = os.path.dirname(c_module_path)
        if '_C' in os.path.basename(c_module_dir):
            # _Cディレクトリが存在する場合、そのディレクトリ全体を収集
            for file in os.listdir(c_module_dir):
                if file.endswith(('.so', '.dylib', '.dll', '.pyd')):
                    file_path = os.path.join(c_module_dir, file)
                    binaries.append((file_path, os.path.basename(c_module_dir)))
                    print(f"[hook-torch] Additional _C binary: {file}")
    else:
        print(f"[hook-torch] torch._C.__file__ not available: {torch._C}")
        
except Exception as e:
    print(f"[hook-torch] Warning: Could not explicitly collect torch._C: {e}")

# PyTorch初期化に必要な環境変数をビルド時にセット
import os
os.environ['PYTORCH_DISABLE_PER_OP_PROFILING'] = '1'  # プロファイリング無効化
os.environ['PYTORCH_DISABLE_NUMPY_WARNING'] = '1'    # NumPy警告無効化 