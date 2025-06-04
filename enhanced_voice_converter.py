#!/usr/bin/env python3
"""
Enhanced Voice Converter with Improved Algorithms
改良アルゴリズムを使用した音声変換システム
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path

# Poetry環境での実行を確保
def ensure_poetry_environment():
    """Poetry環境で実行されているかチェックし、必要に応じて再実行"""
    # Poetry環境で実行されているかの複数の検証
    poetry_env_active = False
    
    # 方法1: VIRTUAL_ENV環境変数をチェック
    if os.environ.get('VIRTUAL_ENV'):
        poetry_env_active = True
    
    # 方法2: 重要な依存関係をテスト
    if not poetry_env_active:
        try:
            import soundfile
            import torch
            poetry_env_active = True
        except ImportError:
            pass
    
    if not poetry_env_active:
        # Poetry環境で再実行
        script_path = Path(__file__).resolve()
        project_root = script_path.parent
        cmd = ["poetry", "run", "python", str(script_path)] + sys.argv[1:]
        
        print("Poetry環境で再実行しています...")
        print(f"実行コマンド: {' '.join(cmd)}")
        os.chdir(project_root)
        try:
            result = subprocess.run(cmd, cwd=project_root, check=True)
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print(f"Poetry実行エラー: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Poetry がインストールされていません。pip install poetry でインストールしてください。")
            sys.exit(1)

# GUI起動時は環境チェックをスキップ
# モジュールとしてインポートされる場合は環境チェックを実行しない
if __name__ == "__main__":
    ensure_poetry_environment()
elif 'gui' not in sys.argv[0].lower():
    # GUI以外からの呼び出しでPoetry環境でない場合のみチェック
    try:
        import soundfile
        import torch
    except ImportError:
        print("Warning: Some dependencies missing. Using basic mode.")
        pass

import numpy as np
import torch

# RVCモジュールの追加
sys.path.append(str(Path(__file__).parent / "rvc"))

from rvc.configs.config import Config
from rvc.modules.vc.modules import VC
from rvc.modules.vc.enhanced_pipeline import EnhancedPipeline
from rvc.lib.infer_pack.models import (
    SynthesizerTrnMs256NSFsid,
    SynthesizerTrnMs256NSFsid_nono,
    SynthesizerTrnMs768NSFsid,
    SynthesizerTrnMs768NSFsid_nono,
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedVC(VC):
    """
    改良版音声変換クラス
    高優先度の改善を実装：
    - 適応的近傍探索
    - F0推定のアンサンブル
    - VADベースセグメント分割
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.enhanced_features = {
            'adaptive_neighbors': True,
            'f0_ensemble': True,
            'vad_segmentation': True
        }
        logger.info("Enhanced VC initialized with improved algorithms")
    
    def get_vc(self, sid_model_path: str | Path, cli_index_file_path: Path | None = None, index_rate_cli: float = 0.75):
        """改良版パイプラインを使用してVCを初期化"""
        # 標準の初期化処理
        result = super().get_vc(sid_model_path, cli_index_file_path, index_rate_cli)
        
        # 改良版パイプラインに強制的に置き換え
        logger.info("Replacing standard pipeline with Enhanced Pipeline...")
        
        # tgt_srが設定されていない場合は適切な値を設定
        if self.tgt_sr is None:
            self.tgt_sr = 40000  # デフォルト値
            logger.warning(f"tgt_sr was None, set to default: {self.tgt_sr}")
        
        enhanced_pipeline = EnhancedPipeline(self.tgt_sr, self.config)
        
        # 既存パイプラインの全ての属性をコピー
        if hasattr(self, 'pipeline') and self.pipeline is not None:
            old_pipeline = self.pipeline
            # 全ての属性をコピー（メソッド以外）
            for attr_name in dir(old_pipeline):
                if not attr_name.startswith('_') and not callable(getattr(old_pipeline, attr_name)):
                    try:
                        attr_value = getattr(old_pipeline, attr_name)
                        setattr(enhanced_pipeline, attr_name, attr_value)
                    except Exception:
                        pass
        
        self.pipeline = enhanced_pipeline
        logger.info(f"Enhanced Pipeline successfully activated: {type(self.pipeline).__name__}")
        
        return result

