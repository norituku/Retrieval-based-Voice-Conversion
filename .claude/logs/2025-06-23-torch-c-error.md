# 2025年6月23日 - torch._C モジュールロードエラー解決作業

## 問題の概要

PyInstallerでビルドしたスタンドアロンアプリで、torch._Cモジュールのロードに失敗する問題が発生。

### エラー詳細
```
NameError: name '_C' is not defined
発生場所: torch/__init__.py:465 - for name in dir(_C):
```

## 原因分析

1. **モジュール名競合**
   - torch/random.py と Python標準のrandomモジュールが競合
   - tempfileモジュールのインポート時に誤ったrandomがロードされる

2. **ライブラリパス問題**
   - _C.cpython-311-darwin.so がFrameworksディレクトリに配置
   - libtorch_python.dylib との依存関係解決失敗

3. **PyInstallerの制約**
   - torch._C はPythonモジュールではなくC++拡張
   - 通常のhiddenimportsでは収集不可能

## 試みた解決策

### 1. runtime_hook.pyでの事前インポート ✅
```python
# torch/random.pyとPython標準ライブラリの競合を回避
import random as stdlib_random
import tempfile as stdlib_tempfile
sys.modules['random'] = stdlib_random
sys.modules['tempfile'] = stdlib_tempfile
```

### 2. ライブラリパス設定の最適化 ✅
```python
torch_paths = [
    os.path.join(frameworks_dir, 'torch', 'lib'),
    frameworks_dir,
]
os.environ['DYLD_LIBRARY_PATH'] = ':'.join(torch_paths)
```

### 3. torch._Cの手動ロード試行 ✅
```python
# torch._Cバイナリを手動ロード
loader = importlib.machinery.ExtensionFileLoader('torch._C', torch_c_path)
spec = importlib.util.spec_from_loader('torch._C', loader)
torch_c_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(torch_c_module)
sys.modules['torch._C'] = torch_c_module
```

### 4. 依存ライブラリの事前ロード ✅
```python
priority_libs = [
    'libc++.1.dylib',
    'libz.1.dylib', 
    'libtorch_cpu.dylib',
    'libtorch_python.dylib',
    'libtorch.dylib'
]
```

## 現在の状態

### 達成事項
- ✅ GUIアプリケーションは起動する
- ✅ runtime_hookで標準ライブラリ競合を回避
- ✅ 依存ライブラリの事前ロードに成功
- ✅ torch._Cの手動ロードに成功（モジュール自体は存在）

### 未解決問題
- ❌ torch.__init__.py内でのインポート時に_Cが未定義
- ❌ 循環インポートの可能性
- ❌ 音声変換機能は未検証

## 今後の方針

1. **GUI内での直接実行を検証**
   - _run_rvc_direct()関数でのtorch初期化を確認
   - runtime_hookでの初期化を避け、実行時初期化に移行

2. **代替アプローチの検討**
   - torch初期化のタイミング変更
   - lazy importパターンの採用
   - 最小限のtorch機能のみ使用

3. **デバッグ強化**
   - torch.__init__.pyの詳細なトレース
   - モジュール読み込み順序の可視化
   - 環境変数の影響調査

## 技術的知見

### PyInstallerとC++拡張の相性
- C++拡張モジュールは特別な処理が必要
- 通常のPythonモジュールとは異なる初期化プロセス
- シンボリックリンクは避け、実ファイルを配置

### macOSの動的ライブラリ管理
- DYLD_LIBRARY_PATHは実行前に設定必要
- @rpathの解決は複雑
- コード署名が動的リンクに影響

### 環境非依存性の維持
- subprocess方式は完全に廃止済み
- 直接インポート方式を堅持
- Poetry/システムPython依存なし

## zlibエラーの再発（2025年6月23日 23:14）

### 問題の症状
runtime_hook簡略化後、torch._Cエラーは回避できたが、今度はlibrosawインポート時にzlibエラーが発生。

```
zlib.error: Error -5 while decompressing data: incomplete or truncated stream
発生場所: librosaインポート時
PyInstaller/loader/pyimod01_archive.py", line 129, in extract
```

### 以前の解決策（効果なし）
- PyInstallerキャッシュクリア済み
- runtime_hookを最小限に簡略化済み
- torch初期化を遅延化済み

### 根本原因の可能性
1. **PYZアーカイブの破損**
   - 大きなモジュールの圧縮に失敗
   - メモリ不足による不完全な圧縮
   
2. **圧縮設定の問題**
   - 現在のspecファイルで圧縮が有効になっている可能性
   - librosaのような大きなモジュールが圧縮に適さない

### 次の対策
1. specファイルでPYZ圧縮を完全無効化
2. librosaを除外して個別処理
3. 別のビルド方法を検討 