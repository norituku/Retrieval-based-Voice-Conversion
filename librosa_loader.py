#!/usr/bin/env python3
"""
librosa動的ローダー
PyInstaller環境でのlibrosa読み込み問題を回避
"""
import sys
import os
from pathlib import Path

def setup_librosa_path():
    """PyInstaller環境でlibrosaのパスを設定"""
    if getattr(sys, 'frozen', False):
        # PyInstaller環境
        if hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(sys.executable).parent
        
        # librosaが個別ディレクトリとして含まれている場合
        librosa_path = base_path / 'librosa'
        if librosa_path.exists():
            sys.path.insert(0, str(base_path))
            print(f"[LIBROSA_LOADER] Added to path: {base_path}")
            
            # 環境変数も設定
            os.environ['LIBROSA_DATA_DIR'] = str(librosa_path)
            
def import_librosa():
    """librosaを安全にインポート"""
    setup_librosa_path()
    
    try:
        import librosa
        print(f"[LIBROSA_LOADER] Successfully imported librosa from: {librosa.__file__}")
        return librosa
    except ImportError as e:
        print(f"[LIBROSA_LOADER] Failed to import librosa: {e}")
        # フォールバック: librosaなしで続行
        return None

# グローバル変数として保持
_librosa = None

def get_librosa():
    """librosaインスタンスを取得"""
    global _librosa
    if _librosa is None:
        _librosa = import_librosa()
    return _librosa
