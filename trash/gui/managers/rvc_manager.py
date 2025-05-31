"""
RVC実行マネージャー
音声変換の実行とプログレス管理
"""
import os
import sys
import subprocess
import threading
import time
from datetime import datetime


class RVCManager:
    """RVC実行とプログレス管理を担当するマネージャー"""
    
    def __init__(self, base_dir, model_dir, config_dir=None):
        self.base_dir = base_dir
        self.model_dir = model_dir
        self.config_dir = config_dir or os.path.join(base_dir, "configs")
        
        # 高品質設定のデフォルト値
        self.default_params = {
            "f0method": "rmvpe",
            "index_rate": 1.0,
            "filter_radius": 7,
            "protect": 0.33,
            "rms_mix_rate": 0.0,
        }
        
        # プロジェクトディレクトリの検出
        self.project_dir = self.detect_project_directory()
        
    def detect_project_directory(self):
        """プロジェクトディレクトリを検出"""
        project_dir = self.base_dir
        
        # macOSアプリバンドル内の場合
        if project_dir.endswith('/Resources'):
            possible_dirs = [
                "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion",
                os.path.expanduser("~/Retrieval-based-Voice-Conversion"),
            ]
            for dir_path in possible_dirs:
                if os.path.exists(os.path.join(dir_path, "pyproject.toml")):
                    project_dir = dir_path
                    break
                    
        return project_dir
        
    def build_command(self, model_info, input_file, output_file, pitch=0, **custom_params):
        """RVCコマンドを構築"""
        # パラメータをマージ
        params = {**self.default_params, **custom_params}
        
        # モデルファイルパス
        model_file = model_info['file']
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"モデルファイルが見つかりません: {model_file}")
        
        # インデックスファイル
        index_file = model_info.get('index_file')
        
        # Hubertモデル
        hubert_path = os.path.join(self.model_dir, "hubert_base.pt")
        if not os.path.exists(hubert_path):
            print(f"Warning: Hubertモデルが見つかりません: {hubert_path}")
        
        # CLIコマンド構築
        cmd = [
            f'cd "{self.project_dir}"',
            "&&",
            "poetry", "run", "rvc", "infer",
            "-m", f'"{model_file}"',
            "-i", f'"{input_file}"',
            "-o", f'"{output_file}"',
            "-fu", str(pitch),
            "-fm", params["f0method"],
            "-ir", str(params["index_rate"]),
            "-fr", str(params["filter_radius"]),
            "-p", str(params["protect"]),
            "-rmr", str(params["rms_mix_rate"])
        ]
        
        # インデックスファイルが存在する場合
        if index_file and os.path.exists(index_file):
            cmd.extend(["-if", f'"{index_file}"'])
            
        # Hubertモデルが存在する場合
        if os.path.exists(hubert_path):
            cmd.extend(["--hubert_model_path", f'"{hubert_path}"'])
        
        return " ".join(cmd)
        
    def run_with_progress(self, model_info, input_file, output_file, progress_callback=None, pitch=0, **params):
        """プログレス監視付きでRVCを実行"""
        def run_in_thread():
            try:
                # プログレス更新
                if progress_callback:
                    progress_callback(0, 0, "プロジェクトとモデルの初期化中...")
                
                # 出力ディレクトリの作成
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                if progress_callback:
                    progress_callback(0, 100, "初期化完了")
                
                # コマンド構築
                cmd = self.build_command(model_info, input_file, output_file, pitch, **params)
                
                if progress_callback:
                    progress_callback(1, 0, "音声ファイルとモデルデータを読み込み中...")
                
                # 環境変数設定
                env = os.environ.copy()
                env['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                env['MODEL_DIR'] = self.model_dir
                
                if progress_callback:
                    progress_callback(1, 100, "データ読み込み完了")
                    progress_callback(2, 0, "音声データの前処理を開始...")
                
                # プロセス実行
                cmd_array = cmd.split()
                self._run_rvc_with_progress(cmd_array, env, progress_callback)
                
                # 結果確認
                if os.path.exists(output_file):
                    if progress_callback:
                        progress_callback(6, 100, "変換完了！")
                    return True, "変換が正常に完了しました"
                else:
                    return False, "出力ファイルの生成に失敗しました"
                    
            except Exception as e:
                error_msg = str(e)
                return False, error_msg
                
        # スレッドで実行
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()
        return thread
        
    def _run_rvc_with_progress(self, cmd_array, env, progress_callback):
        """RVC推論をプログレス追跡しながら実行"""
        if not progress_callback:
            # プログレスコールバックがない場合は通常実行
            subprocess.run(cmd_array, env=env, cwd=self.project_dir)
            return
            
        # ステージ3: 特徴抽出を開始
        progress_callback(3, 0, "音声の特徴を抽出中...")
        
        process = subprocess.Popen(
            cmd_array,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env,
            cwd=self.project_dir
        )
        
        current_stage = 3  # 特徴抽出ステージ
        stage_progress = {3: 0, 4: 0, 5: 0}  # 各ステージの進捗を保持
        line_count = 0
        
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.strip()
                if line:
                    line_count += 1
                    
                    # RVCの処理段階を詳細に解析
                    # 1. 音声読み込み段階
                    if "load_audio" in line or "Loading audio" in line:
                        if stage_progress[3] < 10:
                            stage_progress[3] = 10
                            progress_callback(3, 10, "音声ファイルを読み込み中...")
                    
                    # 2. モデル読み込み段階
                    elif any(keyword in line for keyword in ["Loading model", "load model", "Loading checkpoint"]):
                        if stage_progress[3] < 25:
                            stage_progress[3] = 25
                            progress_callback(3, 25, "AIモデルを読み込み中...")
                    
                    # 3. Hubert特徴抽出
                    elif any(keyword in line for keyword in ["hubert", "Hubert", "extract_feature", "extracting features"]):
                        if stage_progress[3] < 60:
                            stage_progress[3] = 60
                            progress_callback(3, 60, "音声特徴を抽出中...")
                    
                    # 4. F0（ピッチ）推定
                    elif any(keyword in line for keyword in ["f0", "F0", "pitch", "rmvpe", "get_f0"]):
                        if stage_progress[3] < 85:
                            stage_progress[3] = 85
                            progress_callback(3, 85, "ピッチを解析中...")
                    
                    # 5. 推論開始（音声変換）
                    elif any(keyword in line for keyword in ["infer", "Inferring", "inference", "vc start"]):
                        if current_stage < 4:
                            stage_progress[3] = 100
                            progress_callback(3, 100, "特徴抽出完了")
                            current_stage = 4
                            stage_progress[4] = 10
                            progress_callback(4, 10, "音声変換を開始...")
                    
                    # 6. 変換処理中
                    elif any(keyword in line for keyword in ["Converting", "Processing", "net_g.infer"]):
                        if current_stage == 4 and stage_progress[4] < 70:
                            stage_progress[4] = 70
                            progress_callback(4, 70, "AIで音声を変換中...")
                    
                    # 7. 後処理
                    elif any(keyword in line for keyword in ["tgt_sr", "resample", "Resampling"]):
                        if current_stage == 4 and stage_progress[4] < 90:
                            stage_progress[4] = 90
                            progress_callback(4, 90, "音声をリサンプリング中...")
                    
                    # 8. 保存処理
                    elif any(keyword in line for keyword in ["write", "Write", "save", "Save", "sf.write"]):
                        if current_stage < 5:
                            stage_progress[4] = 100
                            progress_callback(4, 100, "音声変換完了")
                            current_stage = 5
                            stage_progress[5] = 50
                            progress_callback(5, 50, "ファイルを保存中...")
                    
                    # 9. 処理時間の記録
                    elif "npy:" in line or "f0:" in line or "infer:" in line:
                        if "npy:" in line:
                            progress_callback(current_stage, stage_progress[current_stage], "特徴抽出時間を記録...")
                        elif "f0:" in line:
                            progress_callback(current_stage, stage_progress[current_stage], "ピッチ推定時間を記録...")
                        elif "infer:" in line:
                            progress_callback(current_stage, stage_progress[current_stage], "推論時間を記録...")
                    
                    # 10. 完了メッセージ
                    elif any(keyword in line for keyword in ["Success", "successfully", "finished", "complete"]):
                        if current_stage == 5:
                            stage_progress[5] = 95
                            progress_callback(5, 95, "処理がほぼ完了...")
                    
                    # 進捗の自動増加（長時間処理対応）
                    if line_count % 5 == 0:  # 5行ごとに微増
                        if current_stage in stage_progress:
                            current = stage_progress[current_stage]
                            if current < 95:  # 95%まで
                                increment = 2 if current < 50 else 1
                                new_progress = min(current + increment, 95)
                                if new_progress > current:
                                    stage_progress[current_stage] = new_progress
                                    messages = {
                                        3: "特徴を解析中...",
                                        4: "音声を変換中...",
                                        5: "最終処理中..."
                                    }
                                    progress_callback(current_stage, new_progress, messages.get(current_stage, "処理中..."))
        
        process.wait()
        
        # エラーチェック
        if process.returncode != 0:
            error_msg = f"RVC inference failed with return code: {process.returncode}"
            raise RuntimeError(error_msg)
        
        # 処理完了を確認
        if current_stage == 3:
            progress_callback(3, 100, "特徴抽出完了")
            progress_callback(4, 100, "音声変換完了")
        elif current_stage == 4:
            progress_callback(4, 100, "音声変換完了")
            
        progress_callback(5, 100, "最適化完了")
        
    def generate_output_filename(self, input_file, model_name, custom_name=None):
        """出力ファイル名を生成"""
        # 入力ファイル名を取得
        input_name = os.path.splitext(os.path.basename(input_file))[0]
        
        # モデル名から安全なファイル名を作成
        safe_model_name = model_name
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '(', ')', '\n', '\r', '\t']:
            safe_model_name = safe_model_name.replace(char, '_')
        safe_model_name = '_'.join(filter(None, safe_model_name.split('_')))
        
        if custom_name and custom_name.strip():
            # カスタム名のバリデーション
            invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
            if any(char in custom_name for char in invalid_chars):
                raise ValueError("ファイル名に無効な文字が含まれています")
            # カスタム名を使用する場合でも {元ファイル名}_{モデル名}_{カスタム名}.wav の形式
            return f"{input_name}_{safe_model_name}_{custom_name.strip()}.wav"
        else:
            # 基本形式: {元ファイル名}_{モデル名}.wav
            return f"{input_name}_{safe_model_name}.wav"