#!/usr/bin/env python3
"""
librosa診断スクリプト
PyInstallerビルド前後でlibrosaの動作を確認
"""
import sys
import os
import traceback
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def check_environment():
    """環境情報の確認"""
    print_section("環境情報")
    print(f"Python: {sys.version}")
    print(f"実行パス: {sys.executable}")
    print(f"プラットフォーム: {sys.platform}")

    # PyInstaller環境の確認
    if hasattr(sys, '_MEIPASS'):
        print(f"PyInstaller環境: True")
        print(f"Bundle Dir: {sys._MEIPASS}")
    else:
        print(f"PyInstaller環境: False")

    print("\nsys.path:")
    for i, p in enumerate(sys.path[:10]):
        print(f"  [{i}] {p}")

def check_basic_imports():
    """基本的なインポートの確認"""
    print_section("基本インポートテスト")

    basic_modules = [
        'numpy',
        'scipy',
        'soundfile',
        'resampy',
        'numba',
        'audioread',
        'joblib',
        'decorator',
        'sklearn',
        'packaging',
        'pooch',
        'soxr',
        'lazy_loader',
        'msgpack'
    ]

    results = {}
    for module in basic_modules:
        try:
            __import__(module)
            results[module] = "✓ OK"
        except Exception as e:
            results[module] = f"✗ {type(e).__name__}: {str(e)}"

    for module, status in results.items():
        print(f"{module:20} {status}")

    return results

def check_librosa_components():
    """librosaの各コンポーネントを個別にテスト"""
    print_section("librosaコンポーネントテスト")

    # まずlibrosa本体のインポートを試みる
    try:
        import librosa
        print("librosa本体: ✓ OK")
        print(f"librosaバージョン: {librosa.__version__}")
        print(f"librosaパス: {librosa.__file__}")
    except Exception as e:
        print(f"librosa本体: ✗ {type(e).__name__}")
        print(f"エラー詳細:\n{traceback.format_exc()}")
        return False

    # 個別コンポーネントのテスト
    components = [
        'librosa.core',
        'librosa.util',
        'librosa.feature',
        'librosa.effects',
        'librosa.filters',
        'librosa.onset',
        'librosa.beat',
        'librosa.decompose',
        'librosa.display'
    ]

    for component in components:
        try:
            parts = component.split('.')
            if len(parts) == 2:
                module = __import__(parts[0])
                getattr(module, parts[1])
            print(f"{component:25} ✓ OK")
        except Exception as e:
            print(f"{component:25} ✗ {type(e).__name__}: {str(e)}")

    return True

def test_audio_loading():
    """音声ファイル読み込みテスト"""
    print_section("音声読み込みテスト")

    # テスト用音声データの作成
    test_audio_path = Path("test_audio.wav")

    try:
        import numpy as np
        import soundfile as sf

        # 1秒のサイン波を生成
        sr = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)

        # ファイルに保存
        sf.write(str(test_audio_path), audio_data, sr)
        print(f"テスト音声作成: ✓ OK ({test_audio_path})")

        # soundfileでの読み込みテスト
        data_sf, sr_sf = sf.read(str(test_audio_path))
        print(f"soundfile読み込み: ✓ OK (shape={data_sf.shape}, sr={sr_sf})")

        # librosaでの読み込みテスト（可能な場合）
        try:
            import librosa
            data_lr, sr_lr = librosa.load(str(test_audio_path), sr=None)
            print(f"librosa読み込み: ✓ OK (shape={data_lr.shape}, sr={sr_lr})")
        except Exception as e:
            print(f"librosa読み込み: ✗ {type(e).__name__}: {str(e)}")

    except Exception as e:
        print(f"テストエラー: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
    finally:
        # クリーンアップ
        if test_audio_path.exists():
            test_audio_path.unlink()
            print("テストファイル削除: ✓")

def check_rvc_audio_module():
    """RVCのaudioモジュールのテスト"""
    print_section("RVC audioモジュールテスト")

    try:
        # RVCモジュールのパスを追加
        if hasattr(sys, '_MEIPASS'):
            rvc_path = Path(sys._MEIPASS).parent / "Resources" / "rvc"
        else:
            rvc_path = Path(__file__).parent / "rvc"

        if rvc_path.exists():
            sys.path.insert(0, str(rvc_path.parent))
            print(f"RVCパス追加: {rvc_path.parent}")

        # RVCのaudioモジュールをインポート
        from rvc.lib import audio
        print("rvc.lib.audio: ✓ OK")

        # 主要な関数の確認
        functions = ['load_audio', 'wav2']
        for func in functions:
            if hasattr(audio, func):
                print(f"  - {func}: ✓ 存在")
            else:
                print(f"  - {func}: ✗ 存在しない")

    except Exception as e:
        print(f"rvc.lib.audio: ✗ {type(e).__name__}")
        print(f"エラー詳細:\n{traceback.format_exc()}")

def main():
    """メイン診断処理"""
    print("librosa診断スクリプト開始")

    # 1. 環境確認
    check_environment()

    # 2. 基本インポート確認
    import_results = check_basic_imports()

    # 3. librosaコンポーネント確認
    librosa_ok = check_librosa_components()

    # 4. 音声読み込みテスト
    test_audio_loading()

    # 5. RVC audioモジュールテスト
    check_rvc_audio_module()

    # 結果サマリ
    print_section("診断結果サマリ")
    failed_imports = [m for m, status in import_results.items() if not status.startswith("✓")]
    if failed_imports:
        print(f"失敗したインポート: {', '.join(failed_imports)}")
    else:
        print("すべての基本インポートが成功")

    if librosa_ok:
        print("librosaのインポート: 成功")
    else:
        print("librosaのインポート: 失敗")

    print("\n診断完了")

if __name__ == "__main__":
    main()
