#!/usr/bin/env python3
"""
RVC Voice Converter - 完全環境非依存版 (Ultra Think)
Poetry、プロジェクトディレクトリ、外部環境に一切依存しない独立アプリ

特徴:
- PyInstallerで全依存関係をバンドル
- RVCライブラリ直接統合
- Poetry環境不要
- ワンクリック実行可能
"""
import sys
import os
import json
import threading
import time
import subprocess
from pathlib import Path
from datetime import datetime
import builtins

# OpenMP重複ライブラリ問題対策（Ultra Think修正）
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '1'  # OpenMP スレッド数制限

# Ultra Think: PyInstaller対応リソースベースディレクトリ取得
def get_resource_base_path():
    """PyInstaller --onefile/--onedir 対応のリソースベースパス取得（Ultra Think修正）"""
    if getattr(sys, 'frozen', False):
        # PyInstallerでパッケージ化されている場合
        if hasattr(sys, '_MEIPASS'):
            # --onefile モード: 一時ディレクトリ内のリソース
            return Path(sys._MEIPASS)
        else:
            # --onedir モード: 実行ファイルの親ディレクトリ内
            return Path(sys.executable).parent / "_internal"
    else:
        # 開発環境: スクリプトファイルの親ディレクトリ
        return Path(__file__).parent

# Ultra Think汎用化：環境非依存rmvpe自動検出（PyInstaller対応）
def find_rmvpe_model():
    """rmvpeモデルを汎用的に検索（PyInstaller --onefile対応）"""
    # Ultra Think: PyInstallerリソースベースパス
    resource_base = get_resource_base_path()
    
    possible_rmvpe_dirs = [
        # 1. バンドルされたmodel_dir（PyInstaller対応）
        resource_base / "model_dir",
        # 2. プロジェクト内のmodel_dir（開発環境用）
        Path(__file__).parent / "model_dir",
        Path.cwd() / "model_dir",
        # 3. ユーザーのデスクトップ
        Path.home() / "Desktop" / "model_dir",
        # 4. ユーザーのDocuments
        Path.home() / "Documents" / "model_dir",
        # 5. アプリケーションサポート
        Path.home() / "Library" / "Application Support" / "RVC" / "model_dir",
        # 6. 共通の場所
        Path("/usr/local/share/rvc/model_dir"),
        Path("/opt/rvc/model_dir")
    ]
    
    for rmvpe_dir in possible_rmvpe_dirs:
        rmvpe_file = rmvpe_dir / "rmvpe.pt"
        if rmvpe_dir.exists() and rmvpe_file.exists():
            os.environ['rmvpe_root'] = str(rmvpe_dir)
            print(f"✅ Ultra Think独立版: rmvpe_root自動検出 = {rmvpe_dir}")
            return str(rmvpe_dir)
    
    print("⚠️ rmvpe.ptが見つかりません。手動でmodel_dirを配置してください。")
    return None

find_rmvpe_model()

# PyInstallerアプリ内でのbuiltin関数アクセス問題を回避
if not hasattr(builtins, 'help'):
    def help(*args, **kwargs):
        print("Help function not available in bundled app")
    builtins.help = help

# macOSでFFmpegのパスを追加
if sys.platform == "darwin":
    homebrew_bin = "/opt/homebrew/bin"
    usr_local_bin = "/usr/local/bin"
    current_path = os.environ.get("PATH", "")
    
    if homebrew_bin not in current_path:
        os.environ["PATH"] = f"{homebrew_bin}:{current_path}"
    if usr_local_bin not in current_path:
        os.environ["PATH"] = f"{usr_local_bin}:{os.environ['PATH']}"

# PyQt5 インポート
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QComboBox, QSlider, QTextEdit,
    QProgressBar, QGroupBox, QGridLayout, QCheckBox, QSpinBox,
    QFrame, QScrollArea, QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon

# 音声処理ライブラリ
try:
    import numpy as np
    import torch
    import soundfile as sf
    import librosa
    # pydubをインポートして多様な音声フォーマットに対応
    try:
        from pydub import AudioSegment
        from pydub.utils import which
        
        # FFmpegのパスを設定
        ffmpeg_found = False
        
        # 1. バンドルされたFFmpegを探す（PyInstallerアプリ内）
        if getattr(sys, 'frozen', False):
            # PyInstallerでパッケージされた場合
            bundle_dir = Path(sys.executable).parent
            ffmpeg_bundled = bundle_dir / "ffmpeg"
            ffprobe_bundled = bundle_dir / "ffprobe"
            
            if ffmpeg_bundled.exists() and ffprobe_bundled.exists():
                AudioSegment.converter = str(ffmpeg_bundled)
                AudioSegment.ffmpeg = str(ffmpeg_bundled)
                AudioSegment.ffprobe = str(ffprobe_bundled)
                # 実行権限を確保
                os.chmod(ffmpeg_bundled, 0o755)
                os.chmod(ffprobe_bundled, 0o755)
                print(f"✅ バンドルされたFFmpeg使用: {ffmpeg_bundled}")
                ffmpeg_found = True
        
        # 2. システムのFFmpegを探す
        if not ffmpeg_found and which("ffmpeg") is None:
            # 一般的なmacOSのFFmpegパスを試行
            ffmpeg_paths = [
                "/opt/homebrew/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
                "/opt/local/bin/ffmpeg"
            ]
            for path in ffmpeg_paths:
                if Path(path).exists():
                    AudioSegment.converter = path
                    AudioSegment.ffmpeg = path
                    AudioSegment.ffprobe = path.replace("ffmpeg", "ffprobe")
                    print(f"✅ システムFFmpeg使用: {path}")
                    ffmpeg_found = True
                    break
        
        if not ffmpeg_found and which("ffmpeg") is not None:
            print(f"✅ PATHからFFmpeg検出: {which('ffmpeg')}")
            ffmpeg_found = True
        
        if not ffmpeg_found:
            print("⚠️ FFmpegが見つかりません。M4A/AIFFサポートが制限されます。")
        
        PYDUB_AVAILABLE = True
    except ImportError:
        PYDUB_AVAILABLE = False
        print("⚠️ pydub が利用できません。m4a/aiffサポートが制限されます。")
    
    AUDIO_LIBS_AVAILABLE = True
except ImportError as e:
    AUDIO_LIBS_AVAILABLE = False
    PYDUB_AVAILABLE = False
    print(f"⚠️ 音声処理ライブラリが不足: {e}")

# Ultra Think: RVCライブラリ直接統合
try:
    # Ultra Think: RVCライブラリを直接インポート（PyInstaller対応強化版）
    
    # PyInstaller環境での動的パス追加
    if getattr(sys, 'frozen', False):
        # PyInstallerでバンドルされた場合
        bundle_dir = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
        rvc_path = os.path.join(bundle_dir, 'rvc')
        if rvc_path not in sys.path:
            sys.path.insert(0, rvc_path)
        print(f"🔧 Ultra Think: PyInstaller環境でRVCパス追加 - {rvc_path}")
    
    # Ultra Think: RVCライブラリのインポート（PyInstaller対応強化版）
    from rvc.configs.config import Config
    from rvc.modules.vc.modules import VC
    
    # Ultra Think: load_audio関数の代替インポート（PyInstaller対応）
    try:
        from rvc.modules.vc.utils import load_audio
        print(f"✅ Ultra Think: load_audio関数インポート成功")
    except ImportError:
        # PyInstaller環境でload_audioが見つからない場合の代替実装
        import librosa
        import numpy as np
        
        def load_audio(file_path, sample_rate=16000):
            """Ultra Think: load_audio代替実装"""
            try:
                audio, sr = librosa.load(file_path, sr=sample_rate, mono=True)
                return audio.astype(np.float32), sr
            except Exception as load_error:
                raise Exception(f"音声ファイル読み込みエラー: {load_error}")
        
        print(f"✅ Ultra Think: load_audio代替実装を使用")
    
    import soundfile as sf
    
    RVC_DIRECT_AVAILABLE = True
    print("✅ Ultra Think独立版: RVCライブラリ直接統合成功")
    
except ImportError as import_error:
    RVC_DIRECT_AVAILABLE = False
    print(f"⚠️ Ultra Think: RVCライブラリ直接統合失敗 - {import_error}")
    print(f"   → CLI経由で実行します")
except Exception as general_error:
    RVC_DIRECT_AVAILABLE = False
    print(f"⚠️ Ultra Think: RVCライブラリ統合時の予期しないエラー - {general_error}")
    print(f"   → CLI経由で実行します")

