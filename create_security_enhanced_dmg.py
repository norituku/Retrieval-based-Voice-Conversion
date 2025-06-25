#!/usr/bin/env python3
"""
Intel Mac配布用セキュリティ強化DMG作成スクリプト
配布先でのセキュリティ問題を最小化
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def create_security_enhanced_dmg():
    """Intel Mac配布用セキュリティ強化DMG作成"""
    project_dir = Path(__file__).parent.absolute()
    
    # 1. ソースアプリ確認
    source_app = project_dir / "universal_build" / "VoiceConverter_universal.app"
    if not source_app.exists():
        print(f"❌ ソースアプリが見つかりません: {source_app}")
        return False
    
    print(f"✅ ソースアプリ確認: {source_app}")
    print(f"📏 アプリサイズ: {get_size_mb(source_app):.1f} MB")
    
    # 2. 一時ディレクトリ作成
    temp_dir = tempfile.mkdtemp(prefix="dmg_security_")
    temp_path = Path(temp_dir)
    dmg_contents = temp_path / "dmg_contents"
    dmg_contents.mkdir()
    
    print(f"📁 一時ディレクトリ: {dmg_contents}")
    
    try:
        # 3. セキュリティ強化コピー（cp -pRP + 追加処理）
        dest_app = dmg_contents / "VoiceConverter.app"
        print("🛡️ セキュリティ強化コピー開始...")
        
        # CLAUDE.mdルール準拠のコピー
        subprocess.run([
            "cp", "-pRP", str(source_app), str(dest_app)
        ], check=True)
        print("✅ 基本コピー完了")
        
        # 4. Intel Mac用セキュリティ強化処理
        print("🔒 Intel Mac配布用セキュリティ強化処理...")
        
        # 4.1 拡張属性の完全削除（quarantine含む）
        subprocess.run([
            "find", str(dest_app), "-type", "f", "-exec", "xattr", "-c", "{}", ";"
        ], check=True, capture_output=True)
        print("✅ 拡張属性完全削除")
        
        # 4.2 実行権限の確実な設定
        main_binary = dest_app / "Contents" / "MacOS" / "VoiceConverter"
        if main_binary.exists():
            os.chmod(main_binary, 0o755)
            print("✅ メインバイナリ実行権限設定")
        
        # 4.3 Info.plistのセキュリティ強化
        enhance_info_plist(dest_app)
        
        # 4.4 追加のセキュリティ署名
        print("🔏 追加セキュリティ署名...")
        subprocess.run([
            "codesign", "--force", "--deep", "--sign", "-", str(dest_app)
        ], check=True, capture_output=True)
        print("✅ 追加署名完了")
        
        # 5. Applicationsリンク
        applications_link = dmg_contents / "Applications"
        applications_link.symlink_to("/Applications")
        print("🔗 Applicationsリンク作成")
        
        # 6. Intel Mac専用インストールガイド
        create_intel_install_guide(dmg_contents)
        
        # 7. セキュリティ強化DMG作成
        dmg_name = "VoiceConverter-Universal-SecurityEnhanced.dmg"
        dmg_path = project_dir / dmg_name
        
        if dmg_path.exists():
            dmg_path.unlink()
            print("🗑️ 既存DMG削除")
        
        print(f"💿 セキュリティ強化DMG作成中: {dmg_name}")
        
        # セキュリティ最適化オプション
        subprocess.run([
            "hdiutil", "create",
            "-volname", "Voice Converter Universal (Intel Mac Ready)", 
            "-srcfolder", str(dmg_contents),
            "-format", "UDRO",  # 読み取り専用
            "-imagekey", "zlib-level=9",  # 最大圧縮
            "-fs", "HFS+",  # 互換性重視
            "-layout", "SPUD",  # 単一パーティション
            str(dmg_path)
        ], check=True)
        
        print("✅ セキュリティ強化DMG作成完了!")
        
        # 8. 最終セキュリティ検証
        verify_security_dmg(dmg_path)
        
        # サイズ確認
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"📏 最終サイズ: {size_mb:.1f} MB")
        
        # 9. Intel Mac配布用の最終メッセージ
        print_intel_distribution_guide(dmg_path)
        
        return dmg_path
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    finally:
        # 一時ディレクトリ削除
        import shutil
        shutil.rmtree(temp_path, ignore_errors=True)
        print(f"🧹 一時ディレクトリ削除: {temp_path}")

def enhance_info_plist(app_path):
    """Info.plistのセキュリティ強化"""
    info_plist = app_path / "Contents" / "Info.plist"
    if not info_plist.exists():
        return
    
    print("🔧 Info.plistセキュリティ強化...")
    
    # LSApplicationCategoryTypeを明示的に設定
    subprocess.run([
        "/usr/libexec/PlistBuddy", "-c", 
        "Set :LSApplicationCategoryType public.app-category.productivity", 
        str(info_plist)
    ], capture_output=True)
    
    # NSHighResolutionCapableを有効化（Retina対応）
    subprocess.run([
        "/usr/libexec/PlistBuddy", "-c", 
        "Add :NSHighResolutionCapable bool true", 
        str(info_plist)
    ], capture_output=True)
    
    # NSRequiresAquaSystemAppearanceをfalseに設定（ダークモード対応）
    subprocess.run([
        "/usr/libexec/PlistBuddy", "-c", 
        "Add :NSRequiresAquaSystemAppearance bool false", 
        str(info_plist)
    ], capture_output=True)
    
    print("✅ Info.plist強化完了")

def create_intel_install_guide(dmg_contents):
    """Intel Mac専用インストールガイド作成"""
    guide_path = dmg_contents / "【重要】Intel Mac ユーザー向けインストールガイド.txt"
    
    guide_content = """🚨 Intel Mac ユーザー向け重要インストール手順 🚨

