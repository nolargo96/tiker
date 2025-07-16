"""
財務比較機能拡張モジュール
competitor_analysis.pyへの統合用の財務データ比較機能

このモジュールは、yfinanceで取得した財務データを使用して
競合他社との詳細な財務比較分析を提供します。
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import warnings

warnings.filterwarnings("ignore")


class FinancialComparison:
    """財務比較分析クラス"""
    
    def __init__(self):
        """財務比較分析の初期化"""
        self.financial_metrics = [
            'marketCap', 'forwardPE', 'trailingPE', 'priceToBook',
            'debtToEquity', 'returnOnEquity', 'returnOnAssets',
            'profitMargins', 'operatingMargins', 'grossMargins',
            'revenueGrowth', 'earningsGrowth', 'currentRatio',
            'quickRatio', 'totalCash', 'totalDebt', 'freeCashflow'
        ]
    
    def get_financial_metrics(self, ticker: str) -> Dict[str, Any]:
        """
        指定銘柄の財務指標を取得
        
        Args:
            ticker (str): ティッカーシンボル
            
        Returns:
            Dict[str, Any]: 財務指標の辞書
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info:
                return {}
            
            # 基本財務指標の取得
            metrics = {
                'ticker': ticker,
                'companyName': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'marketCap': info.get('marketCap'),
                'forwardPE': info.get('forwardPE'),
                'trailingPE': info.get('trailingPE'),
                'priceToBook': info.get('priceToBook'),
                'debtToEquity': info.get('debtToEquity'),
                'returnOnEquity': info.get('returnOnEquity'),
                'returnOnAssets': info.get('returnOnAssets'),
                'profitMargins': info.get('profitMargins'),
                'operatingMargins': info.get('operatingMargins'),
                'grossMargins': info.get('grossMargins'),
                'revenueGrowth': info.get('revenueGrowth'),
                'earningsGrowth': info.get('earningsGrowth'),
                'currentRatio': info.get('currentRatio'),
                'quickRatio': info.get('quickRatio'),
                'totalCash': info.get('totalCash'),
                'totalDebt': info.get('totalDebt'),
                'freeCashflow': info.get('freeCashflow'),
                'employees': info.get('fullTimeEmployees'),
                'beta': info.get('beta'),
                'dividendYield': info.get('dividendYield'),
                'payoutRatio': info.get('payoutRatio')
            }
            
            return metrics
            
        except Exception as e:
            print(f"エラー: {ticker}の財務データ取得に失敗 - {str(e)}")
            return {}
    
    def compare_financial_metrics(self, tickers: List[str]) -> pd.DataFrame:
        """
        複数銘柄の財務指標を比較
        
        Args:
            tickers (List[str]): 比較対象のティッカーリスト
            
        Returns:
            pd.DataFrame: 財務指標比較表
        """
        comparison_data = []
        
        for ticker in tickers:
            print(f"取得中: {ticker}")
            metrics = self.get_financial_metrics(ticker)
            if metrics:
                comparison_data.append(metrics)
        
        if not comparison_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(comparison_data)
        
        # インデックスをティッカーに設定
        df.set_index('ticker', inplace=True)
        
        return df
    
    def analyze_sector_performance(self, target_ticker: str, competitors: List[str]) -> Dict[str, Any]:
        """
        セクター内の相対パフォーマンス分析
        
        Args:
            target_ticker (str): 分析対象銘柄
            competitors (List[str]): 競合銘柄リスト
            
        Returns:
            Dict[str, Any]: セクター分析結果
        """
        all_tickers = [target_ticker] + competitors
        df = self.compare_financial_metrics(all_tickers)
        
        if df.empty:
            return {}
        
        # 数値列のみを選択
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        analysis = {
            'target_ticker': target_ticker,
            'sector_comparison': {},
            'rankings': {},
            'sector_averages': {},
            'target_vs_sector': {}
        }
        
        # セクター平均の計算
        for col in numeric_cols:
            if col in df.columns and not df[col].isna().all():
                sector_avg = df[col].mean()
                target_value = df.loc[target_ticker, col] if target_ticker in df.index else None
                
                analysis['sector_averages'][col] = sector_avg
                
                if target_value is not None and not pd.isna(target_value):
                    # セクター平均との比較
                    vs_sector = ((target_value - sector_avg) / sector_avg * 100) if sector_avg != 0 else 0
                    analysis['target_vs_sector'][col] = {
                        'target_value': target_value,
                        'sector_average': sector_avg,
                        'vs_sector_pct': vs_sector
                    }
                    
                    # ランキング計算
                    valid_values = df[col].dropna()
                    if len(valid_values) > 1:
                        ranking = (valid_values > target_value).sum() + 1
                        total_companies = len(valid_values)
                        analysis['rankings'][col] = {
                            'rank': ranking,
                            'total': total_companies,
                            'percentile': (total_companies - ranking + 1) / total_companies * 100
                        }
        
        return analysis
    
    def generate_financial_report(self, target_ticker: str, competitors: List[str]) -> str:
        """
        財務比較レポートを生成
        
        Args:
            target_ticker (str): 分析対象銘柄
            competitors (List[str]): 競合銘柄リスト
            
        Returns:
            str: レポート文字列
        """
        sector_analysis = self.analyze_sector_performance(target_ticker, competitors)
        
        if not sector_analysis:
            return f"エラー: {target_ticker}の財務データ分析に失敗しました。"
        
        report = f"""
## {target_ticker} 財務分析レポート

### セクター内相対評価

"""
        
        # 主要指標のレポート生成
        key_metrics = {
            'marketCap': ('時価総額', '$'),
            'forwardPE': ('予想PER', '倍'),
            'priceToBook': ('PBR', '倍'),
            'returnOnEquity': ('ROE', '%'),
            'profitMargins': ('利益率', '%'),
            'revenueGrowth': ('売上成長率', '%'),
            'debtToEquity': ('負債比率', '%')
        }
        
        for metric, (name, unit) in key_metrics.items():
            if metric in sector_analysis.get('target_vs_sector', {}):
                data = sector_analysis['target_vs_sector'][metric]
                target_val = data['target_value']
                sector_avg = data['sector_average']
                vs_sector = data['vs_sector_pct']
                
                # パーセンテージ表示の調整
                if unit == '%' and metric in ['returnOnEquity', 'profitMargins', 'revenueGrowth']:
                    target_display = f"{target_val:.1%}" if target_val else "N/A"
                    sector_display = f"{sector_avg:.1%}" if sector_avg else "N/A"
                elif unit == '$' and metric == 'marketCap':
                    target_display = f"${target_val/1e9:.1f}B" if target_val else "N/A"
                    sector_display = f"${sector_avg/1e9:.1f}B" if sector_avg else "N/A"
                else:
                    target_display = f"{target_val:.2f}" if target_val else "N/A"
                    sector_display = f"{sector_avg:.2f}" if sector_avg else "N/A"
                
                # ランキング情報
                rank_info = ""
                if metric in sector_analysis.get('rankings', {}):
                    rank_data = sector_analysis['rankings'][metric]
                    rank_info = f" (順位: {rank_data['rank']}/{rank_data['total']}位, {rank_data['percentile']:.0f}%ile)"
                
                # セクター比較の評価
                if vs_sector > 20:
                    vs_evaluation = "🟢 セクター平均を大幅に上回る"
                elif vs_sector > 5:
                    vs_evaluation = "🔵 セクター平均を上回る"
                elif vs_sector > -5:
                    vs_evaluation = "🟡 セクター平均並み"
                elif vs_sector > -20:
                    vs_evaluation = "🟠 セクター平均を下回る"
                else:
                    vs_evaluation = "🔴 セクター平均を大幅に下回る"
                
                report += f"""
**{name}**: {target_display} (セクター平均: {sector_display}){rank_info}
  → {vs_evaluation} ({vs_sector:+.1f}%)
"""
        
        return report
    
    def get_quarterly_trends(self, ticker: str) -> Dict[str, Any]:
        """
        四半期トレンド分析
        
        Args:
            ticker (str): ティッカーシンボル
            
        Returns:
            Dict[str, Any]: 四半期トレンドデータ
        """
        try:
            stock = yf.Ticker(ticker)
            
            # 四半期財務データ取得
            quarterly_financials = stock.quarterly_financials
            quarterly_balance = stock.quarterly_balance_sheet
            
            trends = {
                'ticker': ticker,
                'revenue_trend': {},
                'profit_trend': {},
                'growth_rates': {}
            }
            
            if not quarterly_financials.empty:
                # 売上高トレンド
                revenue_items = ['Total Revenue', 'Revenue']
                for item in revenue_items:
                    if item in quarterly_financials.index:
                        revenue_data = quarterly_financials.loc[item].dropna()
                        trends['revenue_trend'] = {
                            date.strftime('%Y-Q%m'): value/1e9 
                            for date, value in revenue_data.items()
                        }
                        
                        # 成長率計算（QoQ）
                        if len(revenue_data) >= 2:
                            latest_quarter = revenue_data.iloc[0]
                            prev_quarter = revenue_data.iloc[1]
                            qoq_growth = ((latest_quarter - prev_quarter) / prev_quarter * 100) if prev_quarter != 0 else 0
                            trends['growth_rates']['revenue_qoq'] = qoq_growth
                        
                        break
                
                # 純利益トレンド
                income_items = ['Net Income', 'Net Income From Continuing Ops']
                for item in income_items:
                    if item in quarterly_financials.index:
                        income_data = quarterly_financials.loc[item].dropna()
                        trends['profit_trend'] = {
                            date.strftime('%Y-Q%m'): value/1e9 
                            for date, value in income_data.items()
                        }
                        break
            
            return trends
            
        except Exception as e:
            print(f"エラー: {ticker}の四半期データ取得に失敗 - {str(e)}")
            return {}


