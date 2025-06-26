import logging
import os
import sys
import traceback
from functools import lru_cache
from time import time as ttime
from pathlib import Path

import faiss
import librosa
import numpy as np
import torch
from functools import lru_cache
from typing import Any, Union

import parselmouth
import pyworld
import torch.nn.functional as F
import torchcrepe
from scipy import signal

from .pipeline import Pipeline

logger: logging.Logger = logging.getLogger(__name__)

class EnhancedPipeline(Pipeline):
    """
    改良版音声変換パイプライン
    - 近傍探索の最適化
    - F0推定のアンサンブル
    - セグメント分割の改善
    """
    
    def __init__(self, tgt_sr, config):
        super().__init__(tgt_sr, config)
        
        # 設定を保存（フォールバック用）
        self.config = config
        
        # 必要な属性を明示的に設定（継承で欠落する場合に備えて）
        if not hasattr(self, 'bh') or self.bh is None:
            from scipy import signal
            self.bh, self.ah = signal.butter(N=5, Wn=48, btype="high", fs=16000)
        
        # 改良機能のフラグ
        self.enable_adaptive_neighbors = True
        self.enable_f0_ensemble = True
        self.enable_vad_segmentation = True
        
        # 適応的近傍探索の設定
        self.min_neighbors = 8
        self.max_neighbors = 32
        self.default_neighbors = 16
        
        # F0アンサンブルの重み
        self.f0_weights = {
            'rmvpe': 0.4,
            'crepe': 0.3,
            'harvest': 0.2,
            'dio': 0.1
        }
        
        logger.info("Enhanced Pipeline initialized with improved algorithms")
    
    def adaptive_index_search(self, feats, index, big_npy, index_rate):
        """
        適応的近傍探索
        音声特徴の複雑さに応じて近傍数を動的に調整
        """
        if not self.enable_adaptive_neighbors:
            # 適応的近傍探索が無効の場合はエラー
            raise RuntimeError("適応的近傍探索が無効になっています。RVC設定を確認してください。")
        
        npy = feats[0].cpu().numpy().astype(np.float32)  # Faiss互換性のため明示的にfloat32に
        
        # 特徴量の統計を計算
        feature_std = np.std(npy, axis=0)
        feature_range = np.ptp(npy, axis=0)
        complexity = np.mean(feature_std) * np.mean(feature_range)
        
        # 複雑さに基づいて近傍数を調整
        # 複雑な音声ほど多くの近傍を参照
        k_neighbors = int(self.min_neighbors + 
                         (self.max_neighbors - self.min_neighbors) * 
                         np.tanh(complexity * 0.1))
        
        # 環境変数によるオーバーライド
        k_neighbors = int(os.getenv("RVC_SEARCH_NEIGHBORS", str(k_neighbors)))
        k_neighbors = max(1, min(k_neighbors, self.max_neighbors, big_npy.shape[0]))  # 安全な範囲に制限
        
        logger.debug(f"Adaptive search: complexity={complexity:.3f}, k_neighbors={k_neighbors}")
        
        try:
            # 近傍探索（エラーハンドリング付き）
            score, ix = index.search(npy, k_neighbors)  # kパラメータを位置引数として渡す
        except Exception as e:
            logger.error(f"❌ Faiss search failed: {e}")
            raise RuntimeError(f"Faiss近傍探索に失敗しました: {e}") from e
        
        # ガウシアンカーネルによる重み付け（数値安定性向上）
        # 距離が近いほど高い重みを持つ
        sigma = np.median(score) + 1e-6
        
        # オーバーフロー回避：スコアをクリップして数値安定性を確保
        score_clipped = np.clip(score, 0, 50)  # 大きすぎる値をクリップ
        exponent = -score_clipped**2 / (2 * sigma**2)
        exponent = np.clip(exponent, -500, 0)  # exp関数のオーバーフロー回避
        
        with np.errstate(over='ignore', invalid='ignore'):
            weight = np.exp(exponent)
        
        # NaNやInfの処理
        weight = np.nan_to_num(weight, nan=1e-8, posinf=1e-8, neginf=1e-8)
        
        # 重みの正規化（ゼロ除算回避）
        weight_sum = weight.sum(axis=1, keepdims=True)
        weight_sum = np.where(weight_sum == 0, 1e-8, weight_sum)
        weight /= weight_sum
        
        # 重み付き平均で特徴量を合成
        npy = np.sum(big_npy[ix] * np.expand_dims(weight, axis=2), axis=1)
        
        if self.is_half:
            npy = npy.astype("float16")
            
        feats_enhanced = (
            torch.from_numpy(npy).unsqueeze(0).to(self.device) * index_rate
            + (1 - index_rate) * feats
        )
        
        return feats_enhanced
    
    
    def get_f0_ensemble(self, input_audio_path, x, p_len, f0_up_key, f0_method, filter_radius, inp_f0=None):
        """
        F0推定のアンサンブル
        複数のF0推定手法を組み合わせて精度を向上
        """
        if not self.enable_f0_ensemble:
            # F0アンサンブルが無効の場合はエラー
            raise RuntimeError("F0アンサンブルが無効になっています。RVC設定を確認してください。")
        
        # rmvpe以外の場合のみアンサンブル実行（rmvpeは単体で高精度）
        if f0_method == "pm" or f0_method == "rmvpe":
            return self.get_f0(input_audio_path, x, p_len, f0_up_key, f0_method, filter_radius, inp_f0)
        
        f0_results = {}
        weights = {}
        
        # メインのF0メソッドを実行
        main_f0, main_f0f = self.get_f0(input_audio_path, x, p_len, f0_up_key, f0_method, filter_radius, inp_f0)
        f0_results[f0_method] = main_f0
        weights[f0_method] = self.f0_weights.get(f0_method, 0.5)
        
        # 補助的なF0メソッドを実行（計算時間を考慮して選択的に）
        if f0_method != "harvest":
            try:
                harvest_f0, _ = self.get_f0(input_audio_path, x, p_len, f0_up_key, "harvest", filter_radius, inp_f0)
                f0_results["harvest"] = harvest_f0
                weights["harvest"] = self.f0_weights.get("harvest", 0.2)
            except Exception as e:
                logger.debug(f"Harvest F0 estimation failed: {e}")
        
        # 重み付き中央値でアンサンブル（データ型修正版）
        if len(f0_results) > 1:
            try:
                # 各F0値を重み付けして組み合わせ（データ型を統一）
                f0_ensemble = np.zeros_like(main_f0, dtype=np.float64)  # float64で初期化
                total_weight = sum(weights.values())
                
                for method, f0 in f0_results.items():
                    weight = weights[method] / total_weight
                    # データ型を明示的にfloat64に変換してからアンサンブル計算
                    f0_float = f0.astype(np.float64)
                    f0_ensemble += f0_float * weight
                
                # 外れ値の除去
                f0_median = np.median(f0_ensemble[f0_ensemble > 0])
                f0_std = np.std(f0_ensemble[f0_ensemble > 0])
                
                # 中央値から3σ以上離れた値を補正
                outlier_mask = np.abs(f0_ensemble - f0_median) > 3 * f0_std
                f0_ensemble[outlier_mask] = f0_median
                
                logger.debug(f"F0 ensemble: methods={list(f0_results.keys())}, median={f0_median:.1f}Hz")
                
                # 元のデータ型に変換して返す
                f0_ensemble_final = f0_ensemble.astype(main_f0.dtype)
                return f0_ensemble_final, main_f0f
                
            except Exception as e:
                logger.error(f"❌ F0 ensemble calculation failed: {e}")
                raise RuntimeError(f"F0アンサンブル計算に失敗しました: {e}") from e
        else:
            return main_f0, main_f0f
    
    def get_optimal_segments(self, audio, sr=16000):
        """
        音声活動検出（VAD）ベースのセグメント分割
        無音区間を検出してより自然な分割点を見つける
        """
        if not self.enable_vad_segmentation:
            # VAD無効の場合はエラー
            raise RuntimeError("VADセグメンテーションが無効になっています。RVC設定を確認してください。")
        
        # エネルギーベースのVAD
        hop_length = 512
        frame_length = 2048
        
        # RMSエネルギーを計算
        rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        
        # 動的閾値（中央値の20%）
        threshold = np.median(rms) * 0.2
        
        # 無音区間を検出
        is_silent = rms < threshold
        
        # 無音区間の境界を検出
        silent_boundaries = []
        for i in range(1, len(is_silent)):
            if is_silent[i] and not is_silent[i-1]:  # 無音開始
                start_sample = i * hop_length
                silent_boundaries.append(start_sample)
            elif not is_silent[i] and is_silent[i-1]:  # 無音終了
                end_sample = i * hop_length
                if len(silent_boundaries) > 0 and isinstance(silent_boundaries[-1], int):
                    # 無音区間の中点を分割点として使用
                    mid_point = (silent_boundaries[-1] + end_sample) // 2
                    silent_boundaries[-1] = mid_point
        
        # 標準の分割点と組み合わせ
        opt_ts = []
        standard_segment_size = self.t_center
        
        for t in range(standard_segment_size, audio.shape[0], standard_segment_size):
            # 最も近い無音区間の境界を探す
            if len(silent_boundaries) > 0:
                distances = [abs(t - boundary) for boundary in silent_boundaries]
                min_distance_idx = np.argmin(distances)
                
                # 標準分割点から10%以内に無音区間がある場合はそちらを使用
                if distances[min_distance_idx] < standard_segment_size * 0.1:
                    opt_ts.append(silent_boundaries[min_distance_idx])
                    silent_boundaries.pop(min_distance_idx)  # 使用済みの境界を削除
                else:
                    opt_ts.append(t)
            else:
                opt_ts.append(t)
        
        logger.debug(f"VAD segmentation: {len(opt_ts)} segments, silent regions detected: {len(silent_boundaries)}")
        
        return opt_ts
    
    
    def vc(
        self,
        model,
        net_g,
        sid,
        audio0,
        pitch,
        pitchf,
        times,
        index,
        big_npy,
        index_rate,
        version,
        protect,
    ):
        """改良版の音声変換処理"""
        feats = torch.from_numpy(audio0)
        if self.is_half:
            feats = feats.half()
        else:
            feats = feats.float()
        if feats.dim() == 2:  # double channels
            feats = feats.mean(-1)
        assert feats.dim() == 1, feats.dim()
        feats = feats.view(1, -1)
        padding_mask = torch.BoolTensor(feats.shape).to(self.device).fill_(False)

        inputs = {
            "source": feats.to(self.device),
            "padding_mask": padding_mask,
            "output_layer": 9 if version == "v1" else 12,
        }
        t0 = ttime()
        
        # MPS環境でのweight_norm問題を回避：HubertモデルをCPUで実行
        # PyInstaller環境では常にCPUフォールバックを使用
        import sys
        if hasattr(sys, '_MEIPASS'):
            cpu_fallback_needed = True
            original_device = torch.device('cpu')
        else:
            original_device = next(model.parameters()).device
            cpu_fallback_needed = False
        
        if str(original_device).startswith('mps') and not hasattr(sys, '_MEIPASS'):
            try:
                with torch.no_grad():
                    logits = model.extract_features(**inputs)
                    feats = model.final_proj(logits[0]) if version == "v1" else logits[0]
            except NotImplementedError as e:
                if "aten::_weight_norm_interface" in str(e):
                    logger.warning("MPS weight_norm issue detected, falling back to CPU for Hubert")
                    cpu_fallback_needed = True
                else:
                    raise
        
        if cpu_fallback_needed or not str(original_device).startswith('mps'):
            if cpu_fallback_needed:
                # モデルを一時的にCPUに移動
                model.cpu()
                inputs_cpu = {k: v.cpu() if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
                
                with torch.no_grad():
                    logits = model.extract_features(**inputs_cpu)
                    feats = model.final_proj(logits[0]) if version == "v1" else logits[0]
                    # 結果をMPSに戻す
                    feats = feats.to(original_device)
                
                # モデルを元のデバイスに戻す
                model.to(original_device)
            else:
                with torch.no_grad():
                    logits = model.extract_features(**inputs)
                    feats = model.final_proj(logits[0]) if version == "v1" else logits[0]
            
        if protect < 0.5 and pitch is not None and pitchf is not None:
            feats0 = feats.clone()
            
        # 改良版インデックス検索を使用
        if (
            not isinstance(index, type(None))
            and not isinstance(big_npy, type(None))
            and index_rate != 0
        ):
            feats = self.adaptive_index_search(feats, index, big_npy, index_rate)

        feats = F.interpolate(feats.permute(0, 2, 1), scale_factor=2).permute(0, 2, 1)
        if protect < 0.5 and pitch is not None and pitchf is not None:
            feats0 = F.interpolate(feats0.permute(0, 2, 1), scale_factor=2).permute(
                0, 2, 1
            )
        t1 = ttime()
        p_len = audio0.shape[0] // self.window
        
        # サイズ調整の詳細ログ
        logger.debug(f"Before size adjustment: feats.shape={feats.shape}, p_len={p_len}")
        if pitch is not None and pitchf is not None:
            logger.debug(f"Pitch shapes: pitch={pitch.shape}, pitchf={pitchf.shape}")
        
        # featsのサイズをp_lenに合わせる
        if feats.shape[1] < p_len:
            p_len = feats.shape[1]
            if pitch is not None and pitchf is not None:
                pitch = pitch[:, :p_len]
                pitchf = pitchf[:, :p_len]
                logger.debug(f"Adjusted pitch to p_len={p_len}")
        elif feats.shape[1] > p_len and pitch is not None and pitchf is not None:
            # pitchの方が短い場合、featsを切り詰める
            feats = feats[:, :p_len, :]
            if protect < 0.5:
                feats0 = feats0[:, :p_len, :]
            logger.debug(f"Adjusted feats to p_len={p_len}")

        # Protect処理（サイズ確認付き）
        if protect < 0.5 and pitch is not None and pitchf is not None:
            try:
                pitchff = pitchf.clone()
                pitchff[pitchf > 0] = 1
                pitchff[pitchf < 1] = protect
                pitchff = pitchff.unsqueeze(-1)
                
                # サイズの最終確認
                if feats.shape[1] != pitchff.shape[1]:
                    logger.error(f"Size mismatch: feats.shape[1]={feats.shape[1]}, pitchff.shape[1]={pitchff.shape[1]}")
                    # サイズを強制調整
                    min_len = min(feats.shape[1], pitchff.shape[1])
                    feats = feats[:, :min_len, :]
                    feats0 = feats0[:, :min_len, :]
                    pitchff = pitchff[:, :min_len, :]
                    logger.warning(f"Force adjusted to min_len={min_len}")
                
                feats = feats * pitchff + feats0 * (1 - pitchff)
                feats = feats.to(feats0.dtype)
                logger.debug("✅ Protect processing completed successfully")
                
            except Exception as e:
                logger.error(f"❌ Protect processing failed: {e}")
                logger.warning("🔄 Skipping protect processing")
                # protect処理をスキップして続行
            
        p_len = torch.tensor([p_len], device=self.device).long()
        with torch.no_grad():
            hasp = pitch is not None and pitchf is not None
            arg = (feats, p_len, pitch, pitchf, sid) if hasp else (feats, p_len, sid)
            audio1 = (net_g.infer(*arg)[0][0, 0]).data.cpu().float().numpy()
            del hasp, arg
            
        del feats, p_len, padding_mask
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        t2 = ttime()
        times["npy"] += t1 - t0
        times["infer"] += t2 - t1
        
        return audio1
    
    def pipeline(
        self,
        model,
        net_g,
        sid,
        audio,
        input_audio_path,
        times,
        f0_up_key,
        f0_method,
        file_index,
        index_rate,
        if_f0,
        filter_radius,
        tgt_sr,
        resample_sr,
        rms_mix_rate,
        version,
        protect,
        f0_file=None,
    ):
        """改良版パイプライン処理（詳細エラーハンドリング付き）"""
        
        # 入力データの検証
        logger.info(f"Enhanced Pipeline starting with input audio shape: {audio.shape}")
        logger.info(f"Parameters: f0_method={f0_method}, index_rate={index_rate}, tgt_sr={tgt_sr}")
        
        if audio.size == 0:
            logger.error("❌ Empty input audio provided to pipeline")
            return np.array([], dtype=np.int16)
        
        try:
            # ユニバーサルインデックスファイルの読み込み（NumPy・FAISS両対応）
            if (
                file_index
                and file_index != ""
                and os.path.exists(file_index)
                and index_rate != 0
            ):
                try:
                    from rvc.lib.index_utils import load_index_with_cache
                    index, big_npy = load_index_with_cache(file_index)
                    
                    if index is not None and big_npy is not None:
                        logger.info(f"✅ Index file loaded (universal): {file_index}, ntotal={index.ntotal}, format=auto-detected")
                    else:
                        logger.error(f"❌ Universal index loading failed: {file_index}")
                        index = big_npy = None
                        
                except Exception as e:
                    logger.error(f"❌ Universal index file loading failed: {e}")
                    traceback.print_exc()
                    index = big_npy = None
            else:
                index = big_npy = None
                logger.info("No index file used")
                
            # オーディオの前処理
            logger.info("Starting audio preprocessing...")
            original_audio_stats = f"max={np.max(audio):.3f}, min={np.min(audio):.3f}, mean={np.mean(audio):.3f}"
            logger.info(f"Original audio stats: {original_audio_stats}")
            
            audio = signal.filtfilt(self.bh, self.ah, audio)
            audio_pad = np.pad(audio, (self.window // 2, self.window // 2), mode="reflect")
            
            filtered_audio_stats = f"max={np.max(audio_pad):.3f}, min={np.min(audio_pad):.3f}"
            logger.info(f"Filtered & padded audio stats: {filtered_audio_stats}")
            
            # 改良版セグメント分割
            opt_ts = []
            if audio_pad.shape[0] > self.t_max:
                logger.info("Using VAD-based segmentation...")
                opt_ts = self.get_optimal_segments(audio_pad[self.window // 2 : -self.window // 2])
                logger.info(f"Segments created: {len(opt_ts)}")
            else:
                logger.info("Audio too short for segmentation")
            
            s = 0
            audio_opt = []
            t = None
            t1 = ttime()
            audio_pad = np.pad(audio, (self.t_pad, self.t_pad), mode="reflect")
            p_len = audio_pad.shape[0] // self.window
            inp_f0 = None
            
            logger.info(f"Audio padding completed: shape={audio_pad.shape}, p_len={p_len}")
            
            # F0ファイルの処理
            if hasattr(f0_file, "name"):
                try:
                    with open(f0_file.name, "r") as f:
                        lines = f.read().strip("\n").split("\n")
                    inp_f0 = []
                    for line in lines:
                        inp_f0.append([float(i) for i in line.split(",")])
                    inp_f0 = np.array(inp_f0, dtype="float32")
                    logger.info(f"F0 file loaded: {f0_file.name}")
                except Exception as e:
                    logger.error(f"❌ F0 file loading failed: {e}")
                    traceback.print_exc()
                    
            sid = torch.tensor(sid, device=self.device).unsqueeze(0).long()
            pitch, pitchf = None, None
            
            # 改良版F0推定
            if if_f0 == 1:
                logger.info(f"Starting F0 estimation with method: {f0_method}")
                try:
                    pitch, pitchf = self.get_f0_ensemble(
                        input_audio_path,
                        audio_pad,
                        p_len,
                        f0_up_key,
                        f0_method,
                        filter_radius,
                        inp_f0,
                    )
                    pitch = pitch[:p_len]
                    pitchf = pitchf[:p_len]
                    
                    logger.info(f"✅ F0 estimation successful: pitch shape={pitch.shape}, range={np.min(pitch):.1f}-{np.max(pitch):.1f}")
                    
                    if "mps" not in str(self.device) or "xpu" not in str(self.device):
                        pitchf = pitchf.astype(np.float32)
                    pitch = torch.tensor(pitch, device=self.device).unsqueeze(0).long()
                    pitchf = torch.tensor(pitchf, device=self.device).unsqueeze(0).float()
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"❌ F0 estimation failed with method '{f0_method}': {error_msg}")
                    
                    # MPS FFTエラーの特別な処理
                    if "aten::_fft_r2c" in error_msg or "MPS" in error_msg:
                        logger.error("🚨 MPS FFT Error Detected!")
                        logger.error("💡 SOLUTION: Please change F0 method from 'rmvpe' to 'harvest' in GUI settings")
                        logger.error("   - rmvpe uses FFT operations that are not supported on MPS")
                        logger.error("   - harvest is CPU-compatible and will work on MPS systems")
                        raise RuntimeError(f"F0 estimation failed on MPS: {f0_method} is not compatible with Apple Silicon GPU. Please use 'harvest' method instead.")
                    else:
                        logger.error(f"💡 SUGGESTION: Try using a different F0 method such as 'harvest' or 'dio'")
                        traceback.print_exc()
                        raise RuntimeError(f"F0 estimation failed with {f0_method}: {error_msg}")
            else:
                logger.info("No F0 estimation (if_f0=0)")
                
            t2 = ttime()
            times["f0"] += t2 - t1
            
            # セグメントごとの処理
            logger.info(f"Starting segment processing: {len(opt_ts)} segments")
            segment_count = 0
            
            for t in opt_ts:
                t = t // self.window * self.window
                segment_count += 1
                logger.info(f"Processing segment {segment_count}/{len(opt_ts)}: s={s}, t={t}")
                
                try:
                    # セグメント音声の検証
                    segment_audio = audio_pad[s : t + self.t_pad2 + self.window]
                    if segment_audio.size == 0:
                        logger.error(f"❌ Empty segment audio at segment {segment_count}")
                        continue
                    
                    logger.info(f"Segment audio shape: {segment_audio.shape}")
                    
                    if if_f0 == 1:
                        # ピッチ情報の検証
                        segment_pitch = pitch[:, s // self.window : (t + self.t_pad2) // self.window]
                        segment_pitchf = pitchf[:, s // self.window : (t + self.t_pad2) // self.window]
                        
                        logger.info(f"Segment pitch shape: {segment_pitch.shape}, pitchf shape: {segment_pitchf.shape}")
                        
                        segment_result = self.vc(
                            model,
                            net_g,
                            sid,
                            segment_audio,
                            segment_pitch,
                            segment_pitchf,
                            times,
                            index,
                            big_npy,
                            index_rate,
                            version,
                            protect,
                        )
                    else:
                        segment_result = self.vc(
                            model,
                            net_g,
                            sid,
                            segment_audio,
                            None,
                            None,
                            times,
                            index,
                            big_npy,
                            index_rate,
                            version,
                            protect,
                        )
                    
                    # 結果の検証
                    if segment_result is None or segment_result.size == 0:
                        logger.error(f"❌ Empty result from segment {segment_count}")
                        continue
                    
                    # パディング除去
                    trimmed_result = segment_result[self.t_pad_tgt : -self.t_pad_tgt]
                    
                    if trimmed_result.size == 0:
                        logger.error(f"❌ Empty result after padding removal at segment {segment_count}")
                        continue
                    
                    logger.info(f"✅ Segment {segment_count} processed: shape={trimmed_result.shape}, max={np.max(np.abs(trimmed_result)):.3f}")
                    audio_opt.append(trimmed_result)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing segment {segment_count}: {e}")
                    traceback.print_exc()
                    # セグメント処理失敗時は無音を追加してスキップ
                    expected_length = (t + self.t_pad2 + self.window - s) - 2 * self.t_pad_tgt
                    if expected_length > 0:
                        silent_segment = np.zeros(expected_length, dtype=np.float32)
                        audio_opt.append(silent_segment)
                        logger.warning(f"Added silent segment of length {expected_length}")
                
                s = t
            
            # 最後のセグメント処理
            logger.info("Processing final segment...")
            try:
                final_audio = audio_pad[t:] if t is not None else audio_pad
                if final_audio.size == 0:
                    logger.error("❌ Empty final segment audio")
                else:
                    logger.info(f"Final segment audio shape: {final_audio.shape}")
                    
                    if if_f0 == 1:
                        final_pitch = pitch[:, t // self.window :] if t is not None else pitch
                        final_pitchf = pitchf[:, t // self.window :] if t is not None else pitchf
                        
                        logger.info(f"Final segment pitch shape: {final_pitch.shape}, pitchf shape: {final_pitchf.shape}")
                        
                        final_result = self.vc(
                            model,
                            net_g,
                            sid,
                            final_audio,
                            final_pitch,
                            final_pitchf,
                            times,
                            index,
                            big_npy,
                            index_rate,
                            version,
                            protect,
                        )
                    else:
                        final_result = self.vc(
                            model,
                            net_g,
                            sid,
                            final_audio,
                            None,
                            None,
                            times,
                            index,
                            big_npy,
                            index_rate,
                            version,
                            protect,
                        )
                    
                    # 結果の検証
                    if final_result is None or final_result.size == 0:
                        logger.error("❌ Empty result from final segment")
                    else:
                        # パディング除去
                        trimmed_final = final_result[self.t_pad_tgt : -self.t_pad_tgt]
                        if trimmed_final.size == 0:
                            logger.error("❌ Empty final result after padding removal")
                        else:
                            logger.info(f"✅ Final segment processed: shape={trimmed_final.shape}, max={np.max(np.abs(trimmed_final)):.3f}")
                            audio_opt.append(trimmed_final)
                            
            except Exception as e:
                logger.error(f"❌ Error processing final segment: {e}")
                traceback.print_exc()
            
            # 音声データの結合と後処理
            if len(audio_opt) == 0:
                logger.error("❌ No audio segments were successfully processed")
                return np.array([], dtype=np.int16)
            
            logger.info(f"Concatenating {len(audio_opt)} audio segments...")
            
            # 各セグメントの統計情報をログ出力
            for i, segment in enumerate(audio_opt):
                logger.info(f"Segment {i}: shape={segment.shape}, max={np.max(np.abs(segment)):.3f}")
            
            audio_opt = np.concatenate(audio_opt)
            logger.info(f"✅ Audio concatenation successful: shape={audio_opt.shape}, max={np.max(np.abs(audio_opt)):.3f}")
            
            # RMS調整
            if rms_mix_rate != 1:
                logger.info(f"Applying RMS mixing with rate: {rms_mix_rate}")
                try:
                    audio_opt = change_rms(audio, 16000, audio_opt, tgt_sr, rms_mix_rate)
                    logger.info(f"✅ RMS mixing applied: max={np.max(np.abs(audio_opt)):.3f}")
                except Exception as e:
                    logger.error(f"❌ RMS mixing failed: {e}")
                    traceback.print_exc()
            
            # リサンプリング
            if tgt_sr != resample_sr >= 16000:
                logger.info(f"Resampling from {tgt_sr}Hz to {resample_sr}Hz")
                try:
                    audio_opt = librosa.resample(audio_opt, orig_sr=tgt_sr, target_sr=resample_sr)
                    logger.info(f"✅ Resampling successful: shape={audio_opt.shape}")
                except Exception as e:
                    logger.error(f"❌ Resampling failed: {e}")
                    traceback.print_exc()
            
            # 正規化と16bit変換
            logger.info("Applying final normalization and conversion to int16...")
            try:
                if audio_opt.size == 0:
                    logger.error("❌ Empty audio before normalization")
                    return np.array([], dtype=np.int16)
                
                audio_max = np.abs(audio_opt).max() / 0.99
                max_int16 = 32768
                if audio_max > 1:
                    max_int16 /= audio_max
                
                audio_opt = (audio_opt * max_int16).astype(np.int16)
                logger.info(f"✅ Final conversion successful: shape={audio_opt.shape}, dtype={audio_opt.dtype}")
                
                # メモリクリーンアップ
                del pitch, pitchf, sid
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                logger.info(f"🎉 Enhanced Pipeline completed successfully: output shape={audio_opt.shape}")
                return audio_opt
                
            except Exception as e:
                logger.error(f"❌ Final normalization failed: {e}")
                traceback.print_exc()
                return np.array([], dtype=np.int16)
        
        except Exception as e:
            logger.error(f"❌ Enhanced Pipeline failed with critical error: {e}")
            traceback.print_exc()
            
            # フォールバック処理を削除 - RVC変換失敗時は適切にエラーを報告
            logger.error("🚨 RVC音声変換に失敗しました。適切なモデルファイルと依存関係を確認してください。")
            raise RuntimeError(f"Enhanced Pipeline failed: {e}") from e


# 必要な関数を直接インポート
from .pipeline import change_rms, bh, ah