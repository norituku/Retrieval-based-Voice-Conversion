#!/usr/bin/env python3
"""
RVC Dark Mode GUI - プログレスバー統合版
既存のDark Mode GUIにプログレスバーを統合
"""

# 既存のgui_dark_mode.pyの内容をインポート
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 既存のGUIをインポート
from gui_dark_mode import DarkModeGUI
from progress_integration import ProgressBarIntegration
from utils.progress_tracker import ProcessingStage
import subprocess
import threading
import time


class DarkModeGUIWithProgress(DarkModeGUI):
    """プログレスバー統合版のDark Mode GUI"""
    
    def __init__(self, root):
        super().__init__(root)
        self.progress_integration = None
        
    def run_conversion(self):
        """実際の変換処理（プログレスバー付き）"""
        try:
            # プログレスバーの初期化
            self.progress_integration = ProgressBarIntegration(self)
            self.progress_integration.create_progress_window()
            tracker = self.progress_integration.get_tracker()
            
            # 変換処理を別スレッドで実行
            def conversion_thread():
                try:
                    # 1. 初期化
                    tracker.start_stage(ProcessingStage.INITIALIZATION)
                    self.root.after(0, lambda: self.status_label.config(text="Initializing..."))
                    
                    # プロジェクトディレクトリを確認
                    project_dir = self.base_dir
                    if project_dir.endswith('/Resources'):
                        possible_dirs = [
                            "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion",
                            os.path.expanduser("~/Retrieval-based-Voice-Conversion"),
                        ]
                        for dir_path in possible_dirs:
                            if os.path.exists(os.path.join(dir_path, "pyproject.toml")):
                                project_dir = dir_path
                                break
                    
                    tracker.complete_stage()
                    
                    # 2. データ読み込み
                    tracker.start_stage(ProcessingStage.DATA_LOADING)
                    
                    # モデルパス設定
                    model_id = self.model_info.get('folder') or ''
                    model_path = os.path.join(self.model_dir, model_id) if model_id else os.path.dirname(self.model_info['file'])
                    
                    # インデックスファイル検索
                    index_file = self.model_info.get('index_file')
                    if not index_file and os.path.exists(model_path):
                        index_files = [f for f in os.listdir(model_path) if f.endswith('.index')]
                        if index_files:
                            index_file = os.path.join(model_path, index_files[0])
                    
                    tracker.complete_stage()
                    
                    # 3. 前処理
                    tracker.start_stage(ProcessingStage.PREPROCESSING)
                    
                    # Hubertモデル
                    hubert_path = os.path.join(self.model_dir, "hubert_base.pt")
                    if not os.path.exists(hubert_path):
                        alt_hubert = os.path.join(project_dir, "model_dir", "hubert_base.pt")
                        if os.path.exists(alt_hubert):
                            hubert_path = alt_hubert
                    
                    # コマンド構築
                    cmd_array = [
                        "poetry", "run", "rvc", "infer",
                        "-m", self.model_info["file"],
                        "-i", self.input_var.get(),
                        "-o", self.output_file_path,
                        "-fu", str(self.pitch_var.get()),
                        "-fm", self.f0_method_var.get(),
                        "-ir", str(self.index_rate_var.get()),
                        "-fr", str(self.filter_radius_var.get()),
                        "-p", str(self.protect_var.get()),
                        "-rmr", str(self.rms_mix_rate_var.get())
                    ]
                    
                    if index_file and os.path.exists(index_file):
                        cmd_array.extend(["-if", index_file])
                    
                    if os.path.exists(hubert_path):
                        cmd_array.extend(["--hubert_model_path", hubert_path])
                    
                    # 環境変数の設定
                    env = os.environ.copy()
                    env['PYTHONPATH'] = project_dir
                    env['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                    env['rmvpe_root'] = os.path.join(
                        self.model_dir if os.path.exists(os.path.join(self.model_dir, 'rmvpe.pt')) 
                        else os.path.join(project_dir, 'model_dir')
                    )
                    
                    tracker.complete_stage()
                    
                    # 4-6. RVC推論の実行
                    self._run_rvc_with_progress(cmd_array, env, tracker)
                    
                    # 7. 出力保存
                    tracker.start_stage(ProcessingStage.SAVING_OUTPUT)
                    time.sleep(0.5)  # 保存処理のシミュレーション
                    tracker.complete_stage()
                    
                    # 完了
                    self.root.after(0, lambda: self.on_conversion_complete())
                    time.sleep(1.5)  # 完了表示を見せる
                    
                except Exception as e:
                    self.root.after(0, lambda: self.on_conversion_error(str(e)))
                finally:
                    # プログレスバーを閉じる
                    self.root.after(0, lambda: self.progress_integration.close())
                    
            # スレッドを開始
            thread = threading.Thread(target=conversion_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.on_conversion_error(str(e))
            if self.progress_integration:
                self.progress_integration.close()
            
    def _run_rvc_with_progress(self, cmd_array, env, tracker):
        """RVC推論をプログレス追跡しながら実行"""
        
        # 特徴抽出段階
        tracker.start_stage(ProcessingStage.FEATURE_EXTRACTION)
        
        # プロセスを開始
        process = subprocess.Popen(
            cmd_array,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env,
            cwd=os.path.dirname(self.base_dir) if self.base_dir.endswith('/Resources') else self.base_dir
        )
        
        # 出力を監視しながら進捗を更新
        current_stage = ProcessingStage.FEATURE_EXTRACTION
        line_count = 0
        
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.strip()
                if line:
                    self.log_message(line)
                    line_count += 1
                    
                    # 進捗の推定（実際のRVC出力に基づいて調整）
                    if "Loading" in line or "loading" in line:
                        tracker.update_stage_progress(0.3)
                    elif "Extract" in line or "extract" in line:
                        tracker.update_stage_progress(0.7)
                    elif "Process" in line or "process" in line:
                        if current_stage != ProcessingStage.MODEL_INFERENCE:
                            tracker.complete_stage()
                            tracker.start_stage(ProcessingStage.MODEL_INFERENCE)
                            current_stage = ProcessingStage.MODEL_INFERENCE
                        tracker.update_stage_progress(0.5)
                    elif "Generate" in line or "generate" in line:
                        tracker.update_stage_progress(0.8)
                    elif "Save" in line or "save" in line or "Write" in line or "write" in line:
                        if current_stage != ProcessingStage.POSTPROCESSING:
                            tracker.complete_stage()
                            tracker.start_stage(ProcessingStage.POSTPROCESSING)
                            current_stage = ProcessingStage.POSTPROCESSING
                        tracker.update_stage_progress(0.9)
                    
                    # 一般的な進捗更新（行数に基づく）
                    if current_stage == ProcessingStage.FEATURE_EXTRACTION and line_count % 5 == 0:
                        progress = min(0.9, line_count / 50.0)
                        tracker.update_stage_progress(progress)
                    elif current_stage == ProcessingStage.MODEL_INFERENCE and line_count % 3 == 0:
                        progress = min(0.9, (line_count - 50) / 30.0)
                        tracker.update_stage_progress(progress)
                        
        # プロセスの完了を待つ
        process.wait()
        
        # 現在のステージを完了
        if current_stage == ProcessingStage.FEATURE_EXTRACTION:
            tracker.complete_stage()
            tracker.start_stage(ProcessingStage.MODEL_INFERENCE)
            tracker.complete_stage()
            tracker.start_stage(ProcessingStage.POSTPROCESSING)
        elif current_stage == ProcessingStage.MODEL_INFERENCE:
            tracker.complete_stage()
            tracker.start_stage(ProcessingStage.POSTPROCESSING)
            
        tracker.complete_stage()
        
        # エラーチェック
        if process.returncode != 0:
            raise RuntimeError("RVC inference failed")
            
    def on_conversion_complete(self):
        """変換完了時の処理"""
        self.status_label.config(text="✅ Conversion completed!")
        self.convert_button.config(state='normal')
        self.open_output_button.config(state='normal')
        
    def on_conversion_error(self, error_message):
        """変換エラー時の処理"""
        self.status_label.config(text=f"❌ Error: {error_message}")
        self.convert_button.config(state='normal')
        self.log_message(f"ERROR: {error_message}")


def main():
    """メイン関数"""
    import tkinter as tk
    
    root = tk.Tk()
    app = DarkModeGUIWithProgress(root)
    root.mainloop()


if __name__ == "__main__":
    main()