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

def analyze_portfolio(portfolio_config: dict, today_date_str: Optional[str] = None) -> dict:
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
    
    today_str = today_jst.strftime('%Y-%m-%d')
    
    print(f"\n=== ポートフォリオ統合分析開始 ({today_str}) ===")
    
    results = {
        "analysis_date": today_str,
        "portfolio_summary": {},
        "individual_analysis": {},
        "expert_scores": {},
        "recommendations": {},
        "risk_metrics": {}
    }
    
    # 各銘柄の分析を実行
    for ticker, allocation in portfolio_config.items():
        print(f"\n--- {ticker} ({allocation}%配分) 分析中 ---")
        success, message = analyze_and_chart_stock(ticker, today_date_str)
        
        if success:
            # 分析結果を読み込み
            csv_filename = f'{ticker}_analysis_data_{today_str}.csv'
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
                    "latest_price": latest['Close'],
                    "success": True,
                    "message": message
                }
                
                results["expert_scores"][ticker] = {
                    "TECH": tech_score,
                    "FUND": fund_score, 
                    "MACRO": macro_score,
                    "RISK": risk_score,
                    "OVERALL": (tech_score + fund_score + macro_score + risk_score) / 4
                }
                
                # エントリー推奨度
                recommendation = get_entry_recommendation(tech_score, fund_score, macro_score, risk_score)
                results["recommendations"][ticker] = recommendation
                
            except Exception as e:
                print(f"警告: {ticker}の詳細分析でエラー: {e}")
                results["individual_analysis"][ticker] = {
                    "allocation": allocation,
                    "success": False,
                    "error": str(e)
                }
        else:
            results["individual_analysis"][ticker] = {
                "allocation": allocation,
                "success": False,
                "error": message
            }
    
    # ポートフォリオ全体のサマリー計算
    successful_tickers = [t for t, data in results["individual_analysis"].items() if data["success"]]
    total_allocation = sum(portfolio_config[t] for t in successful_tickers)
    
    results["portfolio_summary"] = {
        "total_tickers": len(portfolio_config),
        "successful_analysis": len(successful_tickers),
        "total_allocation": total_allocation,
        "analysis_coverage": f"{len(successful_tickers)}/{len(portfolio_config)} 銘柄"
    }
    
    # 統合レポート生成
    generate_portfolio_report(results, today_str)
    
    return results

def calculate_tech_score(df: pd.DataFrame) -> float:
    """テクニカル分析スコア (1-5)"""
    latest = df.iloc[-1]
    score = 3.0  # 中立から開始
    
    # 移動平均との関係
    if latest['Close'] > latest['EMA20']:
        score += 0.5
    if latest['Close'] > latest['EMA50']:
        score += 0.5
    if latest['Close'] > latest['SMA200']:
        score += 0.5
    
    # RSI評価
    if 30 <= latest['RSI'] <= 70:
        score += 0.3
    elif latest['RSI'] < 30:
        score += 0.5  # 売られすぎで買いチャンス
    else:
        score -= 0.5  # 買われすぎで注意
    
    # トレンド評価
    ema20_trend = (latest['EMA20'] - df['EMA20'].iloc[-5]) / df['EMA20'].iloc[-5]
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
        "OII": 3.8  # 海洋エンジニアリング・ROVサービス大手、Q1売上13%増、純利益233%増
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
        "OII": 3.8  # 海洋エネルギー需要増、ロボティクス成長、地政学リスクあり
    }
    return macro_scores.get(ticker, 3.0)

def calculate_risk_score(df: pd.DataFrame, allocation: float) -> float:
    """リスク管理スコア (1-5)"""
    # 配分比率とボラティリティに基づくリスク評価
    volatility = df['Close'].pct_change().std() * np.sqrt(252)  # 年率ボラティリティ
    
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

def get_entry_recommendation(tech: float, fund: float, macro: float, risk: float) -> dict:
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
    
    return {
        "score": overall_score,
        "recommendation": recommendation,
        "action": action
    }

