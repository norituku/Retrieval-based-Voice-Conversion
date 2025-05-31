"""
RVC推論プロセスにプログレスバーを統合するラッパー
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from typing import Optional, Tuple
import soundfile as sf
import numpy as np

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.progress_tracker import ProgressTracker, ProcessingStage
from ui.progress_bar_dark_mode import DarkModeProgressManager


class RVCProgressWrapper:
    """RVC推論にプログレスバーを統合するラッパークラス"""
    
    def __init__(self, dark_mode: bool = True):
        self.dark_mode = dark_mode
        self.progress_manager = None
        self.process = None
        
    def convert_with_progress(
        self,
        model_path: str,
        input_path: str,
        output_path: str,
        index_file: Optional[str] = None,
        f0method: str = "rmvpe",
        index_rate: float = 0.75,
        filter_radius: int = 3,
        resample_sr: int = 0,
        rms_mix_rate: float = 0.25,
        protect: float = 0.33,
        **kwargs
    ):
        """プログレスバー付きでRVC推論を実行"""
        
        # プログレスバーの初期化
        self.progress_manager = DarkModeProgressManager(
            "Voice Conversion 処理中",
            dark_mode=self.dark_mode
        )
        self.progress_manager.start()
        
        tracker = self.progress_manager.get_tracker()
        
        try:
            # 1. 初期化
            tracker.start_stage(ProcessingStage.INITIALIZATION)
            self._validate_inputs(model_path, input_path)
            tracker.complete_stage()
            
            # 2. データ読み込み
            tracker.start_stage(ProcessingStage.DATA_LOADING)
            audio_info = self._get_audio_info(input_path)
            tracker.complete_stage()
            
            # 3. 前処理（RVCコマンドの準備）
            tracker.start_stage(ProcessingStage.PREPROCESSING)
            cmd = self._build_rvc_command(
                model_path, input_path, output_path,
                index_file, f0method, index_rate,
                filter_radius, resample_sr, rms_mix_rate, protect
            )
            tracker.complete_stage()
            
            # 4-6. RVC推論の実行（特徴抽出、推論、後処理を含む）
            self._run_rvc_with_progress(cmd, tracker)
            
            # 7. 出力保存（確認）
            tracker.start_stage(ProcessingStage.SAVING_OUTPUT)
            self._verify_output(output_path)
            tracker.complete_stage()
            
            print(f"\n✅ 変換完了: {output_path}")
            time.sleep(2)
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            raise
            
        finally:
            if self.progress_manager:
                self.progress_manager.stop()
                
    def _validate_inputs(self, model_path: str, input_path: str):
        """入力ファイルの検証"""
        if not Path(model_path).exists():
            raise FileNotFoundError(f"モデルが見つかりません: {model_path}")
        if not Path(input_path).exists():
            raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")
            
    def _get_audio_info(self, input_path: str) -> dict:
        """音声ファイルの情報を取得"""
        info = sf.info(input_path)
        return {
            'duration': info.duration,
            'samplerate': info.samplerate,
            'channels': info.channels
        }
        
    def _build_rvc_command(
        self,
        model_path: str,
        input_path: str,
        output_path: str,
        index_file: Optional[str],
        f0method: str,
        index_rate: float,
        filter_radius: int,
        resample_sr: int,
        rms_mix_rate: float,
        protect: float
    ) -> list:
        """RVCコマンドを構築"""
        cmd = [
            "poetry", "run", "rvc", "infer",
            "-m", model_path,
            "-i", input_path,
            "-o", output_path,
            "-fm", f0method,
            "-ir", str(index_rate),
            "-fr", str(filter_radius),
            "-rmr", str(rms_mix_rate),
            "-p", str(protect)
        ]
        
        if index_file:
            cmd.extend(["-if", index_file])
            
        if resample_sr > 0:
            cmd.extend(["-rsr", str(resample_sr)])
            
        return cmd
        
    def _run_rvc_with_progress(self, cmd: list, tracker: ProgressTracker):
        """RVC推論をプログレス追跡しながら実行"""
        
        # 特徴抽出段階
        tracker.start_stage(ProcessingStage.FEATURE_EXTRACTION)
        
        # プロセスを開始
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 出力を監視しながら進捗を更新
        def monitor_output():
            stages_progress = {
                "Loading": 0.3,  # 特徴抽出の30%
                "Extracting": 0.7,  # 特徴抽出の70%
                "Processing": 0.5,  # 推論の50%
                "Generating": 0.8,  # 推論の80%
                "Saving": 0.9,  # 後処理の90%
            }
            
            current_stage = ProcessingStage.FEATURE_EXTRACTION
            
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    print(f"[RVC] {line.strip()}")
                    
                    # 進捗キーワードを検出
                    for keyword, progress in stages_progress.items():
                        if keyword.lower() in line.lower():
                            if keyword in ["Loading", "Extracting"]:
                                tracker.update_stage_progress(progress)
                            elif keyword in ["Processing", "Generating"]:
                                if current_stage != ProcessingStage.MODEL_INFERENCE:
                                    tracker.complete_stage()
                                    tracker.start_stage(ProcessingStage.MODEL_INFERENCE)
                                    current_stage = ProcessingStage.MODEL_INFERENCE
                                tracker.update_stage_progress(progress)
                            elif keyword == "Saving":
                                if current_stage != ProcessingStage.POSTPROCESSING:
                                    tracker.complete_stage()
                                    tracker.start_stage(ProcessingStage.POSTPROCESSING)
                                    current_stage = ProcessingStage.POSTPROCESSING
                                tracker.update_stage_progress(progress)
                                
            # 完了待機
            self.process.wait()
            
            if current_stage == ProcessingStage.FEATURE_EXTRACTION:
                tracker.complete_stage()
                tracker.start_stage(ProcessingStage.MODEL_INFERENCE)
                tracker.complete_stage()
                tracker.start_stage(ProcessingStage.POSTPROCESSING)
                
            tracker.complete_stage()
            
        # モニタリングスレッドを開始
        monitor_thread = threading.Thread(target=monitor_output)
        monitor_thread.start()
        monitor_thread.join()
        
        # エラーチェック
        if self.process.returncode != 0:
            stderr = self.process.stderr.read()
            raise RuntimeError(f"RVC推論が失敗しました: {stderr}")
            
    def _verify_output(self, output_path: str):
        """出力ファイルの確認"""
        if not Path(output_path).exists():
            raise FileNotFoundError(f"出力ファイルが生成されませんでした: {output_path}")
        
        # ファイルサイズチェック
        if Path(output_path).stat().st_size < 1000:  # 1KB未満は異常
            raise ValueError("出力ファイルが正常に生成されていない可能性があります")


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RVC Inference with Progress Bar")
    parser.add_argument("-m", "--model", type=str, required=True, help="モデルファイルのパス")
    parser.add_argument("-i", "--input", type=str, required=True, help="入力音声ファイル")
    parser.add_argument("-o", "--output", type=str, required=True, help="出力音声ファイル")
    parser.add_argument("-if", "--index-file", type=str, help="インデックスファイル")
    parser.add_argument("-fm", "--f0method", type=str, default="rmvpe", help="ピッチ抽出方法")
    parser.add_argument("-ir", "--index-rate", type=float, default=0.75, help="検索機能率")
    parser.add_argument("-fr", "--filter-radius", type=int, default=3, help="フィルター半径")
    parser.add_argument("-rsr", "--resample-sr", type=int, default=0, help="リサンプルレート")
    parser.add_argument("-rmr", "--rms-mix-rate", type=float, default=0.25, help="RMSミックス率")
    parser.add_argument("-p", "--protect", type=float, default=0.33, help="保護率")
    parser.add_argument("--light-mode", action="store_true", help="ライトモードを使用")
    
    args = parser.parse_args()
    
    # ラッパーの実行
    wrapper = RVCProgressWrapper(dark_mode=not args.light_mode)
    
    try:
        wrapper.convert_with_progress(
            model_path=args.model,
            input_path=args.input,
            output_path=args.output,
            index_file=args.index_file,
            f0method=args.f0method,
            index_rate=args.index_rate,
            filter_radius=args.filter_radius,
            resample_sr=args.resample_sr,
            rms_mix_rate=args.rms_mix_rate,
            protect=args.protect
        )
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()