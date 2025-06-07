#!/usr/bin/env python3
"""
GUI版とCLI版の統合・互換性テストツール
設定ファイルの互換性とプリセット共有をテスト
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class IntegrationTester:
    """
    GUI版とCLI版の統合テスト
    """
    
    def __init__(self):
        """テスター初期化"""
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.test_results = []
        
    def log_test(self, test_name: str, result: bool, details: str = ""):
        """テスト結果の記録"""
        self.test_results.append({
            'test': test_name,
            'result': result,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"      {details}")
    
    def test_enhanced_cli_availability(self):
        """Enhanced CLI の可用性テスト"""
        try:
            from voice_converter_enhanced_cli import VoiceConverterEnhancedCLI
            cli = VoiceConverterEnhancedCLI()
            
            # 基本機能テスト
            models = cli.list_models()
            presets = cli.list_presets()
            
            self.log_test(
                "Enhanced CLI Availability",
                True,
                f"Found {len(models)} models, {len(presets)} presets"
            )
            return cli
            
        except Exception as e:
            self.log_test(
                "Enhanced CLI Availability", 
                False, 
                f"Error: {e}"
            )
            return None
    
    def test_settings_file_format(self, cli):
        """設定ファイル形式の互換性テスト"""
        try:
            settings_file = "enhanced_cli_settings.json"
            
            if not os.path.exists(settings_file):
                self.log_test(
                    "Settings File Format",
                    False,
                    "Settings file not found"
                )
                return False
            
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 必須フィールドの確認
            required_fields = [
                'version',
                'app_settings',
                'audio_settings',
                'paths',
                'metadata'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in settings:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_test(
                    "Settings File Format",
                    False,
                    f"Missing fields: {missing_fields}"
                )
                return False
            
            # プリセット形式の確認
            presets = settings.get('audio_settings', {}).get('presets', [])
            valid_presets = 0
            
            for preset in presets:
                if all(key in preset for key in ['name', 'description', 'params']):
                    valid_presets += 1
            
            self.log_test(
                "Settings File Format",
                True,
                f"Valid format with {valid_presets}/{len(presets)} valid presets"
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Settings File Format",
                False,
                f"JSON parsing error: {e}"
            )
            return False
    
    def test_preset_compatibility(self, cli):
        """プリセット互換性テスト"""
        try:
            # 一意のテスト名を生成
            import time
            test_name = f'Integration Test Preset {int(time.time())}'
            
            # サンプルプリセット作成
            test_preset = {
                'name': test_name,
                'description': 'Test preset for integration testing',
                'params': {
                    'pitch': 1,
                    'f0_method': 'harvest',
                    'index_rate': 0.85,
                    'filter_radius': 2,
                    'rms_mix_rate': 0.2,
                    'protect': 0.3
                },
                'is_default': False
            }
            
            # プリセット追加テスト
            success = cli.create_preset(
                name=test_preset['name'],
                description=test_preset['description'],
                **test_preset['params']
            )
            
            if not success:
                self.log_test(
                    "Preset Compatibility",
                    False,
                    "Failed to create test preset"
                )
                return False
            
            # プリセット取得テスト
            presets = cli.list_presets()
            test_preset_found = any(
                p['name'] == test_preset['name'] 
                for p in presets if isinstance(p, dict)
            )
            
            if not test_preset_found:
                self.log_test(
                    "Preset Compatibility",
                    False,
                    "Test preset not found after creation"
                )
                return False
            
            # プリセット削除（クリーンアップ）
            try:
                cli.delete_preset(test_preset['name'])
            except:
                pass  # 削除に失敗しても無視
            
            self.log_test(
                "Preset Compatibility",
                True,
                "Preset creation and retrieval working"
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Preset Compatibility",
                False,
                f"Error: {e}"
            )
            return False
    
    def test_settings_persistence(self, cli):
        """設定永続化テスト"""
        try:
            # 設定バックアップ
            backup_file = "test_settings_backup.json"
            if os.path.exists("enhanced_cli_settings.json"):
                shutil.copy("enhanced_cli_settings.json", backup_file)
            
            # 設定変更
            original_pitch = cli.settings.get('audio_settings.default_params.pitch', 0)
            test_pitch = original_pitch + 1
            
            cli.settings.set('audio_settings.default_params.pitch', test_pitch)
            cli.settings.save_settings()
            
            # 新しいインスタンスで設定読み込み
            from voice_converter_enhanced_cli import VoiceConverterEnhancedCLI
            new_cli = VoiceConverterEnhancedCLI()
            loaded_pitch = new_cli.settings.get('audio_settings.default_params.pitch', 0)
            
            # 設定復元
            if os.path.exists(backup_file):
                shutil.move(backup_file, "enhanced_cli_settings.json")
            
            if loaded_pitch == test_pitch:
                self.log_test(
                    "Settings Persistence",
                    True,
                    f"Settings correctly persisted (pitch: {original_pitch} -> {test_pitch})"
                )
                return True
            else:
                self.log_test(
                    "Settings Persistence",
                    False,
                    f"Settings not persisted correctly (expected: {test_pitch}, got: {loaded_pitch})"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Settings Persistence",
                False,
                f"Error: {e}"
            )
            return False
    
    def test_import_export_compatibility(self):
        """インポート/エクスポート互換性テスト"""
        try:
            from preset_manager import PresetManager
            
            manager = PresetManager()
            
            # エクスポートテスト
            export_file = "test_export.json"
            export_success = manager.export_presets(export_file)
            
            if not export_success:
                self.log_test(
                    "Import/Export Compatibility",
                    False,
                    "Export failed"
                )
                return False
            
            # ファイル検証
            if not os.path.exists(export_file):
                self.log_test(
                    "Import/Export Compatibility",
                    False,
                    "Export file not created"
                )
                return False
            
            # 検証テスト
            validation = manager.validate_preset_file(export_file)
            
            if not validation['valid']:
                self.log_test(
                    "Import/Export Compatibility",
                    False,
                    f"Export file validation failed: {validation['errors']}"
                )
                return False
            
            # クリーンアップ
            os.remove(export_file)
            
            self.log_test(
                "Import/Export Compatibility",
                True,
                "Export and validation successful"
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Import/Export Compatibility",
                False,
                f"Error: {e}"
            )
            return False
    
    def test_batch_processing_integration(self):
        """バッチ処理統合テスト"""
        try:
            from batch_converter import BatchConverterCLI
            
            batch_cli = BatchConverterCLI()
            
            if not batch_cli.enhanced_mode:
                self.log_test(
                    "Batch Processing Integration",
                    False,
                    "Enhanced mode not available for batch processing"
                )
                return False
            
            # テストディレクトリ確認
            test_dir = "test_batch_input"
            if not os.path.exists(test_dir):
                self.log_test(
                    "Batch Processing Integration",
                    False,
                    "Test batch directory not found"
                )
                return False
            
            # ファイルスキャンテスト
            files = batch_cli.scan_directory(test_dir)
            
            if len(files) == 0:
                self.log_test(
                    "Batch Processing Integration",
                    False,
                    "No files found in test directory"
                )
                return False
            
            self.log_test(
                "Batch Processing Integration",
                True,
                f"Batch processing available, found {len(files)} test files"
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Batch Processing Integration",
                False,
                f"Error: {e}"
            )
            return False
    
    def test_error_handling_integration(self):
        """エラーハンドリング統合テスト"""
        try:
            # エラーログディレクトリ確認
            log_dir = "enhanced_cli_logs"
            
            if not os.path.exists(log_dir):
                self.log_test(
                    "Error Handling Integration",
                    False,
                    "Log directory not found"
                )
                return False
            
            # ログファイル確認
            log_files = list(Path(log_dir).glob("*.log"))
            
            if len(log_files) == 0:
                self.log_test(
                    "Error Handling Integration",
                    False,
                    "No log files found"
                )
                return False
            
            # 最新ログファイルの内容確認
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_log, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            if "RVC_GUI" in log_content:
                self.log_test(
                    "Error Handling Integration",
                    True,
                    f"Error handling active, {len(log_files)} log files found"
                )
                return True
            else:
                self.log_test(
                    "Error Handling Integration",
                    False,
                    "Log content format unexpected"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Error Handling Integration",
                False,
                f"Error: {e}"
            )
            return False
    
    def run_all_tests(self):
        """全テストの実行"""
        print("🧪 Running Integration Tests")
        print("=" * 50)
        
        # Enhanced CLI可用性テスト
        cli = self.test_enhanced_cli_availability()
        
        if cli is None:
            print("\n❌ Cannot proceed with other tests (Enhanced CLI not available)")
            return self.generate_report()
        
        # 各テストの実行
        self.test_settings_file_format(cli)
        self.test_preset_compatibility(cli)
        self.test_settings_persistence(cli)
        self.test_import_export_compatibility()
        self.test_batch_processing_integration()
        self.test_error_handling_integration()
        
        return self.generate_report()
    
    def generate_report(self):
        """テストレポートの生成"""
        passed = sum(1 for test in self.test_results if test['result'])
        total = len(self.test_results)
        
        print(f"\n📊 Integration Test Results")
        print("=" * 50)
        print(f"Tests passed: {passed}/{total}")
        print(f"Success rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        if passed == total:
            print("🎉 All integration tests passed!")
        else:
            print("⚠️ Some tests failed - check details above")
        
        # レポートファイル保存
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total,
                'passed': passed,
                'failed': total - passed,
                'success_rate': (passed/total*100) if total > 0 else 0
            },
            'results': self.test_results
        }
        
        report_file = "integration_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return passed == total


def main():
    """メイン実行関数"""
    tester = IntegrationTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()