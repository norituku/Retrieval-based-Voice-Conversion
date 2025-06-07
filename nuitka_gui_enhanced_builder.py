#!/usr/bin/env python3
"""
GUI Dark Mode Enhanced 専用 Nuitka ビルダー
gui_dark_mode_enhanced.pyの全機能を保持したmacOSアプリを作成
"""
import subprocess
import sys
import os
import shutil
import time
from pathlib import Path

class GuiEnhancedNuitkaBuilder:
    """GUI Enhanced専用Nuitkaビルダー"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        
        # Poetry環境の使用を優先
        self.use_poetry = True
        try:
            # Poetry環境確認
            result = subprocess.run(['poetry', 'env', 'info', '--path'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                poetry_env_path = result.stdout.strip()
                self.poetry_python = f"{poetry_env_path}/bin/python"
                if Path(self.poetry_python).exists():
                    print(f"🎯 Poetry環境Python発見: {self.poetry_python}")
                    self.system_python = self.poetry_python
                else:
                    raise FileNotFoundError("Poetry Python not found")
            else:
                raise RuntimeError("Poetry env info failed")
        except:
            print("⚠️ Poetry環境が利用できません。システムPythonにフォールバック")
            self.use_poetry = False
            self.system_python = self.find_system_python()
            if not self.system_python:
                raise RuntimeError("システムPython（tkinter対応）が見つかりません")
        
        print(f"🐍 使用するPython: {self.system_python}")
        print(f"📦 Poetry環境使用: {self.use_poetry}")
    
    def find_system_python(self):
        """システムPython（tkinter対応）を検出"""
        candidates = [
            "/opt/homebrew/bin/python3",
            "/usr/bin/python3",
            "/usr/local/bin/python3",
            "/opt/local/bin/python3"
        ]
        
        for python_path in candidates:
            if Path(python_path).exists():
                try:
                    # tkinter対応確認
                    result = subprocess.run([
                        python_path, "-c", 
                        "import tkinter; import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ tkinter対応Python発見: {python_path}")
                        print(f"   バージョン: {result.stdout.strip()}")
                        return python_path
                except:
                    continue
        
        return None
    
    def prepare_build_environment(self):
        """ビルド環境準備"""
        print("🔧 Nuitkaビルド環境準備中...")
        
        # 1. 必要な依存関係確認
        self.check_dependencies()
        
        # 2. リソースファイル準備
        self.prepare_resources()
        
        # 3. Nuitka互換版ファイルの確認
        self.verify_nuitka_version()
    
    def check_dependencies(self):
        """依存関係の確認とインストール"""
        print("📦 依存関係確認中...")
        
        if self.use_poetry:
            # Poetry環境でのNuitka確認とインストール
            try:
                result = subprocess.run([
                    "poetry", "run", "python", "-c", "import nuitka; print('OK')"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print("📦 Poetry環境にNuitkaインストール中...")
                    install_result = subprocess.run([
                        "poetry", "add", "--group", "dev", "nuitka"
                    ], capture_output=True, text=True)
                    
                    if install_result.returncode != 0:
                        print(f"⚠️ Poetry add失敗、pip経由でインストール...")
                        install_result = subprocess.run([
                            "poetry", "run", "pip", "install", "nuitka"
                        ], capture_output=True, text=True)
                        
                        if install_result.returncode != 0:
                            raise RuntimeError(f"Nuitkaインストール失敗: {install_result.stderr}")
                    
                    print("✅ Nuitka Poetry環境インストール完了")
                else:
                    print("✅ Nuitka既にPoetry環境にインストール済み")
            except Exception as e:
                raise RuntimeError(f"Poetry Nuitka確認エラー: {e}")
        else:
            # システムPython環境でのNuitka確認
            try:
                result = subprocess.run([
                    self.system_python, "-c", "import nuitka; print('OK')"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print("📦 システムPythonにNuitkaインストール中...")
                    install_result = subprocess.run([
                        self.system_python, "-m", "pip", "install", "nuitka", "--break-system-packages"
                    ], capture_output=True, text=True)
                    
                    if install_result.returncode != 0:
                        raise RuntimeError(f"Nuitkaインストール失敗: {install_result.stderr}")
                    else:
                        print("✅ Nuitkaシステム環境インストール完了")
                else:
                    print("✅ Nuitka既にシステム環境にインストール済み")
            except Exception as e:
                raise RuntimeError(f"システムNuitka確認エラー: {e}")
        
        # 必要なPythonパッケージ確認
        required_packages = [
            "numpy", "torch", "soundfile", "librosa", "scipy"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                if self.use_poetry:
                    result = subprocess.run([
                        "poetry", "run", "python", "-c", f"import {package}; print('OK')"
                    ], capture_output=True, text=True)
                else:
                    result = subprocess.run([
                        self.system_python, "-c", f"import {package}; print('OK')"
                    ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    env_type = "Poetry環境" if self.use_poetry else "システム環境"
                    print(f"✅ {package}: {env_type}で利用可能")
                else:
                    missing_packages.append(package)
            except:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️ 不足パッケージ: {missing_packages}")
            if self.use_poetry:
                print("💡 poetry install を実行してください")
            else:
                print("💡 pip install で不足パッケージをインストールしてください")
    
    def prepare_resources(self):
        """リソースファイル準備"""
        print("📁 リソースファイル準備中...")
        
        # 必要なディレクトリとファイル
        required_items = [
            "model_dir",
            "enhanced_output", 
            "configs",
            "enhanced_voice_converter.py",
            "rvc/",
            "pyproject.toml",
            "poetry.lock"
        ]
        
        for item in required_items:
            item_path = self.project_root / item
            if item_path.exists():
                print(f"✅ {item}: 存在確認")
            else:
                print(f"⚠️ {item}: 見つかりません（ビルド時に警告される可能性）")
    
    def verify_nuitka_version(self):
        """Nuitka互換版ファイルの確認"""
        nuitka_file = self.project_root / "gui_dark_mode_enhanced_nuitka.py"
        if not nuitka_file.exists():
            raise RuntimeError(f"Nuitka互換版ファイルが見つかりません: {nuitka_file}")
        
        print(f"✅ Nuitka互換版ファイル確認: {nuitka_file}")
    
    def build_with_nuitka(self):
        """最適化Nuitkaビルド実行"""
        print("🚀 GUI Enhanced Nuitkaビルド開始...")
        
        # 出力ディレクトリ準備
        output_dir = self.project_root / "dist_gui_enhanced_nuitka"
        if output_dir.exists():
            print(f"🗑️ 既存ビルドディレクトリを削除: {output_dir}")
            shutil.rmtree(output_dir)
        output_dir.mkdir()
        
        # Nuitkaコマンド構築（最適化設定）
        if self.use_poetry:
            nuitka_cmd = [
                "poetry", "run", "python", "-m", "nuitka",
            
            # === 基本設定 ===
            "--standalone",
            "--macos-create-app-bundle",
            f"--output-dir={output_dir}",
            
            # === アプリケーション情報 ===
            "--macos-app-name=RVC Voice Converter Enhanced",
            "--macos-app-version=2.0.0",
            "--macos-app-protected-resource=microphone:RVC音声変換のためマイクアクセス",
            
            # === リソースデータの包含 ===
            "--include-data-dir=model_dir=model_dir",
            "--include-data-dir=enhanced_output=enhanced_output", 
            "--include-data-dir=configs=configs",
            "--include-data-files=enhanced_voice_converter.py=enhanced_voice_converter.py",
            "--include-data-files=pyproject.toml=pyproject.toml",
            "--include-data-files=poetry.lock=poetry.lock",
            
            # === Pythonモジュールの強制包含 ===
            "--include-module=enhanced_voice_converter",
            "--include-package=rvc",
            
            # === システムライブラリ（条件付き） ===
            "--include-package=tkinter",
            "--include-package=numpy",
            "--include-package=torch",
            "--include-package=soundfile",
            "--include-package=librosa",
            "--include-package=scipy",
            "--include-package=sklearn",
            
            # === 最適化設定 ===
            "--lto=yes",  # Link Time Optimization
            "--jobs=4",   # 並列ビルド
            
            # === macOS固有設定 ===
            "--macos-target-arch=arm64",  # Apple Siliconに最適化
            
            # === 除外設定（サイズ削減） ===
            "--nofollow-import-to=pytest",
            "--nofollow-import-to=setuptools", 
            "--nofollow-import-to=distutils",
            "--nofollow-import-to=test",
            "--nofollow-import-to=tests",
            
            # === エラー回避 ===
            "--assume-yes-for-downloads",
            "--remove-output",
            
            # === 対象ファイル ===
            "gui_dark_mode_enhanced_nuitka.py"
        ]
        
        print(f"📝 Nuitkaビルドコマンド実行中...")
        print("   コマンドプレビュー:")
        print(f"   {' '.join(nuitka_cmd[:5])} ... [全{len(nuitka_cmd)}オプション]")
        
        # ビルド実行
        start_time = time.time()
        try:
            result = subprocess.run(nuitka_cmd, capture_output=True, text=True, timeout=1800)  # 30分タイムアウト
        except subprocess.TimeoutExpired:
            print("❌ Nuitkaビルドがタイムアウトしました（30分）")
            return None
        
        end_time = time.time()
        build_time = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ Nuitkaビルド成功! (実行時間: {build_time:.1f}秒)")
            
            # 生成されたアプリの確認と最適化
            app_path = output_dir / "gui_dark_mode_enhanced_nuitka.app"
            if app_path.exists():
                # アプリ名を分かりやすく変更
                final_app_path = output_dir / "RVC Voice Converter Enhanced.app"
                if final_app_path.exists():
                    shutil.rmtree(final_app_path)
                shutil.move(str(app_path), str(final_app_path))
                
                # アプリ情報表示
                size_mb = self.get_directory_size(final_app_path) / 1024**2
                print(f"📱 アプリ生成完了: {final_app_path}")
                print(f"📏 アプリサイズ: {size_mb:.1f}MB")
                
                # 権限設定
                self.set_app_permissions(final_app_path)
                
                return final_app_path
            else:
                print("❌ アプリバンドルが見つかりません")
                print("STDOUT:", result.stdout[-1000:] if result.stdout else "なし")
                return None
        else:
            print(f"❌ Nuitkaビルド失敗 (実行時間: {build_time:.1f}秒):")
            print("=== STDOUT ===")
            print(result.stdout[-2000:] if result.stdout else "なし")
            print("\n=== STDERR ===") 
            print(result.stderr[-2000:] if result.stderr else "なし")
            return None
    
    def get_directory_size(self, path):
        """ディレクトリサイズ計算"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                try:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
        return total_size
    
    def set_app_permissions(self, app_path):
        """アプリ権限設定"""
        print("🔐 アプリ権限設定中...")
        try:
            # 実行権限設定
            macos_binary = app_path / "Contents" / "MacOS" / "gui_dark_mode_enhanced_nuitka"
            if macos_binary.exists():
                os.chmod(macos_binary, 0o755)
                print("✅ 実行権限設定完了")
            
            # Info.plistの確認
            info_plist = app_path / "Contents" / "Info.plist"
            if info_plist.exists():
                print("✅ Info.plist確認完了")
            else:
                print("⚠️ Info.plistが見つかりません")
                
        except Exception as e:
            print(f"⚠️ 権限設定エラー: {e}")
    
    def create_dmg(self, app_path):
        """DMGファイル作成（オプション）"""
        if not app_path or not app_path.exists():
            print("❌ アプリが存在しないためDMG作成をスキップ")
            return None
        
        print("📦 DMGファイル作成中...")
        dmg_name = "RVC_Voice_Converter_Enhanced.dmg"
        dmg_path = self.project_root / dmg_name
        
        # 既存DMG削除
        if dmg_path.exists():
            dmg_path.unlink()
        
        try:
            # hdiutil でDMG作成
            cmd = [
                "hdiutil", "create",
                "-volname", "RVC Voice Converter Enhanced",
                "-srcfolder", str(app_path),
                "-ov", "-format", "UDZO",
                str(dmg_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                dmg_size = dmg_path.stat().st_size / 1024**2
                print(f"✅ DMG作成完了: {dmg_path} ({dmg_size:.1f}MB)")
                return dmg_path
            else:
                print(f"❌ DMG作成失敗: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ DMG作成エラー: {e}")
            return None
    
    def test_app(self, app_path):
        """ビルドしたアプリの起動テスト"""
        if not app_path or not app_path.exists():
            print("❌ テスト対象アプリが見つかりません")
            return False
        
        print("🧪 アプリ起動テスト中...")
        try:
            # アプリ起動テスト（5秒で終了）
            test_result = subprocess.run([
                "timeout", "5", "open", str(app_path)
            ], capture_output=True, text=True)
            
            if test_result.returncode in [0, 124]:  # 0=成功, 124=timeout
                print("✅ アプリ起動テスト成功")
                return True
            else:
                print(f"❌ アプリ起動テスト失敗: {test_result.stderr}")
                return False
        except Exception as e:
            print(f"❌ アプリテストエラー: {e}")
            return False

def main():
    """メイン実行"""
    print("🎤 GUI Dark Mode Enhanced - Nuitka ビルダー")
    print("=" * 60)
    
    try:
        builder = GuiEnhancedNuitkaBuilder()
        
        # フェーズ1: 環境準備
        print("\n📋 フェーズ1: 環境準備")
        builder.prepare_build_environment()
        
        # フェーズ2: Nuitkaビルド
        print("\n🏗️ フェーズ2: Nuitkaビルド")
        app_path = builder.build_with_nuitka()
        
        if not app_path:
            print("\n❌ ビルド失敗")
            sys.exit(1)
        
        # フェーズ3: アプリテスト
        print("\n🧪 フェーズ3: アプリテスト")
        test_success = builder.test_app(app_path)
        
        # フェーズ4: DMG作成（オプション）
        if test_success:
            print("\n📦 フェーズ4: DMG作成")
            dmg_path = builder.create_dmg(app_path)
        
        # 完了報告
        print("\n" + "=" * 60)
        print("🎉 ビルド完了!")
        print(f"📱 アプリケーション: {app_path}")
        if 'dmg_path' in locals() and dmg_path:
            print(f"📦 DMGファイル: {dmg_path}")
        print(f"🚀 起動コマンド: open '{app_path}'")
        print("\n💡 使用方法:")
        print("   1. アプリをダブルクリックで起動")
        print("   2. model_dirにRVCモデル(.pth)を配置")
        print("   3. 音声ファイルを選択して変換実行")
        
    except Exception as e:
        print(f"\n❌ ビルドエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()