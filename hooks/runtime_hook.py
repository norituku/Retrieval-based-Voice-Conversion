# PyInstaller ランタイムフック - メモリとパフォーマンスの最適化

import os
import sys

# 環境変数の設定
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # MPS非対応演算のCPUフォールバック
os.environ['OMP_NUM_THREADS'] = '1'              # OpenMPスレッド数を制限（メモリ節約）
os.environ['MKL_NUM_THREADS'] = '1'              # Intel MKLスレッド数を制限
os.environ['NUMEXPR_NUM_THREADS'] = '1'          # NumExprスレッド数を制限

# CUDA無効化（macOS用）
os.environ['CUDA_VISIBLE_DEVICES'] = ''          # CUDAデバイスを非表示
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = ''       # CUDA割り当て設定を無効化

# デバッグ出力を無効化
os.environ['PYTHONWARNINGS'] = 'ignore'

# PyInstaller環境でのモジュールパス設定
if getattr(sys, 'frozen', False):
    # PyInstallerでパッケージ化されている場合
    if hasattr(sys, '_MEIPASS'):
        # --onefile モード
        bundle_dir = sys._MEIPASS
    else:
        # --onedir モード
        bundle_dir = os.path.dirname(os.path.abspath(sys.executable))
    
    # macOSアプリケーションバンドルの場合
    if sys.platform == "darwin":
        # アプリケーションバンドル内のResourcesディレクトリを探す
        app_dir = bundle_dir
        while app_dir and not app_dir.endswith('.app'):
            app_dir = os.path.dirname(app_dir)
        
        if app_dir and app_dir.endswith('.app'):
            resource_dir = os.path.join(app_dir, 'Contents', 'Resources')
            if os.path.exists(resource_dir):
                # sys.pathに追加
                if resource_dir not in sys.path:
                    sys.path.insert(0, resource_dir)
                
                # PYTHONPATHにも追加
                pythonpath = os.environ.get('PYTHONPATH', '')
                if resource_dir not in pythonpath:
                    os.environ['PYTHONPATH'] = f"{resource_dir}:{pythonpath}" if pythonpath else resource_dir

# PyTorchの起動時の最適化はメインスクリプトで行う
# ここでtorchをインポートすると循環参照になる可能性がある 