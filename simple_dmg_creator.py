#!/usr/bin/env python3
"""
シンプルDMG作成スクリプト
確実で高速なmacOSアプリケーション配布パッケージ作成
"""
import subprocess
import shutil
import sys
import tempfile
from pathlib import Path

class SimpleDMGCreator:
    """シンプルDMG作成クラス"""
    
    def __init__(self, app_path, dmg_name="RVC_Voice_Converter"):
        self.app_path = Path(app_path)
        self.dmg_name = dmg_name
        self.dmg_filename = f"{dmg_name}.dmg"
        
    def create_temp_directory(self):
        """一時ディレクトリの作成"""
        print("📂 一時ディレクトリ作成中...")
        
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dmg_"))
        print(f"✅ 一時ディレクトリ: {self.temp_dir}")
        return self.temp_dir
    
    def setup_dmg_contents(self):
        """DMG内容のセットアップ"""
        print("📱 DMG内容をセットアップ中...")
        
        try:
            # アプリをコピー
            target_app = self.temp_dir / self.app_path.name
            shutil.copytree(self.app_path, target_app)
            print(f"  ✅ アプリコピー: {target_app.name}")
            
            # Applicationsフォルダへのシンボリックリンク
            applications_link = self.temp_dir / "Applications"
            applications_link.symlink_to("/Applications")
            print(f"  ✅ Applicationsリンク作成")
            
            # README作成
            readme_content = f"""RVC Voice Converter インストール手順

1. {self.app_path.name} を Applications フォルダにドラッグ&ドロップ
2. アプリケーションフォルダから RVC Voice Converter を起動
3. 必要に応じてセキュリティ設定でアプリを許可

注意: 初回起動時にセキュリティ警告が表示される場合があります。
システム設定 > プライバシーとセキュリティ から許可してください。

© 2024 RVC Voice Converter
"""
            
            readme_path = self.temp_dir / "README.txt"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"  ✅ README作成")
            
            return True
            
        except Exception as e:
            print(f"❌ DMG内容セットアップ失敗: {e}")
            return False
    
    def create_dmg_from_folder(self):
        """フォルダからDMGを作成"""
        print(f"💿 DMG作成中: {self.dmg_filename}")
        
        try:
            # 既存のDMGを削除
            dmg_path = Path(self.dmg_filename)
            if dmg_path.exists():
                dmg_path.unlink()
            
            # hdiutilでDMGを作成
            cmd = [
                "hdiutil", "create",
                "-srcfolder", str(self.temp_dir),
                "-volname", "RVC Voice Converter",
                "-fs", "HFS+",
                "-format", "UDZO",
                "-imagekey", "zlib-level=9",
                self.dmg_filename
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ DMG作成完了: {self.dmg_filename}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ DMG作成失敗: {e}")
            if e.stderr:
                print(f"エラー詳細: {e.stderr}")
            return False
    
    def verify_and_info_dmg(self):
        """DMGの検証と情報表示"""
        print(f"🔍 DMG検証中: {self.dmg_filename}")
        
        try:
            dmg_path = Path(self.dmg_filename)
            
            # ファイルサイズ確認
            size_mb = dmg_path.stat().st_size / 1024 / 1024
            print(f"  📊 DMGサイズ: {size_mb:.1f} MB")
            
            # DMG検証
            verify_cmd = ["hdiutil", "verify", str(dmg_path)]
            subprocess.run(verify_cmd, check=True, capture_output=True)
            print(f"  ✅ DMG検証成功")
            
            # DMG情報表示
            info_cmd = ["hdiutil", "imageinfo", str(dmg_path)]
            info_result = subprocess.run(info_cmd, capture_output=True, text=True)
            
            if info_result.returncode == 0:
                # 重要な情報のみ抽出
                for line in info_result.stdout.split('\\n'):
                    if any(keyword in line for keyword in ['Format:', 'Compressed:', 'Size:']):
                        print(f"  📋 {line.strip()}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ DMG検証失敗: {e}")
            return False
        except Exception as e:
            print(f"❌ DMG情報取得失敗: {e}")
            return False
    
    def cleanup(self):
        """一時ファイルのクリーンアップ"""
        print("🧹 一時ファイルクリーンアップ中...")
        
        try:
            if hasattr(self, 'temp_dir') and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print(f"✅ クリーンアップ完了")
        except Exception as e:
            print(f"⚠️ クリーンアップ警告: {e}")
    
    def create_simple_dmg(self):
        """シンプルDMG作成プロセス"""
        print("💿 シンプルDMG作成開始")
        print("=" * 50)
        
        steps = [
            ("一時ディレクトリ作成", self.create_temp_directory),
            ("DMG内容セットアップ", self.setup_dmg_contents),
            ("DMG作成", self.create_dmg_from_folder),
            ("DMG検証", self.verify_and_info_dmg),
        ]
        
        results = {}
        
        try:
            for step_name, step_func in steps:
                print(f"\\n{'='*15} {step_name} {'='*15}")
                
                try:
                    result = step_func()
                    results[step_name] = result
                    
                    if result:
                        print(f"✅ {step_name}: 成功")
                    else:
                        print(f"❌ {step_name}: 失敗")
                        break
                        
                except Exception as e:
                    print(f"❌ {step_name}: エラー - {e}")
                    results[step_name] = False
                    break
            
            # 最終結果
            print(f"\\n📊 シンプルDMG作成結果:")
            print("=" * 50)
            
            success_count = sum(results.values())
            total_count = len(results)
            
            for step_name, result in results.items():
                status = "✅ 成功" if result else "❌ 失敗"
                print(f"  {step_name:20}: {status}")
            
            print(f"\\n総合結果: {success_count}/{total_count} 成功")
            
            dmg_success = results.get("DMG検証", False)
            
            if dmg_success:
                print(f"🎉 シンプルDMG作成完了！")
                print(f"💿 配布用DMG: {self.dmg_filename}")
                
                print(f"\\n📖 使用方法:")
                print(f"  1. {self.dmg_filename} をダブルクリックしてマウント")
                print(f"  2. RVC Voice Converter.app を Applications フォルダにドラッグ")
                print(f"  3. アプリケーションフォルダから起動")
                print(f"  4. DMGをゴミ箱にドラッグして取り出し")
                
            else:
                print(f"❌ DMG作成に失敗しました")
            
            return {
                'success': dmg_success,
                'dmg_path': Path(self.dmg_filename) if dmg_success else None,
                'results': results
            }
            
        finally:
            # 必ずクリーンアップ
            self.cleanup()

def main():
    """メイン実行関数"""
    app_path = "optimized_apps/RVC Voice Converter.app"
    
    if not Path(app_path).exists():
        print(f"❌ アプリバンドルが見つかりません: {app_path}")
        return False
    
    creator = SimpleDMGCreator(app_path)
    result = creator.create_simple_dmg()
    
    return result['success']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)