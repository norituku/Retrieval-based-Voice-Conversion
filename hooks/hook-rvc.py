"""
PyInstaller hook for RVC modules
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all RVC modules
hiddenimports = collect_submodules('rvc')

# Add specific RVC modules that might be missed
hiddenimports += [
    'rvc.configs',
    'rvc.configs.config',
    'rvc.lib',
    'rvc.lib.audio',
    'rvc.lib.infer_pack',
    'rvc.lib.infer_pack.models',
    'rvc.lib.infer_pack.models_onnx',
    'rvc.lib.infer_pack.onnx_inference',
    'rvc.lib.infer_pack.commons',
    'rvc.lib.infer_pack.modules',
    'rvc.lib.infer_pack.transforms',
    'rvc.lib.infer_pack.attentions',
    'rvc.lib.utils',
    'rvc.modules',
    'rvc.modules.vc',
    'rvc.modules.vc.modules',
    'rvc.modules.vc.pipeline',
    'rvc.modules.vc.utils',
    'rvc.wrapper',
    'rvc.wrapper.cli',
    'rvc.wrapper.cli.cli',
    'rvc.wrapper.cli.handler',
    'rvc.wrapper.cli.handler.infer',
]

# Collect data files
datas = []
