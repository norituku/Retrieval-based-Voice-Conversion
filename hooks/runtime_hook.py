# PyInstaller ランタイムフック - メモリとパフォーマンスの最適化

import os
import sys

# 環境変数の設定
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # MPS非対応演算のCPUフォールバック
os.environ['OMP_NUM_THREADS'] = '1'              # OpenMPスレッド数を制限（メモリ節約）
os.environ['MKL_NUM_THREADS'] = '1'              # Intel MKLスレッド数を制限
os.environ['NUMEXPR_NUM_THREADS'] = '1'          # NumExprスレッド数を制限

# デバッグ出力を無効化
os.environ['PYTHONWARNINGS'] = 'ignore'

# PyTorchの起動時の最適化はメインスクリプトで行う
# ここでtorchをインポートすると循環参照になる可能性がある 