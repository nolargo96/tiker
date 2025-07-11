"""
Investment Report Generator - GOOG形式の投資サマリーレポート生成
"""

from enhanced_analyzer import ComprehensiveAnalysis, EnhancedStockAnalyzer
from datetime import datetime
import yfinance as yf
from typing import Dict, List, Tuple
import numpy as np


class InvestmentReportGenerator:
    """投資サマリーレポート生成器"""

    def __init__(self):
        self.analyzer = EnhancedStockAnalyzer()

    def format_currency(self, value: float, currency: str = "$") -> str:
        """通貨フォーマット"""
        if value >= 1e12:
            return f"{currency}{value/1e12:.1f}T"
        elif value >= 1e9:
            return f"{currency}{value/1e9:.1f}B"
        elif value >= 1e6:
            return f"{currency}{value/1e6:.1f}M"
        else:
            return f"{currency}{value:,.0f}"

    def _format_peg_ratio(self, peg_ratio: float) -> str:
        """PEGレシオのフォーマット"""
        if peg_ratio and peg_ratio > 0:
            return f"{peg_ratio:.2f}"
        else:
            return "N/A"

    def get_52_week_range(self, ticker_symbol: str) -> Tuple[float, float]:
        """52週高値・安値の取得"""
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            return info.get("fiftyTwoWeekHigh", 0.0), info.get("fiftyTwoWeekLow", 0.0)
        except:
            return 0.0, 0.0

    def generate_executive_summary(self, analysis: ComprehensiveAnalysis) -> str:
        """1. 投資サマリー (Executive Summary) セクション"""

        ticker = yf.Ticker(analysis.ticker)
        info = ticker.info

        # 52週高値・安値
        week_52_high, week_52_low = self.get_52_week_range(analysis.ticker)

        # アップサイド・ダウンサイドの計算
        current_price = analysis.valuation_metrics.current_price
        upside = (
            (analysis.valuation_metrics.target_price_bull - current_price)
            / current_price
        ) * 100
        downside = (
            (analysis.valuation_metrics.target_price_bear - current_price)
            / current_price
        ) * 100

        summary_table = f"""
## 1. 投資サマリー (Executive Summary)

### 1.1. 基本情報・主要指標

| 項目 | 詳細 |
|:---|:---|
| 企業名 / ティッカー | {analysis.company_name} ({analysis.ticker}) |
| 取引所 | {info.get('exchange', 'N/A')} |
| 現在株価 | ${current_price:.2f} ({analysis.analysis_date}終値) |
| 時価総額 | {self.format_currency(analysis.market_cap)} |
| 52週高値/安値 | ${week_52_high:.2f} / ${week_52_low:.2f} |
| 売上高成長率 (実績) | {analysis.financial_metrics.revenue_growth:.1f}% (前年比) |
| EPS成長率 (実績) | {analysis.financial_metrics.eps_growth:.1f}% (前年比) |
| 予想PER (Forward P/E) | {analysis.valuation_metrics.pe_ratio:.2f}倍 |
| PEGレシオ | {self._format_peg_ratio(analysis.valuation_metrics.peg_ratio)} |
| 投資判断 | {analysis.recommendation.value} |
| 目標株価 (12ヶ月) | 基本シナリオ: ${analysis.valuation_metrics.target_price_basic:.2f} |
| アップサイド/ダウンサイド | 強気: {upside:+.0f}% (${analysis.valuation_metrics.target_price_bull:.2f}) / 弱気: {downside:+.0f}% (${analysis.valuation_metrics.target_price_bear:.2f}) |
| 投資期間 | 長期 |

### 1.2. 要旨 (Executive Thesis)

{analysis.company_name}は、{self._generate_thesis(analysis)}
"""
        return summary_table

    def _generate_thesis(self, analysis: ComprehensiveAnalysis) -> str:
        """要旨の自動生成"""

        # 強みの特定
        strengths = []
        if analysis.tech_score >= 4.0:
            strengths.append("優れたテクニカル指標")
        if analysis.fund_score >= 4.0:
            strengths.append("堅調なファンダメンタルズ")
        if analysis.financial_metrics.operating_margin >= 20:
            strengths.append(
                f"高い営業利益率({analysis.financial_metrics.operating_margin:.1f}%)"
            )
        if analysis.theme_score.total_score >= 3.0:
            strengths.append("成長テーマとの強い関連性")
        if analysis.esg_score.final_score >= 4.0:
            strengths.append("優れたESG評価")

        # 成長要因の特定
        growth_drivers = []
        if analysis.theme_score.ai_score >= 3.0:
            growth_drivers.append("AI技術の活用")
        if analysis.theme_score.cloud_score >= 3.0:
            growth_drivers.append("クラウド事業の拡大")
        if analysis.theme_score.clean_energy_score >= 3.0:
            growth_drivers.append("クリーンエネルギー分野への参入")

        # リスク要因の特定
        risk_factors = []
        if analysis.valuation_metrics.pe_ratio > 30:
            risk_factors.append("高いバリュエーション")
        if analysis.risk_score <= 2.5:
            risk_factors.append("市場リスクの高まり")

        thesis = f"""主要事業での競争優位性を背景に、{', '.join(growth_drivers) if growth_drivers else '継続的な成長'}により長期的な価値創造を継続している企業である。
        
{', '.join(strengths) if strengths else '安定した業績'}を基盤として、総合スコア{analysis.overall_score:.1f}/5.0という評価を得ている。
        
現在のPER{analysis.valuation_metrics.pe_ratio:.1f}倍は過去の水準と比較して{"割安" if analysis.valuation_metrics.pe_ratio < 20 else "適正" if analysis.valuation_metrics.pe_ratio < 30 else "やや割高"}であり、
{f"主要なリスクは{', '.join(risk_factors)}だが、" if risk_factors else ""}持続的な成長性を考慮すれば投資魅力は高い。"""

        return thesis

    def generate_company_overview(self, analysis: ComprehensiveAnalysis) -> str:
        """2. 企業概要 (Company Overview) セクション"""

        ticker = yf.Ticker(analysis.ticker)
        info = ticker.info

        # 事業セグメント（簡易版）
        sector = info.get("sector", "不明")
        industry = info.get("industry", "不明")

        overview = f"""
## 2. 企業概要 (Company Overview)

### 2.1. 事業内容とセグメント別業績

{analysis.company_name}は{sector}セクターの{industry}業界に属し、以下の事業を展開している：

**主要事業領域：**
- セクター: {sector}
- 業界: {industry}
- 従業員数: {info.get('fullTimeEmployees', 'N/A'):,}人

### 2.2. 主要財務指標

| 指標 | 値 | 評価 |
|:---|:---|:---|
| 売上総利益率 | {analysis.financial_metrics.gross_margin:.1f}% | {"優秀" if analysis.financial_metrics.gross_margin > 50 else "良好" if analysis.financial_metrics.gross_margin > 30 else "要改善"} |
| 営業利益率 | {analysis.financial_metrics.operating_margin:.1f}% | {"優秀" if analysis.financial_metrics.operating_margin > 20 else "良好" if analysis.financial_metrics.operating_margin > 10 else "要改善"} |
| 純利益率 | {analysis.financial_metrics.net_margin:.1f}% | {"優秀" if analysis.financial_metrics.net_margin > 15 else "良好" if analysis.financial_metrics.net_margin > 5 else "要改善"} |
| ROE | {analysis.financial_metrics.roe:.1f}% | {"優秀" if analysis.financial_metrics.roe > 20 else "良好" if analysis.financial_metrics.roe > 10 else "要改善"} |
| 負債資本倍率 | {analysis.financial_metrics.debt_to_equity:.2f} | {"良好" if analysis.financial_metrics.debt_to_equity < 0.5 else "注意" if analysis.financial_metrics.debt_to_equity < 1.0 else "高リスク"} |

### 2.3. 競合優位性とビジネスモデル

**競争優位性の分析：**
- テクニカル評価: {analysis.tech_score:.1f}/5.0
- ファンダメンタル評価: {analysis.fund_score:.1f}/5.0
- 投資テーマ適合度: {analysis.theme_score.total_score:.1f}/5.0

{self._analyze_competitive_advantages(analysis)}
"""
        return overview

    def _analyze_competitive_advantages(self, analysis: ComprehensiveAnalysis) -> str:
        """競合優位性の分析"""
        advantages = []

        if analysis.financial_metrics.gross_margin > 50:
            advantages.append(
                "**高い粗利益率**: プラットフォーム・ビジネスモデルによる優位性"
            )

        if analysis.financial_metrics.roe > 20:
            advantages.append("**高いROE**: 効率的な資本活用による価値創造")

        if analysis.theme_score.ai_score >= 3.0:
            advantages.append("**AI技術**: 先進的な人工知能技術による差別化")

        if analysis.theme_score.cloud_score >= 3.0:
            advantages.append("**クラウド基盤**: スケーラブルなインフラによる競争力")

        if analysis.esg_score.final_score >= 4.0:
            advantages.append("**ESG対応**: 持続可能性への取り組みによる長期的価値創造")

        return (
            "\n".join([f"- {adv}" for adv in advantages])
            if advantages
            else "- 競合優位性の詳細分析が必要"
        )

    def generate_investment_thesis(self, analysis: ComprehensiveAnalysis) -> str:
        """4. 投資テーマとカタリスト セクション"""

        themes = []
        if analysis.theme_score.ai_score >= 2.0:
            themes.append(
                f"**AI革命**: スコア {analysis.theme_score.ai_score:.1f}/5.0 - 人工知能技術の活用による事業変革"
            )
        if analysis.theme_score.cloud_score >= 2.0:
            themes.append(
                f"**クラウド成長**: スコア {analysis.theme_score.cloud_score:.1f}/5.0 - デジタルトランスフォーメーション需要"
            )
        if analysis.theme_score.clean_energy_score >= 2.0:
            themes.append(
                f"**脱炭素**: スコア {analysis.theme_score.clean_energy_score:.1f}/5.0 - カーボンニュートラルへの取り組み"
            )
        if analysis.theme_score.space_score >= 2.0:
            themes.append(
                f"**宇宙産業**: スコア {analysis.theme_score.space_score:.1f}/5.0 - 宇宙関連事業の成長性"
            )

        catalysts = []
        if analysis.catalyst_score.news_sentiment > 3.5:
            catalysts.append("**ポジティブなニュースフロー**: 市場センチメントの改善")
        if analysis.financial_metrics.eps_growth > 15:
            catalysts.append(
                f"**EPS成長**: {analysis.financial_metrics.eps_growth:.1f}%の利益成長"
            )
        if analysis.valuation_metrics.pe_ratio < 20:
            catalysts.append("**バリュエーション魅力**: 適正な株価水準での投資機会")

        thesis_section = f"""
## 4. 投資テーマとカタリスト (Investment Thesis & Catalysts)

### 4.1. 投資テーマ (なぜこの会社に投資するのか)

{chr(10).join([f"{i+1}. {theme}" for i, theme in enumerate(themes)]) if themes else "投資テーマの詳細分析が必要です。"}

### 4.2. カタリスト (株価を動かす材料)

**短期 (～3ヶ月):**
- 四半期決算での業績発表
- セクター動向とマクロ環境の変化
- 主要製品・サービスの進展発表

**中期 (～1年):**
{chr(10).join([f"- {catalyst}" for catalyst in catalysts]) if catalysts else "- 中期カタリストの分析が必要"}

**長期 (1年超):**
- 事業構造の変革と新市場開拓
- 技術革新による競争優位性の確立
- ESG取り組みによる企業価値向上
"""
        return thesis_section

    def generate_risk_analysis(self, analysis: ComprehensiveAnalysis) -> str:
        """7. リスク要因 セクション"""

        # リスクレベルの評価
        risks = []

        if analysis.valuation_metrics.pe_ratio > 30:
            risks.append(
                (
                    "バリュエーション",
                    "高PER水準による調整リスク",
                    "高",
                    "大",
                    "業績成長による正当化が必要",
                )
            )

        if analysis.financial_metrics.debt_to_equity > 0.5:
            risks.append(
                ("財務", "高い負債水準", "中", "中", "借入金の削減と財務体質改善")
            )

        if analysis.risk_score <= 2.5:
            risks.append(
                (
                    "市場",
                    "高いボラティリティ",
                    "中",
                    "中",
                    "ポジションサイジングの最適化",
                )
            )

        if analysis.theme_score.total_score < 2.0:
            risks.append(
                ("事業", "成長テーマからの乖離", "中", "中", "新しい成長領域への参入")
            )

        risk_table = """
## 7. リスク要因 (Key Risks)

| リスク分類 | リスク内容 | 発生可能性 | インパクト | 緩和策・見解 |
|:---|:---|:---:|:---:|:---|"""

        for risk_type, content, probability, impact, mitigation in risks:
            risk_table += f"\n| {risk_type} | {content} | {probability} | {impact} | {mitigation} |"

        if not risks:
            risk_table += (
                "\n| 一般的 | 市場リスク | 中 | 中 | 分散投資によるリスク軽減 |"
            )

        return risk_table

    def generate_esg_analysis(self, analysis: ComprehensiveAnalysis) -> str:
        """8. ESG分析 セクション"""

        esg_section = f"""
## 8. ESG分析 (Environmental, Social, and Governance)

### ESG総合評価
- **総合スコア**: {analysis.esg_score.final_score:.1f}/5.0
- **ESGパーセンタイル**: {analysis.esg_score.percentile if analysis.esg_score.percentile else 'N/A'}%

### 環境 (E):
**機会:**
- 環境効率改善技術の開発・提供
- 再生可能エネルギーの活用拡大
- カーボンニュートラル目標の設定と達成

**リスク:**
- 環境規制の強化による追加コスト
- 気候変動による事業への影響

### 社会 (S):
**機会:**
- 従業員の多様性とインクルージョンの推進
- 地域社会への貢献活動
- 製品・サービスによる社会課題解決

**リスク:**
- 労働環境に関する社会的責任
- データプライバシーとセキュリティ

### ガバナンス (G):
**機会:**
- 透明性の高い企業統治
- リスク管理体制の強化
- ステークホルダーとの対話促進

**リスク:**
- 経営陣の説明責任
- 企業倫理とコンプライアンス
"""
        return esg_section

    def generate_conclusion(self, analysis: ComprehensiveAnalysis) -> str:
        """9. 結論と投資戦略 セクション"""

        # モニタリング項目の生成
        monitoring_items = []
        if analysis.financial_metrics.revenue_growth < 10:
            monitoring_items.append("売上成長率の四半期推移")
        if analysis.financial_metrics.operating_margin < 15:
            monitoring_items.append("営業利益率の改善状況")
        if analysis.catalyst_score.total_score < 3.5:
            monitoring_items.append("ニュースフローとセンチメント")
        if analysis.valuation_metrics.pe_ratio > 25:
            monitoring_items.append("バリュエーション水準の適正性")

        conclusion = f"""
## 9. 結論と投資戦略 (Conclusion & Investment Strategy)

### 9.1. 結論
**総合投資判断**: {analysis.recommendation.value}

{analysis.company_name}は、総合スコア{analysis.overall_score:.1f}/5.0の評価を獲得し、{"長期的な価値創造が期待できる優良投資先" if analysis.overall_score >= 3.5 else "慎重な検討が必要な銘柄" if analysis.overall_score >= 2.5 else "投資リスクが高い銘柄"}として評価される。

### 9.2. 投資戦略
- **投資判断**: {analysis.recommendation.value}
- **目標株価レンジ (12ヶ月)**: ${analysis.valuation_metrics.target_price_bear:.2f} ～ ${analysis.valuation_metrics.target_price_bull:.2f} (基本: ${analysis.valuation_metrics.target_price_basic:.2f})
- **投資期間**: 長期（3-5年）
- **エントリーポイント**: 現在の${analysis.valuation_metrics.current_price:.2f}付近は{"魅力的な水準" if analysis.overall_score >= 3.5 else "慎重な検討が必要な水準"}

### 主要モニタリング項目:
{chr(10).join([f"- {item}" for item in monitoring_items]) if monitoring_items else "- 定期的な業績確認"}
- ESG取り組みの進展
- 業界動向と競合状況の変化
"""
        return conclusion

    def generate_full_report(
        self, ticker_symbol: str, analysis_date: str = None
    ) -> str:
        """完全な投資分析レポートの生成"""

        if analysis_date is None:
            analysis_date = datetime.now().strftime("%Y-%m-%d")

        # 包括的分析の実行
        analysis = self.analyzer.analyze_stock(ticker_symbol, analysis_date)

        # レポートの各セクション生成
        header = f"""# 投資分析レポート: {analysis.company_name} ({analysis.ticker})

**レポート基本情報**
- 日付: {analysis.analysis_date}
- 銘柄名 / ティッカー: {analysis.company_name} ({analysis.ticker})

*本レポートは情報提供のみを目的としたものであり、特定の銘柄の売買等、投資判断を促すものではありません。最終的な投資判断は、ご自身の責任において行っていただくようお願いいたします。*
"""

        sections = [
            header,
            self.generate_executive_summary(analysis),
            self.generate_company_overview(analysis),
            self.generate_investment_thesis(analysis),
            self.generate_risk_analysis(analysis),
            self.generate_esg_analysis(analysis),
            self.generate_conclusion(analysis),
        ]

        return "\n".join(sections)


# 使用例
if __name__ == "__main__":
    generator = InvestmentReportGenerator()

    # TSLAの投資分析レポート生成
    report = generator.generate_full_report("TSLA")

    # ファイルに保存
    with open(
        f"./reports/TSLA_investment_report_{datetime.now().strftime('%Y-%m-%d')}.md",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(report)

    print("投資分析レポートを生成しました。")
    print(report[:1000] + "..." if len(report) > 1000 else report)
