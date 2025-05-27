#!/usr/bin/env python3
"""
gui_dark_mode.py の修正パッチ
run_conversion メソッドの修正版
"""

def run_conversion_fixed(self):
    """実際の変換処理（修正版）"""
    try:
        # CLI経由で変換を実行
        self.root.after(0, lambda: self.status_label.config(text="Starting conversion..."))
        self.root.after(0, lambda: self.log_message("Starting conversion process..."))
        
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
        
        # モデルパス設定
        model_id = self.model_info.get('folder') or ''
        model_path = os.path.join(self.model_dir, model_id) if model_id else os.path.dirname(self.model_info['file'])
        
        # インデックスファイル検索
        index_file = self.model_info.get('index_file')
        if not index_file and os.path.exists(model_path):
            index_files = [f for f in os.listdir(model_path) if f.endswith('.index')]
            if index_files:
                index_file = os.path.join(model_path, index_files[0])
        
        # Hubertモデル
        hubert_path = os.path.join(self.model_dir, "hubert_base.pt")
        if not os.path.exists(hubert_path):
            alt_hubert = os.path.join(project_dir, "model_dir", "hubert_base.pt")
            if os.path.exists(alt_hubert):
                hubert_path = alt_hubert
        
        # rmvpe.ptのパスを確認
        rmvpe_path = os.path.join(self.model_dir, "rmvpe.pt")
        if not os.path.exists(rmvpe_path):
            alt_rmvpe = os.path.join(project_dir, "model_dir", "rmvpe.pt")
            if os.path.exists(alt_rmvpe):
                rmvpe_path = os.path.dirname(alt_rmvpe)
            else:
                rmvpe_path = self.model_dir
        else:
            rmvpe_path = os.path.dirname(rmvpe_path)
        
        # コマンドを配列として構築
        cmd = [
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
        
        # インデックスファイルがある場合
        if index_file and os.path.exists(index_file):
            cmd.extend(["-if", index_file])
        
        # Hubertモデルパス
        if os.path.exists(hubert_path):
            cmd.extend(["--hubert_model_path", hubert_path])
        
        # 環境変数の設定（重要：rmvpe_rootを追加）
        env = os.environ.copy()
        env['PYTHONPATH'] = project_dir
        env['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # M1/M2 Mac対応
        env['rmvpe_root'] = rmvpe_path  # 修正：正しいパスを設定
        env['PYTHONUNBUFFERED'] = '1'
        
        # デバッグ情報をログに記録
        self.root.after(0, lambda: self.log_message(f"Working directory: {project_dir}"))
        self.root.after(0, lambda: self.log_message(f"rmvpe_root: {rmvpe_path}"))
        self.root.after(0, lambda: self.log_message(f"Model path: {self.model_info['file']}"))
        if index_file:
            self.root.after(0, lambda: self.log_message(f"Index file: {index_file}"))
        
        # プロセスの実行
        self.root.after(0, lambda: self.status_label.config(text="Processing audio..."))
        
        # subprocess.Popenを使用
        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=project_dir,
            bufsize=1,
            universal_newlines=True
        )
        
        # 標準出力と標準エラーを並行して読み取る
        import select
        import fcntl
        
        # ノンブロッキングに設定
        def set_nonblocking(fd):
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        set_nonblocking(self.current_process.stdout.fileno())
        set_nonblocking(self.current_process.stderr.fileno())
        
        output_data = []
        error_data = []
        
        while True:
            # プロセスが終了したかチェック
            if self.current_process.poll() is not None:
                break
            
            # 読み取り可能なストリームを選択
            ready, _, _ = select.select(
                [self.current_process.stdout, self.current_process.stderr],
                [], [], 0.1
            )
            
            for stream in ready:
                try:
                    if stream == self.current_process.stdout:
                        line = stream.readline()
                        if line:
                            output_data.append(line.strip())
                            self.root.after(0, lambda msg=line.strip(): self.log_message(msg))
                            
                            # 進捗状況を更新
                            if "Loading" in line:
                                self.root.after(0, lambda: self.status_label.config(text="Loading models..."))
                            elif "Estimating f0" in line:
                                self.root.after(0, lambda: self.status_label.config(text="Analyzing pitch..."))
                            elif "inference" in line.lower():
                                self.root.after(0, lambda: self.status_label.config(text="Converting voice..."))
                                
                    elif stream == self.current_process.stderr:
                        line = stream.readline()
                        if line:
                            error_data.append(line.strip())
                            # エラーでない警告は通常のログとして表示
                            if "UserWarning" in line or "is deprecated" in line:
                                self.root.after(0, lambda msg=line.strip(): self.log_message(msg, "WARNING"))
                            else:
                                self.root.after(0, lambda msg=line.strip(): self.log_message(msg, "ERROR"))
                except:
                    pass
            
            # UIをレスポンシブに保つ
            self.root.update_idletasks()
        
        # 残りの出力を取得
        stdout_remaining, stderr_remaining = self.current_process.communicate()
        if stdout_remaining:
            for line in stdout_remaining.splitlines():
                output_data.append(line)
                self.root.after(0, lambda msg=line: self.log_message(msg))
        if stderr_remaining:
            for line in stderr_remaining.splitlines():
                error_data.append(line)
                self.root.after(0, lambda msg=line: self.log_message(msg, "WARNING"))
        
        # 結果を確認
        returncode = self.current_process.returncode
        
        if returncode == 0 and os.path.exists(self.output_file_path):
            # 成功
            file_size = os.path.getsize(self.output_file_path)
            self.log_message(f"Conversion completed successfully. Output file size: {file_size} bytes", "SUCCESS")
            self.root.after(0, self.conversion_complete)
        else:
            # エラー
            error_msg = "\n".join(error_data[-10:]) if error_data else "Conversion failed"
            
            # 特定のエラーメッセージをチェック
            for line in error_data:
                if "rmvpe_root" in line:
                    error_msg = "RMVPE model path not found. Please check model_dir/rmvpe.pt exists."
                    break
                elif "ModuleNotFoundError" in line:
                    error_msg = "Missing dependencies. Please run: poetry install"
                    break
                    
            self.log_message(f"Conversion failed: {error_msg}", "ERROR")
            self.root.after(0, lambda: self.conversion_error(error_msg))
            
    except Exception as e:
        # エラー処理
        error_msg = f"Conversion failed: {str(e)}"
        import traceback
        self.log_message(f"{error_msg}\n{traceback.format_exc()}", "ERROR")
        self.root.after(0, lambda: self.conversion_error(error_msg))
        
    finally:
        self.current_process = None
