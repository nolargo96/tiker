import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import warnings
from typing import Tuple, Optional, Dict, Any, Union, List

warnings.filterwarnings(
    "ignore"
)  # Suppress warnings, e.g., about future changes in pandas

# HTML レポート生成機能をインポート
try:
    from html_report_generator import HTMLReportGenerator

    HTML_REPORT_AVAILABLE = True
except ImportError:
    HTML_REPORT_AVAILABLE = False
    print(
        "HTMLレポート機能は利用できません。html_report_generator.pyが見つかりません。"
    )


def analyze_and_chart_stock(
    ticker_symbol: str, today_date_str: Optional[str] = None
) -> Tuple[bool, str]:
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
            return (
                False,
                f"エラー: 無効な日付形式です。'YYYY-MM-DD'形式で指定してください: {today_date_str}",
            )
    else:
        today_jst = datetime.now()  # 日本時間として扱う

    today_str = today_jst.strftime("%Y-%m-%d")

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

        print(
            f"データ取得期間: {start_date.strftime('%Y-%m-%d')} から {end_date.strftime('%Y-%m-%d')}"
        )

        stock = yf.Ticker(ticker_symbol)
        # auto_adjust=False を明示的に指定して、調整前のOHLCVデータを取得
        df = stock.history(
            start=start_date, end=end_date, interval="1d", auto_adjust=False
        )

        if df.empty:
            # yfinanceが空のDataFrameを返す場合、無効なティッカーまたはデータ不足の可能性
            info = stock.info  # ティッカー情報で有効性を確認
            if (
                not info or "regularMarketPrice" not in info
            ):  # infoが空か、主要な価格情報がない場合
                return (
                    False,
                    f"{ticker_symbol} は有効な米国株ティッカーではありません。",
                )
            else:
                return False, "データが取得できませんでした。データ不足のため簡易分析。"

        # 250営業日分を確保
        # 取得したデータが250日未満の場合でも、取得できたデータで続行する
        if len(df) < 250:
            print(
                f"警告: {ticker_symbol} の株価データが250営業日分ありません。取得できたのは {len(df)} 日分です。"
            )
            # データが少なすぎる場合は、一部のテクニカル指標が計算できない可能性がある
            if len(df) < 200:  # 200SMA計算に最低200日必要
                print("警告: 200日SMAを計算するためのデータが不足しています。")

        df_analysis = df.copy()  # オリジナルデータを保持しつつ、分析用コピーを作成

        # 2. 移動平均線の計算
        df_analysis["EMA20"] = df_analysis["Close"].ewm(span=20, adjust=False).mean()
        df_analysis["EMA50"] = df_analysis["Close"].ewm(span=50, adjust=False).mean()
        df_analysis["SMA200"] = df_analysis["Close"].rolling(window=200).mean()

        # 3. その他のテクニカル指標の計算 (レポート議論用)
        # RSI
        delta = df_analysis["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        # ゼロ除算を避ける
        rs = gain / loss.replace(0, np.nan)  # lossが0の場合はNaNにする
        df_analysis["RSI"] = 100 - (100 / (1 + rs))

        # ボリンジャーバンド
        df_analysis["BB_middle"] = df_analysis["Close"].rolling(window=20).mean()
        df_analysis["BB_std"] = df_analysis["Close"].rolling(window=20).std()
        df_analysis["BB_upper"] = df_analysis["BB_middle"] + (df_analysis["BB_std"] * 2)
        df_analysis["BB_lower"] = df_analysis["BB_middle"] - (df_analysis["BB_std"] * 2)

        # ATR
        df_analysis["TR"] = np.maximum(
            df_analysis["High"] - df_analysis["Low"],
            np.maximum(
                abs(df_analysis["High"] - df_analysis["Close"].shift(1)),
                abs(df_analysis["Low"] - df_analysis["Close"].shift(1)),
            ),
        )
        df_analysis["ATR"] = df_analysis["TR"].rolling(window=14).mean()

        # 4. チャートの描画と保存
        if not os.path.exists(CHART_DIR):
            os.makedirs(CHART_DIR)
            print(f"ディレクトリ {CHART_DIR} を作成しました。")

        # mplfinanceのスタイルとカラーを設定
        mc = mpf.make_marketcolors(up="green", down="red", inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=False)

        # 追加プロットの準備
        ap0 = [
            mpf.make_addplot(df_analysis["EMA20"], color="blue", width=0.7, panel=0),
            mpf.make_addplot(df_analysis["EMA50"], color="orange", width=0.7, panel=0),
            mpf.make_addplot(df_analysis["SMA200"], color="purple", width=0.7, panel=0),
        ]

        # 16:9 アスペクト比の計算
        figratio = (16, 9)

        # X軸の日付フォーマットは、mplfinanceが自動的に調整するため、
        # ここではJSTへの厳密な変換は行わず、表示フォーマットのみ指定
        # 出来高の片対数表示は `volume_panel=2` で可能だが、今回は通常表示
        mpf.plot(
            df_analysis,
            type="candle",
            style=s,
            title=f"{ticker_symbol} Daily Chart (1 Year) - Data as of {today_str} JST",
            ylabel="Price (USD)",
            volume=True,
            ylabel_lower="Volume",
            addplot=ap0,
            figsize=figratio,
            panel_ratios=(3, 1),  # 価格チャートと出来高チャートの比率
            savefig=dict(fname=CHART_FILEPATH, dpi=100),
            show_nontrading=False,  # 非取引日を詰める
            datetime_format="%Y-%m-%d",  # X軸の日付フォーマット
        )
        print(f"チャートを {CHART_FILEPATH} に保存しました。")

        # 最新データの表示
        latest_data = df_analysis.iloc[-1]
        print(f"\n取得した最新データ（{latest_data.name.strftime('%Y-%m-%d')}時点）：")
        print(f"- 終値: {latest_data['Close']:.2f} USD")
        if "EMA20" in latest_data and not pd.isna(latest_data["EMA20"]):
            print(f"- 20日EMA: {latest_data['EMA20']:.2f} USD")
        if "EMA50" in latest_data and not pd.isna(latest_data["EMA50"]):
            print(f"- 50日EMA: {latest_data['EMA50']:.2f} USD")
        if "SMA200" in latest_data and not pd.isna(latest_data["SMA200"]):
            print(f"- 200日SMA: {latest_data['SMA200']:.2f} USD")
        if "Volume" in latest_data:
            print(f"- 出来高: {latest_data['Volume']:.0f} 株")

        print(f"\n追加テクニカル指標（最新）:")
        if "RSI" in latest_data and not pd.isna(latest_data["RSI"]):
            print(f"RSI(14): {latest_data['RSI']:.2f}")
        if "BB_upper" in latest_data and not pd.isna(latest_data["BB_upper"]):
            print(f"ボリンジャーバンド上限: ${latest_data['BB_upper']:.2f}")
        if "BB_lower" in latest_data and not pd.isna(latest_data["BB_lower"]):
            print(f"ボリンジャーバンド下限: ${latest_data['BB_lower']:.2f}")
        if "ATR" in latest_data and not pd.isna(latest_data["ATR"]):
            print(f"ATR(14): ${latest_data['ATR']:.2f}")

        # 分析用データをCSVに保存
        csv_filename = f"{ticker_symbol}_analysis_data_{today_str}.csv"
        df_analysis.to_csv(csv_filename)
        print(f"\n詳細分析データを {csv_filename} に保存しました。")

        # HTMLレポート生成（利用可能な場合）
        if HTML_REPORT_AVAILABLE:
            try:
                html_generator = HTMLReportGenerator()
                html_success, html_result = html_generator.generate_stock_html_report(
                    ticker=ticker_symbol,
                    analysis_data=df_analysis,
                    chart_path=CHART_FILEPATH,
                    date_str=today_str,
                )
                if html_success:
                    print(f"HTMLレポートを生成しました: {html_result}")
                else:
                    print(f"HTMLレポート生成エラー: {html_result}")
            except Exception as e:
                print(f"HTMLレポート生成中にエラーが発生しました: {str(e)}")

        return True, "チャート作成とデータ分析が完了しました。"

    except Exception as e:
        import traceback

        traceback.print_exc()
        return False, f"エラーが発生しました: {str(e)}"


def analyze_portfolio(
    portfolio_config: Dict[str, float], today_date_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    ポートフォリオ全体の分析を実行し、統合レポートを生成します。

    Args:
        portfolio_config (dict): ポートフォリオ設定 {"TSLA": 30, "FSLR": 25, ...}
        today_date_str (str, optional): 分析基準日

    Returns:
        dict: 統合分析結果
    """
    if today_date_str:
        try:
            today_jst = datetime.strptime(today_date_str, "%Y-%m-%d")
        except ValueError:
            return {"error": f"無効な日付形式: {today_date_str}"}
    else:
        today_jst = datetime.now()

    today_str = today_jst.strftime("%Y-%m-%d")

    print(f"\n=== ポートフォリオ統合分析開始 ({today_str}) ===")

    results = {
        "analysis_date": today_str,
        "portfolio_summary": {},
        "individual_analysis": {},
        "expert_scores": {},
        "recommendations": {},
        "risk_metrics": {},
    }

    # 各銘柄の分析を実行
    for ticker, allocation in portfolio_config.items():
        print(f"\n--- {ticker} ({allocation}%配分) 分析中 ---")
        success, message = analyze_and_chart_stock(ticker, today_date_str)

        if success:
            # 分析結果を読み込み
            csv_filename = f"{ticker}_analysis_data_{today_str}.csv"
            try:
                df = pd.read_csv(csv_filename, index_col=0, parse_dates=True)
                latest = df.iloc[-1]

                # 4専門家スコア算出
                tech_score = calculate_tech_score(df)
                fund_score = calculate_fund_score(ticker, latest)
                macro_score = calculate_macro_score(ticker)
                risk_score = calculate_risk_score(df, allocation)

                results["individual_analysis"][ticker] = {
                    "allocation": allocation,
                    "latest_price": latest["Close"],
                    "success": True,
                    "message": message,
                }

                results["expert_scores"][ticker] = {
                    "TECH": tech_score,
                    "FUND": fund_score,
                    "MACRO": macro_score,
                    "RISK": risk_score,
                    "OVERALL": (tech_score + fund_score + macro_score + risk_score) / 4,
                }

                # エントリー推奨度
                recommendation = get_entry_recommendation(
                    tech_score, fund_score, macro_score, risk_score
                )
                results["recommendations"][ticker] = recommendation

            except Exception as e:
                print(f"警告: {ticker}の詳細分析でエラー: {e}")
                results["individual_analysis"][ticker] = {
                    "allocation": allocation,
                    "success": False,
                    "error": str(e),
                }
        else:
            results["individual_analysis"][ticker] = {
                "allocation": allocation,
                "success": False,
                "error": message,
            }

    # ポートフォリオ全体のサマリー計算
    successful_tickers = [
        t for t, data in results["individual_analysis"].items() if data["success"]
    ]
    total_allocation = sum(portfolio_config[t] for t in successful_tickers)

    results["portfolio_summary"] = {
        "total_tickers": len(portfolio_config),
        "successful_analysis": len(successful_tickers),
        "total_allocation": total_allocation,
        "analysis_coverage": f"{len(successful_tickers)}/{len(portfolio_config)} 銘柄",
    }

    # 統合レポート生成
    generate_portfolio_report(results, today_str)

    return results


def calculate_tech_score(df: pd.DataFrame) -> float:
    """テクニカル分析スコア (1-5)"""
    latest = df.iloc[-1]
    score = 3.0  # 中立から開始

    # 移動平均との関係
    if latest["Close"] > latest["EMA20"]:
        score += 0.5
    if latest["Close"] > latest["EMA50"]:
        score += 0.5
    if latest["Close"] > latest["SMA200"]:
        score += 0.5

    # RSI評価
    if 30 <= latest["RSI"] <= 70:
        score += 0.3
    elif latest["RSI"] < 30:
        score += 0.5  # 売られすぎで買いチャンス
    else:
        score -= 0.5  # 買われすぎで注意

    # トレンド評価
    ema20_trend = (latest["EMA20"] - df["EMA20"].iloc[-5]) / df["EMA20"].iloc[-5]
    if ema20_trend > 0.02:
        score += 0.2
    elif ema20_trend < -0.02:
        score -= 0.2

    return max(1.0, min(5.0, score))


def calculate_fund_score(ticker: str, latest_data: pd.Series) -> float:
    """ファンダメンタル分析スコア (1-5)"""
    # 銘柄別の固定スコア（実際の分析レポートから）
    fund_scores = {
        "TSLA": 3.5,
        "FSLR": 5.0,
        "ASTS": 3.0,
        "OKLO": 3.5,
        "JOBY": 4.0,
        "LUNR": 3.0,
        "RDW": 3.5,
        "OII": 3.8,  # 海洋エンジニアリング・ROVサービス大手、Q1売上13%増、純利益233%増
        "RKLB": 4.2,  # 小型ロケット市場リーダー、売上78%増、Neutron開発中、高成長
    }
    return fund_scores.get(ticker, 3.0)


def calculate_macro_score(ticker: str) -> float:
    """マクロ環境スコア (1-5)"""
    macro_scores = {
        "TSLA": 2.5,
        "FSLR": 4.0,
        "ASTS": 4.0,
        "OKLO": 4.0,
        "JOBY": 4.0,
        "LUNR": 4.0,
        "RDW": 4.0,
        "OII": 3.8,  # 海洋エネルギー需要増、ロボティクス成長、地政学リスクあり
        "RKLB": 4.5,  # 宇宙産業年率20%成長、小型衛星市場拡大、政府予算支援
    }
    return macro_scores.get(ticker, 3.0)


def calculate_risk_score(df: pd.DataFrame, allocation: float) -> float:
    """リスク管理スコア (1-5)"""
    # 配分比率とボラティリティに基づくリスク評価
    volatility = df["Close"].pct_change().std() * np.sqrt(252)  # 年率ボラティリティ

    # 配分リスク評価
    if allocation <= 10:
        allocation_score = 4.0
    elif allocation <= 20:
        allocation_score = 3.5
    elif allocation <= 30:
        allocation_score = 3.0
    else:
        allocation_score = 2.0

    # ボラティリティリスク評価
    if volatility < 0.3:
        vol_score = 4.0
    elif volatility < 0.5:
        vol_score = 3.0
    elif volatility < 0.8:
        vol_score = 2.0
    else:
        vol_score = 1.0

    return (allocation_score + vol_score) / 2


def get_entry_recommendation(
    tech: float, fund: float, macro: float, risk: float
) -> Dict[str, Union[str, float]]:
    """エントリー推奨度を算出"""
    overall_score = (tech + fund + macro + risk) / 4

    if overall_score >= 4.0:
        recommendation = "即時エントリー推奨"
        action = "BUY"
    elif overall_score >= 3.5:
        recommendation = "押し目でのエントリー"
        action = "BUY_DIP"
    elif overall_score >= 3.0:
        recommendation = "慎重なエントリー"
        action = "CAUTIOUS"
    elif overall_score >= 2.5:
        recommendation = "様子見"
        action = "WAIT"
    else:
        recommendation = "エントリー非推奨"
        action = "AVOID"

    return {"score": overall_score, "recommendation": recommendation, "action": action}


def generate_detailed_expert_discussion(
    ticker: str,
    latest_data: pd.Series,
    tech_score: float,
    fund_score: float,
    macro_score: float,
    risk_score: float,
    allocation: float,
) -> str:
    """6ラウンド形式の詳細4専門家討論を生成"""

    # 銘柄別の6ラウンド専門家討論テンプレート
    expert_discussions = {
        "TSLA": {
            "current_situation": "EV競争激化とロボタクシー期待の綱引き状態",
            "round1": {
                "tech_to_fund": "テクニカルには$300が重要なサポートライン。RSI(38.5)で売られすぎ気味だが、Wells Fargoの$120目標は妥当？この価格差をどう評価する？",
                "fund_reply": "$120は極端すぎる。EV販売の短期的減速はあるが、FSD・ロボタクシーの潜在価値は膨大。2026年の商用化成功なら株価は$400-500も視野に入る。",
                "macro_to_risk": "金利高止まりとEV補助金削減が重なり、需要圧迫は深刻。中国市場での競争激化も懸念材料。マクロ逆風下での25%配分は適切か？",
                "risk_reply": "確かに逆風は強い。ボラティリティも高く、25%は上限ギリギリ。20%程度に下げ、残り5%は他成長株に分散するのが賢明かもしれない。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "$300を週足で割れば$250-280ゾーンまで調整。ここが長期投資家の押し目買いゾーン。",
                "fund_view": "PER20倍程度($280前後)なら割安。ただし、四半期赤字継続なら$250も視野。",
                "macro_view": "EV市場全体の調整で$200台前半まで下落リスクもある。セクター全体の圧迫継続。",
                "risk_view": "$240を明確に割れば損切り。リスク管理上、ここが最終防衛ライン。",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "$350を超えれば$400-450が視野。ただし$330-350は強い抵抗帯。",
                "fund_view": "ロボタクシー商用化で株価は$500+も可能。1年後目標$380、3年後$600。",
                "macro_view": "金利低下とEV市場回復で上昇加速。政策転換が鍵。",
                "risk_view": "目標達成確率は1年後30%、3年後15%。期待値は高いがリスクも大。",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "第1段階: $280-300で40%、第2段階: $250-280で50%、第3段階: FSD進捗で10%",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "$240を週足終値で割り込み",
                "fund_exit": "ロボタクシー計画の大幅遅延",
                "macro_exit": "EV市場の構造的不振が明確化",
                "risk_exit": "初期投資の30%損失で機械的損切り",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "2-5年、ロボタクシー商用化まで",
                "exit_plan": "目標価格の50%達成で半分利確、残りは長期コア保有として継続",
            },
        },
        "FSLR": {
            "current_situation": "政策支援とCdTe技術優位性、中国競合との価格競争",
            "round1": {
                "tech_to_fund": "RSI(48.9)で調整一巡感。200日線($156)奪還が焦点だが、Jefferiesの$192目標は保守的すぎないか？",
                "fund_reply": "$192は控えめ。IRA支援継続と66GW受注残を考慮すれば$220-250が適正。CdTe技術の優位性も織り込み不足。",
                "macro_to_risk": "脱炭素政策は追い風だが、トランプ政権復帰でIRA削減リスクが台頭。政策依存の高い25%配分は危険では？",
                "risk_reply": "政策リスクは最大の懸念。ただし、AIデータセンター電力需要は政権関係なく拡大。20%程度に下げて政策動向を注視すべき。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "200日線$156がサポート。割れれば$130-150の強力な買いゾーン出現。",
                "fund_view": "PER15倍($140前後)なら大底圏。政策不安での売りは絶好の仕込み場。",
                "macro_view": "政策変更でも$120割れは考えにくい。技術的優位性は政権に左右されない。",
                "risk_view": "$120を割れば政策リスク顕在化として全ポジション解消も検討。",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "$180突破で$200-220、さらに$250も射程圏内。",
                "fund_view": "2026年度業績好転で株価$250-300も視野。長期目標$280設定。",
                "macro_view": "グローバル脱炭素加速で$300+も可能。電力需要増が追い風。",
                "risk_view": "1年後$210達成確率60%、3年後$280は40%。比較的現実的な目標。",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "第1段階: $150-165で50%、第2段階: $130-150で40%、第3段階: 好決算で10%",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "200日線$156を明確に下抜け",
                "fund_exit": "IRA大幅削減の法案可決",
                "macro_exit": "中国製パネルの米国大量流入",
                "risk_exit": "$120割れで政策リスク顕在化",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "3-5年、エネルギー転換期の長期投資",
                "exit_plan": "$210で30%利確、$250で追加30%、残り40%は長期保有継続",
            },
        },
        "ASTS": {
            "current_situation": "既存スマホ直接衛星通信の革新技術、事業化前の投機段階",
            "round1": {
                "tech_to_fund": "RSI(65.4)で過熱感強い。$30-42の調整待ちだが、AT&T/Verizon提携は本物？巨大市場の実現可能性はいかに？",
                "fund_reply": "技術実証は成功。2025年商用サービス開始予定で、潜在市場は兆円規模。ただし収益化前の投機段階は事実。リスクは極めて高い。",
                "macro_to_risk": "衛星通信市場拡大は確実だが、競合も激化。10%配分でも高リスクでは？地政学リスクで需要増の一方、技術リスクも大きい。",
                "risk_reply": "極めて投機的な銘柄。10%でも上限で、5%程度が適正か。成功時のリターンは巨大だが、失敗確率も相当高い。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "$30-35が重要サポート。割れれば$25前後まで調整の可能性。",
                "fund_view": "商用化前なので明確なバリュエーションは困難。$20-25が投機資金の流入下限か。",
                "macro_view": "衛星通信ブーム終了なら$15-20まで下落リスク。セクター全体の調整に巻き込まれる。",
                "risk_view": "$25割れは技術的・事業的問題の可能性。ここが損切りライン。",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "商用化成功なら$80-100も射程圏内。夢のある銘柄。",
                "fund_view": "成功時は$100-150も可能。ただし確率は低い。期待値計算が重要。",
                "macro_view": "衛星通信革命の先駆者として$200+も理論上可能。",
                "risk_view": "成功確率20-30%として期待値は魅力的。ただし失敗時は80%以上下落。",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "大幅調整待ち。$25-30で50%、商用化マイルストーン達成で追加投資検討",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "$25を明確に下抜け",
                "fund_exit": "商用化計画の大幅遅延や中止",
                "macro_exit": "衛星通信規制の大幅強化",
                "risk_exit": "初期投資の50%損失で即時撤退",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "2-3年、商用化成功まで",
                "exit_plan": "成功時は段階的利確、$80で50%、$120で追加30%売却",
            },
        },
        "OKLO": {
            "current_situation": "小型高速炉Aurora、アルトマン支援で注目集まるSMR先駆者",
            "round1": {
                "tech_to_fund": "RSI(49.2)で中立、上昇トレンド継続中。2044年電力契約は魅力的だが、NRC規制承認の確度は？",
                "fund_reply": "Aurora設計は技術的に先進的。AI電力需要急拡大で長期契約価値は大きい。ただしNRC承認が最大のハードル。2026年承認を想定。",
                "macro_to_risk": "SMR市場拡大期待は大きいが、原子力規制は極めて厳格。10%配分は規制リスクを考慮すると妥当な水準か？",
                "risk_reply": "規制リスクは最大の懸念。ただしアルトマン支援と技術的優位性を評価し、10%は妥当。承認遅延リスクは織り込み済み。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "$40-45が重要サポート。割れれば$30-35まで調整も。",
                "fund_view": "規制承認遅延でも技術価値は維持。$35前後が中長期的下値メド。",
                "macro_view": "SMRブーム終了なら$25-30まで下落リスク。政策変更も要警戒。",
                "risk_view": "$30割れは規制承認の深刻な遅延を示唆。ここが最終防衛ライン。",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "規制承認で$80-100、商用化開始で$120-150も射程圏内。",
                "fund_view": "成功時は$100-150が目標。AI電力需要との相乗効果に期待。",
                "macro_view": "クリーンエネルギー政策とAI需要で$200+も理論上可能。",
                "risk_view": "承認確率50%として期待値は魅力的。3年後$120達成確率40%。",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "第1段階: $40-48で60%、第2段階: 規制進捗で30%、第3段階: 承認確定で10%",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "$30を明確に下抜け",
                "fund_exit": "NRC承認申請の却下",
                "macro_exit": "原子力政策の大幅後退",
                "risk_exit": "規制承認の大幅遅延発表",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "3-7年、商用化軌道に乗るまで",
                "exit_plan": "承認で30%利確、商用化で追加40%、残り30%は長期保有",
            },
        },
        "JOBY": {
            "current_situation": "eVTOL先駆者、FAA認証進捗とトヨタ投資で市場創造",
            "round1": {
                "tech_to_fund": "RSI(53.1)で健全、強い上昇トレンド継続。FAA認証は最終段階だが、2025年200機納入は現実的？",
                "fund_reply": "認証プロセスは順調で2025年商用開始予定。トヨタとの提携で量産体制も整備中。ただし新市場創造のリスクは大きい。",
                "macro_to_risk": "都市交通革新は魅力的だが、規制・社会受容性・コストが課題。10%配分は量産化不確実性を考慮すると適正か？",
                "risk_reply": "確かに不確実性は高い。ただし先行者利益は大きく、10%配分は妥当。失敗時のリスクも織り込み済み。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "$8.00-8.50が重要サポート。ここが押し目買いの絶好機。",
                "fund_view": "認証遅延でも技術的優位性は維持。$7-8が中長期下値メド。",
                "macro_view": "eVTOLブーム終了なら$6前後まで下落リスク。市場形成失敗を織り込み。",
                "risk_view": "$6.50が最終防衛ライン。市場形成失敗なら損切り必要。",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "商用化成功で$15-20、市場拡大で$25-30も視野。",
                "fund_view": "成功時は$20-30が目標。都市交通革命の先駆者として高評価。",
                "macro_view": "規制環境整備と社会受容で$40+も可能。長期的には巨大市場。",
                "risk_view": "成功確率40%として期待値は魅力的。3年後$25達成確率35%。",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "即時エントリー可能。$8.00-8.50押し目は絶好機として追加投資",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "$6.50を明確に下抜け",
                "fund_exit": "FAA認証の大幅遅延",
                "macro_exit": "eVTOL規制の大幅厳格化",
                "risk_exit": "市場形成失敗の明確な兆候",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "3-5年、市場創造期から成長期まで",
                "exit_plan": "$12で30%利確、$20で追加40%、残り30%は市場拡大期まで保有",
            },
        },
        "LUNR": {
            "current_situation": "民間初月面着陸実績、NASA依存とミッション成否が焦点",
            "round1": {
                "tech_to_fund": "RSI(44.1)で弱含み、$9-10サポート重要。NASA48.2億ドル契約は魅力的だが、IM-3の成否が株価を左右？",
                "fund_reply": "月面着陸実績は民間初で技術的価値は高い。ただしミッション成否への依存度が極めて高く、ボラティリティは覚悟要。",
                "macro_to_risk": "第二次宇宙開発競争は追い風だが、NASA予算削減リスクもある。5%配分でも高リスクでは？",
                "risk_reply": "確かに極めて投機的。ミッション失敗時の下落幅は大きく、5%でも上限かもしれない。期待値投資として割り切り必要。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "$9-10が重要サポート。割れれば$6-7まで急落も。",
                "fund_view": "ミッション失敗でも技術資産は残存。$5-6が最悪ケース下値。",
                "macro_view": "宇宙ブーム終了なら$4-5まで下落リスク。セクター全体の調整。",
                "risk_view": "$9割れはミッション失敗を織り込み。ここが損切りライン。",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "ミッション成功で$20-25、連続成功で$30-40も射程圏内。",
                "fund_view": "成功時は$25-35が目標。月経済圏構想での長期期待値は大きい。",
                "macro_view": "月面開発本格化で$50+も理論上可能。超長期の夢株。",
                "risk_view": "成功確率30%として期待値は魅力的。ただしハイリスク・ハイリターン。",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "IM-3前後のイベント投資。少額配分厳守で$9-10での打診買い",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "$9を明確に下抜け",
                "fund_exit": "重要ミッションの連続失敗",
                "macro_exit": "NASA予算の大幅削減",
                "risk_exit": "ミッション失敗による急落時",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "1-3年、主要ミッション成功まで",
                "exit_plan": "成功時は大幅利確。$20で50%、$30で追加40%売却",
            },
        },
        "RDW": {
            "current_situation": "宇宙インフラ多角化、軌道上製造とEdge買収で事業拡大",
            "round1": {
                "tech_to_fund": "RSI(39.9)で調整中、$12.80サポート重要。売上24.7%増は評価できるが、継続赤字をどう見る？",
                "fund_reply": "売上成長は順調だが収益性が課題。軍事分野強化とEdge買収で多角化進展。2025年黒字化を目指すが、達成は不透明。",
                "macro_to_risk": "宇宙インフラ投資拡大は追い風だが、政府依存度が高い。5%配分は妥当だが、資金調達リスクは？",
                "risk_reply": "確かに増資リスクは継続。ただし国家安全保障需要は底堅く、5%配分は適正。収益改善待ちの段階。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "$12.80サポート重要。割れれば$10-11まで調整も。",
                "fund_view": "黒字化遅延でも成長性は評価。$11-12が中長期下値メド。",
                "macro_view": "宇宙セクター調整なら$9-10まで下落リスク。需給悪化を警戒。",
                "risk_view": "$12割れは収益悪化を示唆。ここが損切りライン。",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "黒字化達成で$20-25、事業拡大で$30も射程圏内。",
                "fund_view": "成功時は$25-30が目標。宇宙インフラの多角化で成長加速。",
                "macro_view": "宇宙経済拡大で$35+も可能。長期的な市場拡大に期待。",
                "risk_view": "黒字化確率60%として期待値は魅力的。3年後$25達成確率45%。",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "第1段階: $14.50-15.50で60%、第2段階: 収益改善確認で40%",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "$12を明確に下抜け",
                "fund_exit": "黒字化計画の大幅遅延",
                "macro_exit": "宇宙予算の大幅削減",
                "risk_exit": "収益悪化の継続確定",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "2-4年、黒字化軌道まで",
                "exit_plan": "黒字化で30%利確、事業拡大で追加40%、残り30%は長期保有",
            },
        },
        "OII": {
            "current_situation": "海洋エンジニアリング大手、ROVサービス・ロボティクス成長",
            "round1": {
                "tech_to_fund": "RSI(56.8)で中立、$20-21レンジ圏。Q1売上13%増・純利益233%増は印象的だが、持続可能性は？",
                "fund_reply": "海洋エネルギー需要回復が業績押し上げ。ROVサービスとロボティクス事業の成長性は高い。ただし エネルギー価格依存は課題。",
                "macro_to_risk": "深海油田開発再開は追い風だが、エネルギー政策変更リスクもある。10%配分はエネルギー依存を考慮すると妥当？",
                "risk_reply": "エネルギー価格依存は最大のリスク。ただし海洋ロボティクス需要は多様化しており、10%配分は適正と判断。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "$19-20が重要サポート。割れれば$17-18まで調整も。",
                "fund_view": "エネルギー価格下落でも技術価値は維持。$18-19が中長期下値メド。",
                "macro_view": "エネルギー市場低迷なら$15-17まで下落リスク。需要減少を警戒。",
                "risk_view": "$18割れはエネルギー低迷を示唆。ここが損切りライン。",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "エネルギー回復で$25-27、ロボティクス拡大で$30も射程圏内。",
                "fund_view": "成功時は$27-32が目標。海洋技術のリーダーとして高評価。",
                "macro_view": "海洋開発本格化で$35+も可能。脱炭素とエネルギー安保の両立。",
                "risk_view": "エネルギー回復確率70%として期待値は良好。3年後$28達成確率55%。",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "現水準($21前後)でエントリー可、$19-20押し目は絶好機として追加投資",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "$18を明確に下抜け",
                "fund_exit": "海洋エネルギー需要の構造的減少",
                "macro_exit": "エネルギー政策の大幅転換",
                "risk_exit": "エネルギー価格の長期低迷確定",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "2-4年、エネルギー回復サイクルまで",
                "exit_plan": "$25で30%利確、$28で追加40%、残り30%は長期サイクル投資として保有",
            },
        },
        "RKLB": {
            "current_situation": "小型ロケット市場リーダー、Neutron開発とSpaceX競合の分岐点",
            "round1": {
                "tech_to_fund": "売上78%増・打ち上げ68回成功は印象的だが、現在の高バリュエーション（売上予想11倍）は正当化可能？Neutron開発進捗が鍵？",
                "fund_reply": "高バリュエーションは事実だが、小型ロケット市場年率20%成長を考慮すれば妥当。Neutron成功なら中規模市場参入で成長加速。2026年黒字転換予想。",
                "macro_to_risk": "宇宙産業拡大は確実だが、SpaceXとの競合激化リスクが顕在化。技術優位性は維持できるが、価格競争は避けられない。10%配分は適正？",
                "risk_reply": "SpaceX競合は最大のリスク。ただし小型ロケット市場はニッチで差別化可能。10%配分は成長期待と高ボラティリティのバランスを考慮すると妥当。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "$8-10が重要サポート。割れれば$6-7まで急落リスク。高ボラティリティ要注意。",
                "fund_view": "PER15倍相当($7-8)まで下落でも技術価値は維持。成長株として底値は$6前後。",
                "macro_view": "宇宙セクター調整なら$5-7まで下落リスク。政府予算削減や競合激化を織り込み。",
                "risk_view": "$8割れは成長ストーリー破綻を示唆。$6がブレイクイーブン水準として最終防衛ライン。",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "Neutron成功で$20-25、小型ロケット市場拡大で$30も射程圏内。",
                "fund_view": "2027年売上10億ドル達成なら$25-35が目標。宇宙インフラの要として高評価期待。",
                "macro_view": "宇宙経済本格化で$40+も理論上可能。政府・民間需要の両輪で成長加速。",
                "risk_view": "Neutron成功確率60%、市場拡大70%として期待値は魅力的。3年後$25達成確率50%。",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "第1段階: $8-12で50%、第2段階: Neutron進捗確認で30%、第3段階: 競合優位性確定で20%",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "$8を明確に下抜け、高ボラティリティ継続",
                "fund_exit": "Neutron開発の大幅遅延や技術的失敗",
                "macro_exit": "SpaceXとの価格競争で市場シェア大幅低下",
                "risk_exit": "成長率鈍化で高バリュエーション正当化困難",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "3-5年、Neutron商用化から市場拡大まで",
                "exit_plan": "$18で30%利確、$25で追加40%、残り30%は宇宙経済拡大期まで長期保有",
            },
        },
    }

    discussion = expert_discussions.get(
        ticker,
        {
            "current_situation": "分析データに基づく総合判断",
            "round1": {
                "tech_to_fund": f"RSI({latest_data['RSI']:.1f})、テクニカル状況について、ファンダメンタルズとの整合性は？",
                "fund_reply": "現在の株価水準は適正と判断。成長性を考慮すれば投資妙味あり。",
                "macro_to_risk": "マクロ環境の影響を考慮すると、リスク管理の観点で現在の配分は妥当？",
                "risk_reply": f"配分{allocation}%は適正水準。リスク・リターンバランス良好。",
            },
            "round2": {
                "topic": "下値目標の確定",
                "tech_view": "テクニカル分析による下値目処",
                "fund_view": "ファンダメンタル下値",
                "macro_view": "マクロ要因下値",
                "risk_view": "リスク管理下値",
            },
            "round3": {
                "topic": "上値目標の設定",
                "tech_view": "テクニカル上値目標",
                "fund_view": "ファンダメンタル上値",
                "macro_view": "マクロ要因上値",
                "risk_view": "リスク調整上値",
            },
            "round4": {
                "topic": "段階的エントリー戦略",
                "strategy": "スコアに基づく段階的アプローチ",
            },
            "round5": {
                "topic": "撤退・損切り基準",
                "tech_exit": "テクニカル損切り",
                "fund_exit": "ファンダメンタル損切り",
                "macro_exit": "マクロ要因損切り",
                "risk_exit": "リスク管理損切り",
            },
            "round6": {
                "topic": "保有期間と出口戦略",
                "period": "適切な保有期間",
                "exit_plan": "段階的利確戦略",
            },
        },
    )

    expert_discussion_text = f"""
#### 📊 現在の投資環境評価
**{discussion['current_situation']}**

#### 🎯 6ラウンド専門家討論（全6ラウンド固定・1発言180字以内厳守）

**Round 1: エントリーシグナル検証**
TECH→FUND: {discussion['round1']['tech_to_fund']}
FUND: {discussion['round1']['fund_reply']}
MACRO→RISK: {discussion['round1']['macro_to_risk']}
RISK: {discussion['round1']['risk_reply']}

**Round 2: {discussion['round2']['topic']}**
TECH: {discussion['round2']['tech_view']}
FUND: {discussion['round2']['fund_view']}
MACRO: {discussion['round2']['macro_view']}
RISK: {discussion['round2']['risk_view']}

**Round 3: {discussion['round3']['topic']}**
TECH: {discussion['round3']['tech_view']}
FUND: {discussion['round3']['fund_view']}
MACRO: {discussion['round3']['macro_view']}
RISK: {discussion['round3']['risk_view']}

**Round 4: {discussion['round4']['topic']}**
{discussion['round4']['strategy']}

**Round 5: {discussion['round5']['topic']}**
TECH: {discussion['round5']['tech_exit']}
FUND: {discussion['round5']['fund_exit']}
MACRO: {discussion['round5']['macro_exit']}
RISK: {discussion['round5']['risk_exit']}

**Round 6: {discussion['round6']['topic']}**
{discussion['round6']['period']}
{discussion['round6']['exit_plan']}
"""

    return expert_discussion_text


def generate_portfolio_report(results: dict, date_str: str):
    """統合レポートを生成・保存（4専門家討論付き）"""
    report_filename = f"./reports/portfolio_review_{date_str}.md"

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(f"# ポートフォリオ統合レビュー 〈{date_str}〉\n\n")

        # サマリー
        f.write("## エグゼクティブサマリー\n\n")
        summary = results["portfolio_summary"]
        f.write(f"- **分析対象**: {summary['analysis_coverage']}\n")
        f.write(
            f"- **分析成功率**: {summary['successful_analysis']}/{summary['total_tickers']} 銘柄\n"
        )
        f.write(f"- **総配分**: {summary['total_allocation']}%\n\n")

        # 4専門家統合スコア
        f.write("## 4専門家統合スコア\n\n")
        f.write(
            "| 銘柄 | 配分 | TECH | FUND | MACRO | RISK | 総合 | 推奨アクション |\n"
        )
        f.write(
            "|------|------|------|------|-------|------|------|----------------|\n"
        )

        # スコア順でソート
        sorted_scores = sorted(
            results["expert_scores"].items(),
            key=lambda x: x[1]["OVERALL"],
            reverse=True,
        )

        for ticker, scores in sorted_scores:
            allocation = results["individual_analysis"][ticker]["allocation"]
            recommendation = results["recommendations"][ticker]

            f.write(
                f"| {ticker} | {allocation}% | "
                f"{scores['TECH']:.1f}★ | {scores['FUND']:.1f}★ | "
                f"{scores['MACRO']:.1f}★ | {scores['RISK']:.1f}★ | "
                f"{scores['OVERALL']:.1f}★ | {recommendation['action']} |\n"
            )

        # ポートフォリオ全体の戦略提言
        f.write("\n## 🎯 ポートフォリオ戦略提言\n\n")

        # アクション別集計
        actions = {"BUY": [], "BUY_DIP": [], "CAUTIOUS": [], "WAIT": [], "AVOID": []}
        for ticker, rec in results["recommendations"].items():
            action = rec["action"]
            if action in actions:
                allocation = results["individual_analysis"][ticker]["allocation"]
                actions[action].append(f"{ticker}({allocation}%)")

        f.write("### 推奨アクション別配分\n\n")
        action_names = {
            "BUY": "🟢 **即時エントリー**",
            "BUY_DIP": "🟡 **押し目買い**",
            "CAUTIOUS": "🟠 **慎重エントリー**",
            "WAIT": "⚪ **様子見**",
            "AVOID": "🔴 **回避**",
        }

        for action, name in action_names.items():
            if actions[action]:
                total_allocation = sum(
                    int(t.split("(")[1].split("%")[0]) for t in actions[action]
                )
                f.write(
                    f"- {name}: {', '.join(actions[action])} (合計{total_allocation}%)\n"
                )

        f.write("\n### リスク管理状況\n\n")
        high_risk_allocation = sum(
            results["individual_analysis"][t]["allocation"]
            for t, s in results["expert_scores"].items()
            if s["RISK"] < 2.5
        )
        f.write(f"- **高リスク銘柄配分**: {high_risk_allocation}% ")
        if high_risk_allocation > 20:
            f.write("⚠️ **配分過多、リバランス推奨**\n")
        else:
            f.write("✅ **適正水準**\n")

        # 個別銘柄詳細分析（4専門家討論付き）
        f.write("\n## 📋 個別銘柄詳細分析\n\n")

        for ticker, scores in sorted_scores:
            analysis = results["individual_analysis"][ticker]
            if analysis["success"]:
                f.write(
                    f"### {ticker} ({analysis['allocation']}%配分) - 総合{scores['OVERALL']:.1f}★\n"
                )
                f.write(
                    f"**最新株価**: ${analysis['latest_price']:.2f} | **推奨**: {results['recommendations'][ticker]['recommendation']}\n"
                )

                # CSVデータを読み込んで詳細討論を生成
                try:
                    csv_filename = f"{ticker}_analysis_data_{date_str}.csv"
                    df = pd.read_csv(csv_filename, index_col=0, parse_dates=True)
                    latest_data = df.iloc[-1]

                    discussion = generate_detailed_expert_discussion(
                        ticker,
                        latest_data,
                        scores["TECH"],
                        scores["FUND"],
                        scores["MACRO"],
                        scores["RISK"],
                        analysis["allocation"],
                    )
                    f.write(discussion)

                except Exception as e:
                    f.write(f"\n*詳細分析データの読み込みエラー: {e}*\n")

                f.write("\n---\n")
            else:
                f.write(f"### {ticker} ({analysis['allocation']}%配分)\n")
                f.write(f"**エラー**: {analysis.get('error', '不明')}\n\n")

        # 次回レビュー推奨
        f.write("\n## 📅 次回レビュータイミング\n\n")
        f.write("- **週次チェック**: `python3 scripts/portfolio_quick_review.py`\n")
        f.write("- **アラート監視**: `python3 scripts/portfolio_alerts.py`\n")
        f.write("- **詳細分析**: `python3 unified_stock_analyzer.py --portfolio`\n")
        f.write("- **四半期決算後**: 各銘柄の個別分析を推奨\n\n")

        f.write("---\n\n")
        f.write(
            "> **免責事項**: 本情報は教育目的のシミュレーションであり、投資助言ではありません。実際の投資判断は、ご自身の責任において行うようにしてください。\n"
        )

    print(f"\n📄 4専門家討論付き統合レポートを {report_filename} に保存しました。")


def main():
    """
    tiker-analyzeコマンドのエントリーポイント
    setup.pyのconsole_scriptsから呼び出される
    """
    import argparse

    parser = argparse.ArgumentParser(description="米国株の株価分析とチャート作成")
    parser.add_argument("--ticker", type=str, help="分析対象のティッカーシンボル")
    parser.add_argument("--date", type=str, help="分析基準日 (YYYY-MM-DD形式)")
    parser.add_argument(
        "--portfolio", action="store_true", help="ポートフォリオ統合分析を実行"
    )
    parser.add_argument(
        "--tickers", type=str, help="ポートフォリオ銘柄 (カンマ区切り: TSLA,FSLR,ASTS)"
    )
    parser.add_argument("--weights", type=str, help="配分比率 (カンマ区切り: 30,25,15)")

    args = parser.parse_args()

    if args.portfolio:
        # ポートフォリオ分析
        if args.tickers and args.weights:
            tickers = args.tickers.split(",")
            weights = [float(w) for w in args.weights.split(",")]
            portfolio_config = dict(zip(tickers, weights))
        else:
            # デフォルトポートフォリオ（RKLB追加版）
            portfolio_config = {
                "TSLA": 20,  # 25% → 20%に削減
                "FSLR": 20,  # 25% → 20%に削減
                "RKLB": 10,  # 新規追加：小型ロケット市場リーダー
                "ASTS": 10,  # 維持
                "OKLO": 10,  # 維持
                "JOBY": 10,  # 維持
                "OII": 10,  # 維持
                "LUNR": 5,   # 維持
                "RDW": 5,    # 維持
            }

        results = analyze_portfolio(portfolio_config, args.date)
        print(f"\n=== ポートフォリオ分析完了 ===")
        print(
            f"統合レポート: ./reports/portfolio_review_{results.get('analysis_date', 'unknown')}.md"
        )

    elif args.ticker:
        # 個別銘柄分析
        success, message = analyze_and_chart_stock(args.ticker, args.date)
        print(f"\n結果: {message}")

    else:
        print("エラー: --ticker または --portfolio のいずれかを指定してください")
        parser.print_help()


if __name__ == "__main__":
    main()
