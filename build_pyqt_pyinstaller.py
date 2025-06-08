#!/usr/bin/env python3
"""
PyQt RVC Voice Converter - PyInstallerビルダー
rvc_pyqt_app.py用のPyInstallerビルドシステム
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class PyInstallerRVCBuilder:
    """PyInstaller RVC Voice Converter専用ビルダー"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        
        # PyQtアプリ設定
        self.gui_script = "rvc_pyqt_app.py"
        self.app_name = "RVC_Voice_Converter"
        
        # ビルド出力設定
        self.output_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
        # Poetry環境の使用
        try:
            result = subprocess.run(['poetry', 'env', 'info', '--path'], 
                                  capture_output=True, text=True, check=True)
            poetry_env_path = result.stdout.strip()
            self.poetry_python = f"{poetry_env_path}/bin/python"
            print(f"✅ Poetry環境確認: {poetry_env_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Poetry環境未検出")
            sys.exit(1)
    
    def clean_build_directories(self):
        """ビルドディレクトリをクリーンアップ"""
        for dir_path in [self.output_dir, self.build_dir]:
            if dir_path.exists():
                print(f"🧹 既存ディレクトリを削除: {dir_path}")
                shutil.rmtree(dir_path)
    
    def verify_source_file(self):
        """ソースファイルの存在確認"""
        source_path = self.project_root / self.gui_script
        if not source_path.exists():
            print(f"❌ ソースファイルが見つかりません: {source_path}")
            return False
        print(f"✅ ソースファイル確認: {source_path}")
        return True
    
    def verify_dependencies(self):
        """必要な依存関係の確認"""
        print("🔍 依存関係チェック中...")
        required_modules = [
            # GUI関連
            "PyQt5.QtCore", "PyQt5.QtWidgets", "PyQt5.QtGui",
            # 基本的な数値・音声処理
            "numpy", "torch", "soundfile", "librosa", "pydub", 
            # 音声変換専用
            "av", "pyworld", "scipy", "torchcrepe", "torchaudio", "faiss", "resampy"
        ]
        # fairseqは依存関係チェックからスキップ（PyInstallerでバンドル）
        
        missing_modules = []
        for module in required_modules:
            try:
                result = subprocess.run([
                    self.poetry_python, "-c", f"import {module}; print('✅ {module}')"
                ], capture_output=True, text=True, check=True)
                print(result.stdout.strip())
            except subprocess.CalledProcessError:
                missing_modules.append(module)
                print(f"❌ {module} - 見つかりません")
        
        if missing_modules:
            print(f"❌ 不足している依存関係: {', '.join(missing_modules)}")
            return False
        
        print("✅ すべての依存関係が確認されました")
        return True
    
    def get_fairseq_package_path(self):
        """fairseqパッケージのパスを取得"""
        try:
            result = subprocess.run([
                self.poetry_python, "-c", 
                "import fairseq; import os; print(os.path.dirname(fairseq.__file__))"
            ], capture_output=True, text=True, check=True)
            fairseq_path = result.stdout.strip()
            print(f"✅ fairseqパッケージパス: {fairseq_path}")
            return fairseq_path
        except subprocess.CalledProcessError:
            print("❌ fairseqパッケージが見つかりません")
            return None
    
    def get_python_shared_library(self):
        """Python共有ライブラリのパスを取得"""
        try:
            result = subprocess.run([
                self.poetry_python, "-c", 
                """
import sys
import os
import sysconfig
import glob

# Python共有ライブラリを探す
lib_paths = [
    sysconfig.get_config_var('LIBDIR'),
    os.path.dirname(sys.executable) + '/../lib',
    '/opt/homebrew/lib',
    '/usr/local/lib'
]

for path in lib_paths:
    if path and os.path.exists(path):
        python_libs = glob.glob(f'{path}/libpython3.13*.dylib')
        if python_libs:
            print(python_libs[0])
            break
"""
            ], capture_output=True, text=True, check=True)
            python_lib_path = result.stdout.strip()
            if python_lib_path:
                print(f"✅ Python共有ライブラリパス: {python_lib_path}")
                return python_lib_path
            else:
                print("❌ Python共有ライブラリが見つかりません")
                return None
        except subprocess.CalledProcessError:
            print("❌ Python共有ライブラリの検索に失敗")
            return None
    
    def build_with_pyinstaller(self):
        """PyInstallerでアプリをビルド"""
        print("🔨 PyInstallerビルド開始...")
        
        # アイコンパスの確認
        icon_path = self.project_root / "app_icons" / "rvc_icon.icns"
        
        # FFmpegバイナリのパスを確認
        ffmpeg_paths = [
            "/opt/homebrew/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/local/bin/ffmpeg"
        ]
        
        ffmpeg_binary = None
        ffprobe_binary = None
        for path in ffmpeg_paths:
            if Path(path).exists():
                ffmpeg_binary = path
                ffprobe_binary = path.replace("ffmpeg", "ffprobe")
                break
        
        # fairseqパッケージパスを取得
        fairseq_path = self.get_fairseq_package_path()
        
        # PyInstallerコマンド構築
        pyinstaller_cmd = [
            self.poetry_python, "-m", "PyInstaller",
            "--onedir",                     # ディレクトリ形式（fairseq対応）
            "--windowed",                   # GUI アプリ（コンソールなし）
            f"--name={self.app_name}",      # アプリ名
            "--clean",                      # キャッシュクリア
            # データファイル追加
            "--add-data=rvc:rvc",
            "--add-data=enhanced_voice_converter.py:.",
            # GUI関連の隠れたインポート
            "--hidden-import=PyQt5.QtCore",
            "--hidden-import=PyQt5.QtWidgets", 
            "--hidden-import=PyQt5.QtGui",
            
            # 基本的な数値計算・音声処理
            "--hidden-import=numpy",
            "--hidden-import=numpy.linalg",
            "--hidden-import=numpy.fft",
            
            # Torch関連の包括的設定
            "--hidden-import=torch",
            "--collect-all=torch",
            "--hidden-import=torch._C",
            "--hidden-import=torch._C._nn",
            "--hidden-import=torch._C._fft",
            "--hidden-import=torch._C._linalg",
            "--hidden-import=torch._C._sparse",
            "--hidden-import=torch.nn.functional",
            "--hidden-import=torch.nn.utils",
            "--hidden-import=torch.nn.utils.rnn",
            
            # Torchaudio関連
            "--hidden-import=torchaudio",
            "--hidden-import=torchaudio.functional",
            "--hidden-import=torchaudio.transforms",
            "--hidden-import=torchaudio.models",
            "--collect-all=torchaudio",
            
            # Scipy関連の包括的設定
            "--hidden-import=scipy",
            "--hidden-import=scipy.signal",
            "--hidden-import=scipy.linalg",
            "--hidden-import=scipy.sparse",
            "--hidden-import=scipy.interpolate",
            "--hidden-import=scipy.optimize",
            "--hidden-import=scipy.fft",
            "--collect-all=scipy",
            
            # 音声処理ライブラリ
            "--hidden-import=soundfile",
            "--hidden-import=librosa",
            "--hidden-import=librosa.feature",
            "--hidden-import=librosa.filters",
            "--hidden-import=librosa.util",
            "--hidden-import=librosa.core",
            "--collect-all=librosa",
            
            # 音声フォーマット処理
            "--hidden-import=pydub",
            "--hidden-import=av",
            "--collect-all=av",
            
            # RVC専用音声処理
            "--hidden-import=pyworld",
            "--hidden-import=torchcrepe",
            "--hidden-import=torchcrepe.model",
            "--hidden-import=torchcrepe.decode",
            "--collect-all=torchcrepe",
            
            # 近傍探索・インデックス機能
            "--hidden-import=faiss",
            "--hidden-import=faiss.swigfaiss",
            "--collect-all=faiss",
            
            # 高品質リサンプリング
            "--hidden-import=resampy",
            "--hidden-import=resampy.core",
            "--collect-all=resampy",
            
            # パフォーマンス最適化
            "--hidden-import=numba",
            "--hidden-import=numba.core",
            "--hidden-import=llvmlite",
            
            # 機械学習補助ライブラリ
            "--hidden-import=sklearn",
            "--hidden-import=sklearn.metrics",
            "--hidden-import=sklearn.utils",
            "--collect-all=sklearn",
            
            # 可視化ライブラリ（一部のlibrosaやtorchcrepe機能で必要）
            "--hidden-import=matplotlib",
            "--hidden-import=matplotlib.pyplot",
            
            # 設定管理
            "--hidden-import=omegaconf",
            "--hidden-import=hydra",
            
            # RVCアプリケーション関連
            "--hidden-import=enhanced_voice_converter",
            
            # Fairseq関連
            "--hidden-import=fairseq",
            "--hidden-import=fairseq.models",
            "--hidden-import=fairseq.criterions",
            "--hidden-import=fairseq.dataclass.configs",
            "--hidden-import=fairseq.models.hubert",
            
            # 除外設定（サイズ最適化 - 安全な除外のみ）
            "--exclude-module=tkinter",
            "--exclude-module=pytest",
            "--exclude-module=jupyter",
            "--exclude-module=IPython",
            "--exclude-module=notebook",
            "--exclude-module=spyder",
            "--exclude-module=qtconsole",
            # ソースファイル
            str(self.project_root / self.gui_script)
        ]
        
        # fairseqパッケージ全体を追加
        if fairseq_path:
            pyinstaller_cmd.extend([f"--add-data={fairseq_path}:fairseq"])
            print(f"✅ fairseqパッケージ追加: {fairseq_path}")
            
            # 重要なfairseqサブディレクトリも明示的に追加
            for subdir in ['criterions', 'models', 'dataclass']:
                subdir_path = Path(fairseq_path) / subdir
                if subdir_path.exists():
                    pyinstaller_cmd.extend([f"--add-data={subdir_path}:fairseq/{subdir}"])
                    print(f"✅ fairseq/{subdir}ディレクトリ追加: {subdir_path}")
        else:
            print("⚠️ fairseqパッケージが見つからないため、fairseq関連の機能は制限されます")
        
        # Python共有ライブラリを取得・追加
        python_lib_path = self.get_python_shared_library()
        if python_lib_path and Path(python_lib_path).exists():
            pyinstaller_cmd.extend([f"--add-binary={python_lib_path}:."])
            print(f"✅ Python共有ライブラリ追加: {python_lib_path}")
        else:
            print("⚠️ Python共有ライブラリが見つかりません")
        
        # FFmpegバイナリを追加
        if ffmpeg_binary and Path(ffmpeg_binary).exists():
            pyinstaller_cmd.extend([f"--add-binary={ffmpeg_binary}:."])
            print(f"✅ FFmpeg追加: {ffmpeg_binary}")
        if ffprobe_binary and Path(ffprobe_binary).exists():
            pyinstaller_cmd.extend([f"--add-binary={ffprobe_binary}:."])
            print(f"✅ FFprobe追加: {ffprobe_binary}")
        
        # アイコン追加（macOS）
        if icon_path.exists():
            pyinstaller_cmd.extend([f"--icon={icon_path}"])
            print(f"✅ アイコン追加: {icon_path}")
        else:
            print(f"⚠️ アイコンファイルが見つかりません: {icon_path}")
        
        print(f"実行コマンド: {' '.join(pyinstaller_cmd)}")
        
        try:
            subprocess.run(pyinstaller_cmd, check=True, cwd=self.project_root)
            print("✅ PyInstallerビルド成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstallerビルド失敗: {e}")
            return False
    
    def create_app_bundle_macos(self):
        """macOS用のアプリバンドルを作成"""
        if sys.platform != "darwin":
            print("ℹ️ macOS以外のため、アプリバンドル作成をスキップ")
            return True
        
        print("📱 macOSアプリバンドル作成中...")
        
        # onedirモードでは実行ディレクトリをチェック
        app_dir = self.output_dir / self.app_name
        if not app_dir.exists():
            print(f"❌ アプリディレクトリが見つかりません: {app_dir}")
            return False
        
        exec_file = app_dir / self.app_name
        if not exec_file.exists():
            print(f"❌ 実行ファイルが見つかりません: {exec_file}")
            return False
        
        # .appバンドル作成
        app_bundle = self.output_dir / f"{self.app_name}.app"
        contents_dir = app_bundle / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        # ディレクトリ作成
        for dir_path in [contents_dir, macos_dir, resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # アプリディレクトリ全体を移動（安全な方法）
        target_path = macos_dir / self.app_name
        
        # 移動先が既に存在する場合は削除
        if target_path.exists():
            print(f"🗑️ 既存の移動先を削除: {target_path}")
            if target_path.is_dir():
                shutil.rmtree(str(target_path))
                print(f"📁 ディレクトリを削除: {target_path}")
            else:
                target_path.unlink()
                print(f"📄 ファイルを削除: {target_path}")
        
        # より安全な方法でディレクトリを移動
        try:
            shutil.move(str(app_dir), str(target_path))
            print(f"✅ アプリディレクトリを移動: {app_dir} -> {target_path}")
        except (FileExistsError, OSError) as e:
            # フォールバック: copytree + rmtree
            print(f"⚠️ move失敗、copytreeを使用: {e}")
            shutil.copytree(str(app_dir), str(target_path))
            shutil.rmtree(str(app_dir))
            print(f"✅ アプリディレクトリをコピー＆削除: {app_dir} -> {target_path}")
        
        # Info.plistを作成
        info_plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>RVC Voice Converter</string>
    <key>CFBundleDisplayName</key>
    <string>RVC Voice Converter</string>
    <key>CFBundleIdentifier</key>
    <string>com.rvc.voiceconverter</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>'''
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(info_plist_content)
        
        # アイコンをコピー
        icon_path = self.project_root / "app_icons" / "rvc_icon.icns"
        if icon_path.exists():
            shutil.copy2(icon_path, resources_dir / "icon.icns")
        
        print(f"✅ macOSアプリバンドル作成完了: {app_bundle}")
        return True
    
    def create_launch_script(self):
        """起動スクリプトを作成"""
        if sys.platform == "darwin":
            script_content = f"""#!/bin/bash
cd "$(dirname "$0")"
open "{self.app_name}.app"
"""
            script_path = self.output_dir / "launch_app.sh"
        else:
            script_content = f"""#!/bin/bash
cd "$(dirname "$0")"
./{self.app_name}
"""
            script_path = self.output_dir / "launch_app.sh"
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # 実行権限を付与
        os.chmod(script_path, 0o755)
        print(f"✅ 起動スクリプト作成: {script_path}")
    
    def build(self):
        """ビルドプロセス実行"""
        print("🚀 PyQt RVC Voice Converter ビルド開始")
        
        # ステップ1: 準備
        if not self.verify_source_file():
            return False
        
        if not self.verify_dependencies():
            return False
        
        # ステップ2: クリーンアップ
        self.clean_build_directories()
        
        # ステップ3: ビルド
        if not self.build_with_pyinstaller():
            return False
        
        # ステップ4: 後処理
        if sys.platform == "darwin":
            if not self.create_app_bundle_macos():
                return False
        
        self.create_launch_script()
        
        print(f"🎉 ビルド完了!")
        print(f"📱 アプリケーション: {self.output_dir}")
        
        return True

def main():
    """メイン実行"""
    builder = PyInstallerRVCBuilder()
    success = builder.build()
    
    if success:
        print("\n✅ ビルド成功! アプリケーションを起動できます。")
        sys.exit(0)
    else:
        print("\n❌ ビルドに失敗しました。")
        sys.exit(1)

if __name__ == "__main__":
    main()