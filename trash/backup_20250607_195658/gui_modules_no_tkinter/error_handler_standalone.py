#!/usr/bin/env python3
"""
統一エラーハンドリングとロギングシステム
階層的アプローチによるエラー処理とログ管理
"""

import os
import sys
import logging
import traceback
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
import json

class ErrorLevel(Enum):
    """エラーレベルの定義"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorCategory(Enum):
    """エラーカテゴリーの定義"""
    INPUT_ERROR = "input_error"           # 入力エラー（検証で防げるエラー）
    PROCESSING_ERROR = "processing_error" # 処理エラー（音声変換中のエラー）
    SYSTEM_ERROR = "system_error"         # システムエラー（環境依存のエラー）
    NETWORK_ERROR = "network_error"       # ネットワークエラー
    FILE_ERROR = "file_error"             # ファイル操作エラー
    MODEL_ERROR = "model_error"           # モデル関連エラー
    UI_ERROR = "ui_error"                 # UI関連エラー

class LogRotation:
    """ログローテーション管理"""
    
    def __init__(self, log_dir: str, max_files: int = 5, max_size_mb: int = 10):
        self.log_dir = Path(log_dir)
        self.max_files = max_files
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def should_rotate(self, log_file: Path) -> bool:
        """ローテーションが必要かチェック"""
        if not log_file.exists():
            return False
        return log_file.stat().st_size > self.max_size_bytes
    
    def rotate_logs(self, base_name: str):
        """ログファイルのローテーション"""
        try:
            # 現在のログファイル
            current_log = self.log_dir / f"{base_name}.log"
            
            if not self.should_rotate(current_log):
                return
            
            # 既存のローテーションファイルをシフト
            for i in range(self.max_files - 1, 0, -1):
                old_file = self.log_dir / f"{base_name}.log.{i}"
                new_file = self.log_dir / f"{base_name}.log.{i + 1}"
                
                if old_file.exists():
                    if i == self.max_files - 1:
                        old_file.unlink()  # 最古のファイルを削除
                    else:
                        old_file.rename(new_file)
            
            # 現在のファイルを .1 にリネーム
            if current_log.exists():
                archived_file = self.log_dir / f"{base_name}.log.1"
                current_log.rename(archived_file)
            
        except Exception as e:
            print(f"Failed to rotate logs: {e}")

class ErrorHandler:
    """統一エラーハンドリングシステム"""
    
    def __init__(self, log_dir: str = "logs", enable_ui_callback: bool = True):
        """
        エラーハンドラーの初期化
        
        Args:
            log_dir: ログディレクトリ
            enable_ui_callback: UIコールバックを有効にするか
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # ログローテーション
        self.rotation = LogRotation(str(self.log_dir))
        
        # UIコールバック関数
        self.ui_callbacks: Dict[ErrorLevel, List[Callable]] = {
            level: [] for level in ErrorLevel
        }
        self.enable_ui_callback = enable_ui_callback
        
        # エラー統計
        self.error_stats = {
            'total_errors': 0,
            'errors_by_category': {},
            'errors_by_level': {},
            'session_start': datetime.now()
        }
        
        # クラッシュレポート設定
        self.crash_reports_dir = self.log_dir / "crash_reports"
        self.crash_reports_dir.mkdir(exist_ok=True)
        
        # ロガーの設定
        self._setup_loggers()
        
        # 未処理例外のハンドラー設定
        sys.excepthook = self._handle_unhandled_exception
        threading.excepthook = self._handle_thread_exception
    
    def _setup_loggers(self):
        """ロガーの設定"""
        # メインロガー
        self.logger = logging.getLogger('RVC_GUI')
        self.logger.setLevel(logging.DEBUG)
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # ファイルハンドラー
        log_file = self.log_dir / "rvc_gui.log"
        self.rotation.rotate_logs("rvc_gui")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # ハンドラーを追加
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
        
        # エラー専用ロガー
        self.error_logger = logging.getLogger('RVC_GUI_ERRORS')
        self.error_logger.setLevel(logging.ERROR)
        
        error_file = self.log_dir / "errors.log"
        self.rotation.rotate_logs("errors")
        
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d\n%(funcName)s\n---\n'
        )
        error_handler.setFormatter(error_formatter)
        
        if not self.error_logger.handlers:
            self.error_logger.addHandler(error_handler)
    
    def register_ui_callback(self, level: ErrorLevel, callback: Callable):
        """
        UIコールバック関数の登録
        
        Args:
            level: エラーレベル
            callback: コールバック関数
        """
        if level not in self.ui_callbacks:
            self.ui_callbacks[level] = []
        self.ui_callbacks[level].append(callback)
    
    def log(self, level: ErrorLevel, message: str, category: ErrorCategory = None, 
            exception: Exception = None, extra_data: Dict[str, Any] = None):
        """
        統一ログメソッド
        
        Args:
            level: ログレベル
            message: メッセージ
            category: エラーカテゴリー
            exception: 例外オブジェクト
            extra_data: 追加データ
        """
        # ログエントリの作成
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level.value,
            'message': message,
            'category': category.value if category else None,
            'thread_id': threading.current_thread().ident,
            'function': sys._getframe(1).f_code.co_name,
            'filename': sys._getframe(1).f_code.co_filename,
            'line_number': sys._getframe(1).f_lineno
        }
        
        # 例外情報の追加
        if exception:
            log_entry['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
        
        # 追加データの追加
        if extra_data:
            log_entry['extra_data'] = extra_data
        
        # ログ出力
        log_message = self._format_log_message(log_entry)
        
        if level == ErrorLevel.DEBUG:
            self.logger.debug(log_message)
        elif level == ErrorLevel.INFO:
            self.logger.info(log_message)
        elif level == ErrorLevel.WARNING:
            self.logger.warning(log_message)
        elif level == ErrorLevel.ERROR:
            self.logger.error(log_message)
            self.error_logger.error(json.dumps(log_entry, ensure_ascii=False, indent=2))
        elif level == ErrorLevel.CRITICAL:
            self.logger.critical(log_message)
            self.error_logger.critical(json.dumps(log_entry, ensure_ascii=False, indent=2))
        
        # 統計の更新
        self._update_stats(level, category)
        
        # UIコールバックの呼び出し
        if self.enable_ui_callback and level in self.ui_callbacks:
            for callback in self.ui_callbacks[level]:
                try:
                    callback(log_entry)
                except Exception as e:
                    # コールバック自体でエラーが発生した場合
                    self.logger.error(f"UI callback error: {e}")
    
    def _format_log_message(self, log_entry: Dict[str, Any]) -> str:
        """ログメッセージのフォーマット"""
        message = log_entry['message']
        
        if log_entry.get('category'):
            message = f"[{log_entry['category']}] {message}"
        
        if log_entry.get('exception'):
            exception_info = log_entry['exception']
            message += f" | Exception: {exception_info['type']}: {exception_info['message']}"
        
        return message
    
    def _update_stats(self, level: ErrorLevel, category: ErrorCategory):
        """エラー統計の更新"""
        if level in [ErrorLevel.ERROR, ErrorLevel.CRITICAL]:
            self.error_stats['total_errors'] += 1
        
        # レベル別統計
        level_key = level.value
        if level_key not in self.error_stats['errors_by_level']:
            self.error_stats['errors_by_level'][level_key] = 0
        self.error_stats['errors_by_level'][level_key] += 1
        
        # カテゴリー別統計
        if category:
            cat_key = category.value
            if cat_key not in self.error_stats['errors_by_category']:
                self.error_stats['errors_by_category'][cat_key] = 0
            self.error_stats['errors_by_category'][cat_key] += 1
    
    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        """未処理例外のハンドラー"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # クラッシュレポートの生成
        crash_report = self._generate_crash_report(exc_type, exc_value, exc_traceback)
        
        # ログに記録
        self.log(
            ErrorLevel.CRITICAL,
            f"Unhandled exception: {exc_type.__name__}: {exc_value}",
            ErrorCategory.SYSTEM_ERROR,
            exc_value
        )
        
        # デフォルトハンドラーを呼び出し
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    def _handle_thread_exception(self, args):
        """スレッドでの未処理例外のハンドラー"""
        exc_type, exc_value, exc_traceback, thread = args
        
        self.log(
            ErrorLevel.CRITICAL,
            f"Unhandled thread exception in {thread.name}: {exc_type.__name__}: {exc_value}",
            ErrorCategory.SYSTEM_ERROR,
            exc_value
        )
    
    def _generate_crash_report(self, exc_type, exc_value, exc_traceback) -> str:
        """クラッシュレポートの生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.crash_reports_dir / f"crash_report_{timestamp}.json"
        
        # システム情報の収集
        system_info = {
            'platform': sys.platform,
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'command_line': sys.argv,
            'environment_vars': dict(os.environ)
        }
        
        # クラッシュレポートの作成
        crash_report = {
            'timestamp': datetime.now().isoformat(),
            'exception': {
                'type': exc_type.__name__,
                'message': str(exc_value),
                'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback)
            },
            'system_info': system_info,
            'error_stats': self.error_stats.copy()
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(crash_report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Crash report generated: {report_file}")
            return str(report_file)
        
        except Exception as e:
            self.logger.error(f"Failed to generate crash report: {e}")
            return ""
    
    def get_error_stats(self) -> Dict[str, Any]:
        """エラー統計の取得"""
        stats = self.error_stats.copy()
        stats['session_duration'] = str(datetime.now() - stats['session_start'])
        return stats
    
    def export_logs(self, export_path: str, date_range: Optional[tuple] = None) -> bool:
        """
        ログのエクスポート
        
        Args:
            export_path: エクスポート先パス
            date_range: 日付範囲（開始日、終了日）
            
        Returns:
            エクスポート成功の可否
        """
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'date_range': date_range,
                'error_stats': self.get_error_stats(),
                'logs': []
            }
            
            # ログファイルの読み込み
            log_files = list(self.log_dir.glob("*.log*"))
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        export_data['logs'].append({
                            'filename': log_file.name,
                            'content': content
                        })
                except Exception as e:
                    self.logger.warning(f"Failed to read log file {log_file}: {e}")
            
            # エクスポートファイルの保存
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.log(ErrorLevel.INFO, f"Logs exported to {export_path}")
            return True
            
        except Exception as e:
            self.log(ErrorLevel.ERROR, f"Failed to export logs: {e}", exception=e)
            return False
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """古いログファイルのクリーンアップ"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for log_file in self.log_dir.glob("*.log*"):
                try:
                    file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_date < cutoff_date:
                        log_file.unlink()
                        self.logger.info(f"Deleted old log file: {log_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete log file {log_file}: {e}")
            
            # クラッシュレポートのクリーンアップ
            for report_file in self.crash_reports_dir.glob("*.json"):
                try:
                    file_date = datetime.fromtimestamp(report_file.stat().st_mtime)
                    if file_date < cutoff_date:
                        report_file.unlink()
                        self.logger.info(f"Deleted old crash report: {report_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete crash report {report_file}: {e}")
                    
        except Exception as e:
            self.log(ErrorLevel.ERROR, f"Failed to cleanup old logs: {e}", exception=e)

# 便利なデコレータ
def handle_errors(category: ErrorCategory = ErrorCategory.PROCESSING_ERROR, 
                  reraise: bool = False):
    """
    エラーハンドリングデコレータ
    
    Args:
        category: エラーカテゴリー
        reraise: 例外を再発生させるか
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # グローバルエラーハンドラーが設定されている場合
                if hasattr(wrapper, '_error_handler'):
                    wrapper._error_handler.log(
                        ErrorLevel.ERROR,
                        f"Error in {func.__name__}: {str(e)}",
                        category,
                        e
                    )
                else:
                    # フォールバック
                    logging.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                
                if reraise:
                    raise
                return None
        
        return wrapper
    return decorator

# グローバルエラーハンドラーインスタンス
_global_error_handler: Optional[ErrorHandler] = None

def get_error_handler() -> ErrorHandler:
    """グローバルエラーハンドラーの取得"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler

def init_error_handler(log_dir: str = "logs", enable_ui_callback: bool = True) -> ErrorHandler:
    """グローバルエラーハンドラーの初期化"""
    global _global_error_handler
    _global_error_handler = ErrorHandler(log_dir, enable_ui_callback)
    return _global_error_handler

# 便利な関数
def log_debug(message: str, **kwargs):
    """デバッグログ"""
    get_error_handler().log(ErrorLevel.DEBUG, message, **kwargs)

def log_info(message: str, **kwargs):
    """情報ログ"""
    get_error_handler().log(ErrorLevel.INFO, message, **kwargs)

def log_warning(message: str, **kwargs):
    """警告ログ"""
    get_error_handler().log(ErrorLevel.WARNING, message, **kwargs)

def log_error(message: str, **kwargs):
    """エラーログ"""
    get_error_handler().log(ErrorLevel.ERROR, message, **kwargs)

def log_critical(message: str, **kwargs):
    """クリティカルログ"""
    get_error_handler().log(ErrorLevel.CRITICAL, message, **kwargs)

# テスト関数
def test_error_handler():
    """エラーハンドラーのテスト"""
    import tempfile
    import shutil
    
    # テスト用ディレクトリ
    test_dir = tempfile.mkdtemp()
    
    try:
        # エラーハンドラーの初期化
        handler = ErrorHandler(test_dir)
        
        # 各レベルのログテスト
        handler.log(ErrorLevel.DEBUG, "Debug message")
        handler.log(ErrorLevel.INFO, "Info message")
        handler.log(ErrorLevel.WARNING, "Warning message", ErrorCategory.INPUT_ERROR)
        
        # 例外付きログ
        try:
            raise ValueError("Test exception")
        except Exception as e:
            handler.log(ErrorLevel.ERROR, "Error with exception", ErrorCategory.PROCESSING_ERROR, e)
        
        # 統計の確認
        stats = handler.get_error_stats()
        assert stats['total_errors'] == 1
        assert stats['errors_by_level']['ERROR'] == 1
        assert stats['errors_by_category']['processing_error'] == 1
        
        # デコレータのテスト
        @handle_errors(ErrorCategory.INPUT_ERROR)
        def test_function():
            raise RuntimeError("Test error")
        
        # エラーハンドラーをデコレータに設定
        test_function._error_handler = handler
        
        # エラーが発生してもクラッシュしないことを確認
        result = test_function()
        assert result is None
        
        print("Error handler tests passed!")
        
    finally:
        # テストディレクトリの削除
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_error_handler()