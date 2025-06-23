import os
import logging
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)

# fairseqのHubertローダー
try:
    from fairseq import checkpoint_utils
    FAIRSEQ_AVAILABLE = True
    logger.info("✅ fairseq checkpoint_utils available")
except ImportError:
    FAIRSEQ_AVAILABLE = False
    logger.error("❌ fairseq not available - This is required for voice conversion")
    raise ImportError("fairseq is required for RVC. Please ensure it's properly installed.")


def get_index_path_from_model(sid):
    index_root_path = os.getenv("index_root")
    if not index_root_path or not os.path.exists(index_root_path):
        # index_root が設定されていない、または存在しない場合は、モデルファイルと同じディレクトリを検索対象とする
        # または、インデックスファイルが必須でないなら、ここで空文字列を返しても良い
        model_dir = os.path.dirname(str(sid))
        if os.path.exists(model_dir):
            index_root_path = model_dir
        else:
            return "" # 有効な検索場所がなければ空を返す

    # モデル名 (拡張子なし、パス部分は除く) を取得
    model_name_stem = os.path.basename(str(sid)).split(".")[0]

    found_files = []
    for root, _, files in os.walk(index_root_path, topdown=False):
        for name in files:
            if name.endswith(".index") and "trained" not in name:
                # インデックスファイル名またはパスにモデル名ステムが含まれているかチェック
                # (より堅牢なマッチング方法も検討可能)
                if model_name_stem in name: # ファイル名のみでチェックする場合
                # if model_name_stem in os.path.join(root, name): # フルパスでチェックする場合
                    found_files.append(os.path.join(root, name))
    
    if found_files:
        # ここでは最初に見つかったものを返す (複数ある場合の優先順位付けが必要な場合もある)
        return found_files[0]
    else:
        return "" # 見つからなければ空文字列を返す


def load_hubert(config, hubert_path: str):
    if not hubert_path or not os.path.exists(hubert_path):
        # Hubertモデルのパスが不正な場合はエラーを発生させる（ダミー実装は行わない）
        logger.error(f"Hubert model path is invalid or does not exist: {hubert_path}")
        raise FileNotFoundError(f"Hubert model not found at {hubert_path}")

    try:
        models, _, _ = checkpoint_utils.load_model_ensemble_and_task(
            [hubert_path],
            suffix="",
        )
        hubert_model = models[0]
        hubert_model = hubert_model.to(config.device)
        hubert_model = hubert_model.half() if config.is_half else hubert_model.float()
        return hubert_model.eval()
    except Exception as e:
        logger.error(f"Failed to load Hubert model from {hubert_path}: {e}")
        # CLAUDE.mdルール: ダミー実装ではなくエラーで停止
        raise RuntimeError(f"Cannot load Hubert model: {e}. Voice conversion requires a valid Hubert model.")
