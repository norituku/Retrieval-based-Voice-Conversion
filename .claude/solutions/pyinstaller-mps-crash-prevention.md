# PyInstaller環境でのMPSクラッシュ防止パターン

## 問題パターン
PyInstallerでパッケージ化したアプリケーションで、PyTorchのMPS（Metal Performance Shaders）を使用するとクラッシュが発生する。

**症状:**
- `EXC_CRASH (SIGABRT)`
- `MTLReleaseAssertionFailure`
- `metal gpu stream`でのクラッシュ

## 解決パターン

### 1. 環境変数による無効化（runtime_hook.py）

```python
import os
import sys

# MPS（Metal Performance Shaders）を完全に無効化
os.environ['PYTORCH_DISABLE_MPS'] = '1'
os.environ['PYTORCH_NO_MPS'] = '1'
os.environ['PYTORCH_USE_MPS'] = '0'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
```

### 2. 環境判定による条件分岐

**PyInstaller環境の判定:**
```python
import sys

def is_pyinstaller_env():
    return hasattr(sys, '_MEIPASS')

# 使用例
if is_pyinstaller_env():
    device = torch.device("cpu")  # PyInstaller環境ではCPU強制
else:
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
```

### 3. デバイス選択ロジックのテンプレート

```python
import torch
import sys

def get_optimal_device():
    """環境に応じた最適なデバイスを取得"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller環境: CPU強制（安定性重視）
        return torch.device("cpu")
    
    # 開発環境: 利用可能な最高性能デバイス
    if torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")
```

### 4. 設定クラスでの対応

```python
import sys
import torch

class Config:
    @staticmethod
    def has_mps() -> bool:
        """PyInstaller環境ではMPSを無効化"""
        if hasattr(sys, '_MEIPASS'):
            return False
        return torch.backends.mps.is_available()
    
    @staticmethod
    def get_device() -> torch.device:
        """環境に応じたデバイスを取得"""
        if hasattr(sys, '_MEIPASS'):
            return torch.device("cpu")
        return torch.device("mps" if Config.has_mps() else "cpu")
```

### 5. エラーハンドリング付きデバイス設定

```python
def setup_device_with_fallback():
    """エラーハンドリング付きでデバイスを設定"""
    try:
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller環境では常にCPU
            device = torch.device("cpu")
            print("PyInstaller環境検出 - CPU モードを強制使用")
        elif torch.backends.mps.is_available():
            # MPSテスト実行
            test_tensor = torch.zeros(1).to("mps")
            device = torch.device("mps")
            print("MPS (Apple Silicon) を使用")
        else:
            device = torch.device("cpu")
            print("CPU モードで実行")
    except Exception as e:
        # MPSエラー時のフォールバック
        device = torch.device("cpu")
        print(f"GPU使用に失敗、CPUにフォールバック: {e}")
    
    return device
```

## 適用箇所チェックリスト

### 必須修正ファイル
- [ ] `hooks/runtime_hook.py` - 環境変数設定
- [ ] メインアプリ（GUI等） - デバイス選択ロジック
- [ ] 設定クラス - `has_mps()`等のメソッド
- [ ] パイプライン処理 - モデル実行部分

### 修正パターン

**1. 初期化時のデバイス設定**
```python
# Before
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# After  
device = torch.device("cpu" if hasattr(sys, '_MEIPASS') else 
                     ("mps" if torch.backends.mps.is_available() else "cpu"))
```

**2. 条件判定の修正**
```python
# Before
if torch.backends.mps.is_available():
    # MPS処理

# After
if torch.backends.mps.is_available() and not hasattr(sys, '_MEIPASS'):
    # MPS処理（開発環境のみ）
```

**3. 設定メソッドの修正**
```python
# Before
def has_gpu():
    return torch.backends.mps.is_available() or torch.cuda.is_available()

# After
def has_gpu():
    if hasattr(sys, '_MEIPASS'):
        return False  # PyInstaller環境では無効
    return torch.backends.mps.is_available() or torch.cuda.is_available()
```

## 検証方法

### 1. ビルド前テスト
```python
# テストスクリプト
import sys
import torch

print(f"PyInstaller env: {hasattr(sys, '_MEIPASS')}")
print(f"MPS available: {torch.backends.mps.is_available()}")

try:
    device = get_optimal_device()
    test_tensor = torch.zeros(1).to(device)
    print(f"Device test successful: {device}")
except Exception as e:
    print(f"Device test failed: {e}")
```

### 2. ビルド後確認
- アプリ起動時のデバイスログ確認
- 音声変換テスト実行
- クラッシュ発生の有無確認

## 注意事項

### パフォーマンス影響
- CPU処理は GPU/MPS より低速
- 長時間処理では顕著な差が発生する可能性
- ユーザーへの適切な時間予測表示を推奨

### 開発環境との差異
- 開発環境: MPS使用可能（高速）
- PyInstaller: CPU専用（安定）
- 機能差異が発生しないよう注意

### 将来的な改善案
- PyInstallerでのMetal対応改善を待つ
- 代替GPU加速手法の検討
- 処理の最適化によるCPU性能向上

---

**作成日:** 2025年6月24日  
**適用対象:** PyTorch + PyInstaller プロジェクト  
**重要度:** 🚨 高（クラッシュ防止） 