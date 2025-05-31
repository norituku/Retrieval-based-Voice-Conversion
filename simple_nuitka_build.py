#!/usr/bin/env python3
"""
簡単なNuitkaビルドスクリプト - 最小限の設定でVoice Converterアプリをビルド
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """シンプルなNuitkaビルド"""
    print("🚀 Voice Converter - Simple Nuitka Build")
    print("=" * 50)
    
    # 現在のディレクトリを確認
    current_dir = Path.cwd()
    main_script = current_dir / "gui_dark_mode.py"
    
    if not main_script.exists():
        print(f"❌ エラー: {main_script} が見つかりません")
        return 1
    
    # シンプルなNuitkaコマンド（仮想環境のPythonを使用）
    cmd = [
        "./build_env/bin/python", "-m", "nuitka",
        str(main_script),
        "--standalone",
        "--macos-create-app-bundle",
        "--macos-app-name=Voice Converter",
        "--macos-app-mode=gui",
        "--enable-plugin=tk-inter",
        "--include-data-dir=model_dir=model_dir",
        "--include-data-dir=rvc=rvc",
        "--include-data-file=gui_settings.json=gui_settings.json",
        "--output-dir=dist",
        "--remove-output",
        "--show-progress"
    ]
    
    print("🔨 ビルド実行中...")
    print(f"コマンド: {' '.join(cmd)}")
    
    try:
        # ビルド実行
        result = subprocess.run(cmd, check=True)
        
        # 結果確認
        app_path = current_dir / "dist" / "Voice Converter.app"
        if app_path.exists():
            print("✅ ビルド成功！")
            print(f"📱 アプリの場所: {app_path}")
            
            # アプリサイズを計算
            size = get_directory_size(app_path)
            print(f"📊 アプリサイズ: {size:.1f} MB")
            
            print("\n🎉 ビルド完了！")
            print("次のステップ:")
            print(f"1. アプリを起動: open '{app_path}'")
            print("2. 他のMacでの動作確認")
            
            return 0
        else:
            print("❌ アプリファイルが見つかりません")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"❌ ビルドエラー: {e}")
        return 1
    except FileNotFoundError:
        print("❌ Nuitkaが見つかりません")
        print("インストール: /usr/bin/python3 -m pip install --user nuitka")
        return 1

def get_directory_size(path):
    """ディレクトリのサイズをMBで取得"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # MB

if __name__ == "__main__":
    sys.exit(main())