"""
Competitor Analysis Module for Tiker Stock Analyzer
競合他社分析機能 - ポートフォリオ銘柄の同業リーダー・競合企業との比較

このモジュールは、tikerプロジェクトの競合分析機能を提供します：
- 9銘柄の同業リーダー・競合企業の定義
- 相対的パフォーマンス比較
- 競合比較レポートの生成
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
from src.analysis.stock_analyzer_lib import StockDataManager, TechnicalIndicators, ConfigManager
from src.portfolio.financial_comparison_extension import FinancialComparison

warnings.filterwarnings("ignore")


class CompetitorAnalysis:
    """競合他社分析クラス"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        競合分析クラスの初期化

        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config = ConfigManager(config_path)
        self.data_manager = StockDataManager(self.config)
        self.financial_comparison = FinancialComparison()

        # 9銘柄の競合企業・同業リーダーマッピング
        self.competitor_mapping = {
            "TSLA": {
                "name": "テスラ",
                "sector": "EV・自動運転",
                "competitors": ["NIO", "RIVN", "LCID", "GM", "F"],
                "leader": "TSLA",  # 自身がリーダー
                "descriptions": {
                    "NIO": "中国EV大手、バッテリー交換技術",
                    "RIVN": "電動トラック・バン特化",
                    "LCID": "高級EVセダン、長距離性能",
                    "GM": "伝統的自動車メーカー、EV転換中",
                    "F": "フォード、F-150 Lightning等",
                },
            },
            "FSLR": {
                "name": "ファーストソーラー",
                "sector": "太陽光発電",
                "competitors": ["ENPH", "SEDG", "SPWR", "RUN"],
                "leader": "ENPH",  # エンフェーズがマイクロインバーター市場リーダー
                "descriptions": {
                    "ENPH": "マイクロインバーター市場リーダー",
                    "SEDG": "パワーオプティマイザー技術",
                    "SPWR": "住宅用太陽光システム",
                    "RUN": "太陽光発電リース大手",
                },
            },
            "RKLB": {
                "name": "ロケットラボ",
                "sector": "小型ロケット・宇宙",
                "competitors": ["ASTR", "SPCE", "IRDM"],
                "leader": "RKLB",  # 小型ロケット市場リーダー
                "descriptions": {
                    "ASTR": "小型ロケット新興企業",
                    "SPCE": "宇宙観光・Virgin Galactic",
                    "IRDM": "衛星通信・イリジウム",
                },
            },
            "ASTS": {
                "name": "AST SpaceMobile",
                "sector": "衛星通信",
                "competitors": ["IRDM", "VSAT", "GSAT"],
                "leader": "IRDM",  # イリジウムが衛星通信リーダー
                "descriptions": {
                    "IRDM": "衛星通信業界リーダー",
                    "VSAT": "衛星ブロードバンド",
                    "GSAT": "衛星通信サービス",
                },
            },
            "OKLO": {
                "name": "オークロ",
                "sector": "小型原子炉（SMR）",
                "competitors": ["NNE", "BWXT", "UUUU", "CCJ"],
                "leader": "NNE",  # 原子力大手
                "descriptions": {
                    "NNE": "原子力エンジニアリング大手",
                    "BWXT": "原子力機器・燃料製造",
                    "UUUU": "ウラン採掘・精製",
                    "CCJ": "カナダ・ウラン生産最大手",
                },
            },
            "JOBY": {
                "name": "ジョビー・アビエーション",
                "sector": "eVTOL・都市航空",
                "competitors": ["LILM", "ACHR", "EVEX"],
                "leader": "JOBY",  # eVTOL市場先駆者
                "descriptions": {
                    "LILM": "ドイツeVTOL企業",
                    "ACHR": "エアチャー・電動航空機",
                    "EVEX": "イーブエックス・eVTOL",
                },
            },
            "OII": {
                "name": "オーシャニアリング",
                "sector": "海洋エンジニアリング",
                "competitors": ["SLB", "TDW", "SUBSF"],
                "leader": "SLB",  # シュルンベルジェが油田サービス最大手
                "descriptions": {
                    "SLB": "油田サービス世界最大手",
                    "TDW": "海底設備・ROVサービス",
                    "SUBSF": "海底システム・FMC",
                },
            },
            "LUNR": {
                "name": "インテュイティブ・マシーンズ",
                "sector": "月面探査",
                "competitors": ["RKLB", "ASTR", "SPCE"],
                "leader": "RKLB",  # 宇宙輸送でロケットラボがリーダー
                "descriptions": {
                    "RKLB": "小型ロケット・宇宙輸送",
                    "ASTR": "小型ロケット新興",
                    "SPCE": "宇宙観光・技術",
                },
            },
            "RDW": {
                "name": "レッドワイヤー",
                "sector": "宇宙製造",
                "competitors": ["RKLB", "MAXR", "SPCE"],
                "leader": "MAXR",  # 宇宙インフラでマクサー・リーダー
                "descriptions": {
                    "RKLB": "宇宙インフラ・衛星",
                    "MAXR": "宇宙技術・衛星製造",
                    "SPCE": "宇宙技術・観光",
                },
            },
        }

    def get_competitor_data(
        self, ticker: str, period_days: int = 365
    ) -> Dict[str, Any]:
        """
        指定銘柄の競合企業データを取得

        Args:
            ticker (str): 対象銘柄
            period_days (int): 分析期間（日数）

        Returns:
            Dict[str, Any]: 競合データ
        """
        if ticker not in self.competitor_mapping:
            return {"error": f"{ticker} の競合企業データが見つかりません"}

        competitor_info = self.competitor_mapping[ticker]
        competitors = competitor_info["competitors"]

        # 対象銘柄と競合企業のデータを取得
        all_tickers = [ticker] + competitors
        results = {
            "target_ticker": ticker,
            "target_name": competitor_info["name"],
            "sector": competitor_info["sector"],
            "leader": competitor_info["leader"],
            "data": {},
            "performance_comparison": {},
            "risk_metrics": {},
        }

        for symbol in all_tickers:
            success, df, message = self.data_manager.fetch_stock_data(
                symbol, period_days
            )

            if success and not df.empty:
                # テクニカル指標追加
                df = self.data_manager.add_technical_indicators(df)

                # パフォーマンス指標計算
                latest_price = df["Close"].iloc[-1]
                start_price = df["Close"].iloc[0]
                total_return = (latest_price - start_price) / start_price * 100

                volatility = df["Close"].pct_change().std() * np.sqrt(252) * 100

                # 最大ドローダウン
                rolling_max = df["Close"].expanding().max()
                drawdown = (df["Close"] - rolling_max) / rolling_max * 100
                max_drawdown = drawdown.min()

                results["data"][symbol] = {
                    "name": (
                        competitor_info["descriptions"].get(symbol, symbol)
                        if symbol != ticker
                        else competitor_info["name"]
                    ),
                    "latest_price": latest_price,
                    "total_return_pct": total_return,
                    "volatility_pct": volatility,
                    "max_drawdown_pct": max_drawdown,
                    "data_points": len(df),
                    "latest_rsi": df["RSI"].iloc[-1] if "RSI" in df.columns else None,
                    "price_vs_ema20": (
                        (latest_price - df["EMA20"].iloc[-1])
                        / df["EMA20"].iloc[-1]
                        * 100
                        if "EMA20" in df.columns
                        else None
                    ),
                    "is_target": symbol == ticker,
                    "is_leader": symbol == competitor_info["leader"],
                }
            else:
                results["data"][symbol] = {
                    "error": message,
                    "is_target": symbol == ticker,
                    "is_leader": symbol == competitor_info["leader"],
                }

        # 相対パフォーマンス分析
        self._calculate_relative_performance(results)

        return results

    def _calculate_relative_performance(self, results: Dict[str, Any]) -> None:
        """相対パフォーマンス分析"""
        valid_data = {k: v for k, v in results["data"].items() if "error" not in v}

        if len(valid_data) < 2:
            return

        # リターンランキング
        returns = {k: v["total_return_pct"] for k, v in valid_data.items()}
        sorted_returns = sorted(returns.items(), key=lambda x: x[1], reverse=True)

        # リスク調整リターン（シャープレシオ風）
        risk_adjusted = {}
        for symbol, data in valid_data.items():
            if data["volatility_pct"] > 0:
                risk_adjusted[symbol] = (
                    data["total_return_pct"] / data["volatility_pct"]
                )

        results["performance_comparison"] = {
            "return_ranking": sorted_returns,
            "risk_adjusted_ranking": sorted(
                risk_adjusted.items(), key=lambda x: x[1], reverse=True
            ),
            "sector_average_return": np.mean(list(returns.values())),
            "sector_median_return": np.median(list(returns.values())),
            "target_vs_sector": returns.get(results["target_ticker"], 0)
            - np.mean(list(returns.values())),
        }

    def generate_competitor_report(self, ticker: str, period_days: int = 365) -> str:
        """
        競合比較レポートを生成

        Args:
            ticker (str): 対象銘柄
            period_days (int): 分析期間

        Returns:
            str: レポート文字列
        """
        data = self.get_competitor_data(ticker, period_days)

        if "error" in data:
            return f"エラー: {data['error']}"

        report = f"""
# {data['target_name']} ({ticker}) 競合他社分析レポート

## セクター概要
- **セクター**: {data['sector']}
- **業界リーダー**: {data['leader']}
- **分析期間**: {period_days}日間

## パフォーマンス比較

### リターンランキング
"""

        for i, (symbol, return_pct) in enumerate(
            data["performance_comparison"]["return_ranking"], 1
        ):
            symbol_data = data["data"][symbol]
            status = ""
            if symbol_data["is_target"]:
                status = " 🎯 [分析対象]"
            elif symbol_data["is_leader"]:
                status = " 👑 [業界リーダー]"

            report += f"{i}. **{symbol}** ({symbol_data['name']}): {return_pct:.1f}%{status}\n"

        report += f"""
### セクター統計
- **セクター平均リターン**: {data['performance_comparison']['sector_average_return']:.1f}%
- **セクター中央値**: {data['performance_comparison']['sector_median_return']:.1f}%
- **対セクター相対パフォーマンス**: {data['performance_comparison']['target_vs_sector']:.1f}%

## リスク分析
"""

        for symbol, symbol_data in data["data"].items():
            if "error" not in symbol_data:
                status = ""
                if symbol_data["is_target"]:
                    status = " 🎯"
                elif symbol_data["is_leader"]:
                    status = " 👑"

                report += f"- **{symbol}**{status}: ボラティリティ {symbol_data['volatility_pct']:.1f}%, 最大DD {symbol_data['max_drawdown_pct']:.1f}%\n"

        report += """
## 投資判断への示唆

### 相対的優位性
"""

        target_data = data["data"][ticker]
        if "error" not in target_data:
            rank = next(
                i
                for i, (s, _) in enumerate(
                    data["performance_comparison"]["return_ranking"], 1
                )
                if s == ticker
            )
            total_companies = len(data["performance_comparison"]["return_ranking"])

            if rank <= total_companies // 3:
                report += f"- {ticker}はセクター内で**上位**のパフォーマンス（{rank}/{total_companies}位）\n"
            elif rank <= total_companies * 2 // 3:
                report += f"- {ticker}はセクター内で**中位**のパフォーマンス（{rank}/{total_companies}位）\n"
            else:
                report += f"- {ticker}はセクター内で**下位**のパフォーマンス（{rank}/{total_companies}位）\n"

            if data["performance_comparison"]["target_vs_sector"] > 0:
                report += f"- セクター平均を{abs(data['performance_comparison']['target_vs_sector']):.1f}%**上回る**\n"
            else:
                report += f"- セクター平均を{abs(data['performance_comparison']['target_vs_sector']):.1f}%**下回る**\n"

        report += """
### リスク・リターン評価
"""

        if "error" not in target_data:
            risk_adjusted_rank = next(
                i
                for i, (s, _) in enumerate(
                    data["performance_comparison"]["risk_adjusted_ranking"], 1
                )
                if s == ticker
            )
            report += f"- リスク調整後リターンは{risk_adjusted_rank}/{len(data['performance_comparison']['risk_adjusted_ranking'])}位\n"

            if target_data["volatility_pct"] > 50:
                report += "- **高ボラティリティ**銘柄（年率50%超）\n"
            elif target_data["volatility_pct"] > 30:
                report += "- **中ボラティリティ**銘柄（年率30-50%）\n"
            else:
                report += "- **低ボラティリティ**銘柄（年率30%未満）\n"

        report += f"""
---
*分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*本レポートは教育目的のシミュレーションです。投資判断は自己責任で行ってください。*
"""

        return report

    def analyze_all_portfolio_competitors(
        self, period_days: int = 365
    ) -> Dict[str, str]:
        """
        ポートフォリオ全9銘柄の競合分析を実行

        Args:
            period_days (int): 分析期間

        Returns:
            Dict[str, str]: 各銘柄の競合分析レポート
        """
        portfolio_tickers = list(self.competitor_mapping.keys())
        results = {}

        for ticker in portfolio_tickers:
            print(f"分析中: {ticker}")
            results[ticker] = self.generate_competitor_report(ticker, period_days)

        return results

    def analyze_financial_performance(self, ticker: str) -> Dict[str, Any]:
        """
        財務パフォーマンス分析

        Args:
            ticker (str): 分析対象銘柄

        Returns:
            Dict[str, Any]: 財務分析結果
        """
        if ticker not in self.competitor_mapping:
            return {}

        competitor_info = self.competitor_mapping[ticker]
        competitors = competitor_info['competitors']

        # セクター内財務比較
        sector_analysis = self.financial_comparison.analyze_sector_performance(ticker, competitors)

        # 四半期トレンド
        quarterly_trends = self.financial_comparison.get_quarterly_trends(ticker)

        return {
            'ticker': ticker,
            'sector': competitor_info['sector'],
            'sector_analysis': sector_analysis,
            'quarterly_trends': quarterly_trends,
            'financial_report': self.financial_comparison.generate_financial_report(ticker, competitors)
        }

    def generate_enhanced_competitor_report(self, ticker: str, period_days: int = 365) -> str:
        """
        財務分析を含む拡張競合レポート生成

        Args:
            ticker (str): 分析対象銘柄
            period_days (int): 分析期間

        Returns:
            str: 拡張競合レポート
        """
        # 既存の競合分析レポート生成
        existing_report = self.generate_competitor_report(ticker, period_days)

        # 財務分析の追加
        financial_analysis = self.analyze_financial_performance(ticker)

        if financial_analysis and financial_analysis.get('financial_report'):
            financial_section = f"""

## 📊 財務パフォーマンス分析

{financial_analysis.get('financial_report', '')}

### 四半期売上トレンド
"""

            # 四半期データがある場合
            if 'quarterly_trends' in financial_analysis and financial_analysis['quarterly_trends']:
                trends = financial_analysis['quarterly_trends']
                if 'revenue_trend' in trends and trends['revenue_trend']:
                    for quarter, revenue in list(trends['revenue_trend'].items())[:4]:
                        financial_section += f"- {quarter}: ${revenue:.1f}B\n"

                if 'growth_rates' in trends and 'revenue_qoq' in trends['growth_rates']:
                    qoq = trends['growth_rates']['revenue_qoq']
                    financial_section += f"\n**四半期成長率 (QoQ)**: {qoq:+.1f}%\n"

            enhanced_report = existing_report + financial_section
            return enhanced_report

        return existing_report

    def get_portfolio_financial_comparison(self) -> pd.DataFrame:
        """
        ポートフォリオ9銘柄の財務指標比較

        Returns:
            pd.DataFrame: 財務指標比較表
        """
        portfolio_tickers = list(self.competitor_mapping.keys())
        return self.financial_comparison.compare_financial_metrics(portfolio_tickers)


def main():
    """メイン実行関数"""
    analyzer = CompetitorAnalysis()

    # 個別銘柄の競合分析例
    ticker = "TSLA"
    print(f"{ticker} の競合分析を実行中...")

    # 拡張レポート（財務分析含む）のテスト
    enhanced_report = analyzer.generate_enhanced_competitor_report(ticker, 365)
    print("=== 拡張競合レポート（財務分析含む） ===")
    print(enhanced_report)

    # ポートフォリオ財務比較テスト
    print("\n=== ポートフォリオ9銘柄 財務比較 ===")
    portfolio_comparison = analyzer.get_portfolio_financial_comparison()
    if not portfolio_comparison.empty:
        print(portfolio_comparison[['companyName', 'marketCap', 'forwardPE', 'returnOnEquity', 'profitMargins']].to_string())

    # 全銘柄の競合分析
    print("\n全9銘柄の競合分析を実行中...")
    all_reports = analyzer.analyze_all_portfolio_competitors(365)

    # レポートをファイルに保存
    import os

    reports_dir = "./reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    for ticker, report in all_reports.items():
        filename = f"{reports_dir}/competitor_analysis_{ticker}_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"レポート保存: {filename}")


if __name__ == "__main__":
    main()
