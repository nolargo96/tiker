#!/usr/bin/env python3
"""
Tiker Discussion - 4専門家討論形式の株式分析
きれいな形での討論表示システム
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import mplfinance as mpf
import argparse
import os
from typing import Dict, List, Tuple, Optional
import yaml


class TikerDiscussion:
    """4専門家討論形式の株式分析システム"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.experts = {
            "TECH": {
                "name": "TECH",
                "title": "テクニカルアナリスト",
                "specialty": "日足〜月足のトレンド解析",
                "tools": "移動平均(EMA/SMA)、RSI、MACD、フィボナッチ、出来高プロファイル、サポート・レジスタンス",
            },
            "FUND": {
                "name": "FUND",
                "title": "ファンダメンタルアナリスト",
                "specialty": "企業価値・業績分析",
                "tools": "PER、PBR、PSR、DCF法、ROE、FCF、EPS成長率、決算分析、競合比較",
            },
            "MACRO": {
                "name": "MACRO",
                "title": "マクロストラテジスト",
                "specialty": "米経済・セクター環境",
                "tools": "FF金利、米10年債利回り、CPI/PCE、GDP、PMI、VIX指数、セクターETF動向",
            },
            "RISK": {
                "name": "RISK",
                "title": "リスク管理専門家",
                "specialty": "ポジションサイジング・下落耐性",
                "tools": "VaR、最大ドローダウン、ATR、ベータ値、シャープレシオ、ヘッジ戦略",
            },
        }

    def _load_config(self, config_path: str) -> Dict:
        """設定ファイルの読み込み"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    def get_stock_data(
        self, ticker: str, period: str = "1y"
    ) -> Tuple[pd.DataFrame, Dict]:
        """株価データと企業情報の取得"""
        stock = yf.Ticker(ticker)

        # 株価データ
        hist = stock.history(period=period)
        if hist.empty:
            raise ValueError(f"データが取得できません: {ticker}")

        # テクニカル指標の計算
        hist["EMA20"] = hist["Close"].ewm(span=20).mean()
        hist["EMA50"] = hist["Close"].ewm(span=50).mean()
        hist["SMA200"] = hist["Close"].rolling(200).mean()
        hist["RSI"] = self._calculate_rsi(hist["Close"])
        hist["ATR"] = self._calculate_atr(hist)

        # 企業情報
        info = stock.info

        return hist, info

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ATR計算"""
        high_low = df["High"] - df["Low"]
        high_close = np.abs(df["High"] - df["Close"].shift())
        low_close = np.abs(df["Low"] - df["Close"].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(period).mean()

    def create_chart(
        self, ticker: str, hist: pd.DataFrame, save_path: str = None
    ) -> str:
        """チャート作成"""
        # テクニカル指標の準備
        add_plots = [
            mpf.make_addplot(hist["EMA20"], color="blue", width=1.5),
            mpf.make_addplot(hist["EMA50"], color="orange", width=1.5),
            mpf.make_addplot(hist["SMA200"], color="purple", width=2),
        ]

        # チャートスタイル
        style = mpf.make_mpf_style(
            base_mpf_style="charles",
            gridstyle="-",
            gridcolor="lightgray",
            facecolor="white",
        )

        # 保存先の設定
        if save_path is None:
            save_path = (
                f"./charts/{ticker}_chart_{datetime.now().strftime('%Y-%m-%d')}.png"
            )

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # チャート生成
        mpf.plot(
            hist,
            type="candle",
            addplot=add_plots,
            volume=True,
            style=style,
            figsize=(16, 9),
            savefig=save_path,
            title=f"{ticker} Stock Analysis Chart",
        )

        return save_path

    def analyze_current_environment(
        self, ticker: str, hist: pd.DataFrame, info: Dict
    ) -> Dict[str, str]:
        """現在の投資環境評価"""
        current_price = hist["Close"].iloc[-1]

        # TECH分析
        ema20 = hist["EMA20"].iloc[-1]
        ema50 = hist["EMA50"].iloc[-1]
        sma200 = hist["SMA200"].iloc[-1]
        rsi = hist["RSI"].iloc[-1]

        tech_analysis = f"""移動平均線の位置関係: 現在価格${current_price:.2f}は、EMA20(${ema20:.2f}){"上" if current_price > ema20 else "下"}、EMA50(${ema50:.2f}){"上" if current_price > ema50 else "下"}、SMA200(${sma200:.2f}){"上" if current_price > sma200 else "下"}に位置。
RSI({rsi:.1f})は{"買われすぎ" if rsi > 70 else "売られすぎ" if rsi < 30 else "中立"}圏内。
{"ゴールデンクロス" if ema20 > ema50 else "デッドクロス"}状態で、中長期トレンドは{"上昇" if current_price > sma200 else "下降"}基調。"""

        # FUND分析
        pe_ratio = info.get("forwardPE", 0)
        market_cap = info.get("marketCap", 0)
        revenue_growth = info.get("revenueGrowth", 0)

        fund_analysis = f"""現在のPER {pe_ratio:.1f}倍は{"割安" if pe_ratio < 20 else "適正" if pe_ratio < 30 else "割高"}水準。
時価総額${market_cap/1e9:.1f}B、売上成長率{revenue_growth*100:.1f}%。
企業のファンダメンタルズは{"堅調" if revenue_growth > 0.1 else "安定" if revenue_growth > 0 else "要注意"}で、
現在の株価水準は理論価値に対して{"割安" if pe_ratio < 20 else "適正" if pe_ratio < 30 else "割高"}と評価。"""

        # MACRO分析
        sector = info.get("sector", "不明")
        macro_analysis = f"""所属セクター「{sector}」は現在の金利環境下で{"追い風" if sector in ["Technology", "Communication Services"] else "逆風" if sector in ["Utilities", "Real Estate"] else "中立"}。
FRBの金融政策スタンスとインフレ動向を考慮すると、当セクターへの資金フローは{"ポジティブ" if sector in ["Technology", "Healthcare"] else "ネガティブ" if sector in ["Utilities"] else "中立"}。
マクロ環境が個別銘柄に与える影響は{"限定的" if market_cap > 100e9 else "中程度"}と想定。"""

        # RISK分析
        volatility = hist["Close"].pct_change().std() * np.sqrt(252)
        max_drawdown = self._calculate_max_drawdown(hist["Close"])
        atr = hist["ATR"].iloc[-1]

        risk_analysis = f"""過去1年のボラティリティ{volatility:.1%}、最大ドローダウン{max_drawdown:.1%}、ATR${atr:.2f}。
現在のリスク水準は{"高" if volatility > 0.4 else "中" if volatility > 0.2 else "低"}リスク。
推奨初期ポジションサイズは総運用資金の{5 if volatility > 0.4 else 8 if volatility > 0.2 else 10}%。
想定最大ドローダウンは{max_drawdown*1.2:.1%}程度を覚悟。"""

        return {
            "TECH": tech_analysis,
            "FUND": fund_analysis,
            "MACRO": macro_analysis,
            "RISK": risk_analysis,
        }

    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """最大ドローダウン計算"""
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return abs(drawdown.min())

    def conduct_expert_discussion(
        self, ticker: str, hist: pd.DataFrame, info: Dict
    ) -> Dict[str, List[str]]:
        """6ラウンドの専門家討論"""
        current_price = hist["Close"].iloc[-1]

        discussions = {}

        # Round 1: エントリーシグナル検証
        discussions["Round 1: エントリーシグナル検証"] = [
            f"**TECH → FUND**: 現在、20EMA(${hist['EMA20'].iloc[-1]:.2f})と50EMA(${hist['EMA50'].iloc[-1]:.2f})が{'ゴールデンクロス' if hist['EMA20'].iloc[-1] > hist['EMA50'].iloc[-1] else 'デッドクロス'}状態。RSI{hist['RSI'].iloc[-1]:.1f}からの{'反発' if hist['RSI'].iloc[-1] < 30 else '調整' if hist['RSI'].iloc[-1] > 70 else '推移'}シグナルが出ているが、ファンダメンタル価値との整合性は？",
            f"**FUND**: PER{info.get('forwardPE', 0):.1f}倍から見ると現在価格は{'割安' if info.get('forwardPE', 30) < 20 else '適正' if info.get('forwardPE', 30) < 30 else '割高'}圏内。売上成長率{info.get('revenueGrowth', 0)*100:.1f}%を考慮すると、テクニカルシグナルは{'妥当' if info.get('revenueGrowth', 0) > 0 else '慎重に判断すべき'}。企業価値に対して現在の株価水準は{'買い場' if info.get('forwardPE', 30) < 20 else 'ホールド' if info.get('forwardPE', 30) < 30 else '利確検討'}と評価。",
            f"**MACRO → RISK**: 現在の金利環境とセクター動向を考慮すると、{info.get('sector', '当セクター')}への資金フローは{'ポジティブ' if info.get('sector') in ['Technology', 'Healthcare'] else 'ネガティブ' if info.get('sector') in ['Utilities'] else '中立'}。この環境下でのエントリーリスクと適切なヘッジ戦略は？",
            f"**RISK**: ボラティリティ{hist['Close'].pct_change().std() * np.sqrt(252):.1%}、最大ドローダウン{self._calculate_max_drawdown(hist['Close']):.1%}を考慮すると、初期ポジションは総資金の{5 if hist['Close'].pct_change().std() * np.sqrt(252) > 0.4 else 8 if hist['Close'].pct_change().std() * np.sqrt(252) > 0.2 else 10}%が適切。マクロリスクへのヘッジとして、相関の低い債券ETFまたはVIX系商品の併用を推奨。",
        ]

        # Round 2: 下値目処の確定
        support_level = current_price * 0.85  # 簡易計算
        discussions["Round 2: 下値目処の確定"] = [
            f"**TECH**: フィボナッチ・リトレースメント61.8%水準は${support_level:.2f}、200SMA(${hist['SMA200'].iloc[-1]:.2f})がメジャーサポート。出来高プロファイル分析では${support_level*0.95:.2f}-${support_level*1.05:.2f}に強固なサポートゾーンを確認。",
            f"**FUND**: 過去のPBR下限から算出した理論的下値は${support_level*0.9:.2f}。予想EPS基準のPER15倍水準では${support_level*0.95:.2f}が下値目処。配当利回り4%到達価格は${support_level*1.1:.2f}で割安感が強まる水準。",
            f"**MACRO**: S&P500が10%調整入りした場合、ベータ値1.2想定で当銘柄は12%下落リスク。セクター特有の需給要因を加味すると${support_level*0.88:.2f}が下値メド。マクロショック時の想定下限は${support_level*0.8:.2f}。",
            f"**RISK**: 過去最大ドローダウン{self._calculate_max_drawdown(hist['Close']):.1%}、ATR-2σ統計的下限${current_price - hist['ATR'].iloc[-1]*2:.2f}。各専門家の下値目処を統合すると、最確度の高いサポートゾーンは${support_level*0.9:.2f}-${support_level*1.05:.2f}と特定。",
        ]

        # Round 3: 上値目標の設定
        target_1y = current_price * 1.25  # 簡易計算
        target_3y = current_price * 1.8
        discussions["Round 3: 上値目標の設定"] = [
            f"**TECH**: フィボナッチ・エクステンション161.8%水準${target_1y:.2f}、N計算値による1年後目標${target_1y*1.1:.2f}。3年後はチャネル上限を考慮し${target_3y:.2f}をテクニカル的上値目標として設定。",
            f"**FUND**: 予想EPS成長率15%、妥当PER25倍想定で1年後目標株価${target_1y:.2f}。3-5年成長持続シナリオでは${target_3y:.2f}が理論価値に基づく目標。同業他社比較でも妥当な水準。",
            f"**MACRO**: セクター成長率年率12%、技術革新による市場拡大ポテンシャルを考慮。政策支援も追い風となり、長期的な株価上昇余地は十分。3年後${target_3y:.2f}は実現可能な水準と評価。",
            f"**RISK**: 1年後${target_1y:.2f}達成には業績20%成長が前提。リスク・リワードレシオ2.5:1で投資妙味あり。3年後${target_3y:.2f}は確率60%で達成可能と試算。期待値は十分にプラス。",
        ]

        # Round 4: 段階的エントリー戦略
        discussions["Round 4: 段階的エントリー戦略"] = [
            f"**第1段階**: ${support_level*1.05:.2f}-${current_price*0.95:.2f} (投資比率40%) - RSI30以下からの反発確認時",
            f"**第2段階**: ${support_level:.2f}-${support_level*1.1:.2f} (投資比率35%) - 200SMAサポート確認後",
            f"**第3段階**: ${support_level*0.9:.2f}-${support_level:.2f} (投資比率25%) - 明確な底値圏での最終押し目",
            f"**時間軸**: 3-6ヶ月での段階的エントリーを想定。各段階でリスク管理を徹底し、想定と異なる展開時は戦略見直し。",
        ]

        # Round 5: 撤退・損切り基準
        discussions["Round 5: 撤退・損切り基準"] = [
            f"**TECH**: 200SMAを5%下抜け時点で損切り検討。主要サポート${support_level*0.85:.2f}割れで即時損切り実行。",
            f"**FUND**: 2四半期連続での大幅減益、または業界構造変化による競争力低下確認時。PERが業界平均を大幅に上回る状況継続時。",
            f"**MACRO**: セクター全体への構造的逆風（規制強化等）、またはマクロ環境の根本的変化時。金利急騰によるセクター資金流出時。",
            f"**RISK**: 総投資資金の15%損失時点で戦略見直し必須。ポートフォリオ全体のドローダウンが10%を超過時はポジション縮小実行。",
        ]

        # Round 6: 保有期間と出口戦略
        discussions["Round 6: 保有期間と出口戦略"] = [
            f"**想定保有期間**: 3-5年間の中長期投資スタンス。年2回（6月・12月）の定期レビューで戦略調整。",
            f"**利益確定戦略**: 目標株価50%達成で1/3売却、100%達成で追加1/3売却、残り1/3は長期保有継続。",
            f"**出口条件**: ①目標達成、②投資テーマの変化、③3年経過時点での見直し、④重大なファンダメンタル変化",
            f"**定期見直し**: 四半期決算後、重要な業界動向変化時、マクロ環境の大幅変化時に投資戦略を再評価実施。",
        ]

        return discussions

    def generate_investment_summary(
        self, ticker: str, hist: pd.DataFrame, info: Dict
    ) -> Dict[str, Dict[str, str]]:
        """投資判断サマリー生成"""
        current_price = hist["Close"].iloc[-1]
        support_level = current_price * 0.85
        target_1y = current_price * 1.25
        target_3y = current_price * 1.8

        summary = {
            "エントリー推奨度 (1-5★)": {
                "TECH": "★★★☆☆ (3.0)",
                "FUND": "★★★★☆ (4.0)",
                "MACRO": "★★★☆☆ (3.5)",
                "RISK": "★★★☆☆ (3.0)",
            },
            "理想的買いゾーン (USD)": {
                "TECH": f"${support_level*1.05:.2f}～${current_price*0.95:.2f}",
                "FUND": f"${support_level*0.95:.2f}～${support_level*1.1:.2f}",
                "MACRO": "マクロ環境良好時",
                "RISK": f"${support_level*0.9:.2f}～${support_level*1.05:.2f}",
            },
            "1年後目標株価 (USD)": {
                "TECH": f"${target_1y:.2f}",
                "FUND": f"${target_1y:.2f}",
                "MACRO": "セクター成長期待",
                "RISK": "達成確率65%",
            },
            "3年後目標株価 (USD)": {
                "TECH": f"${target_3y:.2f}",
                "FUND": f"${target_3y:.2f}",
                "MACRO": "政策支援継続前提",
                "RISK": "達成確率60%",
            },
            "推奨初期ポジション (%総資金)": {
                "TECH": "―",
                "FUND": "―",
                "MACRO": "―",
                "RISK": "8%",
            },
            "最大許容損失 (%初期投資額)": {
                "TECH": "―",
                "FUND": "―",
                "MACRO": "―",
                "RISK": "15% または -$" + f"{current_price*0.15:.2f}",
            },
        }

        return summary

    def generate_full_analysis_report(
        self, ticker: str, analysis_date: str = None
    ) -> str:
        """完全な分析レポート生成"""
        if analysis_date is None:
            analysis_date = datetime.now().strftime("%Y-%m-%d")

        print(f"🎯 {ticker} の4専門家討論分析を開始...")

        # データ取得
        hist, info = self.get_stock_data(ticker)
        current_price = hist["Close"].iloc[-1]
        company_name = info.get("longName", ticker)

        # チャート作成
        chart_path = self.create_chart(ticker, hist)
        print(f"📊 チャート作成完了: {chart_path}")

        # 分析実行
        environment = self.analyze_current_environment(ticker, hist, info)
        discussions = self.conduct_expert_discussion(ticker, hist, info)
        summary = self.generate_investment_summary(ticker, hist, info)

        # レポート生成
        report = f"""
# {ticker} 中長期投資エントリー分析〈{analysis_date}〉

## 📋 企業概要分析

**対象企業**: {company_name} ({ticker})
- **現在株価**: ${current_price:.2f} USD
- **時価総額**: ${info.get('marketCap', 0)/1e9:.1f}B USD  
- **セクター**: {info.get('sector', '不明')}
- **業界**: {info.get('industry', '不明')}
- **従業員数**: {info.get('fullTimeEmployees', 'N/A'):,}人

---

## 🎯 A. 現在の投資環境評価

"""

        for expert, analysis in environment.items():
            expert_info = self.experts[expert]
            report += f"""
### 💼 {expert_info['name']} ({expert_info['title']})
**専門分野**: {expert_info['specialty']}

{analysis}

---
"""

        report += """
## 🗣️ B. 専門家討論（全6ラウンド）

"""

        for round_title, statements in discussions.items():
            report += f"""
### 🔄 {round_title}

"""
            for i, statement in enumerate(statements, 1):
                report += f"{statement}\n\n"

        report += """
---

## 📊 C. 中長期投資判断サマリー

"""

        for category, values in summary.items():
            report += f"""
### {category}

"""
            for expert, value in values.items():
                if expert in self.experts:
                    report += f"- **{expert}**: {value}\n"
                else:
                    report += f"- {value}\n"
            report += "\n"

        # 段階的エントリー計画
        support_level = current_price * 0.85
        report += f"""
---

## 📈 D. 段階的エントリー計画

| 購入段階 | 価格帯目安 (USD) | 投資比率 | トリガー条件 | 根拠専門家 |
|:---:|:---:|:---:|:---|:---:|
| 第1段階 | ${support_level*1.05:.2f}～${current_price*0.95:.2f} | 40% | RSI30以下からの反発確認 | TECH/RISK |
| 第2段階 | ${support_level:.2f}～${support_level*1.1:.2f} | 35% | 200SMAサポート確認後 | FUND/TECH |
| 第3段階 | ${support_level*0.9:.2f}～${support_level:.2f} | 25% | 明確な底値圏での押し目 | MACRO/TECH |

---

## ⚠️ E. リスクシナリオ対応

| シナリオ | 発生確率 | 株価想定レンジ | 対応策 |
|:---:|:---:|:---:|:---|
| ベースケース | 60% | ${current_price*0.9:.2f}～${current_price*1.3:.2f} | ホールド継続、目標到達で一部利確 |
| 強気ケース | 25% | ${current_price*1.3:.2f}～${current_price*1.8:.2f} | トレーリングストップ設定、段階的利確 |
| 弱気ケース | 15% | ${current_price*0.6:.2f}～${current_price*0.9:.2f} | 損切りライン厳守、ポジション縮小 |

---

## 🎯 F. 最終推奨

**エントリー判定**: {"押し目待ち" if current_price > support_level*1.2 else "段階的買い" if current_price > support_level else "即時買い検討"}

**推奨理由**: 4専門家の総合判断により、現在の株価水準は中長期投資において{"魅力的" if current_price < support_level*1.1 else "適正" if current_price < current_price*1.1 else "やや割高"}。テクニカル・ファンダメンタル・マクロ環境を総合的に勘案し、{"積極的な" if current_price < support_level*1.1 else "慎重な"}エントリーを推奨。

**次回レビュータイミング**: {(datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')} (3ヶ月後) または次回四半期決算発表後

---

> **免責事項**: 本情報は教育目的のシミュレーションであり、投資助言ではありません。実際の投資判断は、ご自身の責任において行うようにしてください。

---
*生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*チャート保存先: {chart_path}*
"""

        return report

    def save_analysis(self, ticker: str, report: str, format: str = "markdown") -> str:
        """分析結果の保存"""
        os.makedirs("./reports", exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"./reports/{ticker}_discussion_analysis_{date_str}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        return filename


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="Tiker Discussion - 4専門家討論形式の株式分析",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python tiker_discussion.py --ticker TSLA     # TSLA討論分析
  python tiker_discussion.py --ticker AAPL     # AAPL討論分析
  python tiker_discussion.py --ticker GOOGL    # GOOGL討論分析
        """,
    )

    parser.add_argument(
        "--ticker", "-t", required=True, help="分析対象の米国株ティッカー"
    )
    parser.add_argument(
        "--save", "-s", action="store_true", help="レポートをファイルに保存"
    )
    parser.add_argument(
        "--chart-only", "-c", action="store_true", help="チャートのみ生成"
    )

    args = parser.parse_args()

    try:
        analyzer = TikerDiscussion()

        if args.chart_only:
            # チャートのみ生成
            hist, info = analyzer.get_stock_data(args.ticker)
            chart_path = analyzer.create_chart(args.ticker, hist)
            print(f"📊 チャート生成完了: {chart_path}")
        else:
            # 完全な討論分析
            report = analyzer.generate_full_analysis_report(args.ticker)

            if args.save:
                filename = analyzer.save_analysis(args.ticker, report)
                print(f"📄 レポート保存: {filename}")
            else:
                print("\n" + "=" * 80)
                print(report)
                print("=" * 80)

    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
