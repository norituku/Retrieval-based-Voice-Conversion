#!/usr/bin/env python3
"""
Nuitkaを使用してVoice ConverterのmacOSネイティブアプリをビルドするスクリプト
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
from nuitka_config import nuitka_options, additional_resources

def build_app():
    """Nuitkaを使用してアプリをビルド"""
    print("🚀 Voice Converter macOSアプリのビルドを開始...")
    
    # 現在のディレクトリを確認
    current_dir = Path.cwd()
    print(f"📁 現在のディレクトリ: {current_dir}")
    
    # 必要なファイルの存在確認
    main_script = current_dir / "gui_dark_mode.py"
    if not main_script.exists():
        print(f"❌ エラー: {main_script} が見つかりません")
        return False
    
    # Nuitkaコマンドを構築（system pythonを使用）
    cmd = [
        "/usr/bin/python3", "-m", "nuitka",
        str(main_script)
    ]
    
    # オプションを追加
    for key, value in nuitka_options.items():
        if key == 'enable-plugins':
            for plugin in value:
                cmd.extend([f"--enable-plugin={plugin}"])
        elif key == 'include-modules':
            for module in value:
                cmd.extend([f"--include-module={module}"])
        elif key == 'include-data-dirs':
            for data_dir in value:
                cmd.extend([f"--include-data-dir={data_dir}"])
        elif key == 'include-data-files':
            for data_file in value:
                cmd.extend([f"--include-data-file={data_file}"])
        elif isinstance(value, bool):
            if value:
                cmd.append(f"--{key}")
        else:
            cmd.extend([f"--{key}={value}"])
    
    # ビルド実行
    print("🔨 Nuitkaビルドを実行中...")
    print(f"実行コマンド: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("✅ ビルドが正常に完了しました！")
        
        # 生成されたアプリの場所を確認
        app_path = current_dir / "dist" / "Voice Converter.app"
        if app_path.exists():
            print(f"📱 アプリが作成されました: {app_path}")
            
            # アプリのサイズを表示
            size = get_directory_size(app_path)
            print(f"📊 アプリサイズ: {size:.1f} MB")
            
            return True
        else:
            print("⚠️ アプリファイルが見つかりません")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ ビルドエラー: {e}")
        return False
    except FileNotFoundError:
        print("❌ Nuitkaが見つかりません。以下のコマンドでインストールしてください:")
        print("pip install nuitka")
        return False

def get_directory_size(path):
    """ディレクトリのサイズをMBで取得"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # MB

def check_dependencies():
    """必要な依存関係をチェック"""
    print("🔍 依存関係をチェック中...")
    
    # Nuitkaの確認
    try:
        result = subprocess.run(["/usr/bin/python3", "-m", "nuitka", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Nuitka: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Nuitkaが見つかりません")
        print("インストールコマンド: /usr/bin/python3 -m pip install --user nuitka")
        return False
    
    # tkinterの確認（system pythonで）
    try:
        result = subprocess.run(["/usr/bin/python3", "-c", "import tkinter"], 
                              capture_output=True, check=True)
        print("✅ tkinter: 利用可能")
    except subprocess.CalledProcessError:
        print("❌ tkinterが見つかりません")
        return False
    
    return True

def main():
    """メイン実行関数"""
    print("=" * 50)
    print("🎵 Voice Converter - Nuitka Build Script")
    print("=" * 50)
    
    # 依存関係チェック
    if not check_dependencies():
        print("❌ 依存関係のチェックに失敗しました")
        return 1
    
    # ビルド実行
    if build_app():
        print("\n🎉 ビルドが完了しました！")
        print("作成されたアプリは dist/Voice Converter.app です")
        print("\n📋 次のステップ:")
        print("1. アプリを起動してテスト")
        print("2. 他のMacで動作確認")
        print("3. 必要に応じてアプリに署名")
        return 0
    else:
        print("\n❌ ビルドに失敗しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())