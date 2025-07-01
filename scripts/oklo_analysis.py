import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import warnings
warnings.filterwarnings('ignore')

# 日本時間の今日の日付を取得
today_jst = datetime.now()
today_str = today_jst.strftime('%Y-%m-%d')

# OKLOの過去1年分のデータを取得
ticker = "OKLO"  # <--- RKLBからOKLOに変更
end_date = today_jst
start_date = end_date - timedelta(days=365)

print(f"データ取得期間: {start_date.strftime('%Y-%m-%d')} から {end_date.strftime('%Y-%m-%d')} (JST)")
print(f"取得日: {today_str} (JST)")

# データ取得
try:
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date, interval='1d')
    
    if df.empty:
        raise ValueError("データが取得できませんでした")
    
    print(f"\n取得したデータ件数: {len(df)}件")
    
    # 移動平均線の計算
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    
    # チャート描画の準備
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9), gridspec_kw={'height_ratios': [3, 1]})
    
    # ローソク足データの準備
    df_plot = df.reset_index()
    df_plot['Date'] = pd.to_datetime(df_plot['Date'])
    df_plot['Date'] = df_plot['Date'].map(mdates.date2num)
    
    ohlc = df_plot[['Date', 'Open', 'High', 'Low', 'Close']].values
    
    # ローソク足チャート
    candlestick_ohlc(ax1, ohlc, width=0.6, colorup='green', colordown='red', alpha=0.8)
    
    # 移動平均線
    ax1.plot(df_plot['Date'], df['EMA20'].values, 'b-', label='20 EMA', linewidth=1.5)
    ax1.plot(df_plot['Date'], df['EMA50'].values, 'orange', label='50 EMA', linewidth=1.5)
    ax1.plot(df_plot['Date'], df['SMA200'].values, 'purple', label='200 SMA', linewidth=1.5)
    
    # チャート設定
    ax1.set_title(f'{ticker} Daily Chart (1 Year) - Data as of {today_str} JST', fontsize=16, fontweight='bold') # <--- ticker変数を反映 (OKLO)
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # X軸のフォーマット
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # 出来高バーチャート
    colors = ['green' if close >= open else 'red' 
              for close, open in zip(df['Close'].values, df['Open'].values)]
    ax2.bar(df_plot['Date'], df['Volume'].values, width=0.6, color=colors, alpha=0.8)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    # チャートを保存
    chart_filename = f'oklo_chart_{today_str}.png' # <--- rklbからokloに変更
    plt.savefig(chart_filename, dpi=150, bbox_inches='tight')
    print(f"\nチャートを{chart_filename}に保存しました: {chart_filename}") # <--- rklbからokloに変更
    
    # 最新データの表示
    latest = df.iloc[-1]
    print(f"\n最新データ ({df.index[-1].strftime('%Y-%m-%d')}):")
    print(f"終値: ${latest['Close']:.2f}")
    print(f"出来高: {latest['Volume']:,.0f}")
    print(f"20 EMA: ${latest['EMA20']:.2f}")
    print(f"50 EMA: ${latest['EMA50']:.2f}")
    if 'SMA200' in latest and not pd.isna(latest['SMA200']):
        print(f"200 SMA: ${latest['SMA200']:.2f}")
    else:
        print("200 SMA: データなし")

    # テクニカル指標の追加計算（議論用）
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    if loss.eq(0).any(): # ゼロ除算を回避
        df['RSI'] = 100
    else:
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
    
    # ボリンジャーバンド
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    df['BB_std'] = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
    df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)
    
    # ATR
    df['TR'] = np.maximum(df['High'] - df['Low'], 
                          np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                                   abs(df['Low'] - df['Close'].shift(1))))
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    print(f"\n追加テクニカル指標（最新）:")
    if 'RSI' in df.columns and not pd.isna(df['RSI'].iloc[-1]):
        print(f"RSI(14): {df['RSI'].iloc[-1]:.2f}")
    else:
        print("RSI(14): データなし")
    if 'BB_upper' in df.columns and not pd.isna(df['BB_upper'].iloc[-1]):
        print(f"ボリンジャーバンド上限: ${df['BB_upper'].iloc[-1]:.2f}")
    else:
        print("ボリンジャーバンド上限: データなし")
    if 'BB_lower' in df.columns and not pd.isna(df['BB_lower'].iloc[-1]):
        print(f"ボリンジャーバンド下限: ${df['BB_lower'].iloc[-1]:.2f}")
    else:
        print("ボリンジャーバンド下限: データなし")
    if 'ATR' in df.columns and not pd.isna(df['ATR'].iloc[-1]):
        print(f"ATR(14): ${df['ATR'].iloc[-1]:.2f}")
    else:
        print("ATR(14): データなし")

    # データをCSVに保存（分析用）
    csv_filename = 'oklo_data.csv' # <--- rklbからokloに変更
    df.to_csv(csv_filename)
    print(f"\nデータを{csv_filename}に保存しました") # <--- rklbからokloに変更
    
    # plt.show() # GUI環境でない場合はコメントアウト推奨

except Exception as e:
    print(f"エラーが発生しました: {str(e)}")
    import traceback
    traceback.print_exc() 