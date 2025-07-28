from src.analysis.stock_analysis_runner import StockAnalysisRunner


def main():
    """OKLO株価分析スクリプト"""
    StockAnalysisRunner.run_ticker_analysis("OKLO")


if __name__ == "__main__":
    main()
