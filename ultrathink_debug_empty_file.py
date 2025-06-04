#!/usr/bin/env python3
"""
ULTRATHINK: Enhanced変換で空ファイルが生成される根本原因の詳細調査
段階的デバッグで問題箇所を特定
"""

import os
import sys
import json
import tempfile
import logging
import traceback
import numpy as np
import soundfile as sf
from pathlib import Path
import subprocess

# 詳細ログ設定
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UltraThinkDebugger:
    """ULTRATHINK: 空ファイル問題の根本原因調査クラス"""
    
    def __init__(self):
        self.test_results = {}
        self.debug_data = {}
        
    def create_test_audio(self, duration=3, sample_rate=16000):
        """高品質テスト音声を生成"""
        logger.info(f"Creating test audio: {duration}s at {sample_rate}Hz")
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 複数周波数の音声信号（人間の声に近い特性）
        f1, f2, f3 = 200, 400, 800  # 基本周波数とハーモニクス
        audio = (np.sin(2 * np.pi * f1 * t) * 0.4 +
                np.sin(2 * np.pi * f2 * t) * 0.3 +
                np.sin(2 * np.pi * f3 * t) * 0.2)
        
        # エンベロープとビブラート効果
        envelope = np.exp(-t * 0.3) * (1 + 0.1 * np.sin(2 * np.pi * 5 * t))
        audio = audio * envelope
        
        # 少量のノイズ
        audio += np.random.normal(0, 0.01, len(audio))
        
        # 正規化
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.8
        
        logger.info(f"Test audio created: shape={audio.shape}, max={np.max(audio):.3f}, min={np.min(audio):.3f}")
        return audio, sample_rate
    
    def step1_verify_input_audio(self):
        """ステップ1: 入力音声ファイルの検証"""
        logger.info("=" * 60)
        logger.info("STEP 1: 入力音声ファイルの検証")
        logger.info("=" * 60)
        
        try:
            # テスト音声を作成
            audio_data, sample_rate = self.create_test_audio()
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                sf.write(temp_file.name, audio_data, sample_rate)
                temp_path = temp_file.name
            
            # ファイル情報を詳細確認
            file_stat = Path(temp_path).stat()
            logger.info(f"✅ 入力ファイル作成成功: {temp_path}")
            logger.info(f"   ファイルサイズ: {file_stat.st_size} bytes")
            
            # ファイル再読み込みテスト
            read_audio, read_sr = sf.read(temp_path)
            logger.info(f"   再読み込み成功: shape={read_audio.shape}, sr={read_sr}")
            logger.info(f"   音声統計: max={np.max(read_audio):.3f}, min={np.min(read_audio):.3f}")
            
            self.debug_data['input_file'] = temp_path
            self.debug_data['input_audio_data'] = read_audio
            self.debug_data['input_sample_rate'] = read_sr
            self.test_results['step1_input_verification'] = True
            
            return True, temp_path
            
        except Exception as e:
            logger.error(f"❌ 入力ファイル検証失敗: {e}")
            traceback.print_exc()
            self.test_results['step1_input_verification'] = False
            return False, None
    
    def step2_test_mps_fft_issue(self):
        """ステップ2: MPS/FFT問題の詳細分析"""
        logger.info("=" * 60)
        logger.info("STEP 2: MPS/FFT問題の詳細分析")
        logger.info("=" * 60)
        
        try:
            import torch
            
            # 環境確認
            logger.info(f"PyTorch version: {torch.__version__}")
            logger.info(f"MPS available: {torch.backends.mps.is_available()}")
            logger.info(f"PYTORCH_ENABLE_MPS_FALLBACK: {os.environ.get('PYTORCH_ENABLE_MPS_FALLBACK', 'NOT_SET')}")
            
            # MPS環境でのFFTテスト
            if torch.backends.mps.is_available():
                logger.info("Testing FFT operations on MPS...")
                
                # MPSでSTFTテスト
                device = torch.device('mps')
                test_audio = torch.randn(1, 16000).to(device)
                
                try:
                    # STFT実行テスト
                    stft_result = torch.stft(
                        test_audio,
                        n_fft=1024,
                        hop_length=256,
                        return_complex=True
                    )
                    logger.info("✅ MPS STFT test passed")
                    self.test_results['step2_mps_stft'] = True
                    
                except Exception as e:
                    logger.error(f"❌ MPS STFT failed: {e}")
                    self.test_results['step2_mps_stft'] = False
                    
                    # MPS_FALLBACKを設定してリトライ
                    logger.info("Setting PYTORCH_ENABLE_MPS_FALLBACK=1 and retrying...")
                    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                    
                    try:
                        stft_result = torch.stft(
                            test_audio,
                            n_fft=1024,
                            hop_length=256,
                            return_complex=True
                        )
                        logger.info("✅ MPS STFT with fallback passed")
                        self.test_results['step2_mps_fallback'] = True
                    except Exception as e2:
                        logger.error(f"❌ MPS STFT with fallback failed: {e2}")
                        self.test_results['step2_mps_fallback'] = False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ MPS/FFT テスト失敗: {e}")
            traceback.print_exc()
            return False
    
    def step3_test_f0_estimation(self, input_file):
        """ステップ3: F0推定処理の詳細テスト"""
        logger.info("=" * 60)
        logger.info("STEP 3: F0推定処理の詳細テスト")
        logger.info("=" * 60)
        
        if not input_file:
            logger.error("❌ 入力ファイルがありません")
            return False
        
        try:
            # Poetry環境でF0推定テスト
            test_script = f'''
import sys
import os
import numpy as np
import soundfile as sf
sys.path.append("/Users/norikene_satoshi/Retrieval-based-Voice-Conversion")

# MPS fallback設定
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

print("="*60)
print("F0推定テスト開始")
print("="*60)

try:
    from enhanced_voice_converter import EnhancedVoiceConverter
    
    converter = EnhancedVoiceConverter()
    models = converter.list_available_models()
    
    if models:
        model = models[0]
        print(f"モデル使用: {{model['name']}}")
        
        success = converter.load_model(model['path'], model['index_path'])
        if success:
            print("✅ モデル読み込み成功")
            
            # 入力音声情報
            audio_data, sr = sf.read("{input_file}")
            print(f"入力音声: shape={{audio_data.shape}}, sr={{sr}}")
            print(f"音声統計: max={{np.max(audio_data):.3f}}, min={{np.min(audio_data):.3f}}")
            
            # F0推定手法別テスト
            f0_methods = ['harvest', 'dio', 'pm']  # rmvpeはMPSで問題があるため除外
            
            for method in f0_methods:
                print(f"\\n--- F0推定テスト: {{method}} ---")
                try:
                    # F0推定のみ実行（変換はしない）
                    from rvc.modules.vc.pipeline import Pipeline
                    from rvc.configs.config import Config
                    
                    config = Config()
                    pipeline = Pipeline(40000, config)
                    
                    # F0推定実行
                    f0, f0f = pipeline.get_f0(
                        "{input_file}",
                        audio_data,
                        len(audio_data) // 320,
                        0,  # f0_up_key
                        method,
                        3   # filter_radius
                    )
                    
                    print(f"✅ F0推定成功 ({{method}}): shape={{f0.shape}}, mean={{np.mean(f0):.2f}}")
                    
                except Exception as e:
                    print(f"❌ F0推定失敗 ({{method}}): {{e}}")
        
        else:
            print("❌ モデル読み込み失敗")
    else:
        print("❌ モデルが見つかりません")
        
except Exception as e:
    print(f"❌ F0推定テスト失敗: {{e}}")
    import traceback
    traceback.print_exc()

print("="*60)
print("F0推定テスト完了")
print("="*60)
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
                temp_script.write(test_script)
                script_path = temp_script.name
            
            # Poetry環境でF0テストを実行
            result = subprocess.run(
                ['poetry', 'run', 'python', script_path],
                cwd='/Users/norikene_satoshi/Retrieval-based-Voice-Conversion',
                capture_output=True,
                text=True,
                timeout=120
            )
            
            os.unlink(script_path)
            
            logger.info("F0推定テスト結果:")
            print(result.stdout)
            if result.stderr:
                logger.error(f"F0推定エラー: {result.stderr}")
            
            if result.returncode == 0:
                self.test_results['step3_f0_estimation'] = True
                return True
            else:
                self.test_results['step3_f0_estimation'] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ F0推定テスト失敗: {e}")
            traceback.print_exc()
            self.test_results['step3_f0_estimation'] = False
            return False
    
    def step4_test_conversion_pipeline(self, input_file):
        """ステップ4: 変換パイプライン全体の詳細テスト"""
        logger.info("=" * 60)
        logger.info("STEP 4: 変換パイプライン全体の詳細テスト")
        logger.info("=" * 60)
        
        if not input_file:
            logger.error("❌ 入力ファイルがありません")
            return False
        
        try:
            # Poetry環境で詳細な変換テスト
            test_script = f'''
