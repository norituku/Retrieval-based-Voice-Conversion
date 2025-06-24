#!/usr/bin/env python3
"""
RVC Voice Converter 配布用DMG作成ツール
説明ドキュメント同封版
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("📦 RVC Voice Converter 配布用DMG作成ツール")
    
    project_dir = Path(__file__).parent.absolute()
    print(f"📁 プロジェクトディレクトリ: {project_dir}")
    
    # 1. 必要ファイルの確認
    app_path = project_dir / "dist" / "RVC Voice Converter Final.app"
    if not app_path.exists():
        print("❌ RVC Voice Converter Final.app が見つかりません")
        print("先に create_final_standalone.py を実行してください")
        return False
    
    print(f"✅ アプリケーション確認: {app_path}")
    
    # 2. DMG用ディレクトリ作成
    dmg_contents = project_dir / "dmg_contents"
    if dmg_contents.exists():
        shutil.rmtree(dmg_contents)
    dmg_contents.mkdir()
    
    print(f"📁 DMG内容ディレクトリ作成: {dmg_contents}")
    
    # 3. アプリケーションをコピー
    app_dest = dmg_contents / "RVC Voice Converter Final.app"
    print("📱 アプリケーションをコピー中...")
    shutil.copytree(app_path, app_dest)
    print("✅ アプリケーションコピー完了")
    
    # 4. Applicationsフォルダへのシンボリックリンク作成
    applications_link = dmg_contents / "Applications"
    if applications_link.exists():
        applications_link.unlink()
    applications_link.symlink_to("/Applications")
    print("🔗 Applicationsフォルダリンク作成完了")
    
    # 5. 使い方ガイドをコピー
    user_guide = project_dir / "RVC使い方ガイド.txt"
    if user_guide.exists():
        shutil.copy2(user_guide, dmg_contents / "使い方ガイド.txt")
        print("📖 使い方ガイドコピー完了")
    
    # 6. インストール説明書を作成
    install_guide = dmg_contents / "インストール方法.txt"
    with open(install_guide, 'w', encoding='utf-8') as f:
        f.write("""===============================================
    RVC Voice Converter - インストール方法
===============================================

【簡単3ステップでインストール完了！】

ステップ1: アプリをApplicationsフォルダに移動
┌─────────────────────────────────┐
│ "RVC Voice Converter Final.app" を    │
│ "Applications" フォルダにドラッグ      │
└─────────────────────────────────┘

ステップ2: アプリを起動
・Applicationsフォルダから「RVC Voice Converter Final」をダブルクリック
・または、Launchpadから起動

ステップ3: セキュリティ許可（初回のみ）
・「開発元が未確認」と表示されたら
・システム環境設定 → セキュリティとプライバシー
・「このまま開く」をクリック

【完了！】
以降は普通のアプリと同じように使用できます。

===============================================
            重要な特徴
===============================================

✅ インターネット接続不要
   一度インストールすれば、オフラインで完全動作

✅ 追加インストール不要  
   Python、Poetry等の事前準備は一切不要

✅ 高品質音声変換
   AI技術による自然な音声変換

✅ 安全・無料
   完全無料、個人利用は合法

===============================================
            使い方
===============================================

詳しい使い方は「使い方ガイド.txt」をご覧ください。
中学生でも分かるように詳しく説明しています。

===============================================
            サポート
===============================================

・使い方が分からない → 「使い方ガイド.txt」を確認
・技術的な問題 → GitHub の Issues セクション
・一般的な質問 → インターネットで「RVC 使い方」で検索

===============================================
            注意事項
===============================================

【合法的な使用】
・個人の練習、趣味での使用はOK
・商用利用時は著作権に注意
・他人になりすましての悪用は禁止

【推奨環境】
・macOS 10.15 以降
・メモリ 8GB以上推奨
・ストレージ 10GB以上の空き容量

===============================================
            楽しく安全にお使いください！
===============================================
""")
    print("📝 インストール説明書作成完了")
    
    # 7. ライセンス情報をコピー
    license_file = project_dir / "LICENSE"
    if license_file.exists():
        shutil.copy2(license_file, dmg_contents / "LICENSE.txt")
        print("📄 ライセンス情報コピー完了")
    
    # 8. README（概要）を作成
    readme_file = dmg_contents / "README.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("""===============================================
        RVC Voice Converter Final
        AI音声変換アプリケーション
===============================================

【このアプリについて】
RVC (Retrieval-based Voice Conversion) は、
AI技術を使って音声を別の声に変換する
革新的なアプリケーションです。

【ファイル構成】
📱 RVC Voice Converter Final.app
   → メインアプリケーション（これを使います）

📖 使い方ガイド.txt  
   → 詳しい使用方法（必読）

📝 インストール方法.txt
   → インストール手順

📄 LICENSE.txt
   → ライセンス情報

🔗 Applications
   → Applicationsフォルダへのショートカット

【最初にすること】
1. 「インストール方法.txt」を読む
2. アプリをApplicationsフォルダに移動
3. 「使い方ガイド.txt」を読む
4. アプリを楽しむ！

【バージョン情報】
- バージョン: Final 1.0
- 対応OS: macOS 10.15以降  
- 作成日: 2024年6月
- ライセンス: オープンソース

【お楽しみください！】
""")
    print("📄 README作成完了")
    
    # 9. DMGディスクイメージを作成
    dmg_name = "RVC-Voice-Converter-Final-Complete.dmg"
    dmg_path = project_dir / dmg_name
    
    print(f"💿 DMGディスクイメージ作成中: {dmg_name}")
    print("⚠️  この処理には数分かかります...")
    
    try:
        # 既存のDMGファイルを削除
        if dmg_path.exists():
            dmg_path.unlink()
        
        # DMG作成コマンド
        subprocess.run([
            "hdiutil", "create",
            "-volname", "RVC Voice Converter Final",
            "-srcfolder", str(dmg_contents),
            "-ov",
            "-format", "UDZO",  # 圧縮形式
            str(dmg_path)
        ], check=True)
        
        print("✅ DMGディスクイメージ作成完了!")
        
        # ファイルサイズを表示
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"📏 DMGサイズ: {size_mb:.1f} MB")
        
        # 一時ディレクトリを削除
        shutil.rmtree(dmg_contents)
        print("🧹 一時ファイル削除完了")
        
        return dmg_path
        
    except subprocess.CalledProcessError as e:
        print(f"❌ DMG作成エラー: {e}")
        return False

if __name__ == "__main__":
    result = main()
    if result:
        print("\n🎉 配布用DMG作成完了!")
        print(f"📦 ファイル: {result}")
        print("\n📋 DMG内容:")
        print("  📱 RVC Voice Converter Final.app - メインアプリ")
        print("  📖 使い方ガイド.txt - 詳細な使用方法")
        print("  📝 インストール方法.txt - インストール手順")
        print("  📄 README.txt - 概要説明")  
        print("  📄 LICENSE.txt - ライセンス情報")
        print("  🔗 Applications - Applicationsフォルダリンク")
        print("\n🚀 配布準備完了!")
        print("このDMGファイルを配布すれば、誰でも簡単にRVCを使用できます。")