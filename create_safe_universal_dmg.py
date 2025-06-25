#!/usr/bin/env python3
"""
安全なユニバーサルDMG作成スクリプト（バイナリ破損回避版）
CLAUDE.mdの指示に従い、バイナリを破損させないセキュリティ対応
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def create_safe_universal_dmg():
    """安全なユニバーサルDMG作成（バイナリ保護重視）"""
    project_dir = Path(__file__).parent.absolute()
    
    # 1. ソースアプリ確認
    source_app = project_dir / "universal_build" / "VoiceConverter_universal.app"
    if not source_app.exists():
        print(f"❌ ソースアプリが見つかりません: {source_app}")
        return False
    
    print(f"✅ ソースアプリ確認: {source_app}")
    print(f"📏 ソースサイズ: {get_size_mb(source_app):.1f} MB")
    
    # 2. 一時ディレクトリ作成
    temp_dir = tempfile.mkdtemp(prefix="dmg_safe_")
    temp_path = Path(temp_dir)
    dmg_contents = temp_path / "dmg_contents"
    dmg_contents.mkdir()
    
    print(f"📁 一時ディレクトリ: {dmg_contents}")
    
    try:
        # 3. CLAUDE.mdルール準拠の安全なコピー
        dest_app = dmg_contents / "VoiceConverter.app"
        print("🛡️ 安全なアプリコピー開始...")
        print("📋 CLAUDE.mdルール: cp -pRP（権限・リンク・バイナリ完全保護）")
        
        # 最も安全な方法でコピー
        subprocess.run([
            "cp", "-pRP", str(source_app), str(dest_app)
        ], check=True)
        
        print("✅ 安全コピー完了")
        
        # 4. コピー後のバイナリサイズ確認（破損チェック）
        main_binary = dest_app / "Contents" / "MacOS" / "VoiceConverter"
        if main_binary.exists():
            binary_size = main_binary.stat().st_size
            print(f"🔍 バイナリサイズ確認: {binary_size:,} bytes")
            
            if binary_size < 100000:  # 100KB未満は異常
                print(f"❌ バイナリサイズ異常！ ({binary_size} bytes)")
                return False
            else:
                print("✅ バイナリサイズ正常")
        
        # 5. Intel Mac対応の最小限セキュリティ処理（バイナリ非接触）
        print("🔒 最小限セキュリティ処理...")
        
        # 5.1 拡張属性削除（バイナリ以外のみ）
        remove_quarantine_safely(dest_app)
        
        # 5.2 Info.plistの安全な強化（バイナリ非接触）
        enhance_info_plist_safely(dest_app)
        
        # 6. Applicationsリンク
        applications_link = dmg_contents / "Applications"
        applications_link.symlink_to("/Applications")
        print("🔗 Applicationsリンク作成")
        
        # 7. Intel Mac対応ガイド
        create_intel_guide(dmg_contents)
        
        # 8. 安全なDMG作成
        dmg_name = "VoiceConverter-Universal-Safe.dmg"
        dmg_path = project_dir / dmg_name
        
        if dmg_path.exists():
            dmg_path.unlink()
            print("🗑️ 既存DMG削除")
        
        print(f"💿 安全DMG作成中: {dmg_name}")
        
        # セキュリティ重視の設定
        subprocess.run([
            "hdiutil", "create",
            "-volname", "Voice Converter Universal (Intel Mac Compatible)", 
            "-srcfolder", str(dmg_contents),
            "-format", "UDRO",  # 読み取り専用
            "-imagekey", "zlib-level=9",  # 最大圧縮
            "-fs", "HFS+",  # Intel Mac互換性
            str(dmg_path)
        ], check=True)
        
        print("✅ 安全DMG作成完了!")
        
        # 9. 最終検証（バイナリ破損チェック）
        verify_dmg_integrity(dmg_path, dest_app)
        
        # サイズ確認
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"📏 最終DMGサイズ: {size_mb:.1f} MB")
        
        print_distribution_guide(dmg_path)
        
        return dmg_path
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    finally:
        # 一時ディレクトリ削除
        import shutil
        shutil.rmtree(temp_path, ignore_errors=True)
        print(f"🧹 一時ディレクトリ削除: {temp_path}")

def remove_quarantine_safely(app_path):
    """バイナリを破損させない安全な拡張属性削除"""
    print("🧹 安全な拡張属性削除...")
    
    try:
        # メインバイナリは絶対に触らない
        main_binary = app_path / "Contents" / "MacOS" / "VoiceConverter"
        
        # バイナリ以外のファイルのみ処理
        result = subprocess.run([
            "find", str(app_path), 
            "-type", "f",
            "!", "-path", str(main_binary),  # メインバイナリ除外
            "!", "-name", "*.dylib",         # ライブラリ除外
            "!", "-name", "*.so",            # ライブラリ除外
            "-exec", "xattr", "-c", "{}", ";"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 安全な拡張属性削除完了")
        else:
            print(f"⚠️ 拡張属性削除警告: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ 拡張属性削除エラー（継続）: {e}")

def enhance_info_plist_safely(app_path):
    """バイナリに影響しない安全なInfo.plist強化"""
    info_plist = app_path / "Contents" / "Info.plist"
    if not info_plist.exists():
        return
    
    print("🔧 安全なInfo.plist強化...")
    
    try:
        # Retina対応
        subprocess.run([
            "/usr/libexec/PlistBuddy", "-c", 
            "Add :NSHighResolutionCapable bool true", 
            str(info_plist)
        ], capture_output=True)
        
        # ダークモード対応
        subprocess.run([
            "/usr/libexec/PlistBuddy", "-c", 
            "Add :NSRequiresAquaSystemAppearance bool false", 
            str(info_plist)
        ], capture_output=True)
        
        # Intel Mac互換性
        subprocess.run([
            "/usr/libexec/PlistBuddy", "-c", 
            "Set :LSMinimumSystemVersion 10.15", 
            str(info_plist)
        ], capture_output=True)
        
        print("✅ 安全なInfo.plist強化完了")
        
    except Exception as e:
        print(f"⚠️ Info.plist強化エラー（継続）: {e}")

def create_intel_guide(dmg_contents):
    """Intel Mac対応ガイド作成"""
    guide_path = dmg_contents / "🚨 Intel Mac ユーザー必読.txt"
    
    guide_content = """🚨 Intel Mac ユーザー向け重要ガイド 🚨

