#!/usr/bin/env python3
"""
Tiker Unified - 統合株式投資分析システム
使いやすい単一ファイルでの包括的投資分析
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import yaml
import json
import logging
import argparse
import os
import sys
from dataclasses import dataclass, asdict
from enum import Enum


class InvestmentRecommendation(Enum):
    """投資推奨レベル"""

    STRONG_BUY = "強い買い"
    BUY = "買い"
    HOLD = "ホールド"
    SELL = "売り"
    STRONG_SELL = "強い売り"


@dataclass
class StockAnalysis:
    """株式分析結果"""

    ticker: str
    company_name: str = ""
    current_price: float = 0.0
    target_price: float = 0.0
    overall_score: float = 3.0
    recommendation: InvestmentRecommendation = InvestmentRecommendation.HOLD

    # 詳細スコア
    tech_score: float = 3.0
    fund_score: float = 3.0
    macro_score: float = 3.0
    risk_score: float = 3.0
    esg_score: float = 3.0
    theme_score: float = 3.0

    # 財務データ
    pe_ratio: float = 0.0
    revenue_growth: float = 0.0
    profit_margin: float = 0.0
    debt_ratio: float = 0.0

    # ポートフォリオ情報
    allocation: float = 0.0
    sector: str = ""
    themes: List[str] = None

    def __post_init__(self):
        if self.themes is None:
            self.themes = []


class TikerUnified:
    """統合株式投資分析システム"""

    def __init__(self, config_path: str = "config.yaml"):
        """初期化"""
        self.config = self._load_config(config_path)
        self.portfolio_config = self.config.get("portfolio", {})
        self.expert_weights = self.config.get("expert_weights", {})
        self.logger = self._setup_logging()

        # 投資テーマの定義
        self.investment_themes = {
            "EV": ["electric vehicle", "tesla", "battery", "ev", "electric"],
            "Solar": ["solar", "photovoltaic", "renewable", "clean energy"],
            "Space": ["space", "satellite", "rocket", "aerospace", "launch"],
            "Nuclear": ["nuclear", "reactor", "smr", "uranium"],
            "eVTOL": ["evtol", "air taxi", "urban air mobility", "aviation"],
            "AI": ["artificial intelligence", "machine learning", "ai", "neural"],
            "Cloud": ["cloud computing", "saas", "aws", "azure"],
        }

    def _load_config(self, config_path: str) -> Dict:
        """設定ファイルの読み込み"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(
                f"設定ファイル {config_path} が見つかりません。デフォルト設定を使用します。"
            )
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """デフォルト設定"""
        return {
            "portfolio": {
                "holdings": {
                    "TSLA": {"allocation": 20},
                    "FSLR": {"allocation": 20},
                    "RKLB": {"allocation": 10},
                    "ASTS": {"allocation": 10},
                    "OKLO": {"allocation": 10},
                    "JOBY": {"allocation": 10},
                    "OII": {"allocation": 10},
                    "LUNR": {"allocation": 5},
                    "RDW": {"allocation": 5},
                }
            },
            "expert_weights": {
                "TECH": 1.0,
                "FUND": 1.5,
                "MACRO": 1.0,
                "RISK": 1.2,
                "ESG": 0.8,
                "THEME": 1.0,
            },
        }

    def _setup_logging(self) -> logging.Logger:
        """ログ設定"""
        logger = logging.getLogger("TikerUnified")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def get_portfolio_tickers(self) -> List[str]:
        """ポートフォリオの銘柄リストを取得"""
        holdings = self.portfolio_config.get("holdings", {})
        return list(holdings.keys())

    def analyze_stock(self, ticker: str) -> StockAnalysis:
        """単一銘柄の分析"""
        self.logger.info(f"分析開始: {ticker}")

        try:
            # yfinanceでデータ取得
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")

            if hist.empty:
                raise ValueError(f"データが取得できませんでした: {ticker}")

            # 基本情報
            company_name = info.get("longName", ticker)
            current_price = info.get("currentPrice", hist["Close"].iloc[-1])

            # 財務指標
            pe_ratio = info.get("forwardPE", 0.0) or 0.0
            revenue_growth = (
                info.get("revenueGrowth", 0.0) * 100
                if info.get("revenueGrowth")
                else 0.0
            )
            profit_margin = (
                info.get("profitMargins", 0.0) * 100
                if info.get("profitMargins")
                else 0.0
            )
            debt_ratio = info.get("debtToEquity", 0.0) or 0.0

            # スコア計算
            tech_score = self._calculate_tech_score(hist, current_price)
            fund_score = self._calculate_fund_score(info)
            macro_score = self._calculate_macro_score(ticker, info)
            risk_score = self._calculate_risk_score(hist, debt_ratio)
            esg_score = self._calculate_esg_score(ticker)
            theme_score = self._calculate_theme_score(ticker, info)

            # 総合スコア
            scores = {
                "TECH": tech_score,
                "FUND": fund_score,
                "MACRO": macro_score,
                "RISK": risk_score,
                "ESG": esg_score,
                "THEME": theme_score,
            }

            weights = self.expert_weights
            weighted_sum = sum(scores[k] * weights.get(k, 1.0) for k in scores.keys())
            total_weight = sum(weights.get(k, 1.0) for k in scores.keys())
            overall_score = weighted_sum / total_weight if total_weight > 0 else 3.0

            # 投資推奨
            if overall_score >= 4.5:
                recommendation = InvestmentRecommendation.STRONG_BUY
            elif overall_score >= 3.5:
                recommendation = InvestmentRecommendation.BUY
            elif overall_score >= 2.5:
                recommendation = InvestmentRecommendation.HOLD
            elif overall_score >= 1.5:
                recommendation = InvestmentRecommendation.SELL
            else:
                recommendation = InvestmentRecommendation.STRONG_SELL

            # 目標株価（簡易計算）
            target_price = current_price * (1 + (overall_score - 3.0) * 0.15)

            # ポートフォリオ情報
            portfolio_info = self.portfolio_config.get("holdings", {}).get(ticker, {})
            allocation = portfolio_info.get("allocation", 0.0)
            sector = portfolio_info.get("sector", info.get("sector", ""))
            themes = portfolio_info.get("theme", [])

            analysis = StockAnalysis(
                ticker=ticker,
                company_name=company_name,
                current_price=current_price,
                target_price=target_price,
                overall_score=overall_score,
                recommendation=recommendation,
                tech_score=tech_score,
                fund_score=fund_score,
                macro_score=macro_score,
                risk_score=risk_score,
                esg_score=esg_score,
                theme_score=theme_score,
                pe_ratio=pe_ratio,
                revenue_growth=revenue_growth,
                profit_margin=profit_margin,
                debt_ratio=debt_ratio,
                allocation=allocation,
                sector=sector,
                themes=themes,
            )

            self.logger.info(f"分析完了: {ticker} - スコア: {overall_score:.2f}")
            return analysis

        except Exception as e:
            self.logger.error(f"分析エラー: {ticker} - {e}")
            return StockAnalysis(ticker=ticker, company_name=f"エラー: {ticker}")

    def _calculate_tech_score(self, hist: pd.DataFrame, current_price: float) -> float:
        """テクニカルスコア計算"""
        try:
            # 移動平均
            sma_20 = hist["Close"].rolling(20).mean().iloc[-1]
            sma_50 = hist["Close"].rolling(50).mean().iloc[-1]

            score = 3.0

            # 価格が移動平均より上にあるかチェック
            if current_price > sma_20:
                score += 0.5
            if current_price > sma_50:
                score += 0.5

            # トレンド方向
            if sma_20 > sma_50:
                score += 0.5

            # ボラティリティチェック
            volatility = hist["Close"].pct_change().std() * np.sqrt(252)
            if volatility < 0.3:  # 低ボラティリティは安定性の指標
                score += 0.5

            return min(5.0, max(1.0, score))

        except Exception:
            return 3.0

    def _calculate_fund_score(self, info: Dict) -> float:
        """ファンダメンタルスコア計算"""
        score = 3.0

        try:
            # PER評価
            pe = info.get("forwardPE", 0)
            if pe and 0 < pe < 20:
                score += 1.0
            elif pe and 20 <= pe < 30:
                score += 0.5
            elif pe and pe >= 30:
                score -= 0.5

            # 利益率評価
            profit_margin = info.get("profitMargins", 0)
            if profit_margin and profit_margin > 0.15:
                score += 1.0
            elif profit_margin and profit_margin > 0.05:
                score += 0.5

            # 成長率評価
            revenue_growth = info.get("revenueGrowth", 0)
            if revenue_growth and revenue_growth > 0.2:
                score += 1.0
            elif revenue_growth and revenue_growth > 0.1:
                score += 0.5

            return min(5.0, max(1.0, score))

        except Exception:
            return 3.0

    def _calculate_macro_score(self, ticker: str, info: Dict) -> float:
        """マクロスコア計算"""
        score = 3.0

        try:
            # セクター評価
            sector = info.get("sector", "")

            # 成長セクターに高評価
            growth_sectors = [
                "Technology",
                "Communication Services",
                "Consumer Discretionary",
            ]
            if sector in growth_sectors:
                score += 0.5

            # 市場キャップ評価
            market_cap = info.get("marketCap", 0)
            if market_cap > 100e9:  # 大型株
                score += 0.5
            elif market_cap > 10e9:  # 中型株
                score += 0.3

            return min(5.0, max(1.0, score))

        except Exception:
            return 3.0

    def _calculate_risk_score(self, hist: pd.DataFrame, debt_ratio: float) -> float:
        """リスクスコア計算（高いほど低リスク）"""
        score = 3.0

        try:
            # ボラティリティ評価
            volatility = hist["Close"].pct_change().std() * np.sqrt(252)
            if volatility < 0.2:
                score += 1.0
            elif volatility < 0.4:
                score += 0.5
            elif volatility > 0.6:
                score -= 1.0

            # 負債比率評価
            if debt_ratio < 0.3:
                score += 1.0
            elif debt_ratio < 0.6:
                score += 0.5
            elif debt_ratio > 1.0:
                score -= 1.0

            # 最大ドローダウン
            cumulative = (1 + hist["Close"].pct_change()).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = abs(drawdown.min())

            if max_drawdown < 0.2:
                score += 0.5
            elif max_drawdown > 0.5:
                score -= 0.5

            return min(5.0, max(1.0, score))

        except Exception:
            return 3.0

    def _calculate_esg_score(self, ticker: str) -> float:
        """ESGスコア計算"""
        try:
            stock = yf.Ticker(ticker)
            sustainability = stock.sustainability

            if sustainability is not None and not sustainability.empty:
                total_esg = (
                    sustainability.loc["totalEsg", "Value"]
                    if "totalEsg" in sustainability.index
                    else None
                )
                if total_esg:
                    # ESGスコアは低いほど良い
                    if total_esg <= 20:
                        return 5.0
                    elif total_esg <= 30:
                        return 4.0
                    elif total_esg <= 40:
                        return 3.0
                    else:
                        return 2.0
        except Exception:
            pass

        return 3.0

    def _calculate_theme_score(self, ticker: str, info: Dict) -> float:
        """投資テーマスコア計算"""
        try:
            business_summary = info.get("longBusinessSummary", "").lower()

            if not business_summary:
                return 3.0

            max_score = 0
            for theme, keywords in self.investment_themes.items():
                theme_score = sum(
                    business_summary.count(keyword) for keyword in keywords
                )
                max_score = max(max_score, min(5.0, theme_score))

            return max(1.0, max_score) if max_score > 0 else 3.0

        except Exception:
            return 3.0

    def analyze_portfolio(self) -> Dict[str, Any]:
        """ポートフォリオ全体の分析"""
        tickers = self.get_portfolio_tickers()

        if not tickers:
            raise ValueError("ポートフォリオが設定されていません")

        self.logger.info(f"ポートフォリオ分析開始: {len(tickers)}銘柄")

        results = {}
        portfolio_value = 0
        total_allocation = 0

        for ticker in tickers:
            analysis = self.analyze_stock(ticker)
            results[ticker] = analysis

            if analysis.allocation > 0:
                portfolio_value += analysis.current_price * analysis.allocation
                total_allocation += analysis.allocation

        # ポートフォリオサマリー
        avg_score = np.mean(
            [r.overall_score for r in results.values() if r.overall_score > 0]
        )

        # 推奨別集計
        recommendations = {}
        for analysis in results.values():
            rec = analysis.recommendation.value
            recommendations[rec] = recommendations.get(rec, 0) + 1

        # セクター別集計
        sectors = {}
        for analysis in results.values():
            if analysis.sector:
                sectors[analysis.sector] = (
                    sectors.get(analysis.sector, 0) + analysis.allocation
                )

        # テーマ別集計
        themes = {}
        for analysis in results.values():
            for theme in analysis.themes:
                themes[theme] = themes.get(theme, 0) + analysis.allocation

        summary = {
            "portfolio_name": self.portfolio_config.get("name", "ポートフォリオ"),
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "total_stocks": len(tickers),
            "total_allocation": total_allocation,
            "average_score": avg_score,
            "portfolio_value": portfolio_value,
            "recommendations": recommendations,
            "sector_allocation": sectors,
            "theme_allocation": themes,
            "individual_results": results,
        }

        self.logger.info(f"ポートフォリオ分析完了 - 平均スコア: {avg_score:.2f}")
        return summary

    def generate_portfolio_report(self, analysis_results: Dict[str, Any]) -> str:
        """ポートフォリオレポート生成"""
        results = analysis_results["individual_results"]

        report = f"""# {analysis_results['portfolio_name']} - 分析レポート

**分析日**: {analysis_results['analysis_date']}
**銘柄数**: {analysis_results['total_stocks']}
**ポートフォリオ平均スコア**: {analysis_results['average_score']:.2f}/5.0

## エグゼクティブサマリー

"""

        # 投資推奨サマリー
        recommendations = analysis_results["recommendations"]
        if recommendations:
            report += "### 投資推奨分布\n"
            for rec, count in recommendations.items():
                report += f"- **{rec}**: {count}銘柄\n"
            report += "\n"

        # 個別銘柄詳細
        report += "## 銘柄別分析結果\n\n"
        report += "| ティッカー | 企業名 | 配分 | 現在価格 | 目標価格 | 総合スコア | 推奨 | セクター |\n"
        report += "|:---|:---|---:|---:|---:|---:|:---|:---|\n"

        # スコア順でソート
        sorted_results = sorted(
            results.values(), key=lambda x: x.overall_score, reverse=True
        )

        for analysis in sorted_results:
            report += f"| {analysis.ticker} | {analysis.company_name} | {analysis.allocation}% | "
            report += f"${analysis.current_price:.2f} | ${analysis.target_price:.2f} | "
            report += f"{analysis.overall_score:.2f} | {analysis.recommendation.value} | {analysis.sector} |\n"

        # 詳細分析
        report += "\n## 詳細分析\n\n"

        # 高評価銘柄
        top_stocks = [a for a in sorted_results if a.overall_score >= 4.0]
        if top_stocks:
            report += f"### 🌟 高評価銘柄 (スコア4.0以上)\n"
            for stock in top_stocks:
                report += f"- **{stock.ticker}** ({stock.overall_score:.2f}): {stock.company_name}\n"
                report += f"  - 推奨: {stock.recommendation.value}\n"
                report += f"  - 目標価格: ${stock.target_price:.2f} (現在: ${stock.current_price:.2f})\n\n"

        # 注意銘柄
        warning_stocks = [a for a in sorted_results if a.overall_score < 2.5]
        if warning_stocks:
            report += f"### ⚠️ 注意銘柄 (スコア2.5未満)\n"
            for stock in warning_stocks:
                report += f"- **{stock.ticker}** ({stock.overall_score:.2f}): {stock.company_name}\n"
                report += f"  - 推奨: {stock.recommendation.value}\n"
                report += f"  - 課題: リスク要因の詳細確認が必要\n\n"

        # セクター分析
        sectors = analysis_results.get("sector_allocation", {})
        if sectors:
            report += "### セクター配分\n"
            for sector, allocation in sorted(
                sectors.items(), key=lambda x: x[1], reverse=True
            ):
                report += f"- {sector}: {allocation}%\n"
            report += "\n"

        # テーマ分析
        themes = analysis_results.get("theme_allocation", {})
        if themes:
            report += "### 投資テーマ配分\n"
            for theme, allocation in sorted(
                themes.items(), key=lambda x: x[1], reverse=True
            ):
                report += f"- {theme}: {allocation}%\n"
            report += "\n"

        # リスク評価
        report += "## リスク評価\n\n"
        avg_risk = np.mean([r.risk_score for r in results.values() if r.risk_score > 0])
        report += f"ポートフォリオ平均リスクスコア: {avg_risk:.2f}/5.0\n\n"

        if avg_risk < 2.5:
            report += "⚠️ **高リスク**: ポジションサイズの見直しを推奨\n"
        elif avg_risk > 4.0:
            report += "✅ **低リスク**: 安定したポートフォリオ構成\n"
        else:
            report += "📊 **中程度リスク**: バランスの取れたリスク水準\n"

        report += (
            f"\n---\n*本レポートは教育目的のみに提供され、投資助言ではありません。*\n"
        )

        return report

    def save_results(
        self, analysis_results: Dict[str, Any], format: str = "markdown"
    ) -> str:
        """結果を保存"""
        os.makedirs("./reports", exist_ok=True)

        date_str = analysis_results["analysis_date"]

        if format == "markdown":
            report = self.generate_portfolio_report(analysis_results)
            filename = f"./reports/portfolio_analysis_{date_str}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)

        elif format == "json":
            # DataClassをJSONシリアライズ可能に変換
            json_data = {}
            for key, value in analysis_results.items():
                if key == "individual_results":
                    json_data[key] = {
                        ticker: asdict(analysis) for ticker, analysis in value.items()
                    }
                else:
                    json_data[key] = value

            filename = f"./reports/portfolio_analysis_{date_str}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)

        return filename


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="Tiker Unified - 統合株式投資分析システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python tiker_unified.py                    # ポートフォリオ全体分析
  python tiker_unified.py --ticker TSLA      # 単一銘柄分析
  python tiker_unified.py --portfolio        # ポートフォリオ分析（詳細）
  python tiker_unified.py --json             # JSON形式で保存
        """,
    )

    parser.add_argument("--ticker", "-t", help="単一銘柄の分析 (例: TSLA)")
    parser.add_argument(
        "--portfolio", "-p", action="store_true", help="ポートフォリオ全体分析"
    )
    parser.add_argument("--json", "-j", action="store_true", help="JSON形式で保存")
    parser.add_argument(
        "--config", "-c", default="config.yaml", help="設定ファイルパス"
    )

    args = parser.parse_args()

    try:
        analyzer = TikerUnified(args.config)

        if args.ticker:
            # 単一銘柄分析
            print(f"🎯 {args.ticker} 分析開始...")
            analysis = analyzer.analyze_stock(args.ticker)

            print(f"\n📊 分析結果: {analysis.ticker}")
            print(f"企業名: {analysis.company_name}")
            print(f"現在価格: ${analysis.current_price:.2f}")
            print(f"目標価格: ${analysis.target_price:.2f}")
            print(f"総合スコア: {analysis.overall_score:.2f}/5.0")
            print(f"投資推奨: {analysis.recommendation.value}")
            print(f"セクター: {analysis.sector}")

        else:
            # ポートフォリオ分析
            print("📈 ポートフォリオ分析開始...")
            portfolio_results = analyzer.analyze_portfolio()

            print(f"\n🎉 {portfolio_results['portfolio_name']} 分析完了")
            print(f"銘柄数: {portfolio_results['total_stocks']}")
            print(f"平均スコア: {portfolio_results['average_score']:.2f}/5.0")

            # 推奨サマリー表示
            print(f"\n投資推奨分布:")
            for rec, count in portfolio_results["recommendations"].items():
                print(f"  {rec}: {count}銘柄")

            # 上位・下位銘柄表示
            results = portfolio_results["individual_results"]
            sorted_results = sorted(
                results.values(), key=lambda x: x.overall_score, reverse=True
            )

            print(f"\n🌟 トップ3銘柄:")
            for stock in sorted_results[:3]:
                print(
                    f"  {stock.ticker}: {stock.overall_score:.2f} ({stock.recommendation.value})"
                )

            if len(sorted_results) > 3:
                print(f"\n⚠️ 要注意銘柄:")
                for stock in sorted_results[-2:]:
                    print(
                        f"  {stock.ticker}: {stock.overall_score:.2f} ({stock.recommendation.value})"
                    )

            # レポート保存
            format_type = "json" if args.json else "markdown"
            filename = analyzer.save_results(portfolio_results, format_type)
            print(f"\n📄 レポート保存: {filename}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
