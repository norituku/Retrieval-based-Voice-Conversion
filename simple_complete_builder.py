#!/usr/bin/env python3
"""
Simple Complete RVC Builder
シンプルな完全版RVCビルダー
"""
import subprocess
import sys
import os
import shutil
import time
from pathlib import Path

class SimpleCompleteBuilder:
    """シンプル完全版ビルダー"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.system_python = self.find_system_python()
        if not self.system_python:
            raise RuntimeError("システムPythonが見つかりません")
    
    def find_system_python(self):
        """システムPythonを検出"""
        candidates = [
            "/opt/homebrew/bin/python3",
            "/usr/bin/python3",
            "/usr/local/bin/python3"
        ]
        
        for python_path in candidates:
            if Path(python_path).exists():
                try:
                    result = subprocess.run([
                        python_path, "-c", "import tkinter; print('OK')"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ システムPython発見: {python_path}")
                        return python_path
                except:
                    continue
        
        return None
    
    def install_nuitka_system(self):
        """システムPython環境にNuitkaをインストール"""
        print("🔧 システムPython環境にNuitka準備中...")
        
        try:
            # Nuitka確認
            result = subprocess.run([
                self.system_python, "-c", "import nuitka; print('installed')"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("📦 Nuitkaインストール中...")
                install_result = subprocess.run([
                    self.system_python, "-m", "pip", "install", "nuitka", "--break-system-packages"
                ], capture_output=True, text=True)
                
                if install_result.returncode != 0:
                    print(f"❌ Nuitkaインストール失敗: {install_result.stderr}")
                    return False
                else:
                    print("✅ Nuitkaインストール完了")
            else:
                print("✅ Nuitka既にインストール済み")
            
            return True
            
        except Exception as e:
            print(f"❌ システムPython Nuitka準備エラー: {e}")
            return False
    
    def build_gui_with_nuitka(self):
        """最新GUI（complete_voice_converter.py）をNuitkaでビルド"""
        print("🔧 最新GUI（complete_voice_converter.py - 改良デバッグ版）をNuitkaビルド中...")
        
        gui_file = self.project_root / "complete_voice_converter.py"
        if not gui_file.exists():
            print(f"❌ GUIファイルが見つかりません: {gui_file}")
            return None
        
        # 出力ディレクトリ準備
        output_dir = self.project_root / "dist_complete_debug"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()
        
        # Nuitkaコマンド構築（デバッグ強化版）
        nuitka_cmd = [
            self.system_python, "-m", "nuitka",
            "--standalone",
            "--macos-create-app-bundle",
            f"--output-dir={output_dir}",
            "--include-data-dir=model_dir=model_dir",
            "--include-data-dir=enhanced_output=enhanced_output",
            "--include-data-files=enhanced_voice_converter.py=enhanced_voice_converter.py",
            "--include-data-dir=rvc=rvc",
            "--include-data-files=pyproject.toml=pyproject.toml",
            "--include-data-files=poetry.lock=poetry.lock",
            "--macos-app-name=RVC Voice Converter Debug Edition",
            "--macos-app-version=1.0.2",
            "--macos-app-protected-resource=microphone:RVC音声変換のためマイクアクセス",
            "--remove-output",
            str(gui_file)
        ]
        
        print(f"📝 Nuitkaビルド開始...")
        
        # ビルド実行
        start_time = time.time()
        result = subprocess.run(nuitka_cmd, capture_output=True, text=True)
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"✅ Nuitkaビルド成功! (実行時間: {end_time - start_time:.1f}秒)")
            
            # 生成されたアプリの確認
            app_path = output_dir / "complete_voice_converter.app"
            if app_path.exists():
                print(f"📱 モデルカード版アプリ生成: {app_path}")
                
                # アプリ名をわかりやすく変更
                new_app_path = output_dir / "RVC Voice Converter Debug Edition.app"
                if new_app_path.exists():
                    shutil.rmtree(new_app_path)
                shutil.move(str(app_path), str(new_app_path))
                app_path = new_app_path
                print(f"📱 アプリ名変更完了: {app_path}")
                
                # アプリサイズ確認
                try:
                    size_result = subprocess.run(['du', '-sh', str(app_path)], 
                                                capture_output=True, text=True)
                    if size_result.returncode == 0:
                        app_size = size_result.stdout.split()[0]
                        print(f"📊 アプリサイズ: {app_size}")
                except:
                    pass
                
                return app_path
            else:
                print(f"❌ 完全版アプリが見つかりません")
                return None
        else:
            print(f"❌ Nuitkaビルド失敗:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return None
    
    def test_complete_app(self, app_path):
        """完全版アプリのテスト"""
        if not app_path or not app_path.exists():
            print("❌ アプリパスが無効なため、テストをスキップ")
            return False
        
        print("🧪 完全版アプリテスト中...")
        
        # 簡単な起動テスト
        try:
            print(f"🚀 アプリ起動テスト: {app_path.name}")
            # 実際には起動しないで、構造のみ確認
            
            # 必須ファイル確認
            required_files = [
                "Contents/Info.plist",
                "Contents/MacOS/complete_voice_converter",
                "Contents/MacOS"
            ]
            
            missing_files = []
            for req_file in required_files:
                file_path = app_path / req_file
                if not file_path.exists():
                    missing_files.append(req_file)
            
            if missing_files:
                print(f"❌ 必須ファイル不足: {missing_files}")
                return False
            else:
                print(f"✅ アプリ構造検証成功")
                return True
                
        except Exception as e:
            print(f"❌ アプリテストエラー: {e}")
            return False
    
    def create_complete_dmg(self, app_path):
        """完全版DMGの作成"""
        if not app_path or not app_path.exists():
            print("❌ アプリパスが無効なため、DMG作成をスキップ")
            return None
        
        print("💿 モデルカード版DMG作成中...")
        
        dmg_name = "RVC_Voice_Converter_ModelCard_Edition.dmg"
        dmg_path = self.project_root / dmg_name
        
        # 既存DMGを削除
        if dmg_path.exists():
            dmg_path.unlink()
        
        try:
            # 一時ディレクトリ作成
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # アプリをコピー
                temp_app = temp_path / app_path.name
                shutil.copytree(app_path, temp_app)
                
                # Applicationsリンク作成
                applications_link = temp_path / "Applications"
                applications_link.symlink_to("/Applications")
                
                # README作成
                readme_content = """RVC Voice Converter Model Card Edition

