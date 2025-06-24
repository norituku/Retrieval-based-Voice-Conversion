#!/usr/bin/env python3
"""
RVC Worker Process - Separate process to handle RVC inference
"""
import sys
import os
import json
import traceback

def setup_environment():
    """Setup environment for RVC execution"""
    # Add current directory to Python path
    if hasattr(sys, '_MEIPASS'):
        sys.path.insert(0, sys._MEIPASS)
        # Also add the Resources directory if in app bundle
        app_dir = os.path.dirname(os.path.dirname(sys.executable))
        resources_dir = os.path.join(app_dir, 'Contents', 'Resources')
        if os.path.exists(resources_dir):
            sys.path.insert(0, resources_dir)

def main():
    """Main worker function"""
    # 即座にデバッグ出力（インポート前）
    print("Worker: Starting up...", flush=True)
    sys.stdout.flush()
    
    try:
        print("Worker: Reading JSON arguments...", flush=True)
        sys.stdout.flush()
        
        # Check if args file is provided as command line argument
        if len(sys.argv) > 1:
            args_file = sys.argv[1]
            print(f"Worker: Reading args from file: {args_file}", flush=True)
            sys.stdout.flush()
            
            with open(args_file, 'r') as f:
                args_json = f.read()
            
            # Delete the temp file after reading
            try:
                os.remove(args_file)
            except:
                pass
        else:
            print("Worker: Reading args from stdin...", flush=True)
            sys.stdout.flush()
            # Read arguments from stdin
            args_json = sys.stdin.read()
        
        args = json.loads(args_json)
        
        print("Worker: JSON arguments parsed successfully", flush=True)
        print("Worker: Setting up environment...", flush=True)
        sys.stdout.flush()
        setup_environment()
        
        print("Worker: About to import RVC modules...", flush=True)
        sys.stdout.flush()
        
        print("Worker: Importing VC...", flush=True)
        sys.stdout.flush()
        from rvc.wrapper.cli.handler.infer import VC
        
        print("Worker: Importing Config...", flush=True) 
        sys.stdout.flush()
        from rvc.configs.config import Config
        
        print("Worker: RVC modules imported successfully", flush=True)
        print("Worker: Creating Config...", flush=True)
        sys.stdout.flush()
        config = Config()
        
        print("Worker: Config created successfully", flush=True)
        print("Worker: Creating VC instance...", flush=True)
        sys.stdout.flush()
        vc = VC(config)
        
        print("Worker: Loading model with get_vc...")
        from pathlib import Path
        vc.get_vc(
            sid_model_path=args['modelpath'],
            cli_index_file_path=Path(args['indexfile']) if args.get('indexfile') else None,
            index_rate_cli=args.get('indexrate', 0.75)
        )
        
        print(f"Worker: Starting inference...")
        print(f"  Model: {args['modelpath']}")
        print(f"  Input: {args['inputpath']}")
        print(f"  Output: {args['outputpath']}")
        
        # Perform inference
        import soundfile as sf
        sr, audio_data, inference_times = vc.vc_inference(
            sid=args.get('sid', 0),
            input_audio_path=Path(args['inputpath']),
            f0_up_key=args.get('f0upkey', 0),
            f0_method=args.get('f0method', 'rmvpe'),
            f0_file=None,
            index_rate=args.get('indexrate', 0.75),
            filter_radius=args.get('filterradius', 3),
            resample_sr_cli=args.get('resamplesr', 0),
            rms_mix_rate=args.get('rmsmixrate', 0.25),
            protect=args.get('protect', 0.33),
            hubert_path_cli=args['hubertModelPath']
        )
        
        # Save output file
        print(f"Worker: Saving output to {args['outputpath']}")
        sf.write(args['outputpath'], audio_data, sr)
        
        print(f"Worker: Inference completed successfully")
        print(f"Worker: Output saved to {args['outputpath']}")
        
        # Return success
        result = {
            'success': True,
            'output': args['outputpath']
        }
        print(f"RESULT:{json.dumps(result)}")
        
    except Exception as e:
        print(f"Worker: Error occurred: {str(e)}")
        traceback.print_exc()
        result = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        print(f"RESULT:{json.dumps(result)}")
        sys.exit(1)

if __name__ == "__main__":
    main()