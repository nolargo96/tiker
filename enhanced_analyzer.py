"""
Enhanced Stock Analyzer - 包括的投資分析システム
GOOGレポートの分析手法を統合した新しい分析フレームワーク
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import yaml
import json
import logging
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
class ESGScore:
    """ESGスコアデータ"""

    total_esg: Optional[float] = None
    environment_score: Optional[float] = None
    social_score: Optional[float] = None
    governance_score: Optional[float] = None
    percentile: Optional[float] = None
    final_score: float = 3.0


@dataclass
class ThemeScore:
    """投資テーマスコア"""

    ai_score: float = 0.0
    cloud_score: float = 0.0
    clean_energy_score: float = 0.0
    space_score: float = 0.0
    robotics_score: float = 0.0
    total_score: float = 0.0


@dataclass
class CatalystScore:
    """カタリストスコア"""

    news_sentiment: float = 3.0
    earnings_surprise: float = 3.0
    analyst_revisions: float = 3.0
    total_score: float = 3.0


@dataclass
class ManagementScore:
    """経営陣スコア"""

    insider_trading: float = 3.0
    leadership_stability: float = 3.0
    total_score: float = 3.0


@dataclass
class ValuationMetrics:
    """バリュエーション指標"""

    current_price: float = 0.0
    target_price_basic: float = 0.0
    target_price_bull: float = 0.0
    target_price_bear: float = 0.0
    dcf_value: float = 0.0
    pe_ratio: float = 0.0
    peg_ratio: float = 0.0
    pbr: float = 0.0
    ev_sales: float = 0.0


@dataclass
class FinancialMetrics:
    """財務指標"""

    revenue_growth: float = 0.0
    eps_growth: float = 0.0
    gross_margin: float = 0.0
    operating_margin: float = 0.0
    net_margin: float = 0.0
    roe: float = 0.0
    roa: float = 0.0
    debt_to_equity: float = 0.0
    current_ratio: float = 0.0
    free_cash_flow: float = 0.0


@dataclass
class RiskAssessment:
    """リスク評価"""

    regulatory_risk: Tuple[str, str, str] = ("中", "中", "規制強化のリスク")
    competitive_risk: Tuple[str, str, str] = ("中", "中", "競合他社の脅威")
    technology_risk: Tuple[str, str, str] = ("低", "中", "技術革新への対応")
    macro_risk: Tuple[str, str, str] = ("中", "中", "マクロ経済の影響")
    valuation_risk: Tuple[str, str, str] = ("低", "中", "バリュエーション過熱")


@dataclass
class ComprehensiveAnalysis:
    """包括的分析結果"""

    ticker: str
    analysis_date: str

    # 基本情報
    company_name: str = ""
    current_price: float = 0.0
    market_cap: str = ""

    # 既存の4専門家スコア
    tech_score: float = 3.0
    fund_score: float = 3.0
    macro_score: float = 3.0
    risk_score: float = 3.0

    # 新しい分析要素
    esg_score: ESGScore = None
    theme_score: ThemeScore = None
    catalyst_score: CatalystScore = None
    management_score: ManagementScore = None

    # 財務・バリュエーション
    financial_metrics: FinancialMetrics = None
    valuation_metrics: ValuationMetrics = None

    # リスク評価
    risk_assessment: RiskAssessment = None

    # 総合判定
    overall_score: float = 3.0
    recommendation: InvestmentRecommendation = InvestmentRecommendation.HOLD

    def __post_init__(self):
        if self.esg_score is None:
            self.esg_score = ESGScore()
        if self.theme_score is None:
            self.theme_score = ThemeScore()
        if self.catalyst_score is None:
            self.catalyst_score = CatalystScore()
        if self.management_score is None:
            self.management_score = ManagementScore()
        if self.financial_metrics is None:
            self.financial_metrics = FinancialMetrics()
        if self.valuation_metrics is None:
            self.valuation_metrics = ValuationMetrics()
        if self.risk_assessment is None:
            self.risk_assessment = RiskAssessment()


class EnhancedStockAnalyzer:
    """包括的投資分析システム"""

    def __init__(self, config_path: str = "config.yaml"):
        """初期化"""
        self.config = self._load_config(config_path)
        self.investment_themes = self._load_investment_themes()
        self.logger = self._setup_logging()

    def _load_config(self, config_path: str) -> Dict:
        """設定ファイルの読み込み"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # デフォルト設定を返す
            return {
                "expert_weights": {
                    "TECH": 1.0,
                    "FUND": 1.5,
                    "MACRO": 1.0,
                    "RISK": 1.2,
                    "ESG": 0.8,
                    "THEME": 1.0,
                    "CATALYST": 0.7,
                    "MANAGEMENT": 0.8,
                }
            }

    def _load_investment_themes(self) -> Dict[str, List[str]]:
        """投資テーマのキーワード定義"""
        return {
            "AI": [
                "artificial intelligence",
                "machine learning",
                "neural network",
                "deep learning",
                "AI",
            ],
            "Cloud": ["cloud computing", "saas", "iaas", "paas", "cloud services"],
            "CleanEnergy": [
                "solar",
                "wind",
                "renewable",
                "clean energy",
                "battery",
                "sustainable",
            ],
            "Space": ["space", "satellite", "rocket", "aerospace", "launch"],
            "Robotics": ["robotics", "automation", "autonomous", "robot"],
        }

    def _setup_logging(self) -> logging.Logger:
        """ログ設定"""
        logger = logging.getLogger("EnhancedStockAnalyzer")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def get_esg_score(self, ticker_symbol: str) -> ESGScore:
        """ESGスコアの取得と評価"""
        try:
            ticker = yf.Ticker(ticker_symbol)
            sustainability = ticker.sustainability

            if sustainability is not None and not sustainability.empty:
                esg_data = sustainability["Value"].to_dict()

                total_esg = esg_data.get("totalEsg")
                percentile = esg_data.get("percentile", 50)

                # ESGスコアの算出（低いほど良い）
                if total_esg is not None:
                    if total_esg <= 15 and percentile <= 20:
                        final_score = 5.0
                    elif total_esg <= 25 and percentile <= 40:
                        final_score = 4.0
                    elif total_esg <= 35 and percentile <= 60:
                        final_score = 3.0
                    elif total_esg <= 45 and percentile <= 80:
                        final_score = 2.0
                    else:
                        final_score = 1.0
                else:
                    final_score = 3.0

                return ESGScore(
                    total_esg=total_esg,
                    environment_score=esg_data.get("environmentScore"),
                    social_score=esg_data.get("socialScore"),
                    governance_score=esg_data.get("governanceScore"),
                    percentile=percentile,
                    final_score=final_score,
                )

        except Exception as e:
            self.logger.warning(f"ESGデータの取得に失敗: {ticker_symbol} - {e}")

        return ESGScore(final_score=3.0)

    def get_theme_score(self, ticker_symbol: str) -> ThemeScore:
        """投資テーマスコアの算出"""
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info

            business_summary = info.get("longBusinessSummary", "").lower()

            if not business_summary:
                return ThemeScore()

            # 各テーマのスコア算出
            ai_score = min(
                5.0,
                sum(business_summary.count(kw) for kw in self.investment_themes["AI"]),
            )
            cloud_score = min(
                5.0,
                sum(
                    business_summary.count(kw) for kw in self.investment_themes["Cloud"]
                ),
            )
            clean_energy_score = min(
                5.0,
                sum(
                    business_summary.count(kw)
                    for kw in self.investment_themes["CleanEnergy"]
                ),
            )
            space_score = min(
                5.0,
                sum(
                    business_summary.count(kw) for kw in self.investment_themes["Space"]
                ),
            )
            robotics_score = min(
                5.0,
                sum(
                    business_summary.count(kw)
                    for kw in self.investment_themes["Robotics"]
                ),
            )

            # 総合スコア（最高スコアを採用）
            total_score = max(
                ai_score, cloud_score, clean_energy_score, space_score, robotics_score
            )

            return ThemeScore(
                ai_score=ai_score,
                cloud_score=cloud_score,
                clean_energy_score=clean_energy_score,
                space_score=space_score,
                robotics_score=robotics_score,
                total_score=total_score,
            )

        except Exception as e:
            self.logger.warning(f"テーマスコアの算出に失敗: {ticker_symbol} - {e}")

        return ThemeScore()

    def get_catalyst_score(self, ticker_symbol: str) -> CatalystScore:
        """カタリストスコアの算出"""
        try:
            ticker = yf.Ticker(ticker_symbol)
            news = ticker.news

            if not news:
                return CatalystScore()

            # 簡易的なセンチメント分析
            positive_words = [
                "growth",
                "profit",
                "beat",
                "strong",
                "up",
                "gain",
                "bullish",
            ]
            negative_words = [
                "loss",
                "down",
                "weak",
                "miss",
                "bearish",
                "decline",
                "fall",
            ]

            sentiment_scores = []
            for item in news[:10]:  # 最新10件のニュース
                title = item.get("title", "").lower()
                positive_count = sum(title.count(word) for word in positive_words)
                negative_count = sum(title.count(word) for word in negative_words)

                if positive_count > negative_count:
                    sentiment_scores.append(4.0)
                elif negative_count > positive_count:
                    sentiment_scores.append(2.0)
                else:
                    sentiment_scores.append(3.0)

            news_sentiment = np.mean(sentiment_scores) if sentiment_scores else 3.0

            # 決算サプライズ（簡易版）
            earnings_surprise = 3.0  # 実装予定

            # アナリスト評価変更（簡易版）
            analyst_revisions = 3.0  # 実装予定

            total_score = (news_sentiment + earnings_surprise + analyst_revisions) / 3

            return CatalystScore(
                news_sentiment=news_sentiment,
                earnings_surprise=earnings_surprise,
                analyst_revisions=analyst_revisions,
                total_score=total_score,
            )

        except Exception as e:
            self.logger.warning(f"カタリストスコアの算出に失敗: {ticker_symbol} - {e}")

        return CatalystScore()

    def get_management_score(self, ticker_symbol: str) -> ManagementScore:
        """経営陣スコアの算出"""
        try:
            ticker = yf.Ticker(ticker_symbol)

            # インサイダー取引の分析（簡易版）
            insider_trading_score = 3.0  # 実装予定

            # 経営陣の安定性（簡易版）
            leadership_stability = 3.0  # 実装予定

            total_score = (insider_trading_score + leadership_stability) / 2

            return ManagementScore(
                insider_trading=insider_trading_score,
                leadership_stability=leadership_stability,
                total_score=total_score,
            )

        except Exception as e:
            self.logger.warning(f"経営陣スコアの算出に失敗: {ticker_symbol} - {e}")

        return ManagementScore()

    def get_financial_metrics(self, ticker_symbol: str) -> FinancialMetrics:
        """財務指標の取得"""
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info

            return FinancialMetrics(
                revenue_growth=info.get("revenueGrowth", 0.0) * 100,
                eps_growth=info.get("earningsGrowth", 0.0) * 100,
                gross_margin=info.get("grossMargins", 0.0) * 100,
                operating_margin=info.get("operatingMargins", 0.0) * 100,
                net_margin=info.get("profitMargins", 0.0) * 100,
                roe=info.get("returnOnEquity", 0.0) * 100,
                roa=info.get("returnOnAssets", 0.0) * 100,
                debt_to_equity=info.get("debtToEquity", 0.0),
                current_ratio=info.get("currentRatio", 0.0),
                free_cash_flow=info.get("freeCashflow", 0.0),
            )

        except Exception as e:
            self.logger.warning(f"財務指標の取得に失敗: {ticker_symbol} - {e}")

        return FinancialMetrics()

    def get_valuation_metrics(self, ticker_symbol: str) -> ValuationMetrics:
        """バリュエーション指標の取得"""
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info

            current_price = info.get("currentPrice", 0.0)

            # 簡易的な目標株価算出
            target_price_basic = current_price * 1.15  # 15%アップサイド
            target_price_bull = current_price * 1.30  # 30%アップサイド
            target_price_bear = current_price * 0.85  # 15%ダウンサイド

            return ValuationMetrics(
                current_price=current_price,
                target_price_basic=target_price_basic,
                target_price_bull=target_price_bull,
                target_price_bear=target_price_bear,
                dcf_value=current_price * 1.10,  # 簡易DCF
                pe_ratio=info.get("forwardPE", 0.0),
                peg_ratio=info.get("pegRatio", 0.0),
                pbr=info.get("priceToBook", 0.0),
                ev_sales=info.get("enterpriseToRevenue", 0.0),
            )

        except Exception as e:
            self.logger.warning(
                f"バリュエーション指標の取得に失敗: {ticker_symbol} - {e}"
            )

        return ValuationMetrics()

    def analyze_stock(
        self, ticker_symbol: str, analysis_date: Optional[str] = None
    ) -> ComprehensiveAnalysis:
        """包括的株式分析の実行"""
        if analysis_date is None:
            analysis_date = datetime.now().strftime("%Y-%m-%d")

        self.logger.info(f"包括的分析開始: {ticker_symbol}")

        try:
            # 基本情報の取得
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info

            # 既存の4専門家スコア算出（簡易版）
            tech_score = 3.0  # 実装予定
            fund_score = 3.0  # 実装予定
            macro_score = 3.0  # 実装予定
            risk_score = 3.0  # 実装予定

            # 新しい分析要素の取得
            esg_score = self.get_esg_score(ticker_symbol)
            theme_score = self.get_theme_score(ticker_symbol)
            catalyst_score = self.get_catalyst_score(ticker_symbol)
            management_score = self.get_management_score(ticker_symbol)

            # 財務・バリュエーション指標
            financial_metrics = self.get_financial_metrics(ticker_symbol)
            valuation_metrics = self.get_valuation_metrics(ticker_symbol)

            # 総合スコアの算出
            weights = self.config.get(
                "expert_weights",
                {
                    "TECH": 1.0,
                    "FUND": 1.5,
                    "MACRO": 1.0,
                    "RISK": 1.2,
                    "ESG": 0.8,
                    "THEME": 1.0,
                    "CATALYST": 0.7,
                    "MANAGEMENT": 0.8,
                },
            )

            weighted_sum = (
                tech_score * weights.get("TECH", 1.0)
                + fund_score * weights.get("FUND", 1.5)
                + macro_score * weights.get("MACRO", 1.0)
                + risk_score * weights.get("RISK", 1.2)
                + esg_score.final_score * weights.get("ESG", 0.8)
                + theme_score.total_score * weights.get("THEME", 1.0)
                + catalyst_score.total_score * weights.get("CATALYST", 0.7)
                + management_score.total_score * weights.get("MANAGEMENT", 0.8)
            )

            total_weight = sum(weights.values())
            overall_score = weighted_sum / total_weight if total_weight > 0 else 3.0

            # 投資推奨の決定
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

            # 包括的分析結果の作成
            analysis = ComprehensiveAnalysis(
                ticker=ticker_symbol,
                analysis_date=analysis_date,
                company_name=info.get("longName", ticker_symbol),
                current_price=info.get("currentPrice", 0.0),
                market_cap=info.get("marketCap", 0),
                tech_score=tech_score,
                fund_score=fund_score,
                macro_score=macro_score,
                risk_score=risk_score,
                esg_score=esg_score,
                theme_score=theme_score,
                catalyst_score=catalyst_score,
                management_score=management_score,
                financial_metrics=financial_metrics,
                valuation_metrics=valuation_metrics,
                overall_score=overall_score,
                recommendation=recommendation,
            )

            self.logger.info(
                f"包括的分析完了: {ticker_symbol} - 総合スコア: {overall_score:.2f}"
            )
            return analysis

        except Exception as e:
            self.logger.error(f"包括的分析でエラー: {ticker_symbol} - {e}")
            raise

    def generate_investment_report(self, analysis: ComprehensiveAnalysis) -> str:
        """投資分析レポートの生成"""
        report = f"""
# 投資分析レポート: {analysis.company_name} ({analysis.ticker})

## 基本情報
- 分析日: {analysis.analysis_date}
- 現在株価: ${analysis.current_price:.2f}
- 時価総額: ${analysis.market_cap:,}
- 投資推奨: {analysis.recommendation.value}
- 総合スコア: {analysis.overall_score:.2f}/5.0

## 専門家スコア
- TECH (テクニカル): {analysis.tech_score:.1f}/5.0
- FUND (ファンダメンタル): {analysis.fund_score:.1f}/5.0
- MACRO (マクロ): {analysis.macro_score:.1f}/5.0
- RISK (リスク): {analysis.risk_score:.1f}/5.0

## 新しい分析要素
- ESG: {analysis.esg_score.final_score:.1f}/5.0
- 投資テーマ: {analysis.theme_score.total_score:.1f}/5.0
- カタリスト: {analysis.catalyst_score.total_score:.1f}/5.0
- 経営陣: {analysis.management_score.total_score:.1f}/5.0

## 目標株価
- 基本シナリオ: ${analysis.valuation_metrics.target_price_basic:.2f}
- 強気シナリオ: ${analysis.valuation_metrics.target_price_bull:.2f}
- 弱気シナリオ: ${analysis.valuation_metrics.target_price_bear:.2f}

## 主要財務指標
- 売上成長率: {analysis.financial_metrics.revenue_growth:.1f}%
- EPS成長率: {analysis.financial_metrics.eps_growth:.1f}%
- 粗利益率: {analysis.financial_metrics.gross_margin:.1f}%
- 営業利益率: {analysis.financial_metrics.operating_margin:.1f}%
- ROE: {analysis.financial_metrics.roe:.1f}%

## バリュエーション
- PER: {analysis.valuation_metrics.pe_ratio:.1f}倍
- PBR: {analysis.valuation_metrics.pbr:.1f}倍
- EV/Sales: {analysis.valuation_metrics.ev_sales:.1f}倍

---
*本レポートは教育目的のみに提供され、投資助言ではありません。*
"""
        return report


# 使用例
if __name__ == "__main__":
    analyzer = EnhancedStockAnalyzer()

    # GOOGの分析実行
    analysis = analyzer.analyze_stock("GOOG")

    # レポート生成
    report = analyzer.generate_investment_report(analysis)
    print(report)
