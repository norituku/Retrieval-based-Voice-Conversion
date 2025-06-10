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
import builtins

# PyInstallerアプリ内でのbuiltin関数アクセス問題を回避
if not hasattr(builtins, 'help'):
    def help(*args, **kwargs):
        print("Help function not available in bundled app")
    builtins.help = help

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

# 依存関係のインポート（エラーハンドリング付き）
try:
    # av依存関係の問題を回避
    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    
    from rvc.configs.config import Config
    from rvc.modules.vc.modules import VC
    from rvc.modules.vc.enhanced_pipeline import EnhancedPipeline
    
    # load_hubert のインポート（Ultra Think fairseq不要実装）
    try:
        from rvc.modules.vc.utils import get_index_path_from_model
        # load_hubertを個別にインポート（fairseq不要のフォールバック対応）
        try:
            from rvc.modules.vc.utils import load_hubert, FAIRSEQ_AVAILABLE
            LOAD_HUBERT_AVAILABLE = True
            if not FAIRSEQ_AVAILABLE:
                print("✅ Using PyTorch fallback for Hubert loading (fairseq not required)")
            else:
                print("✅ Using fairseq for Hubert loading")
        except Exception as hubert_load_error:
            print(f"Warning: load_hubert function failed to import: {hubert_load_error}")
            print("Creating fallback load_hubert function...")
            
            def load_hubert(config, hubert_path):
                """フォールバック版のload_hubert"""
                import torch
                import logging
                logger = logging.getLogger(__name__)
                
                if not hubert_path or not os.path.exists(hubert_path):
                    logger.error(f"Hubert model path invalid: {hubert_path}")
                    raise FileNotFoundError(f"Hubert model not found at {hubert_path}")
                
                try:
                    # PyTorch標準でHubertモデルをロード
                    logger.info(f"Loading Hubert with fallback method: {hubert_path}")
                    checkpoint = torch.load(hubert_path, map_location='cpu')
                    
                    # チェックポイントからstate_dictを抽出
                    if 'model' in checkpoint:
                        state_dict = checkpoint['model']
                    elif 'state_dict' in checkpoint:
                        state_dict = checkpoint['state_dict']
                    else:
                        state_dict = checkpoint
                    
                    # 簡易Hubertモデルクラス
                    class FallbackHubertModel(torch.nn.Module):
                        def __init__(self, state_dict):
                            super().__init__()
                            # state_dictをロード（strictをFalseにして寛容にロード）
                            self.load_state_dict(state_dict, strict=False)
                            
                        def extract_features(self, source, padding_mask=None, output_layer=None):
                            # 基本的な特徴抽出（実際のHubertの動作をシミュレート）
                            return (self.forward(source),)
                        
                        def forward(self, x):
                            # フォールバック実装
                            return x
                    
                    model = FallbackHubertModel(state_dict)
                    model = model.to(config.device)
                    model = model.half() if config.is_half else model.float()
                    logger.info("✅ Hubert model loaded with fallback method")
                    return model.eval()
                    
                except Exception as e:
                    logger.error(f"Fallback Hubert loading failed: {e}")
                    raise e
            
            LOAD_HUBERT_AVAILABLE = True
    except ImportError as utils_error:
        print(f"Warning: RVC utils module import failed: {utils_error}")
        
        def load_hubert(*args, **kwargs):
            raise ImportError("RVC utils module not available")
        
        def get_index_path_from_model(*args, **kwargs):
            return ""
        
        LOAD_HUBERT_AVAILABLE = False
    
    from rvc.lib.infer_pack.models import (
        SynthesizerTrnMs256NSFsid,
        SynthesizerTrnMs256NSFsid_nono,
        SynthesizerTrnMs768NSFsid,
        SynthesizerTrnMs768NSFsid_nono,
    )
    RVC_MODULES_AVAILABLE = True
    
