#!/usr/bin/env python3
"""
Voice Converter CLI版
Tkinterが利用できない環境でも動作するコマンドライン版
改善システムのコア機能を統合
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# 改善モジュールのインポート（GUI依存を除く）
try:
    # GUI依存を避けて直接インポート
    sys.path.insert(0, 'gui_modules')
    from gui_modules.settings_manager import SettingsManager
    from gui_modules.error_handler import ErrorHandler, ErrorLevel, ErrorCategory
    ENHANCED_MODULES = True
    print("✅ Enhanced modules loaded successfully")
except Exception as e:
    print(f"⚠️ Enhanced modules not available: {e}")
    print("Running in basic mode...")
    ENHANCED_MODULES = False

class VoiceConverterCLI:
    """
    Voice Converter CLI版
    改善システムのコア機能を活用したコマンドライン版
    """
    
    def __init__(self):
        """CLI初期化"""
        print("Voice Converter CLI - Enhanced Edition")
        print("=" * 50)
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 改善システムの初期化
        if ENHANCED_MODULES:
            try:
                # 設定管理システム
                self.settings = SettingsManager("cli_settings.json")
                print("✅ Settings management system initialized")
                
                # エラーハンドリングシステム
                self.error_handler = ErrorHandler("cli_logs", enable_ui_callback=False)
                print("✅ Error handling system initialized")
                
                self.enhanced_mode = True
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
    
    def list_models(self):
        """利用可能なモデル一覧表示"""
        print("\n📁 Available Models:")
        print("-" * 30)
        
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
                    
                    # インデックスファイルの確認
                    index_files = [f for f in os.listdir(item_path) if f.endswith('.index')]
                    has_index = len(index_files) > 0
                    
                    models.append({
                        'id': item,
                        'name': model_name,
                        'path': os.path.join(item_path, pth_file),
                        'index': os.path.join(item_path, index_files[0]) if has_index else None,
                        'has_index': has_index
                    })
                    
                    index_status = "✓" if has_index else "✗"
                    print(f"  [{item}] {model_name} (Index: {index_status})")
        
        if not models:
            print("  No models found")
        
        return models
    
    def list_presets(self):
        """プリセット一覧表示"""
        if not self.enhanced_mode:
            print("⚠️ Presets require enhanced mode")
            return []
        
        print("\n🎛️ Available Presets:")
        print("-" * 30)
        
        presets = self.settings.get('audio_settings.presets', [])
        if not presets:
            print("  No presets available")
            return []
        
        for i, preset in enumerate(presets):
            default_mark = " (Default)" if preset.get('is_default', False) else ""
            print(f"  [{i}] {preset['name']}{default_mark}")
            print(f"      {preset['description']}")
            
            params = preset.get('params', {})
            print(f"      Pitch: {params.get('pitch', 0)}, "
                  f"F0: {params.get('f0_method', 'rmvpe')}, "
                  f"Index: {params.get('index_rate', 1.0)}")
        
        return presets
    
    def show_settings(self):
        """現在の設定表示"""
        print("\n⚙️ Current Settings:")
        print("-" * 30)
        
        if self.enhanced_mode:
            params = self.settings.get('audio_settings.default_params', {})
            print(f"  Pitch: {params.get('pitch', 0)}")
            print(f"  F0 Method: {params.get('f0_method', 'rmvpe')}")
            print(f"  Index Rate: {params.get('index_rate', 1.0)}")
            print(f"  Filter Radius: {params.get('filter_radius', 3)}")
            print(f"  RMS Mix Rate: {params.get('rms_mix_rate', 0.25)}")
            print(f"  Protect: {params.get('protect', 0.33)}")
        else:
            print("  Using default settings (enhanced mode not available)")
            print("  Pitch: 0")
            print("  F0 Method: rmvpe")
            print("  Index Rate: 1.0")
    
    def convert_audio(self, input_file, output_file, model_id, preset_id=None, 
                     pitch=None, f0_method=None, index_rate=None):
        """音声変換実行"""
        print(f"\n🎵 Starting Audio Conversion")
        print("=" * 40)
        
        # 入力ファイルの確認
        if not os.path.exists(input_file):
            self.log_message(f"Input file not found: {input_file}", "ERROR")
            return False
        
        # モデルの確認
        models = self.list_models()
        selected_model = None
        for model in models:
            if model['id'] == model_id or model['name'] == model_id:
                selected_model = model
                break
        
        if not selected_model:
            self.log_message(f"Model not found: {model_id}", "ERROR")
            return False
        
        # パラメータの設定
        if self.enhanced_mode and preset_id is not None:
            presets = self.settings.get('audio_settings.presets', [])
            if 0 <= preset_id < len(presets):
                preset_params = presets[preset_id]['params']
                pitch = pitch or preset_params.get('pitch', 0)
                f0_method = f0_method or preset_params.get('f0_method', 'rmvpe')
                index_rate = index_rate or preset_params.get('index_rate', 1.0)
                print(f"📋 Using preset: {presets[preset_id]['name']}")
        
        # デフォルト値の設定
        if self.enhanced_mode:
            default_params = self.settings.get('audio_settings.default_params', {})
            pitch = pitch or default_params.get('pitch', 0)
            f0_method = f0_method or default_params.get('f0_method', 'rmvpe')
            index_rate = index_rate or default_params.get('index_rate', 1.0)
            filter_radius = default_params.get('filter_radius', 3)
            rms_mix_rate = default_params.get('rms_mix_rate', 0.25)
            protect = default_params.get('protect', 0.33)
        else:
            pitch = pitch or 0
            f0_method = f0_method or 'rmvpe'
            index_rate = index_rate or 1.0
            filter_radius = 3
            rms_mix_rate = 0.25
            protect = 0.33
        
        print(f"🎼 Model: {selected_model['name']}")
        print(f"📄 Input: {os.path.basename(input_file)}")
        print(f"📁 Output: {os.path.basename(output_file)}")
        print(f"⚙️ Parameters: Pitch={pitch}, F0={f0_method}, Index={index_rate}")
        
        try:
            # RVCコマンドの構築と実行
            self.log_message("Building conversion command...", "INFO")
            
            # Poetry環境の確認
            try:
                from rvc_config import POETRY_PYTHON_PATH, RVC_MODULE
                python_path = POETRY_PYTHON_PATH
                rvc_module = RVC_MODULE
                use_poetry = True
            except ImportError:
                python_path = sys.executable
                rvc_module = "rvc.wrapper.cli.cli"
                use_poetry = False
            
            # コマンドライン引数の構築
            cmd = [
                python_path,
                "-m", rvc_module,
                "infer",
                "--input", input_file,
                "--output", output_file,
                "--model", selected_model['path'],
                "--pitch", str(pitch),
                "--filter_radius", str(filter_radius),
                "--index_rate", str(index_rate),
                "--volume_envelope", str(rms_mix_rate),
                "--protect", str(protect),
                "--f0_method", f0_method,
                "--embedder_model", "hubert"
            ]
            
            # インデックスファイルがある場合
            if selected_model['index']:
                cmd.extend(["--index", selected_model['index']])
            
            self.log_message("Starting conversion process...", "INFO")
            print("\n🔄 Converting... (This may take a while)")
            
            # プロセス実行
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message("Conversion completed successfully", "INFO")
                print("✅ Conversion completed!")
                print(f"📁 Output saved to: {output_file}")
                
                # 最近使用ファイルに追加（改善モード）
                if self.enhanced_mode:
                    self.settings.add_recent_file(input_file, 'input')
                    self.settings.save_settings()
                
                return True
            else:
                error_msg = f"Conversion failed: {result.stderr}"
                self.log_message(error_msg, "ERROR")
                print(f"❌ Conversion failed:")
                print(f"   {result.stderr}")
                return False
                
        except Exception as e:
            error_msg = f"Conversion error: {str(e)}"
            self.log_message(error_msg, "ERROR")
            print(f"❌ Conversion error: {e}")
            return False
    
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
            print(f"❌ Failed to create preset '{name}'")
            return False
    
    def show_recent_files(self):
        """最近使用したファイル表示"""
        if not self.enhanced_mode:
            print("⚠️ Recent files tracking requires enhanced mode")
            return
        
        print("\n📂 Recent Files:")
        print("-" * 30)
        
        recent_files = self.settings.get_recent_files('input')
        if not recent_files:
            print("  No recent files")
            return
        
        for i, file_path in enumerate(recent_files[:10]):  # 最新10件
            exists = "✓" if os.path.exists(file_path) else "✗"
            print(f"  [{i}] {os.path.basename(file_path)} ({exists})")
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """
Voice Converter CLI - Enhanced Edition

