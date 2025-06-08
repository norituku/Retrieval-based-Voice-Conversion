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
    """音声変換処理用スレッド"""
    progress_updated = pyqtSignal(int, str)
    conversion_finished = pyqtSignal(bool, str)
    
    def __init__(self, input_file, output_file, model_path, params, model_dir=None):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.model_path = model_path
        self.params = params
        self.model_dir = model_dir
        
    def run(self):
        """音声変換実行"""
        try:
            self.progress_updated.emit(10, "音声ファイル読み込み中...")
            
            if not AUDIO_LIBS_AVAILABLE:
                error_msg = "❌ 必要な音声処理ライブラリ（numpy、torch、soundfile、librosa）がインストールされていません。"
                self.conversion_finished.emit(False, error_msg)
                return
            
            # 音声ファイル読み込み（多様なフォーマット対応）
            audio, sr = self.load_audio_file(self.input_file)
            self.progress_updated.emit(30, "音声データ処理中...")
            
            # RVC音声変換を実行（フォールバック処理なし）
            self.progress_updated.emit(40, "RVCモデル初期化中...")
            converted_audio = self.perform_rvc_conversion(audio, sr)
            
            if converted_audio is None:
                error_msg = "❌ RVC音声変換に失敗しました。モデルファイルや依存関係を確認してください。"
                self.conversion_finished.emit(False, error_msg)
                return
            
            self.progress_updated.emit(70, "音声ファイル保存中...")
            sf.write(self.output_file, converted_audio, sr)
            
            self.progress_updated.emit(100, "RVC変換完了")
            self.conversion_finished.emit(True, f"RVC変換完了: {self.output_file}")
            
        except Exception as e:
            error_msg = f"❌ 音声変換中にエラーが発生: {str(e)}"
            print(error_msg)
            import traceback
            detailed_error = traceback.format_exc()
            print(f"詳細エラー: {detailed_error}")
            self.conversion_finished.emit(False, error_msg)
    
    def perform_rvc_conversion(self, audio, sr):
        """Enhanced Voice Converterを使用した実際のRVC音声変換"""
        print(f"🔍 DEBUG: RVC変換開始 - 音声shape: {audio.shape}, sr: {sr}")
        try:
            # Enhanced Voice Converterをインポート（エラーハンドリング強化）
            try:
                # PyInstallerアプリの場合、_internalディレクトリを追加
                current_dir = Path.cwd()
                internal_dir = current_dir / "_internal"
                if internal_dir.exists():
                    sys.path.insert(0, str(internal_dir))
                    print(f"🔍 DEBUG: _internalディレクトリをsys.pathに追加: {internal_dir}")
                else:
                    sys.path.append(str(current_dir))
                    print(f"🔍 DEBUG: 現在ディレクトリをsys.pathに追加: {current_dir}")
                
                from enhanced_voice_converter import EnhancedVoiceConverter
                print("🔍 DEBUG: Enhanced Voice Converter インポート成功")
            except ImportError as import_error:
                error_msg = str(import_error)
                print(f"🔍 DEBUG: Enhanced Voice Converter インポートエラー: {error_msg}")
                
                if "fairseq" in error_msg.lower():
                    raise Exception("🚨 RVC変換に必要なfairseqライブラリがインストールされていません。\n💡 解決方法: pip install fairseq を実行してください。")
                elif "rvc" in error_msg.lower():
                    raise Exception("🚨 RVCモジュールが見つかりません。\n💡 解決方法: RVCライブラリが正しくインストールされていない可能性があります。")
                else:
                    raise Exception(f"🚨 Enhanced Voice Converterの依存関係エラー: {error_msg}")
            
            # 実行ディレクトリを取得
            if getattr(sys, 'frozen', False):
                app_dir = Path(sys.executable).parent
            else:
                app_dir = Path.cwd()
            
            print(f"🔍 DEBUG: app_dir: {app_dir}")
            
            # モデルディレクトリを決定
            model_dir_path = str(self.model_dir) if self.model_dir else str(app_dir / "model_dir")
            print(f"🔍 DEBUG: 使用するモデルディレクトリ: {model_dir_path}")
            
            # モデルディレクトリの存在確認
            if not Path(model_dir_path).exists():
                raise Exception(f"🚨 モデルディレクトリが存在しません: {model_dir_path}\n💡 解決方法: 正しいモデルディレクトリを選択してください。")
            
            # Enhanced Voice Converterを初期化（エラーハンドリング強化）
            try:
                converter = EnhancedVoiceConverter(
                    model_dir=model_dir_path,
                    output_dir=str(app_dir / "enhanced_output")
                )
                print("🔍 DEBUG: Enhanced Voice Converter 初期化成功")
            except ImportError as init_import_error:
                raise Exception(f"🚨 RVC依存関係エラー: {init_import_error}\n💡 解決方法: 必要な依存ライブラリをインストールしてください。")
            except RuntimeError as init_runtime_error:
                raise Exception(f"🚨 Enhanced Voice Converter初期化エラー: {init_runtime_error}")
            except Exception as init_error:
                raise Exception(f"🚨 初期化中に予期しないエラーが発生: {init_error}")
            
            # 一時ファイルを作成して音声変換を実行
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_input:
                temp_input_path = temp_input.name
                sf.write(temp_input_path, audio, sr)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            try:
                # 利用可能なモデル一覧を取得
                print("🔍 DEBUG: モデル一覧取得開始...")
                models = converter.list_available_models()
                print(f"🔍 DEBUG: 検出されたモデル数: {len(models)}")
                if not models:
                    raise Exception("利用可能な音声モデルが見つかりません")
                
                # 最初のモデルを使用
                selected_model = models[0]
                print(f"🔍 DEBUG: 選択されたモデル: {selected_model['name']}")
                print(f"🔍 DEBUG: モデルパス: {selected_model['path']}")
                
                # モデルを読み込み
                print("🔍 DEBUG: モデル読み込み開始...")
                load_result = converter.load_model(
                    selected_model['path'],
                    selected_model.get('index_path'),
                    self.params.get('index_rate', 0.7)
                )
                print(f"🔍 DEBUG: モデル読み込み結果: {load_result}")
                
                # 音声変換実行
                print("🔍 DEBUG: 音声変換実行開始...")
                print(f"🔍 DEBUG: 入力パス: {temp_input_path}")
                print(f"🔍 DEBUG: 出力パス: {temp_output_path}")
                print(f"🔍 DEBUG: パラメータ: pitch={self.params.get('pitch', 0)}, index_rate={self.params.get('index_rate', 0.7)}")
                
                # コンバーターオブジェクトの詳細確認
                print(f"🔍 URGENT DEBUG: converter type: {type(converter)}")
                print(f"🔍 URGENT DEBUG: converter.__class__.__name__: {converter.__class__.__name__}")
                print(f"🔍 URGENT DEBUG: converter.convert_audio method: {converter.convert_audio}")
                print(f"🔍 URGENT DEBUG: hasattr(converter, 'convert_audio'): {hasattr(converter, 'convert_audio')}")
                
                # 入力ファイルの存在確認
                if not Path(temp_input_path).exists():
                    raise Exception(f"入力ファイルが存在しません: {temp_input_path}")
                print(f"🔍 DEBUG: 入力ファイル確認OK - サイズ: {Path(temp_input_path).stat().st_size} bytes")
                
                print("🔍 URGENT DEBUG: convert_audio呼び出し直前!!!")
                result_path = converter.convert_audio(
                    input_path=temp_input_path,
                    output_path=temp_output_path,
                    f0_up_key=self.params.get('pitch', 0),
                    filter_radius=self.params.get('filter_radius', 3),
                    index_rate=self.params.get('index_rate', 0.7),
                    f0_method="rmvpe"
                )
                print(f"🔍 DEBUG: 音声変換結果パス: {result_path}")
                print(f"🔍 DEBUG: 結果パスtype: {type(result_path)}")
                
                if result_path:
                    print(f"🔍 DEBUG: convert_audio成功 - result_path: {result_path}")
                    
                    # result_pathが実際にファイルパスを指しているか確認
                    if Path(result_path).exists():
                        output_size = Path(result_path).stat().st_size
                        print(f"🔍 DEBUG: 結果ファイル確認OK - サイズ: {output_size} bytes")
                        if output_size > 0:
                            # 変換された音声を読み込み
                            print("🔍 DEBUG: 変換結果音声読み込み開始...")
                            converted_audio, _ = sf.read(result_path)
                            print(f"🔍 DEBUG: 読み込み完了 - shape: {converted_audio.shape}")
                            return converted_audio
                        else:
                            raise Exception(f"結果ファイルが空です: {result_path}")
                    else:
                        # result_pathで指定されたファイルが存在しない場合、temp_output_pathを確認
                        print(f"🔍 DEBUG: result_pathのファイルが見つからない、temp_output_pathを確認: {temp_output_path}")
                        if Path(temp_output_path).exists():
                            output_size = Path(temp_output_path).stat().st_size
                            print(f"🔍 DEBUG: temp出力ファイル確認OK - サイズ: {output_size} bytes")
                            if output_size > 0:
                                # 変換された音声を読み込み
                                print("🔍 DEBUG: temp変換結果音声読み込み開始...")
                                converted_audio, _ = sf.read(temp_output_path)
                                print(f"🔍 DEBUG: temp読み込み完了 - shape: {converted_audio.shape}")
                                return converted_audio
                            else:
                                raise Exception(f"temp出力ファイルが空です: {temp_output_path}")
                        else:
                            raise Exception(f"出力ファイルが作成されていません: result_path={result_path}, temp_output_path={temp_output_path}")
                else:
                    raise Exception("音声変換に失敗しました（result_pathがNone）")
                    
            finally:
                # 一時ファイルを削除
                try:
                    os.unlink(temp_input_path)
                    os.unlink(temp_output_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"🔍 DEBUG: RVC変換でエラー発生: {e}")
            import traceback
            print(f"🔍 DEBUG: 詳細トレースバック: {traceback.format_exc()}")
            raise Exception(f"Enhanced Voice Converter使用中にエラー: {e}")
    
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
        self.index_slider.setValue(70)
        self.index_label = QLabel("0.70")
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
            input_file, output_file, self.current_model['path'], params, self.model_dir
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