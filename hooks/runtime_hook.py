# PyInstaller ランタイムフック - 最小限の環境設定

import os
import sys

# 環境変数の設定
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # MPS非対応演算のCPUフォールバック
os.environ['OMP_NUM_THREADS'] = '1'              # OpenMPスレッド数を制限（メモリ節約）
os.environ['MKL_NUM_THREADS'] = '1'              # Intel MKLスレッド数を制限
os.environ['NUMEXPR_NUM_THREADS'] = '1'          # NumExprスレッド数を制限

# MPS（Metal Performance Shaders）を完全に無効化
os.environ['PYTORCH_DISABLE_MPS'] = '1'          # PyTorchのMPSを無効化
os.environ['PYTORCH_NO_MPS'] = '1'               # 追加のMPS無効化設定
os.environ['PYTORCH_USE_MPS'] = '0'              # MPSを使用しない

# CUDA無効化（macOS用）
os.environ['CUDA_VISIBLE_DEVICES'] = ''          # CUDAデバイスを非表示
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = ''       # CUDA割り当て設定を無効化

# デバッグ出力を無効化
os.environ['PYTHONWARNINGS'] = 'ignore'

# PyInstaller環境でのモジュールパス設定
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print("[Runtime Hook] PyInstaller環境検出")

    # --onefile モード
    bundle_dir = sys._MEIPASS

    # torch/random.pyとPython標準ライブラリの競合を回避
    # 重要: torchをインポートする前に、標準ライブラリのrandomとtempfileをインポート
    import random as stdlib_random
    import tempfile as stdlib_tempfile
    sys.modules['random'] = stdlib_random
    sys.modules['tempfile'] = stdlib_tempfile
    print("[Runtime Hook] 標準ライブラリ競合回避設定完了")

    # macOSアプリケーションバンドルの場合
    if sys.platform == "darwin":
        # アプリケーションバンドルのルートを探す
        app_dir = bundle_dir
        while app_dir and not app_dir.endswith('.app'):
            app_dir = os.path.dirname(app_dir)

        if app_dir and app_dir.endswith('.app'):
            # .app/Contents/ 以下のディレクトリ構造
            frameworks_dir = os.path.join(app_dir, 'Contents', 'Frameworks')

            # torchとその依存ライブラリのパスを設定
            torch_paths = [
                os.path.join(frameworks_dir, 'torch', 'lib'),
                frameworks_dir,
            ]

            # 既存のパスを保持
            existing_path = os.environ.get('DYLD_LIBRARY_PATH', '')
            new_paths = []

            # 存在するパスのみ追加
            for path in torch_paths:
                if os.path.exists(path):
                    new_paths.append(path)

            # パスを設定
            if new_paths:
                new_path_str = ':'.join(new_paths)
                if existing_path:
                    os.environ['DYLD_LIBRARY_PATH'] = f"{new_path_str}:{existing_path}"
                else:
                    os.environ['DYLD_LIBRARY_PATH'] = new_path_str
                print(f"[Runtime Hook] DYLD_LIBRARY_PATH設定: {os.environ['DYLD_LIBRARY_PATH']}")

print("[Runtime Hook] 環境設定完了")

# pdbモジュールのダミー実装（PyInstaller環境でfairseqが必要とする）
if getattr(sys, 'frozen', False):
    # pdbモジュールが存在しない場合のみダミー実装を提供
    try:
        import pdb
        print("[Runtime Hook] pdbモジュールは既に存在")
    except ImportError:
        print("[Runtime Hook] pdbモジュールが存在しない - ダミー実装を提供")
        # 最小限のダミー実装
        class DummyPdb:
            def set_trace(self):
                pass

            def __getattr__(self, name):
                # 他の属性へのアクセスも無視
                return lambda *args, **kwargs: None

        dummy_pdb = DummyPdb()
        sys.modules['pdb'] = dummy_pdb
        print("[Runtime Hook] pdbダミーモジュール登録完了")

# fairseq dataclass互換性パッチ（PyInstaller環境対応）
try:
    # fairseq.dataclass.configsモジュールをインポート前に事前パッチ
    import fairseq
    import fairseq.dataclass

    # help変数の事前定義（グローバルスコープに注入）
    if 'help' not in globals():
        globals()['help'] = "help"
        print("[Runtime Hook] fairseq help変数グローバル注入完了")

    # さらにfairseq.dataclass.configsモジュールレベルでも注入
    import fairseq.dataclass.configs
    if not hasattr(fairseq.dataclass.configs, 'help'):
        fairseq.dataclass.configs.help = "help"
        print("[Runtime Hook] fairseq.dataclass.configs.help注入完了")

except ImportError:
    print("[Runtime Hook] fairseq未インストール - パッチスキップ")
except Exception as e:
    print(f"[Runtime Hook] fairseqパッチエラー: {e}")


# 注意: torch関連の初期化は実行時に行う（遅延初期化）
# これによりモジュール競合や循環インポートを回避
