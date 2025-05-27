#!/usr/bin/env python3
"""
gui_dark_mode.pyの簡易修正スクリプト
内蔵プログレスバーを使用し、別ウィンドウを開かないようにする
"""

import re

def fix_gui_progress():
    # ファイルを読み込み
    with open('gui_dark_mode.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正1: run_conversionメソッド内でtracker関連を削除
    # プログレスバー作成部分を探して置換
    content = re.sub(
        r'# プログレスバーを作成.*?tracker = self\.progress_integration\.get_tracker\(\)',
        '# 内蔵プログレスバーを使用',
        content,
        flags=re.DOTALL
    )
    
    # 修正2: tracker.start_stage(ProcessingStage.xxx) を self.update_progress に置換
    replacements = [
        (r'tracker\.start_stage\(ProcessingStage\.INITIALIZATION\)', 
         'self.update_progress(0, 0, "初期化中...")'),
        (r'tracker\.start_stage\(ProcessingStage\.DATA_LOADING\)', 
         'self.update_progress(1, 0, "データ読み込み中...")'),
        (r'tracker\.start_stage\(ProcessingStage\.PREPROCESSING\)', 
         'self.update_progress(2, 0, "前処理中...")'),
        (r'tracker\.start_stage\(ProcessingStage\.SAVING_OUTPUT\)', 
         'self.update_progress(6, 0, "保存中...")'),
        (r'tracker\.complete_stage\(\)', 
         '# ステージ完了'),
    ]
    
    for old, new in replacements:
        content = re.sub(old, new, content)
    
    # 修正3: _run_rvc_with_progressの呼び出しからtrackerを削除
    content = re.sub(
        r'self\._run_rvc_with_progress\(cmd_array, env, tracker, project_dir\)',
        'self._run_rvc_with_progress(cmd_array, env, project_dir)',
        content
    )
    
    # 修正4: progress_integration関連の削除
    content = re.sub(
        r'self\.root\.after\(0, lambda: self\.progress_integration\.close\(\) if self\.progress_integration else None\)',
        '# プログレスウィンドウのクローズは不要',
        content
    )
    
    content = re.sub(
        r'if self\.progress_integration:[\s\n]*self\.progress_integration\.close\(\)',
        '# プログレスウィンドウのクローズは不要',
        content
    )
    
    # ファイルを書き戻す
    with open('gui_dark_mode_fixed_progress.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修正完了: gui_dark_mode_fixed_progress.py")

if __name__ == "__main__":
    fix_gui_progress()
