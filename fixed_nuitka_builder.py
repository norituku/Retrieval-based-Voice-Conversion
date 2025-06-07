#!/usr/bin/env python3
"""
修正版Nuitkaビルダー
エラー修正とシンプル化された設定
"""
import subprocess
import sys
import os
from pathlib import Path
import time

class FixedNuitkaBuilder:
    """修正版Nuitkaビルダークラス"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.nuitka_path = "/Users/norikene_satoshi/.local/bin/nuitka"
    
    def build_lightweight_rvc_fixed(self):
        """修正版軽量RVCビルド"""
        print("🪶 修正版軽量RVCビルド開始...")
        
        main_script = self.base_dir / "gui_dark_mode_enhanced.py"
        
        # シンプルな軽量版設定
        cmd = [
            self.nuitka_path,
            "--standalone",
            "--macos-create-app-bundle",
            "--macos-app-name=RVC Voice Converter Lite",
            "--macos-app-version=0.3.5-lite",
            "--enable-plugin=tk-inter",
            "--enable-plugin=anti-bloat",
            "--nofollow-import-to=torch",
            "--nofollow-import-to=librosa",
            "--nofollow-import-to=fairseq",
            "--nofollow-import-to=matplotlib",
            "--nofollow-import-to=IPython",
            "--output-dir=dist_lightweight_fixed",
            "--remove-output",
            "--show-progress",
            str(main_script)
        ]
        
        return self._execute_build(cmd, "lightweight_fixed")
    
    def build_basic_rvc_with_minimal_deps(self):
        """最小依存関係でのRVCビルド"""
        print("🔧 最小依存関係RVCビルド開始...")
        
        # まずはプロトタイプを使用
        main_script = self.base_dir / "rvc_gui_prototype.py"
        
        cmd = [
            self.nuitka_path,
            "--standalone", 
            "--macos-create-app-bundle",
            "--macos-app-name=RVC Voice Converter Basic",
            "--macos-app-version=0.3.5-basic",
            "--enable-plugin=tk-inter",
            "--enable-plugin=anti-bloat",
            "--output-dir=dist_basic_fixed",
            "--remove-output",
            "--show-progress",
            str(main_script)
        ]
        
        return self._execute_build(cmd, "basic_fixed")
    
    def _execute_build(self, cmd, build_name):
        """ビルドの実行"""
        print(f"🔧 {build_name} ビルド実行中...")
        print(f"   メインコマンド: {cmd[0]} {cmd[1]} {cmd[2]}")
        
        # 環境変数の設定
        env = os.environ.copy()
        env['PATH'] = "/Users/norikene_satoshi/.local/bin:" + env.get('PATH', '')
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
            
            elapsed = time.time() - start_time
            print(f"✅ {build_name} ビルド成功! (実行時間: {elapsed/60:.1f}分)")
            
            # 結果確認
            output_dir = None
            for i, arg in enumerate(cmd):
                if arg == "--output-dir" and i + 1 < len(cmd):
                    output_dir = cmd[i + 1]
                    break
            
            if output_dir:
                self._check_build_result(build_name, output_dir)
            
            return True
            
        except subprocess.CalledProcessError as e:
            elapsed = time.time() - start_time
            print(f"❌ {build_name} ビルド失敗 (実行時間: {elapsed/60:.1f}分)")
            
            # 重要なエラーメッセージのみ表示
            if e.stderr:
                error_lines = e.stderr.split('\n')
                important_errors = [line for line in error_lines if any(keyword in line.upper() for keyword in ['ERROR', 'FATAL', 'FAILED'])]
                if important_errors:
                    print("重要なエラー:")
                    for error in important_errors[-3:]:  # 最後の3つのエラー
                        print(f"  {error}")
            
            return False
        
        except Exception as e:
            print(f"❌ {build_name} 予期しないエラー: {e}")
            return False
    
    def _check_build_result(self, build_name, output_dir):
        """ビルド結果の確認"""
        output_path = Path(output_dir)
        if not output_path.exists():
            print(f"⚠️ 出力ディレクトリが見つかりません: {output_path}")
            return
        
        # アプリバンドルの検索
        app_files = list(output_path.glob("*.app"))
        if app_files:
            app_path = app_files[0]
            
            # サイズ計算
            total_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
            file_count = len(list(app_path.rglob('*')))
            
            print(f"📊 {build_name} 結果:")
            print(f"   アプリ: {app_path.name}")
            print(f"   サイズ: {total_size / 1024**2:.1f} MB")
            print(f"   ファイル数: {file_count}")
            
            # 起動テスト
            try:
                test_result = subprocess.run(['open', '-W', '-n', str(app_path)], 
                                           timeout=10, capture_output=True)
                if test_result.returncode == 0:
                    print(f"   ✅ 起動テスト: 成功")
                else:
                    print(f"   ⚠️ 起動テスト: 警告")
            except subprocess.TimeoutExpired:
                print(f"   ⏰ 起動テスト: タイムアウト（正常）")
            except Exception:
                print(f"   ❌ 起動テスト: 失敗")
        else:
            print(f"⚠️ アプリバンドルが見つかりません")

def main():
    """メイン実行関数"""
    print("🔧 修正版Nuitkaビルダー")
    print("=" * 50)
    
    builder = FixedNuitkaBuilder()
    
    # 段階的ビルドテスト
    builds = [
        ("プロトタイプベース", builder.build_basic_rvc_with_minimal_deps),
        ("軽量版RVC", builder.build_lightweight_rvc_fixed),
    ]
    
    results = {}
    
    for build_name, build_func in builds:
        print(f"\n{'='*15} {build_name} {'='*15}")
        
        try:
            result = build_func()
            results[build_name] = result
            
            if result:
                print(f"✅ {build_name}: 成功")
            else:
                print(f"❌ {build_name}: 失敗")
                
        except Exception as e:
            print(f"❌ {build_name}: 例外 - {e}")
            results[build_name] = False
        
        # 少し待機
        time.sleep(2)
    
    # 最終結果
    print(f"\n📊 修正版ビルド結果:")
    print("=" * 50)
    
    success_count = sum(1 for r in results.values() if r)
    total_count = len(results)
    
    for build_name, result in results.items():
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"  {build_name}: {status}")
    
    print(f"\n総合結果: {success_count}/{total_count} 成功")
    
    if success_count > 0:
        print("🎉 修正版で一部成功しました！")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)