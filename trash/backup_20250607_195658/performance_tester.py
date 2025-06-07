#!/usr/bin/env python3
"""
RVC パフォーマンステストツール
音声変換処理の性能測定とボトルネック分析
"""

import os
import sys
import time
import json
import psutil
import tracemalloc
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from scipy.io import wavfile
import statistics

class PerformanceTester:
    """
    パフォーマンステストの実行と分析
    """
    
    def __init__(self):
        """テスター初期化"""
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.test_results = []
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> Dict[str, Any]:
        """システム情報の取得"""
        import platform
        
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'processor': platform.processor(),
            'cpu_count': cpu_count,
            'cpu_freq_current': cpu_freq.current if cpu_freq else None,
            'cpu_freq_max': cpu_freq.max if cpu_freq else None,
            'memory_total': memory.total,
            'memory_available': memory.available,
            'python_version': sys.version,
            'timestamp': datetime.now().isoformat()
        }
    
    def log_test(self, test_name: str, metrics: Dict[str, Any]):
        """テスト結果の記録"""
        self.test_results.append({
            'test': test_name,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"\n📊 {test_name}")
        print("=" * 50)
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
    
    def test_file_loading_performance(self) -> Dict[str, Any]:
        """ファイル読み込みパフォーマンステスト"""
        try:
            # テスト用音声ファイルの作成
            test_file = "test_performance_audio.wav"
            sample_rate = 44100
            duration = 10  # 10秒の音声
            samples = np.random.randn(sample_rate * duration) * 0.1
            wavfile.write(test_file, sample_rate, samples.astype(np.float32))
            
            # 読み込みテスト
            load_times = []
            
            for i in range(5):
                start_time = time.time()
                data, sr = wavfile.read(test_file)
                load_time = time.time() - start_time
                load_times.append(load_time)
            
            # クリーンアップ
            os.remove(test_file)
            
            metrics = {
                'file_size_mb': (sample_rate * duration * 4) / (1024 * 1024),
                'avg_load_time': statistics.mean(load_times),
                'min_load_time': min(load_times),
                'max_load_time': max(load_times),
                'std_dev': statistics.stdev(load_times) if len(load_times) > 1 else 0,
                'status': 'success'
            }
            
            self.log_test("File Loading Performance", metrics)
            return metrics
            
        except Exception as e:
            metrics = {
                'status': 'failed',
                'error': str(e)
            }
            self.log_test("File Loading Performance", metrics)
            return metrics
    
    def test_preset_performance(self) -> Dict[str, Any]:
        """プリセット操作パフォーマンステスト"""
        try:
            from voice_converter_enhanced_cli import VoiceConverterEnhancedCLI
            
            cli = VoiceConverterEnhancedCLI()
            
            # プリセット作成テスト
            create_times = []
            for i in range(10):
                start_time = time.time()
                cli.create_preset(
                    name=f"Performance Test {i}",
                    description="Performance test preset",
                    pitch=i % 12,
                    f0_method="harvest",
                    index_rate=0.8
                )
                create_time = time.time() - start_time
                create_times.append(create_time)
            
            # プリセット読み込みテスト
            list_times = []
            for i in range(10):
                start_time = time.time()
                presets = cli.list_presets()
                list_time = time.time() - start_time
                list_times.append(list_time)
            
            # プリセット削除（クリーンアップ）
            delete_times = []
            for i in range(10):
                start_time = time.time()
                try:
                    cli.delete_preset(f"Performance Test {i}")
                except:
                    pass
                delete_time = time.time() - start_time
                delete_times.append(delete_time)
            
            metrics = {
                'avg_create_time': statistics.mean(create_times),
                'avg_list_time': statistics.mean(list_times),
                'avg_delete_time': statistics.mean(delete_times),
                'total_presets_tested': 10,
                'status': 'success'
            }
            
            self.log_test("Preset Operations Performance", metrics)
            return metrics
            
        except Exception as e:
            metrics = {
                'status': 'failed',
                'error': str(e)
            }
            self.log_test("Preset Operations Performance", metrics)
            return metrics
    
    def test_memory_usage(self) -> Dict[str, Any]:
        """メモリ使用量テスト"""
        try:
            # トレースの開始
            tracemalloc.start()
            
            # メモリ使用量の初期値
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # 大きなデータ構造の作成
            large_data = []
            for i in range(100):
                # 1MBのデータを作成
                data = np.random.randn(250000).astype(np.float32)
                large_data.append(data)
            
            # ピークメモリ使用量
            peak_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # メモリ統計
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # データのクリア
            large_data.clear()
            
            # GC後のメモリ
            import gc
            gc.collect()
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            metrics = {
                'initial_memory_mb': initial_memory,
                'peak_memory_mb': peak_memory,
                'final_memory_mb': final_memory,
                'memory_increase_mb': peak_memory - initial_memory,
                'traced_current_mb': current / 1024 / 1024,
                'traced_peak_mb': peak / 1024 / 1024,
                'memory_released': peak_memory > final_memory,
                'status': 'success'
            }
            
            self.log_test("Memory Usage Test", metrics)
            return metrics
            
        except Exception as e:
            metrics = {
                'status': 'failed',
                'error': str(e)
            }
            self.log_test("Memory Usage Test", metrics)
            return metrics
    
    def test_batch_processing_performance(self) -> Dict[str, Any]:
        """バッチ処理パフォーマンステスト"""
        try:
            from batch_converter import BatchProcessor
            
            processor = BatchProcessor(max_workers=2)
            
            # テストタスクの作成
            tasks = []
            for i in range(10):
                task = {
                    'input': f'test_input_{i}.wav',
                    'output': f'test_output_{i}.wav',
                    'params': {
                        'pitch': i % 12,
                        'f0_method': 'harvest'
                    }
                }
                tasks.append(task)
            
            # タスク追加時間の測定
            add_times = []
            for task in tasks:
                start_time = time.time()
                processor.add_task(task)
                add_time = time.time() - start_time
                add_times.append(add_time)
            
            metrics = {
                'task_count': len(tasks),
                'avg_add_time': statistics.mean(add_times),
                'max_workers': processor.max_workers,
                'status': 'success'
            }
            
            self.log_test("Batch Processing Performance", metrics)
            return metrics
            
        except Exception as e:
            metrics = {
                'status': 'failed',
                'error': str(e)
            }
            self.log_test("Batch Processing Performance", metrics)
            return metrics
    
    def test_settings_io_performance(self) -> Dict[str, Any]:
        """設定ファイルI/Oパフォーマンステスト"""
        try:
            # 大きな設定ファイルの作成
            test_settings = {
                'version': '1.0.0',
                'presets': []
            }
            
            # 100個のプリセットを追加
            for i in range(100):
                preset = {
                    'name': f'Test Preset {i}',
                    'description': f'Description for preset {i}',
                    'params': {
                        'pitch': i % 24,
                        'f0_method': ['harvest', 'crepe', 'rmvpe'][i % 3],
                        'index_rate': 0.5 + (i % 50) / 100,
                        'filter_radius': i % 10,
                        'rms_mix_rate': (i % 30) / 100,
                        'protect': (i % 40) / 100
                    }
                }
                test_settings['presets'].append(preset)
            
            # 書き込みテスト
            write_times = []
            test_file = 'test_settings_performance.json'
            
            for i in range(5):
                start_time = time.time()
                with open(test_file, 'w', encoding='utf-8') as f:
                    json.dump(test_settings, f, indent=2)
                write_time = time.time() - start_time
                write_times.append(write_time)
            
            # 読み込みテスト
            read_times = []
            for i in range(5):
                start_time = time.time()
                with open(test_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                read_time = time.time() - start_time
                read_times.append(read_time)
            
            # ファイルサイズ
            file_size = os.path.getsize(test_file) / 1024  # KB
            
            # クリーンアップ
            os.remove(test_file)
            
            metrics = {
                'preset_count': 100,
                'file_size_kb': file_size,
                'avg_write_time': statistics.mean(write_times),
                'avg_read_time': statistics.mean(read_times),
                'write_speed_kb_per_sec': file_size / statistics.mean(write_times),
                'read_speed_kb_per_sec': file_size / statistics.mean(read_times),
                'status': 'success'
            }
            
            self.log_test("Settings I/O Performance", metrics)
            return metrics
            
        except Exception as e:
            metrics = {
                'status': 'failed',
                'error': str(e)
            }
            self.log_test("Settings I/O Performance", metrics)
            return metrics
    
    def run_all_tests(self) -> Dict[str, Any]:
        """全パフォーマンステストの実行"""
        print("🚀 RVC Performance Test Suite")
        print("=" * 50)
        print(f"System: {self.system_info['platform']} {self.system_info['platform_version']}")
        print(f"CPU: {self.system_info['cpu_count']} cores @ {self.system_info['cpu_freq_current']:.0f} MHz")
        print(f"Memory: {self.system_info['memory_total'] / (1024**3):.1f} GB")
        print("=" * 50)
        
        # 各テストの実行
        self.test_file_loading_performance()
        self.test_preset_performance()
        self.test_memory_usage()
        self.test_batch_processing_performance()
        self.test_settings_io_performance()
        
        # サマリーの生成
        passed = sum(1 for test in self.test_results if test['metrics'].get('status') == 'success')
        total = len(self.test_results)
        
        print("\n📊 Performance Test Summary")
        print("=" * 50)
        print(f"Tests passed: {passed}/{total}")
        print(f"Success rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        # パフォーマンス基準の評価
        performance_issues = []
        
        for test in self.test_results:
            if test['test'] == 'File Loading Performance' and test['metrics'].get('status') == 'success':
                if test['metrics']['avg_load_time'] > 1.0:
                    performance_issues.append("File loading is slow (>1s)")
            
            if test['test'] == 'Preset Operations Performance' and test['metrics'].get('status') == 'success':
                if test['metrics']['avg_create_time'] > 0.1:
                    performance_issues.append("Preset creation is slow (>100ms)")
            
            if test['test'] == 'Memory Usage Test' and test['metrics'].get('status') == 'success':
                if test['metrics']['memory_increase_mb'] > 500:
                    performance_issues.append("High memory usage (>500MB increase)")
        
        if performance_issues:
            print("\n⚠️ Performance Issues Found:")
            for issue in performance_issues:
                print(f"  - {issue}")
        else:
            print("\n✅ All performance metrics within acceptable ranges")
        
        # レポートの保存
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.system_info,
            'summary': {
                'total_tests': total,
                'passed': passed,
                'failed': total - passed,
                'success_rate': (passed/total*100) if total > 0 else 0
            },
            'results': self.test_results,
            'performance_issues': performance_issues
        }
        
        report_file = "performance_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return report


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RVC Performance Testing Tool')
    parser.add_argument('--test', type=str, help='Run specific test')
    parser.add_argument('--list', action='store_true', help='List available tests')
    
    args = parser.parse_args()
    
    tester = PerformanceTester()
    
    if args.list:
        print("Available tests:")
        print("  - file_loading")
        print("  - preset_operations")
        print("  - memory_usage")
        print("  - batch_processing")
        print("  - settings_io")
        print("  - all (default)")
        return
    
    if args.test:
        test_map = {
            'file_loading': tester.test_file_loading_performance,
            'preset_operations': tester.test_preset_performance,
            'memory_usage': tester.test_memory_usage,
            'batch_processing': tester.test_batch_processing_performance,
            'settings_io': tester.test_settings_io_performance
        }
        
        if args.test in test_map:
            test_map[args.test]()
        else:
            print(f"Unknown test: {args.test}")
            print("Use --list to see available tests")
    else:
        tester.run_all_tests()


if __name__ == "__main__":
    main()