# competitor_analysis.pyへの統合例
def extend_competitor_analysis():
    """
    CompetitorAnalysisクラスへの財務比較機能統合例
    """
    
    # 既存のCompetitorAnalysisクラスに以下のメソッドを追加
    additional_methods = '''
    
    def __init__(self, config_path: str = "config.yaml"):
        # 既存の初期化コード...
        
        # 財務比較機能を追加
        self.financial_comparison = FinancialComparison()
    
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
        """
        # 既存の競合分析レポート生成...
        existing_report = self.generate_competitor_report(ticker, period_days)
        
        # 財務分析の追加
        financial_analysis = self.analyze_financial_performance(ticker)
        
        if financial_analysis:
            financial_section = f"""

## 📊 財務パフォーマンス分析

{financial_analysis.get('financial_report', '')}

### 四半期売上トレンド
"""
            
            # 四半期データがある場合
            if 'quarterly_trends' in financial_analysis and financial_analysis['quarterly_trends']:
                trends = financial_analysis['quarterly_trends']
                if 'revenue_trend' in trends:
                    for quarter, revenue in list(trends['revenue_trend'].items())[:4]:
                        financial_section += f"- {quarter}: ${revenue:.1f}B\n"
                
                if 'growth_rates' in trends and 'revenue_qoq' in trends['growth_rates']:
                    qoq = trends['growth_rates']['revenue_qoq']
                    financial_section += f"\n**四半期成長率 (QoQ)**: {qoq:+.1f}%\n"
            
            enhanced_report = existing_report + financial_section
            return enhanced_report
        
        return existing_report
    '''
    
    return additional_methods


