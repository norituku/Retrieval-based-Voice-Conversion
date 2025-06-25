#!/usr/bin/env python3
"""
最終配布用DMG作成スクリプト（圧縮版）
indexファイル修正済みユニバーサルアプリを配布
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
import datetime

def create_release_dmg():
    """最終配布用DMG作成（圧縮最適化）"""
    project_dir = Path(__file__).parent.absolute()

    # 1. ソースアプリ確認
    source_app = project_dir / "universal_build" / "VoiceConverter_universal.app"
    if not source_app.exists():
        print(f"❌ ソースアプリが見つかりません: {source_app}")
        return False

    print(f"✅ ソースアプリ確認: {source_app}")

    # 2. 一時ディレクトリ作成
    temp_dir = tempfile.mkdtemp(prefix="dmg_release_")
    temp_path = Path(temp_dir)
    dmg_contents = temp_path / "dmg_contents"
    dmg_contents.mkdir()

    print(f"📁 一時ディレクトリ: {dmg_contents}")

    try:
        # 3. cp -pRPでコピー（CLAUDE.mdルール）
        dest_app = dmg_contents / "VoiceConverter.app"
        print("📱 アプリをコピー中...")

        subprocess.run([
            "cp", "-pRP", str(source_app), str(dest_app)
        ], check=True)

        print("✅ アプリコピー完了")

        # 4. 拡張属性クリア
        print("🧹 拡張属性をクリア中...")
        subprocess.run([
            "xattr", "-cr", str(dest_app)
        ], check=True)

        # 5. 再署名
        print("🔏 アドホック署名中...")
        subprocess.run([
            "codesign", "--force", "--deep", "--sign", "-", str(dest_app)
        ], check=True)

        # 6. Applicationsリンク
        applications_link = dmg_contents / "Applications"
        applications_link.symlink_to("/Applications")
        print("🔗 Applicationsリンク作成")

        # 7. README作成
        readme = dmg_contents / "README.txt"
        with open(readme, 'w', encoding='utf-8') as f:
            f.write(f"""Voice Converter Universal - Installation Guide

【Installation】
1. Drag "VoiceConverter.app" to the "Applications" folder
2. Right-click the app in Finder and select "Open"
3. Click "Open" when the security warning appears
4. The app will now launch normally

【System Requirements】
- macOS 10.15 or later
- Apple Silicon Mac: Native performance
- Intel Mac: Runs via Rosetta 2

【Features】
- Fixed: RVC index file recognition
- Standalone: No Python/Poetry required
- Universal: Works on all modern Macs

【Troubleshooting】
If the app doesn't open:
- Make sure it's in the Applications folder
- Right-click → Open (don't double-click)
- Check Security & Privacy settings

Version: 1.0.0
Build Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
""")
        print("📝 README作成")

        # 8. DMG作成（UDZO圧縮）
        dmg_name = f"VoiceConverter-Universal-{datetime.datetime.now().strftime('%Y%m%d')}.dmg"
        dmg_path = project_dir / dmg_name

        if dmg_path.exists():
            dmg_path.unlink()
            print("🗑️ 既存DMG削除")

        print(f"💿 圧縮DMG作成中: {dmg_name}")
        print("⏳ しばらくお待ちください（約1-2分）...")

        # UDZO形式で圧縮
        subprocess.run([
            "hdiutil", "create",
            "-volname", "Voice Converter Universal",
            "-srcfolder", str(dmg_contents),
            "-format", "UDZO",  # 圧縮形式
            "-imagekey", "zlib-level=9",  # 最大圧縮
            str(dmg_path)
        ], check=True)

        print("✅ DMG作成完了!")

        # サイズ確認
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"📏 サイズ: {size_mb:.1f} MB")

        # DMG検証
        print("\n🔍 DMG検証中...")
        result = subprocess.run([
            "hdiutil", "verify", str(dmg_path)
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ DMG検証: 正常")
        else:
            print("⚠️  DMG検証: 警告あり")

        # 最終情報
        print("\n📊 配布用DMG情報:")
        print(f"   ファイル名: {dmg_name}")
        print(f"   パス: {dmg_path}")
        print(f"   サイズ: {size_mb:.1f} MB")
        print(f"   形式: UDZO (圧縮)")
        print(f"   署名: アドホック署名済み")
        print(f"   互換性: macOS 10.15以降")

        print("\n🎯 機能修正:")
        print("   ✅ RVC indexファイル認識問題を修正")
        print("   ✅ NumPy pickle形式 (.index) 対応")
        print("   ✅ 高品質音声変換を実現")

        return dmg_path

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 一時ディレクトリ削除
        import shutil
        shutil.rmtree(temp_path, ignore_errors=True)
        print(f"\n🧹 一時ディレクトリ削除: {temp_path}")

if __name__ == "__main__":
    print("🚀 Voice Converter Universal - 最終配布用DMG作成")
    print("📱 ユニバーサルバイナリ（Apple Silicon + Intel Mac対応）")
    print("🔧 indexファイル認識問題修正済み")
    print()

    result = create_release_dmg()
    if result:
        print(f"\n🎉 配布用DMG作成成功!")
        print(f"📦 配布準備完了: {result}")
        print("\n配布時の説明:")
        print("- Apple Silicon Mac & Intel Mac両対応")
        print("- Python/Poetry環境不要")
        print("- RVC indexファイル完全対応")
    else:
        print("\n❌ DMG作成失敗")
        sys.exit(1)