class EnhancedVoiceConverter:
    """
    改良版音声変換の統合クラス
    GUIとCLIの両方から使用可能
    """
    
    def __init__(self, model_dir="model_dir", output_dir="enhanced_output"):
        self.model_dir = Path(model_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 設定
        self.config = Config()
        self.vc = EnhancedVC(self.config)
        
        # デフォルトパラメータ（環境設定より先に定義）
        self.default_params = {
            'pitch': 0,
            'f0_method': 'rmvpe',
            'index_rate': 1.0,
            'filter_radius': 3,
            'rms_mix_rate': 0.25,
            'protect': 0.33,
            'resample_sr': 0,
            'f0_up_key': 0
        }
        
        # 必要な環境変数の設定
        self._setup_environment()
        
        # 改良機能の設定
        self.enhancement_settings = {
            'adaptive_neighbors': {
                'enabled': True,
                'min_neighbors': 8,
                'max_neighbors': 32,
                'complexity_factor': 0.1
            },
            'f0_ensemble': {
                'enabled': True,
                'methods': ['rmvpe', 'harvest'],
                'weights': {'rmvpe': 0.7, 'harvest': 0.3}
            },
            'vad_segmentation': {
                'enabled': True,
                'energy_threshold_factor': 0.2,
                'boundary_tolerance': 0.1
            }
        }
        
        logger.info(f"Enhanced Voice Converter initialized")
        logger.info(f"Model directory: {self.model_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def _setup_environment(self):
        """必要な環境変数とパスの設定"""
        # rmvpe_rootの設定
        rmvpe_paths = [
            self.model_dir / "rmvpe.pt",
            Path("model_dir/rmvpe.pt"),
            Path("rmvpe.pt")
        ]
        
        for rmvpe_path in rmvpe_paths:
            if rmvpe_path.exists():
                os.environ['rmvpe_root'] = str(rmvpe_path.parent)
                logger.info(f"rmvpe_root set to: {rmvpe_path.parent}")
                break
        else:
            # rmvpe.ptが見つからない場合、model_dirを設定
            os.environ['rmvpe_root'] = str(self.model_dir)
            logger.warning(f"rmvpe.pt not found, using model_dir as rmvpe_root: {self.model_dir}")
        
        # その他の重要な環境変数
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # MPS環境でのweight_norm問題を回避
        
        # Hubertモデルパスの設定
        hubert_paths = [
            self.model_dir / "hubert_base.pt",
            Path("model_dir/hubert_base.pt"),
            Path("hubert_base.pt")
        ]
        
        for hubert_path in hubert_paths:
            if hubert_path.exists():
                os.environ['HUBERT_PATH'] = str(hubert_path)
                logger.info(f"HUBERT_PATH set to: {hubert_path}")
                break
        else:
            logger.warning("Hubert model not found - voice conversion quality may be limited")
        
        # MPSでFFTが動作しない問題への対処
        import torch
        if torch.backends.mps.is_available():
            logger.warning("MPS detected - using CPU for F0 estimation to avoid FFT issues")
            # MPS使用時はF0メソッドをCPU互換のものに変更
            self.default_params['f0_method'] = 'harvest'  # harvestはCPUで安定動作
    
    def list_available_models(self):
        """利用可能なモデル一覧を取得"""
        models = []
        
        if not self.model_dir.exists():
            logger.warning(f"Model directory not found: {self.model_dir}")
            return models
        
        for model_path in self.model_dir.rglob("*.pth"):
            # システムファイルをスキップ
            if model_path.name.startswith(('hubert', 'rmvpe')):
                continue
                
            model_info = {
                'name': model_path.stem,
                'path': str(model_path),
                'size': model_path.stat().st_size,
                'has_index': False,
                'index_path': None
            }
            
            # インデックスファイルを検索
            index_path = model_path.with_suffix('.index')
            if index_path.exists():
                model_info['has_index'] = True
                model_info['index_path'] = str(index_path)
            else:
                # 同じディレクトリで同名のインデックスファイルを検索
                for idx_file in model_path.parent.glob(f"{model_path.stem}*.index"):
                    model_info['has_index'] = True
                    model_info['index_path'] = str(idx_file)
                    break
            
            models.append(model_info)
        
        return sorted(models, key=lambda x: x['name'])
    
    def load_model(self, model_path, index_path=None, index_rate=1.0):
        """モデルを読み込み"""
        try:
            model_path = Path(model_path)
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # インデックスファイルのパスを決定
            if index_path is None:
                # 自動検索
                auto_index = model_path.with_suffix('.index')
                if auto_index.exists():
                    index_path = auto_index
                else:
                    # 同名のインデックスファイルを検索
                    for idx_file in model_path.parent.glob(f"{model_path.stem}*.index"):
                        index_path = idx_file
                        break
            
            # インデックスパスをPathオブジェクトに変換
            if index_path is not None:
                index_path = Path(index_path)
            
            # VCを初期化
            self.vc.get_vc(model_path, index_path, index_rate)
            
            logger.info(f"Model loaded successfully: {model_path}")
            if index_path:
                logger.info(f"Index file loaded: {index_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def convert_audio(self, input_path, output_path=None, **params):
        """
        音声変換を実行
        改良アルゴリズムを使用
        """
        try:
            input_path = Path(input_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # 出力パスの決定
            if output_path is None:
                output_filename = f"{input_path.stem}_converted.wav"
                output_path = self.output_dir / output_filename
            else:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # パラメータの準備
            conversion_params = self.default_params.copy()
            conversion_params.update(params)
            
            logger.info(f"Starting enhanced conversion:")
            logger.info(f"  Input: {input_path}")
            logger.info(f"  Output: {output_path}")
            logger.info(f"  Parameters: {conversion_params}")
            
            # 改良機能の状態をログ出力
            if hasattr(self.vc.pipeline, 'enable_adaptive_neighbors'):
                logger.info(f"  Enhanced features:")
                logger.info(f"    Adaptive neighbors: {self.vc.pipeline.enable_adaptive_neighbors}")
                logger.info(f"    F0 ensemble: {self.vc.pipeline.enable_f0_ensemble}")
                logger.info(f"    VAD segmentation: {self.vc.pipeline.enable_vad_segmentation}")
            
            # デバッグ: パイプラインの種類確認
            pipeline_type = type(self.vc.pipeline).__name__
            logger.info(f"Using pipeline type: {pipeline_type}")
            
            # 変換実行（正しいvc_inferenceメソッドを使用）
            result = self.vc.vc_inference(
                sid=0,
                input_audio_path=Path(input_path),
                f0_up_key=conversion_params['f0_up_key'],
                f0_method=conversion_params['f0_method'],
                f0_file=None,
                index_rate=conversion_params['index_rate'],
                filter_radius=conversion_params['filter_radius'],
                resample_sr_cli=conversion_params['resample_sr'],
                rms_mix_rate=conversion_params['rms_mix_rate'],
                protect=conversion_params['protect']
            )
            
            if len(result) >= 2:
                sample_rate, audio_data = result[0], result[1]
                
                # 音声データの保存
                import soundfile as sf
                sf.write(str(output_path), audio_data, sample_rate)
                
                logger.info(f"Conversion completed successfully: {output_path}")
                
                # 統計情報
                if len(result) >= 3:
                    times = result[2]
                    logger.info(f"Performance stats: {times}")
                
                return str(output_path)
            else:
                logger.error("Conversion failed: Invalid result")
                return None
                
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return None
    
    def batch_convert(self, input_files, output_dir=None, **params):
        """バッチ変換（改良アルゴリズム使用）"""
        if output_dir is None:
            output_dir = self.output_dir / "batch_output"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        total_files = len(input_files)
        
        logger.info(f"Starting enhanced batch conversion: {total_files} files")
        
        for i, input_file in enumerate(input_files):
            try:
                input_path = Path(input_file)
                output_filename = f"{input_path.stem}_enhanced.wav"
                output_path = output_dir / output_filename
                
                logger.info(f"Converting [{i+1}/{total_files}]: {input_path.name}")
                
                result = self.convert_audio(input_path, output_path, **params)
                
                if result:
                    results.append({
                        'input': str(input_path),
                        'output': result,
                        'status': 'success'
                    })
                    logger.info(f"  ✅ Success: {output_path.name}")
                else:
                    results.append({
                        'input': str(input_path),
                        'output': None,
                        'status': 'failed'
                    })
                    logger.error(f"  ❌ Failed: {input_path.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {input_file}: {e}")
                results.append({
                    'input': str(input_file),
                    'output': None,
                    'status': 'error',
                    'error': str(e)
                })
        
        # 結果サマリー
        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(f"Batch conversion completed: {success_count}/{total_files} successful")
        
        return results
    
    def get_enhancement_status(self):
        """改良機能の状態を取得"""
        status = {
            'pipeline_type': 'enhanced' if hasattr(self.vc.pipeline, 'enable_adaptive_neighbors') else 'standard',
            'features': {}
        }
        
        if hasattr(self.vc.pipeline, 'enable_adaptive_neighbors'):
            status['features'] = {
                'adaptive_neighbors': self.vc.pipeline.enable_adaptive_neighbors,
                'f0_ensemble': self.vc.pipeline.enable_f0_ensemble,
                'vad_segmentation': self.vc.pipeline.enable_vad_segmentation,
                'neighbor_range': f"{self.vc.pipeline.min_neighbors}-{self.vc.pipeline.max_neighbors}"
            }
        
        return status
    
    def configure_enhancements(self, **settings):
        """改良機能の設定を変更"""
        if not hasattr(self.vc.pipeline, 'enable_adaptive_neighbors'):
            logger.warning("Enhanced pipeline not available")
            return False
        
        if 'adaptive_neighbors' in settings:
            self.vc.pipeline.enable_adaptive_neighbors = settings['adaptive_neighbors']
            
        if 'f0_ensemble' in settings:
            self.vc.pipeline.enable_f0_ensemble = settings['f0_ensemble']
            
        if 'vad_segmentation' in settings:
            self.vc.pipeline.enable_vad_segmentation = settings['vad_segmentation']
            
        if 'neighbor_range' in settings:
            min_n, max_n = settings['neighbor_range']
            self.vc.pipeline.min_neighbors = min_n
            self.vc.pipeline.max_neighbors = max_n
        
        logger.info(f"Enhancement settings updated: {settings}")
        return True


def main():
    """テスト実行"""
    converter = EnhancedVoiceConverter()
    
    # 利用可能なモデルを表示
    models = converter.list_available_models()
    print(f"\nAvailable models: {len(models)}")
    for model in models:
        print(f"  - {model['name']} (Index: {'Yes' if model['has_index'] else 'No'})")
    
    # 改良機能の状態を表示
    status = converter.get_enhancement_status()
    print(f"\nEnhancement status: {status}")


if __name__ == "__main__":
    main()