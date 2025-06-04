#!/usr/bin/env python3
"""
ULTRATHINK: ログ重要度分析と分類システム
変換ログを重要度別に分類し、最適な表示方法を決定
"""

import re
import logging
from enum import Enum
from typing import Dict, List, Tuple

class LogImportance(Enum):
    """ログ重要度レベル"""
    CRITICAL = "CRITICAL"    # 必須表示 - エラー、変換結果
    HIGH = "HIGH"           # 重要表示 - 開始/完了、モデル情報
    MEDIUM = "MEDIUM"       # オプション表示 - 詳細パラメータ
    LOW = "LOW"            # デバッグ表示 - 内部処理詳細
    NOISE = "NOISE"        # 非表示 - ライブラリ警告、DEBUG

class LogImportanceAnalyzer:
    """ログ重要度分析クラス"""
    
    def __init__(self):
        # 重要度分類ルール
        self.importance_rules = {
            # CRITICAL: エラーと最終結果
            LogImportance.CRITICAL: [
                r"❌.*[Ee]rror",
                r"🚨.*[Ff]ailed",
                r"❌.*[Ff]ailed",
                r"RuntimeError",
                r"Exception:",
                r"🎉.*completed successfully",
                r"✅.*SUCCESS",
                r"Conversion completed",
                r"conversion successful",
            ],
            
            # HIGH: 重要な進行状況
            LogImportance.HIGH: [
                r"🚀.*Starting.*conversion",
                r"✅.*Enhanced.*initialized",
                r"✅.*Model loaded successfully",
                r"Enhanced status:",
                r"Enhanced features:",
                r"Using model:",
                r"Pipeline type:",
                r"Enhanced Pipeline.*activated",
                r"Output saved to:",
                r"Performance stats:",
                r"🎯.*F0 method set",
            ],
            
            # MEDIUM: 詳細情報（オプション）
            LogImportance.MEDIUM: [
                r"Parameters:",
                r"Input:",
                r"Output:",
                r"F0 estimation.*successful",
                r"Audio.*stats:",
                r"Segments created:",
                r"Processing.*segment",
                r"RMS mixing",
                r"Final.*successful",
                r"Audio concatenation",
            ],
            
            # LOW: デバッグ情報
            LogImportance.LOW: [
                r"DEBUG:",
                r"Starting audio preprocessing",
                r"Audio padding completed",
                r"Before size adjustment",
                r"Adjusted.*to",
                r"Segment.*shape",
                r"Pitch shapes:",
                r"Pipeline Args Overview",
            ],
            
            # NOISE: 不要な情報
            LogImportance.NOISE: [
                r"DEBUG:numba",
                r"bytecode dump:",
                r"UserWarning:",
                r"torch\.nn\.utils\.weight_norm",
                r"MPS.*fallback.*CPU",
                r"performance implications",
                r"dispatch pc=",
                r"stack \[",
                r"overwrite configs\.json",
                r"Use mps instead",
                r"current directory is",
                r"HubertModel Config:",
                r"HubertPretrainingTask Config",
                r"Loading faiss\.",
                r"Successfully loaded faiss\.",
            ]
        }
        
        # コンパイル済み正規表現
        self.compiled_rules = {}
        for importance, patterns in self.importance_rules.items():
            self.compiled_rules[importance] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def classify_log_line(self, log_line: str) -> LogImportance:
        """ログ行の重要度を判定"""
        log_line = log_line.strip()
        
        # 空行は無視
        if not log_line:
            return LogImportance.NOISE
        
        # 重要度順にチェック
        for importance in [LogImportance.CRITICAL, LogImportance.HIGH, LogImportance.MEDIUM, LogImportance.LOW, LogImportance.NOISE]:
            for pattern in self.compiled_rules[importance]:
                if pattern.search(log_line):
                    return importance
        
        # どのパターンにも一致しない場合はMEDIUM
        return LogImportance.MEDIUM
    
    def filter_logs(self, log_lines: List[str], min_importance: LogImportance = LogImportance.HIGH) -> List[str]:
        """重要度に基づいてログをフィルタ"""
        importance_order = [LogImportance.CRITICAL, LogImportance.HIGH, LogImportance.MEDIUM, LogImportance.LOW, LogImportance.NOISE]
        min_level = importance_order.index(min_importance)
        
        filtered_logs = []
        for line in log_lines:
            importance = self.classify_log_line(line)
            if importance_order.index(importance) <= min_level:
                filtered_logs.append(line)
        
        return filtered_logs
    
    def analyze_log_sample(self, log_text: str) -> Dict[LogImportance, int]:
        """ログサンプルの重要度分布を分析"""
        lines = log_text.split('\n')
        distribution = {importance: 0 for importance in LogImportance}
        
        for line in lines:
            importance = self.classify_log_line(line)
            distribution[importance] += 1
        
        return distribution

# ログフィルタリング関数
def create_filtered_logger(name: str, level: LogImportance = LogImportance.HIGH):
    """重要度フィルタ付きロガーを作成"""
    logger = logging.getLogger(name)
    
    # カスタムフォーマッタ
    class ImportanceFilter(logging.Filter):
        def __init__(self, min_importance: LogImportance):
            super().__init__()
            self.analyzer = LogImportanceAnalyzer()
            self.min_importance = min_importance
            
        def filter(self, record):
            importance = self.analyzer.classify_log_line(record.getMessage())
            importance_order = [LogImportance.CRITICAL, LogImportance.HIGH, LogImportance.MEDIUM, LogImportance.LOW, LogImportance.NOISE]
            min_level = importance_order.index(self.min_importance)
            return importance_order.index(importance) <= min_level
    
    # フィルタを追加
    logger.addFilter(ImportanceFilter(level))
    return logger

def demo_log_filtering():
    """ログフィルタリングのデモ"""
    analyzer = LogImportanceAnalyzer()
    
    # サンプルログ
    sample_logs = [
        "🚀 Starting Enhanced conversion...",
        "DEBUG:numba.core.byteflow:bytecode dump:",
        "✅ Model loaded successfully",
        "UserWarning: torch.nn.utils.weight_norm is deprecated",
        "Enhanced status: {'pipeline_type': 'enhanced'}",
        "DEBUG: Before size adjustment: feats.shape=torch.Size([1, 498, 768])",
        "❌ F0 estimation failed: MPS error",
        "🎉 Enhanced Pipeline completed successfully",
        "dispatch pc=36, inst=LOAD_CONST(arg=3, lineno=428)"
    ]
    
    print("🔍 ログ重要度分析デモ")
    print("=" * 60)
    
    for log_line in sample_logs:
        importance = analyzer.classify_log_line(log_line)
        print(f"{importance.value:8} | {log_line}")
    
    print("\n📊 フィルタリング結果:")
    print("=" * 60)
    
    for level in [LogImportance.CRITICAL, LogImportance.HIGH, LogImportance.MEDIUM]:
        filtered = analyzer.filter_logs(sample_logs, level)
        print(f"\n{level.value} 以上 ({len(filtered)} lines):")
        for line in filtered:
            print(f"  {line}")

if __name__ == "__main__":
    demo_log_filtering()