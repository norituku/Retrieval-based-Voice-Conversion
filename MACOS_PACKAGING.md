# RVC macOSアプリケーション パッケージングガイド

## 概要

このガイドでは、RVC Voice Converterを他のMacでワンクリック実行できるmacOSアプリケーションとして配布するための2つの手法を説明します。

## 🎯 推奨アプローチの選択

### Option 1: 軽量版（Platypus） - **推奨**
- **ファイルサイズ**: 50MB以下
- **配布形式**: DMG (軽量)
- **特徴**: 初回実行時に依存関係を自動インストール
- **適用場面**: 一般配布、開発版

### Option 2: スタンドアロン版（PyInstaller）
- **ファイルサイズ**: 3-5GB
- **配布形式**: DMG (大容量)
- **特徴**: すべての依存関係が含まれた完全パッケージ
- **適用場面**: エンタープライズ配布、オフライン環境

---

## 🚀 Option 1: 軽量版（Platypus）の作成

### 前提条件
```bash
# Homebrew（必須）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Platypus（必須）
brew install --cask platypus
```

### 作成手順
```bash
# 1. アプリケーション作成スクリプトの実行
./create_macos_app.sh

# 2. DMG作成確認（推奨: Y）
# DMGディスクイメージを作成しますか？ (y/N): y
```

### 成果物
- `RVC Voice Converter.app` - macOSアプリケーション
- `RVC-Voice-Converter-v1.0.dmg` - 配布用DMG（オプション）

### 特徴・動作フロー
1. **初回起動時**:
   - Homebrew自動インストール（未インストールの場合）
   - Python 3.11 + python-tk自動インストール
   - Poetry自動インストール
   - RVC依存関係自動インストール
   - GUI起動

2. **2回目以降**:
   - 依存関係チェック（高速）
   - GUI即座起動

### メリット・デメリット

**✅ メリット:**
- 軽量（50MB以下）
- 高速配布・ダウンロード
- メンテナンス性が高い
- 既存のrun_gui.shロジックを最大活用

**⚠️ デメリット:**
- 初回起動時にインターネット接続必須
- 依存関係インストールに5-10分必要
- 管理者権限が必要な場合がある

---

## 🏗️ Option 2: スタンドアロン版（PyInstaller）の作成

### 前提条件
```bash
# Poetry環境で実行（既存環境使用）
poetry install

# PyInstaller（スクリプトが自動インストール）
```

### 作成手順
```bash
# 1. スタンドアロンアプリ作成スクリプトの実行
python create_standalone_app.py

# 2. 作成プロセス実行（15-30分程度）
# ⚠️ 大容量ファイルの処理のため時間がかかります

# 3. DMG作成確認（推奨: Y）
# DMGディスクイメージを作成しますか？ (y/N): y
```

### 成果物
- `dist/RVC Voice Converter.app` - スタンドアロンアプリケーション
- `RVC-Voice-Converter-Standalone-v1.0.dmg` - 配布用DMG

### 特徴・動作フロー
1. **起動時**:
   - 依存関係チェック不要（全てバンドル済み）
   - GUI即座起動
   - インターネット接続不要

### メリット・デメリット

**✅ メリット:**
- 完全スタンドアロン（インターネット不要）
- 即座に実行可能
- 依存関係トラブルが発生しない

**⚠️ デメリット:**
- 大容量（3-5GB）
- 配布・ダウンロードに時間がかかる
- tkinter互換性問題が残る可能性

---

## 📋 配布とインストール

### ユーザー向けインストール手順

#### 軽量版の場合
1. DMGファイルをダウンロード・マウント
2. `RVC Voice Converter.app`をApplicationsフォルダにドラッグ&ドロップ
3. アプリを起動（初回は依存関係インストールで5-10分）
4. セキュリティ警告が表示された場合：
   - システム環境設定 → セキュリティとプライバシー → 一般
   - 「このまま開く」をクリック

