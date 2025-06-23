# print("[DEBUG] infer.py script execution started!")

import logging
from pathlib import Path
import os
import sys
import soundfile as sf

# PyInstaller環境でのモジュールパス設定
if getattr(sys, 'frozen', False):
    print(f"[DEBUG] PyInstaller環境検出: sys.frozen = {sys.frozen}")
    print(f"[DEBUG] sys.executable = {sys.executable}")
    
    # PyInstallerでパッケージ化されている場合
    if hasattr(sys, '_MEIPASS'):
        # --onefile モード
        bundle_dir = sys._MEIPASS
    else:
        # --onedir モード
        bundle_dir = os.path.dirname(os.path.abspath(sys.executable))
        bundle_dir = os.path.join(bundle_dir, '_internal')
    
    print(f"[DEBUG] bundle_dir = {bundle_dir}")
    
    # rvcモジュールへのパスを追加
    rvc_path = os.path.join(bundle_dir, 'rvc')
    if os.path.exists(rvc_path) and rvc_path not in sys.path:
        sys.path.insert(0, bundle_dir)
        print(f"[DEBUG] Added to sys.path: {bundle_dir}")
    
    # PyInstallerのリソースディレクトリも確認
    resource_dir = os.path.join(bundle_dir, 'Contents', 'Resources')
    if os.path.exists(resource_dir) and resource_dir not in sys.path:
        sys.path.insert(0, resource_dir)
        print(f"[DEBUG] Added to sys.path: {resource_dir}")
    
    # macOSアプリケーションバンドルの場合の追加チェック
    if sys.platform == "darwin":
        # アプリケーションバンドル内のResourcesディレクトリを探す
        app_dir = bundle_dir
        while app_dir and not app_dir.endswith('.app'):
            app_dir = os.path.dirname(app_dir)
        
        if app_dir and app_dir.endswith('.app'):
            resource_dir = os.path.join(app_dir, 'Contents', 'Resources')
            if os.path.exists(resource_dir) and resource_dir not in sys.path:
                sys.path.insert(0, resource_dir)
                print(f"[DEBUG] Added macOS app Resources to sys.path: {resource_dir}")
    
    print(f"[DEBUG] Final sys.path (first 5): {sys.path[:5]}")

try:
    import click
    # print("[DEBUG] click imported successfully")
except ModuleNotFoundError as e:
    print(f"[DEBUG] FAILED to import click: {e}")
    # exit()

try:
    from dotenv import load_dotenv
    # print("[DEBUG] dotenv imported successfully")
except ModuleNotFoundError as e:
    print(f"[DEBUG] FAILED to import dotenv: {e}")
    # exit()

# print("[DEBUG] scipy.io.wavfile imported successfully")
# try:
#     from scipy.io import wavfile
#     print("[DEBUG] scipy.io.wavfile imported successfully")
# except ModuleNotFoundError as e:
#     print(f"[DEBUG] FAILED to import scipy.io.wavfile: {e}")
#     # exit()

# logging.getLogger("numba").setLevel(logging.WARNING)

try:
    from rvc.modules.vc.modules import VC
    from rvc.configs.config import Config
    # print("[DEBUG] rvc.modules.vc.modules imported successfully")
except ModuleNotFoundError as e:
    print(f"[DEBUG] FAILED to import rvc.modules.vc.modules: {e}")
    import sys
    import traceback
    print(f"[DEBUG] sys.path: {sys.path}")
    print(f"[DEBUG] Traceback: {traceback.format_exc()}")
    sys.exit(1)  # エラーが発生したら即座に終了
except ImportError as e:
    print(f"[DEBUG] FAILED to import rvc.modules.vc.modules (ImportError): {e}")
    import sys
    import traceback
    print(f"[DEBUG] sys.path: {sys.path}")
    print(f"[DEBUG] Traceback: {traceback.format_exc()}")
    sys.exit(1)  # エラーが発生したら即座に終了
except Exception as e:
    print(f"[DEBUG] UNEXPECTED ERROR during import: {e}")
    import sys
    import traceback
    print(f"[DEBUG] sys.path: {sys.path}")
    print(f"[DEBUG] Traceback: {traceback.format_exc()}")
    sys.exit(1)