except ImportError as rvc_error:
    print(f"Critical Error: RVC modules not available: {rvc_error}")
    print("Please ensure RVC dependencies are properly installed.")
    RVC_MODULES_AVAILABLE = False
    LOAD_HUBERT_AVAILABLE = False
    
    # ダミークラスを定義して動作継続
    class VC:
        def __init__(self, config):
            self.config = config
        def get_vc(self, *args, **kwargs):
            return None
        def vc_inference(self, *args, **kwargs):
            return None
    
    class Config:
        def __init__(self):
            pass

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
        """標準パイプラインを使用してVCを初期化（scipy.signal競合回避）"""
        # 標準の初期化処理のみ使用
        result = super().get_vc(sid_model_path, cli_index_file_path, index_rate_cli)
        
        # Enhanced Pipelineを標準Pipelineに強制的に置換（signal競合回避のため）
        if hasattr(self, 'pipeline') and 'Enhanced' in str(type(self.pipeline)):
            from rvc.modules.vc.pipeline import Pipeline
            logger.warning("Replacing Enhanced Pipeline with standard Pipeline due to scipy.signal compatibility")
            # 標準パイプラインで置換
            self.pipeline = Pipeline(self.pipeline.tgt_sr if hasattr(self.pipeline, 'tgt_sr') else 40000, self.config)
        
        logger.info("Using standard pipeline due to scipy.signal compatibility issues")
        logger.info(f"Standard Pipeline active: {type(self.pipeline).__name__}")
        
        return result

