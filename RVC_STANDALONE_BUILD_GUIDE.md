# RVC スタンドアロンアプリ ビルドガイド & 現状課題

## 📋 概要

本ドキュメントは、RVC Voice Converterのスタンドアロンアプリ（arm64版・ユニバーサル版）の作成方法と、2025年6月時点での課題をまとめたものです。

## 🎯 現状（2025年6月22日）

### ✅ 成功している部分
- **arm64版スタンドアロンアプリ**: 完璧に動作、Poetryエラーなし
- **ユニバーサル版アプリ**: 完璧に動作、Poetryエラーなし
- **音声変換機能**: 両バージョンで正常動作

### ❌ 未解決の課題
- **DMG配布パッケージ**: hdiutil createプロセスでバイナリ破損、Poetryエラー発生

## 🔨 arm64版スタンドアロンアプリの作成方法

### 前提条件
- macOS (Apple Silicon推奨)
- Python 3.11（必須）
- Poetry環境構築済み

### ビルド手順

#### 1. Poetry環境の確認
```bash
# Poetry環境パスを確認
poetry env info --path
# 例: /Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11
```

#### 2. PyInstallerでビルド（最重要）
```bash
# ❌ 絶対に使わない（Poetryエラーの原因）
poetry run pyinstaller --clean --noconfirm rvc_minimal.spec

# ✅ 必ず直接パスで実行
/Users/norikene_satoshi/Library/Caches/pypoetry/virtualenvs/rvc-WP0SRWIz-py3.11/bin/pyinstaller --clean --noconfirm rvc_minimal.spec
```

#### 3. コード署名修復
```bash
# fix_codesign.shを実行
./fix_codesign.sh
```

#### 4. 動作確認
```bash
# アプリ起動
open dist/VoiceConverter.app
```

### 成功の鍵
- **Poetry直接パスビルド**: `poetry run`を使わず、Poetry環境のPython直接パスでPyInstallerを実行
- **理由**: スタンドアロンアプリ内でPoetryを呼び出すコードが埋め込まれるのを防ぐ

## 🌍 ユニバーサル版（Rosetta2対応）の作成方法

### 概要
真のuniversal2バイナリではなく、Rosetta2対応によりIntel Macでも動作する実用的アプローチ

### 作成手順

#### 1. create_universal_binary.sh実行
```bash
./create_universal_binary.sh
```

#### 2. 生成されるファイル
- `universal_build/VoiceConverter_universal.app`: Rosetta2対応版（両Mac対応）
- `universal_build/VoiceConverter_arm64.app`: arm64専用版（バックアップ）

### 技術詳細
- **アーキテクチャ**: arm64のみ（Intel MacではRosetta2で翻訳実行）
- **Info.plist設定**:
  - LSArchitecturePriority: ["arm64", "x86_64"]
  - LSMinimumSystemVersion: "10.15"
- **サイズ**: 約2.5GB

### 動作環境
- **Apple Silicon Mac**: ネイティブ実行、最高パフォーマンス
- **Intel Mac**: Rosetta2翻訳実行、実用的パフォーマンス
- **必要OS**: macOS 10.15 Catalina以降

## 🚨 現在の課題: DMG配布パッケージ作成

### 問題の詳細
DMG作成時にアプリバイナリが破損し、「Poetry not found」エラーが発生

### 検証結果
| 段階 | 状態 | 結果 |
|------|------|------|
| オリジナルアプリ | universal_build内 | ✅ 正常動作 |
| tar方式コピー後 | /tmp/dmg_test内 | ✅ 正常動作 |
| 署名・権限処理後 | /tmp/dmg_contents内 | ✅ 正常動作 |
| DMG作成後 | DMG内 | ❌ Poetryエラー |

### 試行済みの方法（全て失敗）

#### コピー方法
- `shutil.copytree()`: ❌ バイナリ破損
- `cp -pRP`: ❌ バイナリ破損  
- `rsync -a`: ❌ バイナリ破損
- `ditto`: ❌ バイナリ破損
- `tar -cpf`: ✅ 成功（ただしDMG作成で破損）

#### DMG形式
- UDRO（読み取り専用）: ❌ Poetryエラー
- UDRW（読み書き可能）: ❌ Poetryエラー
- UDZO（圧縮）: ❌ Poetryエラー

### 根本原因
`hdiutil create`プロセス自体がアプリバイナリを破損させている

## 📦 代替配布方法の検討

### 1. ZIP配布
- メリット: バイナリ破損なし、簡単
- デメリット: インストール手順が必要、見た目が素人っぽい

### 2. PKGインストーラー
- メリット: プロフェッショナル、自動インストール
- デメリット: 開発者証明書が必要、作成が複雑

### 3. 直接配布（.app）
- メリット: 最もシンプル、確実に動作
- デメリット: ダウンロード時の圧縮が必要

## 🎯 推奨事項

### 短期的解決策
1. ZIP形式での配布に切り替える
2. 詳細なインストールガイドを同梱

### 長期的解決策
1. Apple開発者証明書を取得
2. 正式な署名とnotarization
3. PKGインストーラーまたは正式なDMG作成

## 📝 まとめ

- **技術的成功**: スタンドアロンアプリ自体は完璧に動作
- **配布の課題**: DMG作成プロセスの問題のみ未解決
- **回避策**: ZIP配布で実用上の問題なし

---

最終更新: 2025年6月22日