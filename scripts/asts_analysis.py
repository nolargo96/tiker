from src.analysis.stock_analysis_runner import StockAnalysisRunner


def main():
    """ASTS株価分析スクリプト"""
    StockAnalysisRunner.run_ticker_analysis("ASTS")


if __name__ == "__main__":
    main()