if __name__ == "__main__":
    # 使用例とテスト
    print("=== 財務比較機能テスト ===")
    
    # 財務比較クラスのインスタンス化
    financial_comp = FinancialComparison()
    
    # ポートフォリオ銘柄の財務比較
    portfolio_tickers = ["TSLA", "FSLR", "RKLB", "ASTS"]
    print(f"\nポートフォリオ財務比較: {', '.join(portfolio_tickers)}")
    
    comparison_df = financial_comp.compare_financial_metrics(portfolio_tickers)
    if not comparison_df.empty:
        print("\n財務指標比較テーブル:")
        print(comparison_df[['companyName', 'marketCap', 'forwardPE', 'returnOnEquity', 'profitMargins']].to_string())
    
    # 個別銘柄のセクター分析例
    print(f"\n=== TSLA セクター分析 ===")
    competitors = ["NIO", "RIVN", "LCID", "GM", "F"]
    
    sector_analysis = financial_comp.analyze_sector_performance("TSLA", competitors)
    if sector_analysis:
        report = financial_comp.generate_financial_report("TSLA", competitors)
        print(report)
    
    # 四半期トレンド例
    print(f"\n=== TSLA 四半期トレンド ===")
    quarterly_trends = financial_comp.get_quarterly_trends("TSLA")
    if quarterly_trends and 'revenue_trend' in quarterly_trends:
        print("四半期売上推移:")
        for quarter, revenue in list(quarterly_trends['revenue_trend'].items())[:4]:
            print(f"  {quarter}: ${revenue:.1f}B")
    
    print("\n=== テスト完了 ===")