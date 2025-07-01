import yfinance as yf
import mplfinance as mpf
import pandas as pd
import os
from datetime import datetime, timedelta

TICKER = "JOBY"
TODAY_JST_STR = "2024-07-30" # 仮の日付
CHART_DIR = "./charts"
CHART_FILENAME = f"{TICKER}_chart_{TODAY_JST_STR}.png"
CHART_FILEPATH = os.path.join(CHART_DIR, CHART_FILENAME)

def create_stock_chart():
    try:
        # 1. 株価データの取得
        end_date = datetime.strptime(TODAY_JST_STR, "%Y-%m-%d")
        start_date = end_date - timedelta(days=365 * 1.5) # 余裕をもって1.5年分取得

        # auto_adjust=False を明示的に指定して、調整前のOHLCVデータを取得
        data = yf.download(TICKER,
                           start=start_date.strftime("%Y-%m-%d"),
                           end=TODAY_JST_STR,
                           progress=False,
                           auto_adjust=False, # 調整前の値を使用
                           actions=False)     # 配当や分割情報を別カラムにしない

        if data.empty:
            print(f"データ不足: {TICKER} の株価データを取得できませんでした。")
            return False, "データ不足のため簡易分析"

        # データ型を数値に変換
        cols_to_numeric = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in cols_to_numeric:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            else:
                print(f"警告: カラム {col} がデータに存在しません。")
                return False, f"データ不足のため簡易分析（必須カラム {col} が欠損）"

        # NaNが含まれる行を削除 (数値変換エラーによりNaNが発生した場合の対応)
        data.dropna(subset=cols_to_numeric, inplace=True)

        if data.empty: #数値変換とNaN削除の結果、データが空になった場合
            print(f"データ不足: {TICKER} の株価データが数値変換・NaN削除後に空になりました。")
            return False, "データ不足のため簡易分析"

        # 250営業日分を確保 (dropna後にデータが残っていることを確認してからスライス)
        if len(data) < 1: # 万が一、dropna後に空になったがdata.emptyで拾えなかった場合など
             print(f"データ不足: {TICKER} の株価データがフィルタリング後、空になりました。")
             return False, "データ不足のため簡易分析"

        data = data.iloc[-250:] # ここで初めて250日分にスライス
        if len(data) < 250:
            print(f"データ不足: {TICKER} の株価データが250営業日分ありません。取得データ数: {len(data)}")
            return False, "データ不足のため簡易分析"


        # 2. EMAとSMAの計算
        if not isinstance(data['Close'], pd.Series): # 型チェック
            print(f"エラー: data['Close'] がSeriesではありません。型: {type(data['Close'])}")
            return False, "データ処理エラー（内部データ型不整合）"

        data['20EMA'] = data['Close'].ewm(span=20, adjust=False).mean()
        data['50EMA'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['200SMA'] = data['Close'].rolling(window=200).mean()

        # 3. チャートの描画
        # mplfinanceのスタイルとカラーを設定
        mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
        s  = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=False)

        # 追加プロットの準備
        ap0 = [
            mpf.make_addplot(data['20EMA'], color='blue', width=0.7),
            mpf.make_addplot(data['50EMA'], color='orange', width=0.7),
            mpf.make_addplot(data['200SMA'], color='purple', width=0.7),
        ]

        # 16:9 アスペクト比の計算 (例: 幅16インチ、高さ9インチ)
        figratio = (16,9)
        
        # JST変換の注釈: yfinanceのデータは通常UTC基準。mplfinanceはインデックスの日付をそのまま表示。
        # X軸の日付のJSTへの厳密な変換と表示はmplfinanceのカスタマイズが複雑になるため、
        # ここでは取得した日付をそのまま使用し、JSTであるという前提は注釈に留めます。
        # 出来高の片対数表示はvolume_panel=2で指定できますが、まずは通常表示。

        mpf.plot(data,
                 type='candle',
                 style=s,
                 title=f'{TICKER} Stock Chart until {TODAY_JST_STR}',
                 ylabel='Price (USD)',
                 volume=True,
                 addplot=ap0,
                 figsize=figratio, # 16:9
                 panel_ratios=(3,1), # 価格チャートと出来高チャートの比率
                 savefig=dict(fname=CHART_FILEPATH, dpi=100),
                 show_nontrading=False,
                 datetime_format='%Y-%m-%d' # X軸の日付フォーマット
                )
        print(f"チャートを {CHART_FILEPATH} に保存しました。")
        return True, ""

    except Exception as e:
        # yfinance.download内でティッカーが無効な場合に発生する可能性のあるエラーをキャッチ
        # (ただし、yf.downloadは通常、無効なティッカーに対しては空のDataFrameを返すか、一般的なHTTPErrorなどを発生させる)
        # より堅牢なエラーハンドリングのため、具体的なエラータイプをチェックすることが望ましい
        if "No data found for ticker" in str(e) or isinstance(e, KeyError) or "valid ticker" in str(e).lower() : # yf.downloadが特定のエラーを出すか確認が必要
            print(f"{TICKER} は有効な米国株ティッカーではありません。エラー: {e}")
            return False, f"{TICKER} は有効な米国株ティッカーではありません。" # このメッセージで処理を終了させる
        print(f"チャート作成中にエラーが発生しました: {e}")
        # その他のエラーはデータ不足として扱うか、状況に応じて処理
        return False, "データ不足のため簡易分析（チャート作成エラー）"


if __name__ == '__main__':
    if not os.path.exists(CHART_DIR):
        try:
            os.makedirs(CHART_DIR)
            print(f"ディレクトリ {CHART_DIR} を作成しました。")
        except Exception as e:
            print(f"ディレクトリ {CHART_DIR} の作成に失敗しました: {e}")
            # ディレクトリ作成失敗時はスクリプトを終了することも検討
            exit()
            
    success, message = create_stock_chart()
    if not success and "有効な米国株ティッカーではありません" in message:
        # ティッカー無効の場合はここで処理終了という仕様のため、特別な出力は不要
        pass
    elif not success:
        # データ不足やその他のエラーの場合のメッセージは既にprintされている
        # 必要であればここでも追加のメッセージを出力
        pass 