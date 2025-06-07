#!/usr/bin/env python3
"""
大容量リソース（モデルファイル）の外部管理システム
アプリバンドル外での動的ロード
"""
import os
import json
import shutil
import hashlib
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional
import tempfile
import subprocess

class ModelResourceManager:
    """モデルリソースの外部管理クラス"""
    
    def __init__(self, app_support_dir: str = None):
        if app_support_dir is None:
            # macOS Application Support標準ディレクトリ
            home = Path.home()
            self.app_support_dir = home / "Library" / "Application Support" / "RVC Voice Converter"
        else:
            self.app_support_dir = Path(app_support_dir)
        
        self.models_dir = self.app_support_dir / "models"
        self.cache_dir = self.app_support_dir / "cache"
        self.config_file = self.app_support_dir / "model_config.json"
        self.manifest_file = self.app_support_dir / "resource_manifest.json"
        
        # ディレクトリの作成
        self.app_support_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.resource_manifest = self.load_or_create_manifest()
    
    def load_or_create_manifest(self) -> Dict:
        """リソースマニフェストの読み込みまたは作成"""
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ マニフェスト読み込みエラー: {e}")
        
        # デフォルトマニフェスト
        manifest = {
            "version": "1.0",
            "created": self._get_timestamp(),
            "models": {},
            "system_files": {},
            "total_size": 0,
            "last_updated": self._get_timestamp()
        }
        
        self.save_manifest(manifest)
        return manifest
    
    def _get_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def save_manifest(self, manifest: Dict = None):
        """マニフェストの保存"""
        if manifest is None:
            manifest = self.resource_manifest
        
        manifest["last_updated"] = self._get_timestamp()
        
        with open(self.manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """ファイルのハッシュ値計算"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def analyze_current_models(self, source_model_dir: Path) -> Dict:
        """現在のモデルディレクトリを分析"""
        print(f"🔍 モデルディレクトリ分析: {source_model_dir}")
        
        if not source_model_dir.exists():
            print(f"⚠️ モデルディレクトリが見つかりません: {source_model_dir}")
            return {}
        
        model_analysis = {
            "total_files": 0,
            "total_size": 0,
            "system_files": {},
            "model_files": {},
            "categorized": {
                "essential": [],      # 必須ファイル（hubert, rmvpe）
                "models": [],         # モデルファイル（.pth）  
                "indexes": [],        # インデックスファイル（.index）
                "configs": [],        # 設定ファイル（params.json）
                "others": []          # その他
            }
        }
        
        for file_path in source_model_dir.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                relative_path = file_path.relative_to(source_model_dir)
                
                file_info = {
                    "path": str(relative_path),
                    "full_path": str(file_path),
                    "size": size,
                    "size_mb": size / 1024 / 1024,
                    "hash": self.calculate_file_hash(file_path)
                }
                
                model_analysis["total_files"] += 1
                model_analysis["total_size"] += size
                
                # ファイル分類
                filename = file_path.name.lower()
                
                if filename in ['hubert_base.pt', 'rmvpe.pt']:
                    model_analysis["categorized"]["essential"].append(file_info)
                    model_analysis["system_files"][str(relative_path)] = file_info
                elif filename.endswith('.pth'):
                    model_analysis["categorized"]["models"].append(file_info)
                    model_analysis["model_files"][str(relative_path)] = file_info
                elif filename.endswith('.index'):
                    model_analysis["categorized"]["indexes"].append(file_info)
                    model_analysis["model_files"][str(relative_path)] = file_info
                elif filename == 'params.json':
                    model_analysis["categorized"]["configs"].append(file_info)
                    model_analysis["model_files"][str(relative_path)] = file_info
                else:
                    model_analysis["categorized"]["others"].append(file_info)
        
        # 分析結果の表示
        print(f"📊 分析結果:")
        print(f"  総ファイル数: {model_analysis['total_files']:,}")
        print(f"  総サイズ: {model_analysis['total_size'] / 1024**3:.2f} GB")
        print(f"  必須システムファイル: {len(model_analysis['categorized']['essential'])}")
        print(f"  モデルファイル: {len(model_analysis['categorized']['models'])}")
        print(f"  インデックスファイル: {len(model_analysis['categorized']['indexes'])}")
        print(f"  設定ファイル: {len(model_analysis['categorized']['configs'])}")
        print(f"  その他: {len(model_analysis['categorized']['others'])}")
        
        return model_analysis
    
    def create_migration_plan(self, model_analysis: Dict) -> Dict:
        """リソース移行計画の作成"""
        print("\n📋 リソース移行計画を作成中...")
        
        migration_plan = {
            "strategy": "external_resources",
            "bundle_resources": [],      # アプリバンドルに含める小さなファイル
            "external_resources": [],    # 外部配置する大きなファイル
            "total_bundle_size": 0,
            "total_external_size": 0,
            "size_threshold_mb": 10      # 10MB以上は外部配置
        }
        
        # サイズ閾値（MB）
        threshold = migration_plan["size_threshold_mb"] * 1024 * 1024
        
        # 全ファイルを分類
        all_files = []
        for category in model_analysis["categorized"].values():
            all_files.extend(category)
        
        for file_info in all_files:
            if file_info["size"] > threshold:
                migration_plan["external_resources"].append({
                    **file_info,
                    "target_location": "application_support",
                    "load_strategy": "dynamic"
                })
                migration_plan["total_external_size"] += file_info["size"]
            else:
                migration_plan["bundle_resources"].append({
                    **file_info,
                    "target_location": "app_bundle",
                    "load_strategy": "static"
                })
                migration_plan["total_bundle_size"] += file_info["size"]
        
        # 計画の表示
        print(f"📦 アプリバンドル内リソース:")
        print(f"  ファイル数: {len(migration_plan['bundle_resources'])}")
        print(f"  総サイズ: {migration_plan['total_bundle_size'] / 1024**2:.1f} MB")
        
        print(f"🗂️ 外部リソース:")
        print(f"  ファイル数: {len(migration_plan['external_resources'])}")
        print(f"  総サイズ: {migration_plan['total_external_size'] / 1024**3:.2f} GB")
        
        return migration_plan
    
    def execute_migration(self, source_model_dir: Path, migration_plan: Dict) -> bool:
        """リソース移行の実行"""
        print("\n🚚 リソース移行を開始...")
        
        try:
            # 外部リソースのコピー
            print("📁 外部リソースをApplication Supportにコピー中...")
            
            for resource in migration_plan["external_resources"]:
                source_path = Path(resource["full_path"])
                target_path = self.models_dir / resource["path"]
                
                # ターゲットディレクトリの作成
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # ファイルコピー
                if source_path.exists():
                    shutil.copy2(source_path, target_path)
                    print(f"  ✅ {resource['path']} ({resource['size_mb']:.1f} MB)")
                else:
                    print(f"  ❌ {resource['path']} - ソースファイルが見つかりません")
                    return False
            
            # バンドルリソース用の設定作成
            bundle_config = {
                "files": migration_plan["bundle_resources"],
                "total_size": migration_plan["total_bundle_size"],
                "instructions": "これらのファイルはNuitkaビルド時に--include-data-dirで含める"
            }
            
            bundle_config_path = self.app_support_dir / "bundle_resources.json"
            with open(bundle_config_path, 'w', encoding='utf-8') as f:
                json.dump(bundle_config, f, indent=2, ensure_ascii=False)
            
            # マニフェストの更新
            self.resource_manifest["models"].update({
                f["path"]: {
                    "size": f["size"],
                    "hash": f["hash"],
                    "location": "external",
                    "migrated": True
                } for f in migration_plan["external_resources"]
            })
            
            self.resource_manifest["total_size"] = migration_plan["total_external_size"]
            self.save_manifest()
            
            print(f"✅ リソース移行完了")
            print(f"   外部配置: {len(migration_plan['external_resources'])} ファイル")
            print(f"   Application Support: {self.app_support_dir}")
            
            return True
            
        except Exception as e:
            print(f"❌ リソース移行エラー: {e}")
            return False
    
    def create_resource_loader(self) -> str:
        """動的リソースローダーのコード生成"""
        loader_code = '''
"""
動的リソースローダー
Application SupportからモデルファイルをロードするためのUtility
"""
import os
from pathlib import Path
import json

class DynamicResourceLoader:
    """動的リソースローダークラス"""
    
    def __init__(self):
        home = Path.home()
        self.app_support_dir = home / "Library" / "Application Support" / "RVC Voice Converter"
        self.models_dir = self.app_support_dir / "models"
        self.manifest_file = self.app_support_dir / "resource_manifest.json"
        
        self.manifest = self.load_manifest()
    
    def load_manifest(self):
        """リソースマニフェストの読み込み"""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_model_path(self, model_name: str) -> Path:
        """モデルファイルのパスを取得"""
        # まずApplication Supportを確認
        model_path = self.models_dir / model_name
        if model_path.exists():
            return model_path
        
        # フォールバック: 相対パス検索
        for root_path in [self.models_dir, Path("model_dir"), Path(".")]:
            for ext in [".pth", ".pt", ".index"]:
                candidate = root_path / f"{model_name}{ext}"
                if candidate.exists():
                    return candidate
        
        raise FileNotFoundError(f"Model file not found: {model_name}")
    
    def get_system_file_path(self, filename: str) -> Path:
        """システムファイル（hubert, rmvpe）のパスを取得"""
        system_path = self.models_dir / filename
        if system_path.exists():
            return system_path
        
        # フォールバック
        fallback_path = Path("model_dir") / filename
        if fallback_path.exists():
            return fallback_path
            
        raise FileNotFoundError(f"System file not found: {filename}")
    
    def ensure_resources_available(self) -> bool:
        """必須リソースの可用性確認"""
        essential_files = ["hubert_base.pt", "rmvpe.pt"]
        
        for filename in essential_files:
            try:
                self.get_system_file_path(filename)
            except FileNotFoundError:
                return False
        
        return True

# グローバルローダーインスタンス
resource_loader = DynamicResourceLoader()
'''
        
        loader_path = Path("dynamic_resource_loader.py")
        with open(loader_path, 'w', encoding='utf-8') as f:
            f.write(loader_code)
        
        print(f"📝 動的リソースローダーを生成: {loader_path}")
        return str(loader_path)
    
    def generate_nuitka_include_commands(self, migration_plan: Dict) -> List[str]:
        """Nuitka用include-data-dirコマンドの生成"""
        commands = []
        
        # バンドルリソース用のコマンド
        bundle_dirs = set()
        for resource in migration_plan["bundle_resources"]:
            dir_path = Path(resource["path"]).parent
            if str(dir_path) != ".":
                bundle_dirs.add(str(dir_path))
        
        for dir_path in sorted(bundle_dirs):
            commands.append(f"--include-data-dir=model_dir/{dir_path}=model_dir/{dir_path}")
        
        # 個別ファイル
        for resource in migration_plan["bundle_resources"]:
            if Path(resource["path"]).parent == Path("."):
                commands.append(f"--include-data-file=model_dir/{resource['path']}=model_dir/{resource['path']}")
        
        return commands

def main():
    """メイン実行関数"""
    print("🚀 RVC外部リソース管理システム")
    print("=" * 60)
    
    # マネージャー初期化
    manager = ModelResourceManager()
    
    # 現在のモデルディレクトリ分析
    source_dir = Path("model_dir")
    if not source_dir.exists():
        print(f"❌ モデルディレクトリが見つかりません: {source_dir}")
        return False
    
    # 分析実行
    model_analysis = manager.analyze_current_models(source_dir)
    
    # 移行計画作成
    migration_plan = manager.create_migration_plan(model_analysis)
    
    # 移行実行
    success = manager.execute_migration(source_dir, migration_plan)
    
    if success:
        # リソースローダー生成
        loader_path = manager.create_resource_loader()
        
        # Nuitkaコマンド生成
        include_commands = manager.generate_nuitka_include_commands(migration_plan)
        
        print(f"\n🔧 Nuitka Include Commands:")
        for cmd in include_commands:
            print(f"  {cmd}")
        
        # 設定保存
        nuitka_settings = {
            "include_commands": include_commands,
            "external_resources_dir": str(manager.app_support_dir),
            "bundle_size_mb": migration_plan["total_bundle_size"] / 1024**2,
            "external_size_gb": migration_plan["total_external_size"] / 1024**3
        }
        
        settings_path = Path("resource_optimization_settings.json")
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(nuitka_settings, f, indent=2, ensure_ascii=False)
        
        print(f"✅ リソース最適化設定を保存: {settings_path}")
        
        return True
    else:
        print("❌ リソース移行に失敗しました")
        return False

if __name__ == "__main__":
    main()