# numba_logger = logging.getLogger("numba")
# numba_logger.setLevel(logging.WARNING)
# print("[DEBUG] Numba logging level set.")


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="inference audio",
)
@click.option(
    "-m",
    "--modelPath",
    is_flag=False,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="Model path or filename (reads in the directory set in env)",
    required=True,
)
@click.option(
    "-i",
    "--inputPath",
    is_flag=False,
    type=Path,
    help="input audio path or folder",
    required=True,
)
@click.option(
    "-o",
    "--outputPath",
    is_flag=False,
    type=Path,
    help="output audio path or folder",
    required=True,
)
@click.option(
    "-s", "--sid", is_flag=False, type=int, help="Speaker/Singer id", default=0
)
@click.option("-fu", "--f0upkey", is_flag=False, type=int, help="Transpose", default=0)
@click.option(
    "-fm",
    "--f0method",
    is_flag=False,
    type=str,
    help="Pitch extraction algorith",
    default="rmvpe",
)
@click.option(
    "-ff", "--f0file", is_flag=False, type=Path, help="F0 curve file (optional)"
)
@click.option("-if", "--indexFile", is_flag=False, type=Path, help="Feature index file")
@click.option(
    "-ir",
    "--indexRate",
    is_flag=False,
    type=float,
    help="Search feature ratio",
    default=0.75,
)
@click.option(
    "-fr",
    "--filterRadius",
    is_flag=False,
    type=int,
    help="Apply median filtering",
    default=3,
)
@click.option(
    "-rsr",
    "--resamplesr",
    is_flag=False,
    type=int,
    help="Resample the output audio",
    default=0,
)
@click.option(
    "-rmr",
    "--rmsmixrate",
    is_flag=False,
    type=float,
    help="Adjust the volume envelope scaling",
    default=0.25,
)
@click.option(
    "-p",
    "--protect",
    is_flag=False,
    type=float,
    help="Protect voiceless consonants and breath sounds",
    default=0.33,
)
@click.option(
    "--hubert_model_path",
    "hubertModelPath",
    is_flag=False,
    type=Path,
    help="Hubert model path (.pt file)",
    required=True,
)
def infer(
    modelpath,
    inputpath,
    outputpath,
    sid,
    f0upkey,
    f0method,
    f0file,
    indexfile,
    indexrate,
    filterradius,
    resamplesr,
    rmsmixrate,
    protect,
    hubertModelPath,
):
    # print("[DEBUG] infer() function called!")
    # print(f"[DEBUG] infer() args - modelpath: {modelpath}, inputpath: {inputpath}, outputpath: {outputpath}")

    # from rvc.modules.vc.modules import VC # これは既に先頭でインポート済みなので不要

    try:
        # print("[DEBUG] Attempting to load .env")
        load_dotenv() # ここで .env ファイルが読み込まれる
        # print(f"[DEBUG] os.getenv('rmvpe_root') after load_dotenv in infer(): {os.getenv('rmvpe_root')}")
        # print("[DEBUG] .env loaded (or no .env file found, which is also fine). Note: load_dotenv() might have been called at script top.")
    except Exception as e:
        print(f"[DEBUG] ERROR during load_dotenv() (if it was indeed called here): {e}")
        return # 問題発生時はここで止める

    try:
        # print("[DEBUG] Attempting to instantiate VC()")
        config = Config()
        vc = VC(config) # VCは先頭でfrom importされているはず
        # print("[DEBUG] VC() instantiated successfully.")
    except Exception as e:
        print(f"[DEBUG] ERROR during VC() instantiation: {e}")
        return

    try:
        # print(f"[DEBUG] Attempting to call vc.get_vc with modelpath: {modelpath}, indexfile: {indexfile}")
        vc.get_vc(
            modelpath, cli_index_file_path=Path(indexfile) if indexfile else None
        )
        # print("[DEBUG] vc.get_vc() called successfully.")
    except Exception as e:
        print(f"[DEBUG] ERROR during vc.get_vc(): {e}")
        return

    # print("[DEBUG] Before calling vc.vc_inference") # これは既存のデバッグプリント
    try:
        tgt_sr, audio_opt, times = vc.vc_inference(
            sid=sid,
            input_audio_path=Path(inputpath),
            f0_up_key=f0upkey,
            f0_method=f0method,
            f0_file=f0file,
            index_rate=indexrate,
            filter_radius=filterradius,
            resample_sr_cli=resamplesr,
            rms_mix_rate=rmsmixrate,
            protect=protect,
            hubert_path_cli=hubertModelPath,
        )
        # print(f"[DEBUG] After calling vc.vc_inference. tgt_sr: {tgt_sr}, audio_opt is None: {audio_opt is None}")
    except Exception as e:
        print(f"[DEBUG] ERROR during vc_inference: {e}")
        raise e

    print(f"[DEBUG] outputpath value: {outputpath}")
    print(f"[DEBUG] type of outputpath: {type(outputpath)}")
    if outputpath:
        print(f"[DEBUG] Inside 'if outputpath:' block. outputpath.resolve(): {str(outputpath.resolve())}")
        print(f"[DEBUG] Attempting to write to: {str(outputpath.resolve())}")
        print(f"[DEBUG] Target sampling rate: {tgt_sr}")
        print(f"[DEBUG] Audio data shape: {audio_opt.shape}")
        print(f"[DEBUG] Audio data dtype: {audio_opt.dtype}")
        if audio_opt is not None and audio_opt.ndim > 0 and audio_opt.size > 0:
            print(f"[DEBUG infer.py] Before sf.write - outputpath: {str(outputpath.resolve())}")
            print(f"[DEBUG infer.py] Before sf.write - tgt_sr for writing: {tgt_sr}")
            print(f"[DEBUG infer.py] Before sf.write - audio_opt.shape: {audio_opt.shape}")
            print(f"[DEBUG infer.py] Before sf.write - audio_opt.dtype: {audio_opt.dtype}")
            print(f"[DEBUG infer.py] Before sf.write - audio_opt min/max: {audio_opt.min()}/{audio_opt.max()}")

            sf.write(str(outputpath.resolve()), audio_opt, tgt_sr)
            click.echo(times)
            click.echo(f"Finish inference. Check {outputpath}")
        else:
            print(f"[DEBUG infer.py] audio_opt is None or empty. Shape: {audio_opt.shape if audio_opt is not None else 'None'}")
            click.echo("Error: Audio data is empty or invalid after inference.", err=True)
    else:
        print("[DEBUG] 'if outputpath:' condition is FALSE. outputpath is likely None or empty.")
    return tgt_sr, audio_opt, times

if __name__ == "__main__":
    # print("[DEBUG] __name__ == \"__main__\" block reached. Calling infer().") # このブロックが実行されるか
    infer()