def generate_detailed_expert_discussion(ticker: str, latest_data: pd.Series, tech_score: float, fund_score: float, macro_score: float, risk_score: float, allocation: float) -> str:
    """4専門家の詳細討論を生成"""
    
    # 銘柄別の専門家討論テンプレート
    expert_discussions = {
        "TSLA": {
            "current_situation": "EV競争激化とロボタクシー期待の綱引き状態",
            "tech_view": f"RSI({latest_data['RSI']:.1f})で売られすぎ気味、$300サポート重要",
            "fund_view": "短期業績悪化vs長期ロボタクシー期待、Wells Fargo$120は極端",
            "macro_view": "EV市場鈍化、米中関税リスク、金利高止まりで需要圧迫",
            "risk_view": f"ボラティリティ高、配分{allocation}%は慎重管理要",
            "entry_strategy": "押し目待ち($250-280ゾーン)、段階的エントリー推奨",
            "exit_strategy": "$240損切り、ロボタクシー商用化で段階利確"
        },
        "FSLR": {
            "current_situation": "政策支援とCdTe技術優位性、中国競合との価格競争",
            "tech_view": f"RSI({latest_data['RSI']:.1f})で調整一巡、200日線奪還が焦点",
            "fund_view": "IRA支援継続、66GW受注残、Jefferies$192目標は保守的",
            "macro_view": "脱炭素政策追い風、AIデータセンター電力需要拡大期待",
            "risk_view": f"政策リスク最大、配分{allocation}%は政策動向要監視",
            "entry_strategy": "即時エントリー可、$130-150ゾーンは絶好機",
            "exit_strategy": "$120政策リスク損切り、$210段階利確開始"
        },
        "ASTS": {
            "current_situation": "既存スマホ直接衛星通信の革新技術、事業化前",
            "tech_view": f"RSI({latest_data['RSI']:.1f})で過熱感、$30-42調整待ち",
            "fund_view": "AT&T/Verizon提携、巨大市場潜在性、収益化前の投機段階",
            "macro_view": "衛星通信市場拡大、5G補完需要、地政学リスクで需要増",
            "risk_view": f"極めて投機的、配分{allocation}%でも高リスク",
            "entry_strategy": "大幅調整待ち、商用化成功まで少額投資",
            "exit_strategy": "$25技術リスク損切り、成功時段階利確"
        },
        "OKLO": {
            "current_situation": "小型高速炉Aurora、アルトマン支援で注目",
            "tech_view": f"RSI({latest_data['RSI']:.1f})で中立、上昇トレンド継続",
            "fund_view": "2044年電力契約、AI電力需要、規制承認が成否の鍵",
            "macro_view": "SMR市場拡大期待、クリーンエネルギー政策支援",
            "risk_view": f"NRC規制リスク最大、配分{allocation}%は妥当",
            "entry_strategy": "押し目買い($40-48)、規制承認待ち",
            "exit_strategy": "$30規制リスク損切り、商用化で段階利確"
        },
        "JOBY": {
            "current_situation": "eVTOL先駆者、FAA認証進捗とトヨタ投資",
            "tech_view": f"RSI({latest_data['RSI']:.1f})で健全、強い上昇トレンド",
            "fund_view": "FAA認証最終段階、2025年200機納入可能性、市場創造リスク",
            "macro_view": "政府ドローン優位性支援、都市交通革新テーマ",
            "risk_view": f"量産化不確実性、配分{allocation}%は適正",
            "entry_strategy": "即時エントリー可、押し目($8.00-8.50)歓迎",
            "exit_strategy": "$6.50市場形成失敗損切り、$12目標段階利確"
        },
        "LUNR": {
            "current_situation": "民間初月面着陸実績、NASA依存とミッション成否",
            "tech_view": f"RSI({latest_data['RSI']:.1f})で弱含み、$9-10サポート重要",
            "fund_view": "月面着陸実績、NASA48.2億ドル契約、IM-3成否が焦点",
            "macro_view": "第二次宇宙開発競争、月経済圏構想で長期期待",
            "risk_view": f"ミッション成否依存、配分{allocation}%は高リスク許容",
            "entry_strategy": "IM-3前後イベント投資、少額配分厳守",
            "exit_strategy": "$9ミッション失敗損切り、成功時大幅利確"
        },
        "RDW": {
            "current_situation": "宇宙インフラ多角化、軌道上製造とEdge買収",
            "tech_view": f"RSI({latest_data['RSI']:.1f})で調整中、$12.80サポート",
            "fund_view": "売上24.7%増、軍事分野強化、継続赤字が課題",
            "macro_view": "宇宙インフラ投資拡大、国家安全保障需要底堅い",
            "risk_view": f"資金調達リスク、配分{allocation}%は妥当",
            "entry_strategy": "押し目買い($14.50-15.50)、収益改善待ち",
            "exit_strategy": "$12収益悪化損切り、黒字化で利確"
        },
        "OII": {
            "current_situation": "海洋エンジニアリング大手、ROVサービス・ロボティクス成長",
            "tech_view": f"RSI({latest_data['RSI']:.1f})で中立、$20-21レンジ圏",
            "fund_view": "Q1売上13%増・純利益233%増、海洋エネルギー需要回復",
            "macro_view": "深海油田開発再開、海洋ロボティクス需要拡大",
            "risk_view": f"エネルギー価格依存、配分{allocation}%は適正",
            "entry_strategy": "現水準($21前後)でエントリー可、$19-20押し目歓迎",
            "exit_strategy": "$18エネルギー低迷損切り、$25-27利確目標"
        }
    }
    
    discussion = expert_discussions.get(ticker, {
        "current_situation": "分析データに基づく総合判断",
        "tech_view": f"RSI({latest_data['RSI']:.1f})、テクニカル状況要監視",
        "fund_view": "ファンダメンタルズ分析に基づく評価",
        "macro_view": "マクロ環境の影響を考慮",
        "risk_view": f"配分{allocation}%でのリスク管理",
        "entry_strategy": "スコアに基づく段階的アプローチ",
        "exit_strategy": "リスク・リワード管理重視"
    })
    
    expert_discussion_text = f"""
#### 📊 現在の投資環境評価
**{discussion['current_situation']}**

#### 🎯 4専門家討論サマリー

**TECH** (スコア: {tech_score:.1f}★)
*{discussion['tech_view']}*

**FUND** (スコア: {fund_score:.1f}★)  
*{discussion['fund_view']}*

**MACRO** (スコア: {macro_score:.1f}★)
*{discussion['macro_view']}*

**RISK** (スコア: {risk_score:.1f}★)
*{discussion['risk_view']}*

#### 💡 統合投資戦略
- **エントリー**: {discussion['entry_strategy']}
- **エグジット**: {discussion['exit_strategy']}
"""
    
    return expert_discussion_text

