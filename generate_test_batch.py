#!/usr/bin/env python3
"""
バッチテスト用音声ファイル生成
"""

import numpy as np
import scipy.io.wavfile as wavfile
import os

def generate_test_batch():
    """複数のテスト音声を生成"""
    # テストディレクトリ作成
    test_dir = "test_batch_input"
    os.makedirs(test_dir, exist_ok=True)
    
    sample_rate = 44100
    
    # 異なる特性の音声を生成
    test_configs = [
        {"name": "test_440hz_3s", "freq": 440, "duration": 3.0},
        {"name": "test_880hz_2s", "freq": 880, "duration": 2.0},
        {"name": "test_220hz_4s", "freq": 220, "duration": 4.0},
        {"name": "test_complex_3s", "freq": [440, 554, 659], "duration": 3.0},  # 和音
        {"name": "test_sweep_3s", "freq": "sweep", "duration": 3.0},  # 周波数スイープ
    ]
    
    for config in test_configs:
        t = np.linspace(0, config["duration"], int(sample_rate * config["duration"]))
        
        if isinstance(config["freq"], list):
            # 和音生成
            signal = np.zeros_like(t)
            for freq in config["freq"]:
                signal += 0.3 * np.sin(2 * np.pi * freq * t)
        elif config["freq"] == "sweep":
            # 周波数スイープ（220Hz → 880Hz）
            freq_start = 220
            freq_end = 880
            freq_t = np.linspace(freq_start, freq_end, len(t))
            phase = 2 * np.pi * np.cumsum(freq_t) / sample_rate
            signal = 0.5 * np.sin(phase)
        else:
            # 単一周波数
            signal = 0.5 * np.sin(2 * np.pi * config["freq"] * t)
        
        # フェードイン・アウト
        fade_samples = int(0.1 * sample_rate)
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        signal[:fade_samples] *= fade_in
        signal[-fade_samples:] *= fade_out
        
        # 16ビット整数に変換
        signal_int16 = np.int16(signal * 32767)
        
        # ファイル保存
        output_path = os.path.join(test_dir, f"{config['name']}.wav")
        wavfile.write(output_path, sample_rate, signal_int16)
        
        print(f"✅ Generated: {output_path}")
    
    print(f"\n📁 Test batch files created in: {test_dir}/")
    return test_dir

if __name__ == "__main__":
    generate_test_batch()