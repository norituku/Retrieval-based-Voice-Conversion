#!/usr/bin/env python3
"""
プリセット管理拡張ツール
プリセットのインポート・エクスポート・共有機能
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class PresetManager:
    """
    プリセット管理システム
    プリセットの高度な管理とシェアリング機能を提供
    """
    
    def __init__(self, settings_file: str = "enhanced_cli_settings.json"):
        """
        プリセット管理システムの初期化
        
        Args:
            settings_file: 設定ファイルパス
        """
        # Enhanced CLIのインポート
        try:
            from voice_converter_enhanced_cli import VoiceConverterEnhancedCLI
            self.cli = VoiceConverterEnhancedCLI()
            self.enhanced_mode = True
            print("✅ Enhanced CLI loaded for preset management")
        except Exception as e:
            print(f"⚠️ Enhanced CLI not available: {e}")
            self.enhanced_mode = False
            
        self.settings_file = settings_file
        
    def export_presets(self, export_file: str, preset_names: List[str] = None) -> bool:
        """
        プリセットのエクスポート
        
        Args:
            export_file: エクスポート先ファイル
            preset_names: エクスポートするプリセット名のリスト（Noneで全て）
            
        Returns:
            エクスポート成功の可否
        """
        if not self.enhanced_mode:
            print("❌ Enhanced mode required")
            return False
            
        try:
            presets = self.cli.settings.get('audio_settings.presets', [])
            
            # フィルタリング
            if preset_names:
                filtered_presets = [
                    p for p in presets 
                    if p.get('name') in preset_names
                ]
                if len(filtered_presets) != len(preset_names):
                    found_names = [p.get('name') for p in filtered_presets]
                    missing = set(preset_names) - set(found_names)
                    print(f"⚠️ Warning: Presets not found: {missing}")
            else:
                filtered_presets = presets
                
            # エクスポートデータの作成
            export_data = {
                'format_version': '1.0',
                'export_timestamp': datetime.now().isoformat(),
                'app_version': self.cli.settings.get('version', '1.0.0'),
                'exported_by': 'Voice Converter Enhanced CLI',
                'preset_count': len(filtered_presets),
                'presets': filtered_presets,
                'metadata': {
                    'f0_methods': self.cli.settings.get('audio_settings.f0_methods', []),
                    'parameter_ranges': {
                        'pitch': {'min': -24, 'max': 24, 'default': 0},
                        'index_rate': {'min': 0.0, 'max': 1.0, 'default': 1.0},
                        'filter_radius': {'min': 0, 'max': 7, 'default': 3},
                        'rms_mix_rate': {'min': 0.0, 'max': 1.0, 'default': 0.25},
                        'protect': {'min': 0.0, 'max': 0.5, 'default': 0.33}
                    }
                }
            }
            
            # ファイル保存
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Exported {len(filtered_presets)} preset(s) to: {export_file}")
            
            # エクスポート詳細
            for preset in filtered_presets:
                default_mark = " (Default)" if preset.get('is_default', False) else ""
                print(f"   - {preset['name']}{default_mark}")
                
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
            
    def import_presets(self, import_file: str, overwrite: bool = False, 
                      set_default: str = None) -> bool:
        """
        プリセットのインポート
        
        Args:
            import_file: インポート元ファイル
            overwrite: 既存プリセットを上書きするか
            set_default: デフォルトに設定するプリセット名
            
        Returns:
            インポート成功の可否
        """
        if not self.enhanced_mode:
            print("❌ Enhanced mode required")
            return False
            
        try:
            # インポートファイル読み込み
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
                
            # フォーマット検証
            if 'presets' not in import_data:
                print("❌ Invalid preset file format")
                return False
                
            imported_presets = import_data['presets']
            print(f"📦 Importing {len(imported_presets)} preset(s) from: {import_file}")
            
            # 現在のプリセット取得
            current_presets = self.cli.settings.get('audio_settings.presets', [])
            current_names = [p.get('name') for p in current_presets]
            
            imported_count = 0
            skipped_count = 0
            updated_count = 0
            
            for preset in imported_presets:
                preset_name = preset.get('name')
                if not preset_name:
                    print(f"⚠️ Skipping preset without name")
                    skipped_count += 1
                    continue
                    
                # 既存チェック
                exists = preset_name in current_names
                
                if exists and not overwrite:
                    print(f"⚠️ Skipped existing preset: {preset_name}")
                    skipped_count += 1
                    continue
                    
                # デフォルト設定の処理
                if set_default == preset_name:
                    # 他のプリセットのデフォルトを解除
                    for p in current_presets:
                        p['is_default'] = False
                    preset['is_default'] = True
                elif set_default is None:
                    # デフォルト設定を維持（既存の場合）
                    if exists:
                        existing_preset = next(p for p in current_presets if p['name'] == preset_name)
                        preset['is_default'] = existing_preset.get('is_default', False)
                    else:
                        preset['is_default'] = False
                else:
                    preset['is_default'] = False
                    
                # プリセット追加/更新
                if exists:
                    # 既存プリセットを更新
                    for i, p in enumerate(current_presets):
                        if p['name'] == preset_name:
                            current_presets[i] = preset
                            break
                    updated_count += 1
                    print(f"🔄 Updated preset: {preset_name}")
                else:
                    # 新規プリセットを追加
                    current_presets.append(preset)
                    imported_count += 1
                    print(f"➕ Added preset: {preset_name}")
                    
            # 設定保存
            self.cli.settings.set('audio_settings.presets', current_presets)
            self.cli.settings.save_settings()
            
            print(f"\n📊 Import Summary:")
            print(f"   ➕ Added: {imported_count}")
            print(f"   🔄 Updated: {updated_count}")
            print(f"   ⚠️ Skipped: {skipped_count}")
            print(f"   ✅ Total processed: {imported_count + updated_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
            
    def list_preset_files(self, directory: str = ".") -> List[str]:
        """
        プリセットファイルの検索
        
        Args:
            directory: 検索ディレクトリ
            
        Returns:
            プリセットファイルのリスト
        """
        preset_files = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return preset_files
            
        # .jsonファイルを検索してプリセットファイルを特定
        for json_file in dir_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if 'presets' in data and isinstance(data['presets'], list):
                    preset_files.append(str(json_file))
                    
            except (json.JSONDecodeError, IOError):
                continue
                
        return sorted(preset_files)
        
    def validate_preset_file(self, preset_file: str) -> Dict[str, Any]:
        """
        プリセットファイルの検証
        
        Args:
            preset_file: プリセットファイル
            
        Returns:
            検証結果
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        try:
            with open(preset_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 必須フィールドチェック
            if 'presets' not in data:
                result['errors'].append("Missing 'presets' field")
                return result
                
            presets = data['presets']
            if not isinstance(presets, list):
                result['errors'].append("'presets' must be a list")
                return result
                
            # プリセット検証
            valid_presets = 0
            preset_names = set()
            
            for i, preset in enumerate(presets):
                if not isinstance(preset, dict):
                    result['warnings'].append(f"Preset {i} is not a dictionary")
                    continue
                    
                name = preset.get('name')
                if not name:
                    result['warnings'].append(f"Preset {i} missing name")
                    continue
                    
                if name in preset_names:
                    result['warnings'].append(f"Duplicate preset name: {name}")
                else:
                    preset_names.add(name)
                    
                # パラメータ検証
                params = preset.get('params', {})
                if not isinstance(params, dict):
                    result['warnings'].append(f"Preset '{name}' params is not a dictionary")
                    continue
                    
                valid_presets += 1
                
            # 結果まとめ
            result['valid'] = len(result['errors']) == 0 and valid_presets > 0
            result['info'] = {
                'total_presets': len(presets),
                'valid_presets': valid_presets,
                'format_version': data.get('format_version', 'unknown'),
                'export_timestamp': data.get('export_timestamp'),
                'app_version': data.get('app_version')
            }
            
        except json.JSONDecodeError as e:
            result['errors'].append(f"Invalid JSON format: {e}")
        except IOError as e:
            result['errors'].append(f"File reading error: {e}")
        except Exception as e:
            result['errors'].append(f"Validation error: {e}")
            
        return result
        
    def create_sample_presets(self, output_file: str = "sample_presets.json"):
        """
        サンプルプリセットファイルの作成
        
        Args:
            output_file: 出力ファイル名
        """
        sample_presets = [
            {
                'name': 'ボーカル専用高品質',
                'description': '歌声変換に最適化された高品質設定',
                'params': {
                    'pitch': 0,
                    'f0_method': 'mangio-crepe',
                    'index_rate': 1.0,
                    'filter_radius': 3,
                    'rms_mix_rate': 0.3,
                    'protect': 0.4
                },
                'is_default': False,
                'category': 'vocal',
                'quality_level': 'high'
            },
            {
                'name': 'スピーチ最適化',
                'description': '話し声変換用の設定',
                'params': {
                    'pitch': 0,
                    'f0_method': 'harvest',
                    'index_rate': 0.9,
                    'filter_radius': 2,
                    'rms_mix_rate': 0.15,
                    'protect': 0.2
                },
                'is_default': False,
                'category': 'speech',
                'quality_level': 'medium'
            },
            {
                'name': '低CPU使用',
                'description': 'CPU負荷を抑えた高速変換',
                'params': {
                    'pitch': 0,
                    'f0_method': 'harvest',
                    'index_rate': 0.6,
                    'filter_radius': 1,
                    'rms_mix_rate': 0.1,
                    'protect': 0.15
                },
                'is_default': False,
                'category': 'performance',
                'quality_level': 'low'
            }
        ]
        
        export_data = {
            'format_version': '1.0',
            'export_timestamp': datetime.now().isoformat(),
            'app_version': '1.0.0',
            'exported_by': 'Voice Converter Enhanced CLI - Sample Generator',
            'preset_count': len(sample_presets),
            'presets': sample_presets,
            'metadata': {
                'description': 'Sample presets for Voice Converter',
                'categories': ['vocal', 'speech', 'performance'],
                'quality_levels': ['high', 'medium', 'low']
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Sample presets created: {output_file}")
        print(f"   - {len(sample_presets)} presets included")
        
        for preset in sample_presets:
            print(f"   - {preset['name']} ({preset['category']}, {preset['quality_level']} quality)")


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="Preset Manager - Advanced preset management tool"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # エクスポートコマンド
    export_parser = subparsers.add_parser('export', help='Export presets')
    export_parser.add_argument('output_file', help='Output file path')
    export_parser.add_argument('--presets', nargs='+', help='Specific preset names to export')
    
    # インポートコマンド
    import_parser = subparsers.add_parser('import', help='Import presets')
    import_parser.add_argument('input_file', help='Input file path')
    import_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing presets')
    import_parser.add_argument('--set-default', help='Set specific preset as default')
    
    # 検証コマンド
    validate_parser = subparsers.add_parser('validate', help='Validate preset file')
    validate_parser.add_argument('preset_file', help='Preset file to validate')
    
    # リストコマンド
    list_parser = subparsers.add_parser('list', help='List preset files')
    list_parser.add_argument('--directory', default='.', help='Directory to search')
    
    # サンプル生成コマンド
    sample_parser = subparsers.add_parser('create-sample', help='Create sample presets')
    sample_parser.add_argument('--output', default='sample_presets.json', help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    manager = PresetManager()
    
    if args.command == 'export':
        manager.export_presets(args.output_file, args.presets)
        
    elif args.command == 'import':
        manager.import_presets(args.input_file, args.overwrite, args.set_default)
        
    elif args.command == 'validate':
        result = manager.validate_preset_file(args.preset_file)
        
        print(f"📋 Validation Results for: {args.preset_file}")
        print("=" * 50)
        
        if result['valid']:
            print("✅ File is valid")
        else:
            print("❌ File has issues")
            
        if result['errors']:
            print("\n❌ Errors:")
            for error in result['errors']:
                print(f"   - {error}")
                
        if result['warnings']:
            print("\n⚠️ Warnings:")
            for warning in result['warnings']:
                print(f"   - {warning}")
                
        if result['info']:
            print("\n📊 File Information:")
            info = result['info']
            for key, value in info.items():
                print(f"   {key}: {value}")
                
    elif args.command == 'list':
        files = manager.list_preset_files(args.directory)
        
        print(f"📂 Preset files in: {args.directory}")
        print("-" * 30)
        
        if not files:
            print("  No preset files found")
        else:
            for file_path in files:
                # ファイル情報を表示
                try:
                    result = manager.validate_preset_file(file_path)
                    if result['valid']:
                        count = result['info'].get('valid_presets', 0)
                        print(f"  ✅ {file_path} ({count} presets)")
                    else:
                        print(f"  ⚠️ {file_path} (invalid)")
                except:
                    print(f"  ❌ {file_path} (error)")
                    
    elif args.command == 'create-sample':
        manager.create_sample_presets(args.output)


if __name__ == "__main__":
    main()