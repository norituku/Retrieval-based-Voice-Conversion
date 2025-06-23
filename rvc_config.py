#!/usr/bin/env python3
"""
RVC実行用の設定ファイル
"""

import sys
import os

# Poetry仮想環境のPythonパス（Python 3.11版 - 推奨）
POETRY_PYTHON_PATH = "/Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11/bin/python"

# RVCモジュールパス
RVC_MODULE = "rvc.wrapper.cli.cli"

def get_poetry_python():
    """Poetry Python環境のパスを取得（PyInstaller対応）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller環境：常にsys.executableを使用
        # 埋め込みPython環境では、PyInstallerのPython実行環境が最適
        return sys.executable
    else:
        # 通常環境：Poetryパスを使用
        return POETRY_PYTHON_PATH

def get_rvc_command(model_file, input_file, output_file, pitch=0, f0_method="rmvpe",
                   index_rate=1.0, filter_radius=3, protect=0.33, rms_mix_rate=0.25,
                   index_file=None, hubert_path=None):
    """RVC実行コマンドを生成"""
    python_path = get_poetry_python()
    cmd = [
        python_path, "-m", RVC_MODULE, "infer",
        "-m", model_file,
        "-i", input_file,
        "-o", output_file,
        "-fu", str(pitch),
        "-fm", f0_method,
        "-ir", str(index_rate),
        "-fr", str(filter_radius),
        "-p", str(protect),
        "-rmr", str(rms_mix_rate)
    ]
    
    if index_file:
        cmd.extend(["-if", index_file])
    
    if hubert_path:
        cmd.extend(["--hubert_model_path", hubert_path])
    
    return cmd
