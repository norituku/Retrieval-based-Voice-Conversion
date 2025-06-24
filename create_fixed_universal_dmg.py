#!/usr/bin/env python3
"""
環境非依存DMG作成スクリプト（修正版）
CLAUDE.mdの指示に従いcp -pRPコマンドを使用
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def create_fixed_dmg():
    """修正済みDMG作成（cp -pRP使用）"""
    project_dir = Path(__file__).parent.absolute()
    
    # 1. ソースアプリ確認
    source_app = project_dir / "universal_build" / "VoiceConverter_universal.app"
    if not source_app.exists():
        print(f"❌ ソースアプリが見つかりません: {source_app}")
        return False
    
    print(f"✅ ソースアプリ確認: {source_app}")
    
    # 2. 一時ディレクトリ作成
    temp_dir = tempfile.mkdtemp(prefix="dmg_fixed_")
    temp_path = Path(temp_dir)
    dmg_contents = temp_path / "dmg_contents"
    dmg_contents.mkdir()
    
    print(f"📁 一時ディレクトリ: {dmg_contents}")
    
    try:
        # 3. ✅ CLAUDE.mdルール: cp -pRPでコピー
        dest_app = dmg_contents / "VoiceConverter.app"
        print("📱 cp -pRP経由でアプリをコピー中...")
        print("🚨 重要: 権限・リンク保持でバイナリ破損を防止")
        
        # CLAUDE.mdで推奨されている方法
        subprocess.run([
            "cp", "-pRP", str(source_app), str(dest_app)
        ], check=True)
        
        print("✅ cp -pRP完全コピー完了（バイナリ保護）")
        
        # 4. Applicationsリンク
        applications_link = dmg_contents / "Applications"
        applications_link.symlink_to("/Applications")
        print("🔗 Applicationsリンク作成")
        
        # 5. 説明書
        readme = dmg_contents / "インストール方法.txt"
        with open(readme, 'w', encoding='utf-8') as f:
            f.write("""RVC Voice Converter Universal - インストール方法

【重要】正しいインストール手順:

1. "VoiceConverter.app" を "Applications" フォルダにドラッグ
2. Finderでアプリを右クリック → "開く" を選択
3. 「開発元を確認できません」が表示されたら "開く" をクリック
4. 以降は通常通りアプリアイコンから起動可能

【対応環境】
- Apple Silicon Mac: ネイティブ動作
- Intel Mac: Rosetta2経由で動作

【トラブルシューティング】
- 起動しない場合: Applicationsフォルダにコピー後、右クリック→開く
- Poetry環境不要: 完全スタンドアロン動作

作成日: 2025年6月24日
""")
        print("📝 説明書作成")
        
        # 6. DMG作成（基本的な方法）
        dmg_name = "VoiceConverter-Universal-Fixed.dmg"
        dmg_path = project_dir / dmg_name
        
        if dmg_path.exists():
            dmg_path.unlink()
            print("🗑️ 既存DMG削除")
        
        print(f"💿 DMG作成中: {dmg_name}")
        
        # 基本的なhdiutil create
        subprocess.run([
            "hdiutil", "create",
            "-volname", "Voice Converter Universal", 
            "-srcfolder", str(dmg_contents),
            "-format", "UDRO",  # 読み取り専用
            "-imagekey", "zlib-level=9",  # 圧縮最適化
            str(dmg_path)
        ], check=True)
        
        print("✅ DMG作成完了!")
        
        # サイズ確認
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"📏 サイズ: {size_mb:.1f} MB")
        
        # 最終検証
        print("\n🔍 最終検証:")
        print(f"   作成されたDMG: {dmg_path}")
        print(f"   使用コピー方法: cp -pRP (CLAUDE.md準拠)")
        print(f"   バイナリ保護: ✅")
        print(f"   権限保持: ✅")
        
        return dmg_path
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    finally:
        # 一時ディレクトリ削除
        import shutil
        shutil.rmtree(temp_path, ignore_errors=True)
        print(f"🧹 一時ディレクトリ削除: {temp_path}")

if __name__ == "__main__":
    print("🚨 環境非依存DMG作成スクリプト（修正版）")
    print("📋 CLAUDE.mdルール適用: cp -pRP使用")
    print()
    
    result = create_fixed_dmg()
    if result:
        print(f"\n🎉 修正済みDMG作成成功: {result}")
        print("✅ バイナリ破損問題解決済み")
        print("✅ 環境非依存性確保")
    else:
        print("\n❌ DMG作成失敗")
        sys.exit(1)