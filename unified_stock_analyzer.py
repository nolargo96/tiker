import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import warnings
from typing import Tuple, Optional

warnings.filterwarnings('ignore') # Suppress warnings, e.g., about future changes in pandas

def analyze_and_chart_stock(ticker_symbol: str, today_date_str: Optional[str] = None) -> Tuple[bool, str]:
    """
    指定されたティッカーの株価データを取得し、テクニカル指標を計算し、チャートを生成・保存します。

    Args:
        ticker_symbol (str): 分析対象の米国株ティッカーシンボル (例: "AAPL", "MSFT").
        today_date_str (str, optional): 分析基準日を 'YYYY-MM-DD' 形式で指定します。
                                        指定しない場合、実行時の日本時間の日付が使用されます。
    Returns:
        tuple: (bool, str) - 成功した場合は (True, "成功メッセージ"), 失敗した場合は (False, "エラーメッセージ").
    """
    
    # 基準日の設定
    if today_date_str:
        try:
            today_jst = datetime.strptime(today_date_str, "%Y-%m-%d")
        except ValueError:
            return False, f"エラー: 無効な日付形式です。'YYYY-MM-DD'形式で指定してください: {today_date_str}"
    else:
        today_jst = datetime.now() # 日本時間として扱う
    
    today_str = today_jst.strftime('%Y-%m-%d')

    CHART_DIR = "./charts"
    CHART_FILENAME = f"{ticker_symbol}_chart_{today_str}.png"
    CHART_FILEPATH = os.path.join(CHART_DIR, CHART_FILENAME)

    print(f"=== {ticker_symbol} 株価分析・チャート作成開始 ===")
    print(f"分析基準日: {today_str} (JST)")

    try:
        # 1. 株価データの取得
        # yfinanceのhistoryメソッドは、指定された期間のデータを取得するのに適している
        # 過去1年（最低250営業日分）を確保するため、1.5年分のデータを取得
        end_date = today_jst
        start_date = end_date - timedelta(days=365 * 1.5) 
        
        print(f"データ取得期間: {start_date.strftime('%Y-%m-%d')} から {end_date.strftime('%Y-%m-%d')}")

        stock = yf.Ticker(ticker_symbol)
        # auto_adjust=False を明示的に指定して、調整前のOHLCVデータを取得
        df = stock.history(start=start_date, end=end_date, interval='1d', auto_adjust=False)
        
        if df.empty:
            # yfinanceが空のDataFrameを返す場合、無効なティッカーまたはデータ不足の可能性
            info = stock.info # ティッカー情報で有効性を確認
            if not info or 'regularMarketPrice' not in info: # infoが空か、主要な価格情報がない場合
                return False, f"{ticker_symbol} は有効な米国株ティッカーではありません。"
            else:
                return False, "データが取得できませんでした。データ不足のため簡易分析。"
        
        # 250営業日分を確保
        # 取得したデータが250日未満の場合でも、取得できたデータで続行する
        if len(df) < 250:
            print(f"警告: {ticker_symbol} の株価データが250営業日分ありません。取得できたのは {len(df)} 日分です。")
            # データが少なすぎる場合は、一部のテクニカル指標が計算できない可能性がある
            if len(df) < 200: # 200SMA計算に最低200日必要
                print("警告: 200日SMAを計算するためのデータが不足しています。")
        
        df_analysis = df.copy() # オリジナルデータを保持しつつ、分析用コピーを作成
        
        # 2. 移動平均線の計算
        df_analysis['EMA20'] = df_analysis['Close'].ewm(span=20, adjust=False).mean()
        df_analysis['EMA50'] = df_analysis['Close'].ewm(span=50, adjust=False).mean()
        df_analysis['SMA200'] = df_analysis['Close'].rolling(window=200).mean()

        # 3. その他のテクニカル指標の計算 (レポート議論用)
        # RSI
        delta = df_analysis['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        # ゼロ除算を避ける
        rs = gain / loss.replace(0, np.nan) # lossが0の場合はNaNにする
        df_analysis['RSI'] = 100 - (100 / (1 + rs))

        # ボリンジャーバンド
        df_analysis['BB_middle'] = df_analysis['Close'].rolling(window=20).mean()
        df_analysis['BB_std'] = df_analysis['Close'].rolling(window=20).std()
        df_analysis['BB_upper'] = df_analysis['BB_middle'] + (df_analysis['BB_std'] * 2)
        df_analysis['BB_lower'] = df_analysis['BB_middle'] - (df_analysis['BB_std'] * 2)

        # ATR
        df_analysis['TR'] = np.maximum(df_analysis['High'] - df_analysis['Low'], 
                                       np.maximum(abs(df_analysis['High'] - df_analysis['Close'].shift(1)), 
                                                  abs(df_analysis['Low'] - df_analysis['Close'].shift(1))))
        df_analysis['ATR'] = df_analysis['TR'].rolling(window=14).mean()

        # 4. チャートの描画と保存
        if not os.path.exists(CHART_DIR):
            os.makedirs(CHART_DIR)
            print(f"ディレクトリ {CHART_DIR} を作成しました。")

        # mplfinanceのスタイルとカラーを設定
        mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
        s  = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=False)

        # 追加プロットの準備
        ap0 = [
            mpf.make_addplot(df_analysis['EMA20'], color='blue', width=0.7, panel=0),
            mpf.make_addplot(df_analysis['EMA50'], color='orange', width=0.7, panel=0),
            mpf.make_addplot(df_analysis['SMA200'], color='purple', width=0.7, panel=0),
        ]

        # 16:9 アスペクト比の計算
        figratio = (16,9)
        
        # X軸の日付フォーマットは、mplfinanceが自動的に調整するため、
        # ここではJSTへの厳密な変換は行わず、表示フォーマットのみ指定
        # 出来高の片対数表示は `volume_panel=2` で可能だが、今回は通常表示
        mpf.plot(df_analysis,
                 type='candle',
                 style=s,
                 title=f'{ticker_symbol} Daily Chart (1 Year) - Data as of {today_str} JST',
                 ylabel='Price (USD)',
                 volume=True,
                 ylabel_lower='Volume',
                 addplot=ap0,
                 figsize=figratio,
                 panel_ratios=(3,1), # 価格チャートと出来高チャートの比率
                 savefig=dict(fname=CHART_FILEPATH, dpi=100),
                 show_nontrading=False, # 非取引日を詰める
                 datetime_format='%Y-%m-%d' # X軸の日付フォーマット
                )
        print(f"チャートを {CHART_FILEPATH} に保存しました。")

        # 最新データの表示
        latest_data = df_analysis.iloc[-1]
        print(f"\n取得した最新データ（{latest_data.name.strftime('%Y-%m-%d')}時点）：")
        print(f"- 終値: {latest_data['Close']:.2f} USD")
        if 'EMA20' in latest_data and not pd.isna(latest_data['EMA20']):
            print(f"- 20日EMA: {latest_data['EMA20']:.2f} USD")
        if 'EMA50' in latest_data and not pd.isna(latest_data['EMA50']):
            print(f"- 50日EMA: {latest_data['EMA50']:.2f} USD")
        if 'SMA200' in latest_data and not pd.isna(latest_data['SMA200']):
            print(f"- 200日SMA: {latest_data['SMA200']:.2f} USD")
        if 'Volume' in latest_data:
            print(f"- 出来高: {latest_data['Volume']:.0f} 株")
        
        print(f"\n追加テクニカル指標（最新）:")
        if 'RSI' in latest_data and not pd.isna(latest_data['RSI']):
            print(f"RSI(14): {latest_data['RSI']:.2f}")
        if 'BB_upper' in latest_data and not pd.isna(latest_data['BB_upper']):
            print(f"ボリンジャーバンド上限: ${latest_data['BB_upper']:.2f}")
        if 'BB_lower' in latest_data and not pd.isna(latest_data['BB_lower']):
            print(f"ボリンジャーバンド下限: ${latest_data['BB_lower']:.2f}")
        if 'ATR' in latest_data and not pd.isna(latest_data['ATR']):
            print(f"ATR(14): ${latest_data['ATR']:.2f}")

        # 分析用データをCSVに保存
        csv_filename = f'{ticker_symbol}_analysis_data_{today_str}.csv'
        df_analysis.to_csv(csv_filename)
        print(f"\n詳細分析データを {csv_filename} に保存しました。")

        return True, "チャート作成とデータ分析が完了しました。"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, f"エラーが発生しました: {str(e)}"

def main():
    """
    tiker-analyzeコマンドのエントリーポイント
    setup.pyのconsole_scriptsから呼び出される
    """
    import argparse
    parser = argparse.ArgumentParser(description='米国株の株価分析とチャート作成')
    parser.add_argument('--ticker', type=str, default='TSLA', help='分析対象のティッカーシンボル')
    parser.add_argument('--date', type=str, help='分析基準日 (YYYY-MM-DD形式)')
    args = parser.parse_args()

    success, message = analyze_and_chart_stock(args.ticker, args.date)
    print(f"\n結果: {message}")

if __name__ == '__main__':
    main()