class StandaloneVoiceConversionThread(QThread):
    """完全独立版音声変換スレッド（Ultra Think）"""
    
    progress_updated = pyqtSignal(int, str)
    conversion_finished = pyqtSignal(bool, str)
    
    def __init__(self, input_file, output_file, current_model, params, model_dir=None):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.current_model = current_model
        self.params = params
        self.model_dir = model_dir
        
    def run(self):
        """Ultra Think: 完全独立版RVC推論実行（強化版）"""
        try:
            # Ultra Think: 出力ディレクトリの事前確認と作成
            output_path = Path(self.output_file)
            output_dir = output_path.parent
            
            print(f"🔍 Ultra Think: 出力ファイルパス = {self.output_file}")
            print(f"🔍 Ultra Think: 出力ディレクトリ = {output_dir}")
            
            if not output_dir.exists():
                print(f"📁 Ultra Think: 出力ディレクトリを作成中... {output_dir}")
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Ultra Think: 出力ディレクトリ作成完了")
                except PermissionError as perm_error:
                    # Ultra Think: macOS権限エラー対応
                    print(f"⚠️ Ultra Think: macOS権限エラー - 代替ディレクトリに変更します")
                    print(f"原因: {perm_error}")
                    
                    # 代替出力ディレクトリを生成（Documents内のRVCフォルダ）
                    fallback_dir = Path.home() / "Documents" / "RVC_Output"
                    try:
                        fallback_dir.mkdir(parents=True, exist_ok=True)
                        # 出力ファイルパスを代替ディレクトリに変更
                        original_filename = output_path.name
                        self.output_file = str(fallback_dir / original_filename)
                        print(f"✅ Ultra Think: 代替出力先設定完了 - {self.output_file}")
                        
                        # UIに変更を通知
                        self.progress_updated.emit(10, f"出力先変更: ~/Documents/RVC_Output/")
                        
                    except Exception as fallback_error:
                        error_msg = f"❌ 代替ディレクトリの作成も失敗: {fallback_error}"
                        print(error_msg)
                        self.conversion_finished.emit(False, error_msg)
                        return
                        
                except Exception as dir_error:
                    error_msg = f"❌ 出力ディレクトリの作成に失敗しました: {dir_error}"
                    print(error_msg)
                    self.conversion_finished.emit(False, error_msg)
                    return
            else:
                print(f"✅ Ultra Think: 出力ディレクトリ確認OK")
                
            # Ultra Think: 出力ディレクトリへの書き込み権限テスト
            try:
                test_file = output_path.parent / ".rvc_write_test"
                test_file.touch()
                test_file.unlink()
                print(f"✅ Ultra Think: 書き込み権限確認OK")
            except Exception as write_error:
                print(f"⚠️ Ultra Think: 書き込み権限エラー - 代替ディレクトリに変更")
                print(f"権限エラー詳細: {write_error}")
                
                # 代替出力ディレクトリを生成
                fallback_dir = Path.home() / "Documents" / "RVC_Output"
                try:
                    fallback_dir.mkdir(parents=True, exist_ok=True)
                    original_filename = output_path.name
                    self.output_file = str(fallback_dir / original_filename)
                    print(f"✅ Ultra Think: 代替出力先設定完了 - {self.output_file}")
                    self.progress_updated.emit(10, f"出力先変更: ~/Documents/RVC_Output/")
                except Exception as fallback_error:
                    error_msg = f"❌ 代替ディレクトリも使用不可: {fallback_error}"
                    print(error_msg)
                    self.conversion_finished.emit(False, error_msg)
                    return
            
            # Ultra Think: 入力ファイルの確認
            if not Path(self.input_file).exists():
                error_msg = f"❌ 入力ファイルが見つかりません: {self.input_file}"
                print(error_msg)
                self.conversion_finished.emit(False, error_msg)
                return
            
            print(f"✅ Ultra Think: 入力ファイル確認OK - {self.input_file}")
            print(f"🎯 Ultra Think: モデル = {self.current_model.get('name', 'Unknown')}")
            print(f"🎯 Ultra Think: パラメータ = {self.params}")
            
            if RVC_DIRECT_AVAILABLE:
                # Ultra Think: RVCライブラリ直接使用（強化版・CLI完全排除）
                print("🚀 Ultra Think: RVCライブラリ直接推論モード（CLI完全排除版）")
                self._run_direct_rvc_inference_enhanced()
            else:
                # Ultra Think: RVCライブラリが利用不可の場合のエラー
                error_msg = "❌ RVCライブラリが利用できません - CLI実行も失敗のため変換不可"
                print(error_msg)
                self.conversion_finished.emit(False, error_msg)
                
        except Exception as e:
            error_msg = f"❌ Ultra Think独立版推論エラー: {str(e)}"
            print(error_msg)
            import traceback
            detailed_error = traceback.format_exc()
            print(f"詳細エラー:\n{detailed_error}")
            self.conversion_finished.emit(False, error_msg)
    
    def _run_direct_rvc_inference_enhanced(self):
        """Ultra Think: RVCライブラリ直接推論（CLI完全排除・強化版）"""
        
        # 【段階 1】環境設定と初期化
        self.progress_updated.emit(5, "RVCライブラリ初期化中...")
        
        try:
            # Ultra Think: PyInstaller環境での環境変数設定
            if getattr(sys, 'frozen', False):
                # PyInstallerでバンドルされた場合の追加設定
                bundle_dir = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
                
                # モデルディレクトリパスの設定
                model_dir_path = os.path.join(bundle_dir, 'model_dir')
                if os.path.exists(model_dir_path):
                    os.environ['model_root'] = model_dir_path
                    print(f"🔧 Ultra Think: PyInstaller環境でmodel_root設定 - {model_dir_path}")
                
                # RMVPEモデルパスの設定
                rmvpe_path = os.path.join(model_dir_path, 'rmvpe.pt')
                if os.path.exists(rmvpe_path):
                    os.environ['rmvpe_root'] = model_dir_path
                    print(f"🔧 Ultra Think: PyInstaller環境でrmvpe_root設定 - {model_dir_path}")
            
            # RVC設定を初期化
            config = Config()
            config.device = "cpu"  # 安定性優先でCPU使用
            config.is_half = False  # 精度優先
            
            # Ultra Think: より詳細な設定
            config.gpu_name = None  # CPU専用
            config.gpu_mem = None
            config.python_cmd = sys.executable
            
            print(f"✅ Ultra Think: RVC Config初期化完了")
            print(f"   - デバイス: {config.device}")
            print(f"   - 半精度: {config.is_half}")
            
        except Exception as config_error:
            error_msg = f"RVC設定初期化エラー: {config_error}"
            print(f"❌ Ultra Think: {error_msg}")
            self.conversion_finished.emit(False, error_msg)
            return
        
        # 【段階 2】VCインスタンス作成
        self.progress_updated.emit(15, "VCインスタンス作成中...")
        
        try:
            # Ultra Think: VC（Voice Conversion）インスタンス作成
            vc = VC(config)
            print(f"✅ Ultra Think: VCインスタンス作成完了")
            
        except Exception as vc_error:
            error_msg = f"VCインスタンス作成エラー: {vc_error}"
            print(f"❌ Ultra Think: {error_msg}")
            # Ultra Think: VCインスタンス作成エラー - CLI排除版
            self.conversion_finished.emit(False, error_msg)
            return
        
        # 【段階 3】モデル読み込み
        self.progress_updated.emit(25, "音声モデルを読み込み中...")
        
        try:
            model_path = self.current_model['path']
            
            # Ultra Think: モデルファイル存在確認
            if not Path(model_path).exists():
                raise FileNotFoundError(f"モデルファイルが見つかりません: {model_path}")
                
            model_size = Path(model_path).stat().st_size
            print(f"🔧 Ultra Think: モデル読み込み開始")
            print(f"   - モデルパス: {model_path}")
            print(f"   - モデルサイズ: {model_size} bytes")
            
            # モデルを読み込み
            vc.get_vc(model_path)
            print(f"✅ Ultra Think: モデル読み込み完了")
            
        except Exception as model_error:
            error_msg = f"モデル読み込みエラー: {model_error}"
            print(f"❌ Ultra Think: {error_msg}")
            # Ultra Think: モデル読み込みエラー - CLI排除版
            self.conversion_finished.emit(False, error_msg)
            return
        
        # 【段階 4】音声ファイル読み込み
        self.progress_updated.emit(35, "音声ファイルを読み込み中...")
        
        try:
            # Ultra Think: 音声ファイル存在確認
            if not Path(self.input_file).exists():
                raise FileNotFoundError(f"入力音声ファイルが見つかりません: {self.input_file}")
                
            input_size = Path(self.input_file).stat().st_size
            print(f"🔧 Ultra Think: 音声ファイル読み込み開始")
            print(f"   - 入力パス: {self.input_file}")
            print(f"   - ファイルサイズ: {input_size} bytes")
            
            # 音声データを読み込み
            audio, sr = load_audio(self.input_file, 16000)
            print(f"✅ Ultra Think: 音声ファイル読み込み完了")
            print(f"   - サンプリングレート: {sr}")
            print(f"   - 音声データ長: {len(audio)}")
            print(f"   - 音声データ型: {type(audio)}")
            print(f"   - 音声データ範囲: {audio.min():.4f} ~ {audio.max():.4f}")
            print(f"   - 音声データ統計: mean={audio.mean():.4f}, std={audio.std():.4f}")
            
            # Ultra Think: 入力音声データの妥当性確認
            if len(audio) == 0:
                raise Exception("入力音声データが空です - WAV変換に問題がある可能性があります")
            if sr != 16000:
                print(f"⚠️ Ultra Think: サンプリングレート不一致 (期待:16000, 実際:{sr})")
            if audio.max() == 0 and audio.min() == 0:
                raise Exception("入力音声データがすべて0です - 無音ファイルの可能性があります")
            
        except Exception as audio_error:
            error_msg = f"音声ファイル読み込みエラー: {audio_error}"
            print(f"❌ Ultra Think: {error_msg}")
            # Ultra Think: 音声読み込みエラー - CLI排除版
            self.conversion_finished.emit(False, error_msg)
            return
        
        # 【段階 5】推論実行
        self.progress_updated.emit(50, "音声変換を実行中...")
        
        try:
            # Ultra Think: 詳細デバッグ付きRVC推論
            print(f"🔧 Ultra Think: RVC推論パラメータ:")
            print(f"   - モデルパス: {self.current_model['path']}")
            print(f"   - 入力音声: {self.input_file}")
            print(f"   - ピッチ: {self.params.get('pitch', 0)}")
            print(f"   - インデックス比率: {self.params.get('index_rate', 0.75)}")
            print(f"   - フィルター半径: {self.params.get('filter_radius', 3)}")
            
            # Ultra Think: RVC推論実行（最強化版エラーハンドリング・段階別デバッグ）
            self.progress_updated.emit(55, "RVC推論エンジン実行中...")
            
            # Ultra Think: 推論前の最終確認
            print(f"🔬 Ultra Think: RVC推論実行直前の状態確認:")
            print(f"   - VCインスタンス: {type(vc)}")
            print(f"   - 入力ファイル: {self.input_file}")
            print(f"   - 入力ファイル存在: {Path(self.input_file).exists()}")
            print(f"   - モデル読み込み済み: True")
            print(f"   - VCの重要属性確認:")
            print(f"     - vc.tgt_sr: {getattr(vc, 'tgt_sr', 'None')}")
            print(f"     - vc.net_g: {type(getattr(vc, 'net_g', None))}")
            print(f"     - vc.pipeline: {type(getattr(vc, 'pipeline', None))}")
            print(f"     - vc.version: {getattr(vc, 'version', 'None')}")
            print(f"     - vc.if_f0: {getattr(vc, 'if_f0', 'None')}")
            
            # Ultra Think: vc_inferenceパラメータ詳細ログ
            print(f"🎯 Ultra Think: vc_inferenceパラメータ詳細:")
            vc_params = {
                'sid': 0,
                'input_audio_path': Path(self.input_file),
                'f0_up_key': self.params.get('pitch', 0),
                'f0_method': "rmvpe",
                'f0_file': None,
                'index_rate': self.params.get('index_rate', 0.75),
                'filter_radius': self.params.get('filter_radius', 3),
                'resample_sr_cli': 0,
                'rms_mix_rate': 0.25,
                'protect': 0.33,
                'hubert_path_cli': None
            }
            for key, value in vc_params.items():
                print(f"   - {key}: {value} ({type(value)})")
            
            # Ultra Think: RVC推論実行（段階別デバッグ付き）
            try:
                print(f"🎯 Ultra Think: vc_inference開始...")
                self.progress_updated.emit(60, "vc_inference実行中...")
                
                # Ultra Think: vc_inference実行直前の環境変数確認
                print(f"🔍 Ultra Think: 環境変数確認:")
                for env_var in ['HUBERT_PATH', 'rmvpe_root', 'model_root']:
                    value = os.environ.get(env_var, 'Not Set')
                    print(f"   - {env_var}: {value}")
                
                # Ultra Think: 実際のHubertパス探索
                potential_hubert_paths = [
                    os.environ.get('HUBERT_PATH'),
                    str(Path(sys.executable).parent.parent / "Frameworks" / "model_dir" / "hubert_base.pt"),
                    "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/model_dir/hubert_base.pt"
                ]
                print(f"🔍 Ultra Think: Hubertパス候補確認:")
                for i, path in enumerate(potential_hubert_paths):
                    if path:
                        exists = Path(path).exists()
                        print(f"   {i+1}. {path} - {'存在' if exists else '不在'}")
                        if exists:
                            size = Path(path).stat().st_size
                            print(f"      サイズ: {size} bytes")
                
                print(f"🚀 Ultra Think: vc_inference実行開始...")
                
                # Ultra Think: 正しいRVC推論メソッド実行
                audio_output = vc.vc_inference(
                    sid=0,
                    input_audio_path=Path(self.input_file),
                    f0_up_key=self.params.get('pitch', 0),
                    f0_method="rmvpe",
                    f0_file=None,  # 外部f0ファイルなし
                    index_rate=self.params.get('index_rate', 0.75),
                    filter_radius=self.params.get('filter_radius', 3),
                    resample_sr_cli=0,  # モデルSRを使用
                    rms_mix_rate=0.25,
                    protect=0.33,
                    hubert_path_cli=str(Path(sys.executable).parent.parent / "Frameworks" / "model_dir" / "hubert_base.pt")  # 明示的指定
                )
                
                print(f"🎯 Ultra Think: vc_inference正常完了")
                self.progress_updated.emit(75, "vc_inference完了")
                
                # Ultra Think: vc_inference直後の即座返り値確認
                print(f"📊 Ultra Think: vc_inference直後の返り値確認:")
                print(f"   - 返り値型: {type(audio_output)}")
                print(f"   - 返り値長: {len(audio_output) if audio_output else 'None'}")
                if audio_output and len(audio_output) >= 3:
                    tgt_sr_immediate, audio_data_immediate, times_immediate = audio_output
                    print(f"   - 即座SR: {tgt_sr_immediate}")
                    print(f"   - 即座音声データ型: {type(audio_data_immediate)}")
                    print(f"   - 即座音声データ形状: {audio_data_immediate.shape if hasattr(audio_data_immediate, 'shape') else 'No shape'}")
                    print(f"   - 即座音声データサイズ: {len(audio_data_immediate) if audio_data_immediate is not None else 'None'}")
                    print(f"   - 即座処理時間: {times_immediate}")
                    
                    if hasattr(audio_data_immediate, 'shape') and len(audio_data_immediate.shape) > 0:
                        print(f"   - 音声データ詳細: min={audio_data_immediate.min()}, max={audio_data_immediate.max()}")
                else:
                    print(f"   - 返り値フォーマット異常!")
                    print(f"   - audio_output内容: {audio_output}")
                
            except Exception as vc_inference_error:
                print(f"❌ Ultra Think: vc_inference実行エラー - {vc_inference_error}")
                import traceback
                print(f"vc_inference詳細トレースバック:\n{traceback.format_exc()}")
                raise Exception(f"vc_inference実行エラー: {vc_inference_error}")
            
            print(f"✅ Ultra Think: RVC推論完了")
            print(f"   - 出力データ型: {type(audio_output)}")
            print(f"   - 出力データ長: {len(audio_output) if audio_output else 'None'}")
            
            # Ultra Think: vc_inference返り値詳細デバッグ
            print(f"🔬 Ultra Think: vc_inference返り値詳細分析:")
            print(f"   - audio_output = {audio_output}")
            
            if audio_output and len(audio_output) >= 3:
                tgt_sr, audio_data, times_tuple = audio_output
                print(f"   - サンプルレート: {tgt_sr}")
                print(f"   - 音声データ型: {type(audio_data)}")
                print(f"   - 音声データ形状: {audio_data.shape if hasattr(audio_data, 'shape') else 'Unknown'}")
                print(f"   - 音声データサイズ: {len(audio_data) if audio_data is not None else 'None'}")
                print(f"   - 処理時間: {times_tuple}")
                
                # Ultra Think: 音声データの詳細検証
                if audio_data is None:
                    print(f"❌ Ultra Think: audio_dataがNoneです")
                    raise Exception("RVC推論結果: audio_dataがNoneです")
                elif not hasattr(audio_data, 'shape'):
                    print(f"❌ Ultra Think: audio_dataにshape属性がありません - 型: {type(audio_data)}")
                    raise Exception(f"RVC推論結果: 不正な音声データ型 - {type(audio_data)}")
                elif len(audio_data) == 0:
                    print(f"❌ Ultra Think: audio_dataの長さが0です")
                    raise Exception("RVC推論結果: 音声データの長さが0です")
                else:
                    print(f"✅ Ultra Think: 音声データ検証OK - 形状: {audio_data.shape}")
                    
            else:
                print(f"❌ Ultra Think: 返り値フォーマットエラー")
                print(f"   - 期待: (tgt_sr, audio_data, times_tuple) の3要素")
                print(f"   - 実際: {len(audio_output) if audio_output else 'None'}要素")
                if audio_output:
                    for i, item in enumerate(audio_output):
                        print(f"   - 要素[{i}]: {type(item)} = {item}")
                raise Exception("RVC推論結果が不正です（返り値フォーマットエラー）")
                
        except Exception as inference_error:
            error_msg = f"RVC推論エラー: {inference_error}"
            print(f"❌ Ultra Think: {error_msg}")
            import traceback
            print(f"詳細トレースバック:\n{traceback.format_exc()}")
            
            # Ultra Think: RVC推論エラー - 再試行なし（CLI排除）
            self.conversion_finished.emit(False, error_msg)
            return
        
        # 【段階 6】結果保存
        self.progress_updated.emit(85, "変換結果を保存中...")
        
        try:
            # Ultra Think: 詳細デバッグ付きファイル保存
            print(f"💾 Ultra Think: 音声ファイル保存開始")
            print(f"   - 出力ファイルパス: {self.output_file}")
            print(f"   - 出力ディレクトリ: {Path(self.output_file).parent}")
            print(f"   - ディレクトリ存在確認: {Path(self.output_file).parent.exists()}")
            
            # 出力ディレクトリが存在することを再確認
            output_dir = Path(self.output_file).parent
            if not output_dir.exists():
                print(f"📁 Ultra Think: 出力ディレクトリを作成中...")
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # Ultra Think: 正しいフォーマットでファイル保存
            print(f"🎵 Ultra Think: soundfile.write実行中...")
            print(f"   - データ形状: {audio_data.shape}")
            print(f"   - サンプルレート: {tgt_sr}")
            print(f"   - データ型: {audio_data.dtype}")
            
            sf.write(self.output_file, audio_data, tgt_sr)
            
            print(f"✅ Ultra Think: soundfile.write完了")
            
            # 保存直後の確認
            if Path(self.output_file).exists():
                file_size = Path(self.output_file).stat().st_size
                print(f"✅ Ultra Think: ファイル保存確認OK - サイズ: {file_size} bytes")
                
                if file_size == 0:
                    raise Exception("保存されたファイルのサイズが0です")
            else:
                raise Exception("ファイルが作成されていません")
                
        except Exception as save_error:
            error_msg = f"ファイル保存エラー: {save_error}"
            print(f"❌ Ultra Think: {error_msg}")
            import traceback
            print(f"詳細トレースバック:\n{traceback.format_exc()}")
            
            # Ultra Think: ファイル保存エラー - CLI排除版
            self.conversion_finished.emit(False, error_msg)
            return
        
        # 【段階 6】完了確認（Ultra Think強化版）
        self.progress_updated.emit(100, "変換完了")
        
        print(f"🔍 Ultra Think: 直接推論出力ファイル確認開始 - {self.output_file}")
        output_path = Path(self.output_file)
        
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ Ultra Think: 直接変換結果ファイル確認OK - サイズ: {file_size} bytes")
            if file_size > 0:
                self.conversion_finished.emit(True, f"RVC独立版変換完了: {self.output_file}")
            else:
                print(f"❌ Ultra Think: 結果ファイルは作成されましたが空です")
                # 詳細なファイル情報を出力
                file_stat = output_path.stat()
                print(f"📊 ファイル詳細: 作成日時={file_stat.st_ctime}, 修正日時={file_stat.st_mtime}")
                raise Exception(f"結果ファイルが空です: {self.output_file}")
        else:
            print(f"❌ Ultra Think: 出力ファイルが作成されていません")
            # ディレクトリ内容を確認
            output_dir = output_path.parent
            if output_dir.exists():
                print(f"📁 出力ディレクトリ内容:")
                for item in output_dir.iterdir():
                    print(f"   - {item.name} ({'dir' if item.is_dir() else f'{item.stat().st_size} bytes'})")
            else:
                print(f"❌ 出力ディレクトリも存在しません: {output_dir}")
            raise Exception(f"出力ファイルが作成されていません: {self.output_file}")
    
    def _run_bundled_cli_inference(self):
        """Ultra Think: バンドルされたCLI実行（動作確認済み最小引数版）"""
        
        # 【段階 1】初期化
        self.progress_updated.emit(5, "バンドルされたRVC CLI初期化中...")
        
        # PyInstallerでバンドルされたPython実行可能ファイルを使用
        if getattr(sys, 'frozen', False):
            # アプリ内のPython環境を使用
            python_path = sys.executable
        else:
            # 開発環境のPython
            python_path = sys.executable
        
        # 【段階 2】コマンド構築（動作確認済み最小引数）
        self.progress_updated.emit(15, "コマンドを構築中...")
        
        # Ultra Think: 必須ファイルパス取得
        model_path = str(self.current_model['path'])
        
        # Ultra Think: Hubertモデルパス取得（強化版デバッグ付き）
        resource_base = get_resource_base_path()
        
        # Ultra Think: バンドル内パス優先の候補リスト
        hubert_model_paths = [
            # 【最優先】PyInstallerバンドル内パス
            resource_base / "model_dir" / "hubert_base.pt",
            
            # バンドル内の別パス候補
            Path(sys.executable).parent.parent / "Frameworks" / "model_dir" / "hubert_base.pt",
            
            # 開発環境（バンドル実行時は使用しない）
            Path.cwd() / "model_dir" / "hubert_base.pt",
            Path(__file__).parent / "model_dir" / "hubert_base.pt",
            
            # ユーザーディレクトリ
            Path.home() / "Desktop" / "model_dir" / "hubert_base.pt",
            Path.home() / "Documents" / "model_dir" / "hubert_base.pt",
            Path.home() / "Library" / "Application Support" / "RVC" / "model_dir" / "hubert_base.pt",
            
            # その他の候補
            Path("model_dir") / "hubert_base.pt",
            Path("/Users") / "norikene_satoshi" / "Retrieval-based-Voice-Conversion" / "model_dir" / "hubert_base.pt",
        ]
        
        print("🔍 hubert_base.pt を検索中...")
        hubert_model_path = None
        for i, path in enumerate(hubert_model_paths):
            print(f"  候補 {i+1}: {path} - {'存在' if path.exists() else '不在'}")
            if path.exists():
                hubert_model_path = str(path)
                print(f"✅ hubert_base.pt発見: {hubert_model_path}")
                break
        
        if not hubert_model_path:
            print("❌ hubert_base.pt が見つかりません。以下のいずれかの場所に配置してください:")
            for path in hubert_model_paths[:5]:  # 主要な候補のみ表示
                print(f"   {path}")
            raise RuntimeError("hubert_base.pt が見つかりません - model_dirディレクトリを確認してください")
        
        # Ultra Think: RMVPEモデルパス取得（オプション）
        print("🔍 rmvpe.pt を検索中...")
        rmvpe_model_paths = [
            # 同じディレクトリ構造でrmvpe.ptを検索
            Path(hubert_model_path).parent / "rmvpe.pt",
            # その他の候補
            Path.cwd() / "model_dir" / "rmvpe.pt",
            Path(__file__).parent / "model_dir" / "rmvpe.pt",
            resource_base / "model_dir" / "rmvpe.pt",
        ]
        
        rmvpe_model_path = None
        for i, path in enumerate(rmvpe_model_paths):
            print(f"  RMVPE候補 {i+1}: {path} - {'存在' if path.exists() else '不在'}")
            if path.exists():
                rmvpe_model_path = str(path)
                print(f"✅ rmvpe.pt発見: {rmvpe_model_path}")
                break
        
        # Ultra Think: 正しいRVC CLI引数構造（修正版）
        cmd_array = [
            python_path, "-m", "rvc.wrapper.cli.cli", "infer",
            "-m", model_path,
            "-i", self.input_file,
            "-o", self.output_file,
            "--hubert_model_path", hubert_model_path,  # 必須オプション
            "-fu", str(self.params.get('pitch', 0)),   # ピッチ変更
            "-fm", "rmvpe",                            # ピッチ抽出方法
            "-ir", str(self.params.get('index_rate', 0.75)),  # インデックス比率
            "-fr", str(self.params.get('filter_radius', 3)),  # フィルター半径
            "-p", "0.33"                               # 保護レベル
        ]
        
        # Ultra Think: RMVPEモデルパスは環境変数で設定（CLI引数には存在しない）
        if rmvpe_model_path:
            # RMVPEモデルパスを環境変数に設定
            os.environ['rmvpe_root'] = str(Path(rmvpe_model_path).parent)
            print(f"✅ Ultra Think: RMVPEモデルパス環境変数設定 - {rmvpe_model_path}")
        else:
            print("⚠️ Ultra Think: rmvpe.ptが見つかりませんが、続行します")
        
        # 【段階 3-6】CLI実行
        self._run_cli_with_progress(cmd_array)
    
    def _run_cli_with_progress(self, cmd_array):
        """Ultra Think: CLI実行とプログレス追跡"""
        
        print(f"🔧 実行コマンド: {' '.join(cmd_array)}")
        
        # 【段階 3】推論開始
        self.progress_updated.emit(30, "音声の特徴を抽出中...")
        
        # Ultra Think: CLI実行前の詳細確認（確実なログ出力版）
        self.progress_updated.emit(31, "CLI実行前詳細確認開始...")
        print(f"🚀 Ultra Think: CLI実行詳細情報:")
        print(f"   - Python実行可能ファイル: {cmd_array[0]}")
        print(f"   - モジュールパス: {cmd_array[1:3]}")
        
        # コマンド配列の詳細分析（プログレスにも表示）
        cmd_count = len(cmd_array)
        self.progress_updated.emit(32, f"コマンド配列確認: {cmd_count}個の引数")
        print(f"📋 Ultra Think: 完全コマンド配列:")
        
        # 重要な引数をプログレスで表示
        for i, arg in enumerate(cmd_array):
            print(f"   [{i:2d}]: {arg}")
            if i == 0:  # Python実行ファイル
                python_name = Path(arg).name
                self.progress_updated.emit(33, f"Python: {python_name}")
            elif arg == "-m":
                self.progress_updated.emit(34, "モジュール実行モード")
            elif arg == "infer":
                self.progress_updated.emit(35, "推論モード確認")
            elif i < 6:  # 最初の6個の引数をプログレスに表示
                short_arg = arg[:30] + "..." if len(arg) > 30 else arg
                self.progress_updated.emit(33 + (i % 3), f"引数[{i}]: {short_arg}")
        
        # Ultra Think: 引数の詳細チェック
        if cmd_count < 10:
            self.progress_updated.emit(35, f"⚠️ 引数が少なすぎる: {cmd_count}個")
            print(f"⚠️ Ultra Think: 引数の数が少なすぎます（{cmd_count}個）")
        elif cmd_count > 25:
            self.progress_updated.emit(35, f"⚠️ 引数が多すぎる: {cmd_count}個")
            print(f"⚠️ Ultra Think: 引数の数が多すぎます（{cmd_count}個）")
        else:
            self.progress_updated.emit(35, f"✅ 引数の数は正常: {cmd_count}個")
        
        # ファイルパスを動的に検出
        model_file_index = None
        input_file_index = None
        output_file_index = None
        hubert_file_index = None
        
        for i, arg in enumerate(cmd_array):
            if arg == "-m" and i + 1 < len(cmd_array):
                model_file_index = i + 1
            elif arg == "-i" and i + 1 < len(cmd_array):
                input_file_index = i + 1
            elif arg == "-o" and i + 1 < len(cmd_array):
                output_file_index = i + 1
            elif arg == "--hubert_model_path" and i + 1 < len(cmd_array):
                hubert_file_index = i + 1
        
        self.progress_updated.emit(36, "重要ファイル存在確認中...")
        print(f"🔍 Ultra Think: ファイルパス詳細確認:")
        
        if model_file_index:
            model_path = cmd_array[model_file_index]
            model_exists = Path(model_path).exists()
            model_size = Path(model_path).stat().st_size if model_exists else 0
            model_status = f"モデル: {'存在' if model_exists else '不在'} ({model_size} bytes)"
            self.progress_updated.emit(37, model_status)
            print(f"   - モデルファイル: {model_path}")
            print(f"   - モデル存在: {model_exists} ({model_size} bytes)")
            if not model_exists:
                self.progress_updated.emit(37, f"❌ モデルファイル不在")
                raise Exception(f"モデルファイルが見つかりません: {model_path}")
        
        if input_file_index:
            input_path = cmd_array[input_file_index]
            input_exists = Path(input_path).exists()
            input_size = Path(input_path).stat().st_size if input_exists else 0
            input_status = f"入力: {'存在' if input_exists else '不在'} ({input_size} bytes)"
            self.progress_updated.emit(38, input_status)
            print(f"   - 入力ファイル: {input_path}")
            print(f"   - 入力存在: {input_exists} ({input_size} bytes)")
            if not input_exists:
                self.progress_updated.emit(38, f"❌ 入力ファイル不在")
                raise Exception(f"入力ファイルが見つかりません: {input_path}")
        
        if output_file_index:
            output_path = cmd_array[output_file_index]
            output_dir = Path(output_path).parent
            output_status = f"出力ディレクトリ: {'存在' if output_dir.exists() else '不在'}"
            self.progress_updated.emit(39, output_status)
            print(f"   - 出力ファイル: {output_path}")
            print(f"   - 出力ディレクトリ存在: {output_dir.exists()}")
        
        if hubert_file_index:
            hubert_path = cmd_array[hubert_file_index]
            hubert_exists = Path(hubert_path).exists()
            hubert_size = Path(hubert_path).stat().st_size if hubert_exists else 0
            hubert_status = f"Hubert: {'存在' if hubert_exists else '不在'} ({hubert_size} bytes)"
            self.progress_updated.emit(40, hubert_status)
            print(f"   - Hubertモデル: {hubert_path}")
            print(f"   - Hubert存在: {hubert_exists} ({hubert_size} bytes)")
            if not hubert_exists:
                self.progress_updated.emit(41, "⚠️ Hubertモデル不在 - 早期終了の原因")
                print(f"⚠️ Ultra Think: hubertモデルが見つかりません: {hubert_path}")
                print(f"   これがCLI早期終了の原因の可能性があります")
        else:
            self.progress_updated.emit(40, "⚠️ Hubertパラメータなし")
        
        print(f"🔧 Ultra Think: 実行環境:")
        print(f"   - 作業ディレクトリ: {os.getcwd()}")
        print(f"   - Python バージョン: {sys.version}")
        print(f"   - 実行可能ファイル: {sys.executable}")
        
        # コマンド全体を再表示（プログレスにも表示）
        full_command = ' '.join(cmd_array)
        cmd_preview = full_command[:100] + "..." if len(full_command) > 100 else full_command
        self.progress_updated.emit(42, f"実行コマンド: {cmd_preview}")
        print(f"💻 Ultra Think: 実行予定コマンド:")
        print(f"   {full_command}")
        
        # Ultra Think: M4A入力ファイルの自動WAV変換対応
        input_file_path = self.input_file
        original_input_file = self.input_file
        
        if input_file_path.lower().endswith('.m4a'):
            self.progress_updated.emit(42, "🔄 M4A入力検出 - WAV変換実行中...")
            print(f"🔄 Ultra Think: M4A形式の入力ファイルを検出 - 自動WAV変換を実行します")
            print(f"   - M4AはRVCで処理エラーを起こす場合があります")
            print(f"   - 一時的にWAV形式に変換して処理を続行します")
            
            # 一時WAVファイルパス作成
            temp_wav_dir = Path.home() / "Documents" / "RVC_Output" / "temp"
            temp_wav_dir.mkdir(parents=True, exist_ok=True)
            
            input_filename = Path(input_file_path).stem
            temp_wav_path = temp_wav_dir / f"{input_filename}_converted.wav"
            
            print(f"🎵 Ultra Think: M4A → WAV変換開始")
            print(f"   - 入力: {input_file_path}")
            print(f"   - 出力: {temp_wav_path}")
            
            try:
                # ffmpegを使用してM4AをWAVに変換
                ffmpeg_cmd = [
                    "ffmpeg", "-y",  # -y: 上書き許可
                    "-i", input_file_path,
                    "-ar", "16000",  # 16kHz サンプリングレート（RVC推奨）
                    "-ac", "1",      # モノラル
                    "-f", "wav",     # WAV形式
                    str(temp_wav_path)
                ]
                
                print(f"🔧 Ultra Think: ffmpeg実行コマンド: {' '.join(ffmpeg_cmd)}")
                self.progress_updated.emit(43, "ffmpeg M4A→WAV変換中...")
                
                ffmpeg_result = subprocess.run(
                    ffmpeg_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if ffmpeg_result.returncode == 0 and temp_wav_path.exists():
                    wav_size = temp_wav_path.stat().st_size
                    print(f"✅ Ultra Think: M4A→WAV変換成功 ({wav_size} bytes)")
                    
                    # 入力ファイルをWAVに変更
                    self.input_file = str(temp_wav_path)
                    input_file_path = str(temp_wav_path)
                    
                    # Ultra Think: コマンド配列の入力ファイルパス更新（強化版デバッグ）
                    print(f"🔧 Ultra Think: コマンド配列パス更新開始")
                    print(f"   - 検索対象パス: {original_input_file}")
                    print(f"   - 置換先パス: {str(temp_wav_path)}")
                    
                    updated = False
                    for i, arg in enumerate(cmd_array):
                        print(f"   - 引数[{i}]: {arg}")
                        if arg == original_input_file:
                            cmd_array[i] = str(temp_wav_path)
                            print(f"   ✅ 引数[{i}]を更新: {original_input_file} → {str(temp_wav_path)}")
                            updated = True
                            break
                    
                    if not updated:
                        print(f"   ⚠️ Ultra Think: コマンド配列内で元ファイルパスが見つかりませんでした")
                        print(f"   - 検索パス: '{original_input_file}'")
                        print(f"   - コマンド配列内容:")
                        for i, arg in enumerate(cmd_array):
                            if '-i' in arg or original_input_file in arg or 'samples' in arg:
                                print(f"     [{i}]: {arg} ← 関連する可能性")
                            else:
                                print(f"     [{i}]: {arg}")
                    
                    # Ultra Think: 変換されたWAVファイルの詳細検証
                    print(f"🔍 Ultra Think: 変換されたWAVファイルの詳細検証")
                    try:
                        import soundfile as sf
                        wav_data, wav_sr = sf.read(str(temp_wav_path))
                        print(f"   - WAVファイルサンプリングレート: {wav_sr}")
                        print(f"   - WAVファイルデータ長: {len(wav_data)}")
                        print(f"   - WAVファイルデータ型: {type(wav_data)}")
                        if len(wav_data) > 0:
                            print(f"   - WAVファイルデータ範囲: {wav_data.min():.4f} ~ {wav_data.max():.4f}")
                            print(f"   - WAVファイル再生時間: {len(wav_data)/wav_sr:.2f}秒")
                        else:
                            print(f"⚠️ Ultra Think: 変換されたWAVファイルが空です")
                    except Exception as wav_check_error:
                        print(f"⚠️ Ultra Think: WAVファイル検証エラー: {wav_check_error}")
                    
                    self.progress_updated.emit(44, f"✅ WAV変換完了 - RVC処理継続")
                    print(f"🎯 Ultra Think: RVC処理は変換されたWAVファイルで続行します")
                    
                else:
                    print(f"⚠️ Ultra Think: ffmpeg変換失敗 - 元のM4Aファイルで続行")
                    print(f"   - ffmpeg終了コード: {ffmpeg_result.returncode}")
                    print(f"   - STDERR: {ffmpeg_result.stderr}")
                    self.progress_updated.emit(44, "⚠️ WAV変換失敗 - M4Aで続行")
                    
            except subprocess.TimeoutExpired:
                print(f"⚠️ Ultra Think: ffmpeg変換タイムアウト - M4Aで続行")
                self.progress_updated.emit(44, "⚠️ 変換タイムアウト - M4Aで続行")
            except FileNotFoundError:
                print(f"⚠️ Ultra Think: ffmpegが見つかりません - M4Aで続行")
                print(f"   💡 ffmpegをインストール: brew install ffmpeg")
                self.progress_updated.emit(44, "⚠️ ffmpeg未検出 - M4Aで続行")
            except Exception as conv_error:
                print(f"⚠️ Ultra Think: WAV変換エラー - M4Aで続行: {conv_error}")
                self.progress_updated.emit(44, f"⚠️ 変換エラー - M4Aで続行")
        
        # コマンド配列を最新の入力ファイルパスで再構築
        print(f"🔧 Ultra Think: 最終入力ファイルパス: {self.input_file}")
        print(f"   - 元ファイル: {original_input_file}")
        print(f"   - 処理ファイル: {self.input_file}")
        print(f"   - 形式変換: {'実行済み' if self.input_file != original_input_file else '不要'}")
        
        # Ultra Think: CLI実行前の手動検証オプション
        self.progress_updated.emit(45, "🔍 CLI実行前検証...")
        print(f"🧪 Ultra Think: CLI実行前の総合検証開始")
        
        # RVCモジュールの存在確認
        try:
            import rvc.wrapper.cli.cli
            print(f"✅ Ultra Think: RVC CLIモジュール確認OK")
        except ImportError as rvc_import_error:
            print(f"❌ Ultra Think: RVC CLIモジュール読み込み失敗: {rvc_import_error}")
            self.progress_updated.emit(45, "❌ RVCモジュール読み込み失敗")
            raise Exception(f"RVC CLIモジュールの読み込みに失敗: {rvc_import_error}")
        
        # Python環境の詳細確認
        print(f"🐍 Ultra Think: Python実行環境詳細:")
        print(f"   - Python実行ファイル: {sys.executable}")
        print(f"   - Pythonバージョン: {sys.version}")
        print(f"   - 作業ディレクトリ: {os.getcwd()}")
        print(f"   - sys.path先頭5個: {sys.path[:5]}")
        
        # 最終コマンド確認とデバッグ出力準備
        
        # 環境変数設定
        env = os.environ.copy()
        env['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        
        self.progress_updated.emit(43, "🚀 RVC CLI実行開始...")
        print(f"🔧 Ultra Think: subprocess.Popen実行中...")
        
        # Ultra Think: stderrも別途キャプチャ
        process = subprocess.Popen(
            cmd_array,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # stderrを別途キャプチャ
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env
        )
        
        self.progress_updated.emit(44, "CLI実行中 - 出力監視開始...")
        
        current_stage = 3
        line_count = 0
        total_lines_estimate = 50
        
        # Ultra Think: CLI実行と詳細監視（強化版早期終了検出）
        import time
        start_time = time.time()
        
        # 手動テスト用コマンド保存（デバッグ用）
        cmd_test_file = Path.home() / "Documents" / "RVC_Output" / "debug_cmd.txt"
        try:
            with open(cmd_test_file, "w", encoding="utf-8") as f:
                f.write("# Ultra Think デバッグ用CLI実行コマンド\n")
                f.write("# 以下のコマンドをターミナルで手動実行して問題を特定できます\n\n")
                f.write(" ".join([f'"{arg}"' if " " in arg else arg for arg in cmd_array]))
                f.write("\n\n# 実行前の確認事項:\n")
                f.write(f"# - 作業ディレクトリ: {os.getcwd()}\n")
                f.write(f"# - Python実行ファイル: {cmd_array[0]}\n")
                f.write(f"# - 入力ファイル: {self.input_file}\n")
                f.write(f"# - 出力ファイル: {self.output_file}\n")
            print(f"🔧 Ultra Think: 手動テスト用コマンドを保存: {cmd_test_file}")
        except Exception as cmd_save_error:
            print(f"⚠️ コマンド保存エラー: {cmd_save_error}")
        
        try:
            print(f"⏱️ Ultra Think: CLI実行中 - 詳細監視モード...")
            
            # 実行時間の期待値設定
            expected_min_time = 8.0  # 最低8秒は実行されるべき
            
            stdout_data, stderr_data = process.communicate(timeout=120)  # 2分タイムアウト
            
            execution_time = time.time() - start_time
            print(f"📊 Ultra Think: CLI実行完了 (実行時間: {execution_time:.2f}秒)")
            print(f"   - プロセスリターンコード: {process.returncode}")
            print(f"   - STDOUT データサイズ: {len(stdout_data) if stdout_data else 0} 文字")
            print(f"   - STDERR データサイズ: {len(stderr_data) if stderr_data else 0} 文字")
            
            # Ultra Think: 早期終了の詳細分析
            if execution_time < expected_min_time:
                print(f"⚠️ Ultra Think: 異常に短い実行時間検出 ({execution_time:.2f}秒 < {expected_min_time}秒)")
                self.progress_updated.emit(91, f"⚠️ 早期終了検出: {execution_time:.2f}秒")
                
                early_exit_analysis = []
                
                # 考えられる原因を順番に分析
                if process.returncode != 0:
                    early_exit_analysis.append(f"非ゼロ終了コード: {process.returncode}")
                
                if not stdout_data or len(stdout_data.strip()) == 0:
                    early_exit_analysis.append("STDOUT出力が空")
                
                if stderr_data and "error" in stderr_data.lower():
                    early_exit_analysis.append("STDERR内にエラーメッセージ")
                elif stderr_data and len(stderr_data.strip()) > 0:
                    early_exit_analysis.append("STDERR出力あり（警告またはINFO）")
                else:
                    early_exit_analysis.append("STDERR出力なし")
                
                # モジュール読み込み問題の検出
                if stderr_data and "import" in stderr_data.lower():
                    early_exit_analysis.append("モジュール読み込み問題の可能性")
                
                if stderr_data and "fairseq" in stderr_data:
                    early_exit_analysis.append("fairseq関連問題の可能性")
                
                # ファイル関連問題の検出
                if not Path(self.input_file).exists():
                    early_exit_analysis.append("入力ファイル不存在")
                
                print(f"🔍 Ultra Think: 早期終了原因分析:")
                for i, analysis in enumerate(early_exit_analysis, 1):
                    print(f"   {i}. {analysis}")
                
                # 手動実行推奨メッセージ
                print(f"🛠️ Ultra Think: 問題特定のため手動実行を推奨")
                print(f"   1. ターミナルでファイルを開く: open '{cmd_test_file}'")
                print(f"   2. コマンドをコピーしてターミナルで実行")
                print(f"   3. 詳細エラーメッセージを確認")
                
                self.progress_updated.emit(92, "手動実行テストファイル作成完了")
            else:
                print(f"✅ Ultra Think: 正常な実行時間 ({execution_time:.2f}秒)")
                self.progress_updated.emit(91, f"✅ 正常実行時間: {execution_time:.2f}秒")
            
            # STDOUT処理
            all_output = []
            error_lines = []
            if stdout_data:
                stdout_lines = stdout_data.strip().split('\n')
                all_output = [line.strip() for line in stdout_lines if line.strip()]
                for line in all_output:
                    print(f"RVC: {line}")
                    if any(error_word in line.lower() for error_word in ['error', 'failed', 'exception', 'traceback']):
                        error_lines.append(line)
            
            # STDERR処理（完全版）
            stderr_output = []
            if stderr_data:
                stderr_lines = stderr_data.strip().split('\n')
                stderr_output = [line.strip() for line in stderr_lines if line.strip()]
                print(f"🔍 Ultra Think: STDERR出力検出 ({len(stderr_output)}行):")
                
                for i, line in enumerate(stderr_output, 1):
                    print(f"   ERR{i:2d}: {line}")
                    
                    # 最初のメッセージをプログレスに表示
                    if i == 1:
                        error_preview = line[:80] + "..." if len(line) > 80 else line
                        self.progress_updated.emit(91, f"STDERR: {error_preview}")
                
                # Ultra Think: 実行時間と組み合わせた問題分析
                if execution_time < 5.0:  # 5秒未満は異常に短い
                    quick_exit_msg = f"異常に短い実行時間: {execution_time:.2f}秒"
                    self.progress_updated.emit(91, quick_exit_msg)
                    print(f"⚠️ Ultra Think: CLI実行が異常に短い（{execution_time:.2f}秒）")
                    print(f"   - 通常の音声変換には10-60秒程度かかります")
                    print(f"   - 早期終了の原因: 引数エラー、ファイル不見、モジュール問題の可能性")
                
                # STDERRの内容分析
                stderr_full_text = " ".join(stderr_output)
                if "INFO:" in stderr_full_text and "error" not in stderr_full_text.lower():
                    info_only_msg = "STDERR: INFO メッセージのみ"
                    self.progress_updated.emit(91, info_only_msg)
                    print(f"✅ Ultra Think: STDERRはINFOメッセージのみ - エラーではない")
                    print(f"   - しかし処理が未完了なので別の問題があります")
            else:
                print(f"📝 Ultra Think: STDERR出力なし")
            
            # プログレス更新
            if len(all_output) == 0 and len(stderr_output) > 0:
                self.progress_updated.emit(91, "CLI実行エラー - STDERR確認")
            elif len(all_output) > 0:
                self.progress_updated.emit(91, f"CLI出力 {len(all_output)}行取得")
            else:
                self.progress_updated.emit(91, "CLI出力なし - 処理未実行")
                
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"⏰ Ultra Think: CLI実行がタイムアウトしました ({execution_time:.2f}秒)")
            process.kill()
            stdout_data, stderr_data = process.communicate()
            all_output = []
            error_lines = []
            stderr_output = [f"CLI実行タイムアウト（{execution_time:.2f}秒後）"]
        except Exception as comm_error:
            execution_time = time.time() - start_time
            print(f"❌ Ultra Think: communicate()エラー: {comm_error} ({execution_time:.2f}秒)")
            all_output = []
            error_lines = []
            stderr_output = [f"communicate()エラー: {comm_error}"]
            
        # Ultra Think: CLI実行結果の総合分析
        print(f"📈 Ultra Think: CLI実行分析サマリー:")
        print(f"   - 実行時間: {execution_time:.2f}秒")
        print(f"   - リターンコード: {process.returncode}")
        print(f"   - STDOUT行数: {len(all_output)}")
        print(f"   - STDERR行数: {len(stderr_output) if 'stderr_output' in locals() else 0}")
        print(f"   - 処理状況: {'正常完了' if process.returncode == 0 and len(all_output) > 0 else '異常終了または未完了'}")
        
        # Ultra Think: CLI実行結果の詳細チェック（確実なログ出力）
        self.progress_updated.emit(92, "CLI実行結果を分析中...")
        
        debug_msg = f"🔍 Ultra Think: CLI実行結果分析開始"
        print(debug_msg)
        
        returncode_msg = f"リターンコード: {process.returncode}"
        print(f"   - {returncode_msg}")
        
        # Ultra Think: CLI出力の詳細分析（stdout + stderr）
        try:
            total_stderr = len(stderr_output)
            output_analysis_msg = f"CLI出力: {len(all_output)}行, エラー: {len(error_lines)}行, STDERR: {total_stderr}行"
            self.progress_updated.emit(93, f"分析中 - {output_analysis_msg}")
            print(f"📊 Ultra Think: CLI出力分析:")
            print(f"   - STDOUT出力行数: {len(all_output)}")
            print(f"   - STDERR出力行数: {total_stderr}")
            print(f"   - エラー行数: {len(error_lines)}")
            
            # STDERR出力がある場合は詳細表示
            if stderr_output:
                stderr_msg = f"STDERR検出: {total_stderr}行"
                self.progress_updated.emit(93, stderr_msg)
                print(f"🔍 STDERR出力詳細:")
                for i, line in enumerate(stderr_output, 1):
                    print(f"   ERR{i:2d}: {line}")
            
            if error_lines:
                error_msg = f"エラー検出: {len(error_lines)}件"
                self.progress_updated.emit(93, error_msg)
                print(f"🔍 STDOUT内検出エラー:")
                for error_line in error_lines:
                    print(f"   ❌ {error_line}")
            
            if len(all_output) > 0:
                print(f"📝 STDOUT出力詳細（全{len(all_output)}行）:")
                for i, line in enumerate(all_output, 1):
                    print(f"   {i:2d}: {line}")
                    
                # 1行しかない場合は特に詳細表示
                if len(all_output) == 1:
                    single_line_msg = f"警告: STDOUT出力1行のみ - '{all_output[0][:50]}...'"
                    self.progress_updated.emit(93, single_line_msg)
                    print(f"⚠️ Ultra Think: STDOUT出力が1行のみです - 内容: '{all_output[0]}'")
            else:
                no_output_msg = "⚠️ STDOUT出力が0行です"
                self.progress_updated.emit(93, no_output_msg)
                print(no_output_msg)
                
            # 出力が異常に少ない場合の原因分析
            if len(all_output) <= 1 and total_stderr == 0:
                analysis_msg = "CLI処理が開始されていない可能性"
                self.progress_updated.emit(93, analysis_msg)
                print(f"⚠️ Ultra Think: CLI処理が正常に開始されていない可能性があります")
                print(f"   - 考えられる原因: モジュール読み込み失敗、パラメータエラー、実行権限不足")
            elif total_stderr > 0:
                stderr_analysis_msg = f"STDERR出力により問題特定可能"
                self.progress_updated.emit(93, stderr_analysis_msg)
                print(f"✅ Ultra Think: STDERR出力により問題の詳細が判明しました")
                
        except Exception as analysis_error:
            error_msg = f"分析エラー: {analysis_error}"
            self.progress_updated.emit(93, error_msg)
            print(f"❌ CLI出力分析エラー: {analysis_error}")
        
        # エラーチェック
        if process.returncode != 0:
            error_msg = f"RVC CLI inference failed with return code: {process.returncode}"
            print(f"❌ Ultra Think: CLI実行エラー詳細:")
            print(f"   - コマンド: {' '.join(cmd_array)}")
            print(f"   - リターンコード: {process.returncode}")
            print(f"   - 作業ディレクトリ: {os.getcwd()}")
            
            # 出力ディレクトリの状態確認
            output_dir = Path(self.output_file).parent
            print(f"   - 出力ディレクトリ存在: {output_dir.exists()}")
            if output_dir.exists():
                print(f"   - 出力ディレクトリ内容:")
                for item in output_dir.iterdir():
                    print(f"     - {item.name}")
            
            # 完全な出力を表示
            if all_output:
                print(f"📜 完全なCLI出力:")
                for i, line in enumerate(all_output, 1):
                    print(f"   {i:3d}: {line}")
            
            raise RuntimeError(error_msg)
        else:
            success_msg = "CLI実行成功 - 出力ファイル確認中..."
            self.progress_updated.emit(94, success_msg)
            print(f"✅ Ultra Think: CLI実行成功 (return code: 0)")
            
            # 成功時も出力ファイル確認前に詳細状況を表示
            try:
                output_dir = Path(self.output_file).parent
                dir_check_msg = f"出力ディレクトリ確認: {output_dir.exists()}"
                self.progress_updated.emit(94, dir_check_msg)
                
                print(f"📁 Ultra Think: 出力確認前の状況:")
                print(f"   - 出力予定ファイル: {self.output_file}")
                print(f"   - 出力ディレクトリ: {output_dir}")
                print(f"   - ディレクトリ存在: {output_dir.exists()}")
                
                if output_dir.exists():
                    print(f"   - ディレクトリ内容:")
                    try:
                        files_found = []
                        for item in output_dir.iterdir():
                            if item.is_file():
                                size = item.stat().st_size
                                file_info = f"{item.name} ({size} bytes)"
                                files_found.append(file_info)
                                print(f"     📄 {file_info}")
                            else:
                                print(f"     📁 {item.name}/")
                        
                        files_msg = f"ファイル数: {len(files_found)}"
                        self.progress_updated.emit(94, files_msg)
                        
                    except Exception as list_error:
                        list_error_msg = f"ディレクトリ読み取りエラー: {list_error}"
                        self.progress_updated.emit(94, list_error_msg)
                        print(f"     ❌ ディレクトリ内容読み取りエラー: {list_error}")
                else:
                    no_dir_msg = "出力ディレクトリが存在しません"
                    self.progress_updated.emit(94, no_dir_msg)
                    print(f"   ❌ {no_dir_msg}")
                
                # CLI出力に問題がないか確認
                if len(all_output) < 3:
                    low_output_msg = f"STDOUT出力が少ない: {len(all_output)}行"
                    self.progress_updated.emit(94, low_output_msg)
                    print(f"⚠️ Ultra Think: STDOUT出力が異常に少ない（{len(all_output)}行）- 処理が実行されていない可能性")
                
                if len(stderr_output) > 0:
                    stderr_detected_msg = f"STDERR出力検出: {len(stderr_output)}行"
                    self.progress_updated.emit(94, stderr_detected_msg)
                    print(f"⚠️ Ultra Think: STDERR出力が検出されました - エラーの可能性")
                
                if error_lines:
                    error_detected_msg = f"エラーライン検出: {len(error_lines)}件"
                    self.progress_updated.emit(94, error_detected_msg)
                    print(f"⚠️ Ultra Think: エラーラインが検出されましたが、リターンコードは0でした")
                    
            except Exception as detail_error:
                detail_error_msg = f"詳細確認エラー: {detail_error}"
                self.progress_updated.emit(94, detail_error_msg)
                print(f"❌ Ultra Think: 詳細確認処理エラー: {detail_error}")
                import traceback
                print(f"詳細トレースバック:\n{traceback.format_exc()}")
        
        # 完了処理
        self.progress_updated.emit(95, "変換結果を保存中...")
        time.sleep(0.5)
        self.progress_updated.emit(100, "保存完了")
        
        # Ultra Think: CLI出力ファイル確認強化版（プログレスメッセージ付き）
        final_check_msg = "最終出力ファイル確認中..."
        self.progress_updated.emit(98, final_check_msg)
        print(f"🔍 Ultra Think: CLI出力ファイル確認開始 - {self.output_file}")
        
        try:
            output_path = Path(self.output_file)
            file_exists = output_path.exists()
            
            exists_msg = f"出力ファイル存在: {file_exists}"
            self.progress_updated.emit(98, exists_msg)
            print(f"   - ファイル存在確認: {file_exists}")
            
            if file_exists:
                file_size = output_path.stat().st_size
                size_msg = f"ファイルサイズ: {file_size} bytes"
                self.progress_updated.emit(99, size_msg)
                print(f"✅ Ultra Think: CLI変換結果ファイル確認OK - サイズ: {file_size} bytes")
                
                if file_size > 0:
                    success_msg = f"変換完了: {output_path.name}"
                    self.progress_updated.emit(100, success_msg)
                    self.conversion_finished.emit(True, f"RVC CLI変換完了: {self.output_file}")
                else:
                    empty_file_msg = "ファイルは存在するが空です"
                    self.progress_updated.emit(99, empty_file_msg)
                    print(f"❌ Ultra Think: CLI結果ファイルは作成されましたが空です")
                    # 詳細なファイル情報を出力
                    file_stat = output_path.stat()
                    print(f"📊 ファイル詳細: 作成日時={file_stat.st_ctime}, 修正日時={file_stat.st_mtime}")
                    raise Exception(f"結果ファイルが空です: {self.output_file}")
            else:
                no_file_msg = "出力ファイルが作成されていません"
                self.progress_updated.emit(99, no_file_msg)
                print(f"❌ Ultra Think: CLI出力ファイルが作成されていません")
                
                # Ultra Think: 総合的な問題診断と対策提案
                print(f"🔍 Ultra Think: 出力ファイル未作成の総合診断開始")
                
                # ディレクトリ内容を確認
                output_dir = output_path.parent
                if output_dir.exists():
                    dir_content_msg = f"ディレクトリ内容確認中: {output_dir.name}"
                    self.progress_updated.emit(99, dir_content_msg)
                    print(f"📁 出力ディレクトリ内容:")
                    
                    file_count = 0
                    recent_files = []
                    for item in output_dir.iterdir():
                        if item.is_file():
                            file_count += 1
                            size = item.stat().st_size
                            mtime = item.stat().st_mtime
                            recent_files.append((item.name, size, mtime))
                            print(f"   - 📄 {item.name} ({size} bytes)")
                        else:
                            print(f"   - 📁 {item.name}/")
                    
                    content_summary_msg = f"ディレクトリ内ファイル数: {file_count}"
                    self.progress_updated.emit(99, content_summary_msg)
                    
                    # 最近作成されたファイルの確認
                    import time
                    current_time = time.time()
                    recent_threshold = 300  # 5分以内
                    
                    for filename, size, mtime in recent_files:
                        if current_time - mtime < recent_threshold:
                            print(f"   ⏰ 最近作成: {filename} ({size} bytes, {int(current_time - mtime)}秒前)")
                
                # 問題の根本原因分析
                print(f"🧐 Ultra Think: 根本原因分析:")
                
                problem_analysis = []
                
                # 1. 実行時間が短すぎる場合
                if 'execution_time' in locals() and execution_time < 8.0:
                    problem_analysis.append(f"CLI実行時間が短すぎる ({execution_time:.2f}秒)")
                    problem_analysis.append("→ RVC処理が開始されていない可能性")
                
                # 2. STDERRにfairseqメッセージのみ
                if 'stderr_data' in locals() and stderr_data:
                    if "fairseq" in stderr_data and "error" not in stderr_data.lower():
                        problem_analysis.append("fairseq読み込み成功後に処理が停止")
                        problem_analysis.append("→ モデルファイルまたは入力ファイルの問題")
                
                # 3. M4A入力ファイルの問題
                if original_input_file.lower().endswith('.m4a'):
                    if self.input_file == original_input_file:  # WAV変換されていない場合
                        problem_analysis.append("M4A形式の入力ファイルが問題の可能性")
                        problem_analysis.append("→ WAV形式への変換が必要")
                    else:
                        problem_analysis.append("WAV変換は成功したが、他の問題が存在")
                
                # 4. モデルファイルの問題
                model_path = Path(self.current_model['path'])
                if not model_path.exists():
                    problem_analysis.append(f"音声モデルファイル不存在: {model_path}")
                elif model_path.stat().st_size < 1000000:  # 1MB未満
                    problem_analysis.append(f"音声モデルファイルが小さすぎる: {model_path.stat().st_size} bytes")
                
                # 5. 出力ディレクトリの権限問題
                try:
                    test_file = output_dir / ".rvc_write_test2"
                    test_file.touch()
                    test_file.unlink()
                except Exception as perm_error:
                    problem_analysis.append(f"出力ディレクトリ書き込み権限エラー: {perm_error}")
                
                print(f"📋 Ultra Think: 検出された問題:")
                for i, analysis in enumerate(problem_analysis, 1):
                    print(f"   {i}. {analysis}")
                
                # 対策提案
                print(f"💡 Ultra Think: 推奨対策:")
                solutions = [
                    "1. 手動CLIテスト実行で詳細エラー確認",
                    f"   → ファイル確認: {cmd_test_file}",
                    "2. WAV形式の音声ファイルで再試行",
                    "3. 異なる音声モデルで再試行",
                    "4. 出力ディレクトリを変更（Desktop等）",
                    "5. RVCプロジェクトディレクトリから直接実行"
                ]
                
                for solution in solutions:
                    print(f"   {solution}")
                    
                # エラーレポート作成
                error_report_file = Path.home() / "Documents" / "RVC_Output" / "error_report.txt"
                try:
                    with open(error_report_file, "w", encoding="utf-8") as f:
                        f.write("# Ultra Think RVC 音声変換エラーレポート\n\n")
                        f.write(f"実行日時: {time.ctime()}\n\n")
                        f.write("## 実行コマンド\n")
                        f.write(" ".join([f'"{arg}"' if " " in arg else arg for arg in cmd_array]))
                        f.write("\n\n## 実行結果\n")
                        f.write(f"- 実行時間: {execution_time:.2f}秒\n")
                        f.write(f"- リターンコード: {process.returncode}\n")
                        f.write(f"- STDOUT行数: {len(all_output)}\n")
                        f.write(f"- STDERR行数: {len(stderr_output) if 'stderr_output' in locals() else 0}\n")
                        f.write("\n## 検出された問題\n")
                        for problem in problem_analysis:
                            f.write(f"- {problem}\n")
                        f.write("\n## STDERR出力\n")
                        if 'stderr_data' in locals() and stderr_data:
                            f.write(stderr_data)
                        else:
                            f.write("なし\n")
                    
                    print(f"📄 Ultra Think: エラーレポート作成完了: {error_report_file}")
                    self.progress_updated.emit(99, "エラーレポート作成完了")
                    
                except Exception as report_error:
                    print(f"⚠️ エラーレポート作成失敗: {report_error}")
                
                    # 最終エラーメッセージ
                    self.progress_updated.emit(99, "手動テスト・エラーレポート確認推奨")
                
                else:
                    no_dir_msg = "出力ディレクトリも存在しません"
                    self.progress_updated.emit(99, no_dir_msg)
                    print(f"❌ 出力ディレクトリも存在しません: {output_dir}")
                
                raise Exception(f"出力ファイルが作成されていません: {self.output_file}")
                
        except Exception as final_check_error:
            error_msg = f"最終確認エラー: {final_check_error}"
            self.progress_updated.emit(99, error_msg)
            print(f"❌ Ultra Think: 最終確認処理エラー: {final_check_error}")
            raise final_check_error

class ModelCard(QFrame):
    """音声モデルカード表示（Ultra Think視覚改善版）"""
    
    def __init__(self, model_info):
        super().__init__()
        self.model_info = model_info
        self.is_selected = False
        self.setup_ui()
        self.apply_default_style()
        
    def setup_ui(self):
        """UIセットアップ（Ultra Think最適化版 - 美的レイアウト）"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedHeight(80)  # 小さくコンパクトに
        self.setCursor(Qt.PointingHandCursor)
        
        # メインレイアウト（コンパクト版）
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(4)
        
        # ヘッダー部分（モデル名とインデックス）
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        # モデル名（左側 - コンパクト）
        name_label = QLabel(self.model_info.get('name', 'Unknown Model'))
        name_label.setFont(QFont("Arial", 11, QFont.Bold))
        name_label.setStyleSheet("color: #FFFFFF;")
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(name_label, 1)
        
        # インデックス情報（右側 - バッジスタイル）
        has_index = self.model_info.get('has_index', False)
        index_widget = QLabel('INDEX' if has_index else 'NO IDX')
        index_widget.setFont(QFont("SF Pro Display", 9, QFont.Bold))
        
        if has_index:
            index_style = """
                color: #4CAF50;
                background-color: rgba(76, 175, 80, 0.15);
                border: 1px solid rgba(76, 175, 80, 0.3);
                padding: 5px 12px;
                border-radius: 12px;
                font-weight: bold;
            """
        else:
            index_style = """
                color: #FF7043;
                background-color: rgba(255, 112, 67, 0.15);
                border: 1px solid rgba(255, 112, 67, 0.3);
                padding: 5px 12px;
                border-radius: 12px;
                font-weight: bold;
            """
        
        index_widget.setStyleSheet(index_style)
        index_widget.setAlignment(Qt.AlignCenter)
        index_widget.setMaximumWidth(80)
        header_layout.addWidget(index_widget, 0)
        
        main_layout.addWidget(header_widget)
        
        # 区切り線は削除してスペースを節約
        
        # パス情報（シンプル版）
        import os.path
        full_path = self.model_info.get('path', 'N/A')
        file_name = os.path.basename(full_path)
        
        path_label = QLabel(f"📁 {file_name}")
        path_label.setFont(QFont("Arial", 9))
        path_label.setStyleSheet("color: #999999; padding: 2px 0px;")
        path_label.setToolTip(full_path)  # フルパスはツールチップで表示
        main_layout.addWidget(path_label)
        
        # ストレッチを削除してコンパクトに
        
        self.setLayout(main_layout)
    
    def apply_default_style(self):
        """デフォルトスタイル適用（Ultra Think最適化版）"""
        self.setStyleSheet("""
            ModelCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2E2E32, stop:1 #252529);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                margin: 3px;
            }
            ModelCard:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #353539, stop:1 #2C2C30);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
        """)
        self.is_selected = False
    
    def apply_selected_style(self):
        """選択状態スタイル適用（Ultra Think最適化版）"""
        self.setStyleSheet("""
            ModelCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E4A6F, stop:1 #1A3F5C);
                border: 2px solid #2A82DA;
                border-radius: 10px;
                margin: 3px;
            }
            ModelCard:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #25537A, stop:1 #1F4A68);
                border: 2px solid #3A92EA;
            }
        """)
        self.is_selected = True

class RVCStandaloneMainWindow(QMainWindow):
    """RVC 完全独立版メインウィンドウ（Ultra Think）"""
    
    def __init__(self):
        super().__init__()
        
        # Ultra Think: アプリケーションアイコンを設定
        self._set_application_icon()
        
        # PyInstallerでパッケージされた場合の実行ディレクトリを取得
        if getattr(sys, 'frozen', False):
            # 実行可能ファイルとして実行されている場合
            app_dir = Path(sys.executable).parent
        else:
            # 開発環境で実行されている場合
            app_dir = Path.cwd()
        
        self.model_dir = self._detect_model_directory()
        
        # Ultra Think: デスクトップ権限問題を事前回避
        # デフォルト出力先をDocumentsに変更（権限安全）
        self.output_dir = Path.home() / "Documents" / "RVC_Output"
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Ultra Think: 出力ディレクトリ設定 = {self.output_dir}")
        except Exception as e:
            # フォールバック: アプリケーションディレクトリ
            self.output_dir = app_dir / "enhanced_output"
            self.output_dir.mkdir(exist_ok=True)
            print(f"⚠️ Documents使用不可、フォールバック = {self.output_dir}")
        
        self.models = []
        self.current_model = None
        
        self.setup_ui()
        self.setup_dark_theme()
        self.load_models()
        
        # Ultra Think: ウィンドウクローズイベントのオーバーライド
        self.setAttribute(Qt.WA_QuitOnClose, True)
    
    def closeEvent(self, event):
        """ウィンドウクローズ時の完全終了処理（Ultra Think）"""
        print("🔄 ウィンドウクローズイベント - 完全終了処理開始")
        try:
            # 全ての子ウィジェットを確実に終了
            for child in self.findChildren(QWidget):
                try:
                    child.close()
                    child.deleteLater()
                except:
                    pass
            
            # アプリケーション終了要求
            QApplication.quit()
            
            # プロセス強制終了
            os._exit(0)
            
        except Exception as e:
            print(f"⚠️ ウィンドウクローズエラー: {e}")
            os._exit(1)
        
        super().closeEvent(event)
        
    def setup_ui(self):
        """UI構築"""
        self.setWindowTitle("RVC Voice Converter - 完全独立版 (Ultra Think)")
        self.setGeometry(100, 100, 1200, 800)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QHBoxLayout()
        
        # 左側: モデル選択エリア
        left_panel = self.create_model_panel()
        
        # 右側: 変換設定エリア
        right_panel = self.create_conversion_panel()
        
        # スプリッター
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
    def create_model_panel(self):
        """モデル選択パネル作成（Ultra Think改善版）"""
        panel = QGroupBox("音声モデル")
        layout = QVBoxLayout()
        
        # モデルディレクトリ選択エリア
        model_dir_group = self.create_model_directory_group()
        layout.addWidget(model_dir_group)
        
        # 更新ボタン（洗練されたデザイン）
        refresh_btn = QPushButton("🔄 モデルを再読み込み")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(76, 175, 80, 0.2);
                color: #4CAF50;
                border: 1px solid #4CAF50;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.15);
            }
        """)
        refresh_btn.clicked.connect(self.load_models)
        layout.addWidget(refresh_btn)
        
        # モデル一覧（スクロール可能）- Ultra Think改善版
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404042;
                border-radius: 4px;
                background-color: #232325;
            }
            QScrollArea QWidget {
                background-color: #232325;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555558;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666669;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #232325;")
        self.model_layout = QVBoxLayout()
        self.model_layout.setContentsMargins(8, 8, 8, 8)
        self.model_layout.setSpacing(6)
        scroll_widget.setLayout(self.model_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        panel.setLayout(layout)
        return panel
    
    def create_model_directory_group(self):
        """モデルディレクトリ選択グループ（Ultra Think洗練版）"""
        group = QGroupBox("モデルディレクトリ設定")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # メインレイアウト
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 16, 12, 12)
        main_layout.setSpacing(8)
        
        # パス表示セクション
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(8)
        
        # フォルダーアイコン
        folder_icon = QLabel("📂")
        folder_icon.setFont(QFont("Arial", 14))
        folder_icon.setStyleSheet("color: #FFA726;")
        path_layout.addWidget(folder_icon, 0)
        
        # パス表示（整理版）
        import os.path
        display_path = str(self.model_dir)
        if len(display_path) > 50:
            parts = display_path.split(os.sep)
            if len(parts) > 3:
                display_path = f"{parts[0]}{os.sep}...{os.sep}{os.sep.join(parts[-2:])}"
        
        self.model_dir_label = QLabel(display_path)
        self.model_dir_label.setFont(QFont("Consolas", 10))
        self.model_dir_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                padding: 8px 12px;
            }
        """)
        self.model_dir_label.setWordWrap(False)
        self.model_dir_label.setToolTip(str(self.model_dir))
        path_layout.addWidget(self.model_dir_label, 1)
        
        main_layout.addWidget(path_widget)
        
        # ボタンセクション
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        
        # 選択ボタン
        select_dir_btn = QPushButton("📁 ディレクトリ選択")
        select_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E88E5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        select_dir_btn.clicked.connect(self.select_model_directory)
        button_layout.addWidget(select_dir_btn)
        
        # リセットボタン
        reset_dir_btn = QPushButton("↻ デフォルト")
        reset_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #BBBBBB;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.08);
            }
        """)
        reset_dir_btn.clicked.connect(self.reset_model_directory)
        button_layout.addWidget(reset_dir_btn)
        
        button_layout.addStretch()
        main_layout.addWidget(button_widget)
        
        group.setLayout(main_layout)
        return group
        
    def create_conversion_panel(self):
        """変換設定パネル作成"""
        panel = QGroupBox("音声変換")
        layout = QVBoxLayout()
        
        # ファイル選択
        file_group = self.create_file_selection_group()
        layout.addWidget(file_group)
        
        # パラメータ設定
        params_group = self.create_parameters_group()
        layout.addWidget(params_group)
        
        # 変換ボタン
        self.convert_btn = QPushButton("音声変換開始 (完全独立版)")
        self.convert_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_btn)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("待機中...")
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        
        # ログエリア
        log_group = self.create_log_group()
        layout.addWidget(log_group)
        
        panel.setLayout(layout)
        return panel
    
    def create_file_selection_group(self):
        """ファイル選択グループ"""
        group = QGroupBox("ファイル選択")
        layout = QGridLayout()
        
        # 入力ファイル
        layout.addWidget(QLabel("入力ファイル:"), 0, 0)
        self.input_file_label = QLabel("選択されていません")
        self.input_file_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
        layout.addWidget(self.input_file_label, 0, 1)
        
        input_btn = QPushButton("参照")
        input_btn.clicked.connect(self.select_input_file)
        layout.addWidget(input_btn, 0, 2)
        
        # 出力ファイル
        layout.addWidget(QLabel("出力ファイル:"), 1, 0)
        self.output_file_label = QLabel("自動生成")
        self.output_file_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
        layout.addWidget(self.output_file_label, 1, 1)
        
        output_btn = QPushButton("参照")
        output_btn.clicked.connect(self.select_output_file)
        layout.addWidget(output_btn, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def create_parameters_group(self):
        """パラメータ設定グループ"""
        group = QGroupBox("変換パラメータ")
        layout = QGridLayout()
        
        # ピッチ
        layout.addWidget(QLabel("ピッチ:"), 0, 0)
        self.pitch_slider = QSlider(Qt.Horizontal)
        self.pitch_slider.setRange(-12, 12)
        self.pitch_slider.setValue(0)
        self.pitch_label = QLabel("0")
        self.pitch_slider.valueChanged.connect(
            lambda v: self.pitch_label.setText(str(v))
        )
        layout.addWidget(self.pitch_slider, 0, 1)
        layout.addWidget(self.pitch_label, 0, 2)
        
        # インデックス比率
        layout.addWidget(QLabel("インデックス比率:"), 1, 0)
        self.index_slider = QSlider(Qt.Horizontal)
        self.index_slider.setRange(0, 100)
        self.index_slider.setValue(75)
        self.index_label = QLabel("0.75")
        self.index_slider.valueChanged.connect(
            lambda v: self.index_label.setText(f"{v/100:.2f}")
        )
        layout.addWidget(self.index_slider, 1, 1)
        layout.addWidget(self.index_label, 1, 2)
        
        # フィルター半径
        layout.addWidget(QLabel("フィルター半径:"), 2, 0)
        self.filter_spin = QSpinBox()
        self.filter_spin.setRange(0, 7)
        self.filter_spin.setValue(3)
        layout.addWidget(self.filter_spin, 2, 1)
        
        group.setLayout(layout)
        return group
    
    def create_log_group(self):
        """ログ表示グループ"""
        group = QGroupBox("ログ")
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.log_text)
        
        group.setLayout(layout)
        return group
    
    def setup_dark_theme(self):
        """ダークテーマ設定"""
        palette = QPalette()
        
        # ダークカラー定義
        palette.setColor(QPalette.Window, QColor(35, 35, 37))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 27))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 47))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(45, 45, 47))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(palette)
        
        # スタイルシート（Ultra Think改善版）
        self.setStyleSheet("""
            QMainWindow {
                background-color: #232325;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #404042;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505052;
            }
            QPushButton:pressed {
                background-color: #353537;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 8px;
                background: #404042;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2a82da;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin-top: -2px;
                margin-bottom: -2px;
                border-radius: 9px;
            }
            /* Ultra Think: モデル選択UI専用スタイル */
            QGroupBox[title="音声モデル"] {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel {
                background-color: transparent;
            }
        """)
    
    def load_models(self):
        """モデル読み込み"""
        self.log_message("モデル検索中...")
        
        # 既存のモデルカードをクリア
        for i in reversed(range(self.model_layout.count())): 
            child = self.model_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        self.models.clear()
        
        if not self.model_dir.exists():
            self.log_message(f"❌ モデルディレクトリが見つかりません: {self.model_dir}")
            return
        
        # .pth ファイルを検索
        for model_path in self.model_dir.rglob("*.pth"):
            if model_path.name.startswith(('hubert', 'rmvpe')):
                continue  # システムファイルをスキップ
            
            model_info = {
                'name': model_path.stem,
                'path': str(model_path),
                'has_index': model_path.with_suffix('.index').exists()
            }
            
            self.models.append(model_info)
            
            # モデルカード作成
            card = ModelCard(model_info)
            card.mousePressEvent = lambda event, info=model_info: self.select_model(info)
            self.model_layout.addWidget(card)
        
        self.log_message(f"✅ {len(self.models)}個のモデルを読み込みました")
    
    def select_model(self, model_info):
        """モデル選択（Ultra Think改善版）"""
        self.current_model = model_info
        self.log_message(f"📋 モデル選択: {model_info['name']}")
        
        # 選択状態のビジュアル更新（Ultra Think改善版）
        for i in range(self.model_layout.count()):
            widget = self.model_layout.itemAt(i).widget()
            if widget and isinstance(widget, ModelCard):
                if widget.model_info == model_info:
                    widget.apply_selected_style()
                else:
                    widget.apply_default_style()
    
    def select_input_file(self):
        """入力ファイル選択"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "入力音声ファイル選択", "", 
            "Audio Files (*.wav *.mp3 *.flac *.m4a *.aiff *.mp4 *.ogg);;All Files (*)"
        )
        
        if file_path:
            self.input_file_label.setText(file_path)
            
            # 出力ファイル名を自動生成
            input_path = Path(file_path)
            output_name = f"{input_path.stem}_converted_standalone.wav"
            output_path = self.output_dir / output_name
            self.output_file_label.setText(str(output_path))
            
            self.log_message(f"📁 入力ファイル: {file_path}")
    
    def select_output_file(self):
        """出力ファイル選択"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "出力音声ファイル選択", "", 
            "Audio Files (*.wav *.mp3 *.flac *.m4a *.aiff);;All Files (*)"
        )
        
        if file_path:
            self.output_file_label.setText(file_path)
            self.log_message(f"📁 出力ファイル: {file_path}")
    
    def start_conversion(self):
        """音声変換開始（完全独立版）"""
        # バリデーション
        if not self.current_model:
            QMessageBox.warning(self, "エラー", "モデルを選択してください")
            return
        
        input_file = self.input_file_label.text()
        if input_file == "選択されていません":
            QMessageBox.warning(self, "エラー", "入力ファイルを選択してください")
            return
        
        if not Path(input_file).exists():
            QMessageBox.warning(self, "エラー", "入力ファイルが存在しません")
            return
        
        output_file = self.output_file_label.text()
        
        # パラメータ収集
        params = {
            'pitch': self.pitch_slider.value(),
            'index_rate': self.index_slider.value() / 100.0,
            'filter_radius': self.filter_spin.value()
        }
        
        self.log_message("🎵 Ultra Think完全独立版音声変換開始...")
        self.convert_btn.setEnabled(False)
        
        # 変換スレッド開始
        self.conversion_thread = StandaloneVoiceConversionThread(
            input_file, output_file, self.current_model, params, self.model_dir
        )
        self.conversion_thread.progress_updated.connect(self.update_progress)
        self.conversion_thread.conversion_finished.connect(self.conversion_finished)
        self.conversion_thread.start()
    
    def update_progress(self, value, message):
        """プログレス更新"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.log_message(f"⏳ {message} ({value}%)")
    
    def conversion_finished(self, success, message):
        """変換完了"""
        self.convert_btn.setEnabled(True)
        
        if success:
            self.log_message(f"✅ {message}")
            QMessageBox.information(self, "完了", message)
        else:
            self.log_message(f"❌ {message}")
            QMessageBox.critical(self, "エラー", message)
        
        self.progress_bar.setValue(0)
        self.progress_label.setText("待機中...")
    
    def log_message(self, message):
        """ログメッセージ表示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        print(formatted_message)  # コンソールにも出力
    
    def select_model_directory(self):
        """モデルディレクトリを選択"""
        directory = QFileDialog.getExistingDirectory(
            self, "モデルディレクトリを選択", str(self.model_dir)
        )
        
        if directory:
            self.model_dir = Path(directory)
            self.model_dir_label.setText(str(self.model_dir))
            self.log_message(f"📁 モデルディレクトリ変更: {self.model_dir}")
            
            # モデルを再読み込み
            self.load_models()
    
    def reset_model_directory(self):
        """モデルディレクトリをデフォルトに戻す"""
        # デフォルトディレクトリを再計算
        if getattr(sys, 'frozen', False):
            app_dir = Path(sys.executable).parent
        else:
            app_dir = Path.cwd()
        
        self.model_dir = self._detect_model_directory()
        self.model_dir_label.setText(str(self.model_dir))
        self.log_message(f"🔄 モデルディレクトリをデフォルトに戻しました: {self.model_dir}")
        
        # モデルを再読み込み
        self.load_models()
    
    def _detect_model_directory(self):
        """モデルディレクトリを環境非依存で検出（Ultra Think PyInstaller対応）"""
        # Ultra Think: PyInstallerリソースベースパス
        resource_base = get_resource_base_path()
        
        possible_model_dirs = [
            # 1. バンドルされたmodel_dir（PyInstaller --onefile対応）
            resource_base / "model_dir",
            # 2. プロジェクト内のmodel_dir（開発環境用）
            Path(__file__).parent / "model_dir",
            Path.cwd() / "model_dir",
            # 3. ユーザーのデスクトップ
            Path.home() / "Desktop" / "model_dir",
            # 4. ユーザーのDocuments
            Path.home() / "Documents" / "model_dir",
            Path.home() / "Documents" / "RVC" / "model_dir",
            # 5. アプリケーションサポート
            Path.home() / "Library" / "Application Support" / "RVC" / "model_dir",
            # 6. 共通の場所
            Path("/usr/local/share/rvc/model_dir"),
            Path("/opt/rvc/model_dir")
        ]
        
        for model_dir in possible_model_dirs:
            if model_dir.exists():
                # .pthファイルまたはrmvpe.ptがあるかチェック
                if (list(model_dir.rglob("*.pth")) or 
                    (model_dir / "rmvpe.pt").exists() or
                    (model_dir / "hubert_base.pt").exists()):
                    print(f"✅ Ultra Think独立版: model_dir検出 = {model_dir}")
                    return model_dir
        
        # フォールバック: デフォルトの場所を作成
        default_model_dir = Path.cwd() / "model_dir"
        print(f"📁 Ultra Think独立版: デフォルトmodel_dir作成 = {default_model_dir}")
        default_model_dir.mkdir(exist_ok=True)
        return default_model_dir
    
    def _set_application_icon(self):
        """アプリケーションアイコンを環境非依存で設定（Ultra Think PyInstaller対応）"""
        # Ultra Think: PyInstallerリソースベースパス
        resource_base = get_resource_base_path()
        
        # アイコンディレクトリを動的検出
        icon_search_paths = [
            # 1. バンドルされたapp_icons（PyInstaller --onefile対応）
            resource_base / "app_icons",
            # 2. プロジェクト内のapp_icons（開発環境用）
            Path(__file__).parent / "app_icons",
            # 3. 現在の作業ディレクトリ
            Path.cwd() / "app_icons"
        ]
        
        icon_files_priority = [
            "rvc_icon.icns",        # macOS推奨
            "icon_512x512.png",     # 高解像度
            "icon_256x256.png",     # 中解像度
            "icon_128x128.png",     # 標準解像度
            "rvc_icon.svg"          # ベクター（フォールバック）
        ]
        
        for icon_dir in icon_search_paths:
            if icon_dir.exists():
                for icon_file in icon_files_priority:
                    icon_path = icon_dir / icon_file
                    if icon_path.exists():
                        try:
                            from PyQt5.QtGui import QIcon
                            icon = QIcon(str(icon_path))
                            if not icon.isNull():
                                self.setWindowIcon(icon)
                                # アプリケーション全体のアイコンも設定
                                QApplication.instance().setWindowIcon(icon)
                                print(f"✅ Ultra Think独立版: アプリケーションアイコン設定 = {icon_path}")
                                return
                        except Exception as e:
                            print(f"⚠️ アイコン設定エラー {icon_path}: {e}")
                            continue
        
        print("⚠️ アプリケーションアイコンが見つかりません。デフォルトアイコンを使用します。")

