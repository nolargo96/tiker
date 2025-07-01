import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

TICKER = "JOBY"
TODAY_JST_STR = "2024-07-30"
CHART_DIR = "./charts"
CHART_FILENAME = f"{TICKER}_chart_{TODAY_JST_STR}.png"
CHART_FILEPATH = os.path.join(CHART_DIR, CHART_FILENAME)

def create_stock_chart_debug():
    try:
        print(f"=== {TICKER} チャート作成開始 ===")
        
        # 1. 株価データの取得
        end_date = datetime.strptime(TODAY_JST_STR, "%Y-%m-%d")
        start_date = end_date - timedelta(days=365 * 1.5)
        
        print(f"データ取得期間: {start_date.strftime('%Y-%m-%d')} から {TODAY_JST_STR}")
        
        # シンプルなダウンロード
        data = yf.download(TICKER, start=start_date, end=end_date, progress=False)
        
        print(f"取得データサイズ: {len(data)} 行")
        print(f"データのカラム: {list(data.columns)}")
        print(f"データの型情報:")
        print(data.dtypes)
        
        if data.empty:
            print(f"エラー: {TICKER} のデータが取得できませんでした")
            return False
        
        # 最新250日分を使用
        data = data.tail(250)
        print(f"\n250日分に絞り込み後のデータサイズ: {len(data)} 行")
        
        # テクニカル指標の計算
        print("\nテクニカル指標を計算中...")
        data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
        data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['SMA200'] = data['Close'].rolling(window=200).mean()
        
        print("計算後のデータ:")
        print(data[['Close', 'EMA20', 'EMA50', 'SMA200']].tail())
        
        # シンプルなチャート作成を試みる
        print("\nシンプルなチャートを作成中...")
        
        # まず基本的なチャートだけ
        mpf.plot(data,
                 type='candle',
                 volume=True,
                 style='yahoo',
                 title=f'{TICKER} Stock Chart',
                 savefig=CHART_FILEPATH)
        
        print(f"チャートを {CHART_FILEPATH} に保存しました")
        return True
        
    except Exception as e:
        print(f"エラーが発生しました: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_stock_chart_debug()
    if success:
        print("\n=== チャート作成成功 ===")
    else:
        print("\n=== チャート作成失敗 ===") 