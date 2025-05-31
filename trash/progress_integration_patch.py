"""
プログレスバー統合改善パッチ
内蔵のステータスセクションを使用して、別ウィンドウを開かずに進捗を表示
"""

import os
import time
import threading
from datetime import datetime

class ProgressIntegrationPatch:
    """既存のGUIの内蔵プログレスバーを使用するためのパッチ"""
    
    @staticmethod
    def patch_run_conversion(gui_instance):
        """run_conversionメソッドを置き換え"""
        
        def new_run_conversion():
            """実際の変換処理（内蔵プログレスバー使用）"""
            try:
                # 変換フラグを設定
                gui_instance.is_converting = True
                
                # プロジェクトディレクトリを確認
                project_dir = gui_instance.base_dir
                if project_dir.endswith('/Resources'):
                    possible_dirs = [
                        "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion",
                        os.path.expanduser("~/Retrieval-based-Voice-Conversion"),
                    ]
                    for dir_path in possible_dirs:
                        if os.path.exists(os.path.join(dir_path, "pyproject.toml")):
                            project_dir = dir_path
                            break
                
                # ステージ0: 初期化（0-10%）
                gui_instance.update_progress(0, 0, "プロジェクトとモデルの初期化中...")
                time.sleep(0.3)
                gui_instance.update_progress(0, 50, "環境を準備しています...")
                time.sleep(0.3)
                gui_instance.update_progress(0, 100, "初期化完了")
                
                # ステージ1: データ読み込み（10-20%）
                gui_instance.update_progress(1, 0, "音声ファイルを開いています...")
                model_id = gui_instance.model_info.get('folder') or ''
                model_path = os.path.join(gui_instance.model_dir, model_id) if model_id else os.path.dirname(gui_instance.model_info['file'])
                
                gui_instance.update_progress(1, 30, "モデルファイルを読み込み中...")
                index_file = gui_instance.model_info.get('index_file')
                if not index_file and os.path.exists(model_path):
                    index_files = [f for f in os.listdir(model_path) if f.endswith('.index')]
                    if index_files:
                        index_file = os.path.join(model_path, index_files[0])
                
                gui_instance.update_progress(1, 70, "インデックスファイルを確認中...")
                time.sleep(0.2)
                gui_instance.update_progress(1, 100, "データ読み込み完了")
