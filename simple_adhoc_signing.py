#!/usr/bin/env python3
"""
シンプルなアドホック署名スクリプト
問題のあるファイルを回避してクリーンな署名を実行
"""
import subprocess
import sys
from pathlib import Path

class SimpleAdHocSigner:
    """シンプルアドホック署名クラス"""
    
    def __init__(self, app_path):
        self.app_path = Path(app_path)
    
    def clean_problematic_files(self):
        """問題のあるファイルのクリーンアップ"""
        print("🧹 問題のあるファイルをクリーンアップ中...")
        
        problematic_patterns = [
            'tcl-files/cookiejar*',
            'tcl-files/encoding/*.enc',
            'tk-files/encoding/*.enc',
        ]
        
        removed_count = 0
        
        for pattern in problematic_patterns:
            pattern_path = self.app_path / "Contents" / "MacOS" / pattern
            
            # globパターンで検索
            for file_path in self.app_path.rglob(pattern.split('/')[-1]):
                if any(p in str(file_path) for p in pattern.split('/')[:-1]):
                    try:
                        if file_path.is_file():
                            file_path.unlink()
                            print(f"  🗑️ 削除: {file_path.relative_to(self.app_path)}")
                            removed_count += 1
                    except Exception as e:
                        print(f"  ⚠️ 削除失敗: {file_path} - {e}")
        
        print(f"✅ {removed_count}個のファイルを削除")
        return removed_count > 0
    
    def simple_adhoc_sign(self):
        """シンプルなアドホック署名"""
        print(f"🔏 シンプルアドホック署名実行: {self.app_path.name}")
        
        try:
            # より制限の少ない署名オプション
            cmd = [
                'codesign',
                '--force',
                '--sign', '-',
                '--deep',
                '--preserve-metadata=entitlements,requirements,flags,runtime',
                str(self.app_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ シンプルアドホック署名完了")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ シンプルアドホック署名失敗: {e}")
            if e.stderr:
                print(f"エラー詳細: {e.stderr}")
            return False
    
    def basic_adhoc_sign(self):
        """最基本のアドホック署名"""
        print(f"🔖 最基本アドホック署名実行: {self.app_path.name}")
        
        try:
            # 最もシンプルな署名
            cmd = [
                'codesign',
                '--force',
                '--sign', '-',
                str(self.app_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ 最基本アドホック署名完了")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 最基本アドホック署名失敗: {e}")
            if e.stderr:
                print(f"エラー詳細: {e.stderr}")
            return False
    
    def verify_and_test(self):
        """署名検証とテスト"""
        print(f"🔍 署名検証中: {self.app_path.name}")
        
        try:
            # 署名検証
            cmd = ['codesign', '--verify', str(self.app_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ 署名検証成功")
            
            # 署名情報表示
            info_cmd = ['codesign', '--display', '--verbose', str(self.app_path)]
            info_result = subprocess.run(info_cmd, capture_output=True, text=True)
            
            if info_result.stderr:
                print("\\n📋 署名情報:")
                for line in info_result.stderr.split('\\n')[:5]:  # 最初の5行のみ
                    if line.strip():
                        print(f"  {line}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 署名検証失敗: {e}")
            return False
    
    def comprehensive_simple_signing(self):
        """包括的シンプル署名プロセス"""
        print("🔖 包括的シンプル署名プロセス開始")
        print("=" * 60)
        
        # 署名方法を順番に試行
        signing_methods = [
            ("シンプルアドホック署名", self.simple_adhoc_sign),
            ("最基本アドホック署名", self.basic_adhoc_sign),
        ]
        
        # まず問題ファイルをクリーンアップ
        print("\\n🧹 前処理中...")
        # self.clean_problematic_files()  # ファイル削除は慎重に
        
        signing_success = False
        
        for method_name, method_func in signing_methods:
            print(f"\\n{'='*15} {method_name} {'='*15}")
            
            try:
                result = method_func()
                if result:
                    print(f"✅ {method_name}: 成功")
                    signing_success = True
                    break
                else:
                    print(f"❌ {method_name}: 失敗")
                    
            except Exception as e:
                print(f"❌ {method_name}: エラー - {e}")
        
        # 署名検証
        if signing_success:
            print(f"\\n{'='*15} 検証テスト {'='*15}")
            verify_result = self.verify_and_test()
        else:
            verify_result = False
        
        # 最終結果
        print(f"\\n📊 シンプル署名結果:")
        print("=" * 60)
        
        if signing_success:
            print(f"✅ コード署名: 成功")
            if verify_result:
                print(f"✅ 署名検証: 成功")
            else:
                print(f"⚠️ 署名検証: 問題あり")
        else:
            print(f"❌ コード署名: 失敗")
        
        return {
            'signing_success': signing_success,
            'verify_result': verify_result if signing_success else False
        }

def main():
    """メイン実行関数"""
    app_path = "optimized_apps/RVC Voice Converter.app"
    
    if not Path(app_path).exists():
        print(f"❌ アプリバンドルが見つかりません: {app_path}")
        return False
    
    signer = SimpleAdHocSigner(app_path)
    result = signer.comprehensive_simple_signing()
    
    return result['signing_success']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)