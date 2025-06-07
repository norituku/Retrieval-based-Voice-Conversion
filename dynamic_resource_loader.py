
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
