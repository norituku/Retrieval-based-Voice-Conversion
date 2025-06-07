#!/usr/bin/env python3
"""
設定管理システム - 構造化されたJSON設定ファイル管理
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class SettingsManager:
    """
    アプリケーション設定の一元管理クラス
    JSON構造の最適化とプリセット機能を提供
    """
    
    # デフォルト設定スキーマ
    DEFAULT_SETTINGS = {
        "version": "1.0.0",
        "app_settings": {
            "theme": "dark",
            "window_size": {
                "width": 900,
                "height": 500,
                "remember_size": True
            },
            "window_position": {
                "x": None,
                "y": None,
                "remember_position": True
            },
            "ui_preferences": {
                "show_tooltips": True,
                "auto_scroll_logs": True,
                "compact_mode": False
            },
            "recent_files": {
                "input_files": [],
                "output_directories": [],
                "max_recent": 10
            }
        },
        "audio_settings": {
            "default_params": {
                "pitch": 0,
                "f0_method": "rmvpe",
                "index_rate": 1.0,
                "filter_radius": 3,
                "rms_mix_rate": 0.25,
                "protect": 0.33,
                "hop_length": 128,
                "split_audio": False,
                "f0_autotune": False,
                "formant_shift": 0
            },
            "presets": [
                {
                    "name": "高品質（推奨）",
                    "description": "最高品質の変換設定",
                    "params": {
                        "pitch": 0,
                        "f0_method": "rmvpe",
                        "index_rate": 1.0,
                        "filter_radius": 3,
                        "rms_mix_rate": 0.25,
                        "protect": 0.33
                    },
                    "is_default": True
                },
                {
                    "name": "高速変換",
                    "description": "処理速度を重視した設定",
                    "params": {
                        "pitch": 0,
                        "f0_method": "harvest",
                        "index_rate": 0.8,
                        "filter_radius": 2,
                        "rms_mix_rate": 0.2,
                        "protect": 0.25
                    },
                    "is_default": False
                },
                {
                    "name": "ボーカル専用",
                    "description": "歌声変換に最適化",
                    "params": {
                        "pitch": 0,
                        "f0_method": "mangio-crepe",
                        "index_rate": 1.0,
                        "filter_radius": 3,
                        "rms_mix_rate": 0.3,
                        "protect": 0.4
                    },
                    "is_default": False
                }
            ],
            "f0_methods": [
                {"name": "rmvpe", "description": "最高品質（推奨）", "quality": 5, "speed": 3},
                {"name": "mangio-crepe", "description": "高品質（歌声向け）", "quality": 5, "speed": 2},
                {"name": "crepe", "description": "高品質", "quality": 4, "speed": 2},
                {"name": "harvest", "description": "高速", "quality": 3, "speed": 5},
                {"name": "dio", "description": "最高速", "quality": 2, "speed": 5}
            ]
        },
        "paths": {
            "model_directory": "",
            "default_output_directory": "",
            "hubert_model_path": "",
            "last_input_directory": "",
            "last_output_directory": ""
        },
        "advanced": {
            "performance": {
                "max_concurrent_conversions": 1,
                "memory_optimization": True,
                "gpu_acceleration": "auto"
            },
            "logging": {
                "level": "INFO",
                "max_log_files": 5,
                "max_log_size_mb": 10,
                "enable_debug": False
            },
            "experimental": {
                "enable_batch_processing": False,
                "enable_real_time_preview": False,
                "auto_backup_settings": True
            }
        },
        "metadata": {
            "created_date": None,
            "last_modified": None,
            "app_version": "1.0.0",
            "settings_migrations": []
        }
    }
    
    def __init__(self, settings_file: str, create_backup: bool = True):
        """
        設定管理システムの初期化
        
        Args:
            settings_file: 設定ファイルのパス
            create_backup: バックアップファイルを作成するか
        """
        self.settings_file = Path(settings_file)
        self.backup_file = self.settings_file.with_suffix('.json.backup')
        self.create_backup = create_backup
        
        # 設定データ
        self.settings = {}
        
        # 設定ファイルディレクトリを作成
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 設定を読み込み
        self.load_settings()
        
        # ロギング設定
        self._setup_logging()
    
    def _setup_logging(self):
        """ロギングシステムの設定"""
        log_level = self.get('advanced.logging.level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def load_settings(self) -> bool:
        """
        設定ファイルの読み込み
        
        Returns:
            読み込み成功の可否
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # スキーマ検証とマイグレーション
                self.settings = self._migrate_settings(loaded_settings)
                logging.info(f"Settings loaded from {self.settings_file}")
                return True
            else:
                # デフォルト設定を使用
                self.settings = self._create_default_settings()
                self.save_settings()
                logging.info("Default settings created")
                return True
                
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")
            # バックアップからの復元を試行
            if self._restore_from_backup():
                return True
            
            # 最後の手段としてデフォルト設定を使用
            self.settings = self._create_default_settings()
            return False
    
    def save_settings(self) -> bool:
        """
        設定ファイルの保存
        
        Returns:
            保存成功の可否
        """
        try:
            # バックアップの作成
            if self.create_backup and self.settings_file.exists():
                self._create_backup()
            
            # メタデータの更新
            self.settings['metadata']['last_modified'] = datetime.now().isoformat()
            
            # 設定ファイルの保存
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Settings saved to {self.settings_file}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        設定値の取得（ドット記法対応）
        
        Args:
            key: 設定キー（例: "app_settings.theme"）
            default: デフォルト値
            
        Returns:
            設定値
        """
        try:
            keys = key.split('.')
            value = self.settings
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        設定値の設定（ドット記法対応）
        
        Args:
            key: 設定キー
            value: 設定値
            
        Returns:
            設定成功の可否
        """
        try:
            keys = key.split('.')
            target = self.settings
            
            # 最後のキー以外まで辿る
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            
            # 値を設定
            target[keys[-1]] = value
            return True
            
        except Exception as e:
            logging.error(f"Failed to set setting {key}: {e}")
            return False
    
    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """
        プリセットの取得
        
        Args:
            name: プリセット名
            
        Returns:
            プリセット設定またはNone
        """
        presets = self.get('audio_settings.presets', [])
        for preset in presets:
            if preset.get('name') == name:
                return preset
        return None
    
    def get_default_preset(self) -> Optional[Dict[str, Any]]:
        """
        デフォルトプリセットの取得
        
        Returns:
            デフォルトプリセットまたはNone
        """
        presets = self.get('audio_settings.presets', [])
        for preset in presets:
            if preset.get('is_default', False):
                return preset
        return presets[0] if presets else None
    
    def add_preset(self, name: str, description: str, params: Dict[str, Any], 
                   is_default: bool = False) -> bool:
        """
        プリセットの追加
        
        Args:
            name: プリセット名
            description: プリセット説明
            params: パラメータ
            is_default: デフォルトプリセットにするか
            
        Returns:
            追加成功の可否
        """
        try:
            presets = self.get('audio_settings.presets', [])
            
            # 既存プリセットのチェック
            for preset in presets:
                if preset.get('name') == name:
                    logging.warning(f"Preset '{name}' already exists")
                    return False
            
            # デフォルトプリセットの更新
            if is_default:
                for preset in presets:
                    preset['is_default'] = False
            
            # 新しいプリセットを追加
            new_preset = {
                'name': name,
                'description': description,
                'params': params,
                'is_default': is_default
            }
            presets.append(new_preset)
            
            self.set('audio_settings.presets', presets)
            return True
            
        except Exception as e:
            logging.error(f"Failed to add preset '{name}': {e}")
            return False
    
    def remove_preset(self, name: str) -> bool:
        """
        プリセットの削除
        
        Args:
            name: プリセット名
            
        Returns:
            削除成功の可否
        """
        try:
            presets = self.get('audio_settings.presets', [])
            
            # プリセットを探して削除
            for i, preset in enumerate(presets):
                if preset.get('name') == name:
                    presets.pop(i)
                    self.set('audio_settings.presets', presets)
                    logging.info(f"Preset '{name}' removed")
                    return True
            
            logging.warning(f"Preset '{name}' not found")
            return False
            
        except Exception as e:
            logging.error(f"Failed to remove preset '{name}': {e}")
            return False
    
    def export_presets(self, export_path: str) -> bool:
        """
        プリセットのエクスポート
        
        Args:
            export_path: エクスポート先ファイルパス
            
        Returns:
            エクスポート成功の可否
        """
        try:
            presets = self.get('audio_settings.presets', [])
            export_data = {
                'version': self.get('version'),
                'export_date': datetime.now().isoformat(),
                'presets': presets
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Presets exported to {export_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to export presets: {e}")
            return False
    
    def import_presets(self, import_path: str, merge: bool = True) -> bool:
        """
        プリセットのインポート
        
        Args:
            import_path: インポート元ファイルパス
            merge: 既存のプリセットとマージするか
            
        Returns:
            インポート成功の可否
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_presets = import_data.get('presets', [])
            if not imported_presets:
                logging.warning("No presets found in import file")
                return False
            
            if merge:
                current_presets = self.get('audio_settings.presets', [])
                
                # 重複チェックとマージ
                for imported_preset in imported_presets:
                    name = imported_preset.get('name')
                    exists = any(p.get('name') == name for p in current_presets)
                    
                    if not exists:
                        current_presets.append(imported_preset)
                    else:
                        logging.warning(f"Preset '{name}' already exists, skipping")
                
                self.set('audio_settings.presets', current_presets)
            else:
                self.set('audio_settings.presets', imported_presets)
            
            logging.info(f"Presets imported from {import_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to import presets: {e}")
            return False
    
    def add_recent_file(self, file_path: str, file_type: str = 'input') -> bool:
        """
        最近使用したファイルの追加
        
        Args:
            file_path: ファイルパス
            file_type: ファイルタイプ（'input' または 'output'）
            
        Returns:
            追加成功の可否
        """
        try:
            if file_type == 'input':
                recent_list = self.get('app_settings.recent_files.input_files', [])
            elif file_type == 'output':
                recent_list = self.get('app_settings.recent_files.output_directories', [])
            else:
                return False
            
            # 既存のエントリを削除
            if file_path in recent_list:
                recent_list.remove(file_path)
            
            # 先頭に追加
            recent_list.insert(0, file_path)
            
            # 最大数を超えた場合は古いものを削除
            max_recent = self.get('app_settings.recent_files.max_recent', 10)
            if len(recent_list) > max_recent:
                recent_list = recent_list[:max_recent]
            
            # 設定を更新
            if file_type == 'input':
                self.set('app_settings.recent_files.input_files', recent_list)
            else:
                self.set('app_settings.recent_files.output_directories', recent_list)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to add recent file: {e}")
            return False
    
    def get_recent_files(self, file_type: str = 'input') -> List[str]:
        """
        最近使用したファイルの取得
        
        Args:
            file_type: ファイルタイプ
            
        Returns:
            ファイルパスのリスト
        """
        if file_type == 'input':
            return self.get('app_settings.recent_files.input_files', [])
        elif file_type == 'output':
            return self.get('app_settings.recent_files.output_directories', [])
        else:
            return []
    
    def reset_to_defaults(self) -> bool:
        """
        設定をデフォルトにリセット
        
        Returns:
            リセット成功の可否
        """
        try:
            self.settings = self._create_default_settings()
            self.save_settings()
            logging.info("Settings reset to defaults")
            return True
            
        except Exception as e:
            logging.error(f"Failed to reset settings: {e}")
            return False
    
    def _create_default_settings(self) -> Dict[str, Any]:
        """デフォルト設定の作成"""
        settings = self.DEFAULT_SETTINGS.copy()
        settings['metadata']['created_date'] = datetime.now().isoformat()
        settings['metadata']['last_modified'] = datetime.now().isoformat()
        return settings
    
    def _migrate_settings(self, loaded_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        設定のマイグレーション
        
        Args:
            loaded_settings: 読み込まれた設定
            
        Returns:
            マイグレーション後の設定
        """
        # バージョンチェック
        loaded_version = loaded_settings.get('version', '0.0.0')
        current_version = self.DEFAULT_SETTINGS['version']
        
        if loaded_version != current_version:
            logging.info(f"Migrating settings from {loaded_version} to {current_version}")
            
            # マイグレーション処理
            migrated_settings = self._merge_settings(self.DEFAULT_SETTINGS.copy(), loaded_settings)
            migrated_settings['version'] = current_version
            
            # マイグレーション履歴を記録
            if 'metadata' not in migrated_settings:
                migrated_settings['metadata'] = {}
            if 'settings_migrations' not in migrated_settings['metadata']:
                migrated_settings['metadata']['settings_migrations'] = []
            
            migration_record = {
                'from_version': loaded_version,
                'to_version': current_version,
                'migrated_date': datetime.now().isoformat()
            }
            migrated_settings['metadata']['settings_migrations'].append(migration_record)
            
            return migrated_settings
        
        return loaded_settings
    
    def _merge_settings(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """
        デフォルト設定と読み込み設定のマージ
        
        Args:
            default: デフォルト設定
            loaded: 読み込み設定
            
        Returns:
            マージされた設定
        """
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_settings(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def _create_backup(self) -> bool:
        """バックアップファイルの作成"""
        try:
            if self.settings_file.exists():
                import shutil
                shutil.copy2(self.settings_file, self.backup_file)
                logging.debug(f"Backup created: {self.backup_file}")
                return True
        except Exception as e:
            logging.error(f"Failed to create backup: {e}")
        return False
    
    def _restore_from_backup(self) -> bool:
        """バックアップからの復元"""
        try:
            if self.backup_file.exists():
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    backup_settings = json.load(f)
                
                self.settings = self._migrate_settings(backup_settings)
                logging.info("Settings restored from backup")
                return True
        except Exception as e:
            logging.error(f"Failed to restore from backup: {e}")
        return False
    
    def get_f0_method_info(self, method: str) -> Optional[Dict[str, Any]]:
        """
        F0メソッドの詳細情報を取得
        
        Args:
            method: F0メソッド名
            
        Returns:
            メソッド情報またはNone
        """
        f0_methods = self.get('audio_settings.f0_methods', [])
        for method_info in f0_methods:
            if method_info.get('name') == method:
                return method_info
        return None
    
    def get_all_f0_methods(self) -> List[Dict[str, Any]]:
        """
        利用可能なF0メソッドの一覧を取得
        
        Returns:
            F0メソッドの情報リスト
        """
        return self.get('audio_settings.f0_methods', [])
    
    def validate_settings(self) -> Dict[str, List[str]]:
        """
        設定の妥当性チェック
        
        Returns:
            検証結果（エラーと警告のリスト）
        """
        errors = []
        warnings = []
        
        # パスの存在チェック
        model_dir = self.get('paths.model_directory')
        if model_dir and not os.path.exists(model_dir):
            errors.append(f"Model directory does not exist: {model_dir}")
        
        # プリセットの妥当性チェック
        presets = self.get('audio_settings.presets', [])
        default_count = sum(1 for p in presets if p.get('is_default', False))
        if default_count == 0:
            warnings.append("No default preset defined")
        elif default_count > 1:
            warnings.append("Multiple default presets defined")
        
        # 数値範囲チェック
        defaults = self.get('audio_settings.default_params', {})
        if not (-24 <= defaults.get('pitch', 0) <= 24):
            errors.append("Pitch value out of range (-24 to 24)")
        
        if not (0 <= defaults.get('index_rate', 0) <= 1):
            errors.append("Index rate out of range (0 to 1)")
        
        return {'errors': errors, 'warnings': warnings}

# 使用例とテスト関数
def test_settings_manager():
    """設定管理システムのテスト"""
    import tempfile
    
    # テスト用の一時ファイル
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        settings_file = tmp.name
    
    try:
        # 設定管理システムの初期化
        settings = SettingsManager(settings_file)
        
        # 設定の取得・設定テスト
        assert settings.get('app_settings.theme') == 'dark'
        settings.set('app_settings.theme', 'light')
        assert settings.get('app_settings.theme') == 'light'
        
        # プリセットのテスト
        preset = settings.get_default_preset()
        assert preset is not None
        
        # カスタムプリセットの追加
        assert settings.add_preset(
            'test_preset',
            'Test preset',
            {'pitch': 5, 'f0_method': 'harvest'},
            is_default=False
        )
        
        # 最近使用したファイルのテスト
        assert settings.add_recent_file('/path/to/test.wav', 'input')
        recent = settings.get_recent_files('input')
        assert '/path/to/test.wav' in recent
        
        # 設定の保存・読み込みテスト
        assert settings.save_settings()
        
        # 新しいインスタンスで読み込み
        settings2 = SettingsManager(settings_file)
        assert settings2.get('app_settings.theme') == 'light'
        
        print("All tests passed!")
        
    finally:
        # テストファイルの削除
        os.unlink(settings_file)
        backup_file = settings_file + '.backup'
        if os.path.exists(backup_file):
            os.unlink(backup_file)

if __name__ == "__main__":
    test_settings_manager()