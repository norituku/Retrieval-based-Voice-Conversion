import logging
import traceback
from collections import OrderedDict
from io import BytesIO
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import faiss

from rvc.configs.config import Config
from rvc.lib.audio import load_audio, wav2
from rvc.lib.infer_pack.models import (
    SynthesizerTrnMs256NSFsid,
    SynthesizerTrnMs256NSFsid_nono,
    SynthesizerTrnMs768NSFsid,
    SynthesizerTrnMs768NSFsid_nono,
)
# from rvc.lib.infer_pack.models_onnx import SynthesizerTrnMsNSFsid_ONNX # 問題のインポート文をコメントアウト
from rvc.modules.vc.pipeline import Pipeline
from rvc.modules.vc.utils import *

logger: logging.Logger = logging.getLogger(__name__)

SYNTHESIZER_CLASS_MAP = {
    ("v1", 1): SynthesizerTrnMs256NSFsid,
    ("v1", 0): SynthesizerTrnMs256NSFsid_nono,
    ("v2", 1): SynthesizerTrnMs768NSFsid,
    ("v2", 0): SynthesizerTrnMs768NSFsid_nono,
}

class VC:
    def __init__(self, config: Config):
        logger.info(f"[DEBUG VC.__init__] Initializing VC")
        self.config = config
        self.n_spk = None
        self.tgt_sr = None # get_vc で設定
        self.net_g = None  # get_vc で設定
        self.version = None # get_vc で設定
        self.if_f0 = None   # get_vc で設定

        self.file_index: str = ""  # インデックスファイルのパス (get_vc で設定)
        self.index: faiss.Index | None = None # ロードされたfaissインデックス (get_vc で設定)
        self.pipeline: Pipeline | None = None   # Pipelineオブジェクト (get_vc で設定)

        self.device = config.device
        self.is_half = config.is_half
        logger.info(f"[DEBUG VC.__init__] device: {self.device}, is_half: {self.is_half}")

    def get_vc(self, sid_model_path: str | Path, cli_index_file_path: Path | None = None, index_rate_cli: float = 0.75):
        logger.info(f"[DEBUG get_vc called] ========= START get_vc ========= ")
        logger.info(f"  sid_model_path: {sid_model_path}, type: {type(sid_model_path)}")
        logger.info(f"  cli_index_file_path (param): {cli_index_file_path}, type: {type(cli_index_file_path)}")
        logger.info(f"  index_rate_cli (param): {index_rate_cli}, type: {type(index_rate_cli)}")

        if isinstance(sid_model_path, Path):
            person_model_str_path = str(sid_model_path.resolve())
        else:
            person_model_str_path = sid_model_path
        
        logger.info(f"[DEBUG get_vc] Using model file (person_model_str_path): {person_model_str_path}")

        if not os.path.exists(person_model_str_path):
            logger.error(f"Model file {person_model_str_path} does not exist.")
            raise FileNotFoundError(f"Model file {person_model_str_path} not found.")

        logger.info(f"Loading model checkpoint: {person_model_str_path}")
        try:
            self.cpt = torch.load(person_model_str_path, map_location="cpu")
        except Exception as e:
            logger.error(f"Failed to load model checkpoint {person_model_str_path}: {e}", exc_info=True)
            raise

        logger.info(f"[DEBUG loaded_model_info model_path={person_model_str_path}]")
        original_config_list = self.cpt.get('config')
        self.version = self.cpt.get("version", "v1")
        self.if_f0 = self.cpt.get("f0", 1) 
        model_sr_text = self.cpt.get('sr') 
        
        logger.info(f"  original_config_list: {original_config_list}")
        logger.info(f"  version: {self.version}")
        logger.info(f"  if_f0 (1 means has f0): {self.if_f0}")
        logger.info(f"  model_sr_text (e.g., \"40k\"): {model_sr_text}")

        # --- Config list and tgt_sr determination (copied and adapted from previous attempt) ---
        adjusted_config_list = list(original_config_list) 
        expected_sr_from_config_last_element = None

        if self.version == "v2":
            if len(adjusted_config_list) == 19:
                expected_sr_from_config_last_element = adjusted_config_list[-1]
                logger.info(f"V2 model, 19-element config. Expected SR from last element: {expected_sr_from_config_last_element}")
                # For v2 models, we need to exclude the last 2 elements (gin_channels and sr) to get 17 args
                adjusted_config_list = adjusted_config_list[:-2] # Use first 17 for synthesizer positional args
                logger.info(f"Adjusted config for synthesizer (17 elements): {adjusted_config_list}")
            elif len(adjusted_config_list) == 18:
                logger.info(f"V2 model, 18-element config. SR will be derived from model_sr_text.")
                adjusted_config_list = adjusted_config_list[:-1] # Remove last element to get 17
            else:
                logger.warning(f"V2 model, unexpected config length: {len(adjusted_config_list)}. Defaulting to 17 elements if possible.")
                if len(adjusted_config_list) > 17: adjusted_config_list = adjusted_config_list[:17]
        elif self.version == "v1":
            if len(adjusted_config_list) == 18:
                expected_sr_from_config_last_element = adjusted_config_list[-1]
                logger.info(f"V1 model, 18-element config. Expected SR from last element: {expected_sr_from_config_last_element}")
                # For v1 models, we need to exclude the last element (sr) to get 17 args
                adjusted_config_list = adjusted_config_list[:-1] # Use first 17 for synthesizer positional args
            else:
                logger.warning(f"V1 model, unexpected config length: {len(adjusted_config_list)}. Defaulting to 17 elements if possible.")
                if len(adjusted_config_list) > 17: adjusted_config_list = adjusted_config_list[:17]
        else:
            logger.warning(f"Unknown model version: {self.version}. Assuming 17-element config structure if possible.")
            if len(adjusted_config_list) > 17: adjusted_config_list = adjusted_config_list[:17]

        if model_sr_text and isinstance(model_sr_text, str) and "k" in model_sr_text:
            try:
                self.tgt_sr = int(model_sr_text.replace("k", "")) * 1000
                logger.info(f"self.tgt_sr set from model_sr_text '{model_sr_text}': {self.tgt_sr}")
            except ValueError:
                logger.warning(f"Could not parse model_sr_text '{model_sr_text}'. Will try config.")
                self.tgt_sr = None # Reset for next check
        
        if not self.tgt_sr and expected_sr_from_config_last_element is not None and isinstance(expected_sr_from_config_last_element, int):
            self.tgt_sr = expected_sr_from_config_last_element
            logger.info(f"self.tgt_sr set from config's last element: {self.tgt_sr}")
        elif not self.tgt_sr: # Fallback if still not set
            self.tgt_sr = 40000 
            logger.warning(f"Could not determine tgt_sr. Defaulting to {self.tgt_sr}.")

        if self.version == "v2" and len(adjusted_config_list) == 17:
            try:
                n_spk_from_weight = self.cpt["weight"]["emb_g.weight"].shape[0]
                # In the 17-element list, n_spk is at index -2 (position 15)
                if adjusted_config_list[-2] != n_spk_from_weight:
                    logger.warning(f"Adjusting n_spk in config (was {adjusted_config_list[-2]}) to {n_spk_from_weight} from emb_g.weight")
                    adjusted_config_list[-2] = n_spk_from_weight
                logger.info(f"Final n_spk in config: {adjusted_config_list[-2]}, gin_channels: {adjusted_config_list[-1]}")
            except Exception as e:
                logger.error(f"Error adjusting n_spk/gin_channels for V2 model: {e}")
        logger.info(f"Final adjusted_config_list for Synthesizer: {adjusted_config_list}")
        logger.info(f"Final self.tgt_sr for output: {self.tgt_sr}")
        # --- End of Config list and tgt_sr determination ---

        synthesizer_key = (self.version, self.if_f0)
        SynthesizerClass = SYNTHESIZER_CLASS_MAP.get(synthesizer_key)
        if SynthesizerClass is None:
            logger.error(f"No SynthesizerClass found for version={self.version}, if_f0={self.if_f0}")
            raise ValueError(f"Unsupported model version/type: {self.version}, if_f0={self.if_f0}")
        
        logger.info(f"Selected Synthesizer: {SynthesizerClass.__name__}")
        sr_for_synthesizer_constructor = self.tgt_sr # Use the actual target sample rate
        logger.info(f"SR value for Synthesizer constructor: {sr_for_synthesizer_constructor}")
        try:
            self.net_g = SynthesizerClass(
                *adjusted_config_list,  # Unpack the config list as individual arguments
                sr=sr_for_synthesizer_constructor, 
                is_half=self.is_half,
            )
            self.net_g.eval().to(self.device)
            if self.is_half:
                self.net_g = self.net_g.half()
            
            # Load the model weights from checkpoint
            self.net_g.load_state_dict(self.cpt["weight"], strict=False)
            logger.info(f"Model weights loaded from checkpoint")
            logger.info(f"Synthesizer initialized and model loaded to device: {self.device}")
        except Exception as e:
            logger.error(f"Failed to initialize SynthesizerClass {SynthesizerClass.__name__}: {e}", exc_info=True)
            raise

        self.n_spk = self.cpt["config"][-3] # From original config or adjusted if v2
        
        # --- Index file determination and loading --- 
        self.file_index = "" 
        self.index = None    

        if cli_index_file_path and cli_index_file_path.exists():
            self.file_index = str(cli_index_file_path.resolve())
            logger.info(f"[DEBUG get_vc] Using CLI-provided index file: {self.file_index}")
        elif index_rate_cli > 0:
            logger.info(f"[DEBUG get_vc] index_rate_cli ({index_rate_cli}) > 0. Attempting automatic index search for model: {Path(person_model_str_path).stem}")
            found_index_path = get_index_path_from_model(person_model_str_path)
            if found_index_path:
                self.file_index = found_index_path
                logger.info(f"[DEBUG get_vc] Automatically found index file: {self.file_index}")
            else:
                logger.info(f"[DEBUG get_vc] No index file found automatically.")
        else:
            logger.info(f"[DEBUG get_vc] index_rate_cli ({index_rate_cli}) <= 0. No index file will be used.")
        
        if self.file_index and Path(self.file_index).exists():
            try:
                logger.info(f"[DEBUG get_vc] Attempting to load faiss index from: {self.file_index}")
                self.index = faiss.read_index(self.file_index)
                logger.info(f"[DEBUG get_vc] Faiss index loaded successfully. ntotal: {self.index.ntotal}")
            except Exception as e:
                logger.error(f"Failed to load faiss index '{self.file_index}': {e}. Proceeding without index.", exc_info=True)
                self.index = None 
                self.file_index = "" 
        elif self.file_index: # Path was set but file doesn't exist
             logger.warning(f"[DEBUG get_vc] Index file path '{self.file_index}' is set but file does not exist. Proceeding without index.")
             self.index = None; self.file_index = ""
        else: 
            logger.info(f"[DEBUG get_vc] No index file to load (path is empty or was not found). Proceeding without faiss index.")
        
        logger.info(f"[DEBUG get_vc] Final effective index_file path: '{self.file_index if self.file_index else 'None'}', faiss index object is None: {self.index is None}")
        # --- End of Index file determination --- 

        # --- Pipeline Initialization --- 
        logger.info(f"[DEBUG get_vc] Initializing Pipeline...")
        try:
            self.pipeline = Pipeline(
                tgt_sr=self.tgt_sr, 
                config=self.config  # Full Config object 
            )
            # Set additional attributes after initialization
            self.pipeline.net_g = self.net_g
            self.pipeline.if_f0 = self.if_f0
            self.pipeline.version = self.version
            self.pipeline.n_spk = self.n_spk
            # Set index-related attributes
            self.pipeline.index_path_str = self.file_index
            self.pipeline.index_object = self.index
            if self.index is not None:
                self.pipeline.index = self.index
                self.pipeline.big_npy = self.index.reconstruct_n(0, self.index.ntotal)
            logger.info(f"[DEBUG get_vc] Pipeline initialized successfully: {type(self.pipeline)}")
        except Exception as e:
            logger.error(f"Failed to initialize Pipeline: {e}", exc_info=True)
            raise
        # --- End of Pipeline Initialization --- 

        logger.info(f"[DEBUG get_vc] ========= END get_vc ========= ")
        # No explicit return, instance is configured.
        return

    def vc_inference(
        self,
        sid: int, # スピーカーID
        input_audio_path: Path, # 入力音声ファイルのパス
        f0_up_key: int,         # ピッチシフト量 (半音単位、例: 0, 12, -12)
        f0_method: str,         # f0推定メソッド (e.g., "rmvpe", "harvest")
        f0_file: Path | None,   # 外部f0ファイル (.f0.npy) のパス (オプション)
        # index_file_cli_override: Path | None, # この引数はget_vcで処理されるのでvc_inferenceでは直接使わない
        index_rate: float,      # 特徴量検索結果の混合率 (0.0 to 1.0)
        filter_radius: int,     # f0抽出時の中央値フィルタの半径 (奇数推奨、例: 3, 5)
        resample_sr_cli: int,   # CLI指定の入力音声リサンプリングレート (0ならモデルSR)
        rms_mix_rate: float,    # 元音声と出力音声のRMS混合率 (0.0 to 1.0)
        protect: float,         # 無声音/弱い音の保護率 (0.0 to 1.0)
        hubert_path_cli: str | Path | None = None, # CLI指定のHubertモデルパス
    ):
        logger.info(f"[VC.vc_inference called] ========= START vc_inference ========= ")
        logger.info(f"  Params: sid={sid}, input_audio_path='{input_audio_path}', f0_up_key={f0_up_key}, f0_method='{f0_method}'")
        # index_file_cli_override は get_vc で考慮済みなのでここではログ出力不要 (代わりに pipeline.index_path を確認)
        logger.info(f"          f0_file='{f0_file}', index_rate={index_rate}")
        logger.info(f"          filter_radius={filter_radius}, resample_sr_cli={resample_sr_cli}, rms_mix_rate={rms_mix_rate}")
        logger.info(f"          protect={protect}, hubert_path_cli='{hubert_path_cli}'")

        # --- Pre-checks --- 
        if not self.pipeline:
            logger.error("[VC.vc_inference] CRITICAL: self.pipeline is not initialized! Call get_vc() first.")
            _error_sr = self.tgt_sr if self.tgt_sr is not None else 40000
            return _error_sr, np.zeros(0, dtype=np.float32), (0.0, 0.0, 0.0)
        
        if not self.net_g:
            logger.error("[VC.vc_inference] CRITICAL: self.net_g (synthesizer model) is not loaded! Call get_vc() first.")
            _error_sr = self.tgt_sr if self.tgt_sr is not None else 40000
            return _error_sr, np.zeros(0, dtype=np.float32), (0.0, 0.0, 0.0)
        
        if self.tgt_sr is None:
            logger.error("[VC.vc_inference] CRITICAL: self.tgt_sr is None! Model not properly loaded via get_vc().")
            return 40000, np.zeros(0, dtype=np.float32), (0.0, 0.0, 0.0)

        # --- Hubert Model Loading --- 
        _hubert_model_actual_path: str | None = None
        if isinstance(hubert_path_cli, Path):
            _hubert_model_actual_path = str(hubert_path_cli.resolve())
        elif isinstance(hubert_path_cli, str) and hubert_path_cli.strip():
            _hubert_model_actual_path = hubert_path_cli.strip()
        else:
            env_hubert_path = os.getenv("HUBERT_PATH")
            if env_hubert_path and env_hubert_path.strip():
                _hubert_model_actual_path = env_hubert_path.strip()
                logger.info(f"  Using Hubert model from HUBERT_PATH env var: '{_hubert_model_actual_path}'")
            else:
                logger.warning("  Hubert model path not provided via CLI or HUBERT_PATH env var.")

        hubert_model: torch.nn.Module | None = None
        if _hubert_model_actual_path:
            if Path(_hubert_model_actual_path).exists():
                logger.info(f"  Attempting to load Hubert model from: '{_hubert_model_actual_path}'")
                try:
                    hubert_model = load_hubert(self.config, _hubert_model_actual_path)
                    logger.info(f"  Hubert model loaded successfully. Type: {type(hubert_model)}")
                except Exception as e:
                    logger.error(f"  Failed to load Hubert model from '{_hubert_model_actual_path}': {e}", exc_info=True)
                    return self.tgt_sr, np.zeros(0, dtype=np.float32), (0.0, 0.0, 0.0)
            else:
                logger.error(f"  Hubert model path specified ('{_hubert_model_actual_path}') but file does not exist.")
                return self.tgt_sr, np.zeros(0, dtype=np.float32), (0.0, 0.0, 0.0)
        else:
            logger.warning("  No Hubert model path. If the RVC model requires Hubert features, inference will likely fail or produce poor results.")

        # --- Input Audio Processing --- 
        # Pipeline expects 16000Hz input for Hubert processing
        _input_audio_target_sr = 16000  # Fixed to Hubert's expected sample rate
        logger.info(f"  Input audio will be resampled to Hubert's required SR: {_input_audio_target_sr}Hz.")

        logger.info(f"  Loading input audio from: '{input_audio_path}' (target SR for loading: {_input_audio_target_sr}Hz)")
        try:
            audio_input_np = load_audio(input_audio_path, _input_audio_target_sr)
            logger.info(f"  Input audio loaded. Shape: {audio_input_np.shape}, Dtype: {audio_input_np.dtype}")
            if not (audio_input_np.ndim > 0 and audio_input_np.size > 0):
                logger.error("  Loaded audio data is empty or has an invalid shape!")
                return self.tgt_sr, np.zeros(0, dtype=np.float32), (0.0, 0.0, 0.0)
            logger.info(f"    Stats (initial): min={audio_input_np.min():.4f}, max={audio_input_np.max():.4f}, mean={audio_input_np.mean():.4f}, std={audio_input_np.std():.4f}")
        except Exception as e:
            logger.error(f"  Failed to load input audio from '{input_audio_path}': {e}", exc_info=True)
            return self.tgt_sr, np.zeros(0, dtype=np.float32), (0.0, 0.0, 0.0)

        audio_max_abs_val = np.abs(audio_input_np).max()
        if audio_max_abs_val > 0.950001: # Normalize if exceeding threshold
            audio_input_np /= (audio_max_abs_val / 0.95)
            logger.info(f"  Input audio normalized (original max_abs={audio_max_abs_val:.4f}).")
            logger.info(f"    Stats (normalized): min={audio_input_np.min():.4f}, max={audio_input_np.max():.4f}, mean={audio_input_np.mean():.4f}")
        else:
            logger.info(f"  Input audio not normalized (max_abs={audio_max_abs_val:.4f} <= 0.95).")

        # --- f0 (Pitch) Estimation --- 
        logger.info(f"  Estimating f0. Method: '{f0_method}', Input audio path for get_f0: '{str(input_audio_path.resolve())}'")
        pitch_np: np.ndarray | None = None
        pitchf_np: np.ndarray | None = None
        try:
            # Calculate p_len from audio data
            audio_pad = np.pad(audio_input_np, (self.pipeline.t_pad, self.pipeline.t_pad), mode="reflect")
            p_len = audio_pad.shape[0] // self.pipeline.window
            
            pitch_np, pitchf_np = self.pipeline.get_f0(
                input_audio_path=str(input_audio_path.resolve()), 
                x=audio_input_np, 
                p_len=p_len,
                f0_up_key=f0_up_key,
                f0_method=f0_method,
                filter_radius=filter_radius,
                inp_f0=f0_file,
            )
            logger.info(f"  f0 estimation completed.")
            if pitch_np is not None:
                logger.info(f"    Pitch: Shape={pitch_np.shape}, Dtype={pitch_np.dtype}, Min={pitch_np.min():.2f}, Max={pitch_np.max():.2f}, Mean={pitch_np.mean():.2f}")
            else:
                logger.warning("    Pitch (pitch_np) is None after get_f0.")
            if pitchf_np is not None:
                logger.info(f"    PitchF (pitchf_np): Shape={pitchf_np.shape}, Dtype={pitchf_np.dtype}, Min={pitchf_np.min():.2f}, Max={pitchf_np.max():.2f}, Mean={pitchf_np.mean():.2f}")
            else:
                logger.info("    PitchF (pitchf_np) is None after get_f0 (normal if not produced by method or f0_file used).")
        except Exception as e:
            logger.error(f"  Error during f0 estimation: {e}", exc_info=True)
            return self.tgt_sr, np.zeros(0, dtype=np.float32), (0.0, 0.0, 0.0)

        # --- Main Inference via Pipeline --- 
        logger.info(f"  Calling self.pipeline.pipeline for main RVC inference...")
        logger.info(f"    Pipeline Args Overview:")
        logger.info(f"      Hubert Model Provided: {hubert_model is not None}")
        logger.info(f"      Speaker ID (sid): {sid}")
        logger.info(f"      Audio Input to Pipeline: Shape={audio_input_np.shape}, Dtype={audio_input_np.dtype}")
        logger.info(f"      Pitch Input to Pipeline is None: {pitch_np is None}")
        logger.info(f"      PitchF Input to Pipeline is None: {pitchf_np is None}")
        logger.info(f"      Pipeline internal index_path: '{self.pipeline.index_path_str if self.pipeline.index_path_str else 'Not Set'}', index_object is None: {self.pipeline.index_object is None}")
        logger.info(f"      Index Rate: {index_rate}")
        logger.info(f"      RMS Mix Rate: {rms_mix_rate}")
        logger.info(f"      Protect (Breath): {protect}")
        logger.info(f"      F0 Up Key: {f0_up_key}")
        logger.info(f"      Target Output SR: {self.tgt_sr}")

        # Initialize return values for safety
        audio_output_np = np.zeros(0, dtype=np.float32)
        times_tuple = (0.0, 0.0, 0.0) # (npy_time, f0_time, infer_time)

        try:
            times = {"npy": 0, "f0": 0, "infer": 0}  # Will be updated by pipeline
            audio_output_np = self.pipeline.pipeline( 
                model=hubert_model,
                net_g=self.net_g,
                sid=sid, 
                audio=audio_input_np, 
                input_audio_path=str(input_audio_path.resolve()),
                times=times,
                f0_up_key=f0_up_key,
                f0_method=f0_method,
                file_index=self.file_index if self.file_index else "",
                index_rate=index_rate,
                if_f0=self.if_f0,
                filter_radius=filter_radius,
                tgt_sr=self.tgt_sr, 
                resample_sr=resample_sr_cli if resample_sr_cli else 0,
                rms_mix_rate=rms_mix_rate,
                version=self.version,
                protect=protect,
                f0_file=f0_file,
            )
            times_tuple = (times.get("npy", 0), times.get("f0", 0), times.get("infer", 0))  # Convert dict to tuple
        except Exception as e:
            logger.error(f"  CRITICAL ERROR during self.pipeline.pipeline execution: {e}", exc_info=True)
            return self.tgt_sr, audio_output_np, times_tuple # Return whatever we have, even if empty

        logger.info(f"  self.pipeline.pipeline completed.")
        if len(times_tuple) == 3:
            logger.info(f"    Returned processing times: NPY={times_tuple[0]:.4f}s, F0={times_tuple[1]:.4f}s, Infer={times_tuple[2]:.4f}s")
        else:
            logger.info(f"    Returned processing times: {times_tuple}") # Fallback if not 3 elements
        
        if audio_output_np is not None:
            logger.info(f"    Output Audio (audio_output_np) - Shape: {audio_output_np.shape}, Dtype: {audio_output_np.dtype}")
            if audio_output_np.ndim > 0 and audio_output_np.size > 0:
                logger.info(f"      Stats: min={audio_output_np.min():.4f}, max={audio_output_np.max():.4f}, mean={audio_output_np.mean():.4f}, std={audio_output_np.std():.4f}")
            else:
                logger.warning("    Output audio (audio_output_np) is empty or has an invalid shape after pipeline execution!")
        else:
            logger.error("    CRITICAL: Output audio (audio_output_np) is None after pipeline! This should not happen.")
            audio_output_np = np.zeros(0, dtype=np.float32) # Ensure we return an ndarray

        logger.info(f"[VC.vc_inference] ========= END vc_inference ========= ")
        return self.tgt_sr, audio_output_np, times_tuple

    def vc_multi(
        self,
        sid: int,
        paths: list,
        opt_root: Path,
        f0_up_key: int = 0,
        f0_method: str = "rmvpe",
        f0_file: Path | None = None,
        index_file: Path | None = None,
        index_rate: float = 0.75,
        filter_radius: int = 3,
        resample_sr: int = 0,
        rms_mix_rate: float = 0.25,
        protect: float = 0.33,
        output_format: str = "wav",
        hubert_path: str | None = None,
    ):
        try:
            os.makedirs(opt_root, exist_ok=True)
            paths = [path.name for path in paths]
            infos = []
            for path in paths:
                tgt_sr, audio_opt, times, info = self.vc_inference(
                    sid,
                    Path(path),
                    f0_up_key,
                    f0_method,
                    f0_file,
                    index_file,
                    index_rate,
                    filter_radius,
                    resample_sr,
                    rms_mix_rate,
                    protect,
                    hubert_path,
                )
                if info:
                    try:
                        if output_format in ["wav", "flac"]:
                            sf.write(
                                f"{opt_root}/{os.path.basename(path)}.{output_format}",
                                audio_opt,
                                tgt_sr,
                            )
                        else:
                            with BytesIO() as wavf:
                                sf.write(wavf, audio_opt, tgt_sr, format="wav")
                                wavf.seek(0, 0)
                                with open(
                                    f"{opt_root}/{os.path.basename(path)}.{output_format}",
                                    "wb",
                                ) as outf:
                                    wav2(wavf, outf, output_format)
                    except Exception:
                        info += traceback.format_exc()
                infos.append(f"{os.path.basename(path)}->{info}")
                yield "\n".join(infos)
            yield "\n".join(infos)
        except:
            yield traceback.format_exc()
