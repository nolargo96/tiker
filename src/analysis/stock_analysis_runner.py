# -*- coding: utf-8 -*-
"""
Stock Analysis Runner
個別株式分析の統一実行クラス
"""

from typing import Optional, Tuple
from datetime import datetime
from src.analysis.stock_analyzer_lib import StockAnalyzer


class StockAnalysisRunner:
    """統一された株式分析実行クラス"""
    
    def __init__(self, ticker: str, date: Optional[str] = None):
        """
        Args:
            ticker: 株式ティッカーシンボル
            date: 分析基準日（YYYY-MM-DD形式、Noneの場合は今日）
        """
        self.ticker = ticker.upper()
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.analyzer = StockAnalyzer()
    
    def run_analysis(self) -> Tuple[bool, str]:
        """
        分析を実行する
        
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        print(f"=== {self.ticker} 株価分析開始 ===")
        print(f"分析基準日: {self.date}")
        
        success, message = self.analyzer.analyze_stock(self.ticker, self.date)
        
        if success:
            print(f"\n=== {self.ticker} 分析完了 ===")
            print("チャートとデータが正常に生成されました。")
            print(f"- チャート: ./charts/{self.ticker}_chart_{self.date}.png")
            print(f"- データ: {self.ticker}_analysis_data_{self.date}.csv")
            return True, "分析完了"
        else:
            print(f"エラーが発生しました: {message}")
            return False, message
    
    @staticmethod
    def run_ticker_analysis(ticker: str, date: Optional[str] = None) -> Tuple[bool, str]:
        """
        静的メソッドで分析を実行（後方互換性のため）
        
        Args:
            ticker: 株式ティッカーシンボル
            date: 分析基準日
            
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        runner = StockAnalysisRunner(ticker, date)
        return runner.run_analysis()


def main():
    """テスト用のメイン関数"""
    import sys
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
        date = sys.argv[2] if len(sys.argv) > 2 else None
        StockAnalysisRunner.run_ticker_analysis(ticker, date)
    else:
        print("Usage: python stock_analysis_runner.py <TICKER> [DATE]")


if __name__ == "__main__":
    main()