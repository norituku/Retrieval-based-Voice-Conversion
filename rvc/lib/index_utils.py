"""
インデックスファイル読み込みユーティリティ
NumPy形式とFAISS形式の両方に対応した統一インターフェース
"""
import os
import logging
import traceback
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import faiss

logger = logging.getLogger(__name__)

def detect_index_format(file_path: str) -> str:
    """
    インデックスファイルの形式を自動検出
    
    Args:
        file_path: インデックスファイルのパス
        
    Returns:
        'numpy' | 'faiss' | 'unknown'
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)
        
        # NumPy形式の検出（.npy、.npz、または\x93NUMヘッダー）
        if header.startswith(b'\x93NUMPY') or header.startswith(b'\x93NUM'):
            return 'numpy'
        
        # FAISS形式の検出（バイナリ形式のため、FAISS読み込みテストで判定）
        try:
            # 小さなテスト読み込み
            test_index = faiss.read_index(file_path)
            del test_index  # メモリ解放
            return 'faiss'
        except:
            pass
            
        return 'unknown'
        
    except Exception as e:
        logger.error(f"インデックス形式検出エラー: {file_path} - {e}")
        return 'unknown'

def numpy_to_faiss_index(numpy_array: np.ndarray, index_type: str = 'IndexFlatL2') -> faiss.Index:
    """
    NumPy配列をFAISSインデックスに変換
    
    Args:
        numpy_array: 変換元のNumPy配列 (shape: [n_vectors, dimension])
        index_type: FAISSインデックスの種類
        
    Returns:
        faiss.Index: 作成されたFAISSインデックス
    """
    if len(numpy_array.shape) != 2:
        raise ValueError(f"NumPy配列は2次元である必要があります。現在の形状: {numpy_array.shape}")
    
    n_vectors, dimension = numpy_array.shape
    
    # float32に変換（FAISSの要件）
    if numpy_array.dtype != np.float32:
        logger.info(f"データ型を {numpy_array.dtype} → float32 に変換中...")
        numpy_array = numpy_array.astype(np.float32)
    
    # FAISSインデックスを作成
    if index_type == 'IndexFlatL2':
        index = faiss.IndexFlatL2(dimension)
    elif index_type == 'IndexFlatIP':
        index = faiss.IndexFlatIP(dimension)
    elif index_type == 'IndexHNSWFlat':
        index = faiss.IndexHNSWFlat(dimension, 32)
    else:
        # デフォルトはL2距離
        logger.warning(f"未知のインデックス種類: {index_type}、IndexFlatL2を使用")
        index = faiss.IndexFlatL2(dimension)
    
    # ベクトルを追加
    logger.info(f"FAISSインデックスに {n_vectors}個のベクトル（次元: {dimension}）を追加中...")
    index.add(numpy_array)
    
    logger.info(f"✅ FAISSインデックス作成完了: ntotal={index.ntotal}")
    return index

def load_index_universal(file_path: str, auto_convert: bool = True) -> Tuple[Optional[faiss.Index], Optional[np.ndarray]]:
    """
    ユニバーサルインデックス読み込み関数
    NumPy形式とFAISS形式の両方に対応
    
    Args:
        file_path: インデックスファイルのパス
        auto_convert: NumPy形式の場合、自動的にFAISSに変換するかどうか
        
    Returns:
        Tuple[faiss.Index | None, np.ndarray | None]: (FAISSインデックス, big_npy配列)
    """
    if not os.path.exists(file_path):
        logger.error(f"インデックスファイルが見つかりません: {file_path}")
        return None, None
    
    try:
        # ファイル形式を自動検出
        format_type = detect_index_format(file_path)
        logger.info(f"インデックスファイル形式検出: {file_path} → {format_type}")
        
        if format_type == 'faiss':
            # FAISS形式の読み込み
            logger.info(f"FAISS形式として読み込み中: {file_path}")
            index = faiss.read_index(file_path)
            big_npy = index.reconstruct_n(0, index.ntotal)
            logger.info(f"✅ FAISS読み込み成功: ntotal={index.ntotal}, shape={big_npy.shape}")
            return index, big_npy
            
        elif format_type == 'numpy':
            # NumPy形式の読み込み
            logger.info(f"NumPy形式として読み込み中: {file_path}")
            numpy_array = np.load(file_path)
            logger.info(f"✅ NumPy読み込み成功: shape={numpy_array.shape}, dtype={numpy_array.dtype}")
            
            if auto_convert:
                # 自動的にFAISSに変換
                logger.info("NumPy配列をFAISSインデックスに変換中...")
                index = numpy_to_faiss_index(numpy_array)
                return index, numpy_array
            else:
                # NumPy配列のみ返す（FAISSインデックスなし）
                logger.info("NumPy配列のみ返却（FAISS変換なし）")
                return None, numpy_array
                
        else:
            # 未知の形式
            logger.error(f"未対応のインデックス形式: {file_path}")
            return None, None
            
    except Exception as e:
        logger.error(f"インデックス読み込みエラー: {file_path} - {e}")
        traceback.print_exc()
        return None, None

def load_index_with_cache(file_path: str, cache_dir: Optional[str] = None) -> Tuple[Optional[faiss.Index], Optional[np.ndarray]]:
    """
    キャッシュ機能付きインデックス読み込み
    NumPy形式の場合、変換されたFAISSファイルをキャッシュして次回高速化
    
    Args:
        file_path: インデックスファイルのパス
        cache_dir: キャッシュディレクトリ（Noneの場合は元ファイルと同じディレクトリ）
        
    Returns:
        Tuple[faiss.Index | None, np.ndarray | None]: (FAISSインデックス, big_npy配列)
    """
    if not os.path.exists(file_path):
        logger.error(f"インデックスファイルが見つかりません: {file_path}")
        return None, None
    
    # キャッシュファイルパスを決定
    file_path_obj = Path(file_path)
    if cache_dir is None:
        cache_dir = file_path_obj.parent
    else:
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_file_path = cache_dir / f"{file_path_obj.stem}_faiss_cache.index"
    
    # 既存のキャッシュファイルをチェック
    if cache_file_path.exists():
        original_mtime = file_path_obj.stat().st_mtime
        cache_mtime = cache_file_path.stat().st_mtime
        
        if cache_mtime >= original_mtime:
            # キャッシュが新しい場合はそれを使用
            logger.info(f"キャッシュされたFAISSファイルを使用: {cache_file_path}")
            try:
                index = faiss.read_index(str(cache_file_path))
                big_npy = index.reconstruct_n(0, index.ntotal)
                logger.info(f"✅ キャッシュ読み込み成功: ntotal={index.ntotal}")
                return index, big_npy
            except Exception as e:
                logger.warning(f"キャッシュファイル読み込み失敗、元ファイルから再生成: {e}")
    
    # 通常の読み込み
    format_type = detect_index_format(file_path)
    
    if format_type == 'faiss':
        # FAISSファイルはキャッシュ不要
        return load_index_universal(file_path, auto_convert=True)
        
    elif format_type == 'numpy':
        # NumPy形式の場合、FAISSに変換してキャッシュ
        logger.info(f"NumPy形式ファイルを変換してキャッシュ作成: {file_path}")
        index, big_npy = load_index_universal(file_path, auto_convert=True)
        
        if index is not None:
            try:
                # FAISSインデックスをキャッシュに保存
                faiss.write_index(index, str(cache_file_path))
                logger.info(f"✅ FAISSキャッシュ保存完了: {cache_file_path}")
            except Exception as e:
                logger.warning(f"キャッシュ保存失敗（処理は続行）: {e}")
        
        return index, big_npy
    
    else:
        logger.error(f"未対応のインデックス形式: {file_path}")
        return None, None

# 後方互換性のためのエイリアス
read_index_auto = load_index_universal