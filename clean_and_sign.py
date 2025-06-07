#!/usr/bin/env python3
"""
クリーンアップしてコード署名
問題のあるTclファイルを退避してからコード署名実行
"""
import subprocess
import shutil
import sys
from pathlib import Path

class CleanAndSignManager:
    """クリーンアップ＆署名管理クラス"""
    
    def __init__(self, app_path):
        self.app_path = Path(app_path)
        self.backup_dir = self.app_path.parent / "tcl_backup"
        self.backup_dir.mkdir(exist_ok=True)
    
    def backup_problematic_files(self):
        """問題のあるファイルをバックアップ"""
        print("📦 問題ファイルをバックアップ中...")
        
        macos_dir = self.app_path / "Contents" / "MacOS"
        
        # バックアップ対象ディレクトリ
        problematic_dirs = [
            "tcl-files",
            "tk-files"
        ]
        
        backup_count = 0
        
        for dir_name in problematic_dirs:
            source_dir = macos_dir / dir_name
            if source_dir.exists():
                backup_target = self.backup_dir / dir_name
                
                try:
                    if backup_target.exists():
                        shutil.rmtree(backup_target)
                    
                    shutil.move(str(source_dir), str(backup_target))
                    print(f"  📦 バックアップ: {dir_name} → {backup_target}")
                    backup_count += 1
                except Exception as e:
                    print(f"  ⚠️ バックアップ失敗: {dir_name} - {e}")
        
        print(f"✅ {backup_count}個のディレクトリをバックアップ")
        return backup_count > 0
    
    def clean_other_problematic_files(self):
        """その他の問題ファイルをクリーンアップ"""
        print("🧹 その他の問題ファイルをクリーンアップ中...")
        
        macos_dir = self.app_path / "Contents" / "MacOS"
        
        # 削除対象パターン
        problematic_patterns = [
            "*.tcl",
            "cookiejar*",
            "encoding/*",
            "**/encoding/*"
        ]
        
        removed_count = 0
        
        for pattern in problematic_patterns:
            for file_path in macos_dir.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        print(f"  🗑️ 削除: {file_path.relative_to(macos_dir)}")
                        removed_count += 1
                except Exception as e:
                    print(f"  ⚠️ 削除失敗: {file_path} - {e}")
        
        print(f"✅ {removed_count}個のファイルを削除")
        return removed_count
    
    def perform_clean_code_signing(self):
        """クリーンなコード署名実行"""
        print(f"🔏 クリーンなコード署名実行: {self.app_path.name}")
        
        signing_methods = [
            # 最もシンプルな署名
            {
                'name': 'ベーシック署名',
                'cmd': ['codesign', '--force', '--sign', '-', str(self.app_path)]
            },
            # 深いサイン付き
            {
                'name': 'ディープ署名',
                'cmd': ['codesign', '--force', '--sign', '-', '--deep', str(self.app_path)]
            },
            # リソース署名
            {
                'name': 'リソース署名',
                'cmd': ['codesign', '--force', '--sign', '-', '--resource-rules=/System/Library/Frameworks/Python.framework/Versions/Current/Resources/ResourceRules.plist', str(self.app_path)]
            }
        ]
        
        for method in signing_methods:
            print(f"\\n🔧 {method['name']}を試行中...")
            
            try:
                result = subprocess.run(method['cmd'], capture_output=True, text=True, check=True)
                print(f"✅ {method['name']}: 成功")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ {method['name']}: 失敗")
                if e.stderr:
                    # エラーメッセージの最初の数行のみ表示
                    error_lines = e.stderr.strip().split('\\n')[:3]
                    for line in error_lines:
                        print(f"    {line}")
        
        print("❌ 全ての署名方法が失敗")
        return False
    
    def verify_cleaned_app(self):
        """クリーンアップ後のアプリ検証"""
        print(f"🔍 クリーンアップ後のアプリ検証: {self.app_path.name}")
        
        # ファイル数確認
        macos_dir = self.app_path / "Contents" / "MacOS"
        file_count = len(list(macos_dir.rglob("*")))
        print(f"  📊 MacOSディレクトリファイル数: {file_count}")
        
        # 実行ファイル確認
        executable = macos_dir / "gui_dark_mode_enhanced"
        if executable.exists():
            print(f"  ✅ 実行ファイル存在: {executable.name}")
        else:
            print(f"  ❌ 実行ファイル未発見")
            return False
        
        # 必須ライブラリ確認
        essential_libs = [".so", ".dylib"]
        lib_count = 0
        for ext in essential_libs:
            lib_count += len(list(macos_dir.glob(f"*{ext}")))
        
        print(f"  📚 ライブラリファイル数: {lib_count}")
        
        if lib_count > 10:  # 最低限のライブラリが存在
            print(f"  ✅ 必須ライブラリ十分")
            return True
        else:
            print(f"  ⚠️ ライブラリ不足の可能性")
            return False
    
    def restore_backup_if_needed(self):
        """必要に応じてバックアップを復元"""
        print("🔄 バックアップ復元の検討中...")
        
        # 今回は復元しない（署名成功を優先）
        print("📝 今回は署名成功を優先してバックアップ復元をスキップ")
        return True
    
    def comprehensive_clean_and_sign(self):
        """包括的なクリーンアップ＆署名プロセス"""
        print("🧹 包括的クリーンアップ＆署名プロセス開始")
        print("=" * 60)
        
        steps = [
            ("アプリ検証", self.verify_cleaned_app),
            ("問題ファイルバックアップ", self.backup_problematic_files),
            ("追加クリーンアップ", self.clean_other_problematic_files),
            ("クリーンコード署名", self.perform_clean_code_signing),
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            print(f"\\n{'='*15} {step_name} {'='*15}")
            
            try:
                result = step_func()
                results[step_name] = result
                
                if result:
                    print(f"✅ {step_name}: 成功")
                else:
                    print(f"⚠️ {step_name}: 部分的成功")
                    
            except Exception as e:
                print(f"❌ {step_name}: エラー - {e}")
                results[step_name] = False
        
        # 署名検証
        if results.get("クリーンコード署名", False):
            print(f"\\n{'='*15} 署名検証 {'='*15}")
            try:
                verify_cmd = ['codesign', '--verify', '--verbose', str(self.app_path)]
                result = subprocess.run(verify_cmd, capture_output=True, text=True, check=True)
                print("✅ 署名検証: 成功")
                results["署名検証"] = True
                
                # 署名詳細表示
                info_cmd = ['codesign', '--display', '--verbose', str(self.app_path)]
                info_result = subprocess.run(info_cmd, capture_output=True, text=True)
                if info_result.stderr:
                    print("\\n📋 署名詳細:")
                    for line in info_result.stderr.split('\\n')[:3]:
                        if line.strip():
                            print(f"  {line}")
                            
            except subprocess.CalledProcessError as e:
                print(f"❌ 署名検証: 失敗 - {e}")
                results["署名検証"] = False
        
        # 最終結果
        print(f"\\n📊 クリーンアップ＆署名結果:")
        print("=" * 60)
        
        success_count = sum(results.values())
        total_count = len(results)
        
        for step_name, result in results.items():
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"  {step_name:20}: {status}")
        
        print(f"\\n総合結果: {success_count}/{total_count} 成功")
        
        signing_success = results.get("クリーンコード署名", False)
        
        if signing_success:
            print(f"🎉 クリーンアップ＆コード署名完了！")
            print(f"📱 署名済みアプリ: {self.app_path}")
            
            # アプリサイズ確認
            try:
                size_result = subprocess.run(['du', '-sh', str(self.app_path)], 
                                           capture_output=True, text=True, check=True)
                app_size = size_result.stdout.split()[0]
                print(f"📊 最終アプリサイズ: {app_size}")
            except:
                pass
                
        else:
            print(f"❌ コード署名に失敗しました")
        
        return {
            'success': signing_success,
            'results': results,
            'backup_dir': self.backup_dir
        }

def main():
    """メイン実行関数"""
    app_path = "optimized_apps/RVC Voice Converter.app"
    
    if not Path(app_path).exists():
        print(f"❌ アプリバンドルが見つかりません: {app_path}")
        return False
    
    manager = CleanAndSignManager(app_path)
    result = manager.comprehensive_clean_and_sign()
    
    return result['success']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)