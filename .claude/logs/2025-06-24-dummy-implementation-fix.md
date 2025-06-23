# 2025年6月24日 - ダミー実装による音声品質劣化の修正

## 問題の概要

PyInstallerスタンドアロンアプリで音声変換は動作するが、声質が著しく劣化している。

### 影響範囲
- Hubert特徴抽出がダミー実装
- Parselmouth（F0推定）がダミー実装
- 結果として音声の本質的な特徴が失われる

## 修正対象ファイル

1. `rvc/modules/vc/utils.py`
   - DummyHubertModelクラスを削除
   - 本来のHubertモデルロードを復活

2. `rvc/modules/vc/pipeline.py`
   - DummyParselmouthクラスを削除
   - 本来のparselmouthインポートを復活

3. `rvc/modules/vc/enhanced_pipeline.py`
   - DummyParselmouthクラスを削除
   - 本来のparselmouthインポートを復活

4. `rvc_minimal.spec`
   - parselmouthをhiddenimportsに追加
   - 必要な動的ライブラリを収集

## 修正方針

### CLAUDE.mdルールの遵守
- RVCのアルゴリズムを改変しない
- エラー回避のためのダミー実装は行わない
- 必須モジュール欠落時は明確なエラーで停止

### 技術的対応
1. try-except でのダミー代替を削除
2. ImportErrorは上位に伝播させる
3. GUI側で適切なエラーメッセージ表示 