#!/usr/bin/env python3
"""
macOSアプリケーションコード署名管理システム
Developer ID、アドホック署名、自己署名証明書に対応
"""
import subprocess
import sys
from pathlib import Path
import re

class CodeSigningManager:
    """コード署名管理クラス"""
    
    def __init__(self, app_path):
        self.app_path = Path(app_path)
        self.signing_results = {}
        
    def check_available_certificates(self):
        """利用可能な署名証明書の確認"""
        print("🔐 利用可能な署名証明書を確認中...")
        
        certificates = {
            'developer_id': [],
            'mac_developer': [],
            'self_signed': [],
            'other': []
        }
        
        try:
            # Keychainから証明書を取得
            result = subprocess.run([
                'security', 'find-identity', '-v', '-p', 'codesigning'
            ], capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\\n')
            
            for line in lines:
                if 'Developer ID Application' in line:
                    certificates['developer_id'].append(line.strip())
                elif 'Mac Developer' in line:
                    certificates['mac_developer'].append(line.strip())
                elif 'iPhone Developer' not in line and '1) ' in line:
                    certificates['other'].append(line.strip())
                    
        except subprocess.CalledProcessError as e:
            print(f"⚠️ 証明書確認エラー: {e}")
        
        # 結果表示
        print("\\n📋 利用可能な証明書:")
        
        if certificates['developer_id']:
            print(f"  🟢 Developer ID Application: {len(certificates['developer_id'])}個")
            for cert in certificates['developer_id'][:2]:  # 最初の2つを表示
                print(f"    {cert}")
        else:
            print(f"  🔴 Developer ID Application: なし")
            
        if certificates['mac_developer']:
            print(f"  🟡 Mac Developer: {len(certificates['mac_developer'])}個")
        else:
            print(f"  🔴 Mac Developer: なし")
            
        if certificates['other']:
            print(f"  🟠 その他の証明書: {len(certificates['other'])}個")
        
        return certificates
    
    def create_self_signed_certificate(self):
        """自己署名証明書の作成（開発用）"""
        print("\\n🔧 自己署名証明書を作成中...")
        
        cert_name = "RVC Voice Converter Developer"
        
        try:
            # 既存の証明書を確認
            result = subprocess.run([
                'security', 'find-certificate', '-c', cert_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 既存の自己署名証明書を発見: {cert_name}")
                return cert_name
            
            # 新しい自己署名証明書を作成
            create_cmd = [
                'security', 'create-keypair',
                '-a', 'RSA',
                '-s', '2048',
                '-f', '1',
                '-t', '1',
                '-d', '365',
                '-k', '~/Library/Keychains/login.keychain',
                cert_name
            ]
            
            # 代替方法：certtoolを使用
            alt_cmd = [
                'certtool', 'y', 'c', 'n',
                'RVC Voice Converter',
                'Developer',
                'com.rvc.voiceconverter',
                'JP',
                cert_name
            ]
            
            try:
                subprocess.run(create_cmd, check=True, capture_output=True)
                print(f"✅ 自己署名証明書を作成: {cert_name}")
                return cert_name
            except subprocess.CalledProcessError:
                print(f"⚠️ 自己署名証明書作成をスキップ（既存証明書使用）")
                return None
                
        except Exception as e:
            print(f"⚠️ 自己署名証明書作成エラー: {e}")
            return None
    
    def perform_adhoc_signing(self):
        """アドホック署名の実行"""
        print(f"\\n🔏 アドホック署名を実行: {self.app_path.name}")
        
        try:
            # アドホック署名コマンド
            cmd = [
                'codesign',
                '--force',
                '--sign', '-',  # アドホック署名
                '--timestamp',
                '--options', 'runtime',
                '--deep',
                str(self.app_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ アドホック署名完了")
            self.signing_results['adhoc'] = True
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ アドホック署名失敗: {e}")
            if e.stderr:
                print(f"エラー詳細: {e.stderr}")
            self.signing_results['adhoc'] = False
            return False
    
    def perform_developer_id_signing(self, certificates):
        """Developer ID署名の実行"""
        if not certificates['developer_id']:
            print("⚠️ Developer ID証明書がありません")
            return False
            
        print(f"\\n🔐 Developer ID署名を実行: {self.app_path.name}")
        
        # 最初のDeveloper ID証明書を使用
        cert_line = certificates['developer_id'][0]
        
        # 証明書名を抽出
        match = re.search(r'"([^"]*Developer ID Application[^"]*)"', cert_line)
        if not match:
            print("❌ Developer ID証明書名の抽出に失敗")
            return False
            
        cert_name = match.group(1)
        print(f"使用する証明書: {cert_name}")
        
        try:
            # Developer ID署名コマンド
            cmd = [
                'codesign',
                '--force',
                '--sign', cert_name,
                '--timestamp',
                '--options', 'runtime',
                '--deep',
                str(self.app_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ Developer ID署名完了")
            self.signing_results['developer_id'] = True
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Developer ID署名失敗: {e}")
            if e.stderr:
                print(f"エラー詳細: {e.stderr}")
            self.signing_results['developer_id'] = False
            return False
    
    def perform_self_signed_certificate_signing(self, cert_name):
        """自己署名証明書による署名"""
        if not cert_name:
            print("⚠️ 自己署名証明書がありません")
            return False
            
        print(f"\\n🔖 自己署名証明書署名を実行: {self.app_path.name}")
        
        try:
            cmd = [
                'codesign',
                '--force',
                '--sign', cert_name,
                '--deep',
                str(self.app_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ 自己署名証明書署名完了")
            self.signing_results['self_signed'] = True
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 自己署名証明書署名失敗: {e}")
            if e.stderr:
                print(f"エラー詳細: {e.stderr}")
            self.signing_results['self_signed'] = False
            return False
    
    def verify_signature(self):
        """署名の検証"""
        print(f"\\n🔍 署名検証: {self.app_path.name}")
        
        try:
            # 署名検証コマンド
            cmd = ['codesign', '--verify', '--deep', '--strict', str(self.app_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ 署名検証成功")
            
            # 署名詳細表示
            detail_cmd = ['codesign', '--display', '--verbose=2', str(self.app_path)]
            detail_result = subprocess.run(detail_cmd, capture_output=True, text=True)
            
            if detail_result.stderr:
                print("\\n📋 署名詳細:")
                for line in detail_result.stderr.split('\\n'):
                    if line.strip():
                        print(f"  {line}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 署名検証失敗: {e}")
            return False
    
    def check_gatekeeper_compatibility(self):
        """Gatekeeper互換性確認"""
        print(f"\\n🛡️ Gatekeeper互換性確認: {self.app_path.name}")
        
        try:
            # spctlコマンドでGatekeeper評価
            cmd = ['spctl', '--assess', '--type', 'execute', str(self.app_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Gatekeeper互換性: OK")
                return True
            else:
                print("⚠️ Gatekeeper互換性: 問題あり")
                if result.stderr:
                    print(f"詳細: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️ Gatekeeper確認エラー: {e}")
            return False
    
    def comprehensive_code_signing(self):
        """包括的なコード署名プロセス"""
        print("🔐 包括的コード署名プロセス開始")
        print("=" * 60)
        
        # 1. 利用可能な証明書確認
        certificates = self.check_available_certificates()
        
        # 2. 署名方法の優先順位で実行
        signing_methods = [
            ("Developer ID署名", lambda: self.perform_developer_id_signing(certificates)),
            ("アドホック署名", self.perform_adhoc_signing),
        ]
        
        signing_success = False
        
        for method_name, method_func in signing_methods:
            print(f"\\n{'='*20} {method_name} {'='*20}")
            
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
        
        # 3. 署名検証
        if signing_success:
            print(f"\\n{'='*20} 署名検証 {'='*20}")
            verify_result = self.verify_signature()
            
            # 4. Gatekeeper互換性確認
            print(f"\\n{'='*20} Gatekeeper確認 {'='*20}")
            gatekeeper_result = self.check_gatekeeper_compatibility()
            
        # 5. 最終結果
        print(f"\\n📊 コード署名結果:")
        print("=" * 60)
        
        if signing_success:
            print(f"✅ コード署名: 成功")
            if verify_result:
                print(f"✅ 署名検証: 成功")
            else:
                print(f"⚠️ 署名検証: 問題あり")
                
            if gatekeeper_result:
                print(f"✅ Gatekeeper: 互換性OK")
            else:
                print(f"⚠️ Gatekeeper: 要注意")
        else:
            print(f"❌ コード署名: 失敗")
        
        return {
            'signing_success': signing_success,
            'verify_result': verify_result if signing_success else False,
            'gatekeeper_result': gatekeeper_result if signing_success else False,
            'signing_results': self.signing_results
        }

def main():
    """メイン実行関数"""
    app_path = "optimized_apps/RVC Voice Converter.app"
    
    if not Path(app_path).exists():
        print(f"❌ アプリバンドルが見つかりません: {app_path}")
        return False
    
    manager = CodeSigningManager(app_path)
    result = manager.comprehensive_code_signing()
    
    return result['signing_success']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)