#!/usr/bin/env python3
"""
Nuitka Full Bundle Builder
Nuitkaで全依存関係をバンドルするビルダー
"""
import subprocess
import sys
import os
import shutil
import time
from pathlib import Path

class NuitkaFullBundleBuilder:
    """Nuitka全依存関係バンドルビルダー"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.build_timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    def check_environment(self):
        """環境チェック"""
        print("🔍 環境チェック中...")
        
        # Poetry環境の確認
        poetry_check = subprocess.run(["poetry", "env", "info"], capture_output=True, text=True)
        if poetry_check.returncode != 0:
            print("❌ Poetry環境が見つかりません")
            return False
        
        print("✅ Poetry環境確認済み")
        
        # 必要なパッケージの確認
        required_packages = ["nuitka", "numpy", "torch", "enhanced_voice_converter"]
        missing = []
        
        for package in required_packages:
            result = subprocess.run([
                "poetry", "run", "python", "-c", f"import {package.replace('-', '_')}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                missing.append(package)
        
        if missing:
            print(f"❌ 不足パッケージ: {', '.join(missing)}")
            print("  poetry install を実行してください")
            return False
        
        print("✅ 必要パッケージ確認済み")
        return True
    
    def install_nuitka_in_poetry(self):
        """Poetry環境にNuitkaをインストール"""
        print("📦 NuitkaをPoetry環境にインストール中...")
        
        result = subprocess.run([
            "poetry", "add", "nuitka", "--group", "dev"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Nuitkaインストール完了")
            return True
        else:
            print("❌ Nuitkaインストール失敗")
            return False
    
    def build_complete_app(self):
        """完全版アプリをビルド"""
        print("\n🔨 完全版アプリビルド開始...")
        
        # 出力ディレクトリ
        output_dir = self.project_root / f"dist_complete_{self.build_timestamp}"
        output_dir.mkdir(exist_ok=True)
        
        # Nuitkaコマンド構築（Poetry環境で実行）
        nuitka_cmd = [
            "poetry", "run", "python", "-m", "nuitka",
            
            # 基本設定
            "--standalone",
            "--onefile",  # 単一実行ファイル
            "--macos-create-app-bundle",
            f"--output-dir={output_dir}",
            
            # アプリ情報
            "--macos-app-name=RVC Voice Converter",
            "--macos-app-version=1.0.0",
            "--company-name=RVC Project",
            "--product-name=RVC Voice Converter",
            "--file-description=Retrieval-based Voice Conversion Application",
            
            # プラグイン有効化
            "--plugin-enable=numpy",
            "--plugin-enable=torch",
            "--plugin-enable=tk-inter",
            "--plugin-enable=matplotlib",
            "--plugin-enable=multiprocessing",
            
            # 全インポートを追跡
            "--follow-imports",
            "--follow-import-to=enhanced_voice_converter",
            "--follow-import-to=log_importance_analyzer",
            "--follow-import-to=rvc",
            
            # パッケージを強制的に含む
            "--include-package=tkinter",
            "--include-package=numpy",
            "--include-package=torch",
            "--include-package=torchaudio",
            "--include-package=soundfile",
            "--include-package=scipy",
            "--include-package=librosa",
            "--include-package=faiss",
            "--include-package=pyworld",
            "--include-package=parselmouth",
            "--include-package=torchcrepe",
            "--include-package=onnx",
            "--include-package=onnxruntime",
            
            # データファイル
            "--include-data-dir=model_dir=model_dir",
            "--include-data-dir=rvc=rvc",
            "--include-data-files=pyproject.toml=pyproject.toml",
            
            # 最適化設定
            "--assume-yes-for-downloads",
            "--remove-output",
            "--quiet",
            "--no-progressbar",
            
            # ソースファイル
            "gui_dark_mode_enhanced_complete.py"
        ]
        
        print("🚀 Nuitkaビルド実行中...")
        print("  これには10-30分かかる場合があります...")
        
        # ビルド実行
        start_time = time.time()
        result = subprocess.run(nuitka_cmd)
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ ビルド成功！（{elapsed_time:.1f}秒）")
            
            # 生成されたアプリを探す
            app_path = None
            for item in output_dir.iterdir():
                if item.suffix == ".app":
                    app_path = item
                    break
            
            if app_path:
                print(f"📱 アプリケーション: {app_path}")
                
                # アイコン設定
                self.set_app_icon(app_path)
                
                # DMG作成
                self.create_dmg(app_path, output_dir)
                
                return app_path
            else:
                print("❌ .appファイルが見つかりません")
        else:
            print(f"\n❌ ビルド失敗（{elapsed_time:.1f}秒）")
            print("  ログを確認してください")
        
        return None
    
    def set_app_icon(self, app_path):
        """アプリアイコンを設定"""
        icon_path = self.project_root / "app_icons" / "rvc_icon.icns"
        if icon_path.exists():
            resources_dir = app_path / "Contents" / "Resources"
            if resources_dir.exists():
                shutil.copy(icon_path, resources_dir / "rvc_icon.icns")
                
                # Info.plist更新
                info_plist = app_path / "Contents" / "Info.plist"
                if info_plist.exists():
                    content = info_plist.read_text()
                    content = content.replace(
                        "<key>CFBundleIconFile</key>\n\t<string></string>",
                        "<key>CFBundleIconFile</key>\n\t<string>rvc_icon</string>"
                    )
                    info_plist.write_text(content)
                    print("✅ アイコン設定完了")
    
    def create_dmg(self, app_path, output_dir):
        """DMGファイル作成"""
        print("\n💿 DMGファイル作成中...")
        
        dmg_name = f"RVC_Voice_Converter_{self.build_timestamp}.dmg"
        dmg_path = output_dir / dmg_name
        
        # 一時フォルダ作成
        temp_dir = output_dir / "dmg_temp"
        temp_dir.mkdir(exist_ok=True)
        
        # アプリをコピー
        shutil.copytree(app_path, temp_dir / app_path.name)
        
        # Applications シンボリックリンク作成
        os.symlink("/Applications", str(temp_dir / "Applications"))
        
        # DMG作成コマンド
        dmg_cmd = [
            "hdiutil", "create",
            "-volname", "RVC Voice Converter",
            "-srcfolder", str(temp_dir),
            "-ov",
            "-format", "UDZO",
            str(dmg_path)
        ]
        
        result = subprocess.run(dmg_cmd, capture_output=True, text=True)
        
        # 一時フォルダ削除
        shutil.rmtree(temp_dir)
        
        if result.returncode == 0:
            print(f"✅ DMG作成完了: {dmg_path}")
            return dmg_path
        else:
            print(f"❌ DMG作成失敗: {result.stderr}")
            return None
    
    def run(self):
        """ビルド実行"""
        print("🏗️ Nuitka全依存関係バンドルビルド")
        print("=" * 50)
        
        # 環境チェック
        if not self.check_environment():
            return False
        
        # Nuitkaインストール確認
        nuitka_check = subprocess.run([
            "poetry", "run", "python", "-c", "import nuitka"
        ], capture_output=True, text=True)
        
        if nuitka_check.returncode != 0:
            if not self.install_nuitka_in_poetry():
                return False
        
        # ビルド実行
        app_path = self.build_complete_app()
        
        if app_path:
            print("\n" + "="*50)
            print("✅ ビルド完了！")
            print(f"\n📱 アプリケーション:")
            print(f"   {app_path}")
            print(f"\n🚀 実行方法:")
            print(f"   open '{app_path}'")
            print("\n📦 このアプリは全ての依存関係を含んでいるため、")
            print("   他のMacでもPython環境なしで動作します。")
            return True
        else:
            print("\n❌ ビルド失敗")
            return False

if __name__ == "__main__":
    builder = NuitkaFullBundleBuilder()
    success = builder.run()
    sys.exit(0 if success else 1)