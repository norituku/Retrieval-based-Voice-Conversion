#!/usr/bin/env python3
"""
NumPy形式のインデックスファイルをFAISS形式に変換するスクリプト
"""

import os
import sys
import numpy as np
import faiss
from pathlib import Path

def convert_numpy_to_faiss_index(numpy_file_path, output_path=None):
    """NumPy配列をFAISS IndexFlatL2に変換"""
    if not os.path.exists(numpy_file_path):
        print(f"❌ ファイルが見つかりません: {numpy_file_path}")
        return False
    
    try:
        # NumPy配列を読み込み
        print(f"📖 NumPy配列を読み込み中: {numpy_file_path}")
        features = np.load(numpy_file_path)
        print(f"✅ 配列形状: {features.shape}")
        print(f"✅ データ型: {features.dtype}")
        
        # float32に変換（FAISSの要件）
        if features.dtype != np.float32:
            print(f"🔄 {features.dtype} → float32 に変換中...")
            features = features.astype(np.float32)
        
        # 2次元配列かチェック
        if len(features.shape) != 2:
            print(f"❌ 2次元配列が必要です。現在の形状: {features.shape}")
            return False
        
        # FAISS IndexFlatL2を作成
        dimension = features.shape[1]
        print(f"🔧 FAISS IndexFlatL2を作成中（次元: {dimension}）...")
        index = faiss.IndexFlatL2(dimension)
        
        # ベクトルを追加
        print(f"📥 {features.shape[0]}個のベクトルを追加中...")
        index.add(features)
        
        # 出力パスを決定
        if output_path is None:
            output_path = str(numpy_file_path).replace('.index', '_faiss.index')
        
        # FAISSインデックスを保存
        print(f"💾 FAISSインデックスを保存中: {output_path}")
        faiss.write_index(index, output_path)
        
        # 検証
        print("🔍 保存されたインデックスを検証中...")
        test_index = faiss.read_index(output_path)
        print(f"✅ 検証成功: {test_index.ntotal}個のベクトル")
        
        return output_path
        
    except Exception as e:
        print(f"❌ 変換エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_and_convert_numpy_indices(model_dir):
    """model_dirでNumPy形式のインデックスファイルを探して変換"""
    model_path = Path(model_dir)
    if not model_path.exists():
        print(f"❌ モデルディレクトリが見つかりません: {model_dir}")
        return
    
    print(f"🔍 NumPy形式のインデックスファイルを検索中: {model_dir}")
    
    converted_count = 0
    for index_file in model_path.rglob("*.index"):
        # ファイルヘッダーをチェック
        try:
            with open(index_file, 'rb') as f:
                header = f.read(8)
            
            if header.startswith(b'\x93NUM'):
                print(f"\n📁 NumPy形式のファイルを発見: {index_file}")
                output_path = str(index_file).replace('.index', '_faiss.index')
                
                result = convert_numpy_to_faiss_index(str(index_file), output_path)
                if result:
                    print(f"✅ 変換成功: {result}")
                    converted_count += 1
                    
                    # 元のファイルをバックアップ
                    backup_path = str(index_file) + '.numpy_backup'
                    os.rename(str(index_file), backup_path)
                    print(f"💾 元ファイルをバックアップ: {backup_path}")
                    
                    # FAISSファイルを元の名前にリネーム
                    os.rename(result, str(index_file))
                    print(f"🔄 FAISSファイルを元の名前に変更: {index_file}")
                else:
                    print(f"❌ 変換失敗: {index_file}")
            else:
                print(f"✅ 既にFAISS形式: {index_file}")
                
        except Exception as e:
            print(f"⚠️ ファイル確認エラー: {index_file} - {e}")
    
    print(f"\n📊 変換結果: {converted_count}個のファイルを変換しました")

def main():
    print("🔧 RVC インデックスファイル修復ツール")
    print("=" * 50)
    
    # アプリ内のmodel_dirを確認
    app_model_dirs = [
        "/Applications/VoiceConverter.app/Contents/Resources/model_dir",
        "model_dir",
        "./model_dir"
    ]
    
    for model_dir in app_model_dirs:
        if os.path.exists(model_dir):
            print(f"\n🎯 対象ディレクトリ: {model_dir}")
            find_and_convert_numpy_indices(model_dir)
        else:
            print(f"⏭️ スキップ（存在しない）: {model_dir}")
    
    print("\n✅ 処理完了！")
    print("\n📋 説明:")
    print("- NumPy形式（.npy）のインデックスファイルをFAISS形式に変換しました")
    print("- 元のファイルは .numpy_backup として保存されています")
    print("- 変換後のファイルは音声変換で正常に使用できます")
    
if __name__ == "__main__":
    try:
        import faiss
        main()
    except ImportError:
        print("❌ FAISSライブラリが見つかりません")
        print("Poetry環境で実行してください:")
        print("poetry run python fix_index_files.py")
        sys.exit(1)