from typing import Tuple
from src.analysis.stock_analysis_runner import StockAnalysisRunner


def main() -> Tuple[bool, str]:
    """TSLA株価分析スクリプト"""
    return StockAnalysisRunner.run_ticker_analysis("TSLA")


if __name__ == "__main__":
    main()
