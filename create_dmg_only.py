#!/usr/bin/env python3
"""
DMG作成専用スクリプト
正常動作するユニバーサル版アプリからDMGを作成
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def create_dmg():
    """DMG作成のみ実行"""
    project_dir = Path(__file__).parent.absolute()
    
    # 1. ソースアプリ確認
    source_app = project_dir / "universal_build" / "VoiceConverter_universal.app"
    if not source_app.exists():
        print(f"❌ ソースアプリが見つかりません: {source_app}")
        return False
    
    print(f"✅ ソースアプリ確認: {source_app}")
    
    # 2. 一時ディレクトリ作成
    temp_dir = tempfile.mkdtemp(prefix="dmg_")
    temp_path = Path(temp_dir)
    dmg_contents = temp_path / "dmg_contents"
    dmg_contents.mkdir()
    
    print(f"📁 一時ディレクトリ: {dmg_contents}")
    
    try:
        # 3. アプリを直接コピー
        dest_app = dmg_contents / "VoiceConverter Universal.app"
        print("📱 ditto経由でアプリをコピー中...")
        
        # dittoで完全コピー（macOS標準、最も安全）
        subprocess.run([
            "ditto", str(source_app), str(dest_app)
        ], check=True)
        
        print("✅ ditto完全コピー完了")
        
        # 4. Applicationsリンク
        applications_link = dmg_contents / "Applications"
        applications_link.symlink_to("/Applications")
        print("🔗 Applicationsリンク作成")
        
        # 5. 説明書
        readme = dmg_contents / "インストール方法.txt"
        with open(readme, 'w', encoding='utf-8') as f:
            f.write("""RVC Voice Converter Universal - インストール

1. "VoiceConverter Universal.app" を "Applications" にドラッグ
2. Applicationsから起動
3. 初回起動時にセキュリティ許可

対応: Apple Silicon & Intel Mac (Rosetta2)
""")
        print("📝 説明書作成")
        
        # 6. DMG作成（最も基本的な方法）
        dmg_name = "RVC-Voice-Converter-Universal.dmg"
        dmg_path = project_dir / dmg_name
        
        if dmg_path.exists():
            dmg_path.unlink()
        
        print(f"💿 DMG作成中: {dmg_name}")
        
        # 基本的なhdiutil create
        subprocess.run([
            "hdiutil", "create",
            "-volname", "RVC Voice Converter Universal", 
            "-srcfolder", str(dmg_contents),
            "-format", "UDRO",  # 読み取り専用
            str(dmg_path)
        ], check=True)
        
        print("✅ DMG作成完了!")
        
        # サイズ確認
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"📏 サイズ: {size_mb:.1f} MB")
        
        return dmg_path
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    finally:
        # 一時ディレクトリ削除
        import shutil
        shutil.rmtree(temp_path, ignore_errors=True)

if __name__ == "__main__":
    result = create_dmg()
    if result:
        print(f"\n🎉 DMG作成成功: {result}")
    else:
        print("\n❌ DMG作成失敗")
        sys.exit(1)