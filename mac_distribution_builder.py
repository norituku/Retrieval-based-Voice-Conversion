#!/usr/bin/env python3
"""
Mac Distribution Builder for RVC Voice Converter
商用配布レベルのmacOSアプリビルダー

記事参考: https://techblog.hacomono.jp/entry/2024/06/04/1100
戦略:
- マルチファイル配布（--standalone）
- 拡張属性対応
- ユーザーフレンドリーなDMG
- セキュリティ制限への対処
"""
import subprocess
import sys
import os
import shutil
import time
import tempfile
from pathlib import Path
import json

class MacDistributionBuilder:
    """商用配布レベルのmacOSアプリビルダー"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.build_timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.app_name = "RVC Voice Converter"
        self.app_version = "1.0.0"
        
    def check_prerequisites(self):
        """配布ビルドの前提条件チェック"""
        print("🔍 配布ビルド前提条件チェック...")
        
        requirements = {
            "Poetry環境": self._check_poetry(),
            "Nuitka": self._check_nuitka(),
            "GUI実行ファイル": self._check_gui_file(),
            "音声モデル": self._check_models(),
            "コード署名環境": self._check_signing()
        }
        
        all_ok = True
        for name, status in requirements.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {name}")
            if not status:
                all_ok = False
        
        return all_ok
    
    def _check_poetry(self):
        """Poetry環境確認"""
        try:
            result = subprocess.run(["poetry", "env", "info"], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_nuitka(self):
        """Nuitka確認"""
        try:
            result = subprocess.run(["poetry", "run", "python", "-c", "import nuitka"], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_gui_file(self):
        """GUIファイル確認"""
        return (self.project_root / "gui_dark_mode_enhanced.py").exists()
    
    def _check_models(self):
        """音声モデル確認"""
        model_dir = self.project_root / "model_dir"
        if not model_dir.exists():
            return False
        pth_files = list(model_dir.rglob("*.pth"))
        return len(pth_files) > 0
    
    def _check_signing(self):
        """コード署名環境確認（開発版では任意）"""
        try:
            result = subprocess.run(["security", "find-identity", "-v"], capture_output=True, text=True)
            has_dev_id = "Developer ID Application" in result.stdout
            print(f"    📝 Apple Developer ID: {'あり' if has_dev_id else 'なし（開発版として続行）'}")
            return True  # 開発版では常にTrue
        except:
            print("    📝 コード署名環境: 不明（開発版として続行）")
            return True
    
    def create_distribution_info(self):
        """配布情報ファイル作成"""
        print("📝 配布情報ファイル作成中...")
        
        info = {
            "app_name": self.app_name,
            "version": self.app_version,
            "build_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python_version": sys.version.split()[0],
            "distribution_notes": {
                "security": "macOS Gatekeeper制限があります。初回起動時は右クリック→開くを使用してください。",
                "requirements": "macOS 10.15以上、Poetry環境（音声変換用）",
                "features": [
                    "Enhanced Voice Converter統合",
                    "6つの高品質音声モデル内蔵",
                    "ダークモードGUI",
                    "ログ重要度分析",
                    "MPS最適化済み"
                ]
            }
        }
        
        info_path = self.project_root / "distribution_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配布情報保存: {info_path}")
        return info_path
    
    def build_standalone_app(self):
        """スタンドアロンアプリビルド（マルチファイル配布）"""
        print("🔨 スタンドアロンアプリビルド開始...")
        
        # 出力ディレクトリ
        output_dir = self.project_root / f"dist_mac_distribution_{self.build_timestamp}"
        output_dir.mkdir(exist_ok=True)
        
        # アプリアイコン
        icon_path = self.project_root / "app_icons" / "rvc_icon.icns"
        
        # Nuitkaコマンド（商用配布最適化）
        nuitka_cmd = [
            "poetry", "run", "python", "-m", "nuitka",
            
            # 基本設定
            "--standalone",  # マルチファイル配布（推奨）
            "--macos-create-app-bundle",
            f"--output-dir={output_dir}",
            
            # アプリケーション情報
            f"--macos-app-name={self.app_name}",
            f"--macos-app-version={self.app_version}",
            "--company-name=RVC Voice Converter Project",
            "--product-name=RVC Voice Converter",
            "--file-description=Real-time Voice Conversion Application",
            
            # アイコン・UI
            f"--macos-app-icon={icon_path}" if icon_path.exists() else "--macos-app-icon=none",
            
            # 依存関係の完全統合
            "--follow-imports",
            "--follow-import-to=enhanced_voice_converter",
            "--follow-import-to=log_importance_analyzer",
            "--follow-import-to=gui_modules",
            "--follow-import-to=rvc",
            
            # 必須モジュール
            "--include-module=tkinter",
            "--include-module=enhanced_voice_converter",
            "--include-module=log_importance_analyzer",
            
            # データファイル
            "--include-data-dir=model_dir=model_dir",
            "--include-data-dir=rvc=rvc",
            "--include-data-dir=gui_modules=gui_modules",
            "--include-data-dir=configs=configs",
            "--include-data-files=enhanced_voice_converter.py=enhanced_voice_converter.py",
            "--include-data-files=log_importance_analyzer.py=log_importance_analyzer.py",
            "--include-data-files=rvc_config.py=rvc_config.py",
            "--include-data-files=pyproject.toml=pyproject.toml",
            
            # 最適化設定
            "--assume-yes-for-downloads",
            "--remove-output",
            "--show-progress",
            
            # プラグイン（エラー回避版）
            "--plugin-enable=torch",
            
            # ソースファイル
            "gui_dark_mode_enhanced.py"
        ]
        
        print("🚀 Nuitkaビルド実行中（配布版最適化）...")
        print("  ⏳ 5-15分程度かかります...")
        
        # ビルド実行
        start_time = time.time()
        process = subprocess.Popen(
            nuitka_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # リアルタイム出力
        for line in process.stdout:
            if "%" in line or "INFO:" in line:
                print(f"  {line.strip()}")
        
        process.wait()
        elapsed_time = time.time() - start_time
        
        if process.returncode == 0:
            print(f"✅ ビルド成功！（{elapsed_time:.1f}秒）")
            
            # アプリパスを特定
            app_path = output_dir / f"{self.app_name}.app"
            if not app_path.exists():
                # 代替パス確認
                for item in output_dir.iterdir():
                    if item.suffix == ".app":
                        app_path = item
                        break
            
            return app_path if app_path.exists() else None
        else:
            print(f"❌ ビルド失敗（{elapsed_time:.1f}秒）")
            return None
    
    def handle_macos_security(self, app_path):
        """macOSセキュリティ制限への対応"""
        print("🔐 macOSセキュリティ制限対応中...")
        
        if not app_path or not app_path.exists():
            print("❌ アプリパスが無効")
            return False
        
        try:
            # 拡張属性を削除（重要！）
            print("  📝 拡張属性（xattr）削除中...")
            result = subprocess.run([
                "xattr", "-cr", str(app_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ 拡張属性削除完了")
            else:
                print(f"  ⚠️ 拡張属性削除警告: {result.stderr}")
            
            # アドホック署名（開発用）
            print("  ✍️ アドホック署名実行中...")
            sign_result = subprocess.run([
                "codesign", "--force", "--deep", "--sign", "-", str(app_path)
            ], capture_output=True, text=True)
            
            if sign_result.returncode == 0:
                print("  ✅ アドホック署名完了")
            else:
                print(f"  ⚠️ 署名警告: {sign_result.stderr}")
            
            # 署名検証
            verify_result = subprocess.run([
                "codesign", "--verify", "--verbose", str(app_path)
            ], capture_output=True, text=True)
            
            if verify_result.returncode == 0:
                print("  ✅ 署名検証成功")
                return True
            else:
                print(f"  ⚠️ 署名検証警告: {verify_result.stderr}")
                return True  # 警告でも続行
                
        except Exception as e:
            print(f"❌ セキュリティ対応エラー: {e}")
            return False
    
    def create_user_friendly_dmg(self, app_path):
        """ユーザーフレンドリーなDMG作成"""
        print("💿 配布用DMG作成中...")
        
        if not app_path or not app_path.exists():
            print("❌ アプリパスが無効")
            return None
        
        dmg_name = f"{self.app_name.replace(' ', '_')}_v{self.app_version}_{self.build_timestamp}.dmg"
        dmg_path = self.project_root / dmg_name
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # アプリをコピー
                temp_app = temp_path / app_path.name
                shutil.copytree(app_path, temp_app)
                
                # Applications リンク
                applications_link = temp_path / "Applications"
                applications_link.symlink_to("/Applications")
                
                # ユーザーガイド作成
                guide_content = f"""RVC Voice Converter v{self.app_version}

