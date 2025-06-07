#!/usr/bin/env python3
"""
最適化されたInfo.plistの作成とアプリバンドル統合
macOSアプリケーション標準に準拠した完全なメタデータ
"""
import plistlib
import shutil
from pathlib import Path
import subprocess
import sys

class InfoPlistOptimizer:
    """Info.plist最適化クラス"""
    
    def __init__(self, source_app_path, output_dir="optimized_apps"):
        self.source_app = Path(source_app_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # アプリ名から出力パスを決定
        self.app_name = "RVC Voice Converter"
        self.optimized_app = self.output_dir / f"{self.app_name}.app"
        
        # アイコンパス
        self.icon_path = Path("app_icons/rvc_icon.icns")
    
    def create_optimized_info_plist(self):
        """最適化されたInfo.plistの作成"""
        print("📝 最適化されたInfo.plistを作成中...")
        
        # 完全なInfo.plist辞書
        info_plist = {
            # === 基本アプリケーション情報 ===
            'CFBundleDisplayName': 'RVC Voice Converter',
            'CFBundleName': 'RVC Voice Converter',
            'CFBundleExecutable': 'gui_dark_mode_enhanced',
            'CFBundleIdentifier': 'com.rvc.voiceconverter',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleInfoDictionaryVersion': '6.0',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': 'RVC1',
            
            # === アイコンとUI ===
            'CFBundleIconFile': 'rvc_icon.icns',
            'CFBundleIconName': 'rvc_icon',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.14.0',  # macOS Mojave以降
            
            # === アプリケーション分類 ===
            'LSApplicationCategoryType': 'public.app-category.music',
            'NSHumanReadableCopyright': '© 2024 RVC Voice Converter. All rights reserved.',
            
            # === ファイル関連付け ===
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Audio File',
                    'CFBundleTypeRole': 'Editor',
                    'CFBundleTypeIconFile': 'rvc_icon.icns',
                    'LSItemContentTypes': [
                        'com.microsoft.waveform-audio',
                        'public.mp3',
                        'com.apple.m4a-audio',
                        'org.xiph.flac',
                        'org.xiph.ogg-audio'
                    ],
                    'LSHandlerRank': 'Alternate'
                }
            ],
            
            # === UTI（Uniform Type Identifier）エクスポート ===
            'UTExportedTypeDeclarations': [
                {
                    'UTTypeIdentifier': 'com.rvc.voiceconverter.project',
                    'UTTypeDescription': 'RVC Voice Conversion Project',
                    'UTTypeIconFile': 'rvc_icon.icns',
                    'UTTypeConformsTo': ['public.data'],
                    'UTTypeTagSpecification': {
                        'public.filename-extension': ['rvcproj']
                    }
                }
            ],
            
            # === セキュリティとプライバシー ===
            'NSMicrophoneUsageDescription': 'RVC Voice Converterは音声ファイルの変換処理のためにマイクアクセスを要求する場合があります。',
            'NSDesktopFolderUsageDescription': 'RVC Voice Converterは音声ファイルの読み書きのためにデスクトップフォルダアクセスが必要です。',
            'NSDocumentsFolderUsageDescription': 'RVC Voice Converterは音声ファイルの読み書きのためにドキュメントフォルダアクセスが必要です。',
            'NSDownloadsFolderUsageDescription': 'RVC Voice Converterは音声ファイルの読み書きのためにダウンロードフォルダアクセスが必要です。',
            
            # === ネットワークとセキュリティ ===
            'NSAppTransportSecurity': {
                'NSAllowsArbitraryLoads': False,
                'NSExceptionDomains': {}
            },
            
            # === 追加メタデータ ===
            'CFBundleGetInfoString': 'RVC Voice Converter 1.0.0, © 2024 RVC Voice Converter.',
            'NSPrincipalClass': 'NSApplication',
            'LSMultipleInstancesProhibited': False,
            
            # === パフォーマンス最適化 ===
            'LSRequiresNativeExecution': True,
            'LSArchitecturePriority': ['arm64', 'x86_64'],
            
            # === デバッグと開発 ===
            'ITSAppUsesNonExemptEncryption': False,
            'LSSupportsOpeningDocumentsInPlace': False,
            
            # === UI設定 ===
            'NSSupportsAutomaticGraphicsSwitching': True,
            'CSResourcesFileMapped': True,
        }
        
        return info_plist
    
    def copy_and_optimize_app_bundle(self):
        """アプリバンドルのコピーと最適化"""
        print(f"📂 アプリバンドルを最適化: {self.source_app} → {self.optimized_app}")
        
        # 既存の最適化アプリを削除
        if self.optimized_app.exists():
            shutil.rmtree(self.optimized_app)
        
        # ソースアプリをコピー
        shutil.copytree(self.source_app, self.optimized_app)
        
        print(f"✅ アプリバンドルコピー完了")
        return True
    
    def integrate_optimized_info_plist(self):
        """最適化されたInfo.plistの統合"""
        info_plist_data = self.create_optimized_info_plist()
        info_plist_path = self.optimized_app / "Contents" / "Info.plist"
        
        # Info.plistを書き込み
        with open(info_plist_path, 'wb') as f:
            plistlib.dump(info_plist_data, f)
        
        print(f"✅ 最適化されたInfo.plistを統合: {info_plist_path}")
        return True
    
    def integrate_app_icon(self):
        """アプリアイコンの統合"""
        if not self.icon_path.exists():
            print(f"⚠️ アイコンファイルが見つかりません: {self.icon_path}")
            return False
        
        # Resourcesディレクトリにアイコンをコピー
        resources_dir = self.optimized_app / "Contents" / "Resources"
        resources_dir.mkdir(exist_ok=True)
        
        target_icon_path = resources_dir / "rvc_icon.icns"
        shutil.copy2(self.icon_path, target_icon_path)
        
        print(f"✅ アプリアイコンを統合: {target_icon_path}")
        return True
    
    def update_permissions(self):
        """アプリバンドルの適切な権限設定"""
        print("🔒 アプリバンドル権限を最適化中...")
        
        # 実行ファイルに実行権限を付与
        executable_path = self.optimized_app / "Contents" / "MacOS" / "gui_dark_mode_enhanced"
        if executable_path.exists():
            executable_path.chmod(0o755)
            print(f"✅ 実行権限設定: {executable_path}")
        
        # .soファイルに適切な権限を設定
        macos_dir = self.optimized_app / "Contents" / "MacOS"
        for so_file in macos_dir.glob("*.so"):
            so_file.chmod(0o644)
        
        # .dylibファイルに適切な権限を設定
        for dylib_file in macos_dir.glob("*.dylib"):
            dylib_file.chmod(0o644)
        
        print("✅ ライブラリ権限設定完了")
        return True
    
    def verify_app_bundle(self):
        """アプリバンドルの検証"""
        print("🔍 アプリバンドル検証中...")
        
        required_items = [
            "Contents/Info.plist",
            "Contents/MacOS/gui_dark_mode_enhanced",
            "Contents/Resources/rvc_icon.icns",
            "Contents/_CodeSignature"
        ]
        
        verification_results = {}
        
        for item in required_items:
            item_path = self.optimized_app / item
            exists = item_path.exists()
            verification_results[item] = exists
            
            status = "✅" if exists else "❌"
            print(f"  {status} {item}")
        
        # アプリサイズ確認
        try:
            result = subprocess.run(['du', '-sh', str(self.optimized_app)], 
                                  capture_output=True, text=True, check=True)
            app_size = result.stdout.split()[0]
            print(f"  📊 アプリサイズ: {app_size}")
        except:
            print(f"  📊 アプリサイズ: 計測失敗")
        
        success_count = sum(verification_results.values())
        total_count = len(verification_results)
        
        print(f"\n📋 検証結果: {success_count}/{total_count} 成功")
        
        return success_count == total_count
    
    def optimize_complete_app_bundle(self):
        """完全なアプリバンドル最適化プロセス"""
        print("🚀 完全なmacOSアプリバンドル最適化開始")
        print("=" * 60)
        
        steps = [
            ("アプリバンドルコピー", self.copy_and_optimize_app_bundle),
            ("Info.plist最適化", self.integrate_optimized_info_plist),
            ("アプリアイコン統合", self.integrate_app_icon),
            ("権限設定最適化", self.update_permissions),
            ("アプリバンドル検証", self.verify_app_bundle),
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            print(f"\n🔧 {step_name}中...")
            try:
                result = step_func()
                results[step_name] = result
                
                if result:
                    print(f"✅ {step_name}: 成功")
                else:
                    print(f"❌ {step_name}: 失敗")
                    
            except Exception as e:
                print(f"❌ {step_name}: エラー - {e}")
                results[step_name] = False
        
        # 最終結果
        print(f"\n📊 アプリバンドル最適化結果:")
        print("=" * 60)
        
        success_count = sum(results.values())
        total_count = len(results)
        
        for step_name, result in results.items():
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"  {step_name:20}: {status}")
        
        print(f"\n総合結果: {success_count}/{total_count} 成功")
        
        if success_count == total_count:
            print(f"🎉 完全なmacOSアプリバンドル最適化完了！")
            print(f"📱 最適化アプリ: {self.optimized_app}")
        else:
            print(f"⚠️ 一部ステップが失敗しました")
        
        return {
            'success': success_count == total_count,
            'app_path': self.optimized_app,
            'results': results
        }

def main():
    """メイン実行関数"""
    # 最も完成度の高いアプリバンドルを選択
    source_app = "dist_lightweight_fixed/gui_dark_mode_enhanced.app"
    
    if not Path(source_app).exists():
        print(f"❌ ソースアプリが見つかりません: {source_app}")
        return False
    
    optimizer = InfoPlistOptimizer(source_app)
    result = optimizer.optimize_complete_app_bundle()
    
    return result['success']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)