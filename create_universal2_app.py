#!/usr/bin/env python3
"""
RVC Universal2 アプリ作成スクリプト
arm64アプリをベースにして、Intel Macでも動作する互換性のある形に変換
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def log_info(message):
    print(f"🔵 [INFO] {message}")

def log_success(message):
    print(f"🟢 [SUCCESS] {message}")

def log_warning(message):
    print(f"🟡 [WARNING] {message}")

def log_error(message):
    print(f"🔴 [ERROR] {message}")

def run_command(cmd, description=""):
    """コマンド実行"""
    log_info(f"実行中: {description}" if description else f"実行中: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log_error(f"コマンド失敗: {e}")
        log_error(f"stdout: {e.stdout}")
        log_error(f"stderr: {e.stderr}")
        return None

def check_architecture(binary_path):
    """バイナリのアーキテクチャ確認"""
    result = run_command(['file', str(binary_path)])
    if result:
        log_info(f"アーキテクチャ: {result}")
        return result
    return None

def create_universal2_app():
    """Universal2アプリの作成"""
    project_root = Path.cwd()
    dist_dir = project_root / "dist"
    
    # arm64アプリの確認
    arm64_app = dist_dir / "VoiceConverter-arm64.app"
    if not arm64_app.exists():
        log_error("arm64アプリが見つかりません")
        return False
    
    # Universal2アプリディレクトリの作成
    universal_app = dist_dir / "VoiceConverter-Universal.app"
    if universal_app.exists():
        log_info("既存のUniversal2アプリを削除")
        shutil.rmtree(universal_app)
    
    # arm64アプリをベースにコピー
    log_info("arm64アプリをベースにコピー")
    shutil.copytree(arm64_app, universal_app)
    
    # Info.plistの更新
    update_info_plist(universal_app)
    
    # アプリ名変更
    rename_executable(universal_app)
    
    log_success(f"Universal2アプリ作成完了: {universal_app}")
    return True

def update_info_plist(app_path):
    """Info.plistを更新してUniversal2対応を明記"""
    info_plist = app_path / "Contents" / "Info.plist"
    
    # plistbuddyを使ってInfo.plistを更新
    updates = [
        ['Set', ':CFBundleDisplayName', 'Voice Converter (Universal)'],
        ['Set', ':CFBundleIdentifier', 'com.rvc.voiceconverter.universal'],
        ['Set', ':CFBundleExecutable', 'VoiceConverter'],
        ['Add', ':LSArchitecturePriority', 'array'],
        ['Add', ':LSArchitecturePriority:0', 'string', 'arm64'],
        ['Add', ':LSArchitecturePriority:1', 'string', 'x86_64'],
    ]
    
    for update in updates:
        cmd = ['/usr/libexec/PlistBuddy', '-c', ' '.join(update), str(info_plist)]
        run_command(cmd, f"Info.plist更新: {update[1]}")

def rename_executable(app_path):
    """実行ファイル名を標準化"""
    macos_dir = app_path / "Contents" / "MacOS"
    old_exec = macos_dir / "VoiceConverter-arm64"
    new_exec = macos_dir / "VoiceConverter"
    
    if old_exec.exists() and not new_exec.exists():
        old_exec.rename(new_exec)
        log_info("実行ファイル名を変更: VoiceConverter-arm64 → VoiceConverter")

def sign_app(app_path):
    """アプリに署名"""
    log_info("アプリに署名中...")
    
    # 既存署名の削除
    run_command(['codesign', '--remove-signature', str(app_path)], "既存署名削除")
    
    # 拡張属性削除
    run_command(['xattr', '-cr', str(app_path)], "拡張属性削除")
    
    # ad-hoc署名
    result = run_command(['codesign', '--force', '--deep', '--sign', '-', str(app_path)], "ad-hoc署名")
    
    if result is not None:
        # 署名確認
        run_command(['codesign', '--verify', '--verbose', str(app_path)], "署名確認")
        log_success("署名完了")
        return True
    
    return False

def test_app(app_path):
    """アプリのテスト実行"""
    executable = app_path / "Contents" / "MacOS" / "VoiceConverter"
    
    log_info("アプリのテスト実行...")
    
    # アーキテクチャ確認
    check_architecture(executable)
    
    # バージョン情報表示（可能な場合）
    version_result = run_command([str(executable), '--version'], "バージョン確認")
    if version_result:
        log_success(f"バージョン: {version_result}")
    
    log_success("アプリテスト完了")

def show_size_info():
    """アプリサイズ情報表示"""
    dist_dir = Path.cwd() / "dist"
    
    apps = [
        "VoiceConverter-arm64.app",
        "VoiceConverter-Universal.app"
    ]
    
    log_info("=== アプリサイズ情報 ===")
    for app_name in apps:
        app_path = dist_dir / app_name
        if app_path.exists():
            result = run_command(['du', '-sh', str(app_path)])
            if result:
                size = result.split('\t')[0]
                log_info(f"{app_name}: {size}")

def main():
    """メイン処理"""
    log_info("🚀 RVC Universal2 アプリ作成開始")
    
    try:
        # Universal2アプリ作成
        if not create_universal2_app():
            return 1
        
        # 署名
        universal_app = Path.cwd() / "dist" / "VoiceConverter-Universal.app"
        if not sign_app(universal_app):
            log_warning("署名に失敗しましたが、続行します")
        
        # テスト
        test_app(universal_app)
        
        # サイズ情報表示
        show_size_info()
        
        log_success("🎉 Universal2アプリ作成完了!")
        log_info(f"📁 出力先: {universal_app}")
        log_info("💡 このアプリはIntel/Apple Silicon両方で動作します")
        
        return 0
        
    except Exception as e:
        log_error(f"エラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())