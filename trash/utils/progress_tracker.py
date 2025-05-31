"""
進捗追跡システム
実際の処理進捗をリアルタイムで追跡し、UIに反映させるためのクラス
"""

import time
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import threading


class ProcessingStage(Enum):
    """処理段階の定義"""
    INITIALIZATION = "初期化"
    DATA_LOADING = "データ読み込み"
    PREPROCESSING = "前処理"
    FEATURE_EXTRACTION = "特徴抽出"
    MODEL_INFERENCE = "モデル推論"
    POSTPROCESSING = "後処理"
    SAVING_OUTPUT = "出力保存"
    COMPLETED = "完了"


@dataclass
class StageInfo:
    """各処理段階の情報"""
    name: str
    weight: float  # 全体に対する重み（0.0～1.0）
    description: str


class ProgressTracker:
    """
    処理進捗を追跡するクラス
    """
    
    def __init__(self):
        # 各処理段階の重み付け（合計1.0になるように設定）
        self.stages: Dict[ProcessingStage, StageInfo] = {
            ProcessingStage.INITIALIZATION: StageInfo("初期化", 0.05, "システムを初期化しています..."),
            ProcessingStage.DATA_LOADING: StageInfo("データ読み込み", 0.10, "音声データを読み込んでいます..."),
            ProcessingStage.PREPROCESSING: StageInfo("前処理", 0.20, "音声データを前処理しています..."),
            ProcessingStage.FEATURE_EXTRACTION: StageInfo("特徴抽出", 0.30, "音声特徴を抽出しています..."),
            ProcessingStage.MODEL_INFERENCE: StageInfo("モデル推論", 0.25, "音声変換を実行しています..."),
            ProcessingStage.POSTPROCESSING: StageInfo("後処理", 0.08, "出力を最適化しています..."),
            ProcessingStage.SAVING_OUTPUT: StageInfo("出力保存", 0.02, "結果を保存しています..."),
        }
        
        self.current_stage: Optional[ProcessingStage] = None
        self.stage_progress: float = 0.0  # 現在のステージ内での進捗（0.0～1.0）
        self.overall_progress: float = 0.0  # 全体の進捗（0.0～1.0）
        self.callbacks: List[Callable[[float, str], None]] = []
        self._lock = threading.Lock()
        
    def add_callback(self, callback: Callable[[float, str], None]):
        """
        進捗更新時のコールバック関数を追加
        callback(progress: float, message: str)
        """
        self.callbacks.append(callback)
        
    def start_stage(self, stage: ProcessingStage):
        """新しい処理段階を開始"""
        with self._lock:
            self.current_stage = stage
            self.stage_progress = 0.0
            self._update_overall_progress()
            self._notify_callbacks()
            
    def update_stage_progress(self, progress: float):
        """
        現在の処理段階内での進捗を更新
        progress: 0.0～1.0の値
        """
        with self._lock:
            self.stage_progress = min(max(progress, 0.0), 1.0)
            self._update_overall_progress()
            self._notify_callbacks()
            
    def complete_stage(self):
        """現在の処理段階を完了"""
        with self._lock:
            self.stage_progress = 1.0
            self._update_overall_progress()
            self._notify_callbacks()
            
    def _update_overall_progress(self):
        """全体の進捗を計算"""
        if self.current_stage is None:
            self.overall_progress = 0.0
            return
            
        completed_weight = 0.0
        
        # 完了したステージの重みを加算
        for stage, info in self.stages.items():
            if stage == self.current_stage:
                # 現在のステージは部分的に完了
                completed_weight += info.weight * self.stage_progress
                break
            else:
                # このステージは完了済み
                completed_weight += info.weight
                
        self.overall_progress = completed_weight
        
    def _notify_callbacks(self):
        """登録されたコールバックに進捗を通知"""
        if self.current_stage:
            message = self.stages[self.current_stage].description
            for callback in self.callbacks:
                callback(self.overall_progress, message)
                
    def get_progress_percentage(self) -> int:
        """進捗をパーセンテージで取得"""
        return int(self.overall_progress * 100)
        
    def get_current_message(self) -> str:
        """現在の処理メッセージを取得"""
        if self.current_stage:
            return self.stages[self.current_stage].description
        return "待機中..."
        
    def reset(self):
        """進捗をリセット"""
        with self._lock:
            self.current_stage = None
            self.stage_progress = 0.0
            self.overall_progress = 0.0
            self._notify_callbacks()


class SubTaskTracker:
    """
    サブタスク用の進捗トラッカー
    大きな処理段階内での細かい進捗を追跡
    """
    
    def __init__(self, parent_tracker: ProgressTracker, total_items: int):
        self.parent_tracker = parent_tracker
        self.total_items = total_items
        self.current_item = 0
        
    def update(self, current_item: int):
        """サブタスクの進捗を更新"""
        self.current_item = min(current_item, self.total_items)
        if self.total_items > 0:
            progress = self.current_item / self.total_items
            self.parent_tracker.update_stage_progress(progress)
            
    def increment(self):
        """サブタスクを1つ進める"""
        self.update(self.current_item + 1)
