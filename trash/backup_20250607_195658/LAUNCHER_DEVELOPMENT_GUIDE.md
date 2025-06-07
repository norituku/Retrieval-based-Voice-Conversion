# Voice Converter 起動スクリプト関連 開発手順書

## 目次
1. [概要](#1-概要)
2. [関連ファイルの構成](#2-関連ファイルの構成)
3. [起動スクリプトの開発](#3-起動スクリプトの開発)
4. [GUIアプリケーションの開発](#4-guiアプリケーションの開発)
5. [音声変換処理の実装](#5-音声変換処理の実装)
6. [ビルドと配布](#6-ビルドと配布)
7. [トラブルシューティング](#7-トラブルシューティング)

---

## 1. 概要

### 1.1 プロジェクトの目的
`launch_voice_converter.sh`を中心とした、Voice ConverterのmacOSデスクトップアプリケーション開発に特化した手順書です。

### 1.2 開発フロー
```
launch_voice_converter.sh
    ↓ 起動
gui_dark_mode.py
    ↓ 音声変換要求
run_inference.py
    ↓ RVC呼び出し
rvc_config.py (設定)
    ↓ 実行
音声ファイル出力
```

### 1.3 必要な環境
- macOS 10.15以降
- Python 3.11.9（推奨）または Python 3.9.6
- Poetry（依存関係管理）
- Nuitka（ビルドツール）

---

## 2. 関連ファイルの構成

### 2.1 ファイル一覧と役割

```
Retrieval-based-Voice-Conversion/
├── launch_voice_converter.sh    # メイン起動スクリプト
├── gui_dark_mode.py             # GUIアプリケーション本体
├── run_inference.py             # 音声変換実行スクリプト
├── rvc_config.py                # RVC設定ファイル
├── gui_settings.json            # GUI設定ファイル
├── build_mac_app.sh             # macOSアプリビルドスクリプト
├── model_dir/                   # モデルファイル格納ディレクトリ
└── dist/                        # ビルド成果物出力先
    └── Voice Converter.app      # 最終的なアプリケーション
```

### 2.2 各ファイルの詳細

#### launch_voice_converter.sh
```bash
#!/bin/bash
# Voice Converter 起動スクリプト（正しいPython環境を使用）

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Voice Converter を起動中..."

# 環境変数を設定
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PYOBJC_DISABLE_GIL_VALIDATION=1
export TK_SILENCE_DEPRECATION=1

# 正しいPython環境（3.11.9）でgui_dark_modeを起動
echo "Python 3.11.9環境で起動します..."
/usr/local/bin/python3 gui_dark_mode.py "$@"
```

#### gui_settings.json
```json
{
  "model_directory": "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/model_dir"
}
```

---

## 3. 起動スクリプトの開発

### 3.1 改良版起動スクリプトの実装

#### 改良版 launch_voice_converter.sh
```bash
#!/bin/bash
# Voice Converter 起動スクリプト - 改良版
# Python環境を自動検出し、適切な設定で起動する

set -e  # エラー時に即座に終了

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ログファイルの設定
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/voice_converter_$(date +%Y%m%d_%H%M%S).log"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "===== Voice Converter 起動開始 ====="

# Python環境の検出
detect_python() {
    # 優先順位でPythonを検索
    PYTHON_PATHS=(
        "/usr/local/bin/python3.11"
        "/usr/local/bin/python3"
        "/opt/homebrew/bin/python3.11"
        "/opt/homebrew/bin/python3"
        "/usr/bin/python3"
    )
    
    for python_path in "${PYTHON_PATHS[@]}"; do
        if [ -x "$python_path" ]; then
            version=$("$python_path" --version 2>&1 | cut -d' ' -f2)
            log "Python found: $python_path (version $version)"
            echo "$python_path"
            return 0
        fi
    done
    
    log "ERROR: Python 3が見つかりません"
    return 1
}

# 環境変数の設定
setup_environment() {
    # macOS固有の環境変数
    export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
    export PYOBJC_DISABLE_GIL_VALIDATION=1
    export TK_SILENCE_DEPRECATION=1
    
    # オーディオ関連の環境変数
    export AUDIODEV=coreaudio
    export SDL_AUDIODRIVER=coreaudio
    
    # Tkinter関連
    export TCL_LIBRARY="/usr/local/lib/tcl8.6"
    export TK_LIBRARY="/usr/local/lib/tk8.6"
    
    log "環境変数を設定しました"
}

# 依存関係のチェック
check_dependencies() {
    log "依存関係をチェック中..."
    
    # 必要なPythonモジュールのチェック
    "$PYTHON_CMD" -c "
import sys
modules = ['tkinter', 'json', 'subprocess', 'threading', 'pathlib']
missing = []
for module in modules:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)
if missing:
    print(f'Missing modules: {missing}')
    sys.exit(1)
" 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        log "ERROR: 必要なPythonモジュールが不足しています"
        return 1
    fi
    
    log "すべての依存関係が満たされています"
}

# メイン処理
main() {
    # Python実行コマンドを検出
    PYTHON_CMD=$(detect_python)
    if [ $? -ne 0 ]; then
        osascript -e 'display alert "エラー" message "Python 3が見つかりません。Homebrewなどでインストールしてください。"'
        exit 1
    fi
    
    # 環境設定
    setup_environment
    
    # 依存関係チェック
    if ! check_dependencies; then
        osascript -e 'display alert "エラー" message "必要なPythonモジュールが不足しています。ログを確認してください。"'
        exit 1
    fi
    
    # GUI起動
    log "Voice Converter GUIを起動します..."
    "$PYTHON_CMD" "$SCRIPT_DIR/gui_dark_mode.py" "$@" 2>&1 | tee -a "$LOG_FILE"
    
    # 終了コードを取得
    exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        log "Voice Converter が正常に終了しました"
    else
        log "Voice Converter がエラーで終了しました (exit code: $exit_code)"
        osascript -e 'display alert "エラー" message "Voice Converterが異常終了しました。ログファイルを確認してください。"'
    fi
    
    exit $exit_code
}

# トラップ設定（異常終了時のクリーンアップ）
trap 'log "スクリプトが中断されました"' INT TERM

# メイン処理を実行
main "$@"
```

### 3.2 起動スクリプトの権限設定

```bash
# 実行権限を付与
chmod +x launch_voice_converter.sh

# 所有者の確認と修正
ls -la launch_voice_converter.sh
# 必要に応じて所有者を変更
# chown $(whoami) launch_voice_converter.sh
```

### 3.3 デスクトップショートカットの作成

```bash
# Automatorアプリケーションの作成スクリプト
cat > create_launcher_app.sh << 'EOF'
#!/bin/bash

# Voice Converter.appを作成
APP_NAME="Voice Converter"
APP_DIR="$HOME/Desktop/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# ディレクトリ構造を作成
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

# 実行スクリプトを作成
cat > "$MACOS_DIR/$APP_NAME" << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")/../../../Retrieval-based-Voice-Conversion"
./launch_voice_converter.sh
SCRIPT

chmod +x "$MACOS_DIR/$APP_NAME"

# Info.plistを作成
cat > "$CONTENTS_DIR/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Voice Converter</string>
    <key>CFBundleIdentifier</key>
    <string>com.rvc.voiceconverter</string>
    <key>CFBundleName</key>
    <string>Voice Converter</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
PLIST

echo "Voice Converter.app created on Desktop"
EOF

chmod +x create_launcher_app.sh
./create_launcher_app.sh
```

---

## 4. GUIアプリケーションの開発

### 4.1 gui_dark_mode.pyの基本構造

```python
#!/usr/bin/env python3
"""
Voice Converter Dark Mode GUI
メインアプリケーションインターフェース
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import subprocess
import threading
from pathlib import Path
import time

class VoiceConverterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Converter")
        
        # 設定の読み込み
        self.load_settings()
        
        # UIの初期化
        self.setup_ui()
        
        # 変換プロセスの状態
        self.conversion_process = None
        self.is_converting = False
        
    def load_settings(self):
        """設定ファイルの読み込み"""
        settings_path = Path(__file__).parent / "gui_settings.json"
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                "model_directory": str(Path(__file__).parent / "model_dir")
            }
            self.save_settings()
    
    def save_settings(self):
        """設定の保存"""
        settings_path = Path(__file__).parent / "gui_settings.json"
        with open(settings_path, 'w') as f:
            json.dump(self.settings, f, indent=2)
```

### 4.2 ダークモードUIの実装

```python
def setup_ui(self):
    """ダークモードUIのセットアップ"""
    # ダークテーマの設定
    self.setup_dark_theme()
    
    # メインフレーム
    main_frame = ttk.Frame(self.root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # タイトル
    title_label = ttk.Label(
        main_frame, 
        text="🎤 Voice Converter", 
        font=('SF Pro Display', 24, 'bold')
    )
    title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
    
    # ファイル選択セクション
    self.create_file_section(main_frame)
    
    # モデル選択セクション
    self.create_model_section(main_frame)
    
    # パラメータセクション
    self.create_parameters_section(main_frame)
    
    # コントロールセクション
    self.create_control_section(main_frame)
    
    # ログセクション
    self.create_log_section(main_frame)
    
def setup_dark_theme(self):
    """ダークテーマの設定"""
    style = ttk.Style()
    
    # カラーパレット
    colors = {
        'bg': '#1a1a1a',
        'fg': '#ffffff',
        'select_bg': '#404040',
        'select_fg': '#ffffff',
        'button_bg': '#404040',
        'button_fg': '#ffffff',
        'entry_bg': '#2a2a2a',
        'entry_fg': '#ffffff',
    }
    
    # ウィンドウ背景
    self.root.configure(bg=colors['bg'])
    
    # スタイル設定
    style.theme_use('clam')
    
    style.configure('TLabel', 
                   background=colors['bg'], 
                   foreground=colors['fg'])
    
    style.configure('TButton',
                   background=colors['button_bg'],
                   foreground=colors['button_fg'],
                   borderwidth=0,
                   focuscolor='none')
    
    style.map('TButton',
             background=[('active', '#505050'),
                        ('pressed', '#606060')])
    
    style.configure('TEntry',
                   fieldbackground=colors['entry_bg'],
                   foreground=colors['entry_fg'],
                   borderwidth=0,
                   insertcolor=colors['fg'])
    
    style.configure('TCombobox',
                   fieldbackground=colors['entry_bg'],
                   foreground=colors['entry_fg'],
                   borderwidth=0,
                   arrowcolor=colors['fg'])
    
    style.configure('TFrame',
                   background=colors['bg'],
                   borderwidth=0)
    
    style.configure('TLabelframe',
                   background=colors['bg'],
                   foreground=colors['fg'],
                   borderwidth=1,
                   relief='solid')
    
    style.configure('TLabelframe.Label',
                   background=colors['bg'],
                   foreground=colors['fg'])
```

### 4.3 音声変換処理の統合

```python
def start_conversion(self):
    """音声変換の開始"""
    if self.is_converting:
        messagebox.showwarning("警告", "変換処理が実行中です")
        return
    
    # 入力検証
    if not self.validate_inputs():
        return
    
    # 変換スレッドを開始
    self.is_converting = True
    self.update_ui_state(False)
    
    conversion_thread = threading.Thread(target=self.run_conversion)
    conversion_thread.daemon = True
    conversion_thread.start()

def run_conversion(self):
    """変換処理の実行"""
    try:
        # パラメータの取得
        input_file = self.input_path.get()
        output_file = self.output_path.get()
        model_file = self.selected_model.get()
        pitch = self.pitch_shift.get()
        f0_method = self.f0_method.get()
        index_rate = self.index_rate.get()
        filter_radius = self.filter_radius.get()
        rms_mix_rate = self.rms_mix_rate.get()
        protect = self.protect_rate.get()
        
        # run_inference.pyの実行
        cmd = [
            sys.executable,
            str(Path(__file__).parent / "run_inference.py"),
            input_file,
            model_file,
            output_file,
            str(pitch),
            f0_method,
            str(index_rate),
            str(filter_radius),
            str(rms_mix_rate),
            str(protect)
        ]
        
        self.log("変換を開始しました...")
        
        # プロセスの実行
        self.conversion_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 出力の監視
        for line in iter(self.conversion_process.stdout.readline, ''):
            if line:
                self.log(line.strip())
                
                # プログレスの更新
                if "Progress:" in line:
                    try:
                        progress = int(line.split(":")[1].strip().rstrip('%'))
                        self.update_progress(progress)
                    except:
                        pass
        
        # プロセスの完了待機
        self.conversion_process.wait()
        
        if self.conversion_process.returncode == 0:
            self.log("✅ 変換が完了しました！")
            messagebox.showinfo("完了", f"変換が完了しました。\n出力: {output_file}")
        else:
            stderr = self.conversion_process.stderr.read()
            self.log(f"❌ エラー: {stderr}")
            messagebox.showerror("エラー", "変換中にエラーが発生しました。")
            
    except Exception as e:
        self.log(f"❌ 例外エラー: {str(e)}")
        messagebox.showerror("エラー", f"予期しないエラー: {str(e)}")
        
    finally:
        self.is_converting = False
        self.update_ui_state(True)
        self.update_progress(0)
```

---

## 5. 音声変換処理の実装

### 5.1 run_inference.pyの改良

```python
#!/usr/bin/env python3
"""
Voice Converter Inference Runner
改良版 - より詳細なフィードバックとエラーハンドリング
"""
import os
import sys
import json
import subprocess
import time
from pathlib import Path
import soundfile as sf
import numpy as np

class InferenceRunner:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.rvc_config_path = self.script_dir / "rvc_config.py"
        
    def validate_inputs(self, args):
        """入力パラメータの検証"""
        if len(args) < 10:
            raise ValueError("引数が不足しています")
        
        input_audio = Path(args[1])
        model_path = Path(args[2])
        
        if not input_audio.exists():
            raise FileNotFoundError(f"入力ファイルが見つかりません: {input_audio}")
        
        if not model_path.exists():
            raise FileNotFoundError(f"モデルファイルが見つかりません: {model_path}")
        
        # 音声ファイルの検証
        try:
            data, sr = sf.read(str(input_audio))
            print(f"入力音声: {sr}Hz, {len(data)/sr:.2f}秒")
        except Exception as e:
            raise ValueError(f"音声ファイルの読み込みエラー: {e}")
        
        return True
    
    def run_rvc_inference(self, params):
        """RVC推論の実行"""
        # rvc_configから設定を読み込む
        if self.rvc_config_path.exists():
            sys.path.insert(0, str(self.script_dir))
            from rvc_config import get_rvc_command, POETRY_PYTHON_PATH
            
            cmd = get_rvc_command(
                model_file=params['model_path'],
                input_file=params['input_audio'],
                output_file=params['output_path'],
                pitch=params['pitch'],
                f0_method=params['f0_method'],
                index_rate=params['index_rate'],
                filter_radius=params['filter_radius'],
                protect=params['protect'],
                rms_mix_rate=params['rms_mix_rate'],
                index_file=params.get('index_file')
            )
        else:
            # フォールバック: 直接RVCモジュールを呼び出す
            cmd = [
                sys.executable, "-m", "rvc.wrapper.cli.cli", "infer",
                "-m", params['model_path'],
                "-i", params['input_audio'],
                "-o", params['output_path'],
                "-fu", str(params['pitch']),
                "-fm", params['f0_method'],
                "-ir", str(params['index_rate']),
                "-fr", str(params['filter_radius']),
                "-p", str(params['protect']),
                "-rmr", str(params['rms_mix_rate'])
            ]
        
        # プロセスの実行
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # タイムアウト付きで実行
        try:
            stdout, stderr = process.communicate(timeout=300)  # 5分のタイムアウト
            
            if process.returncode != 0:
                raise RuntimeError(f"RVC実行エラー: {stderr}")
                
            return True
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise TimeoutError("変換処理がタイムアウトしました")
    
    def simulate_progress(self, duration=5):
        """プログレス表示のシミュレーション"""
        steps = [
            (10, "モデルを読み込み中..."),
            (25, "音声データを前処理中..."),
            (40, "特徴を抽出中..."),
            (60, "音声を変換中..."),
            (80, "後処理を実行中..."),
            (95, "ファイルを保存中..."),
            (100, "完了")
        ]
        
        for progress, message in steps:
            print(message)
            print(f"Progress: {progress}%")
            time.sleep(duration / len(steps))
    
    def main(self):
        """メイン処理"""
        try:
            # 入力検証
            self.validate_inputs(sys.argv)
            
            # パラメータの解析
            params = {
                'input_audio': sys.argv[1],
                'model_path': sys.argv[2],
                'output_path': sys.argv[3],
                'pitch': int(sys.argv[4]),
                'f0_method': sys.argv[5],
                'index_rate': float(sys.argv[6]),
                'filter_radius': int(sys.argv[7]),
                'rms_mix_rate': float(sys.argv[8]),
                'protect': float(sys.argv[9]),
                'index_file': sys.argv[10] if len(sys.argv) > 10 else None
            }
            
            print("音声変換を開始します...")
            print(f"モデル: {Path(params['model_path']).name}")
            print(f"ピッチシフト: {params['pitch']}半音")
            print(f"F0抽出方法: {params['f0_method']}")
            
            # 実際の変換またはシミュレーション
            if Path(params['model_path']).suffix == '.pth':
                # 実際のRVC変換
                self.run_rvc_inference(params)
            else:
                # デモ/テスト用のシミュレーション
                self.simulate_progress()
                
                # 入力ファイルを出力にコピー（デモ用）
                import shutil
                shutil.copy2(params['input_audio'], params['output_path'])
            
            print("Voice conversion completed")
            print(f"出力ファイル: {params['output_path']}")
            
        except Exception as e:
            print(f"エラー: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    runner = InferenceRunner()
    runner.main()
```

### 5.2 rvc_config.pyの拡張

```python
#!/usr/bin/env python3
"""
RVC実行用の設定ファイル - 拡張版
"""
import os
from pathlib import Path

# Poetry仮想環境のPythonパス（自動検出機能付き）
def get_poetry_python():
    """Poetry環境のPythonパスを自動検出"""
    # 手動設定パス
    manual_path = "/Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11/bin/python"
    if os.path.exists(manual_path):
        return manual_path
    
    # Poetry環境の自動検出を試みる
    try:
        import subprocess
        result = subprocess.run(
            ["poetry", "env", "info", "--path"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            env_path = result.stdout.strip()
            python_path = Path(env_path) / "bin" / "python"
            if python_path.exists():
                return str(python_path)
    except:
        pass
    
    # フォールバック
    return "python3"

POETRY_PYTHON_PATH = get_poetry_python()

# RVCモジュールパス
RVC_MODULE = "rvc.wrapper.cli.cli"

# モデルディレクトリ
MODEL_DIR = Path(__file__).parent / "model_dir"

# デフォルト設定
DEFAULT_SETTINGS = {
    "f0_method": "rmvpe",
    "index_rate": 0.75,
    "filter_radius": 3,
    "protect": 0.33,
    "rms_mix_rate": 0.25,
    "resample_sr": 0,
}

def get_rvc_command(model_file, input_file, output_file, pitch=0, 
                   f0_method=None, index_rate=None, filter_radius=None, 
                   protect=None, rms_mix_rate=None, index_file=None, 
                   hubert_path=None, resample_sr=None):
    """RVC実行コマンドを生成（デフォルト値対応）"""
    
    # デフォルト値の適用
    f0_method = f0_method or DEFAULT_SETTINGS["f0_method"]
    index_rate = index_rate if index_rate is not None else DEFAULT_SETTINGS["index_rate"]
    filter_radius = filter_radius if filter_radius is not None else DEFAULT_SETTINGS["filter_radius"]
    protect = protect if protect is not None else DEFAULT_SETTINGS["protect"]
    rms_mix_rate = rms_mix_rate if rms_mix_rate is not None else DEFAULT_SETTINGS["rms_mix_rate"]
    resample_sr = resample_sr if resample_sr is not None else DEFAULT_SETTINGS["resample_sr"]
    
    cmd = [
        POETRY_PYTHON_PATH, "-m", RVC_MODULE, "infer",
        "-m", str(model_file),
        "-i", str(input_file),
        "-o", str(output_file),
        "-fu", str(pitch),
        "-fm", f0_method,
        "-ir", str(index_rate),
        "-fr", str(filter_radius),
        "-p", str(protect),
        "-rmr", str(rms_mix_rate),
        "-rsr", str(resample_sr)
    ]
    
    if index_file and Path(index_file).exists():
        cmd.extend(["-if", str(index_file)])
    
    if hubert_path and Path(hubert_path).exists():
        cmd.extend(["--hubert_model_path", str(hubert_path)])
    
    return cmd

def get_available_models():
    """利用可能なモデルファイルのリストを取得"""
    models = []
    
    if MODEL_DIR.exists():
        # .pthファイル
        models.extend([
            {
                "path": str(f),
                "name": f.stem,
                "type": "pth",
                "size": f.stat().st_size / (1024 * 1024)  # MB
            }
            for f in MODEL_DIR.glob("*.pth")
        ])
        
        # .onnxファイル
        models.extend([
            {
                "path": str(f),
                "name": f.stem,
                "type": "onnx",
                "size": f.stat().st_size / (1024 * 1024)  # MB
            }
            for f in MODEL_DIR.glob("*.onnx")
        ])
    
    return sorted(models, key=lambda x: x["name"])

def validate_environment():
    """環境の検証"""
    issues = []
    
    # Pythonパスの確認
    if not os.path.exists(POETRY_PYTHON_PATH):
        issues.append(f"Poetry Pythonが見つかりません: {POETRY_PYTHON_PATH}")
    
    # モデルディレクトリの確認
    if not MODEL_DIR.exists():
        issues.append(f"モデルディレクトリが見つかりません: {MODEL_DIR}")
    elif not list(MODEL_DIR.glob("*.pth")) and not list(MODEL_DIR.glob("*.onnx")):
        issues.append("モデルファイルが見つかりません")
    
    return issues
```

---

## 6. ビルドと配布

### 6.1 改良版ビルドスクリプト

```python
#!/usr/bin/env python3
"""
build_launcher_app.py - Voice Converterアプリケーションビルダー
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
import plistlib

class AppBuilder:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.app_name = "Voice Converter"
        self.bundle_id = "com.rvc.voiceconverter"
        self.version = "1.0.0"
        
    def create_app_bundle(self):
        """macOSアプリケーションバンドルの作成"""
        print("Creating Voice Converter.app...")
        
        # アプリケーションディレクトリ構造
        app_dir = self.script_dir / "dist" / f"{self.app_name}.app"
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        # 既存のアプリを削除
        if app_dir.exists():
            shutil.rmtree(app_dir)
        
        # ディレクトリ作成
        for dir_path in [macos_dir, resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 実行可能ファイルの作成
        self.create_executable(macos_dir)
        
        # Info.plistの作成
        self.create_info_plist(contents_dir)
        
        # リソースのコピー
        self.copy_resources(resources_dir)
        
        # アイコンの設定
        self.set_app_icon(resources_dir)
        
        print(f"✅ App bundle created: {app_dir}")
        return app_dir
    
    def create_executable(self, macos_dir):
        """実行可能ファイルの作成"""
        executable_path = macos_dir / self.app_name
        
        script_content = f'''#!/bin/bash
# Voice Converter App Launcher

# アプリケーションのベースディレクトリを取得
APP_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
RESOURCES_DIR="$APP_DIR/Contents/Resources"

# プロジェクトディレクトリに移動
cd "$RESOURCES_DIR"

# 起動スクリプトを実行
exec ./launch_voice_converter.sh "$@"
'''
        
        executable_path.write_text(script_content)
        executable_path.chmod(0o755)
    
    def create_info_plist(self, contents_dir):
        """Info.plistの作成"""
        info = {
            'CFBundleExecutable': self.app_name,
            'CFBundleIdentifier': self.bundle_id,
            'CFBundleName': self.app_name,
            'CFBundleDisplayName': self.app_name,
            'CFBundleVersion': self.version,
            'CFBundleShortVersionString': self.version,
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': '????',
            'LSMinimumSystemVersion': '10.15',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,  # ダークモード対応
            'CFBundleIconFile': 'AppIcon',
            'NSMicrophoneUsageDescription': 'Voice Converterは音声処理のためにマイクへのアクセスが必要です。',
            'LSApplicationCategoryType': 'public.app-category.music',
        }
        
        plist_path = contents_dir / 'Info.plist'
        with open(plist_path, 'wb') as f:
            plistlib.dump(info, f)
    
    def copy_resources(self, resources_dir):
        """必要なリソースをコピー"""
        files_to_copy = [
            'launch_voice_converter.sh',
            'gui_dark_mode.py',
            'run_inference.py',
            'rvc_config.py',
            'gui_settings.json'
        ]
        
        for file_name in files_to_copy:
            src = self.script_dir / file_name
            if src.exists():
                shutil.copy2(src, resources_dir)
                if file_name.endswith('.sh'):
                    (resources_dir / file_name).chmod(0o755)
        
        # ディレクトリのコピー
        dirs_to_copy = ['model_dir', 'rvc']
        for dir_name in dirs_to_copy:
            src_dir = self.script_dir / dir_name
            if src_dir.exists():
                dst_dir = resources_dir / dir_name
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
    
    def set_app_icon(self, resources_dir):
        """アプリケーションアイコンの設定"""
        icon_path = self.script_dir / "assets" / "icon.icns"
        if icon_path.exists():
            shutil.copy2(icon_path, resources_dir / "AppIcon.icns")
        else:
            # アイコンがない場合は作成
            self.create_default_icon(resources_dir / "AppIcon.icns")
    
    def create_default_icon(self, icon_path):
        """デフォルトアイコンの作成（簡易版）"""
        # iconutilコマンドでアイコンセットから.icnsを作成
        # ここでは省略（実際の実装では適切なアイコンを用意）
        pass
    
    def create_dmg(self, app_path):
        """DMGインストーラーの作成"""
        print("Creating DMG installer...")
        
        dmg_name = f"{self.app_name}.dmg"
        dmg_path = self.script_dir / dmg_name
        
        # 既存のDMGを削除
        if dmg_path.exists():
            dmg_path.unlink()
        
        # DMG作成コマンド
        cmd = [
            'hdiutil', 'create',
            '-volname', self.app_name,
            '-srcfolder', str(app_path),
            '-ov',
            '-format', 'UDZO',
            str(dmg_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ DMG created: {dmg_path}")
            return dmg_path
        else:
            print(f"❌ DMG creation failed: {result.stderr}")
            return None
    
    def sign_app(self, app_path):
        """アプリケーションの署名（オプション）"""
        # 開発者IDがある場合のみ実行
        cmd = ['codesign', '--force', '--deep', '--sign', '-', str(app_path)]
        subprocess.run(cmd, capture_output=True)
    
    def build(self):
        """ビルドプロセスの実行"""
        print("🔨 Building Voice Converter for macOS...")
        
        # アプリバンドルの作成
        app_path = self.create_app_bundle()
        
        # 署名（オプション）
        self.sign_app(app_path)
        
        # DMGの作成
        dmg_path = self.create_dmg(app_path)
        
        print("\n✅ Build completed successfully!")
        print(f"📦 Application: {app_path}")
        if dmg_path:
            print(f"💿 Installer: {dmg_path}")
        
        # 起動方法の表示
        print("\n🚀 To run the app:")
        print(f"   open '{app_path}'")

if __name__ == "__main__":
    builder = AppBuilder()
    builder.build()
```

### 6.2 Nuitkaを使用したネイティブビルド

```bash
#!/bin/bash
# build_native.sh - Nuitkaによるネイティブビルド

echo "Building native Voice Converter with Nuitka..."

# Nuitkaのインストール確認
if ! command -v nuitka3 &> /dev/null; then
    echo "Installing Nuitka..."
    pip install nuitka
fi

# ビルドディレクトリのクリーンアップ
rm -rf build dist

# Nuitkaビルド
python -m nuitka \
    --standalone \
    --macos-create-app-bundle \
    --macos-app-name="Voice Converter" \
    --enable-plugin=tk-inter \
    --include-data-dir=model_dir=model_dir \
    --include-data-dir=rvc=rvc \
    --include-data-file=gui_settings.json=gui_settings.json \
    --include-data-file=rvc_config.py=rvc_config.py \
    --include-data-file=run_inference.py=run_inference.py \
    --output-dir=dist \
    gui_dark_mode.py

echo "Build completed!"
```

---

## 7. トラブルシューティング

### 7.1 よくある問題と解決方法

#### Python環境の問題

**問題**: "Python 3が見つかりません"
```bash
# 解決方法1: Homebrewでインストール
brew install python@3.11

# 解決方法2: pyenvを使用
pyenv install 3.11.9
pyenv global 3.11.9
```

**問題**: Tkinterが見つからない
```bash
# macOSでの解決方法
brew install python-tk@3.11

# または
brew reinstall python@3.11
```

#### 起動時のエラー

**問題**: "Permission denied"エラー
```bash
# スクリプトに実行権限を付与
chmod +x launch_voice_converter.sh
chmod +x run_inference.py
```

**問題**: モジュールインポートエラー
```bash
# Poetry環境の再構築
poetry install --no-root

# または仮想環境の再作成
poetry env remove python
poetry install
```

#### GUI関連の問題

**問題**: ウィンドウが表示されない
```python
# デバッグモードで起動
python gui_dark_mode.py --debug

# または環境変数を設定
export DISPLAY=:0
python gui_dark_mode.py
```

**問題**: ダークモードが適用されない
```python
# 手動でテーマを設定
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
style = ttk.Style()
style.theme_use('aqua')  # macOS用テーマ
```

### 7.2 デバッグツール

#### ログ出力の確認
```bash
# ログファイルの監視
tail -f logs/voice_converter_*.log

# エラーログのみ表示
grep "ERROR" logs/voice_converter_*.log
```

#### プロセスの監視
```bash
# 実行中のPythonプロセスを確認
ps aux | grep -E "python.*gui_dark_mode"

# プロセスの強制終了
pkill -f "gui_dark_mode.py"
```

#### 環境情報の収集
```python
#!/usr/bin/env python3
"""
debug_environment.py - 環境情報収集スクリプト
"""
import sys
import platform
import subprocess
import pkg_resources
from pathlib import Path

def collect_environment_info():
    """環境情報を収集"""
    info = {
        "Python Version": sys.version,
        "Platform": platform.platform(),
        "macOS Version": platform.mac_ver()[0] if platform.system() == "Darwin" else "N/A",
        "Current Directory": str(Path.cwd()),
        "Python Executable": sys.executable,
    }
    
    # インストール済みパッケージ
    packages = []
    for pkg in ['tkinter', 'soundfile', 'numpy', 'poetry']:
        try:
            version = pkg_resources.get_distribution(pkg).version
            packages.append(f"{pkg}=={version}")
        except:
            packages.append(f"{pkg}: Not installed")
    
    info["Packages"] = "\n".join(packages)
    
    # Poetry環境の確認
    try:
        result = subprocess.run(
            ["poetry", "env", "info"],
            capture_output=True,
            text=True
        )
        info["Poetry Environment"] = result.stdout if result.returncode == 0 else "Not found"
    except:
        info["Poetry Environment"] = "Poetry not installed"
    
    return info

if __name__ == "__main__":
    print("=== Voice Converter Environment Info ===")
    for key, value in collect_environment_info().items():
        print(f"\n{key}:")
        print(value)
```

### 7.3 パフォーマンス最適化

#### メモリ使用量の削減
```python
# gui_dark_mode.pyの最適化
import gc

class VoiceConverterGUI:
    def cleanup_resources(self):
        """リソースのクリーンアップ"""
        # 未使用のオブジェクトを削除
        if hasattr(self, 'conversion_process'):
            if self.conversion_process and self.conversion_process.poll() is None:
                self.conversion_process.terminate()
        
        # ガベージコレクションを強制実行
        gc.collect()
```

#### 起動時間の短縮
```bash
# 起動スクリプトの最適化
# launch_voice_converter.sh

# 不要なチェックをスキップするオプション
SKIP_CHECKS=${SKIP_CHECKS:-0}

if [ "$SKIP_CHECKS" -eq 0 ]; then
    check_dependencies
else
    log "依存関係チェックをスキップしました"
fi
```

---

## 付録

### A. ファイルテンプレート

#### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Poetry
poetry.lock

# Build
build/
dist/
*.egg-info/
.eggs/

# macOS
.DS_Store
*.app/
*.dmg

# Logs
logs/
*.log

# Model files
model_dir/*.pth
model_dir/*.onnx
model_dir/*.index

# Output
output/
results/
```

#### setup.cfg
```ini
[metadata]
name = voice-converter
version = 1.0.0
author = RVC Project
description = Voice Converter Application

[options]
python_requires = >=3.9
install_requires =
    tkinter
    soundfile
    numpy
    
[options.entry_points]
console_scripts =
    voice-converter = gui_dark_mode:main
```

### B. 参考リンク
- [RVC公式ドキュメント](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion)
- [Tkinter公式ドキュメント](https://docs.python.org/3/library/tkinter.html)
- [Nuitkaドキュメント](https://nuitka.net/doc/user-manual.html)
- [macOS App Bundle仕様](https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html)

---

最終更新日: 2025年6月1日