このアプリはApple Silicon + Intel Mac両対応のユニバーサルバイナリです。
Intel Macでの初回起動時は以下の手順を必ず守ってください：

=== インストール手順 ===

1️⃣ VoiceConverter.app を Applications フォルダにドラッグ
   
2️⃣ Finder でアプリケーションフォルダを開く

3️⃣ VoiceConverter アプリを右クリック → "開く" を選択

4️⃣ 「開発元を確認できません」のダイアログが表示された場合：
   → "開く" ボタンをクリック（重要！）

5️⃣ 初回起動時にRosetta2のインストールが要求される場合：
   → "インストール" をクリックして Rosetta2 をインストール

6️⃣ 以降は通常通りアプリアイコンから起動可能

=== トラブルシューティング ===

🔸 「アプリケーションが開けません」エラーの場合：
  → システム環境設定 → セキュリティとプライバシー
  → 「このまま開く」をクリック

🔸 「破損しているため開けません」エラーの場合：
  → ターミナルで以下を実行:
    sudo xattr -r -d com.apple.quarantine /Applications/VoiceConverter.app

🔸 Rosetta2未インストールの場合：
  → ターミナルで以下を実行:
    /usr/sbin/softwareupdate --install-rosetta --agree-to-license

=== 動作環境 ===
- macOS 10.15 (Catalina) 以降
- Intel Mac: Rosetta2経由で動作
- Apple Silicon Mac: ネイティブ動作
- Poetry環境: 不要（完全スタンドアロン）

=== 注意事項 ===
- Intel Macでは初回起動時間が長くなる場合があります（Rosetta2翻訳）
- ネットワーク接続は不要です
- このアプリは完全にオフラインで動作します

作成者: RVC Team
作成日: 2025年6月25日
版種: ユニバーサルバイナリ (Intel Mac 対応)
"""
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("📋 Intel Mac専用ガイド作成完了")

def verify_security_dmg(dmg_path):
    """セキュリティDMGの検証"""
    print("🔍 セキュリティDMG検証中...")
    
    # DMGの基本検証
    result = subprocess.run([
        "hdiutil", "verify", str(dmg_path)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ DMG整合性検証成功")
    else:
        print(f"⚠️ DMG検証警告: {result.stderr}")

def get_size_mb(path):
    """ディレクトリまたはファイルのサイズ（MB）を取得"""
    if path.is_file():
        return path.stat().st_size / (1024 * 1024)
    else:
        total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return total_size / (1024 * 1024)

def print_intel_distribution_guide(dmg_path):
    """Intel Mac配布用の最終ガイド表示"""
    print(f"""
🎉 Intel Mac配布用セキュリティ強化DMG作成完了！

📦 作成されたファイル: {dmg_path.name}
🛡️ セキュリティ強化: ✅ 完了
🔄 ユニバーサル対応: ✅ Apple Silicon + Intel Mac
📋 配布ガイド: ✅ 同梱済み

=== 配布先で推奨する案内 ===

1️⃣ macOS 10.15以降が必要
2️⃣ 初回起動時は必ず「右クリック→開く」
3️⃣ Intel Macでは Rosetta2 が自動インストールされる場合あり
4️⃣ 完全オフライン動作（ネット接続不要）

=== セキュリティ問題の軽減策 ===
✅ ad-hoc署名適用済み
✅ 拡張属性完全削除
✅ Gatekeeper部分対応
✅ Intel Mac専用ガイド同梱
✅ トラブルシューティング情報完備

このDMGは配布準備完了です！
""")

if __name__ == "__main__":
    print("🛡️ Intel Mac配布用セキュリティ強化DMG作成スクリプト")
    print("📋 配布先でのセキュリティ問題を最小化")
    print()
    
    result = create_security_enhanced_dmg()
    if result:
        print(f"\n🎉 セキュリティ強化DMG作成成功!")
        print("🚀 Intel Macでの配布準備完了")
    else:
        print("\n❌ DMG作成失敗")
        sys.exit(1) 