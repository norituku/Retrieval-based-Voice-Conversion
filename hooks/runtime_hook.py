# PyInstaller ランタイムフック - 最小限の環境設定

import os
import sys

# 重複実行防止
if os.environ.get('RVC_RUNTIME_HOOK_LOADED'):
    sys.exit(0)
os.environ['RVC_RUNTIME_HOOK_LOADED'] = '1'

# 環境変数の設定
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['PYTORCH_DISABLE_MPS'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['PYTHONWARNINGS'] = 'ignore'

# PyInstaller環境でのモジュールパス設定
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    bundle_dir = sys._MEIPASS
    
    # 標準ライブラリ競合回避
    import random as stdlib_random
    import tempfile as stdlib_tempfile
    sys.modules['random'] = stdlib_random
    sys.modules['tempfile'] = stdlib_tempfile
    
    # macOSアプリケーションバンドルの場合
    if sys.platform == "darwin":
        app_dir = bundle_dir
        while app_dir and not app_dir.endswith('.app'):
            app_dir = os.path.dirname(app_dir)
        
        if app_dir and app_dir.endswith('.app'):
            frameworks_dir = os.path.join(app_dir, 'Contents', 'Frameworks')
            torch_lib = os.path.join(frameworks_dir, 'torch', 'lib')
            
            if os.path.exists(torch_lib):
                existing = os.environ.get('DYLD_LIBRARY_PATH', '')
                if existing:
                    os.environ['DYLD_LIBRARY_PATH'] = f"{torch_lib}:{existing}"
                else:
                    os.environ['DYLD_LIBRARY_PATH'] = torch_lib

# pdbダミー実装
if getattr(sys, 'frozen', False):
    try:
        import pdb
    except ImportError:
        class DummyPdb:
            def set_trace(self): pass
            def __getattr__(self, name): return lambda *args, **kwargs: None
        sys.modules['pdb'] = DummyPdb()

# fairseq helpパッチ
try:
    import builtins
    if not hasattr(builtins, 'help'):
        builtins.help = "help"
    
    import fairseq.dataclass.configs as configs_module
    if not hasattr(configs_module, 'help'):
        configs_module.help = "help"
except:
    pass