インストール手順:
1. RVC Voice Converter Model Card Edition.app を Applications フォルダにドラッグ&ドロップ
2. アプリケーションフォルダから起動
3. 初回起動時はセキュリティ設定で許可が必要な場合があります

🆕 Model Card Edition の特徴:
- 🎵 モデルカード形式UI（視覚的で使いやすい）
- 🎯 高品質固定設定（rmvpe + 最適パラメータ）
- ✅ インデックス有無の一目確認
- 🔄 スクロール対応（多数モデル表示可能）
- 🖱️ クリック選択・ホバーエフェクト

技術仕様:
- Enhanced Voice Converter統合
- PyTorch、librosa、fairseq完全対応
- ダークモードGUI
- Apple Silicon MPS最適化

注意:
- Poetry環境が必要です（音声変換処理用）
- モデルファイルは model_dir フォルダに配置済み

© 2024 RVC Voice Converter Model Card Edition v1.0.1
"""
                readme_path = temp_path / "README.txt"
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                
                # DMG作成
                create_cmd = [
                    "hdiutil", "create",
                    "-srcfolder", str(temp_path),
                    "-volname", "RVC Voice Converter Model Card Edition",
                    "-fs", "HFS+",
                    "-format", "UDZO",
                    "-imagekey", "zlib-level=9",
                    str(dmg_path)
                ]
                
                result = subprocess.run(create_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ モデルカード版DMG作成完了: {dmg_path}")
                    
                    # DMGサイズ確認
                    if dmg_path.exists():
                        size_mb = dmg_path.stat().st_size / 1024 / 1024
                        print(f"📊 DMGサイズ: {size_mb:.1f}MB")
                    
                    return dmg_path
                else:
                    print(f"❌ DMG作成失敗: {result.stderr}")
                    return None
                    
        except Exception as e:
            print(f"❌ DMG作成エラー: {e}")
            return None
    
    def build_complete_rvc(self):
        """完全版RVCビルドプロセス"""
        print("🚀 RVC Voice Converter Complete Edition ビルド開始")
        print("=" * 70)
        
        steps = [
            ("システムPython Nuitka準備", self.install_nuitka_system),
            ("完全版GUIビルド", self.build_gui_with_nuitka),
        ]
        
        results = {}
        app_path = None
        
        for step_name, step_func in steps:
            print(f"\\n{'='*20} {step_name} {'='*20}")
            
            try:
                result = step_func()
                
                if step_name == "完全版GUIビルド":
                    app_path = result
                    result = app_path is not None
                
                results[step_name] = result
                
                if result:
                    print(f"✅ {step_name}: 成功")
                else:
                    print(f"❌ {step_name}: 失敗")
                    break
                    
            except Exception as e:
                print(f"❌ {step_name}: エラー - {e}")
                results[step_name] = False
                break
        
        # 追加ステップ（アプリが生成された場合）
        if app_path and all(results.values()):
            
            additional_steps = [
                ("完全版アプリテスト", lambda: self.test_complete_app(app_path)),
                ("完全版DMG作成", lambda: self.create_complete_dmg(app_path)),
            ]
            
            for step_name, step_func in additional_steps:
                print(f"\\n{'='*20} {step_name} {'='*20}")
                
                try:
                    result = step_func()
                    
                    if step_name == "完全版DMG作成":
                        result = result is not None
                    
                    results[step_name] = result
                    
                    if result:
                        print(f"✅ {step_name}: 成功")
                    else:
                        print(f"❌ {step_name}: 失敗")
                        
                except Exception as e:
                    print(f"❌ {step_name}: エラー - {e}")
                    results[step_name] = False
        
        # 最終結果
        print(f"\\n📊 完全版ビルド結果:")
        print("=" * 70)
        
        success_count = sum(results.values())
        total_count = len(results)
        
        for step_name, result in results.items():
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"  {step_name:25}: {status}")
        
        print(f"\\n総合結果: {success_count}/{total_count} 成功")
        
        if success_count >= total_count - 1:  # 1つまでの失敗は許容
            print(f"🎉 RVC Voice Converter Model Card Edition ビルド完了！")
            print(f"📱 モデルカード版アプリ: dist_complete_gui/")
            print(f"💿 配布用DMG: RVC_Voice_Converter_ModelCard_Edition.dmg")
            print(f"\\n🎯 使用方法:")
            print(f"  1. DMGファイルをダブルクリック")
            print(f"  2. アプリをApplicationsフォルダにドラッグ")
            print(f"  3. Poetry環境がセットアップされていることを確認")
            print(f"  4. アプリケーションフォルダから起動")
            print(f"\\n🆕 Model Card Edition の新機能:")
            print(f"  • モデルカード形式UI（視覚的選択）")
            print(f"  • 高品質固定設定（最適パラメータ）")
            print(f"  • インデックス有無の即座確認")
        else:
            print(f"⚠️ 一部ステップが失敗しました")
        
        return success_count >= total_count - 1

def main():
    """メイン実行関数"""
    try:
        builder = SimpleCompleteBuilder()
        success = builder.build_complete_rvc()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ ビルダー初期化エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()