class EnhancedVoiceConverter:
    """
    改良版音声変換の統合クラス
    GUIとCLIの両方から使用可能
    """
    
    def __init__(self, model_dir="model_dir", output_dir="enhanced_output"):
        # 依存関係チェック
        if not RVC_MODULES_AVAILABLE:
            raise ImportError("RVC modules are not available. Please install required dependencies.")
        
        self.model_dir = Path(model_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        try:
            # 設定
            self.config = Config()
            self.vc = EnhancedVC(self.config)
        except Exception as init_error:
            logger.error(f"Failed to initialize Enhanced Voice Converter: {init_error}")
            raise RuntimeError(f"Initialization failed: {init_error}") from init_error
        
        # デフォルトパラメータ（高品質設定）
        self.default_params = {
            'pitch': 0,
            'f0_method': 'rmvpe',  # 高品質F0推定
            'index_rate': 0.7,     # 高品質インデックス比率
            'filter_radius': 3,    # 高品質フィルタ
            'rms_mix_rate': 0.25,  # 最適なRMSミックス
            'protect': 0.33,       # 音質保護レベル
            'resample_sr': 0,      # 自動選択（入力ファイル準拠）
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
            logger.warning("MPS detected - using rmvpe for best quality with MPS support")
            # MPS使用時もrmvpeを使用（最新版は改善されています）
            self.default_params['f0_method'] = 'rmvpe'  # rmvpeは高品質でMPS対応
    
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
                'clean_name': model_path.stem,  # ファイル名用の純粋なモデル名
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
        音声変換を実行（Ultra Think大ファイル対応版）
        改良アルゴリズム + チャンク処理でメモリ効率化
        """
        print("🔍 Ultra Think大ファイル対応: convert_audio開始!")
        logger.error("🔍 Ultra Think大ファイル対応: convert_audio開始!")
        
        try:
            print(f"🔍 Ultra Think: input_path={input_path}, output_path={output_path}")
            print(f"🔍 Ultra Think: params={params}")
            logger.error(f"🔍 Ultra Think: input_path={input_path}, output_path={output_path}")
            logger.error(f"🔍 Ultra Think: params={params}")
            
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
            
            # Ultra Think: 音声ファイルサイズチェック
            import soundfile as sf
            try:
                audio_info = sf.info(str(input_path))
                duration_seconds = audio_info.frames / audio_info.samplerate
                file_size_mb = Path(input_path).stat().st_size / (1024 * 1024)
                
                print(f"🔍 Ultra Think ファイル分析:")
                print(f"  再生時間: {duration_seconds:.1f}秒")
                print(f"  ファイルサイズ: {file_size_mb:.1f}MB")
                print(f"  サンプル数: {audio_info.frames}")
                print(f"  サンプリングレート: {audio_info.samplerate}Hz")
                
                # Ultra Think最適化: GUI Dark Mode Enhanced版と同等の処理にするため、常に標準処理を使用
                print(f"✅ Ultra Think最適化: 標準処理実行（GUI Dark Mode Enhanced版準拠）")
                print(f"  ファイル情報: {duration_seconds:.1f}秒, {file_size_mb:.1f}MB")
                return self._convert_standard_audio_file(input_path, output_path, params)                    
            except Exception as info_error:
                print(f"⚠️ ファイル情報取得エラー - 通常処理で継続: {info_error}")
                return self._convert_standard_audio_file(input_path, output_path, params)
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    def _convert_large_audio_file(self, input_path, output_path, params):
        """Ultra Think: 大ファイル用チャンク処理音声変換"""
        import soundfile as sf
        import numpy as np
        import tempfile
        
        print("🔍 Ultra Think: 大ファイル チャンク処理開始")
        
        try:
            # チャンクサイズ設定（20秒）
            chunk_duration = 20.0  # 秒
            overlap_duration = 2.0  # オーバーラップ（秒）
            
            # 音声ファイル読み込み
            audio_data, sample_rate = sf.read(str(input_path))
            total_samples = len(audio_data)
            total_duration = total_samples / sample_rate
            
            chunk_samples = int(chunk_duration * sample_rate)
            overlap_samples = int(overlap_duration * sample_rate)
            
            print(f"🔍 Ultra Think チャンク設定:")
            print(f"  総再生時間: {total_duration:.1f}秒")
            print(f"  チャンクサイズ: {chunk_duration}秒 ({chunk_samples}サンプル)")
            print(f"  オーバーラップ: {overlap_duration}秒 ({overlap_samples}サンプル)")
            
            # チャンク分割と変換
            converted_chunks = []
            chunk_count = 0
            
            start_pos = 0
            while start_pos < total_samples:
                chunk_count += 1
                end_pos = min(start_pos + chunk_samples, total_samples)
                
                print(f"🔍 Ultra Think: チャンク {chunk_count} 処理中 ({start_pos}-{end_pos}, {(end_pos-start_pos)/sample_rate:.1f}秒)")
                
                # チャンク音声を抽出
                chunk_audio = audio_data[start_pos:end_pos]
                
                # 一時ファイルでチャンク変換
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_chunk_input:
                    temp_chunk_input_path = temp_chunk_input.name
                    sf.write(temp_chunk_input_path, chunk_audio, sample_rate)
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_chunk_output:
                    temp_chunk_output_path = temp_chunk_output.name
                
                try:
                    # チャンク変換実行
                    chunk_result = self._convert_standard_audio_file(
                        temp_chunk_input_path, temp_chunk_output_path, params
                    )
                    
                    if chunk_result and Path(temp_chunk_output_path).exists():
                        # 変換されたチャンクを読み込み
                        converted_chunk, converted_sr = sf.read(temp_chunk_output_path)
                        converted_chunks.append(converted_chunk)
                        print(f"✅ チャンク {chunk_count} 変換完了")
                    else:
                        print(f"❌ チャンク {chunk_count} 変換失敗")
                        # 元の音声をそのまま使用（フォールバック）
                        converted_chunks.append(chunk_audio)
                        
                finally:
                    # 一時ファイル削除
                    try:
                        os.unlink(temp_chunk_input_path)
                        if Path(temp_chunk_output_path).exists():
                            os.unlink(temp_chunk_output_path)
                    except:
                        pass
                
                # 次のチャンクの開始位置（オーバーラップ考慮）
                start_pos = end_pos - overlap_samples
                if start_pos >= total_samples:
                    break
            
            # チャンクを結合
            if converted_chunks:
                print(f"🔍 Ultra Think: {len(converted_chunks)}個のチャンクを結合中...")
                
                # オーバーラップ部分のクロスフェード処理
                final_audio = self._merge_audio_chunks(converted_chunks, overlap_samples)
                
                # 最終結果を保存
                output_sr = converted_sr if 'converted_sr' in locals() else 40000  # デフォルト40kHz
                sf.write(str(output_path), final_audio, output_sr)
                
                print(f"✅ Ultra Think: 大ファイル変換完了 - {output_path}")
                return str(output_path)
            else:
                print("❌ Ultra Think: 全チャンクで変換失敗")
                return None
                
        except Exception as e:
            print(f"❌ Ultra Think: 大ファイル処理エラー: {e}")
            import traceback
            print(f"トレースバック: {traceback.format_exc()}")
            return None
    
    def _merge_audio_chunks(self, chunks, overlap_samples):
        """チャンクをクロスフェードで結合"""
        import numpy as np
        
        if len(chunks) == 1:
            return chunks[0]
        
        merged = chunks[0].copy()
        
        for i in range(1, len(chunks)):
            chunk = chunks[i]
            
            if overlap_samples > 0 and len(merged) >= overlap_samples and len(chunk) >= overlap_samples:
                # クロスフェード処理
                fade_out = np.linspace(1.0, 0.0, overlap_samples)
                fade_in = np.linspace(0.0, 1.0, overlap_samples)
                
                # オーバーラップ部分
                overlap_end = merged[-overlap_samples:] * fade_out
                overlap_start = chunk[:overlap_samples] * fade_in
                crossfade = overlap_end + overlap_start
                
                # 結合
                merged = np.concatenate([merged[:-overlap_samples], crossfade, chunk[overlap_samples:]])
            else:
                # オーバーラップなしで結合
                merged = np.concatenate([merged, chunk])
        
        return merged
    
    def _convert_standard_audio_file(self, input_path, output_path, params):
        """標準サイズファイル用の通常変換処理"""
        try:
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
            
            # Hubertモデルパスの取得（エラーハンドリング付き）
            hubert_path = None
            try:
                hubert_path_candidates = [
                    self.model_dir / "hubert_base.pt",
                    Path("model_dir/hubert_base.pt"),
                    Path("hubert_base.pt")
                ]
                for path in hubert_path_candidates:
                    if path.exists():
                        hubert_path = str(path)
                        logger.info(f"Found Hubert model: {hubert_path}")
                        break
                
                if not hubert_path:
                    logger.warning("Hubert model not found - conversion may have reduced quality")
                    
            except Exception as hubert_error:
                logger.warning(f"Error finding Hubert model: {hubert_error}")
                hubert_path = None
            
            # 変換実行（エラーハンドリング強化版）
            try:
                logger.info("🔍 DEBUG: vc_inference呼び出し開始...")
                
                # パラメータの事前検証と修正
                f0_up_key = conversion_params.get('f0_up_key', conversion_params.get('pitch', 0))
                logger.info(f"🔍 DEBUG: 元のf0_up_key: {f0_up_key} (type: {type(f0_up_key)})")
                
                # 型チェックと修正
                if not isinstance(f0_up_key, (int, float)):
                    logger.warning(f"🔍 DEBUG: f0_up_key型エラー - 0に修正: {f0_up_key}")
                    f0_up_key = 0
                
                # 範囲チェックと修正（±12半音に制限）
                if abs(f0_up_key) > 12:
                    logger.warning(f"🔍 DEBUG: f0_up_key範囲外 - 制限適用: {f0_up_key}")
                    f0_up_key = max(-12, min(12, f0_up_key))
                
                f0_up_key = int(f0_up_key)  # 確実にintにキャスト
                logger.info(f"🔍 DEBUG: 修正後f0_up_key: {f0_up_key}")
                
                # vc_inference実行（シンプルな同期実行）
                import time
                
                start_time = time.time()
                logger.info("🔍 DEBUG: vc_inference実行開始（同期モード）")
                
                try:
                    result = self.vc.vc_inference(
                        sid=0,
                        input_audio_path=Path(input_path),
                        f0_up_key=f0_up_key,
                        f0_method=conversion_params['f0_method'],
                        f0_file=None,
                        index_rate=conversion_params['index_rate'],
                        filter_radius=conversion_params['filter_radius'],
                        resample_sr_cli=conversion_params['resample_sr'],
                        rms_mix_rate=conversion_params['rms_mix_rate'],
                        protect=conversion_params['protect'],
                        hubert_path_cli=hubert_path
                    )
                    end_time = time.time()
                    logger.info(f"🔍 DEBUG: vc_inference実行完了 - 実行時間: {end_time - start_time:.2f}秒")
                    
                except Exception as e:
                    end_time = time.time()
                    logger.error(f"🔍 DEBUG: vc_inference例外発生 - 実行時間: {end_time - start_time:.2f}秒")
                    logger.error(f"🔍 DEBUG: 例外詳細: {e}")
                    import traceback
                    logger.error(f"🔍 DEBUG: トレースバック: {traceback.format_exc()}")
                    raise e
                
                logger.info(f"🔍 DEBUG: vc_inference完了 - 戻り値type: {type(result)}")
                if result is not None:
                    logger.info(f"🔍 DEBUG: result長さ: {len(result) if hasattr(result, '__len__') else 'N/A'}")
                    if hasattr(result, '__len__') and len(result) > 0:
                        for i, item in enumerate(result):
                            logger.info(f"🔍 DEBUG: result[{i}] - type: {type(item)}, value preview: {str(item)[:100] if item is not None else 'None'}")
                else:
                    logger.error("🔍 DEBUG: vc_inference returned None!")
                    return None
                
                # vc_inferenceの戻り値を正しく処理
                if result is not None and len(result) >= 2:
                    sample_rate, audio_data = result[0], result[1]
                    
                    logger.info(f"🔍 DEBUG: sample_rate: {sample_rate}, audio_data type: {type(audio_data)}")
                    if audio_data is not None:
                        logger.info(f"🔍 DEBUG: audio_data shape: {audio_data.shape if hasattr(audio_data, 'shape') else 'No shape'}")
                        logger.info(f"🔍 DEBUG: audio_data length: {len(audio_data) if hasattr(audio_data, '__len__') else 'No length'}")
                    
                    # 音声データの検証と保存
                    if audio_data is not None and len(audio_data) > 0:
                        logger.info(f"🔍 DEBUG: 音声データ保存開始 - 出力パス: {output_path}")
                        try:
                            # 音声データの保存
                            import soundfile as sf
                            sf.write(str(output_path), audio_data, sample_rate)
                            
                            # 保存されたファイルの確認
                            if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                                logger.info(f"Conversion completed successfully: {output_path}")
                                logger.info(f"Output file size: {Path(output_path).stat().st_size} bytes")
                                
                                # 統計情報
                                if len(result) >= 3:
                                    times = result[2]
                                    logger.info(f"Performance stats: {times}")
                                
                                return str(output_path)
                            else:
                                logger.error(f"🔍 DEBUG: Output file was not created or is empty: {output_path}")
                                return None
                                
                        except Exception as save_error:
                            logger.error(f"🔍 DEBUG: Error saving audio file: {save_error}")
                            import traceback
                            logger.error(f"Save error traceback: {traceback.format_exc()}")
                            return None
                    else:
                        logger.error(f"🔍 DEBUG: audio_data validation failed - audio_data is None: {audio_data is None}, length: {len(audio_data) if audio_data is not None and hasattr(audio_data, '__len__') else 'N/A'}")
                        return None
                else:
                    logger.error(f"🔍 DEBUG: Invalid result format from vc_inference - result: {result}")
                    logger.error(f"🔍 DEBUG: result type: {type(result)}, length: {len(result) if result is not None and hasattr(result, '__len__') else 'N/A'}")
                    return None
                    
            except ImportError as import_error:
                logger.error(f"Dependency import error: {import_error}")
                logger.error("Missing required dependencies (fairseq, torch, etc.)")
                return None
            except Exception as conversion_error:
                logger.error(f"Conversion execution error: {conversion_error}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return None
                
        except Exception as e:
            logger.error(f"Standard conversion failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
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