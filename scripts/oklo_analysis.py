import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_analyzer_lib import StockAnalyzer
from datetime import datetime

def main():
    """OKLO株価分析スクリプト"""
    ticker = "OKLO"
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    print(f"=== {ticker} 株価分析開始 ===")
    print(f"分析基準日: {today_str}")
    
    # StockAnalyzerを使用して分析を実行
    analyzer = StockAnalyzer()
    success, message = analyzer.analyze_stock(ticker, today_str)
    
    if success:
        print(f"\n=== {ticker} 分析完了 ===")
        print("チャートとデータが正常に生成されました。")
        print(f"- チャート: ./charts/{ticker}_chart_{today_str}.png")
        print(f"- データ: {ticker}_analysis_data_{today_str}.csv")
    else:
        print(f"エラーが発生しました: {message}")

if __name__ == '__main__':
    main() 