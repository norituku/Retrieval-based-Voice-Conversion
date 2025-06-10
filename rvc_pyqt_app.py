#!/usr/bin/env python3
"""
RVC Voice Converter - PyQt5 Edition
記事手順に従った PyQt5 + PyInstaller --onefile 対応版

参考記事: https://techblog.hacomono.jp/entry/2024/06/04/1100
- venv でパッケージ管理
- PyQt5 でGUI
- PyInstaller --onefile で単一ファイル化
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

# Ultra Think最終修正：rmvpe環境変数を自動設定
possible_rmvpe_dirs = [
    "/Users/norikene_satoshi/Desktop/model_dir",
    str(Path.cwd() / "model_dir"),
    str(Path(__file__).parent / "model_dir")
]
for rmvpe_dir in possible_rmvpe_dirs:
    if Path(rmvpe_dir).exists() and Path(rmvpe_dir + "/rmvpe.pt").exists():
        os.environ['rmvpe_root'] = rmvpe_dir
        print(f"✅ Ultra Think: rmvpe_root自動設定 = {rmvpe_dir}")
        break

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

class VoiceConversionThread(QThread):
    """音声変換処理用スレッド（Ultra Think最適化版）"""
    
    def _filter_enhanced_output(self, line):
        """Enhanced Voice Converter出力の高度フィルタリング（GUI Dark Mode Enhanced版準拠）"""
        import re
        
        # Enhanced変換の重要な進行状況ログを判定
        enhanced_progress_patterns = [
            r"Enhanced Pipeline starting",
            r"Segment \d+/\d+", 
            r"Processing.*segment",
            r"Audio concatenation",
            r"Enhanced Pipeline completed",
            r"Conversion completed successfully",
            r"✅.*processed:",
            r"Performance stats:",
            r"Enhanced features:",
            r"Model loaded successfully",
            r"Starting enhanced conversion",
            r"RESULT:"
        ]
        
        # Enhanced変換の重要な進行状況は常に表示
        for pattern in enhanced_progress_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return line  # 重要な進行状況は表示
        
        # 詳細なデバッグログはフィルタ（大幅拡張版）
        debug_noise_patterns = [
            # Enhanced Pipeline デバッグ
            r"DEBUG:.*Before size adjustment",
            r"DEBUG:.*Pitch shapes:",
            r"DEBUG:.*Adjusted pitch to", 
            r"DEBUG:.*Adaptive search:",
            r"DEBUG:.*✅ Protect processing completed",
            r"🔍 DEBUG:.*",  # 全般的なデバッグログ
            
            # RVC内部処理
            r"current directory is",
            r"Loading faiss\.",
            r"Successfully loaded faiss\.",
            r"\[DEBUG.*\].*Attempting to load",
            r"Final.*SR.*for output:",
            r"Selected Synthesizer:",
            r"Model weights loaded from checkpoint",
            r"Synthesizer initialized and model loaded", 
            r"Faiss index loaded successfully",
            r"Pipeline initialized successfully",
            r"\[DEBUG.*\]",
            
            # PyTorch/MPS関連
            r"UserWarning:",
            r"torch\.nn\.utils\.weight_norm",
            r"MPS.*fallback.*CPU",
            r"performance implications",
            r"overwrite configs\.json",
            r"Use mps instead",
            r"is_half:.*device:",
            r"No supported Nvidia GPU found",
            r"INFO:rvc\.configs\.config:",
            
            # Fairseq/Hubert関連
            r"HubertModel Config:",
            r"HubertPretrainingTask Config:",
            r"Hubert model loaded successfully",
            r"Input audio will be resampled",
            r"Loading input audio from:",
            r"⚠️ fairseq not available",
            
            # 数値統計（冗長）
            r"Stats.*min=.*max=.*mean=",
            r"Input audio loaded\. Shape:",
            r"f0 estimation completed\.",
            r"Pitch.*Shape=.*Dtype=",
            r"INFO:.*Stats: min=",
            r"INFO:.*Shape:",
            r"INFO:.*memory usage",
            
            # 繰り返しの多い技術詳細
            r"Pipeline Args Overview:", 
            r"Pipeline internal index_path:",
            r"Calling self\.pipeline\.pipeline",
            r"Returned processing times:",
            r"VC\.vc_inference.*START",
            r"VC\.vc_inference.*END",
            r"INFO:rvc\.modules\.vc\.modules:",
            r"INFO:rvc\.modules\.vc\.pipeline:",
            r"INFO:enhanced_voice_converter:.*shape",
            r"INFO:enhanced_voice_converter:.*type",
            r"INFO:enhanced_voice_converter:.*memory",
            r"🔍 Pipeline:",
            r"🔍 DummyHubert:",
            
            # Deprecation warnings
            r"FutureWarning:",
            r"DeprecationWarning:",
            r"PendingDeprecationWarning:"
        ]
        
        # デバッグノイズパターンに一致する場合は非表示
        for pattern in debug_noise_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return None  # フィルタして非表示
        
        return line  # その他は表示
    # 注: _filter_enhanced_output関数は新実装では使用されません
    progress_updated = pyqtSignal(int, str)
    conversion_finished = pyqtSignal(bool, str)
    
    def __init__(self, input_file, output_file, current_model, params, model_dir=None):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.current_model = current_model  # 修正: model_path → current_model
        self.params = params
        self.model_dir = model_dir
        
    def run(self):
        """GUI Dark Mode版の6段階変換工程を完全移植（Ultra Think方針A）"""
        try:
            # 【段階 0】プロジェクトとモデルの初期化（GUI Dark Mode版と完全同一）
            self.progress_updated.emit(0, "プロジェクトとモデルの初期化中...")
            
            # プロジェクトディレクトリを確認（GUI Dark Mode版と完全同一）
            project_dir = str(Path.cwd())
            if project_dir.endswith('/Resources'):
                possible_dirs = [
                    "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion",
                    os.path.expanduser("~/Retrieval-based-Voice-Conversion"),
                ]
                for dir_path in possible_dirs:
                    if os.path.exists(os.path.join(dir_path, "pyproject.toml")):
                        project_dir = dir_path
                        break
            
            time.sleep(0.5)  # GUI Dark Mode版と同じ視覚的フィードバック
            self.progress_updated.emit(5, "初期化完了")
            
            # 【段階 1】音声ファイルとモデルデータを読み込み（GUI Dark Mode版と完全同一）
            self.progress_updated.emit(10, "音声ファイルとモデルデータを読み込み中...")
            
            # モデル情報を構築（GUI Dark Mode版と完全同一のロジック）
            model_path = Path(self.current_model['path'])
            model_dir = model_path.parent
            
            # インデックスファイルを検索（GUI Dark Mode版と完全同一）
            index_file = None
            if self.current_model.get('has_index', False):
                if os.path.exists(model_dir):
                    index_files = [f for f in os.listdir(model_dir) if f.endswith('.index')]
                    if index_files:
                        index_file = os.path.join(model_dir, index_files[0])
            
            time.sleep(0.5)
            self.progress_updated.emit(15, "データ読み込み完了")
            
            # 【段階 2】音声データの前処理開始（GUI Dark Mode版と完全同一）
            self.progress_updated.emit(20, "音声データの前処理を開始...")
            
            # Hubertモデルパスを検索（GUI Dark Mode版と完全同一）
            hubert_path = os.path.join(project_dir, "model_dir", "hubert_base.pt")
            if not os.path.exists(hubert_path):
                alt_hubert = os.path.join(project_dir, "model_dir", "hubert_base.pt")
                if os.path.exists(alt_hubert):
                    hubert_path = alt_hubert
            
            # Poetry環境チェック（GUI Dark Mode版と完全同一）
            poetry_available = subprocess.run(
                ["which", "poetry"],
                capture_output=True,
                text=True
            ).returncode == 0
            
            if not poetry_available:
                raise RuntimeError("Poetry not found. Please install Poetry first.")
            
            # GUI Dark Mode版と完全同一のコマンド構築
            try:
                from rvc_config import POETRY_PYTHON_PATH, RVC_MODULE
                USE_HARDCODED_PATH = True
            except ImportError:
                USE_HARDCODED_PATH = False
            
            if USE_HARDCODED_PATH and os.path.exists(POETRY_PYTHON_PATH):
                cmd_array = [
                    POETRY_PYTHON_PATH, "-m", RVC_MODULE, "infer",
                    "-m", str(model_path),
                    "-i", self.input_file,  # GUI Dark Mode版: 直接ファイル使用
                    "-o", self.output_file,  # GUI Dark Mode版: 直接ファイル使用
                    "-fu", str(self.params.get('pitch', 0)),
                    "-fm", "rmvpe",
                    "-ir", str(self.params.get('index_rate', 0.75)),
                    "-fr", str(self.params.get('filter_radius', 3)),
                    "-p", "0.33",
                    "-rmr", "0.25"
                ]
                print(f"Using hardcoded Python path: {POETRY_PYTHON_PATH}")
            else:
                # Poetry環境のPythonパスを取得（GUI Dark Mode版と完全同一）
                poetry_env_result = subprocess.run(
                    ["poetry", "env", "info", "--path"],
                    capture_output=True,
                    text=True,
                    cwd=project_dir
                )
                
                if poetry_env_result.returncode == 0:
                    poetry_env_path = poetry_env_result.stdout.strip()
                    python_path = os.path.join(poetry_env_path, "bin", "python")
                    if os.path.exists(python_path):
                        # 仮想環境のPythonを直接使用（GUI Dark Mode版と完全同一）
                        cmd_array = [
                            python_path, "-m", "rvc.wrapper.cli.cli", "infer",
                            "-m", str(model_path),
                            "-i", self.input_file,
                            "-o", self.output_file,
                            "-fu", str(self.params.get('pitch', 0)),
                            "-fm", "rmvpe",
                            "-ir", str(self.params.get('index_rate', 0.75)),
                            "-fr", str(self.params.get('filter_radius', 3)),
                            "-p", "0.33",
                            "-rmr", "0.25"
                        ]
                        print(f"Using Python from: {python_path}")
                    else:
                        # フォールバック: poetry runを使用（GUI Dark Mode版と完全同一）
                        cmd_array = [
                            "poetry", "run", "rvc", "infer",
                            "-m", str(model_path),
                            "-i", self.input_file,
                            "-o", self.output_file,
                            "-fu", str(self.params.get('pitch', 0)),
                            "-fm", "rmvpe",
                            "-ir", str(self.params.get('index_rate', 0.75)),
                            "-fr", str(self.params.get('filter_radius', 3)),
                            "-p", "0.33",
                            "-rmr", "0.25"
                        ]
                else:
                    # poetry runを使用（GUI Dark Mode版と完全同一）
                    cmd_array = [
                        "poetry", "run", "rvc", "infer",
                        "-m", str(model_path),
                        "-i", self.input_file,
                        "-o", self.output_file,
                        "-fu", str(self.params.get('pitch', 0)),
                        "-fm", "rmvpe",
                        "-ir", str(self.params.get('index_rate', 0.75)),
                        "-fr", str(self.params.get('filter_radius', 3)),
                        "-p", "0.33",
                        "-rmr", "0.25"
                    ]
            
            # インデックスファイルとHubertパスを追加（GUI Dark Mode版と完全同一）
            if index_file and os.path.exists(index_file):
                cmd_array.extend(["-if", index_file])
            
            if os.path.exists(hubert_path):
                cmd_array.extend(["--hubert_model_path", hubert_path])
            
            # 環境変数の設定（GUI Dark Mode版と完全同一）
            env = os.environ.copy()
            env['PYTHONPATH'] = project_dir
            env['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            env['rmvpe_root'] = os.path.join(
                project_dir, 'model_dir' if os.path.exists(os.path.join(project_dir, 'model_dir', 'rmvpe.pt'))
                else 'model_dir'
            )
            
            # Conda環境変数をクリア（GUI Dark Mode版と完全同一）
            env.pop('CONDA_DEFAULT_ENV', None)
            env.pop('CONDA_PREFIX', None)
            env.pop('CONDA_PYTHON_EXE', None)
            env.pop('CONDA_EXE', None)
            env.pop('CONDA_PROMPT_MODIFIER', None)
            env.pop('_CE_CONDA', None)
            env.pop('_CE_M', None)
            
            self.progress_updated.emit(25, "前処理完了")
            
            # 【段階 3-6】RVC推論の実行（GUI Dark Mode版完全移植）
            self._run_rvc_with_progress_pyqt(cmd_array, env, project_dir)
            
            # 【段階 7】出力保存確認（GUI Dark Mode版と完全同一）
            self.progress_updated.emit(95, "変換結果を保存中...")
            time.sleep(0.5)
            self.progress_updated.emit(100, "保存完了")
            
            # 出力ファイルの確認（GUI Dark Mode版と完全同一）
            if Path(self.output_file).exists():
                file_size = Path(self.output_file).stat().st_size
                print(f"✅ 変換結果ファイル確認OK - サイズ: {file_size} bytes")
                if file_size > 0:
                    self.conversion_finished.emit(True, f"RVC変換完了: {self.output_file}")
                else:
                    raise Exception(f"結果ファイルが空です: {self.output_file}")
            else:
                raise Exception(f"出力ファイルが作成されていません: {self.output_file}")
                
        except Exception as e:
            error_msg = f"❌ GUI Dark Mode版6段階変換工程でエラー: {str(e)}"
            print(error_msg)
            import traceback
            detailed_error = traceback.format_exc()
            print(f"詳細エラー: {detailed_error}")
            self.conversion_finished.emit(False, error_msg)
    
    def _run_rvc_with_progress_pyqt(self, cmd_array, env, project_dir):
        """GUI Dark Mode版の_run_rvc_with_progressを完全移植（PyQt版）"""
        
        print(f"🔧 実行コマンド: {' '.join(cmd_array)}")
        print(f"🔧 作業ディレクトリ: {project_dir}")
        
        # 【段階 3】特徴抽出開始（GUI Dark Mode版と完全同一）
        self.progress_updated.emit(30, "音声の特徴を抽出中...")
        
        process = subprocess.Popen(
            cmd_array,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env,
            cwd=project_dir
        )
        
        current_stage = 3  # 特徴抽出ステージ（GUI Dark Mode版と完全同一）
        line_count = 0
        total_lines_estimate = 100  # 推定行数
        
        # GUI Dark Mode版と完全同一のログ処理とプログレス追跡
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.strip()
                if line:
                    print(f"RVC: {line}")
                    line_count += 1
                    
                    # 行数に基づく進捗更新（GUI Dark Mode版と完全同一）
                    stage_progress = min((line_count / total_lines_estimate) * 100, 100)
                    
                    # キーワードによる進捗とステージの推定（GUI Dark Mode版と完全同一）
                    if "Loading" in line or "loading" in line:
                        progress_val = 30 + int(stage_progress * 0.1)
                        self.progress_updated.emit(progress_val, "モデルを読み込み中...")
                    elif "Extract" in line or "extract" in line:
                        if current_stage == 3:
                            progress_val = 35 + int(stage_progress * 0.2)
                            self.progress_updated.emit(progress_val, "特徴抽出を実行中...")
                    elif "Process" in line or "process" in line:
                        if current_stage < 4:
                            # ステージ4: モデル推論に移行（GUI Dark Mode版と完全同一）
                            self.progress_updated.emit(55, "特徴抽出完了")
                            current_stage = 4
                            self.progress_updated.emit(60, "AIモデルで音声を変換中...")
                        progress_val = 60 + int(stage_progress * 0.15)
                        self.progress_updated.emit(progress_val, "音声変換を処理中...")
                    elif "Generate" in line or "generate" in line:
                        progress_val = 75 + int(stage_progress * 0.1)
                        self.progress_updated.emit(progress_val, "音声を生成中...")
                    elif "Save" in line or "save" in line or "Write" in line or "write" in line:
                        if current_stage < 5:
                            # ステージ5: 後処理に移行（GUI Dark Mode版と完全同一）
                            self.progress_updated.emit(85, "音声変換完了")
                            current_stage = 5
                            self.progress_updated.emit(88, "音質の最適化を実行中...")
                        progress_val = 88 + int(stage_progress * 0.05)
                        self.progress_updated.emit(progress_val, "最適化処理中...")
                    
                    # 進捗の詳細表示（GUI Dark Mode版と完全同一）
                    if line_count % 5 == 0:  # 5行ごとに更新
                        if current_stage == 3:
                            progress = min(35 + stage_progress * 0.2, 54)
                            self.progress_updated.emit(int(progress), f"特徴抽出中... ({line_count}行処理)")
                        elif current_stage == 4:
                            progress = min(60 + stage_progress * 0.15, 74)
                            self.progress_updated.emit(int(progress), f"音声変換中... ({line_count}行処理)")
                        elif current_stage == 5:
                            progress = min(88 + stage_progress * 0.05, 92)
                            self.progress_updated.emit(int(progress), f"後処理中... ({line_count}行処理)")
        
        process.wait()
        
        # エラーチェック（GUI Dark Mode版と完全同一）
        if process.returncode != 0:
            error_msg = f"RVC inference failed with return code: {process.returncode}"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        
        # 処理完了を確認（GUI Dark Mode版と完全同一）
        if current_stage == 3:
            self.progress_updated.emit(55, "特徴抽出完了")
            self.progress_updated.emit(85, "音声変換完了")
            self.progress_updated.emit(93, "後処理完了")
        elif current_stage == 4:
            self.progress_updated.emit(85, "音声変換完了")
            self.progress_updated.emit(93, "後処理完了")
        elif current_stage == 5:
            self.progress_updated.emit(93, "後処理完了")
    
    def load_audio_file(self, file_path):
        """多様な音声フォーマットに対応した音声ファイル読み込み"""
        file_ext = Path(file_path).suffix.lower()
        
        # まず soundfile で直接読み込みを試行
        try:
            audio, sr = sf.read(file_path)
            return audio, sr
        except Exception as sf_error:
            print(f"soundfile読み込み失敗: {sf_error}")
            
            # soundfile で失敗した場合、pydub を使用
            if PYDUB_AVAILABLE:
                try:
                    print(f"pydubで {file_ext} ファイルを変換中...")
                    
                    # pydub で読み込み
                    if file_ext == '.m4a':
                        audio_segment = AudioSegment.from_file(file_path, format="m4a")
                    elif file_ext == '.aiff':
                        audio_segment = AudioSegment.from_file(file_path, format="aiff")
                    elif file_ext == '.mp3':
                        audio_segment = AudioSegment.from_mp3(file_path)
                    elif file_ext == '.mp4':
                        audio_segment = AudioSegment.from_file(file_path, format="mp4")
                    else:
                        # その他の形式も汎用的に試行
                        audio_segment = AudioSegment.from_file(file_path)
                    
                    # WAV形式に正規化（モノラル、16bit）
                    audio_segment = audio_segment.set_channels(1)  # モノラル化
                    audio_segment = audio_segment.set_frame_rate(44100)  # 44.1kHzに統一
                    
                    # numpy配列に変換
                    audio_data = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
                    audio_data = audio_data / 32768.0  # 16bitから正規化
                    
                    return audio_data, audio_segment.frame_rate
                    
                except Exception as pydub_error:
                    print(f"pydub読み込み失敗: {pydub_error}")
                    raise Exception(f"音声ファイル読み込み失敗: soundfile({sf_error}), pydub({pydub_error})")
            else:
                raise Exception(f"対応していない音声フォーマット: {file_ext}. pydubが必要です。")

class ModelCard(QFrame):
    """音声モデルカード表示"""
    
    def __init__(self, model_info):
        super().__init__()
        self.model_info = model_info
        self.setup_ui()
        
    def setup_ui(self):
        """UIセットアップ"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedHeight(120)
        
        layout = QVBoxLayout()
        
        # モデル名
        name_label = QLabel(self.model_info.get('name', 'Unknown Model'))
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(name_label)
        
        # ファイルパス
        path_label = QLabel(f"Path: {self.model_info.get('path', 'N/A')}")
        path_label.setFont(QFont("Arial", 9))
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        # インデックス情報
        has_index = self.model_info.get('has_index', False)
        index_label = QLabel(f"Index: {'あり' if has_index else 'なし'}")
        index_label.setFont(QFont("Arial", 9))
        index_label.setStyleSheet(f"color: {'green' if has_index else 'orange'};")
        layout.addWidget(index_label)
        
        self.setLayout(layout)

