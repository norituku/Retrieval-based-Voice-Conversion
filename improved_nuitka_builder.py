#!/usr/bin/env python3
"""
Improved Nuitka Builder
改良版Nuitkaビルダー（エラー修正版）
"""
import subprocess
import sys
import os
import shutil
import time
from pathlib import Path

class ImprovedNuitkaBuilder:
    """改良版Nuitkaビルダー"""
    
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
        
        # tkinterの確認（システムPython経由）
        tkinter_check = subprocess.run([
            "python3", "-c", "import tkinter; print('tkinter available')"
        ], capture_output=True, text=True)
        
        if tkinter_check.returncode != 0:
            print("❌ tkinterが利用できません")
            return False
        
        print("✅ tkinter確認済み")
        return True
    
    def install_missing_packages(self):
        """不足パッケージをインストール"""
        print("📦 不足パッケージをインストール中...")
        
        # 必要パッケージリスト
        packages = [
            "nuitka",
            "numpy",
            "torch",
            "torchaudio", 
            "soundfile",
            "scipy",
            "librosa",
            "faiss-cpu",
            "pyworld",
            "praat-parselmouth",
            "torchcrepe",
            "onnx",
            "onnxruntime"
        ]
        
        for package in packages:
            print(f"  ✓ {package}確認中...")
            result = subprocess.run([
                "poetry", "run", "python", "-c", f"import {package.replace('-', '_').replace('praat_', '')}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  📦 {package}インストール中...")
                subprocess.run(["poetry", "add", package], capture_output=True)
        
        print("✅ 全パッケージ確認完了")
    
    def build_complete_app(self):
        """完全版アプリビルド"""
        print("\n🔨 完全版アプリビルド開始...")
        
        # 出力ディレクトリ
        output_dir = self.project_root / f"dist_improved_{self.build_timestamp}"
        output_dir.mkdir(exist_ok=True)
        
        # アイコンパス
        icon_path = self.project_root / "app_icons" / "rvc_icon.icns"
        
        # Nuitkaコマンド構築（改良版）
        nuitka_cmd = [
            "poetry", "run", "python", "-m", "nuitka",
            
            # 基本設定
            "--standalone",
            "--macos-create-app-bundle",
            f"--output-dir={output_dir}",
            
            # アプリ情報
            "--macos-app-name=RVC Voice Converter Full",
            "--macos-app-version=1.0.0",
            "--company-name=RVC Project",
            "--product-name=RVC Voice Converter",
            "--file-description=Retrieval-based Voice Conversion Application",
            
            # アイコン設定
            f"--macos-app-icon={icon_path}" if icon_path.exists() else "--macos-app-icon=none",
            
            # プラグイン有効化（エラー修正版）
            "--plugin-enable=torch",
            # numpy プラグインは非推奨のため削除
            # tk-inter プラグインはエラーになるため削除
            # matplotlib、multiprocessingは自動有効化のため削除
            
            # 全インポートを追跡
            "--follow-imports",
            "--follow-import-to=enhanced_voice_converter", 
            "--follow-import-to=log_importance_analyzer",
            "--follow-import-to=rvc",
            
            # 特定モジュールを含む
            "--include-module=tkinter",
            "--include-module=numpy",
            "--include-module=torch",
            "--include-module=torchaudio",
            "--include-module=soundfile",
            "--include-module=scipy",
            "--include-module=librosa",
            "--include-module=enhanced_voice_converter",
            "--include-module=log_importance_analyzer",
            
            # パッケージを強制的に含む（主要なもののみ）
            "--include-package=numpy",
            "--include-package=torch",
            "--include-package=soundfile",
            "--include-package=scipy",
            "--include-package=librosa",
            
            # データファイル
            "--include-data-dir=model_dir=model_dir",
            "--include-data-dir=rvc=rvc",
            "--include-data-files=enhanced_voice_converter.py=enhanced_voice_converter.py",
            "--include-data-files=log_importance_analyzer.py=log_importance_analyzer.py",
            
            # 最適化設定
            "--assume-yes-for-downloads",
            "--remove-output",
            
            # ソースファイル
            "gui_dark_mode_enhanced_complete.py"
        ]
        
        print("🚀 Nuitkaビルド実行中...")
        print("  改良版設定でビルド実行...")
        
        # ビルド実行
        start_time = time.time()
        
        # プロセス実行（リアルタイム出力）
        process = subprocess.Popen(
            nuitka_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 出力を表示
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        elapsed_time = time.time() - start_time
        
        if process.returncode == 0:
            print(f"\n✅ ビルド成功！（{elapsed_time:.1f}秒）")
            
            # 生成されたアプリを探す
            app_path = None
            for item in output_dir.iterdir():
                if item.suffix == ".app":
                    app_path = item
                    break
            
            if app_path:
                print(f"📱 アプリケーション: {app_path}")
                
                # アプリ署名とDMG作成
                self.sign_and_package(app_path, output_dir)
                
                return app_path
            else:
                print("❌ .appファイルが見つかりません")
        else:
            print(f"\n❌ ビルド失敗（{elapsed_time:.1f}秒）")
        
        return None
    
    def sign_and_package(self, app_path, output_dir):
        """アプリ署名とDMG作成"""
        print("\n🔐 アプリ署名中...")
        
        # 簡易署名（開発用）
        sign_cmd = [
            "codesign", "--force", "--deep", "--sign", "-",
            str(app_path)
        ]
        
        try:
            result = subprocess.run(sign_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ アプリ署名完了")
            else:
                print(f"⚠️ アプリ署名失敗: {result.stderr}")
        except:
            print("⚠️ codesignコマンドが見つかりません")
        
        # DMG作成
        print("\n💿 DMGファイル作成中...")
        
        dmg_name = f"RVC_Voice_Converter_Full_{self.build_timestamp}.dmg"
        dmg_path = output_dir / dmg_name
        
        # 一時フォルダ作成
        temp_dir = output_dir / "dmg_temp"
        temp_dir.mkdir(exist_ok=True)
        
        # アプリをコピー
        shutil.copytree(app_path, temp_dir / app_path.name)
        
        # Applications シンボリックリンク作成
        try:
            os.symlink("/Applications", str(temp_dir / "Applications"))
        except:
            pass
        
        # DMG作成コマンド
        dmg_cmd = [
            "hdiutil", "create",
            "-volname", "RVC Voice Converter Full",
            "-srcfolder", str(temp_dir),
            "-ov",
            "-format", "UDZO",
            str(dmg_path)
        ]
        
        try:
            result = subprocess.run(dmg_cmd, capture_output=True, text=True)
            
            # 一時フォルダ削除
            shutil.rmtree(temp_dir)
            
            if result.returncode == 0:
                print(f"✅ DMG作成完了: {dmg_path}")
                return dmg_path
            else:
                print(f"❌ DMG作成失敗: {result.stderr}")
        except Exception as e:
            print(f"❌ DMG作成エラー: {e}")
        
        return None
    
    def run(self):
        """ビルド実行"""
        print("🏗️ 改良版Nuitka全依存関係ビルド")
        print("=" * 50)
        
        # 環境チェック
        if not self.check_environment():
            return False
        
        # パッケージインストール
        self.install_missing_packages()
        
        # ビルド実行
        app_path = self.build_complete_app()
        
        if app_path:
            print("\n" + "="*50)
            print("✅ ビルド完了！")
            print(f"\n📱 アプリケーション:")
            print(f"   {app_path}")
            print(f"\n🚀 実行方法:")
            print(f"   open '{app_path}'")
            print("\n🎯 目標達成:")
            print("   このアプリは全ての依存関係を含んでいるため、")
            print("   異なる環境のMacでもPython環境なしで動作します。")
            return True
        else:
            print("\n❌ ビルド失敗")
            return False

if __name__ == "__main__":
    builder = ImprovedNuitkaBuilder()
    success = builder.run()
    sys.exit(0 if success else 1)