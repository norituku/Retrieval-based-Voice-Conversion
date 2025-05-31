"""
デザインシステム
統一されたUIデザイントークンの定義
"""

class DesignTokens:
    """アプリケーション全体で使用するデザイントークン"""
    
    # カラーパレット - 視認性を向上
    colors = {
        # 背景階層
        'background_primary': '#0F0F10',    # わずかに青みがかった黒
        'background_secondary': '#1A1A1C',   # パネルとカード
        'background_tertiary': '#252528',    # 上昇したサーフェス
        'background_elevated': '#2F2F33',    # 最高の標高
        
        # サーフェスカラー
        'surface_card': '#1C1C1F',
        'surface_overlay': '#26262A',
        'surface_popover': '#2A2A2E',
        'surface_sidebar': '#141416',
        
        # テキストカラー（コントラストを改善）
        'text_primary': '#FFFFFF',
        'text_secondary': '#B8B8B8',
        'text_tertiary': '#808080',
        'text_disabled': '#505050',
        
        # ブランドカラー - 音楽/オーディオテーマ（より鮮やか）
        'accent_primary': '#5A9FFF',     # 明るい青
        'accent_secondary': '#8B6FFF',   # 紫
        'accent_tertiary': '#FF7A7A',    # コーラルレッド
        'accent_quaternary': '#5EDDD4',  # ティール
        
        # システムセマンティックカラー
        'success': '#52E88C',
        'warning': '#FFD23F',
        'error': '#FF6B6B',
        'info': '#6BB6FF',
        
        # インタラクティブ状態
        'hover': '#2A2A2E',
        'pressed': '#1F1F23',
        'focus': '#5A9FFF',
        'selection': '#5A9FFF33',
        
        # 分割線とボーダー
        'divider': '#2A2A2E',
        'border_subtle': '#2F2F33',
        'border_strong': '#505055',
    }
    
    # タイポグラフィ - SF Pro for macOS（よりコンパクト）
    typography = {
        'large_title': {'size': 28, 'weight': 'normal'},
        'title1': {'size': 22, 'weight': 'normal'},
        'title2': {'size': 18, 'weight': 'normal'},
        'title3': {'size': 16, 'weight': 'normal'},
        'headline': {'size': 14, 'weight': 'bold'},
        'body': {'size': 13, 'weight': 'normal'},
        'body_bold': {'size': 13, 'weight': 'bold'},
        'callout': {'size': 12, 'weight': 'normal'},
        'subheadline': {'size': 11, 'weight': 'normal'},
        'footnote': {'size': 10, 'weight': 'normal'},
        'caption1': {'size': 9, 'weight': 'normal'},
        'caption2': {'size': 9, 'weight': 'normal'},
    }
    
    # スペーシング - 超コンパクトグリッドシステム
    spacing = {
        'xxxs': 1,
        'xxs': 2,
        'xs': 3,
        'sm': 4,
        'md': 5,
        'lg': 6,
        'xl': 8,
        'xxl': 10,
        'xxxl': 12,
        'xxxxl': 16,
    }
    
    # コーナー半径
    radius = {
        'tiny': 2,
        'small': 3,
        'medium': 4,
        'large': 6,
        'extra_large': 8,
        'round': 999,
    }
    
    # レイアウト（コンパクト設定）
    layout = {
        'sidebar_width': 200,
        'min_window_width': 900,
        'min_window_height': 500,
        'toolbar_height': 35,
        'max_content_width': 650,
    }
    
    # フォントファミリーの定義
    fonts = {
        'family': 'SF Pro Display',
        'mono': 'SF Mono'
    }