Available Commands:
  models              List available voice models
  presets             List available presets
  settings            Show current settings
  recent              Show recent files
  convert             Convert audio file
  create-preset       Create new preset
  help                Show this help

Convert Command Usage:
  python voice_converter_cli.py convert <input_file> <output_file> <model_id> [options]
  
  Options:
    --preset <id>       Use preset (number from presets list)
    --pitch <value>     Pitch adjustment (-12 to 12)
    --f0-method <name>  F0 extraction method (rmvpe, harvest, crepe, etc.)
    --index-rate <val>  Index usage rate (0.0 to 1.0)

Examples:
  # List models
  python voice_converter_cli.py models
  
  # Convert with default settings
  python voice_converter_cli.py convert input.wav output.wav 0
  
  # Convert with preset
  python voice_converter_cli.py convert input.wav output.wav 0 --preset 0
  
  # Convert with custom parameters
  python voice_converter_cli.py convert input.wav output.wav 0 --pitch 2 --f0-method rmvpe

Enhanced Features (when available):
  ✅ Preset management
  ✅ Settings persistence
  ✅ Recent files tracking
  ✅ Advanced error handling
  ✅ Structured logging
"""
        print(help_text)

def main():
    """メイン実行関数"""
    cli = VoiceConverterCLI()
    
    if len(sys.argv) < 2:
        cli.show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "models":
        cli.list_models()
    
    elif command == "presets":
        cli.list_presets()
    
    elif command == "settings":
        cli.show_settings()
    
    elif command == "recent":
        cli.show_recent_files()
    
    elif command == "help":
        cli.show_help()
    
    elif command == "convert":
        if len(sys.argv) < 5:
            print("❌ Usage: convert <input_file> <output_file> <model_id>")
            return
        
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        model_id = sys.argv[4]
        
        # オプションパラメータの解析
        parser = argparse.ArgumentParser()
        parser.add_argument('command')
        parser.add_argument('input_file')
        parser.add_argument('output_file')
        parser.add_argument('model_id')
        parser.add_argument('--preset', type=int, help='Preset ID')
        parser.add_argument('--pitch', type=int, help='Pitch adjustment')
        parser.add_argument('--f0-method', help='F0 extraction method')
        parser.add_argument('--index-rate', type=float, help='Index usage rate')
        
        args = parser.parse_args()
        
        cli.convert_audio(
            input_file=args.input_file,
            output_file=args.output_file,
            model_id=args.model_id,
            preset_id=args.preset,
            pitch=args.pitch,
            f0_method=getattr(args, 'f0_method'),
            index_rate=getattr(args, 'index_rate')
        )
    
    elif command == "create-preset":
        if len(sys.argv) < 4:
            print("❌ Usage: create-preset <name> <description> [--pitch <val>] [--f0-method <name>] ...")
            return
        
        name = sys.argv[2]
        description = sys.argv[3]
        
        # オプションパラメータの解析
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

if __name__ == "__main__":
    main()