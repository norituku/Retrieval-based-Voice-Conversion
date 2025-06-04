#!/usr/bin/env python3
"""
Nuitka RVC macOSビルド設定
基本設定から段階的な最適化ビルド
"""
import subprocess
import sys
import os
from pathlib import Path
import time

class NuitkaBuilder:
    """Nuitka ビルダークラス"""
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(__file__).parent if base_dir is None else Path(base_dir)
        self.nuitka_path = self.find_nuitka()
        self.python_path = self.find_python()
        
    def find_nuitka(self):
        """Nuitka実行パスの検出"""
        possible_paths = [
            "/Users/norikene_satoshi/.local/bin/nuitka",
            "nuitka",  # PATH上のnuitka
        ]
        
        for path in possible_paths:
            if Path(path).exists() or self._command_exists(path):
                return path
        
        raise RuntimeError("Nuitka が見つかりません。pipx install nuitka でインストールしてください。")
    
    def find_python(self):
        """最適なPythonの検出"""
        return "/opt/homebrew/bin/python3"  # tkinter対応のシステムPython
    
    def _command_exists(self, command):
        """コマンドの存在確認"""
        try:
            subprocess.run([command, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def build_minimal_test(self):
        """最小テストアプリのビルド"""
        print("🧪 最小テストアプリのビルド開始...")
        
        script_path = self.base_dir / "nuitka_test_minimal.py"
        if not script_path.exists():
            print(f"❌ テストスクリプトが見つかりません: {script_path}")
            return False
        
        # 最小設定でのビルド
        cmd = [
            self.nuitka_path,
            "--standalone",
            "--enable-plugin=tk-inter",
            "--output-dir=dist_minimal",
            "--remove-output",
            "--show-progress",
            str(script_path)
        ]
        
        return self._execute_build(cmd, "minimal_test")
    
    def build_basic_gui(self):
        """基本GUIアプリのビルド"""
        print("🎨 基本GUIアプリのビルド開始...")
        
        script_path = self.base_dir / "nuitka_test_app.py"
        if not script_path.exists():
            print(f"❌ GUIテストスクリプトが見つかりません: {script_path}")
            return False
        
        # 基本GUI設定でのビルド
        cmd = [
            self.nuitka_path,
            "--standalone",
            "--enable-plugin=tk-inter",
            "--enable-plugin=anti-bloat",
            "--output-dir=dist_basic_gui",
            "--remove-output",
            "--show-progress",
            "--show-memory",
            str(script_path)
        ]
        
        return self._execute_build(cmd, "basic_gui")
    
    def build_rvc_prototype(self):
        """RVCプロトタイプのビルド（Poetry環境依存なし）"""
        print("🚀 RVCプロトタイプのビルド開始...")
        
        script_path = self.base_dir / "gui_dark_mode_enhanced.py"
        if not script_path.exists():
            print(f"❌ RVCメインスクリプトが見つかりません: {script_path}")
            return False
        
        # RVC基本設定でのビルド
        cmd = [
            self.nuitka_path,
            "--standalone",
            "--enable-plugin=tk-inter",
            "--enable-plugin=anti-bloat",
            
            # macOS設定
            "--macos-create-app-bundle",
            "--macos-app-name=RVC Voice Converter Test",
            "--macos-app-version=0.3.5-test",
            
            # 基本的なモジュール包含
            "--include-package=rvc",
            
            # 除外設定（サイズ削減）
            "--nofollow-import-to=torch",  # 初期テストではPyTorch除外
            "--nofollow-import-to=librosa",
            "--nofollow-import-to=fairseq",
            "--nofollow-import-to=scipy",
            
            # データファイル
            "--include-data-dir=rvc/configs=rvc/configs",
            
            # 出力設定
            "--output-dir=dist_rvc_prototype",
            "--remove-output",
            "--show-progress",
            "--show-memory",
            "--verbose",
            
            str(script_path)
        ]
        
        return self._execute_build(cmd, "rvc_prototype")
    
    def _execute_build(self, cmd, build_name):
        """ビルドの実行"""
        print(f"🔧 {build_name} ビルドコマンド:")
        print(f"   {' '.join(cmd)}")
        print()
        
        # 環境変数の設定
        env = os.environ.copy()
        env['PATH'] = "/Users/norikene_satoshi/.local/bin:" + env.get('PATH', '')
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
            
            elapsed = time.time() - start_time
            print(f"✅ {build_name} ビルド成功! (実行時間: {elapsed:.1f}秒)")
            
            # ビルド結果の分析
            self._analyze_build_result(build_name, cmd[cmd.index("--output-dir") + 1])
            
            return True
            
        except subprocess.CalledProcessError as e:
            elapsed = time.time() - start_time
            print(f"❌ {build_name} ビルド失敗 (実行時間: {elapsed:.1f}秒)")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            return False
    
    def _analyze_build_result(self, build_name, output_dir):
        """ビルド結果の分析"""
        output_path = Path(output_dir)
        if not output_path.exists():
            print(f"⚠️ 出力ディレクトリが見つかりません: {output_path}")
            return
        
        # ファイルサイズの計算
        total_size = 0
        file_count = 0
        
        for file_path in output_path.rglob('*'):
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                file_count += 1
        
        print(f"📊 {build_name} ビルド結果:")
        print(f"   ファイル数: {file_count:,}")
        print(f"   総サイズ: {total_size / 1024**2:.1f} MB")
        
        # アプリバンドルの場合は追加情報
        app_files = list(output_path.glob("*.app"))
        if app_files:
            app_path = app_files[0]
            print(f"   アプリバンドル: {app_path.name}")
            print(f"   アプリパス: {app_path}")
    
    def run_build_sequence(self):
        """段階的ビルドシーケンス"""
        print("🎯 Nuitka段階的ビルドシーケンス開始")
        print("=" * 60)
        
        build_steps = [
            ("最小テスト", self.build_minimal_test),
            ("基本GUI", self.build_basic_gui),
            ("RVCプロトタイプ", self.build_rvc_prototype),
        ]
        
        results = {}
        
        for step_name, build_func in build_steps:
            print(f"\n{'='*20} {step_name} {'='*20}")
            try:
                result = build_func()
                results[step_name] = result
                
                if result:
                    print(f"✅ {step_name}: 成功")
                else:
                    print(f"❌ {step_name}: 失敗")
                    # 失敗した場合は次のステップに進むかユーザーに確認
                    print(f"⚠️ {step_name}が失敗しましたが、次のステップに進みます...")
                
            except Exception as e:
                print(f"❌ {step_name}: 例外発生 - {e}")
                results[step_name] = False
            
            print()
        
        # 最終結果
        print("🏁 ビルドシーケンス完了")
        print("=" * 60)
        success_count = sum(1 for r in results.values() if r)
        total_count = len(results)
        
        for step_name, result in results.items():
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"  {step_name:15}: {status}")
        
        print(f"\n📊 総合結果: {success_count}/{total_count} 成功")
        
        if success_count > 0:
            print("🎉 少なくとも一部のビルドが成功しました！")
        else:
            print("😞 全てのビルドが失敗しました。設定を確認してください。")
        
        return results

def main():
    """メイン実行関数"""
    try:
        builder = NuitkaBuilder()
        print(f"🔧 Nuitka設定:")
        print(f"   Nuitka: {builder.nuitka_path}")
        print(f"   Python: {builder.python_path}")
        print(f"   ベースディレクトリ: {builder.base_dir}")
        print()
        
        # 段階的ビルドの実行
        results = builder.run_build_sequence()
        
        return any(results.values())
        
    except Exception as e:
        print(f"❌ ビルダー初期化エラー: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)