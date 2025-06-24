# PyInstaller hook for fairseq - RVC音声変換用

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

# fairseqモジュール全体を収集
hiddenimports = collect_submodules('fairseq')

# fairseq dataファイルを収集
datas = collect_data_files('fairseq')

# fairseq.dataclass.configs.py内のhelp変数問題に対する特別対応
# PyInstallerが収集時にモジュールを正しく処理できるよう、
# hiddenimportsに明示的に追加
hiddenimports += [
    'fairseq.dataclass.configs',
    'fairseq.dataclass.constants',
    'fairseq.checkpoint_utils',
    'fairseq.distributed',
    'fairseq.models',
    'fairseq.modules',
    'fairseq.tasks',
    'fairseq.criterions',
    'fairseq.optim',
    'fairseq.lr_scheduler',
    # dataclass関連
    'dataclasses',
    'omegaconf',
]

print(f"[hook-fairseq] Hidden imports count: {len(hiddenimports)}")
print(f"[hook-fairseq] Data files count: {len(datas)}")