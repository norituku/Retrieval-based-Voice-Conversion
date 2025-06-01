#!/usr/bin/env python3
"""
バッチ処理拡張モジュール
複数ファイルの一括変換機能
"""

import os
import sys
import json
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, Future
import argparse

class BatchProcessor:
    """
    バッチ処理エンジン
    並列処理とプログレス管理を提供
    """
    
    def __init__(self, max_workers: int = 2):
        """
        バッチプロセッサの初期化
        
        Args:
            max_workers: 最大並列処理数
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = []
        self.results = []
        self.progress_callback = None
        self.cancel_flag = threading.Event()
        
    def add_task(self, task: Dict[str, Any]):
        """
        タスクの追加
        
        Args:
            task: タスク情報（input, output, params等）
        """
        task['id'] = len(self.tasks)
        task['status'] = 'pending'
        task['start_time'] = None
        task['end_time'] = None
        task['error'] = None
        self.tasks.append(task)
        
    def set_progress_callback(self, callback: Callable):
        """プログレスコールバックの設定"""
        self.progress_callback = callback
        
    def process_task(self, task: Dict[str, Any], converter_func: Callable) -> Dict[str, Any]:
        """
        単一タスクの処理
        
        Args:
            task: タスク情報
            converter_func: 変換関数
            
        Returns:
            処理結果
        """
        if self.cancel_flag.is_set():
            task['status'] = 'cancelled'
            return task
            
        task['status'] = 'processing'
        task['start_time'] = datetime.now()
        
        if self.progress_callback:
            self.progress_callback(task)
        
        try:
            # 変換実行
            result = converter_func(
                input_file=task['input'],
                output_file=task['output'],
                model_id=task['model_id'],
                **task.get('params', {})
            )
            
            task['status'] = 'completed' if result else 'failed'
            task['result'] = result
            
        except Exception as e:
            task['status'] = 'error'
            task['error'] = str(e)
            
        task['end_time'] = datetime.now()
        task['duration'] = (task['end_time'] - task['start_time']).total_seconds()
        
        if self.progress_callback:
            self.progress_callback(task)
            
        return task
        
    def run(self, converter_func: Callable) -> List[Dict[str, Any]]:
        """
        バッチ処理の実行
        
        Args:
            converter_func: 変換関数
            
        Returns:
            処理結果リスト
        """
        self.cancel_flag.clear()
        futures = []
        
        # タスクをサブミット
        for task in self.tasks:
            future = self.executor.submit(self.process_task, task, converter_func)
            futures.append(future)
            
        # 結果を収集
        self.results = []
        for future in futures:
            try:
                result = future.result()
                self.results.append(result)
            except Exception as e:
                print(f"Task execution error: {e}")
                
        return self.results
        
    def cancel(self):
        """処理のキャンセル"""
        self.cancel_flag.set()
        self.executor.shutdown(wait=False)
        
    def get_stats(self) -> Dict[str, Any]:
        """統計情報の取得"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t['status'] == 'completed')
        failed = sum(1 for t in self.tasks if t['status'] in ['failed', 'error'])
        cancelled = sum(1 for t in self.tasks if t['status'] == 'cancelled')
        pending = sum(1 for t in self.tasks if t['status'] == 'pending')
        processing = sum(1 for t in self.tasks if t['status'] == 'processing')
        
        total_duration = sum(
            t.get('duration', 0) for t in self.tasks 
            if t.get('duration') is not None
        )
        
        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'cancelled': cancelled,
            'pending': pending,
            'processing': processing,
            'success_rate': (completed / total * 100) if total > 0 else 0,
            'total_duration': total_duration,
            'average_duration': total_duration / completed if completed > 0 else 0
        }


