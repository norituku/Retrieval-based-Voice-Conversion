import logging
import os
import traceback
from io import BytesIO
from pathlib import Path
from typing import Union

import av
import librosa
import numpy as np
import soundfile as sf

logger: logging.Logger = logging.getLogger(__name__)


def wav2(wav_in, wav_out, format):
    if format == "flac":
        av.AudioResampler(format="s16", layout="mono", rate=44100).resample(
            av.open(wav_in, mode="r").decode("audio")
        ).encode(wav_out, codec="flac", format="flac")
    else:
        av.AudioResampler(format="s16", layout="mono", rate=44100).resample(
            av.open(wav_in, mode="r").decode("audio")
        ).encode(wav_out, format=format)


def audio2(audio_in, audio_out, target_format, target_sr):
    logger.info("audio2: input %s, output %s", audio_in, audio_out)
    inp = av.open(audio_in, "rb")
    if target_format == "f32le":
        out = av.open(audio_out, "wb", format="f32le")
        ost = out.add_stream("pcm_f32le", rate=target_sr, layout="mono")
    elif target_format == "s16le":
        out = av.open(audio_out, "wb", format="s16le")
        ost = out.add_stream("pcm_s16le", rate=target_sr, layout="mono")
    else:
        raise ValueError("Unknown target format")
    for frame in inp.decode(audio=0):
        for p in ost.encode(frame):
            out.write_packet(p)
    inp.close()
    out.close()


def load_audio(file: Union[str, Path], sr: int, to_mono: bool = False):
    # file が文字列の場合、Pathオブジェクトに変換
    if isinstance(file, str):
        file_obj = Path(file)
    elif isinstance(file, Path):
        file_obj = file
    else:
        # 予期しない型の場合のエラー処理 (通常は Union[str, Path] なのでここには来ないはず)
        logger.error(f"load_audio: Unexpected type for file argument: {type(file)}")
        raise TypeError(f"Expected str or Path, got {type(file)}")

    try:
        # https://github.com/librosa/librosa/issues/1015
        # https://github.com/librosa/librosa/issues/1271
        if not file_obj.exists(): # Pathオブジェクトの exists() を使用
            raise RuntimeError(
                f"You input a wrong audio path that does not exist: {file_obj}"
            )
        
        # M4A/AACファイルの場合はlibrosaを使用、その他はsoundfileを使用
        file_suffix = file_obj.suffix.lower()
        if file_suffix in ['.m4a', '.aac']:
            logger.info(f"Loading M4A/AAC file with librosa: {file_obj}")
            # librosaでM4A/AACファイルを読み込み（ffmpegバックエンド使用）
            audio_data, audio_sr = librosa.load(str(file_obj), sr=None, mono=False)
            # librosaは(チャンネル, サンプル)の順なので、soundfileと同じ形式に変換
            if audio_data.ndim > 1:
                audio_data = audio_data.T
        else:
            # 従来通りsoundfileで読み込み
            audio_data, audio_sr = sf.read(file_obj, dtype="float32")

        if audio_data.ndim > 1 and to_mono:
            audio_data = np.mean(audio_data, axis=1)
        
        if audio_data.ndim > 1 and not to_mono:
            audio_data = audio_data[:, 0]

        if audio_sr != sr:
            audio_data = librosa.resample(audio_data, orig_sr=audio_sr, target_sr=sr)

        return audio_data

    except AttributeError:
        logger.error(f"AttributeError in load_audio with file: {file}. This indicates an unexpected input type or structure.")
        raise

    except Exception as e:
        logger.error(f"Failed to load audio: {file}")
        logger.error(traceback.format_exc())
        raise e


def load_audio_from_bytes(audio_bytes: bytes, sr: int, to_mono: bool = False):
    try:
        with BytesIO(audio_bytes) as bio:
            audio_data, audio_sr = sf.read(bio, dtype="float32")

        if audio_data.ndim > 1 and to_mono:
            audio_data = np.mean(audio_data, axis=1)
        
        if audio_data.ndim > 1 and not to_mono:
            audio_data = audio_data[:, 0]

        if audio_sr != sr:
            audio_data = librosa.resample(audio_data, orig_sr=audio_sr, target_sr=sr)

        return audio_data
    except Exception as e:
        logger.error("Failed to load audio from bytes")
        logger.error(traceback.format_exc())
        raise e
