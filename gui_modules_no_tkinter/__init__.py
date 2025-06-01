#!/usr/bin/env python3
"""
GUI改善モジュール（Tkinter依存なし版）
Voice Converter GUI の改善システム - 非GUI環境対応
"""

from .settings_manager_standalone import SettingsManager
from .error_handler_standalone import ErrorHandler, init_error_handler, log_info, log_error, log_warning, ErrorCategory, ErrorLevel

__version__ = "1.0.0"
__author__ = "Voice Converter Development Team"

__all__ = [
    # 設定管理
    'SettingsManager',
    
    # エラーハンドリング
    'ErrorHandler',
    'init_error_handler',
    'log_info',
    'log_error', 
    'log_warning',
    'ErrorCategory',
    'ErrorLevel',
]