#### スタンドアロン版の場合
1. DMGファイルをダウンロード・マウント（大容量のため時間がかかる）
2. `RVC Voice Converter.app`をApplicationsフォルダにドラッグ&ドロップ
3. アプリを起動（即座に利用可能）
4. セキュリティ警告対応は軽量版と同様

---

## 🔧 開発者向け情報

### ファイル構成
```
RVC Voice Converter.app/
├── Contents/
│   ├── Info.plist              # アプリメタデータ
│   ├── MacOS/
│   │   └── RVC Voice Converter # 実行ファイル
│   ├── Resources/
│   │   ├── run_gui_app.sh      # 起動スクリプト（軽量版）
│   │   ├── rvc_icon.icns       # アプリアイコン
│   │   └── [依存関係]          # PyInstallerバンドル（スタンドアロン版）
│   └── Frameworks/             # 共有ライブラリ（必要に応じて）
```

### カスタマイズポイント

#### アプリ情報の変更
- `create_macos_app.sh` 内の変数を編集:
  ```bash
  APP_NAME="Your App Name"
  ```

#### アイコンの変更
- `app_icons/rvc_icon.icns` を置き換え

#### バンドルIDの変更
- セキュリティ上、独自のBundle IDを使用推奨:
  ```bash
  -I "com.yourcompany.yourapp"
  ```

### コード署名とノータリゼーション（高度）

Apple Developer Programメンバーの場合、追加のセキュリティ強化が可能：

```bash
# コード署名
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" "RVC Voice Converter.app"

# ノータリゼーション送信
xcrun notarytool submit "RVC-Voice-Converter-v1.0.dmg" --keychain-profile "YourProfile" --wait

# ノータリゼーションチケット添付
xcrun stapler staple "RVC Voice Converter.app"
```

---

## 🧪 テストとトラブルシューティング

### 基本テスト手順
1. **清潔な環境でのテスト**:
   - 新しいmacOS仮想マシンまたは別のMac
   - Homebrew/Poetry未インストール環境

2. **機能テスト**:
   - アプリケーション起動
   - モデル読み込み
   - 音声変換実行
   - 設定保存・読み込み

### よくある問題と解決策

#### 「開発元が未確認」エラー
```bash
# 解決方法:
# システム環境設定 → セキュリティとプライバシー → 一般
# → "このまま開く"をクリック
```

#### tkinter関連エラー
```bash
# 軽量版の場合、python-tkの自動インストールで解決
# スタンドアロン版の場合、PyInstaller設定の調整が必要
```

#### 初回起動の長時間化
```bash
# 軽量版の正常動作です
# プログレス表示の改善が今後の課題
```

---

## 📊 性能比較

| 項目 | 軽量版 (Platypus) | スタンドアロン版 (PyInstaller) |
|------|-------------------|------------------------------|
| ファイルサイズ | 50MB以下 | 3-5GB |
| 配布時間 | 数秒 | 数分-数時間 |
| 初回起動時間 | 5-10分 | 即座 |
| インターネット要件 | 初回のみ必要 | 不要 |
| メンテナンス性 | 高 | 中 |
| 互換性 | 高 | 中-高 |

---

## 🎯 推奨用途

### 軽量版（Platypus）
- ✅ 一般ユーザー向け配布
- ✅ 開発・テスト版
- ✅ 頻繁なアップデート
- ✅ インターネット接続が期待できる環境

### スタンドアロン版（PyInstaller）
- ✅ エンタープライズ環境
- ✅ オフライン環境
- ✅ 一回限りのデモ・プレゼンテーション
- ✅ 技術的なサポートが困難な環境

---

## 📞 サポート

### トラブルシューティング
1. 本ドキュメントの確認
2. GitHub Issues での報告
3. 詳細なログ情報の提供

### 今後の改善予定
- [ ] 自動更新機能
- [ ] プログレス表示の改善
- [ ] Apple Silicon最適化
- [ ] App Store配布対応