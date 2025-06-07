#!/usr/bin/env python3
"""
RVC Voice Converter アプリアイコン生成スクリプト
音声変換をテーマにしたmacOSアプリアイコンを作成
"""
import os
import sys
import subprocess
from pathlib import Path

class RVCIconGenerator:
    """RVCアプリアイコン生成クラス"""
    
    def __init__(self, output_dir="app_icons"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # アイコンサイズ定義（macOS標準）
        self.icon_sizes = [
            16, 32, 64, 128, 256, 512, 1024
        ]
    
    def create_svg_icon(self):
        """SVGアイコンの作成"""
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- グラデーション定義 -->
    <linearGradient id="backgroundGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2d2d2d;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="micGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#007acc;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#4CAF50;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#007acc;stop-opacity:0.8" />
      <stop offset="50%" style="stop-color:#4CAF50;stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:#007acc;stop-opacity:0.8" />
    </linearGradient>
  </defs>
  
  <!-- 背景（角丸四角形） -->
  <rect x="64" y="64" width="896" height="896" rx="160" ry="160" fill="url(#backgroundGradient)" stroke="#007acc" stroke-width="8"/>
  
  <!-- マイクロフォン本体 -->
  <ellipse cx="512" cy="350" rx="80" ry="120" fill="url(#micGradient)" stroke="#ffffff" stroke-width="6"/>
  
  <!-- マイクロフォンスタンド -->
  <rect x="490" y="470" width="44" height="200" fill="url(#micGradient)" stroke="#ffffff" stroke-width="4"/>
  
  <!-- マイクロフォンベース -->
  <ellipse cx="512" cy="720" rx="120" ry="30" fill="url(#micGradient)" stroke="#ffffff" stroke-width="4"/>
  
  <!-- 音波エフェクト（左側） -->
  <path d="M 350 300 Q 280 350 350 400" stroke="url(#waveGradient)" stroke-width="12" fill="none" stroke-linecap="round"/>
  <path d="M 320 280 Q 220 350 320 420" stroke="url(#waveGradient)" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M 290 260 Q 160 350 290 440" stroke="url(#waveGradient)" stroke-width="8" fill="none" stroke-linecap="round"/>
  
  <!-- 音波エフェクト（右側） -->
  <path d="M 674 300 Q 744 350 674 400" stroke="url(#waveGradient)" stroke-width="12" fill="none" stroke-linecap="round"/>
  <path d="M 704 280 Q 804 350 704 420" stroke="url(#waveGradient)" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M 734 260 Q 864 350 734 440" stroke="url(#waveGradient)" stroke-width="8" fill="none" stroke-linecap="round"/>
  
  <!-- 変換矢印 -->
  <path d="M 512 520 L 512 580 M 492 560 L 512 580 L 532 560" stroke="#ffffff" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  
  <!-- RVCテキスト -->
  <text x="512" y="850" font-family="Arial, sans-serif" font-size="80" font-weight="bold" text-anchor="middle" fill="#ffffff">RVC</text>
  
  <!-- 小さな音符装飾 -->
  <circle cx="200" cy="200" r="8" fill="#4CAF50"/>
  <circle cx="824" cy="200" r="8" fill="#4CAF50"/>
  <circle cx="200" cy="824" r="8" fill="#007acc"/>
  <circle cx="824" cy="824" r="8" fill="#007acc"/>
</svg>'''
        
        svg_path = self.output_dir / "rvc_icon.svg"
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"✅ SVGアイコンを作成: {svg_path}")
        return svg_path
    
    def convert_to_png_sizes(self, svg_path):
        """SVGを各サイズのPNGに変換"""
        png_files = []
        
        # macOSに標準インストールされているpython-wand（ImageMagick）を試行
        try:
            # rsvg-convert（librsvg）を使用
            for size in self.icon_sizes:
                png_path = self.output_dir / f"icon_{size}x{size}.png"
                
                # rsvg-convertコマンドの実行
                cmd = [
                    "rsvg-convert",
                    "-w", str(size),
                    "-h", str(size),
                    "--keep-aspect-ratio",
                    "--output", str(png_path),
                    str(svg_path)
                ]
                
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    png_files.append(png_path)
                    print(f"  ✅ {size}x{size} PNG作成完了")
                except subprocess.CalledProcessError:
                    print(f"  ⚠️ {size}x{size} PNG作成スキップ（rsvg-convert不使用）")
                    
        except Exception as e:
            print(f"⚠️ PNG変換をスキップ: {e}")
        
        # sipsコマンド（macOS標準）を使用した変換も試行
        if not png_files:
            try:
                for size in self.icon_sizes:
                    png_path = self.output_dir / f"icon_{size}x{size}.png"
                    
                    # sipsコマンドでSVGからPNGへ変換
                    cmd = [
                        "sips",
                        "-s", "format", "png",
                        "-Z", str(size),
                        str(svg_path),
                        "--out", str(png_path)
                    ]
                    
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                        png_files.append(png_path)
                        print(f"  ✅ {size}x{size} PNG作成完了（sips使用）")
                    except subprocess.CalledProcessError:
                        print(f"  ⚠️ {size}x{size} PNG作成失敗（sips）")
            except Exception as e:
                print(f"⚠️ sips変換失敗: {e}")
        
        return png_files
    
    def create_icns_file(self, png_files):
        """PNGファイルから.icnsファイルを作成"""
        if not png_files:
            print("⚠️ PNGファイルがないため.icns作成をスキップ")
            return None
        
        icns_path = self.output_dir / "rvc_app_icon.icns"
        
        try:
            # iconutilを使用して.icnsファイルを作成
            iconset_dir = self.output_dir / "rvc_icon.iconset"
            iconset_dir.mkdir(exist_ok=True)
            
            # iconset用のファイル名規則に従ってコピー
            iconset_mapping = {
                16: "icon_16x16.png",
                32: ["icon_16x16@2x.png", "icon_32x32.png"],
                64: "icon_32x32@2x.png",
                128: ["icon_64x64@2x.png", "icon_128x128.png"],
                256: ["icon_128x128@2x.png", "icon_256x256.png"],
                512: ["icon_256x256@2x.png", "icon_512x512.png"],
                1024: "icon_512x512@2x.png"
            }
            
            for size in self.icon_sizes:
                source_file = self.output_dir / f"icon_{size}x{size}.png"
                if source_file.exists():
                    mapping = iconset_mapping.get(size, [])
                    if isinstance(mapping, str):
                        mapping = [mapping]
                    
                    for target_name in mapping:
                        target_path = iconset_dir / target_name
                        subprocess.run(["cp", str(source_file), str(target_path)], check=True)
            
            # iconutilでicnsファイルを作成
            cmd = ["iconutil", "-c", "icns", str(iconset_dir)]
            subprocess.run(cmd, check=True, capture_output=True)
            
            print(f"✅ .icnsファイルを作成: {icns_path}")
            return icns_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ .icns作成失敗: {e}")
            return None
        except Exception as e:
            print(f"❌ .icns作成エラー: {e}")
            return None
    
    def generate_app_icon(self):
        """完全なアプリアイコン生成プロセス"""
        print("🎨 RVC Voice Converter アプリアイコン生成開始")
        print("=" * 60)
        
        # 1. SVGアイコン作成
        svg_path = self.create_svg_icon()
        
        # 2. PNGサイズ変換
        print("\n📐 PNGサイズ変換中...")
        png_files = self.convert_to_png_sizes(svg_path)
        
        # 3. .icnsファイル作成
        print("\n🔧 .icnsファイル作成中...")
        icns_path = self.create_icns_file(png_files)
        
        # 4. 結果レポート
        print("\n📊 アイコン生成結果:")
        print(f"  SVGソース: ✅ {svg_path}")
        print(f"  PNGファイル: {len(png_files)}個")
        if icns_path:
            print(f"  .icnsファイル: ✅ {icns_path}")
        else:
            print(f"  .icnsファイル: ❌ 作成失敗")
        
        return {
            'svg_path': svg_path,
            'png_files': png_files,
            'icns_path': icns_path,
            'success': icns_path is not None
        }

def main():
    """メイン実行関数"""
    generator = RVCIconGenerator()
    result = generator.generate_app_icon()
    
    if result['success']:
        print("\n🎉 アプリアイコン生成完了！")
        return True
    else:
        print("\n⚠️ アイコン生成は部分的に完了")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)