#!/usr/bin/env python3
"""
Tiker Analysis Runner
統一株式分析エンジンの実行スクリプト
"""

import argparse
from typing import NoReturn
from src.analysis.unified_analyzer import main as unified_analyzer_main


def main() -> NoReturn:
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(description='Tiker Stock Analysis')
    parser.add_argument('--ticker', type=str, required=True, help='Stock ticker symbol')
    parser.add_argument('--date', type=str, help='Analysis date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 分析実行（引数を直接渡す）
    if args.date:
        # NOTE: unified_analyzer.pyで引数処理を改善する必要がある
        import sys
        sys.argv = ['unified_analyzer', '--ticker', args.ticker, '--date', args.date]
    else:
        import sys
        sys.argv = ['unified_analyzer', '--ticker', args.ticker]
    
    unified_analyzer_main()


if __name__ == "__main__":
    main()