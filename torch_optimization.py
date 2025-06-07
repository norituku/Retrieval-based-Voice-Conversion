#!/usr/bin/env python3
"""
PyTorch Nuitka最適化スクリプト
CPUのみ版への変換とサイズ削減
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
import json
import time

class PyTorchOptimizer:
    """PyTorch最適化クラス"""
    
    def __init__(self):
        self.poetry_env = self.detect_poetry_env()
        self.optimization_report = {
            'start_time': time.time(),
            'checks': {},
            'optimizations': {},
            'results': {}
        }
    
    def detect_poetry_env(self):
        """Poetry環境の検出"""
        # Poetry環境のPythonパスを取得
        try:
            result = subprocess.run(['poetry', 'run', 'which', 'python'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return None
    
    def analyze_pytorch_installation(self):
        """PyTorchインストール状況の分析"""
        print("🔍 PyTorch環境分析開始...")
        
        # Poetry環境でのPyTorch確認
        if self.poetry_env:
            try:
                result = subprocess.run([self.poetry_env, '-c', '''
import json
import sys
try:
    import torch
    info = {
        "version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False,
        "path": torch.__file__,
        "size_estimate": "unknown"
    }
    print(json.dumps(info))
except ImportError as e:
    print(json.dumps({"error": str(e)}))
'''], capture_output=True, text=True)
                
                if result.returncode == 0:
                    torch_info = json.loads(result.stdout)
                    self.optimization_report['checks']['pytorch'] = torch_info
                    
                    print(f"✅ PyTorch検出: v{torch_info.get('version', 'unknown')}")
                    print(f"   CUDA: {'有効' if torch_info.get('cuda_available') else '無効'}")
                    print(f"   MPS: {'有効' if torch_info.get('mps_available') else '無効'}")
                    
                    return torch_info
                else:
                    print("❌ PyTorchが見つかりません")
                    self.optimization_report['checks']['pytorch'] = {"error": "Not found"}
                    return None
                    
            except Exception as e:
                print(f"❌ PyTorch分析エラー: {e}")
                self.optimization_report['checks']['pytorch'] = {"error": str(e)}
                return None
        else:
            print("⚠️ Poetry環境が検出されませんでした")
            return None
    
    def check_dependencies_size(self):
        """依存関係のサイズチェック"""
        print("\n📊 依存関係サイズ分析...")
        
        packages_to_check = [
            'torch',
            'numpy',
            'scipy',
            'librosa',
            'fairseq',
            'soundfile',
            'numba'
        ]
        
        size_info = {}
        
        if self.poetry_env:
            for package in packages_to_check:
                try:
                    result = subprocess.run([self.poetry_env, '-c', f'''
import json
try:
    import {package}
    import os
    from pathlib import Path
    
    pkg_path = Path({package}.__file__).parent
    total_size = sum(f.stat().st_size for f in pkg_path.rglob("*") if f.is_file())
    
    info = {{
        "package": "{package}",
        "path": str(pkg_path),
        "size_mb": total_size / 1024 / 1024,
        "files": len(list(pkg_path.rglob("*")))
    }}
    print(json.dumps(info))
except Exception as e:
    print(json.dumps({{"package": "{package}", "error": str(e)}}))
'''], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        info = json.loads(result.stdout)
                        size_info[package] = info
                        
                        if 'size_mb' in info:
                            print(f"  {package:12}: {info['size_mb']:>8.1f} MB ({info.get('files', 0):,} files)")
                        else:
                            print(f"  {package:12}: エラー - {info.get('error', 'Unknown')}")
                            
                except Exception as e:
                    print(f"  {package:12}: 分析失敗 - {e}")
                    size_info[package] = {"error": str(e)}
        
        self.optimization_report['checks']['package_sizes'] = size_info
        
        # 総サイズ計算
        total_size = sum(pkg.get('size_mb', 0) for pkg in size_info.values() if 'size_mb' in pkg)
        print(f"\n📦 総依存関係サイズ: {total_size:.1f} MB")
        
        return size_info
    
    def create_optimization_recommendations(self):
        """最適化推奨事項の作成"""
        print("\n💡 最適化推奨事項...")
        
        recommendations = []
        
        # PyTorch最適化
        pytorch_info = self.optimization_report['checks'].get('pytorch', {})
        if pytorch_info.get('cuda_available'):
            recommendations.append({
                'priority': 'HIGH',
                'action': 'PyTorchをCPU版に置き換え',
                'command': 'pip uninstall torch && pip install torch --index-url https://download.pytorch.org/whl/cpu',
                'savings': '~1.5GB'
            })
        
        # 大きなパッケージの最適化
        package_sizes = self.optimization_report['checks'].get('package_sizes', {})
        for pkg_name, pkg_info in package_sizes.items():
            if pkg_info.get('size_mb', 0) > 100:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'action': f'{pkg_name}の最適化を検討',
                    'size': f"{pkg_info['size_mb']:.1f} MB",
                    'suggestion': 'Nuitkaの--nofollow-import-toで部分的に除外可能'
                })
        
        self.optimization_report['recommendations'] = recommendations
        
        # 推奨事項の表示
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['priority']}] {rec['action']}")
            if 'command' in rec:
                print(f"   コマンド: {rec['command']}")
            if 'savings' in rec:
                print(f"   削減可能: {rec['savings']}")
            if 'suggestion' in rec:
                print(f"   提案: {rec['suggestion']}")
        
        return recommendations
    
    def export_optimization_config(self):
        """Nuitka用最適化設定のエクスポート"""
        print("\n📝 Nuitka最適化設定を生成...")
        
        nuitka_config = {
            'plugins': [
                'tk-inter',
                'numpy',
                'anti-bloat'
            ],
            'include_packages': [
                'rvc',
                'numpy',
                'scipy.signal',
                'soundfile'
            ],
            'nofollow_imports': []
        }
        
        # PyTorch最適化
        pytorch_info = self.optimization_report['checks'].get('pytorch', {})
        if pytorch_info and not pytorch_info.get('error'):
            if pytorch_info.get('cuda_available'):
                nuitka_config['nofollow_imports'].extend([
                    'torch.cuda',
                    'torch.distributed',
                    'torch.nn.parallel'
                ])
            
            if pytorch_info.get('mps_available'):
                nuitka_config['plugins'].append('torch')
        else:
            # PyTorchが利用できない場合は完全に除外
            nuitka_config['nofollow_imports'].append('torch')
        
        # 大きなパッケージの部分除外
        package_sizes = self.optimization_report['checks'].get('package_sizes', {})
        
        # matplotlib, IPython等の不要なパッケージ
        nuitka_config['nofollow_imports'].extend([
            'matplotlib',
            'IPython',
            'jupyter',
            'notebook',
            'pytest',
            'sphinx',
            'setuptools',
            'pip',
            'wheel'
        ])
        
        # fairseqの最適化（大きい場合）
        if package_sizes.get('fairseq', {}).get('size_mb', 0) > 20:
            nuitka_config['nofollow_imports'].extend([
                'fairseq.distributed',
                'fairseq.benchmark',
                'fairseq.model_parallel'
            ])
        
        self.optimization_report['nuitka_config'] = nuitka_config
        
        # 設定ファイルの保存
        config_path = Path('nuitka_optimization_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(nuitka_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 最適化設定を保存: {config_path}")
        
        return nuitka_config
    
    def generate_optimization_report(self):
        """最適化レポートの生成"""
        self.optimization_report['end_time'] = time.time()
        self.optimization_report['duration'] = self.optimization_report['end_time'] - self.optimization_report['start_time']
        
        report_path = Path('pytorch_optimization_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 最適化レポートを保存: {report_path}")
        
        # サマリー表示
        print("\n🎯 最適化サマリー:")
        print("=" * 60)
        
        if 'pytorch' in self.optimization_report['checks']:
            pytorch = self.optimization_report['checks']['pytorch']
            if not pytorch.get('error'):
                print(f"PyTorch: v{pytorch.get('version', 'unknown')}")
                print(f"  - CUDA: {'有効（要最適化）' if pytorch.get('cuda_available') else '無効（最適）'}")
                print(f"  - MPS: {'有効' if pytorch.get('mps_available') else '無効'}")
        
        total_size = sum(
            pkg.get('size_mb', 0) 
            for pkg in self.optimization_report['checks'].get('package_sizes', {}).values() 
            if 'size_mb' in pkg
        )
        print(f"\n総依存関係サイズ: {total_size:.1f} MB")
        
        recommendations = self.optimization_report.get('recommendations', [])
        high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
        if high_priority:
            print(f"\n⚠️ 高優先度の最適化: {len(high_priority)}件")
        
        print(f"\n実行時間: {self.optimization_report['duration']:.2f}秒")
        
        return self.optimization_report

def main():
    """メイン実行関数"""
    print("🚀 PyTorch Nuitka最適化分析")
    print("=" * 60)
    
    optimizer = PyTorchOptimizer()
    
    # 分析実行
    optimizer.analyze_pytorch_installation()
    optimizer.check_dependencies_size()
    optimizer.create_optimization_recommendations()
    optimizer.export_optimization_config()
    report = optimizer.generate_optimization_report()
    
    print("\n✅ PyTorch最適化分析完了！")
    
    return report

if __name__ == "__main__":
    main()