class RVCMainWindow(QMainWindow):
    """RVC メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        
        # PyInstallerでパッケージされた場合の実行ディレクトリを取得
        if getattr(sys, 'frozen', False):
            # 実行可能ファイルとして実行されている場合
            app_dir = Path(sys.executable).parent
        else:
            # 開発環境で実行されている場合
            app_dir = Path.cwd()
        
        self.model_dir = app_dir / "model_dir"
        self.output_dir = app_dir / "enhanced_output"
        self.output_dir.mkdir(exist_ok=True)
        
        self.models = []
        self.current_model = None
        
        self.setup_ui()
        self.setup_dark_theme()
        self.load_models()
        
    def setup_ui(self):
        """UI構築"""
        self.setWindowTitle("RVC Voice Converter - PyQt5 Edition")
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
        """モデル選択パネル作成"""
        panel = QGroupBox("音声モデル")
        layout = QVBoxLayout()
        
        # モデルディレクトリ選択エリア
        model_dir_group = self.create_model_directory_group()
        layout.addWidget(model_dir_group)
        
        # 更新ボタン
        refresh_btn = QPushButton("モデル更新")
        refresh_btn.clicked.connect(self.load_models)
        layout.addWidget(refresh_btn)
        
        # モデル一覧（スクロール可能）
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.model_layout = QVBoxLayout()
        scroll_widget.setLayout(self.model_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        panel.setLayout(layout)
        return panel
    
    def create_model_directory_group(self):
        """モデルディレクトリ選択グループ"""
        group = QGroupBox("モデルディレクトリ")
        layout = QGridLayout()
        
        # 現在のディレクトリ表示
        layout.addWidget(QLabel("現在のディレクトリ:"), 0, 0)
        self.model_dir_label = QLabel(str(self.model_dir))
        self.model_dir_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: #2a2a2a;")
        self.model_dir_label.setWordWrap(True)
        layout.addWidget(self.model_dir_label, 0, 1)
        
        # ディレクトリ選択ボタン
        select_dir_btn = QPushButton("ディレクトリを選択")
        select_dir_btn.clicked.connect(self.select_model_directory)
        layout.addWidget(select_dir_btn, 0, 2)
        
        # デフォルトに戻すボタン
        reset_dir_btn = QPushButton("デフォルトに戻す")
        reset_dir_btn.clicked.connect(self.reset_model_directory)
        layout.addWidget(reset_dir_btn, 1, 2)
        
        group.setLayout(layout)
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
        self.convert_btn = QPushButton("音声変換開始")
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
        self.index_slider.setValue(75)  # CLI版デフォルト0.75に合わせる
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
        
        # スタイルシート
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
        """モデル選択"""
        self.current_model = model_info
        self.log_message(f"📋 モデル選択: {model_info['name']}")
        
        # 選択状態のビジュアル更新
        for i in range(self.model_layout.count()):
            widget = self.model_layout.itemAt(i).widget()
            if widget:
                if hasattr(widget, 'model_info') and widget.model_info == model_info:
                    widget.setStyleSheet("QFrame { border: 2px solid #2a82da; }")
                else:
                    widget.setStyleSheet("QFrame { border: 1px solid gray; }")
    
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
            output_name = f"{input_path.stem}_converted.wav"
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
        """音声変換開始"""
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
        
        self.log_message("🎵 音声変換開始...")
        self.convert_btn.setEnabled(False)
        
        # 変換スレッド開始
        self.conversion_thread = VoiceConversionThread(
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
        
        self.model_dir = app_dir / "model_dir"
        self.model_dir_label.setText(str(self.model_dir))
        self.log_message(f"🔄 モデルディレクトリをデフォルトに戻しました: {self.model_dir}")
        
        # モデルを再読み込み
        self.load_models()

def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    
    # アプリケーション情報
    app.setApplicationName("RVC Voice Converter")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("RVC Project")
    
    # メインウィンドウ作成
    window = RVCMainWindow()
    window.show()
    
    # システム情報ログ
    window.log_message("🚀 RVC Voice Converter - PyQt5 Edition 起動")
    window.log_message(f"🐍 Python: {sys.version.split()[0]}")
    window.log_message(f"📊 音声ライブラリ: {'利用可能' if AUDIO_LIBS_AVAILABLE else '制限モード'}")
    window.log_message(f"🎵 対応フォーマット: WAV, MP3, FLAC" + (", M4A, AIFF, MP4" if PYDUB_AVAILABLE else " (基本形式のみ)"))
    
    # アプリケーション実行
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()