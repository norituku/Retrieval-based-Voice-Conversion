# zlibエラー詳細ログ - 2025年6月24日

## エラー概要
- **エラータイプ**: `zlib.error: Error -5 while decompressing data: incomplete or truncated stream`
- **発生場所**: `librosa`モジュールのインポート時
- **詳細パス**: `/rvc/lib/audio.py` line 9
- **環境**: PyInstallerでビルドされたスタンドアロンアプリ内

## エラーの完全なスタックトレース
```
[23:14:45] ERROR: RVC実行エラー: Error -5 while decompressing data: incomplete or truncated stream
[23:14:45] ERROR: 詳細: Traceback (most recent call last):
  File "<string>", line 2104, in _run_rvc_direct
  File "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/dist/RVC Voice Converter Final.app/Contents/Frameworks/rvc/modules/vc/modules.py", line 13, in <module>
    from rvc.lib.audio import load_audio, wav2
  File "/Users/norikene_satoshi/Retrieval-based-Voice-Conversion/dist/RVC Voice Converter Final.app/Contents/Frameworks/rvc/lib/audio.py", line 9, in <module>
    import librosa
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "PyInstaller/loader/pyimod02_importers.py", line 446, in exec_module
  File "PyInstaller/loader/pyimod02_importers.py", line 383, in _check_name_wrapper
  File "PyInstaller/loader/pyimod02_importers.py", line 503, in get_code
  File "PyInstaller/loader/pyimod01_archive.py", line 129, in extract
zlib.error: Error -5 while decompressing data: incomplete or truncated stream
```

## エラーパターンの変遷
1. **Error -3**: incorrect header check（ヘッダーチェックエラー）
2. **Error -5**: incomplete or truncated stream（不完全なストリーム）

## 問題の根本原因分析
1. **PYZアーカイブの問題**
   - PyInstallerがlibrosaモジュールを圧縮する際にデータが破損
   - ファイルサイズが大きすぎてアーカイブが不完全

2. **librosaの特殊性**
   - 音声処理ライブラリとして非常に大きなモジュール
   - 多数の依存関係とバイナリファイルを含む

3. **PyInstallerの制限**
   - 大きなモジュールの圧縮/展開に問題がある
   - zlibによる圧縮が特定のファイルで失敗

## 試みた解決策
1. ✅ PyInstallerキャッシュのクリア
2. ✅ PYZ圧縮レベルを0に設定（無圧縮）
3. ✅ UPXを無効化
4. ✅ hiddenimportsにlibrosa関連を追加
5. ❌ noarchive=Trueオプション（まだ効果なし）

## 次の対処方針
1. **librosaを完全に除外してデータとして含める**
2. **OneFileモードからOneFolderモードへの変更**
3. **代替パッケージングツールの検討**
