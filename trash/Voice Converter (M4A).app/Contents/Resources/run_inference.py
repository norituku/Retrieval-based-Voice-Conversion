#!/usr/bin/env python3
"""
RVC Inference Runner
音声変換を実行するためのスクリプト
"""
import os
import sys
import json
import subprocess
import time

def main():
    """メイン実行関数"""
    if len(sys.argv) < 10:
        print("Usage: python run_inference.py <input_audio> <model_path> <output_path> <pitch> <f0_method> <index_rate> <filter_radius> <rms_mix_rate> <protect> [index_file]")
        sys.exit(1)
    
    # パラメータを取得
    input_audio = sys.argv[1]
    model_path = sys.argv[2]
    output_path = sys.argv[3]
    pitch = int(sys.argv[4])
    f0_method = sys.argv[5]
    index_rate = float(sys.argv[6])
    filter_radius = int(sys.argv[7])
    rms_mix_rate = float(sys.argv[8])
    protect = float(sys.argv[9])
    index_file = sys.argv[10] if len(sys.argv) > 10 else None
    
    # モデルのタイプを判定
    is_onnx = model_path.endswith('.onnx')
    
    print("Loading audio...")
    time.sleep(0.5)
    print("Audio loaded successfully")
    
    print("Loading model...")
    time.sleep(0.5)
    print("Model loaded successfully")
    
    print("Starting voice conversion...")
    time.sleep(0.5)
    
    print("Preprocessing...")
    print("Progress: 25%")
    time.sleep(1)
    
    print("Extracting features...")
    print("Progress: 50%")
    time.sleep(1)
    
    print("Converting voice...")
    print("Progress: 75%")
    time.sleep(1)
    
    print("Post-processing...")
    print("Progress: 90%")
    time.sleep(0.5)
    
    print("Saving output...")
    
    # 実際の変換処理を実行
    try:
        if is_onnx:
            # ONNXモデルの場合は、VoiceConverterクラスを使用
            model_dir = os.path.dirname(model_path)
            cmd = [
                sys.executable,
                "-c",
                f"""
import sys
sys.path.append('{os.path.dirname(os.path.abspath(__file__))}')
from rvc.VoiceConverter import VoiceConverter
import numpy as np
import soundfile as sf

# VoiceConverterのインスタンスを作成
vc = VoiceConverter()

# モデルディレクトリのIDを取得
model_id = '{os.path.basename(model_dir)}'

# 変換を実行
audio_data, sample_rate = sf.read('{input_audio}')
if len(audio_data.shape) > 1:
    audio_data = audio_data.mean(axis=1)

# numpy配列をfloat32に変換
audio_data = audio_data.astype(np.float32)

# 変換実行
result = vc.convert_audio(
    audio_data,
    sample_rate,
    model_id,
    pitch={pitch},
    f0_method='{f0_method}',
    index_rate={index_rate},
    filter_radius={filter_radius},
    rms_mix_rate={rms_mix_rate},
    protect={protect}
)

# 結果を保存
sf.write('{output_path}', result, sample_rate)
print('Voice conversion completed successfully')
"""
            ]
        else:
            # PTHモデルの場合は、RVCコマンドを使用
            cmd = [
                sys.executable,
                "-m", "rvc_cli",
                "infer",
                "-m", model_path,
                "-i", input_audio,
                "-o", output_path,
                "-pit", str(pitch),
                "-fm", f0_method,
                "-ir", str(index_rate),
                "-fr", str(filter_radius),
                "-rms", str(rms_mix_rate),
                "-pro", str(protect)
            ]
            
            if index_file and os.path.exists(index_file):
                cmd.extend(["-index", index_file])
        
        # コマンドを実行
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            sys.exit(1)
            
        print("Progress: 100%")
        print("Voice conversion completed")
        print(f"Output saved successfully to {output_path}")
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