def generate_portfolio_report(results: dict, date_str: str):
    """統合レポートを生成・保存（4専門家討論付き）"""
    report_filename = f"./reports/portfolio_review_{date_str}.md"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(f"# ポートフォリオ統合レビュー 〈{date_str}〉\n\n")
        
        # サマリー
        f.write("## エグゼクティブサマリー\n\n")
        summary = results["portfolio_summary"]
        f.write(f"- **分析対象**: {summary['analysis_coverage']}\n")
        f.write(f"- **分析成功率**: {summary['successful_analysis']}/{summary['total_tickers']} 銘柄\n")
        f.write(f"- **総配分**: {summary['total_allocation']}%\n\n")
        
        # 4専門家統合スコア
        f.write("## 4専門家統合スコア\n\n")
        f.write("| 銘柄 | 配分 | TECH | FUND | MACRO | RISK | 総合 | 推奨アクション |\n")
        f.write("|------|------|------|------|-------|------|------|----------------|\n")
        
        # スコア順でソート
        sorted_scores = sorted(
            results["expert_scores"].items(), 
            key=lambda x: x[1]["OVERALL"], 
            reverse=True
        )
        
        for ticker, scores in sorted_scores:
            allocation = results["individual_analysis"][ticker]["allocation"]
            recommendation = results["recommendations"][ticker]
            
            f.write(f"| {ticker} | {allocation}% | "
                   f"{scores['TECH']:.1f}★ | {scores['FUND']:.1f}★ | "
                   f"{scores['MACRO']:.1f}★ | {scores['RISK']:.1f}★ | "
                   f"{scores['OVERALL']:.1f}★ | {recommendation['action']} |\n")
        
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
            "AVOID": "🔴 **回避**"
        }
        
        for action, name in action_names.items():
            if actions[action]:
                total_allocation = sum(int(t.split('(')[1].split('%')[0]) for t in actions[action])
                f.write(f"- {name}: {', '.join(actions[action])} (合計{total_allocation}%)\n")
        
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
                f.write(f"### {ticker} ({analysis['allocation']}%配分) - 総合{scores['OVERALL']:.1f}★\n")
                f.write(f"**最新株価**: ${analysis['latest_price']:.2f} | **推奨**: {results['recommendations'][ticker]['recommendation']}\n")
                
                # CSVデータを読み込んで詳細討論を生成
                try:
                    csv_filename = f'{ticker}_analysis_data_{date_str}.csv'
                    df = pd.read_csv(csv_filename, index_col=0, parse_dates=True)
                    latest_data = df.iloc[-1]
                    
                    discussion = generate_detailed_expert_discussion(
                        ticker, latest_data, 
                        scores['TECH'], scores['FUND'], scores['MACRO'], scores['RISK'],
                        analysis['allocation']
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
        f.write("> **免責事項**: 本情報は教育目的のシミュレーションであり、投資助言ではありません。実際の投資判断は、ご自身の責任において行うようにしてください。\n")
    
    print(f"\n📄 4専門家討論付き統合レポートを {report_filename} に保存しました。")

def main():
    """
    tiker-analyzeコマンドのエントリーポイント
    setup.pyのconsole_scriptsから呼び出される
    """
    import argparse
    parser = argparse.ArgumentParser(description='米国株の株価分析とチャート作成')
    parser.add_argument('--ticker', type=str, help='分析対象のティッカーシンボル')
    parser.add_argument('--date', type=str, help='分析基準日 (YYYY-MM-DD形式)')
    parser.add_argument('--portfolio', action='store_true', help='ポートフォリオ統合分析を実行')
    parser.add_argument('--tickers', type=str, help='ポートフォリオ銘柄 (カンマ区切り: TSLA,FSLR,ASTS)')
    parser.add_argument('--weights', type=str, help='配分比率 (カンマ区切り: 30,25,15)')
    
    args = parser.parse_args()

    if args.portfolio:
        # ポートフォリオ分析
        if args.tickers and args.weights:
            tickers = args.tickers.split(',')
            weights = [float(w) for w in args.weights.split(',')]
            portfolio_config = dict(zip(tickers, weights))
        else:
            # デフォルトポートフォリオ（OII追加版）
            portfolio_config = {
                "TSLA": 25,    # 30% → 25%に削減
                "FSLR": 25,    # 30% → 25%に削減
                "ASTS": 10,    # 維持
                "OKLO": 10,    # 維持
                "JOBY": 10,    # 維持
                "OII": 10,     # 新規追加
                "LUNR": 5,     # 維持
                "RDW": 5       # 維持
            }
        
        results = analyze_portfolio(portfolio_config, args.date)
        print(f"\n=== ポートフォリオ分析完了 ===")
        print(f"統合レポート: ./reports/portfolio_review_{results.get('analysis_date', 'unknown')}.md")
    
    elif args.ticker:
        # 個別銘柄分析
        success, message = analyze_and_chart_stock(args.ticker, args.date)
        print(f"\n結果: {message}")
    
    else:
        print("エラー: --ticker または --portfolio のいずれかを指定してください")
        parser.print_help()

if __name__ == '__main__':
    main()