class BatchConverterCLI:
    """
    バッチ変換CLI
    Enhanced CLIと統合して複数ファイル変換を実現
    """
    
    def __init__(self):
        """初期化"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Enhanced CLIのインポート
        try:
            from voice_converter_enhanced_cli import VoiceConverterEnhancedCLI
            self.converter = VoiceConverterEnhancedCLI()
            self.enhanced_mode = True
            print("✅ Enhanced CLI loaded for batch processing")
        except Exception as e:
            print(f"⚠️ Enhanced CLI not available: {e}")
            self.enhanced_mode = False
            
    def scan_directory(self, input_dir: str, pattern: str = "*.wav") -> List[str]:
        """
        ディレクトリ内の音声ファイルをスキャン
        
        Args:
            input_dir: 入力ディレクトリ
            pattern: ファイルパターン
            
        Returns:
            ファイルパスのリスト
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"❌ Directory not found: {input_dir}")
            return []
            
        # サポートされる拡張子
        extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        
        files = []
        if pattern == "*.*":
            # 全音声ファイルを検索
            for ext in extensions:
                files.extend(input_path.glob(f"*{ext}"))
        else:
            # 指定パターンで検索
            files = list(input_path.glob(pattern))
            
        # 音声ファイルのみフィルタ
        audio_files = [
            str(f) for f in files 
            if f.suffix.lower() in extensions
        ]
        
        return sorted(audio_files)
        
    def create_batch_tasks(self, input_files: List[str], output_dir: str, 
                          model_id: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        バッチタスクの作成
        
        Args:
            input_files: 入力ファイルリスト
            output_dir: 出力ディレクトリ
            model_id: モデルID
            params: 変換パラメータ
            
        Returns:
            タスクリスト
        """
        tasks = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for input_file in input_files:
            input_name = Path(input_file).stem
            output_file = str(output_path / f"{input_name}_converted.wav")
            
            task = {
                'input': input_file,
                'output': output_file,
                'model_id': model_id,
                'params': params.copy()
            }
            tasks.append(task)
            
        return tasks
        
    def progress_callback(self, task: Dict[str, Any]):
        """プログレス表示コールバック"""
        status_emoji = {
            'pending': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'failed': '❌',
            'error': '⚠️',
            'cancelled': '🚫'
        }
        
        emoji = status_emoji.get(task['status'], '❓')
        filename = os.path.basename(task['input'])
        
        if task['status'] == 'processing':
            print(f"{emoji} [{task['id']+1}] Processing: {filename}")
        elif task['status'] == 'completed':
            duration = task.get('duration', 0)
            print(f"{emoji} [{task['id']+1}] Completed: {filename} ({duration:.1f}s)")
        elif task['status'] in ['failed', 'error']:
            error = task.get('error', 'Unknown error')
            print(f"{emoji} [{task['id']+1}] Failed: {filename} - {error}")
            
    def run_batch(self, input_dir: str, output_dir: str, model_id: str,
                 pattern: str = "*.wav", max_workers: int = 2, **params):
        """
        バッチ変換の実行
        
        Args:
            input_dir: 入力ディレクトリ
            output_dir: 出力ディレクトリ
            model_id: モデルID
            pattern: ファイルパターン
            max_workers: 最大並列数
            **params: 変換パラメータ
        """
        print(f"\n🔄 Batch Audio Conversion")
        print("=" * 50)
        
        # ファイルスキャン
        input_files = self.scan_directory(input_dir, pattern)
        if not input_files:
            print("❌ No audio files found")
            return
            
        print(f"📁 Found {len(input_files)} audio file(s)")
        for i, f in enumerate(input_files[:5]):  # 最初の5件表示
            print(f"   [{i+1}] {os.path.basename(f)}")
        if len(input_files) > 5:
            print(f"   ... and {len(input_files)-5} more")
            
        # タスク作成
        tasks = self.create_batch_tasks(input_files, output_dir, model_id, params)
        
        # バッチプロセッサ初期化
        processor = BatchProcessor(max_workers=max_workers)
        processor.set_progress_callback(self.progress_callback)
        
        for task in tasks:
            processor.add_task(task)
            
        print(f"\n🚀 Starting batch conversion with {max_workers} worker(s)")
        print(f"📂 Output directory: {output_dir}")
        
        start_time = datetime.now()
        
        # 変換実行
        if self.enhanced_mode:
            results = processor.run(self.converter.convert_audio)
        else:
            print("❌ Enhanced mode required for batch processing")
            return
            
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # 統計表示
        stats = processor.get_stats()
        print(f"\n📊 Batch Conversion Summary")
        print("=" * 50)
        print(f"Total files: {stats['total']}")
        print(f"✅ Completed: {stats['completed']}")
        print(f"❌ Failed: {stats['failed']}")
        print(f"🚫 Cancelled: {stats['cancelled']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Total time: {total_duration:.1f}s")
        print(f"Average time per file: {stats['average_duration']:.1f}s")
        
        # 結果をJSONに保存
        report_file = os.path.join(output_dir, "batch_report.json")
        report = {
            'timestamp': datetime.now().isoformat(),
            'input_dir': input_dir,
            'output_dir': output_dir,
            'model_id': model_id,
            'parameters': params,
            'stats': stats,
            'results': [
                {
                    'input': t['input'],
                    'output': t['output'],
                    'status': t['status'],
                    'duration': t.get('duration'),
                    'error': t.get('error')
                }
                for t in results
            ]
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"\n📄 Batch report saved to: {report_file}")


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="Batch Audio Converter - Process multiple files at once"
    )
    
    parser.add_argument('input_dir', help='Input directory containing audio files')
    parser.add_argument('output_dir', help='Output directory for converted files')
    parser.add_argument('model_id', help='Model ID or name')
    
    parser.add_argument('--pattern', default='*.wav',
                       help='File pattern to match (default: *.wav)')
    parser.add_argument('--workers', type=int, default=2,
                       help='Number of parallel workers (default: 2)')
    parser.add_argument('--preset', type=int,
                       help='Preset ID to use')
    parser.add_argument('--pitch', type=int,
                       help='Pitch adjustment')
    parser.add_argument('--f0-method',
                       help='F0 extraction method')
    parser.add_argument('--index-rate', type=float,
                       help='Index usage rate')
    
    args = parser.parse_args()
    
    # パラメータ準備
    params = {}
    if args.preset is not None:
        params['preset_id'] = args.preset
    if args.pitch is not None:
        params['pitch'] = args.pitch
    if args.f0_method:
        params['f0_method'] = args.f0_method
    if args.index_rate is not None:
        params['index_rate'] = args.index_rate
        
    # バッチ変換実行
    cli = BatchConverterCLI()
    cli.run_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        model_id=args.model_id,
        pattern=args.pattern,
        max_workers=args.workers,
        **params
    )


if __name__ == "__main__":
    main()