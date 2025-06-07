#\!/bin/bash

# 保持するファイル・フォルダのリスト
KEEP_FILES=(
    "gui_dark_mode_enhanced.py"
    "enhanced_voice_converter.py" 
    "log_importance_analyzer.py"
    "rvc_config.py"
    "gui_modules"
    "gui_dark_mode.py"
    "pyproject.toml"
    "poetry.lock"
    "simple_complete_builder.py"
    "nuitka_config.py"
    "enhanced_output"
    "model_dir"
    "rvc"
    "CLAUDE.md"
    "README.md"
    "LICENSE"
    "trash"
    "dist_complete_gui"
    "configs"
    ".git"
    ".gitignore"
)

# バックアップディレクトリ
BACKUP_DIR="trash/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "🗂️  gui_dark_mode_enhanced.py関連ファイル以外をtrashに移動中..."

# 現在のディレクトリの全アイテムを確認
for item in *; do
    # .で始まるファイルをスキップ
    if [[ "$item" == .* ]]; then
        continue
    fi
    
    # 保持リストにあるかチェック
    should_keep=false
    for keep_item in "${KEEP_FILES[@]}"; do
        if [[ "$item" == "$keep_item" ]]; then
            should_keep=true
            break
        fi
    done
    
    # 保持リストにない場合はtrashに移動
    if [[ "$should_keep" == false ]]; then
        echo "📦 Moving: $item"
        mv "$item" "$BACKUP_DIR/"
    else
        echo "✅ Keeping: $item"
    fi
done

echo "✅ 移動完了: $BACKUP_DIR"
