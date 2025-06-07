#!/usr/bin/env python3
"""
Full Dependency RVC Builder
全依存関係を含むRVCビルダー
"""
import subprocess
import sys
import os
import shutil
import time
import json
from pathlib import Path

class FullDependencyBuilder:
    """全依存関係内包型ビルダー"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.poetry_python = self.find_poetry_python()
        self.system_python = self.find_system_python()
        
    def find_poetry_python(self):
        """Poetry環境のPythonを検出"""
        try:
            result = subprocess.run([
                "poetry", "run", "which", "python"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                poetry_python = result.stdout.strip()
                print(f"✅ Poetry Python発見: {poetry_python}")
                return poetry_python
        except:
            pass
        
        print("❌ Poetry環境が見つかりません")
        return None
    
    def find_system_python(self):
        """システムPythonを検出（tkinter用）"""
        candidates = [
            "/opt/homebrew/bin/python3",
            "/usr/bin/python3",
            "/usr/local/bin/python3"
        ]
        
        for python_path in candidates:
            if Path(python_path).exists():
                try:
                    result = subprocess.run([
                        python_path, "-c", "import tkinter; print('OK')"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ システムPython発見: {python_path}")
                        return python_path
                except:
                    continue
        
        return None
    
    def install_dependencies(self):
        """Poetry環境に全依存関係をインストール"""
        print("📦 依存関係インストール中...")
        
        # Poetry環境に必要なパッケージをインストール
        packages = [
            "nuitka",
            "numpy",
            "torch",
            "torchaudio", 
            "soundfile",
            "scipy",
            "librosa",
            "ffmpeg-python",
            "faiss-cpu",
            "pyworld",
            "praat-parselmouth",
            "torchcrepe",
            "onnx",
            "onnxruntime",
            "tensorboard",
            "matplotlib",
            "Pillow",
            "requests",
            "tqdm",
            "colorama",
            "gradio",
            "edge-tts",
            "tensorboardX",
            "pydub",
            "pyyaml",
            "numba",
            "resampy",
            "tabulate",
            "uvicorn",
            "fastapi",
            "python-multipart",
            "python-dotenv",
            "av",
            "platformdirs",
            "httpx"
        ]
        
        for package in packages:
            print(f"  - {package}をインストール中...")
            result = subprocess.run([
                "poetry", "add", package
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"    ⚠️ {package}インストール失敗（既存の可能性）")
        
        print("✅ 依存関係インストール完了")
    
    def create_wrapper_script(self):
        """tkinterとPoetry環境を橋渡しするラッパースクリプト作成"""
        wrapper_content = '''#!/usr/bin/env python3
"""
RVC GUI Wrapper
システムのtkinterとPoetry環境の依存関係を橋渡し
"""
import sys
import os
import subprocess
from pathlib import Path

# システムPythonのtkinterパスを追加
sys.path.insert(0, "/opt/homebrew/lib/python3.13/lib-dynload")
sys.path.insert(0, "/opt/homebrew/lib/python3.13")

# Poetry環境の依存関係パスを追加  
poetry_site_packages = Path(__file__).parent / "poetry_libs"
if poetry_site_packages.exists():
    sys.path.insert(0, str(poetry_site_packages))

# GUIを起動
from gui_dark_mode_enhanced_complete import VoiceConverterGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceConverterGUI(root)
    root.mainloop()
'''
        
        wrapper_path = self.project_root / "rvc_wrapper.py"
        wrapper_path.write_text(wrapper_content)
        print(f"✅ ラッパースクリプト作成: {wrapper_path}")
        return wrapper_path
    
    def copy_poetry_libs(self, output_dir):
        """Poetry環境のライブラリをコピー"""
        print("📁 Poetry環境のライブラリをコピー中...")
        
        # Poetry環境のsite-packagesを見つける
        result = subprocess.run([
            "poetry", "run", "python", "-c",
            "import site; print(site.getsitepackages()[0])"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            site_packages = Path(result.stdout.strip())
            dest_dir = output_dir / "poetry_libs"
            
            if site_packages.exists():
                shutil.copytree(site_packages, dest_dir, dirs_exist_ok=True)
                print(f"✅ ライブラリコピー完了: {dest_dir}")
                return True
        
        print("❌ Poetry環境のライブラリコピー失敗")
        return False
    
    def build_with_nuitka(self):
        """Nuitkaで全依存関係を含むビルド"""
        print("🔨 Nuitkaビルド開始...")
        
        # 出力ディレクトリ準備
        output_dir = self.project_root / "dist_full_dependency"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()
        
        # ラッパースクリプト作成
        wrapper_script = self.create_wrapper_script()
        
        # Poetry環境のライブラリをコピー
        self.copy_poetry_libs(output_dir)
        
        # Nuitkaコマンド構築
        nuitka_cmd = [
            self.system_python, "-m", "nuitka",
            "--standalone",
            "--macos-create-app-bundle",
            f"--output-dir={output_dir}",
            
            # データディレクトリ
            "--include-data-dir=model_dir=model_dir",
            "--include-data-dir=enhanced_output=enhanced_output",
            "--include-data-dir=poetry_libs=poetry_libs",
            "--include-data-dir=rvc=rvc",
            
            # 必要なファイル
            "--include-data-files=gui_dark_mode_enhanced_complete.py=gui_dark_mode_enhanced_complete.py",
            "--include-data-files=enhanced_voice_converter.py=enhanced_voice_converter.py",
            "--include-data-files=log_importance_analyzer.py=log_importance_analyzer.py",
            "--include-data-files=pyproject.toml=pyproject.toml",
            
            # パッケージ含有
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
            
            # その他の設定
            "--plugin-enable=numpy",
            "--plugin-enable=torch",
            "--plugin-enable=tk-inter",
            "--macos-app-name=RVC Voice Converter Complete",
            "--macos-app-version=1.0.0",
            "--follow-imports",
            "--assume-yes-for-downloads",
            
            str(wrapper_script)
        ]
        
        print("🚀 Nuitkaビルド実行中...")
        print(f"コマンド: {' '.join(nuitka_cmd)}")
        
        # ビルド実行
        result = subprocess.run(nuitka_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Nuitkaビルド成功！")
            
            # appファイルを見つける
            app_path = None
            for item in output_dir.iterdir():
                if item.suffix == ".app":
                    app_path = item
                    break
            
            if app_path:
                print(f"✅ アプリケーション作成完了: {app_path}")
                
                # DMG作成
                self.create_dmg(app_path, output_dir)
                
                return app_path
            else:
                print("❌ .appファイルが見つかりません")
        else:
            print(f"❌ Nuitkaビルド失敗:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
        
        return None
    
    def create_dmg(self, app_path, output_dir):
        """DMGファイル作成"""
        print("💿 DMGファイル作成中...")
        
        dmg_name = "RVC_Voice_Converter_Complete.dmg"
        dmg_path = output_dir / dmg_name
        
        # create-dmgコマンド
        dmg_cmd = [
            "create-dmg",
            "--volname", "RVC Voice Converter Complete",
            "--window-size", "600", "400",
            "--icon-size", "100",
            "--icon", app_path.name, "150", "200",
            "--app-drop-link", "450", "200",
            str(dmg_path),
            str(app_path.parent)
        ]
        
        try:
            result = subprocess.run(dmg_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ DMG作成完了: {dmg_path}")
            else:
                print(f"⚠️ DMG作成失敗: {result.stderr}")
        except FileNotFoundError:
            print("⚠️ create-dmgがインストールされていません")
            print("  brew install create-dmg でインストールしてください")
    
    def run(self):
        """ビルド実行"""
        print("🏗️ 全依存関係内包型RVCビルド開始")
        print("=" * 50)
        
        # 環境チェック
        if not self.poetry_python:
            print("❌ Poetry環境が必要です")
            return False
        
        if not self.system_python:
            print("❌ システムPython（tkinter付き）が必要です")
            return False
        
        # 依存関係インストール
        self.install_dependencies()
        
        # ビルド実行
        app_path = self.build_with_nuitka()
        
        if app_path:
            print("\n✅ ビルド完了！")
            print(f"📱 アプリケーション: {app_path}")
            print("\n🚀 実行方法:")
            print(f"   open '{app_path}'")
            return True
        else:
            print("\n❌ ビルド失敗")
            return False

if __name__ == "__main__":
    builder = FullDependencyBuilder()
    builder.run()