🎯 インストール手順:
1. RVC Voice Converter.app を Applications フォルダにドラッグ&ドロップ
2. アプリケーションフォルダから起動

⚠️ 初回起動時の重要な注意:
- macOSセキュリティにより「開発元が未確認」と表示される場合があります
- その場合は以下の手順で起動してください：
  1. アプリを右クリック
  2. 「開く」を選択
  3. 「開く」をクリックして許可

🎵 主な機能:
- リアルタイム音声変換
- 6つの高品質音声モデル内蔵
- Enhanced Voice Converter統合
- ダークモードGUI
- ログ重要度分析

📋 システム要件:
- macOS 10.15以上
- Poetry環境（音声変換処理用）

🔧 トラブルシューティング:
- アプリが起動しない場合: ターミナルで「poetry install」を実行
- 変換できない場合: model_dirにモデルファイルがあることを確認

💡 サポート:
GitHub: https://github.com/your-repo/rvc-voice-converter

© 2024 RVC Voice Converter Project
"""
                
                guide_path = temp_path / "🎯 インストールガイド.txt"
                with open(guide_path, 'w', encoding='utf-8') as f:
                    f.write(guide_content)
                
                # DMG作成
                create_cmd = [
                    "hdiutil", "create",
                    "-volname", f"{self.app_name} v{self.app_version}",
                    "-srcfolder", str(temp_path),
                    "-ov",
                    "-format", "UDZO",
                    "-imagekey", "zlib-level=9",
                    str(dmg_path)
                ]
                
                result = subprocess.run(create_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ DMG作成完了: {dmg_path}")
                    
                    # DMGサイズ表示
                    if dmg_path.exists():
                        size_mb = dmg_path.stat().st_size / 1024 / 1024
                        print(f"📊 DMGサイズ: {size_mb:.1f}MB")
                    
                    return dmg_path
                else:
                    print(f"❌ DMG作成失敗: {result.stderr}")
                    return None
                    
        except Exception as e:
            print(f"❌ DMG作成エラー: {e}")
            return None
    
    def run_distribution_build(self):
        """配布ビルド実行"""
        print("🚀 RVC Voice Converter 配布ビルド開始")
        print("=" * 60)
        
        # 前提条件チェック
        if not self.check_prerequisites():
            print("❌ 前提条件が満たされていません")
            return False
        
        # 配布情報作成
        self.create_distribution_info()
        
        # アプリビルド
        app_path = self.build_standalone_app()
        if not app_path:
            print("❌ アプリビルド失敗")
            return False
        
        # セキュリティ対応
        if not self.handle_macos_security(app_path):
            print("⚠️ セキュリティ対応で警告がありましたが続行します")
        
        # DMG作成
        dmg_path = self.create_user_friendly_dmg(app_path)
        if not dmg_path:
            print("❌ DMG作成失敗")
            return False
        
        # 最終結果
        print("\n" + "=" * 60)
        print("🎉 配布ビルド完了！")
        print(f"\n📱 アプリケーション:")
        print(f"   {app_path}")
        print(f"💿 配布用DMG:")
        print(f"   {dmg_path}")
        print(f"\n🎯 配布方法:")
        print(f"  1. DMGファイルをユーザーに送付")
        print(f"  2. インストールガイドを参照してもらう")
        print(f"  3. 初回起動時は右クリック→開くで許可")
        print(f"\n⚠️ 注意事項:")
        print(f"  • Gatekeeper制限により初回起動時に警告が表示されます")
        print(f"  • 商用配布にはApple Developer IDでの署名が推奨されます")
        
        return True

def main():
    """メイン実行"""
    try:
        builder = MacDistributionBuilder()
        success = builder.run_distribution_build()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ビルダーエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()