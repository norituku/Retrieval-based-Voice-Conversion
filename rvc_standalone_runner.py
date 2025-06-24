#!/usr/bin/env python3
"""
Standalone RVC runner for PyInstaller environment.
This avoids the recursive subprocess issue by providing a direct entry point.
"""
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='RVC Standalone Runner')
    parser.add_argument('--modelPath', required=True, help='Path to model file')
    parser.add_argument('--inputPath', required=True, help='Path to input audio file')
    parser.add_argument('--outputPath', required=True, help='Path to output audio file')
    parser.add_argument('--indexFile', help='Path to index file')
    parser.add_argument('--sid', type=int, default=0, help='Speaker ID')
    parser.add_argument('--f0upkey', type=int, default=0, help='Pitch shift')
    parser.add_argument('--f0method', default='rmvpe', help='F0 method')
    parser.add_argument('--indexRate', type=float, default=0.75, help='Index rate')
    parser.add_argument('--filterRadius', type=int, default=3, help='Filter radius')
    parser.add_argument('--resamplesr', type=int, default=0, help='Resample sample rate')
    parser.add_argument('--rmsmixrate', type=float, default=0.25, help='RMS mix rate')
    parser.add_argument('--protect', type=float, default=0.33, help='Protect rate')
    parser.add_argument('--hubert_model_path', required=True, help='Path to Hubert model')
    
    args = parser.parse_args()
    
    # Import RVC modules
    print("Importing RVC modules...")
    from rvc.wrapper.cli.handler.infer import VC
    from rvc.configs.config import Config
    
    print("Initializing RVC...")
    config = Config()
    vc = VC(config)
    
    print(f"Starting inference...")
    print(f"Model: {args.modelPath}")
    print(f"Input: {args.inputPath}")
    print(f"Output: {args.outputPath}")
    
    # Perform inference
    vc.vc_single(
        sid=args.sid,
        input_audio_path=args.inputPath,
        f0_up_key=args.f0upkey,
        f0_file=None,
        f0_method=args.f0method,
        file_index=args.indexFile,
        file_index2="",
        index_rate=args.indexRate,
        filter_radius=args.filterRadius,
        resample_sr=args.resamplesr,
        rms_mix_rate=args.rmsmixrate,
        protect=args.protect,
        crepe_hop_length=128,
        vc_output_file=args.outputPath,
        vc_transform=0,
        model_path=args.modelPath,
        config=config,
        hubert_model_path=args.hubert_model_path
    )
    
    print(f"Inference completed: {args.outputPath}")

if __name__ == "__main__":
    main()