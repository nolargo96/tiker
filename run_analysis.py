#!/usr/bin/env python3
"""
Tiker Analysis Runner
統一株式分析エンジンの実行スクリプト
"""

import sys
import os
import argparse

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 新しいパッケージ構造からインポート
from src.analysis.unified_analyzer import main as unified_analyzer_main

if __name__ == "__main__":
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='Tiker Stock Analysis')
    parser.add_argument('--ticker', type=str, required=True, help='Stock ticker symbol')
    parser.add_argument('--date', type=str, help='Analysis date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 引数を sys.argv に設定して実行
    sys.argv = ['unified_analyzer', '--ticker', args.ticker]
    if args.date:
        sys.argv.extend(['--date', args.date])
    
    # 分析実行
    unified_analyzer_main()