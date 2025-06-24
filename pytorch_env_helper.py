#!/usr/bin/env python3
"""
PyTorch環境セットアップヘルパー
スタンドアロンアプリでPyTorchを正しく初期化するためのユーティリティ
"""
import os
import sys
import ctypes
import platform
from pathlib import Path

def setup_pytorch_environment():
    """PyTorch実行環境を設定"""
    # PyInstallerバンドル内かチェック
    if not hasattr(sys, '_MEIPASS'):
        return  # 開発環境では何もしない
    
    bundle_dir = Path(sys._MEIPASS)
    
    # macOSの場合の特別な処理
    if platform.system() == 'Darwin':
        # 動的ライブラリパスの設定
        lib_paths = []
        
        # PyInstallerバンドル内のパス
        torch_lib = bundle_dir / 'torch' / 'lib'
        if torch_lib.exists():
            lib_paths.append(str(torch_lib))
        
        # アプリバンドルの場合
        exe_path = Path(sys.executable)
        if 'MacOS' in exe_path.parts:
            app_bundle = exe_path.parent.parent
            frameworks = app_bundle / 'Frameworks'
            resources = app_bundle / 'Resources'
            
            # Frameworksディレクトリ内
            if frameworks.exists():
                lib_paths.append(str(frameworks))
                torch_frameworks = frameworks / 'torch' / 'lib'
                if torch_frameworks.exists():
                    lib_paths.append(str(torch_frameworks))
            
            # Resourcesディレクトリ内
            if resources.exists():
                torch_resources = resources / 'torch' / 'lib'
                if torch_resources.exists():
                    lib_paths.append(str(torch_resources))
        
        # 環境変数設定
        if lib_paths:
            dyld_path = ':'.join(lib_paths)
            os.environ['DYLD_LIBRARY_PATH'] = dyld_path
            os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = dyld_path
        
        # libtorch_python.dylibを事前ロード
        for path in lib_paths:
            libtorch_python = Path(path) / 'libtorch_python.dylib'
            if libtorch_python.exists():
                try:
                    ctypes.CDLL(str(libtorch_python), mode=ctypes.RTLD_GLOBAL)
                    break
                except Exception:
                    pass
            
            # libtorch.dylibも試す
            libtorch = Path(path) / 'libtorch.dylib'
            if libtorch.exists():
                try:
                    ctypes.CDLL(str(libtorch), mode=ctypes.RTLD_GLOBAL)
                except Exception:
                    pass

def import_torch_with_fix():
    """PyTorchを修正付きでインポート"""
    setup_pytorch_environment()
    
    # torch._Cが見つからない場合の回避策
    try:
        import torch
        if not hasattr(torch, '_C'):
            # _Cモジュールを手動で探す
            if hasattr(sys, '_MEIPASS'):
                import importlib.util
                
                # 可能なパス
                possible_paths = [
                    Path(sys._MEIPASS) / 'torch' / '_C.cpython-311-darwin.so',
                    Path(sys._MEIPASS) / 'torch' / '_C.cpython-310-darwin.so',
                    Path(sys._MEIPASS) / 'torch' / '_C.cpython-39-darwin.so',
                    Path(sys._MEIPASS) / 'torch' / '_C.so',
                ]
                
                for c_path in possible_paths:
                    if c_path.exists():
                        spec = importlib.util.spec_from_file_location("torch._C", c_path)
                        if spec and spec.loader:
                            torch._C = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(torch._C)
                            break
        
        return torch
    except Exception as e:
        raise RuntimeError(f"Failed to import torch: {e}")

# グローバルに環境をセットアップ
setup_pytorch_environment()
