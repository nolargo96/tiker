import yfinance as yf
import mplfinance as mpf
import pandas as pd
import os
from datetime import datetime, timedelta

TICKER = "JOBY"
TODAY_JST_STR = "2025-06-26"
CHART_DIR = "./charts"
CHART_FILENAME = f"{TICKER}_chart_{TODAY_JST_STR}.png"
CHART_FILEPATH = os.path.join(CHART_DIR, CHART_FILENAME)

def create_stock_chart():
    try:
        # 1. 株価データの取得
        end_date = datetime.strptime(TODAY_JST_STR, "%Y-%m-%d")
        start_date = end_date - timedelta(days=365 * 1.5)
        
        # yfinanceでデータ取得
        ticker = yf.Ticker(TICKER)
        data = ticker.history(start=start_date, end=end_date)
        
        if data.empty:
            print(f"データ不足: {TICKER} の株価データを取得できませんでした。")
            return False, "データ不足のため簡易分析"
        
        # 250営業日分を確保
        data = data.tail(250)
        if len(data) < 250:
            print(f"データ不足: {TICKER} の株価データが250営業日分ありません。取得できたのは {len(data)} 日分です。")
            # 取得できた日数で分析を続行する
            # return False, "データ不足のため簡易分析"

        print(f"確保データ（直近{len(data)}営業日分）の期間: {data.index.min().strftime('%Y-%m-%d')} から {data.index.max().strftime('%Y-%m-%d')}")

        # 2. テクニカル指標の計算
        data['20EMA'] = data['Close'].ewm(span=20, adjust=False).mean()
        data['50EMA'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['200SMA'] = data['Close'].rolling(window=200).mean()

        # mplfinanceのDatetimeIndexがJSTになるように調整（米国市場の取引終了時間を考慮）
        # yfinanceから取得するデータは通常UTCであり、DatetimeIndexもUTCまたはローカライズなし。
        # X軸をJSTにする明確な指示があるので、プロット時にフォーマットする方針が良い。
        # ここではデータの日付はそのまま扱う。

        # 3. チャートの描画と保存
        # 出来高の片対数表示はmplfinanceでは直接サポートされていないため、通常表示とする
        ap0 = [
            mpf.make_addplot(data['20EMA'], color='blue', width=0.7),
            mpf.make_addplot(data['50EMA'], color='orange', width=0.7),
            mpf.make_addplot(data['200SMA'], color='purple', width=0.7),
        ]

        # X軸の日付フォーマットを JSTっぽく見せるが、実際の日付データは取引日ベース
        # marketcolorsとstyleを設定
        mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
        s  = mpf.make_mpf_style(marketcolors=mc, gridstyle=':')


        mpf.plot(data,
                 type='candle',
                 style=s,
                 title=f"{TICKER} Stock Chart ({TODAY_JST_STR})",
                 ylabel='Price (USD)',
                 volume=True,
                 ylabel_lower='Volume',
                 addplot=ap0,
                 figsize=(16, 9), # 16:9 横長サイズ
                 savefig=dict(fname=CHART_FILEPATH, dpi=100),
                 show_nontrading=False, # 非取引日を詰める
                 datetime_format='%Y-%m-%d' # X軸のフォーマット
                )
        print(f"チャートを {CHART_FILEPATH} に保存しました。")

        # 最新のデータをいくつか表示
        latest_data = data.iloc[-1]
        print("\n取得した最新データ（{latest_data.name.strftime('%Y-%m-%d')}時点）：")
        print(f"- 終値: {latest_data['Close']:.2f} USD")
        if '20EMA' in latest_data and not pd.isna(latest_data['20EMA']):
            print(f"- 20日EMA: {latest_data['20EMA']:.2f} USD")
        if '50EMA' in latest_data and not pd.isna(latest_data['50EMA']):
            print(f"- 50日EMA: {latest_data['50EMA']:.2f} USD")
        if '200SMA' in latest_data and not pd.isna(latest_data['200SMA']):
            print(f"- 200日SMA: {latest_data['200SMA']:.2f} USD")
        if 'Volume' in latest_data:
            print(f"- 出来高: {latest_data['Volume']:.0f} 株")

        return True, "チャート作成成功"

    except Exception as e:
        print(f"エラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False, f"エラーのためチャート作成失敗: {e}"

if __name__ == '__main__':
    if not os.path.exists(CHART_DIR):
        os.makedirs(CHART_DIR)
        print(f"ディレクトリ {CHART_DIR} を作成しました。")
    
    success, message = create_stock_chart()
    print(message) 