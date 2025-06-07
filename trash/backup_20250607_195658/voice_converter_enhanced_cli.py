#!/usr/bin/env python3
"""
Voice Converter Enhanced CLI版
Tkinter依存なしで改善システムをフル活用するコマンドライン版
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# 改善モジュールのインポート（Tkinter依存なし版）
try:
    sys.path.insert(0, 'gui_modules_no_tkinter')
    from settings_manager_standalone import SettingsManager
    from error_handler_standalone import ErrorHandler, ErrorLevel, ErrorCategory
    ENHANCED_MODULES = True
    print("✅ Enhanced modules (no-tkinter) loaded successfully")
except Exception as e:
    print(f"⚠️ Enhanced modules not available: {e}")
    print("Running in basic mode...")
    ENHANCED_MODULES = False

class VoiceConverterEnhancedCLI:
    """
    Voice Converter Enhanced CLI版
    改善システムのフル機能を活用したコマンドライン版
    """
    
    def __init__(self):
        """CLI初期化"""
        print("Voice Converter Enhanced CLI")
        print("=" * 50)
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 改善システムの初期化
        if ENHANCED_MODULES:
            try:
                # 設定管理システム
                self.settings = SettingsManager("enhanced_cli_settings.json")
                print("✅ Settings management system initialized")
                
                # エラーハンドリングシステム
                self.error_handler = ErrorHandler("enhanced_cli_logs", enable_ui_callback=False)
                print("✅ Error handling system initialized")
                
                self.enhanced_mode = True
                self._setup_default_presets()
            except Exception as e:
                print(f"⚠️ Enhanced systems failed to initialize: {e}")
                self.enhanced_mode = False
        else:
            self.enhanced_mode = False
        
        # 基本設定
        self.model_dir = os.path.join(self.base_dir, "model_dir")
        self.default_output_dir = os.path.join(self.base_dir, "output")
        os.makedirs(self.default_output_dir, exist_ok=True)
        
        print(f"Model directory: {self.model_dir}")
        print(f"Output directory: {self.default_output_dir}")
        print(f"Enhanced mode: {'✅ Enabled' if self.enhanced_mode else '❌ Disabled'}")
    
    def _setup_default_presets(self):
        """デフォルトプリセットのセットアップ"""
        if not self.enhanced_mode:
            return
        
        # 既存プリセットの確認
        existing_presets = self.settings.get('audio_settings.presets', [])
        if existing_presets:
            return  # 既にプリセットが存在する
        
        # デフォルトプリセットの作成
        default_presets = [
            {
                'name': '高品質（推奨）',
                'description': '最高品質の変換設定',
                'params': {
                    'pitch': 0,
                    'f0_method': 'rmvpe',
                    'index_rate': 1.0,
                    'filter_radius': 3,
                    'rms_mix_rate': 0.25,
                    'protect': 0.33
                },
                'is_default': True
            },
            {
                'name': '高速変換',
                'description': '処理速度を重視した設定',
                'params': {
                    'pitch': 0,
                    'f0_method': 'harvest',
                    'index_rate': 0.8,
                    'filter_radius': 2,
                    'rms_mix_rate': 0.2,
                    'protect': 0.25
                },
                'is_default': False
            },
            {
                'name': 'ボーカル専用',
                'description': '歌声変換に最適化',
                'params': {
                    'pitch': 0,
                    'f0_method': 'mangio-crepe',
                    'index_rate': 1.0,
                    'filter_radius': 3,
                    'rms_mix_rate': 0.3,
                    'protect': 0.4
                },
                'is_default': False
            }
        ]
        
        for preset in default_presets:
            self.settings.add_preset(
                preset['name'],
                preset['description'],
                preset['params'],
                preset['is_default']
            )
        
        self.settings.save_settings()
        print("✅ Default presets created")
    
    def log_message(self, message, level="INFO"):
        """統一ログメッセージ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.enhanced_mode:
            if level == "ERROR":
                self.error_handler.log(ErrorLevel.ERROR, message, ErrorCategory.PROCESSING_ERROR)
            elif level == "WARNING":
                self.error_handler.log(ErrorLevel.WARNING, message)
            else:
                self.error_handler.log(ErrorLevel.INFO, message)
        
        print(f"[{timestamp}] {level}: {message}")
    
    def list_models(self, detailed=False):
        """利用可能なモデル一覧表示"""
        print("\n📁 Available Models:")
        print("-" * 40)
        
        if not os.path.exists(self.model_dir):
            print("❌ Model directory not found")
            return []
        
        models = []
        for item in os.listdir(self.model_dir):
            item_path = os.path.join(self.model_dir, item)
            if os.path.isdir(item_path):
                # .pthファイルを探す
                pth_files = [f for f in os.listdir(item_path) if f.endswith('.pth')]
                if pth_files:
                    pth_file = pth_files[0]
                    model_name = os.path.splitext(pth_file)[0]
                    model_path = os.path.join(item_path, pth_file)
                    
                    # インデックスファイルの確認
                    index_files = [f for f in os.listdir(item_path) if f.endswith('.index')]
                    has_index = len(index_files) > 0
                    
                    # ファイルサイズの取得
                    file_size = os.path.getsize(model_path)
                    size_mb = file_size / (1024 * 1024)
                    
                    models.append({
                        'id': item,
                        'name': model_name,
                        'path': model_path,
                        'index': os.path.join(item_path, index_files[0]) if has_index else None,
                        'has_index': has_index,
                        'size_mb': size_mb
                    })
                    
                    if detailed:
                        index_status = "✓" if has_index else "✗"
                        print(f"  [{item:2}] {model_name}")
                        print(f"      Index: {index_status}, Size: {size_mb:.1f} MB")
                        print(f"      Path: {model_path}")
                    else:
                        index_status = "✓" if has_index else "✗"
                        print(f"  [{item:2}] {model_name} (Index: {index_status}, {size_mb:.1f} MB)")
        
        if not models:
            print("  No models found")
        else:
            print(f"\nTotal: {len(models)} model(s) available")
        
        return models
    
    def list_presets(self, detailed=False):
        """プリセット一覧表示"""
        if not self.enhanced_mode:
            print("⚠️ Presets require enhanced mode")
            return []
        
        print("\n🎛️ Available Presets:")
        print("-" * 40)
        
        presets = self.settings.get('audio_settings.presets', [])
        if not presets:
            print("  No presets available")
            return []
        
        for i, preset in enumerate(presets):
            default_mark = " (Default)" if preset.get('is_default', False) else ""
            print(f"  [{i:2}] {preset['name']}{default_mark}")
            
            if detailed:
                print(f"      Description: {preset['description']}")
                params = preset.get('params', {})
                print(f"      Parameters:")
                print(f"        Pitch: {params.get('pitch', 0)}")
                print(f"        F0 Method: {params.get('f0_method', 'rmvpe')}")
                print(f"        Index Rate: {params.get('index_rate', 1.0)}")
                print(f"        Filter Radius: {params.get('filter_radius', 3)}")
                print(f"        RMS Mix Rate: {params.get('rms_mix_rate', 0.25)}")
                print(f"        Protect: {params.get('protect', 0.33)}")
            else:
                params = preset.get('params', {})
                print(f"      {preset['description']}")
                print(f"      Pitch: {params.get('pitch', 0)}, "
                      f"F0: {params.get('f0_method', 'rmvpe')}, "
                      f"Index: {params.get('index_rate', 1.0)}")
        
        print(f"\nTotal: {len(presets)} preset(s) available")
        return presets
    
    def show_settings(self):
        """現在の設定表示"""
        print("\n⚙️ Current Settings:")
        print("-" * 40)
        
        if self.enhanced_mode:
            params = self.settings.get('audio_settings.default_params', {})
            print(f"  Pitch: {params.get('pitch', 0)}")
            print(f"  F0 Method: {params.get('f0_method', 'rmvpe')}")
            print(f"  Index Rate: {params.get('index_rate', 1.0)}")
            print(f"  Filter Radius: {params.get('filter_radius', 3)}")
            print(f"  RMS Mix Rate: {params.get('rms_mix_rate', 0.25)}")
            print(f"  Protect: {params.get('protect', 0.33)}")
            
            # 統計情報
            print(f"\n📊 Statistics:")
            error_stats = self.error_handler.get_error_stats()
            print(f"  Total errors: {error_stats.get('total_errors', 0)}")
            print(f"  Session duration: {error_stats.get('session_duration', 'N/A')}")
            
            # 最近使用したファイル
            recent_files = self.settings.get_recent_files('input')
            print(f"  Recent files: {len(recent_files)}")
        else:
            print("  Using default settings (enhanced mode not available)")
            print("  Pitch: 0")
            print("  F0 Method: rmvpe")
            print("  Index Rate: 1.0")
    
    def convert_audio(self, input_file, output_file, model_id, preset_id=None, 
                     pitch=None, f0_method=None, index_rate=None, 
                     filter_radius=None, rms_mix_rate=None, protect=None, 
                     verbose=False):
        """音声変換実行"""
        print(f"\n🎵 Starting Audio Conversion")
        print("=" * 50)
        
        # 入力ファイルの確認
        if not os.path.exists(input_file):
            self.log_message(f"Input file not found: {input_file}", "ERROR")
            return False
        
        # ファイルサイズとフォーマットの確認
        file_size = os.path.getsize(input_file)
        file_size_mb = file_size / (1024 * 1024)
        file_ext = os.path.splitext(input_file)[1].lower()
        
        print(f"📄 Input: {os.path.basename(input_file)} ({file_size_mb:.1f} MB, {file_ext})")
        
        # 出力ディレクトリの作成
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"📁 Created output directory: {output_dir}")
        
        # モデルの確認
        models = self.list_models()
        selected_model = None
        for model in models:
            if model['id'] == model_id or model['name'] == model_id:
                selected_model = model
                break
        
        if not selected_model:
            self.log_message(f"Model not found: {model_id}", "ERROR")
            print("Available models:")
            self.list_models()
            return False
        
        # パラメータの設定
        if self.enhanced_mode and preset_id is not None:
            presets = self.settings.get('audio_settings.presets', [])
            if 0 <= preset_id < len(presets):
                preset_params = presets[preset_id]['params']
                pitch = pitch if pitch is not None else preset_params.get('pitch', 0)
                f0_method = f0_method or preset_params.get('f0_method', 'rmvpe')
                index_rate = index_rate if index_rate is not None else preset_params.get('index_rate', 1.0)
                filter_radius = filter_radius if filter_radius is not None else preset_params.get('filter_radius', 3)
                rms_mix_rate = rms_mix_rate if rms_mix_rate is not None else preset_params.get('rms_mix_rate', 0.25)
                protect = protect if protect is not None else preset_params.get('protect', 0.33)
                print(f"📋 Using preset: {presets[preset_id]['name']}")
            else:
                print(f"⚠️ Invalid preset ID: {preset_id}")
        
        # デフォルト値の設定
        if self.enhanced_mode:
            default_params = self.settings.get('audio_settings.default_params', {})
            pitch = pitch if pitch is not None else default_params.get('pitch', 0)
            f0_method = f0_method or default_params.get('f0_method', 'rmvpe')
            index_rate = index_rate if index_rate is not None else default_params.get('index_rate', 1.0)
            filter_radius = filter_radius if filter_radius is not None else default_params.get('filter_radius', 3)
            rms_mix_rate = rms_mix_rate if rms_mix_rate is not None else default_params.get('rms_mix_rate', 0.25)
            protect = protect if protect is not None else default_params.get('protect', 0.33)
        else:
            pitch = pitch if pitch is not None else 0
            f0_method = f0_method or 'rmvpe'
            index_rate = index_rate if index_rate is not None else 1.0
            filter_radius = filter_radius if filter_radius is not None else 3
            rms_mix_rate = rms_mix_rate if rms_mix_rate is not None else 0.25
            protect = protect if protect is not None else 0.33
        
        print(f"🎼 Model: {selected_model['name']} ({selected_model['size_mb']:.1f} MB)")
        print(f"📁 Output: {os.path.basename(output_file)}")
        print(f"⚙️ Parameters:")
        print(f"   Pitch: {pitch}")
        print(f"   F0 Method: {f0_method}")
        print(f"   Index Rate: {index_rate}")
        print(f"   Filter Radius: {filter_radius}")
        print(f"   RMS Mix Rate: {rms_mix_rate}")
        print(f"   Protect: {protect}")
        
        if selected_model['has_index']:
            print(f"📇 Index: Available")
        else:
            print(f"📇 Index: Not available")
        
        try:
            # RVCコマンドの構築と実行
            self.log_message("Building conversion command...", "INFO")
            
            # Poetry環境の確認
            try:
                from rvc_config import POETRY_PYTHON_PATH, RVC_MODULE
                python_path = POETRY_PYTHON_PATH
                rvc_module = RVC_MODULE
                use_poetry = True
                print(f"🐍 Using Poetry environment: {python_path}")
            except ImportError:
                python_path = sys.executable
                rvc_module = "rvc.wrapper.cli.cli"
                use_poetry = False
                print(f"🐍 Using system Python: {python_path}")
            
            # コマンドライン引数の構築
            cmd = [
                python_path,
                "-m", rvc_module,
                "infer",
                "-i", input_file,
                "-o", output_file,
                "-m", selected_model['path'],
                "-fu", str(pitch),
                "-fr", str(filter_radius),
                "-ir", str(index_rate),
                "-rmr", str(rms_mix_rate),
                "-p", str(protect),
                "-fm", f0_method
            ]
            
            # インデックスファイルがある場合
            if selected_model['index']:
                cmd.extend(["-if", selected_model['index']])
            
            # Hubertモデルパスを探す
            hubert_path = None
            possible_paths = [
                "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/hubert_base.pt",
                "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/rvc/models/hubert/hubert_base.pt",
                "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/models/hubert_base.pt"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    hubert_path = path
                    break
            
            if hubert_path:
                cmd.extend(["--hubert_model_path", hubert_path])
            else:
                # デフォルトパスを使用
                cmd.extend(["--hubert_model_path", "hubert_base.pt"])
            
            if verbose:
                print(f"🔧 Command: {' '.join(cmd)}")
            
            self.log_message("Starting conversion process...", "INFO")
            print("\n🔄 Converting... (This may take a while)")
            
            # 進行状況の表示
            start_time = datetime.now()
            
            # プロセス実行
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            if result.returncode == 0:
                self.log_message("Conversion completed successfully", "INFO")
                print("✅ Conversion completed!")
                print(f"⏱️ Duration: {duration}")
                print(f"📁 Output saved to: {output_file}")
                
                # 出力ファイルサイズの確認
                if os.path.exists(output_file):
                    output_size = os.path.getsize(output_file)
                    output_size_mb = output_size / (1024 * 1024)
                    print(f"📊 Output size: {output_size_mb:.1f} MB")
                
                # 最近使用ファイルに追加（改善モード）
                if self.enhanced_mode:
                    self.settings.add_recent_file(input_file, 'input')
                    self.settings.save_settings()
                
                return True
            else:
                error_msg = f"Conversion failed (exit code {result.returncode}): {result.stderr}"
                self.log_message(error_msg, "ERROR")
                print(f"❌ Conversion failed:")
                print(f"   Exit code: {result.returncode}")
                print(f"   Error: {result.stderr}")
                if verbose and result.stdout:
                    print(f"   Output: {result.stdout}")
                return False
                
        except Exception as e:
            error_msg = f"Conversion error: {str(e)}"
            self.log_message(error_msg, "ERROR")
            print(f"❌ Conversion error: {e}")
            return False
    
    def show_recent_files(self):
        """最近使用したファイル表示"""
        if not self.enhanced_mode:
            print("⚠️ Recent files tracking requires enhanced mode")
            return
        
        print("\n📂 Recent Files:")
        print("-" * 40)
        
        recent_files = self.settings.get_recent_files('input')
        if not recent_files:
            print("  No recent files")
            return
        
        for i, file_path in enumerate(recent_files[:10]):  # 最新10件
            exists = "✓" if os.path.exists(file_path) else "✗"
            file_size = "N/A"
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            print(f"  [{i:2}] {os.path.basename(file_path)} ({exists}) - {file_size}")
    
    def create_preset(self, name, description, pitch=0, f0_method='rmvpe', 
                     index_rate=1.0, filter_radius=3, rms_mix_rate=0.25, protect=0.33):
        """新しいプリセットの作成"""
        if not self.enhanced_mode:
            print("⚠️ Preset creation requires enhanced mode")
            return False
        
        params = {
            'pitch': pitch,
            'f0_method': f0_method,
            'index_rate': index_rate,
            'filter_radius': filter_radius,
            'rms_mix_rate': rms_mix_rate,
            'protect': protect
        }
        
        if self.settings.add_preset(name, description, params):
            self.settings.save_settings()
            print(f"✅ Preset '{name}' created successfully")
            self.log_message(f"Preset created: {name}", "INFO")
            return True
        else:
            print(f"❌ Failed to create preset '{name}' (may already exist)")
            return False
    
    def delete_preset(self, preset_id):
        """プリセットの削除"""
        if not self.enhanced_mode:
            print("⚠️ Preset deletion requires enhanced mode")
            return False
        
        presets = self.settings.get('audio_settings.presets', [])
        if 0 <= preset_id < len(presets):
            preset_name = presets[preset_id]['name']
            if self.settings.remove_preset(preset_name):
                self.settings.save_settings()
                print(f"✅ Preset '{preset_name}' deleted successfully")
                return True
        
        print(f"❌ Invalid preset ID: {preset_id}")
        return False
    
    def export_settings(self, export_file):
        """設定のエクスポート"""
        if not self.enhanced_mode:
            print("⚠️ Settings export requires enhanced mode")
            return False
        
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'settings': self.settings.settings,
                'presets': self.settings.get('audio_settings.presets', [])
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Settings exported to: {export_file}")
            self.log_message(f"Settings exported to {export_file}", "INFO")
            return True
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def show_system_info(self):
        """システム情報表示"""
        print("\n💻 System Information:")
        print("-" * 40)
        print(f"  Python: {sys.version.split()[0]}")
        print(f"  Platform: {sys.platform}")
        print(f"  Working Directory: {os.getcwd()}")
        print(f"  Enhanced Mode: {'✅ Enabled' if self.enhanced_mode else '❌ Disabled'}")
        
        if self.enhanced_mode:
            print(f"  Settings File: {self.settings.settings_file}")
            print(f"  Log Directory: enhanced_cli_logs/")
            
            # ログファイルの確認
            log_dir = Path("enhanced_cli_logs")
            if log_dir.exists():
                log_files = list(log_dir.glob("*.log"))
                print(f"  Log Files: {len(log_files)}")
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """
Voice Converter Enhanced CLI

Available Commands:
  models [--detailed]         List available voice models
  presets [--detailed]        List available presets
  settings                    Show current settings
  recent                      Show recent files
  convert                     Convert audio file
  create-preset               Create new preset
  delete-preset <id>          Delete preset by ID
  export-settings <file>      Export settings to file
  system-info                 Show system information
  help                        Show this help

Convert Command Usage:
  python voice_converter_enhanced_cli.py convert <input> <output> <model> [options]
  
  Options:
    --preset <id>           Use preset (number from presets list)
    --pitch <value>         Pitch adjustment (-12 to 12)
    --f0-method <name>      F0 extraction method (rmvpe, harvest, crepe, etc.)
    --index-rate <val>      Index usage rate (0.0 to 1.0)
    --filter-radius <val>   Filter radius (0 to 7)
    --rms-mix-rate <val>    RMS mix rate (0.0 to 1.0)
    --protect <val>         Protect rate (0.0 to 0.5)
    --verbose               Show detailed output

Examples:
  # List models with details
  python voice_converter_enhanced_cli.py models --detailed
  
  # List presets with details  
  python voice_converter_enhanced_cli.py presets --detailed
  
  # Convert with default settings
  python voice_converter_enhanced_cli.py convert input.wav output.wav 4
  
  # Convert with preset
  python voice_converter_enhanced_cli.py convert input.wav output.wav 4 --preset 0
  
  # Convert with custom parameters
  python voice_converter_enhanced_cli.py convert input.wav output.wav 4 --pitch 2 --f0-method rmvpe --verbose
  
  # Create new preset
  python voice_converter_enhanced_cli.py create-preset "My Preset" "Custom settings" --pitch 1 --f0-method harvest

Enhanced Features:
  ✅ Advanced preset management
  ✅ Settings persistence and export
  ✅ Recent files tracking
  ✅ Comprehensive error handling
  ✅ Structured logging with rotation
  ✅ Performance monitoring
  ✅ System information display
"""
        print(help_text)

def main():
    """メイン実行関数"""
    cli = VoiceConverterEnhancedCLI()
    
    if len(sys.argv) < 2:
        cli.show_help()
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "models":
            detailed = "--detailed" in sys.argv
            cli.list_models(detailed=detailed)
        
        elif command == "presets":
            detailed = "--detailed" in sys.argv
            cli.list_presets(detailed=detailed)
        
        elif command == "settings":
            cli.show_settings()
        
        elif command == "recent":
            cli.show_recent_files()
        
        elif command == "system-info":
            cli.show_system_info()
        
        elif command == "help":
            cli.show_help()
        
        elif command == "delete-preset":
            if len(sys.argv) < 3:
                print("❌ Usage: delete-preset <preset_id>")
                return
            preset_id = int(sys.argv[2])
            cli.delete_preset(preset_id)
        
        elif command == "export-settings":
            if len(sys.argv) < 3:
                print("❌ Usage: export-settings <output_file>")
                return
            export_file = sys.argv[2]
            cli.export_settings(export_file)
        
        elif command == "convert":
            if len(sys.argv) < 5:
                print("❌ Usage: convert <input_file> <output_file> <model_id> [options]")
                return
            
            # 基本引数
            input_file = sys.argv[2]
            output_file = sys.argv[3]
            model_id = sys.argv[4]
            
            # オプション解析
            parser = argparse.ArgumentParser()
            parser.add_argument('command')
            parser.add_argument('input_file')
            parser.add_argument('output_file')
            parser.add_argument('model_id')
            parser.add_argument('--preset', type=int, help='Preset ID')
            parser.add_argument('--pitch', type=int, help='Pitch adjustment')
            parser.add_argument('--f0-method', help='F0 extraction method')
            parser.add_argument('--index-rate', type=float, help='Index usage rate')
            parser.add_argument('--filter-radius', type=int, help='Filter radius')
            parser.add_argument('--rms-mix-rate', type=float, help='RMS mix rate')
            parser.add_argument('--protect', type=float, help='Protect rate')
            parser.add_argument('--verbose', action='store_true', help='Verbose output')
            
            args = parser.parse_args()
            
            cli.convert_audio(
                input_file=args.input_file,
                output_file=args.output_file,
                model_id=args.model_id,
                preset_id=args.preset,
                pitch=args.pitch,
                f0_method=getattr(args, 'f0_method'),
                index_rate=getattr(args, 'index_rate'),
                filter_radius=getattr(args, 'filter_radius'),
                rms_mix_rate=getattr(args, 'rms_mix_rate'),
                protect=args.protect,
                verbose=args.verbose
            )
        
        elif command == "create-preset":
            if len(sys.argv) < 4:
                print("❌ Usage: create-preset <name> <description> [options]")
                return
            
            name = sys.argv[2]
            description = sys.argv[3]
            
            # オプション解析
            parser = argparse.ArgumentParser()
            parser.add_argument('command')
            parser.add_argument('name')
            parser.add_argument('description')
            parser.add_argument('--pitch', type=int, default=0)
            parser.add_argument('--f0-method', default='rmvpe')
            parser.add_argument('--index-rate', type=float, default=1.0)
            parser.add_argument('--filter-radius', type=int, default=3)
            parser.add_argument('--rms-mix-rate', type=float, default=0.25)
            parser.add_argument('--protect', type=float, default=0.33)
            
            args = parser.parse_args()
            
            cli.create_preset(
                name=args.name,
                description=args.description,
                pitch=args.pitch,
                f0_method=getattr(args, 'f0_method'),
                index_rate=getattr(args, 'index_rate'),
                filter_radius=getattr(args, 'filter_radius'),
                rms_mix_rate=getattr(args, 'rms_mix_rate'),
                protect=args.protect
            )
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'help' to see available commands")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        if ENHANCED_MODULES:
            cli.log_message(f"Unhandled error: {e}", "ERROR")

if __name__ == "__main__":
    main()