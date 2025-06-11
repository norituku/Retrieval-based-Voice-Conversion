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
    # RVCライブラリを直接インポート（環境非依存）
    from rvc.configs.config import Config
    from rvc.modules.vc.modules import VC
    from rvc.modules.vc.utils import load_audio
    RVC_DIRECT_AVAILABLE = True
    print("✅ Ultra Think独立版: RVCライブラリ直接統合成功")
except ImportError as e:
    RVC_DIRECT_AVAILABLE = False
    print(f"⚠️ RVCライブラリ直接統合失敗: {e}")

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
        """Ultra Think: 完全独立版RVC推論実行"""
        try:
            if RVC_DIRECT_AVAILABLE:
                # 方法1: RVCライブラリ直接使用（推奨）
                self._run_direct_rvc_inference()
            else:
                # 方法2: 内蔵CLI実行（フォールバック）
                self._run_bundled_cli_inference()
                
        except Exception as e:
            error_msg = f"❌ Ultra Think独立版推論エラー: {str(e)}"
            print(error_msg)
            import traceback
            detailed_error = traceback.format_exc()
            print(f"詳細エラー: {detailed_error}")
            self.conversion_finished.emit(False, error_msg)
    
    def _run_direct_rvc_inference(self):
        """Ultra Think: RVCライブラリ直接推論"""
        
        # 【段階 1】初期化
        self.progress_updated.emit(5, "RVCライブラリ初期化中...")
        
        # RVC設定を初期化
        config = Config()
        config.device = "cpu"  # 安定性優先でCPU使用
        config.is_half = False  # 精度優先
        
        # 【段階 2】モデル読み込み
        self.progress_updated.emit(15, "音声モデルを読み込み中...")
        
        model_path = self.current_model['path']
        vc = VC(config)
        
        # モデルを読み込み
        vc.get_vc(model_path)
        
        # 【段階 3】音声ファイル読み込み
        self.progress_updated.emit(30, "音声ファイルを読み込み中...")
        
        # 音声データを読み込み
        audio, sr = load_audio(self.input_file, 16000)
        
        # 【段階 4】推論実行
        self.progress_updated.emit(50, "音声変換を実行中...")
        
        # RVC推論を実行
        audio_output = vc.vc_single(
            sid=0,
            input_audio_path=self.input_file,
            f0_up_key=self.params.get('pitch', 0),
            f0_method="rmvpe",
            file_index="",  # インデックスファイル
            file_index2="",
            index_rate=self.params.get('index_rate', 0.75),
            filter_radius=self.params.get('filter_radius', 3),
            resample_sr=0,
            rms_mix_rate=0.25,
            protect=0.33
        )
        
        # 【段階 5】結果保存
        self.progress_updated.emit(85, "変換結果を保存中...")
        
        # 出力ファイルに保存
        sf.write(self.output_file, audio_output[1], audio_output[0])
        
        # 【段階 6】完了確認
        self.progress_updated.emit(100, "変換完了")
        
        if Path(self.output_file).exists():
            file_size = Path(self.output_file).stat().st_size
            print(f"✅ Ultra Think独立版変換完了 - サイズ: {file_size} bytes")
            if file_size > 0:
                self.conversion_finished.emit(True, f"RVC独立版変換完了: {self.output_file}")
            else:
                raise Exception(f"結果ファイルが空です: {self.output_file}")
        else:
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
        
        # Ultra Think: Hubertモデルパス取得（必須）
        resource_base = get_resource_base_path()
        hubert_model_paths = [
            resource_base / "model_dir" / "hubert_base.pt",
            Path("model_dir") / "hubert_base.pt",
            Path.cwd() / "model_dir" / "hubert_base.pt"
        ]
        
        hubert_model_path = None
        for path in hubert_model_paths:
            if path.exists():
                hubert_model_path = str(path)
                break
        
        if not hubert_model_path:
            raise RuntimeError("hubert_base.pt が見つかりません")
        
        # 動作確認済み最小限のコマンド構築
        cmd_array = [
            python_path, "-m", "rvc.wrapper.cli.cli", "infer",
            "-m", model_path,
            "-i", self.input_file,
            "-o", self.output_file,
            "--hubert_model_path", hubert_model_path,  # 必須オプション
            "-fu", str(self.params.get('pitch', 0)),
            "-fm", "rmvpe"
            # 最小限の引数のみ（動作確認済み）
        ]
        
        # 【段階 3-6】CLI実行
        self._run_cli_with_progress(cmd_array)
    
    def _run_cli_with_progress(self, cmd_array):
        """Ultra Think: CLI実行とプログレス追跡"""
        
        print(f"🔧 実行コマンド: {' '.join(cmd_array)}")
        
        # 【段階 3】推論開始
        self.progress_updated.emit(30, "音声の特徴を抽出中...")
        
        # 環境変数設定
        env = os.environ.copy()
        env['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        
        process = subprocess.Popen(
            cmd_array,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env
        )
        
        current_stage = 3
        line_count = 0
        total_lines_estimate = 50
        
        # CLI出力を監視してプログレス更新
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.strip()
                if line:
                    print(f"RVC: {line}")
                    line_count += 1
                    
                    # 進捗推定
                    stage_progress = min((line_count / total_lines_estimate) * 100, 100)
                    
                    # キーワードによる進捗判定
                    if "Loading" in line or "loading" in line:
                        progress_val = 30 + int(stage_progress * 0.1)
                        self.progress_updated.emit(progress_val, "モデルを読み込み中...")
                    elif "Extract" in line or "extract" in line:
                        if current_stage == 3:
                            progress_val = 35 + int(stage_progress * 0.2)
                            self.progress_updated.emit(progress_val, "特徴抽出を実行中...")
                    elif "Process" in line or "process" in line:
                        if current_stage < 4:
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
                            self.progress_updated.emit(85, "音声変換完了")
                            current_stage = 5
                            self.progress_updated.emit(88, "音質の最適化を実行中...")
                        progress_val = 88 + int(stage_progress * 0.05)
                        self.progress_updated.emit(progress_val, "最適化処理中...")
        
        process.wait()
        
        # エラーチェック
        if process.returncode != 0:
            error_msg = f"RVC CLI inference failed with return code: {process.returncode}"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        
        # 完了処理
        self.progress_updated.emit(95, "変換結果を保存中...")
        time.sleep(0.5)
        self.progress_updated.emit(100, "保存完了")
        
        # 出力ファイル確認
        if Path(self.output_file).exists():
            file_size = Path(self.output_file).stat().st_size
            print(f"✅ CLI変換結果ファイル確認OK - サイズ: {file_size} bytes")
            if file_size > 0:
                self.conversion_finished.emit(True, f"RVC CLI変換完了: {self.output_file}")
            else:
                raise Exception(f"結果ファイルが空です: {self.output_file}")
        else:
            raise Exception(f"出力ファイルが作成されていません: {self.output_file}")

class ModelCard(QFrame):
    """音声モデルカード表示（Ultra Think視覚改善版）"""
    
    def __init__(self, model_info):
        super().__init__()
        self.model_info = model_info
        self.is_selected = False
        self.setup_ui()
        self.apply_default_style()
        
    def setup_ui(self):
        """UIセットアップ（Ultra Think改善版）"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedHeight(130)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # モデル名（改善版）
        name_label = QLabel(self.model_info.get('name', 'Unknown Model'))
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setStyleSheet("color: #ffffff; margin-bottom: 2px;")
        layout.addWidget(name_label)
        
        # ファイルパス（改善版）
        path_text = self.model_info.get('path', 'N/A')
        if len(path_text) > 50:
            path_text = "..." + path_text[-47:]
        path_label = QLabel(f"Path: {path_text}")
        path_label.setFont(QFont("Arial", 8))
        path_label.setStyleSheet("color: #cccccc;")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        # インデックス情報（改善版）
        has_index = self.model_info.get('has_index', False)
        index_label = QLabel(f"Index: {'あり' if has_index else 'なし'}")
        index_label.setFont(QFont("Arial", 9, QFont.Bold))
        index_color = "#4CAF50" if has_index else "#FF9800"
        index_label.setStyleSheet(f"color: {index_color}; margin-top: 2px;")
        layout.addWidget(index_label)
        
        self.setLayout(layout)
    
    def apply_default_style(self):
        """デフォルトスタイル適用（Ultra Think）"""
        self.setStyleSheet("""
            ModelCard {
                background-color: #2d2d30;
                border: 1px solid #404042;
                border-radius: 6px;
                margin: 2px;
            }
            ModelCard:hover {
                background-color: #3d3d40;
                border: 1px solid #555558;
            }
        """)
        self.is_selected = False
    
    def apply_selected_style(self):
        """選択状態スタイル適用（Ultra Think）"""
        self.setStyleSheet("""
            ModelCard {
                background-color: #1e3a5f;
                border: 2px solid #2A82DA;
                border-radius: 6px;
                margin: 2px;
            }
            ModelCard:hover {
                background-color: #264a6f;
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
        self.output_dir = app_dir / "enhanced_output"
        self.output_dir.mkdir(exist_ok=True)
        
        self.models = []
        self.current_model = None
        
        self.setup_ui()
        self.setup_dark_theme()
        self.load_models()
        
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
        
        # 更新ボタン
        refresh_btn = QPushButton("モデル更新")
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
    """メイン関数"""
    app = QApplication(sys.argv)
    
    # アプリケーション情報
    app.setApplicationName("RVC Voice Converter - 完全独立版")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("RVC Project - Ultra Think")
    
    # メインウィンドウ作成
    window = RVCStandaloneMainWindow()
    window.show()
    
    # システム情報ログ
    window.log_message("🚀 RVC Voice Converter - 完全独立版 (Ultra Think) 起動")
    window.log_message(f"🐍 Python: {sys.version.split()[0]}")
    window.log_message(f"📊 音声ライブラリ: {'利用可能' if AUDIO_LIBS_AVAILABLE else '制限モード'}")
    window.log_message(f"🔧 RVC直接統合: {'利用可能' if RVC_DIRECT_AVAILABLE else 'CLI経由'}")
    window.log_message(f"🎵 対応フォーマット: WAV, MP3, FLAC" + (", M4A, AIFF, MP4" if PYDUB_AVAILABLE else " (基本形式のみ)"))
    window.log_message("🔥 Poetry環境不要 - 完全独立動作")
    
    # アプリケーション実行
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()