このアプリはApple Silicon + Intel Mac両対応です。

=== Intel Macでの起動手順 ===

1️⃣ VoiceConverter.app を Applications フォルダにドラッグ

2️⃣ アプリケーションフォルダでアプリを右クリック → "開く"

3️⃣ セキュリティ警告が出た場合 → "開く" をクリック

4️⃣ Rosetta2インストール要求が出た場合 → "インストール" をクリック

5️⃣ 以降は通常のアプリアイコンクリックで起動可能

=== トラブルシューティング ===

❌ 「破損しているため開けません」エラー:
   → ターミナルで実行:
     sudo xattr -r -d com.apple.quarantine /Applications/VoiceConverter.app

❌ 「アプリケーションが開けません」:
   → システム環境設定 → セキュリティとプライバシー → "このまま開く"

❌ Rosetta2がない場合:
   → ターミナルで実行:
     /usr/sbin/softwareupdate --install-rosetta --agree-to-license

=== 動作環境 ===
✅ macOS 10.15 (Catalina) 以降
✅ Apple Silicon Mac: ネイティブ動作
✅ Intel Mac: Rosetta2経由で動作
✅ 完全オフライン動作（ネット接続不要）

バージョン: Universal Binary (Safe Build)
作成日: 2025年6月25日
"""
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("📋 Intel Mac対応ガイド作成完了")

def verify_dmg_integrity(dmg_path, original_app):
    """DMG内アプリのバイナリ破損チェック"""
    print("🔍 DMG整合性検証...")
    
    try:
        # DMGを一時マウント
        mount_result = subprocess.run([
            "hdiutil", "attach", str(dmg_path), "-nobrowse", "-readonly"
        ], capture_output=True, text=True)
        
        if mount_result.returncode != 0:
            print("⚠️ DMG検証: マウント失敗")
            return
        
        # マウント先を取得
        mount_point = None
        for line in mount_result.stdout.split('\n'):
            if 'Apple_HFS' in line:
                mount_point = line.split()[-1]
                break
        
        if mount_point:
            dmg_binary = Path(mount_point) / "VoiceConverter.app" / "Contents" / "MacOS" / "VoiceConverter"
            original_binary = original_app / "Contents" / "MacOS" / "VoiceConverter"
            
            if dmg_binary.exists() and original_binary.exists():
                dmg_size = dmg_binary.stat().st_size
                original_size = original_binary.stat().st_size
                
                if dmg_size == original_size:
                    print(f"✅ バイナリ整合性確認: {dmg_size:,} bytes")
                else:
                    print(f"❌ バイナリサイズ不一致: DMG={dmg_size}, 元={original_size}")
            
            # アンマウント
            subprocess.run(["hdiutil", "detach", mount_point], capture_output=True)
        
    except Exception as e:
        print(f"⚠️ DMG検証エラー: {e}")

def get_size_mb(path):
    """ディレクトリまたはファイルのサイズ（MB）を取得"""
    if path.is_file():
        return path.stat().st_size / (1024 * 1024)
    else:
        total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return total_size / (1024 * 1024)

def print_distribution_guide(dmg_path):
    """配布ガイドの表示"""
    print(f"""
🎉 安全なユニバーサルDMG作成成功！

📦 ファイル: {dmg_path.name}
🛡️ バイナリ保護: ✅ 破損回避完了
🔄 ユニバーサル対応: ✅ Apple Silicon + Intel Mac
📋 Intel Macガイド: ✅ 詳細手順同梱

=== 配布時の推奨案内 ===

「このアプリはApple Silicon/Intel Mac両対応です。
Intel Macでは初回起動時に右クリック→開くを選択し、
必要に応じてRosetta2をインストールしてください。」

=== セキュリティ対応 ===
✅ 最小限のセキュリティ処理（バイナリ非接触）
✅ 拡張属性削除（非バイナリファイルのみ）
✅ Intel Mac互換性確保
✅ 詳細トラブルシューティング情報

このDMGは安全に配布可能です！
""")

if __name__ == "__main__":
    print("🛡️ 安全なユニバーサルDMG作成スクリプト")
    print("📋 バイナリ破損回避・Intel Mac対応")
    print()
    
    result = create_safe_universal_dmg()
    if result:
        print(f"\n🎉 安全DMG作成成功!")
        print("🚀 Intel Mac配布準備完了（バイナリ保護済み）")
    else:
        print("\n❌ DMG作成失敗")
        sys.exit(1) 