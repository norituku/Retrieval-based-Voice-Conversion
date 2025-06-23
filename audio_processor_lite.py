"""
audio_processor_lite.py - librosaを使わない軽量音声処理
soundfileのみを使用してRVCに必要な基本的な音声処理を実装
"""

import os
import sys
import numpy as np
import soundfile as sf
from pathlib import Path
import warnings

class AudioProcessorLite:
    """軽量音声処理クラス（librosa非依存）"""

    def __init__(self):
        self.default_sr = 22050

    def load_audio(self, file_path, sr=None, offset=0.0, duration=None):
        """
        音声ファイルを読み込む（librosa.loadの代替）

        Args:
            file_path: 音声ファイルパス
            sr: 目標サンプリングレート（Noneの場合は元のレートを維持）
            offset: 開始位置（秒）
            duration: 読み込む長さ（秒）

        Returns:
            audio: 音声データ (numpy array)
            sample_rate: サンプリングレート
        """
        try:
            # ファイル情報を取得
            info = sf.info(file_path)
            original_sr = info.samplerate

            # オフセットと期間の計算
            start_frame = int(offset * original_sr)
            frames = info.frames - start_frame

            if duration is not None:
                frames = min(frames, int(duration * original_sr))

            # 音声データの読み込み
            audio, file_sr = sf.read(
                file_path,
                start=start_frame,
                frames=frames,
                dtype='float32',
                always_2d=False
            )

            # モノラルに変換（ステレオの場合）
            if audio.ndim > 1:
                audio = np.mean(audio, axis=1)

            # リサンプリング（必要な場合）
            if sr is not None and sr != file_sr:
                audio = self.resample_simple(audio, file_sr, sr)
                file_sr = sr

            return audio, file_sr

        except Exception as e:
            warnings.warn(f"Error loading audio file: {e}")
            # フォールバック：無音を返す
            return np.zeros(self.default_sr), self.default_sr

    def save_audio(self, file_path, audio, sr=22050):
        """
        音声をファイルに保存

        Args:
            file_path: 保存先パス
            audio: 音声データ
            sr: サンプリングレート
        """
        # 値の範囲を-1.0から1.0にクリップ
        audio = np.clip(audio, -1.0, 1.0)

        # ファイルに書き込み
        sf.write(file_path, audio, sr, subtype='PCM_16')

    def resample_simple(self, audio, orig_sr, target_sr):
        """
        シンプルなリサンプリング（線形補間）

        Args:
            audio: 入力音声データ
            orig_sr: 元のサンプリングレート
            target_sr: 目標サンプリングレート

        Returns:
            リサンプリングされた音声データ
        """
        if orig_sr == target_sr:
            return audio

        # リサンプリング比率
        ratio = target_sr / orig_sr

        # 新しい長さ
        new_length = int(len(audio) * ratio)

        # 線形補間によるリサンプリング
        old_indices = np.arange(len(audio))
        new_indices = np.linspace(0, len(audio) - 1, new_length)

        resampled = np.interp(new_indices, old_indices, audio)

        return resampled

    def get_duration(self, file_path):
        """音声ファイルの長さを取得（秒）"""
        try:
            info = sf.info(file_path)
            return info.duration
        except:
            return 0.0

    def normalize_audio(self, audio, target_level=-20.0):
        """
        音声を正規化

        Args:
            audio: 入力音声
            target_level: 目標レベル (dB)

        Returns:
            正規化された音声
        """
        # RMS計算
        rms = np.sqrt(np.mean(audio**2))

        if rms > 0:
            # 目標RMSレベル
            target_rms = 10**(target_level / 20)

            # スケーリング係数
            scale = target_rms / rms

            # 適用（クリッピングを避ける）
            scaled = audio * scale
            max_val = np.max(np.abs(scaled))
            if max_val > 0.95:
                scaled = scaled * 0.95 / max_val

            return scaled
        else:
            return audio

    def trim_silence(self, audio, sr, threshold_db=-40, frame_length=2048):
        """
        無音部分をトリミング

        Args:
            audio: 入力音声
            sr: サンプリングレート
            threshold_db: 無音判定閾値 (dB)
            frame_length: フレーム長

        Returns:
            トリミングされた音声
        """
        # dBに変換
        threshold = 10**(threshold_db / 20)

        # フレームごとのエネルギー計算
        hop_length = frame_length // 4
        frames = []

        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            frame_energy = np.sqrt(np.mean(frame**2))
            frames.append(frame_energy > threshold)

        # 音声が含まれる範囲を検出
        if any(frames):
            start_frame = next(i for i, x in enumerate(frames) if x)
            end_frame = len(frames) - next(i for i, x in enumerate(reversed(frames)) if x)

            start_sample = start_frame * hop_length
            end_sample = min(end_frame * hop_length + frame_length, len(audio))

            return audio[start_sample:end_sample]
        else:
            return audio

# グローバルインスタンス
audio_processor = AudioProcessorLite()

# librosaのAPIをエミュレート
def load(file_path, sr=None, offset=0.0, duration=None, mono=True, res_type='kaiser_best'):
    """librosa.loadの代替実装"""
    return audio_processor.load_audio(file_path, sr, offset, duration)

def get_duration(filename=None, y=None, sr=22050):
    """librosa.get_durationの代替実装"""
    if filename is not None:
        return audio_processor.get_duration(filename)
    elif y is not None:
        return len(y) / sr
    else:
        raise ValueError("Either filename or y must be provided")

# RVCで使用される関数を提供
def wav2(audio, sr):
    """RVCのwav2関数の実装"""
    # 正規化とリサンプリング
    if sr != audio_processor.default_sr:
        audio = audio_processor.resample_simple(audio, sr, audio_processor.default_sr)

    # 正規化
    audio = audio_processor.normalize_audio(audio)

    return audio

def load_audio(file_path, sr=None):
    """RVCのload_audio関数の実装"""
    audio, file_sr = audio_processor.load_audio(file_path, sr)
    return audio

# テスト関数
if __name__ == "__main__":
    print("Audio Processor Lite - テスト")

    # テスト音声の作成
    test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 22050))

    # 保存と読み込みテスト
    audio_processor.save_audio("test_lite.wav", test_audio, 22050)
    loaded_audio, sr = audio_processor.load_audio("test_lite.wav")

    print(f"音声読み込み成功: shape={loaded_audio.shape}, sr={sr}")

    # クリーンアップ
    os.remove("test_lite.wav")
