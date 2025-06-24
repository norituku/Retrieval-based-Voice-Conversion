#!/usr/bin/env python3
"""
改良版 DMG作成スクリプト
アプリケーションフォルダへのシンボリックリンクを含む
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def run_command(cmd, shell=False):
    """コマンド実行"""
    print(f"実行中: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"エラー: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return None

def create_dmg_with_applications_link():
    """アプリケーションフォルダへのリンクを含むDMGを作成"""
    
    # パス設定
    app_path = Path("dist_arm64/VoiceConverter.app")
    dmg_name = "VoiceConverter-Universal.dmg"
    volume_name = "Voice Converter"
    
    if not app_path.exists():
        print(f"エラー: {app_path} が見つかりません")
        return False
    
    # 既存のDMGを削除
    if Path(dmg_name).exists():
        os.remove(dmg_name)
    
    # 一時ディレクトリの作成
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # アプリをコピー
        print("アプリケーションをコピー中...")
        app_copy = temp_path / "VoiceConverter.app"
        shutil.copytree(app_path, app_copy)
        
        # Applicationsへのシンボリックリンクを作成
        print("Applicationsへのリンクを作成中...")
        apps_link = temp_path / "Applications"
        os.symlink("/Applications", str(apps_link))
        
        # 読み書き可能なDMGを作成
        print("DMGを作成中...")
        temp_dmg = "temp.dmg"
        
        cmd = [
            'hdiutil', 'create',
            '-volname', volume_name,
            '-srcfolder', str(temp_path),
            '-ov',
            '-format', 'UDRW',
            temp_dmg
        ]
        
        if run_command(cmd) is None:
            return False
        
        # DMGをマウント
        print("DMGをマウント中...")
        mount_output = run_command(['hdiutil', 'attach', temp_dmg, '-nobrowse', '-mountpoint', '/tmp/dmg_mount'])
        if mount_output is None:
            return False
        
        # アイコンの配置を設定（AppleScript使用）
        print("アイコン配置を設定中...")
        applescript = '''
        tell application "Finder"
            tell disk "Voice Converter"
                open
                set current view of container window to icon view
                set toolbar visible of container window to false
                set statusbar visible of container window to false
                set the bounds of container window to {400, 100, 900, 400}
                set theViewOptions to the icon view options of container window
                set arrangement of theViewOptions to not arranged
                set icon size of theViewOptions to 72
                set position of item "VoiceConverter.app" of container window to {125, 150}
                set position of item "Applications" of container window to {375, 150}
                close
                open
                update without registering applications
                delay 2
            end tell
        end tell
        '''
        
        run_command(['osascript', '-e', applescript])
        
        # アンマウント
        print("DMGをアンマウント中...")
        run_command(['hdiutil', 'detach', '/tmp/dmg_mount'])
        
        # 読み取り専用に変換
        print("最終的なDMGに変換中...")
        cmd = [
            'hdiutil', 'convert',
            temp_dmg,
            '-format', 'UDZO',
            '-o', dmg_name
        ]
        
        if run_command(cmd) is None:
            return False
        
        # 一時DMGを削除
        os.remove(temp_dmg)
        
        # 最終的なファイルサイズを表示
        size = os.path.getsize(dmg_name) / (1024 * 1024 * 1024)
        print(f"\n✅ DMG作成完了: {dmg_name} ({size:.1f}GB)")
        
        return True

def main():
    """メイン処理"""
    print("🔨 改良版DMG作成開始...")
    
    # 作業ディレクトリの確認
    if not Path("dist_arm64/VoiceConverter.app").exists():
        print("エラー: dist_arm64/VoiceConverter.app が見つかりません")
        print("先に build_arm64.sh を実行してください")
        return 1
    
    # DMG作成
    if create_dmg_with_applications_link():
        print("\n📦 配布準備完了！")
        print("1. DMGファイルをダブルクリックして開く")
        print("2. VoiceConverter.app を Applications フォルダにドラッグ")
        print("3. Applicationsフォルダから起動")
        return 0
    else:
        print("\n❌ DMG作成に失敗しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())