import sys
import os
import numpy as np
import soundfile as sf
from pathlib import Path
sys.path.append("/Users/norikene_satoshi/Retrieval-based-Voice-Conversion")

# 詳細ログ設定
import logging
logging.basicConfig(level=logging.DEBUG)

# MPS fallback設定
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

print("="*60)
print("変換パイプライン詳細テスト開始")
print("="*60)

try:
    from enhanced_voice_converter import EnhancedVoiceConverter
    
    converter = EnhancedVoiceConverter()
    
    # 出力ディレクトリ作成
    output_dir = Path("/tmp/ultrathink_debug_output")
    output_dir.mkdir(exist_ok=True)
    
    models = converter.list_available_models()
    if models:
        model = models[0]
        print(f"モデル使用: {{model['name']}}")
        
        success = converter.load_model(model['path'], model['index_path'])
        if success:
            print("✅ モデル読み込み成功")
            
            # 変換前の入力ファイル確認
            input_audio, input_sr = sf.read("{input_file}")
            print(f"入力音声確認: shape={{input_audio.shape}}, sr={{input_sr}}")
            print(f"入力統計: max={{np.max(input_audio):.3f}}, min={{np.min(input_audio):.3f}}, mean={{np.mean(input_audio):.3f}}")
            
            # 変換実行（MPS fallback使用、安全なF0手法）
            output_path = output_dir / "debug_output.wav"
            print(f"出力パス: {{output_path}}")
            
            print("\\n🚀 変換開始...")
            result = converter.convert_audio(
                input_path="{input_file}",
                output_path=str(output_path),
                f0_method='harvest',  # MPS問題回避
                pitch=0,
                index_rate=0.5,  # 安全な値
                filter_radius=3,
                rms_mix_rate=0.25,
                protect=0.33
            )
            
            if result:
                print(f"✅ 変換完了: {{result}}")
                
                # 出力ファイル詳細確認
                if Path(result).exists():
                    file_size = Path(result).stat().st_size
                    print(f"出力ファイルサイズ: {{file_size}} bytes")
                    
                    if file_size > 1000:  # 1KB以上なら成功
                        output_audio, output_sr = sf.read(result)
                        print(f"出力音声: shape={{output_audio.shape}}, sr={{output_sr}}")
                        print(f"出力統計: max={{np.max(output_audio):.3f}}, min={{np.min(output_audio):.3f}}")
                        print("✅ 変換成功: 有効な音声データが生成されました")
                    else:
                        print(f"❌ 変換失敗: 出力ファイルが小さすぎます ({{file_size}} bytes)")
                        
                        # 空ファイルの原因調査
                        try:
                            empty_audio, empty_sr = sf.read(result)
                            print(f"空ファイル読み込み: shape={{empty_audio.shape}}, sr={{empty_sr}}")
                        except Exception as e:
                            print(f"空ファイル読み込み失敗: {{e}}")
                else:
                    print("❌ 出力ファイルが作成されていません")
            else:
                print("❌ 変換失敗: Noneが返されました")
        else:
            print("❌ モデル読み込み失敗")
    else:
        print("❌ モデルが見つかりません")
        
