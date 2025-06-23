# zlibエラー解決策 - 2025年6月24日

## 問題: PyInstallerでlibrosaモジュールが正しく解凍されない

### 根本原因
PyInstallerのPYZアーカイブ（.pyz）からlibrosaモジュールを展開する際に、zlibの解凍エラーが発生。
これはlibrosaが大きく複雑なモジュールであるため、PyInstallerの圧縮/展開機構に問題が生じている。

## 解決策1: OneFolderモードでのビルド（推奨）

### 理由
- OneFileモードは全てを1つの実行ファイルに圧縮するため、大きなモジュールで問題が発生しやすい
- OneFolderモードは各モジュールを個別のファイルとして保持するため、圧縮問題を回避できる

### 実装手順
1. `RVC_Final_OneFolder.spec`ファイルを作成
2. `EXE`セクションでOneFile=Falseに設定
3. `COLLECT`セクションを使用してファイルを収集

## 解決策2: librosaを別途バイナリとして含める

### 実装方法
```python
# specファイルで除外
excludes = ['librosa']

# datasセクションで個別に追加
import librosa
librosa_path = Path(librosa.__file__).parent
datas.append((str(librosa_path), 'librosa'))
```

## 解決策3: 圧縮を完全に無効化

### 実装方法
```python
# PYZの作成を完全にスキップ
a = Analysis(
    # ...
    noarchive=True,  # アーカイブを使用しない
)

# EXEセクションでも圧縮を無効化
exe = EXE(
    # ...
    compress=False,  # 圧縮を無効化
    archive=None,    # アーカイブを使用しない
)
```

## 解決策4: 代替音声ライブラリの使用

### 候補
1. **soundfile + numpy**: 基本的な音声読み込み/書き込み
2. **pydub**: シンプルな音声処理
3. **scipy.io.wavfile**: WAVファイルの直接処理

### 実装上の注意
音声変換パイプラインを変更しないという制約があるため、librosaのAPIと互換性のあるラッパーを作成する必要がある。

## 推奨アプローチ

1. **最初に試すべき**: OneFolderモードでのビルド
2. **それでもダメなら**: librosaを除外してデータとして含める
3. **最終手段**: 最小限の音声処理ライブラリで代替実装

## 実装優先順位

1. ✅ OneFolderモードのspecファイル作成
2. ⏳ OneFolderモードでのビルドとテスト
3. 🔄 必要に応じて他の解決策を試行
