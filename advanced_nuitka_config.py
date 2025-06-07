#!/usr/bin/env python3
"""
高度なNuitka設定
最大限の最適化とmacOS互換性
依存関係最適化とリソース管理を統合
"""
import subprocess
import sys
import os
import json
from pathlib import Path
import time

class AdvancedNuitkaBuilder:
    """高度なNuitkaビルダークラス"""
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(__file__).parent if base_dir is None else Path(base_dir)
        self.nuitka_path = self.find_nuitka()
        
        # 最適化設定の読み込み
        self.optimization_config = self.load_optimization_config()
        self.resource_settings = self.load_resource_settings()
        
        self.build_profiles = {
            'lightweight': 'RVCライトバージョン（依存関係最小）',
            'standard': 'RVC標準バージョン（CPU PyTorch）',
            'full': 'RVC完全版（全依存関係）'
        }
    
    def find_nuitka(self):
        """Nuitka実行パスの検出"""
        possible_paths = [
            "/Users/norikene_satoshi/.local/bin/nuitka",
            "nuitka",
        ]
        
        for path in possible_paths:
            if Path(path).exists() or self._command_exists(path):
                return path
        
        raise RuntimeError("Nuitka が見つかりません")
    
    def _command_exists(self, command):
        """コマンドの存在確認"""
        try:
            subprocess.run([command, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def load_optimization_config(self):
        """PyTorch最適化設定の読み込み"""
        config_path = self.base_dir / "nuitka_optimization_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_resource_settings(self):
        """リソース最適化設定の読み込み"""
        settings_path = self.base_dir / "resource_optimization_settings.json"
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def build_lightweight_rvc(self):
        """軽量版RVCのビルド（GUI + 動的リソースローダー）"""
        print("🪶 軽量版RVCビルド開始...")
        
        main_script = self.base_dir / "gui_dark_mode_enhanced.py"
        if not main_script.exists():
            print(f"❌ メインスクリプトが見つかりません: {main_script}")
            return False
        
        # 軽量版設定
        cmd = [
            self.nuitka_path,
            
            # === 基本設定 ===
            "--standalone",
            "--macos-create-app-bundle",
            "--macos-app-name=RVC Voice Converter Lite",
            "--macos-app-version=0.3.5-lite",
            "--macos-signed-app-name=com.rvc.voiceconverter.lite",
            
            # === GUI最適化 ===
            "--enable-plugin=tk-inter",
            "--enable-plugin=anti-bloat",
            
            # === 重い依存関係の除外 ===
            "--nofollow-import-to=torch",
            "--nofollow-import-to=librosa",
            "--nofollow-import-to=fairseq",
            "--nofollow-import-to=scipy",
            "--nofollow-import-to=numpy",
            "--nofollow-import-to=soundfile",
            
            # === 不要モジュール除外 ===
            "--nofollow-import-to=matplotlib",
            "--nofollow-import-to=IPython",
            "--nofollow-import-to=jupyter",
            "--nofollow-import-to=pytest",
            
            # === 軽量データ包含 ===
            "--include-data-dir=rvc/configs=rvc/configs",
            "--include-data-file=dynamic_resource_loader.py=dynamic_resource_loader.py",
            
            # === 出力設定 ===
            "--output-dir=dist_lightweight",
            "--remove-output",
            "--show-progress",
            "--show-memory",
            
            str(main_script)
        ]
        
        return self._execute_build(cmd, "lightweight")
    
    def build_standard_rvc(self):
        """標準版RVCのビルド（CPU PyTorch + 最適化）"""
        print("⚖️ 標準版RVCビルド開始...")
        
        main_script = self.base_dir / "gui_dark_mode_enhanced.py"
        
        # 標準版設定（最適化済み依存関係を含む）
        cmd = [
            self.nuitka_path,
            
            # === 基本設定 ===
            "--standalone",
            "--macos-create-app-bundle",
            "--macos-app-name=RVC Voice Converter",
            "--macos-app-version=0.3.5",
            "--macos-signed-app-name=com.rvc.voiceconverter",
            
            # === パフォーマンス最適化 ===
            "--enable-plugin=tk-inter",
            "--enable-plugin=numpy",
            "--enable-plugin=anti-bloat",
            
            # === PyTorch最適化 ===
            "--enable-plugin=torch",
        ]
        
        # PyTorch最適化設定の適用
        optimization_config = self.optimization_config
        if optimization_config:
            for exclude in optimization_config.get('nofollow_imports', []):
                cmd.append(f"--nofollow-import-to={exclude}")
            
            for package in optimization_config.get('include_packages', []):
                cmd.append(f"--include-package={package}")
        
        # リソース設定の適用
        if self.resource_settings and 'include_commands' in self.resource_settings:
            for include_cmd in self.resource_settings['include_commands']:
                cmd.append(include_cmd)
        
        cmd.extend([
            # === 詳細最適化 ===
            "--assume-yes-for-downloads",
            "--report=compilation-report.xml",
            
            # === 出力設定 ===
            "--output-dir=dist_standard",
            "--remove-output",
            "--show-progress",
            "--show-memory",
            "--verbose",
            
            str(main_script)
        ])
        
        return self._execute_build(cmd, "standard")
    
    def build_full_rvc(self):
        """完全版RVCのビルド（全機能）"""
        print("🚀 完全版RVCビルド開始...")
        
        main_script = self.base_dir / "enhanced_voice_converter.py"
        if not main_script.exists():
            main_script = self.base_dir / "gui_dark_mode_enhanced.py"
        
        # 完全版設定
        cmd = [
            self.nuitka_path,
            
            # === 基本設定 ===
            "--standalone",
            "--macos-create-app-bundle",
            "--macos-app-name=RVC Voice Converter Pro",
            "--macos-app-version=0.3.5-pro",
            "--macos-signed-app-name=com.rvc.voiceconverter.pro",
            
            # === 全機能有効化 ===
            "--enable-plugin=tk-inter",
            "--enable-plugin=numpy",
            "--enable-plugin=torch",
            "--enable-plugin=anti-bloat",
            
            # === 包含モジュール ===
            "--include-package=rvc",
            "--include-package=librosa",
            "--include-package=soundfile",
            "--include-package=scipy.signal",
            "--include-package=numpy",
            "--include-package=numba",
            
            # === 選択的除外のみ ===
            "--nofollow-import-to=matplotlib",
            "--nofollow-import-to=IPython",
            "--nofollow-import-to=jupyter",
            "--nofollow-import-to=pytest",
            
            # === 完全データ包含 ===
            "--include-data-dir=rvc=rvc",
        ]
        
        # リソース設定の適用
        if self.resource_settings and 'include_commands' in self.resource_settings:
            for include_cmd in self.resource_settings['include_commands']:
                cmd.append(include_cmd)
        
        cmd.extend([
            # === 最大最適化 ===
            "--assume-yes-for-downloads",
            "--report=compilation-report-full.xml",
            
            # === 出力設定 ===
            "--output-dir=dist_full",
            "--remove-output",
            "--show-progress",
            "--show-memory",
            "--verbose",
            
            str(main_script)
        ])
        
        return self._execute_build(cmd, "full", timeout=1800)  # 30分タイムアウト
    
    def _execute_build(self, cmd, build_name, timeout=600):
        """ビルドの実行"""
        print(f"🔧 {build_name} ビルドコマンド:")
        print(f"   {' '.join(cmd[:10])}...")  # 最初の10個だけ表示
        print()
        
        # 環境変数の設定
        env = os.environ.copy()
        env['PATH'] = "/Users/norikene_satoshi/.local/bin:" + env.get('PATH', '')
        env['NUITKA_CACHE_DIR'] = str(self.base_dir / ".nuitka_cache")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, 
                                  env=env, timeout=timeout)
            
            elapsed = time.time() - start_time
            print(f"✅ {build_name} ビルド成功! (実行時間: {elapsed/60:.1f}分)")
            
            # ビルド結果の分析
            self._analyze_advanced_build_result(build_name, cmd[cmd.index("--output-dir") + 1])
            
            return True
            
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            print(f"⏰ {build_name} ビルドタイムアウト (実行時間: {elapsed/60:.1f}分)")
            return False
            
        except subprocess.CalledProcessError as e:
            elapsed = time.time() - start_time
            print(f"❌ {build_name} ビルド失敗 (実行時間: {elapsed/60:.1f}分)")
            
            # エラー詳細の表示（最後の20行のみ）
            if e.stderr:
                error_lines = e.stderr.split('\n')[-20:]
                print("エラー詳細（最後の20行）:")
                for line in error_lines:
                    print(f"  {line}")
            
            return False
    
    def _analyze_advanced_build_result(self, build_name, output_dir):
        """高度なビルド結果の分析"""
        output_path = Path(output_dir)
        if not output_path.exists():
            print(f"⚠️ 出力ディレクトリが見つかりません: {output_path}")
            return
        
        # アプリバンドルの検索
        app_files = list(output_path.glob("*.app"))
        if not app_files:
            print(f"⚠️ アプリバンドルが見つかりません")
            return
        
        app_path = app_files[0]
        
        # 詳細分析
        total_size = 0
        file_count = 0
        largest_files = []
        
        for file_path in app_path.rglob('*'):
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                file_count += 1
                
                # 大きなファイル（10MB以上）を記録
                if size > 10 * 1024 * 1024:
                    largest_files.append({
                        'path': str(file_path.relative_to(app_path)),
                        'size_mb': size / 1024**2
                    })
        
        # 分析結果の表示
        print(f"📊 {build_name} ビルド詳細分析:")
        print(f"   アプリバンドル: {app_path.name}")
        print(f"   総サイズ: {total_size / 1024**3:.2f} GB")
        print(f"   ファイル数: {file_count:,}")
        
        if largest_files:
            print(f"   大きなファイル (>10MB):")
            for file_info in sorted(largest_files, key=lambda x: x['size_mb'], reverse=True)[:5]:
                print(f"     {file_info['path']}: {file_info['size_mb']:.1f} MB")
        
        # パフォーマンス評価
        size_gb = total_size / 1024**3
        if size_gb < 0.1:
            print(f"   🟢 サイズ評価: 優秀 ({size_gb:.2f} GB)")
        elif size_gb < 0.5:
            print(f"   🟡 サイズ評価: 良好 ({size_gb:.2f} GB)")
        elif size_gb < 1.0:
            print(f"   🟠 サイズ評価: 普通 ({size_gb:.2f} GB)")
        else:
            print(f"   🔴 サイズ評価: 要最適化 ({size_gb:.2f} GB)")
    
    def run_advanced_build_sequence(self):
        """高度なビルドシーケンス"""
        print("🎯 高度なNuitkaビルドシーケンス開始")
        print("=" * 60)
        
        # プロファイル選択
        print("利用可能なビルドプロファイル:")
        for profile, description in self.build_profiles.items():
            print(f"  {profile}: {description}")
        
        build_sequence = [
            ("軽量版", self.build_lightweight_rvc),
            ("標準版", self.build_standard_rvc),
            # ("完全版", self.build_full_rvc),  # 時間がかかるため最後に
        ]
        
        results = {}
        
        for build_name, build_func in build_sequence:
            print(f"\n{'='*20} {build_name} {'='*20}")
            
            try:
                result = build_func()
                results[build_name] = result
                
                if result:
                    print(f"✅ {build_name}: 成功")
                else:
                    print(f"❌ {build_name}: 失敗")
                
                # 少し待機（システムの安定化のため）
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {build_name}: 例外発生 - {e}")
                results[build_name] = False
            
            print()
        
        # 最終結果
        print("🏁 高度ビルドシーケンス完了")
        print("=" * 60)
        
        success_count = sum(1 for r in results.values() if r)
        total_count = len(results)
        
        for build_name, result in results.items():
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"  {build_name:15}: {status}")
        
        print(f"\n📊 総合結果: {success_count}/{total_count} 成功")
        
        if success_count > 0:
            print("🎉 少なくとも一部のビルドが成功しました！")
            
            # 推奨事項
            if success_count == total_count:
                print("✨ 全てのビルドが成功 - フェーズ4に進む準備完了")
            else:
                print("⚠️ 一部失敗 - 成功したビルドを基に進行可能")
        
        return results

def main():
    """メイン実行関数"""
    try:
        builder = AdvancedNuitkaBuilder()
        
        print(f"🔧 高度なNuitka設定:")
        print(f"   Nuitka: {builder.nuitka_path}")
        print(f"   最適化設定: {'読み込み済み' if builder.optimization_config else '未設定'}")
        print(f"   リソース設定: {'読み込み済み' if builder.resource_settings else '未設定'}")
        print()
        
        # 高度なビルドシーケンスの実行
        results = builder.run_advanced_build_sequence()
        
        return any(results.values())
        
    except Exception as e:
        print(f"❌ 高度ビルダー初期化エラー: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)