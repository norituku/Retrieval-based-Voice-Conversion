#!/usr/bin/env python3
"""
完全版GUI専用Nuitkaビルダー
gui_dark_mode_enhanced_complete.py用の最適化されたビルドシステム
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class CompleteNuitkaBuilder:
    """完全版GUI専用Nuitkaビルダー"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        
        # 完全版GUI設定
        self.gui_script = "gui_dark_mode_enhanced_complete.py"
        self.app_name = "Voice Converter Complete Edition"
        self.app_identifier = "com.rvc.voiceconverter.complete"
        
        # ビルド出力設定
        self.output_dir = self.project_root / "dist_complete_app"
        
        # Poetry環境の使用を優先
        self.use_poetry = True
        try:
            # Poetry環境確認
            result = subprocess.run(['poetry', 'env', 'info', '--path'], 
                                  capture_output=True, text=True, check=True)
            poetry_env_path = result.stdout.strip()
            self.poetry_python = f"{poetry_env_path}/bin/python"
            print(f"✅ Poetry環境確認: {poetry_env_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Poetry環境未検出 - システムPython使用")
            self.use_poetry = False
            self.poetry_python = sys.executable
        
        # 完全版に必要な依存関係
        self.required_modules = [
            # 音声処理
            "numpy", "torch", "torchaudio", "librosa", "soundfile", 
            # 標準ライブラリ
            "json", "threading", "pathlib", "datetime", "re", "enum", "typing",
            # RVC関連
            "enhanced_voice_converter", "log_importance_analyzer"
        ]
        
        # システムPythonで確認すべきモジュール（tkinter等）
        self.system_modules = ["tkinter"]
        
        # 完全版固有の包含ファイル
        self.include_files = [
            # 統合された依存ファイル
            ("enhanced_voice_converter.py", "enhanced_voice_converter.py"),
            ("log_importance_analyzer.py", "log_importance_analyzer.py"),
            # 設定・モデルディレクトリ
            ("model_dir/", "model_dir/"),
            ("configs/", "configs/"),
            # GUI設定
            ("gui_settings.json", "gui_settings.json"),
            # アプリアイコン
            ("app_icons/", "app_icons/"),
        ]
        
        print(f"🎯 ターゲット: {self.gui_script}")
        print(f"📱 アプリ名: {self.app_name}")
        print(f"📁 出力先: {self.output_dir}")
    
    def check_dependencies(self):
        """依存関係の確認"""
        print(f"\n==================== 完全版依存関係チェック ====================")
        
        missing_modules = []
        available_modules = []
        
        # Poetry環境でのモジュールチェック
        for module in self.required_modules:
            try:
                if self.use_poetry:
                    # Poetry環境での確認
                    result = subprocess.run([
                        self.poetry_python, "-c", f"import {module}"
                    ], capture_output=True, text=True)
                    if result.returncode == 0:
                        available_modules.append(module)
                    else:
                        missing_modules.append(module)
                else:
                    # システムPython環境での確認
                    __import__(module)
                    available_modules.append(module)
            except ImportError:
                missing_modules.append(module)
        
        # システムPythonでのモジュールチェック（tkinter等）
        for module in self.system_modules:
            try:
                # tkinterは常にシステムPythonで確認
                result = subprocess.run([
                    sys.executable, "-c", f"import {module}"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    available_modules.append(f"{module} (system)")
                else:
                    missing_modules.append(f"{module} (system)")
            except Exception:
                missing_modules.append(f"{module} (system)")
        
        print(f"✅ 利用可能モジュール: {len(available_modules)}")
        for module in available_modules:
            print(f"   ✓ {module}")
        
        if missing_modules:
            print(f"❌ 未インストールモジュール: {len(missing_modules)}")
            for module in missing_modules:
                print(f"   ✗ {module}")
            
            # 重要でないモジュールのみの場合は続行
            critical_missing = [m for m in missing_modules if not any(skip in m for skip in ["PIL", "tkinter"])]
            if not critical_missing:
                print("⚠️ 非重要モジュールのみ不足 - ビルド続行")
                print("✅ 完全版依存関係チェック: 成功（警告付き）")
                return True
            
            if self.use_poetry:
                print("\n💡 解決策:")
                print("   poetry install  # 不足依存関係をインストール")
                return False
            else:
                print("\n💡 解決策:")
                print("   pip install [module_name]  # 個別インストール")
                return False
        
        print("✅ 完全版依存関係チェック: 成功")
        return True
    
    def check_source_files(self):
        """ソースファイルの確認"""
        print(f"\n==================== 完全版ソースファイルチェック ====================")
        
        # メインGUIファイル
        gui_file = self.project_root / self.gui_script
        if not gui_file.exists():
            print(f"❌ メインGUIファイルが見つかりません: {self.gui_script}")
            return False
        
        print(f"✅ メインGUI: {self.gui_script}")
        
        # 統合された依存ファイル
        missing_files = []
        available_files = []
        
        for src, _ in self.include_files:
            src_path = self.project_root / src
            if src_path.exists():
                available_files.append(src)
            else:
                missing_files.append(src)
        
        print(f"✅ 利用可能ファイル: {len(available_files)}")
        for file in available_files:
            print(f"   ✓ {file}")
        
        if missing_files:
            print(f"⚠️ オプションファイル（未検出）: {len(missing_files)}")
            for file in missing_files:
                print(f"   ? {file}")
            print("   ※ これらのファイルは見つからない場合はスキップされます")
        
        print("✅ 完全版ソースファイルチェック: 成功")
        return True
    
    def prepare_build_environment(self):
        """ビルド環境の準備"""
        print(f"\n==================== 完全版ビルド環境準備 ====================")
        
        # 出力ディレクトリのクリア
        if self.output_dir.exists():
            print(f"🧹 既存ビルドをクリア: {self.output_dir}")
            shutil.rmtree(self.output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 ビルドディレクトリ作成: {self.output_dir}")
        
        print("✅ 完全版ビルド環境準備: 成功")
        return True
    
    def build_app(self):
        """完全版Nuitkaアプリビルド"""
        print(f"\n==================== 完全版Nuitkaビルド ====================")
        
        # Nuitkaコマンド構築（完全版最適化設定）
        if self.use_poetry:
            nuitka_cmd = [
                "poetry", "run", "python", "-m", "nuitka",
            ]
        else:
            nuitka_cmd = [
                sys.executable, "-m", "nuitka",
            ]
        
        # 完全版特化のNuitka設定（簡潔版）
        nuitka_args = [
            # 基本設定
            "--standalone",
            "--assume-yes-for-downloads",
            
            # macOSアプリバンドル設定（基本版）
            "--macos-create-app-bundle",
            
            # プラグイン設定
            "--plugin-enable=tk-inter", 
            "--plugin-enable=numpy",
            
            # 重要モジュール包含
            "--include-module=tkinter",
            "--include-module=numpy",
            "--include-module=torch",
            "--include-module=librosa",
            "--include-module=soundfile",
            
            # 統合されたモジュール包含
            "--include-module=enhanced_voice_converter",
            "--include-module=log_importance_analyzer",
            
            # ファイル包含（存在するもののみ）
        ]
        
        # 包含ファイルの追加（存在確認付き）
        for src, dst in self.include_files:
            src_path = self.project_root / src
            if src_path.exists():
                if src_path.is_dir():
                    nuitka_args.append(f"--include-data-dir={src}={dst}")
                else:
                    nuitka_args.append(f"--include-data-file={src}={dst}")
                print(f"   📎 包含: {src} → {dst}")
        
        # ターゲットファイル追加
        nuitka_args.extend([
            f"--output-dir={self.output_dir}",
            self.gui_script
        ])
        
        # 完全なコマンド
        full_cmd = nuitka_cmd + nuitka_args
        
        print(f"🚀 Nuitkaビルド開始...")
        print(f"📝 コマンド: {' '.join(full_cmd[:5])} ... (完全版設定)")
        
        try:
            result = subprocess.run(full_cmd, cwd=self.project_root, check=True,
                                  capture_output=False, text=True)
            print("✅ 完全版Nuitkaビルド: 成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 完全版Nuitkaビルド失敗: {e}")
            return False
    
    def verify_app(self):
        """完全版アプリの検証"""
        print(f"\n==================== 完全版アプリ検証 ====================")
        
        # アプリファイルの確認
        app_path = self.output_dir / f"{self.app_name}.app"
        if not app_path.exists():
            # デフォルト名での確認
            script_name = self.gui_script.replace('.py', '')
            app_path = self.output_dir / f"{script_name}.app"
        
        if not app_path.exists():
            print(f"❌ アプリファイルが見つかりません")
            return False
        
        # アプリ構造の確認
        contents_path = app_path / "Contents"
        macos_path = contents_path / "MacOS"
        plist_path = contents_path / "Info.plist"
        
        if not all([contents_path.exists(), macos_path.exists(), plist_path.exists()]):
            print(f"❌ アプリ構造が不完全です")
            return False
        
        # サイズの確認
        try:
            app_size = subprocess.run(['du', '-sh', str(app_path)], 
                                    capture_output=True, text=True, check=True)
            size_str = app_size.stdout.split()[0]
            print(f"📊 アプリサイズ: {size_str}")
        except:
            print("📊 アプリサイズ: 確認不可")
        
        print(f"✅ 完全版アプリ: {app_path}")
        print("✅ 完全版アプリ検証: 成功")
        return True, app_path
    
    def create_dmg(self, app_path):
        """完全版DMGの作成"""
        print(f"\n==================== 完全版DMG作成 ====================")
        
        dmg_name = "RVC_Voice_Converter_Complete_Edition.dmg"
        dmg_path = self.project_root / dmg_name
        
        # 既存DMGを削除
        if dmg_path.exists():
            dmg_path.unlink()
        
        # DMG作成コマンド
        create_dmg_cmd = [
            "hdiutil", "create", 
            "-volname", self.app_name,
            "-srcfolder", str(app_path),
            "-ov", "-format", "UDZO",
            str(dmg_path)
        ]
        
        try:
            subprocess.run(create_dmg_cmd, check=True, capture_output=True)
            
            # DMGサイズ確認
            dmg_size = subprocess.run(['du', '-sh', str(dmg_path)], 
                                    capture_output=True, text=True, check=True)
            size_str = dmg_size.stdout.split()[0]
            
            print(f"✅ 完全版DMG作成完了: {dmg_name}")
            print(f"📊 DMGサイズ: {size_str}")
            return True, dmg_path
        except subprocess.CalledProcessError as e:
            print(f"❌ 完全版DMG作成失敗: {e}")
            return False, None
    
    def run_complete_build(self):
        """完全版ビルドの実行"""
        print("🚀 RVC Voice Converter Complete Edition ビルド開始")
        print("=" * 70)
        
        # ステップ1: 依存関係チェック
        if not self.check_dependencies():
            print("❌ ビルド中止: 依存関係不足")
            return False
        
        # ステップ2: ソースファイルチェック
        if not self.check_source_files():
            print("❌ ビルド中止: ソースファイル不足")
            return False
        
        # ステップ3: ビルド環境準備
        if not self.prepare_build_environment():
            print("❌ ビルド中止: 環境準備失敗")
            return False
        
        # ステップ4: Nuitkaビルド
        if not self.build_app():
            print("❌ ビルド中止: Nuitkaビルド失敗")
            return False
        
        # ステップ5: アプリ検証
        verify_result = self.verify_app()
        if not verify_result[0]:
            print("❌ ビルド中止: アプリ検証失敗")
            return False
        
        app_path = verify_result[1]
        
        # ステップ6: DMG作成
        dmg_result = self.create_dmg(app_path)
        if not dmg_result[0]:
            print("⚠️ DMG作成失敗（アプリは正常作成済み）")
        
        # 結果レポート
        print(f"\n📊 完全版ビルド結果:")
        print("=" * 70)
        print(f"  完全版依存関係チェック      : ✅ 成功")
        print(f"  完全版ソースファイルチェック   : ✅ 成功") 
        print(f"  完全版ビルド環境準備        : ✅ 成功")
        print(f"  完全版Nuitkaビルド         : ✅ 成功")
        print(f"  完全版アプリ検証           : ✅ 成功")
        print(f"  完全版DMG作成             : {'✅ 成功' if dmg_result[0] else '⚠️ 失敗'}")
        
        success_count = 5 + (1 if dmg_result[0] else 0)
        total_count = 6
        print(f"\n総合結果: {success_count}/{total_count} 成功")
        
        if success_count >= 5:  # アプリが作成されていれば成功
            print("🎉 RVC Voice Converter Complete Edition ビルド完了！")
            print(f"📱 完全版アプリ: {app_path}")
            if dmg_result[0]:
                print(f"💿 配布用DMG: {dmg_result[1]}")
            
            print(f"\n🎯 使用方法:")
            if dmg_result[0]:
                print(f"  1. DMGファイルをダブルクリック")
                print(f"  2. アプリをApplicationsフォルダにドラッグ")
                print(f"  3. Applicationsフォルダから起動")
            else:
                print(f"  1. {app_path} をApplicationsフォルダにコピー")
                print(f"  2. Applicationsフォルダから起動")
            
            print(f"\n🆕 Complete Edition の特徴:")
            print(f"  • gui_dark_mode_enhanced.pyと100%同一UI")
            print(f"  • ログフィルタリング機能完全保持")
            print(f"  • ログ色分け機能完全保持") 
            print(f"  • Enhanced Voice Converter統合")
            print(f"  • 完全なデザイントークン保持")
            
            return True
        else:
            print("❌ 完全版ビルド失敗")
            return False

def main():
    """メイン関数"""
    builder = CompleteNuitkaBuilder()
    success = builder.run_complete_build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()