except Exception as e:
    print(f"❌ 変換パイプラインテスト失敗: {{e}}")
    import traceback
    traceback.print_exc()

print("="*60)
print("変換パイプライン詳細テスト完了")
print("="*60)
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
                temp_script.write(test_script)
                script_path = temp_script.name
            
            # Poetry環境で変換テストを実行
            result = subprocess.run(
                ['poetry', 'run', 'python', script_path],
                cwd='/Users/norikene_satoshi/Retrieval-based-Voice-Conversion',
                capture_output=True,
                text=True,
                timeout=180
            )
            
            os.unlink(script_path)
            
            logger.info("変換パイプラインテスト結果:")
            print(result.stdout)
            if result.stderr:
                logger.error(f"変換エラー: {result.stderr}")
            
            # 成功判定
            if "変換成功: 有効な音声データが生成されました" in result.stdout:
                self.test_results['step4_conversion_pipeline'] = True
                return True
            else:
                self.test_results['step4_conversion_pipeline'] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ 変換パイプラインテスト失敗: {e}")
            traceback.print_exc()
            self.test_results['step4_conversion_pipeline'] = False
            return False
    
    def step5_analyze_gui_integration(self):
        """ステップ5: GUI統合での問題分析"""
        logger.info("=" * 60)
        logger.info("STEP 5: GUI統合での問題分析")
        logger.info("=" * 60)
        
        try:
            # GUIからの呼び出しをシミュレート
            gui_script = '''
import sys
import os
import json
sys.path.append("/Users/norikene_satoshi/Retrieval-based-Voice-Conversion")

# MPS fallback設定
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

print("="*60)
print("GUI統合問題分析")
print("="*60)

try:
    # gui_dark_mode_enhanced.pyの重要な部分をテスト
    from enhanced_voice_converter import EnhancedVoiceConverter
    
    print("Enhanced Voice Converterインポート成功")
    
    # GUIと同じ処理パスを模擬
    converter = EnhancedVoiceConverter()
    
    # モデル情報
    models = converter.list_available_models()
    print(f"利用可能モデル数: {len(models)}")
    
    if models:
        model = models[0]
        print(f"テストモデル: {model['name']}")
        
        # GUIと同じパラメータでテスト
        load_success = converter.load_model(model['path'], model['index_path'])
        print(f"モデル読み込み: {'成功' if load_success else '失敗'}")
        
        if load_success:
            # Enhancement status確認
            status = converter.get_enhancement_status()
            print(f"Enhanced status: {status}")
            
            # GUIの設定検証
            if status['pipeline_type'] == 'enhanced':
                print("✅ Enhanced Pipeline正常動作")
                
                # エラーハンドリング確認
                pipeline = converter.vc.pipeline
                if hasattr(pipeline, 'enable_adaptive_neighbors'):
                    print(f"Enhanced機能状態:")
                    print(f"  - Adaptive neighbors: {pipeline.enable_adaptive_neighbors}")
                    print(f"  - F0 ensemble: {pipeline.enable_f0_ensemble}")  
                    print(f"  - VAD segmentation: {pipeline.enable_vad_segmentation}")
                    print("✅ 全Enhanced機能確認済み")
                else:
                    print("❌ Enhanced Pipeline機能が検出されません")
            else:
                print("❌ Enhanced Pipelineが動作していません")
        else:
            print("❌ モデル読み込み失敗")
    else:
        print("❌ モデルが見つかりません")
        
except Exception as e:
    print(f"❌ GUI統合テスト失敗: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
print("GUI統合問題分析完了")
print("="*60)
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
                temp_script.write(gui_script)
                script_path = temp_script.name
            
            result = subprocess.run(
                ['poetry', 'run', 'python', script_path],
                cwd='/Users/norikene_satoshi/Retrieval-based-Voice-Conversion',
                capture_output=True,
                text=True,
                timeout=60
            )
            
            os.unlink(script_path)
            
            logger.info("GUI統合テスト結果:")
            print(result.stdout)
            if result.stderr:
                logger.error(f"GUI統合エラー: {result.stderr}")
            
            if "全Enhanced機能確認済み" in result.stdout:
                self.test_results['step5_gui_integration'] = True
                return True
            else:
                self.test_results['step5_gui_integration'] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ GUI統合テスト失敗: {e}")
            traceback.print_exc()
            self.test_results['step5_gui_integration'] = False
            return False
    
    def generate_ultrathink_report(self):
        """ULTRATHINK: 総合分析レポート生成"""
        logger.info("=" * 80)
        logger.info("🧠 ULTRATHINK: 根本原因分析レポート")
        logger.info("=" * 80)
        
        # 各ステップの結果を分析
        steps = [
            ('step1_input_verification', '入力音声ファイル検証'),
            ('step2_mps_stft', 'MPS STFT処理'),
            ('step2_mps_fallback', 'MPS Fallback処理'),
            ('step3_f0_estimation', 'F0推定処理'),
            ('step4_conversion_pipeline', '変換パイプライン'),
            ('step5_gui_integration', 'GUI統合')
        ]
        
        logger.info("📊 各ステップの結果:")
        for step_key, step_name in steps:
            result = self.test_results.get(step_key, None)
            if result is True:
                status = "✅ 成功"
            elif result is False:
                status = "❌ 失敗"
            else:
                status = "⚠️  未実行"
            logger.info(f"  {step_name}: {status}")
        
        # 根本原因の特定
        logger.info("\n🔍 根本原因分析:")
        
        critical_failures = []
        for step_key, step_name in steps:
            if self.test_results.get(step_key) is False:
                critical_failures.append(step_name)
        
        if not critical_failures:
            logger.info("✅ 全ステップが成功 - 問題は特定の環境条件にある可能性")
        else:
            logger.error(f"❌ 失敗ステップ: {', '.join(critical_failures)}")
        
        # 推定される問題と解決策
        logger.info("\n💡 推定される問題と解決策:")
        
        if self.test_results.get('step2_mps_stft') is False:
            logger.error("🚨 MPS FFT問題が主要原因:")
            logger.error("  - rmvpeモデルがMPSで動作しない")
            logger.error("  - F0推定でエラーが発生し、空の音声データが生成される")
            logger.info("  解決策: harvest/dioメソッドの使用、MPS fallback有効化")
        
        if self.test_results.get('step3_f0_estimation') is False:
            logger.error("🚨 F0推定が失敗:")
            logger.error("  - F0推定エラーが変換処理全体を破綻させる")
            logger.info("  解決策: より安定したF0手法の使用")
        
        if self.test_results.get('step4_conversion_pipeline') is False:
            logger.error("🚨 変換パイプライン問題:")
            logger.error("  - Enhanced Pipeline内でエラーが発生")
            logger.error("  - エラーハンドリングが不適切")
            logger.info("  解決策: より詳細なエラーハンドリングとフォールバック")
        
        # 最終的な推奨事項
        logger.info("\n🎯 最終推奨事項:")
        logger.info("1. MPS環境でのrmvpe使用を避け、harvestまたはdioを使用")
        logger.info("2. PYTORCH_ENABLE_MPS_FALLBACK=1を常に設定")
        logger.info("3. F0推定エラー時の適切なフォールバック処理を実装")
        logger.info("4. 変換パイプライン内での中間データ検証を追加")
        logger.info("5. GUIからのエラー情報をより詳細にログ出力")
        
        return {
            'test_results': self.test_results,
            'debug_data': self.debug_data,
            'critical_failures': critical_failures
        }

def main():
    """メイン実行関数"""
    logger.info("🧠 ULTRATHINK DEBUG SESSION 開始")
    logger.info("Enhanced変換で空ファイルが生成される問題の根本原因調査")
    
    debugger = UltraThinkDebugger()
    
    # ステップ1: 入力ファイル検証
    success1, input_file = debugger.step1_verify_input_audio()
    
    # ステップ2: MPS/FFT問題分析
    debugger.step2_test_mps_fft_issue()
    
    # ステップ3: F0推定テスト
    if input_file:
        debugger.step3_test_f0_estimation(input_file)
        
        # ステップ4: 変換パイプライン全体テスト
        debugger.step4_test_conversion_pipeline(input_file)
        
        # クリーンアップ
        os.unlink(input_file)
    
    # ステップ5: GUI統合分析
    debugger.step5_analyze_gui_integration()
    
    # 最終レポート生成
    report = debugger.generate_ultrathink_report()
    
    # レポート保存
    with open('ultrathink_debug_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n📄 詳細レポート保存: ultrathink_debug_report.json")

if __name__ == "__main__":
    main()