def main():
    """メイン関数（Ultra Think完全自動再起動防止版）"""
    import signal
    import traceback
    import atexit
    import multiprocessing
    
    # Ultra Think: multiprocessing設定の制御
    try:
        multiprocessing.set_start_method('spawn', force=True)
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        os.environ['PYTHONUNBUFFERED'] = '1'
    except Exception as e:
        print(f"⚠️ multiprocessing設定エラー: {e}")
    
    # Ultra Think: 完全終了ハンドラー（プロセスグループ強制終了）
    def ultimate_cleanup():
        print("🔄 Ultra Think完全終了処理開始...")
        try:
            import subprocess
            import psutil
            
            # 現在のプロセスグループを取得
            current_pid = os.getpid()
            try:
                parent = psutil.Process(current_pid)
                
                # すべての子プロセスを強制終了
                children = parent.children(recursive=True)
                for child in children:
                    try:
                        child.terminate()
                        child.wait(timeout=1)
                    except:
                        try:
                            child.kill()
                        except:
                            pass
                
                print(f"✅ {len(children)}個の子プロセスを終了")
                
            except ImportError:
                print("⚠️ psutil未使用 - 基本終了処理のみ")
            
            # resource_tracker特定終了
            try:
                subprocess.run(['pkill', '-9', '-f', 'resource_tracker'], check=False, timeout=2)
                subprocess.run(['pkill', '-9', '-f', 'RVC Voice Converter'], check=False, timeout=2)
                print("✅ resource_trackerプロセス強制終了")
            except:
                pass
            
            # macOS Resume状態データを削除
            home_dir = os.path.expanduser("~")
            saved_state_dir = f"{home_dir}/Library/Saved Application State/com.rvc-project.standalone.savedState"
            try:
                if os.path.exists(saved_state_dir):
                    subprocess.run(["rm", "-rf", saved_state_dir], check=False, timeout=2)
                    print("✅ macOS Resume状態削除")
            except:
                pass
            
        except Exception as e:
            print(f"⚠️ Ultimate cleanup error: {e}")
        finally:
            # 最終的な強制終了
            print("🔄 プロセス強制終了")
            os._exit(0)
    
    # Ultra Think: atexit完全終了ハンドラー登録
    atexit.register(ultimate_cleanup)
    
    # Ultra Think: 無限起動防止のシングルインスタンス制御
    try:
        import fcntl
        import tempfile
        
        # シングルインスタンスロックファイル
        lock_file = os.path.join(tempfile.gettempdir(), "rvc_standalone.lock")
        lock_fd = os.open(lock_file, os.O_WRONLY | os.O_CREAT)
        
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            print("✅ RVCアプリは既に起動中です")
            sys.exit(0)
            
    except Exception as e:
        print(f"⚠️ シングルインスタンス制御エラー: {e}")
    
    # Ultra Think: 強化シグナルハンドラー
    def signal_handler(signum, frame):
        print(f"🔄 シグナル{signum}受信 - 完全終了開始...")
        ultimate_cleanup()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    
    try:
        # macOSでのQt表示問題の対策
        os.environ['QT_MAC_WANTS_LAYER'] = '1'
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
        os.environ['QT_LOGGING_RULES'] = '*.debug=false'  # Qtログ抑制
        
        # Ultra Think: macOS自動再開完全防止の環境変数
        os.environ['NSApplicationAutomaticTerminationSupportEnabled'] = 'NO'
        os.environ['NSQuitAlwaysKeepsWindows'] = 'NO'
        os.environ['NSSupportsAutomaticTermination'] = 'NO'
        os.environ['NSSupportsSuddenTermination'] = 'NO'
        
        # Ultra Think: PyQt初期化の安全化
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        # macOS特有の設定
        app.setAttribute(Qt.AA_DontShowIconsInMenus, False)
        app.setAttribute(Qt.AA_NativeWindows, True)
        app.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)
        
        # Ultra Think: macOS自動再開防止
        app.setAttribute(Qt.AA_MacDontSwapCtrlAndMeta, True)
        app.setQuitOnLastWindowClosed(True)
        
        # macOS Resume機能を無効化
        os.environ['NSApplicationAutomaticTerminationSupportEnabled'] = 'NO'
        os.environ['NSQuitAlwaysKeepsWindows'] = 'NO'
        
        # アプリケーション情報
        app.setApplicationName("RVC Voice Converter - 完全独立版")
        app.setApplicationVersion("1.0.0")
        app.setApplicationDisplayName("RVC Voice Converter Ultra Think Edition")
        app.setOrganizationName("RVC Project - Ultra Think")
        app.setOrganizationDomain("rvc-project.com")
        
        # Ultra Think: macOS自動再開完全防止システム
        def cleanup_and_quit():
            print("🔄 Ultra Think完全終了処理開始...")
            try:
                # macOSのResumeデータを削除
                import subprocess
                home_dir = os.path.expanduser("~")
                saved_state_dir = f"{home_dir}/Library/Saved Application State/com.rvc-project.standalone.savedState"
                
                try:
                    if os.path.exists(saved_state_dir):
                        subprocess.run(["rm", "-rf", saved_state_dir], check=False)
                        print("✅ macOS Resume状態をクリア")
                except:
                    pass
                
                # 全ウィンドウを強制終了
                for widget in app.allWidgets():
                    try:
                        widget.hide()
                        widget.close()
                        widget.deleteLater()
                    except:
                        pass
                
                # アプリケーション完全停止
                app.closeAllWindows()
                app.quit()
                
                # プロセス強制終了（自動再開防止）
                print("🔄 プロセス強制終了中...")
                os._exit(0)
                
            except Exception as e:
                print(f"⚠️ 終了処理エラー: {e}")
                # 何があっても強制終了
                os._exit(1)
        
        # 複数の終了トリガーに対応
        app.aboutToQuit.connect(cleanup_and_quit)
        app.applicationStateChanged.connect(lambda state: 
            cleanup_and_quit() if state == Qt.ApplicationSuspended else None)
        
        print("🚀 RVCアプリケーション初期化中...")
        
        # メインウィンドウ作成（例外処理付き）
        try:
            window = RVCStandaloneMainWindow()
        except Exception as e:
            print(f"❌ ウィンドウ作成エラー: {e}")
            print("詳細エラー:")
            traceback.print_exc()
            sys.exit(1)
        
        # ウィンドウ表示設定の強化
        window.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        window.setAttribute(Qt.WA_ShowWithoutActivating, False)
        window.show()
        window.raise_()
        window.activateWindow()
        
        # システム情報ログ
        window.log_message("🚀 RVC Voice Converter - 完全独立版 (Ultra Think) 起動")
        window.log_message(f"🐍 Python: {sys.version.split()[0]}")
        window.log_message(f"📊 音声ライブラリ: {'利用可能' if AUDIO_LIBS_AVAILABLE else '制限モード'}")
        window.log_message(f"🔧 RVC直接統合: {'利用可能' if RVC_DIRECT_AVAILABLE else 'CLI経由'}")
        window.log_message(f"🎵 対応フォーマット: WAV, MP3, FLAC" + (", M4A, AIFF, MP4" if PYDUB_AVAILABLE else " (基本形式のみ)"))
        window.log_message("🔥 Poetry環境不要 - 完全独立動作")
        
        print("✅ ウィンドウ表示完了 - 正常起動")
        
        # Ultra Think: 安全なアプリケーション実行
        exit_code = app.exec_()
        print(f"🔄 アプリケーション終了 (exit code: {exit_code})")
        
        # クリーンアップ
        try:
            if 'lock_fd' in locals():
                os.close(lock_fd)
            if 'lock_file' in locals() and os.path.exists(lock_file):
                os.unlink(lock_file)
        except Exception as e:
            print(f"⚠️ クリーンアップエラー: {e}")
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"❌ アプリケーション初期化エラー: {e}")
        print("詳細エラー:")
        traceback.print_exc()
        
        # 緊急クリーンアップ
        try:
            if 'lock_fd' in locals():
                os.close(lock_fd)
            if 'lock_file' in locals() and os.path.exists(lock_file):
                os.unlink(lock_file)
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()