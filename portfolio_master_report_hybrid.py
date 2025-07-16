"""
ハイブリッドポートフォリオレポート生成
全体戦略（概要・最適化）+ 9銘柄別統合タブ構成

実行方法:
    python portfolio_master_report_hybrid.py
"""

import os
import glob
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional
from competitor_analysis import CompetitorAnalysis
from financial_comparison_extension import FinancialComparison
from html_report_generator import HTMLReportGenerator
from stock_analyzer_lib import StockDataManager, ConfigManager, TechnicalIndicators
import yfinance as yf
import warnings

warnings.filterwarnings("ignore")


class PortfolioMasterReportHybrid:
    """ハイブリッドポートフォリオレポート生成クラス"""
    
    def __init__(self):
        self.config = ConfigManager("config.yaml")
        self.competitor_analyzer = CompetitorAnalysis()
        self.financial_comparison = FinancialComparison()
        self.html_generator = HTMLReportGenerator("config.yaml")
        self.data_manager = StockDataManager(self.config)
        
        # ポートフォリオ構成とセクター色定義
        self.portfolio = {
            "TSLA": {"weight": 20, "name": "Tesla", "sector": "EV・自動運転", "color": "#e31837"},
            "FSLR": {"weight": 20, "name": "First Solar", "sector": "ソーラーパネル", "color": "#ffd700"},
            "RKLB": {"weight": 10, "name": "Rocket Lab", "sector": "小型ロケット", "color": "#ff6b35"},
            "ASTS": {"weight": 10, "name": "AST SpaceMobile", "sector": "衛星通信", "color": "#4a90e2"},
            "OKLO": {"weight": 10, "name": "Oklo", "sector": "SMR原子炉", "color": "#50c878"},
            "JOBY": {"weight": 10, "name": "Joby Aviation", "sector": "eVTOL", "color": "#9b59b6"},
            "OII": {"weight": 10, "name": "Oceaneering", "sector": "海洋エンジニアリング", "color": "#1abc9c"},
            "LUNR": {"weight": 5, "name": "Intuitive Machines", "sector": "月面探査", "color": "#34495e"},
            "RDW": {"weight": 5, "name": "Redwire", "sector": "宇宙インフラ", "color": "#e74c3c"}
        }
        
        self.report_date = datetime.now().strftime('%Y-%m-%d')
        
    def read_discussion_report(self, ticker: str) -> Optional[str]:
        """討論形式レポートを読み込む"""
        pattern = f"reports/{ticker}_discussion_analysis_*.md"
        files = glob.glob(pattern)
        if files:
            latest_file = max(files)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"エラー: {ticker}の討論レポート読み込み失敗 - {e}")
        return None
        
    def read_competitor_report(self, ticker: str) -> Optional[str]:
        """競合分析レポートを読み込む"""
        pattern = f"reports/competitor_analysis_{ticker}_*.md"
        files = glob.glob(pattern)
        if files:
            latest_file = max(files)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"エラー: {ticker}の競合レポート読み込み失敗 - {e}")
        return None
    
    def get_current_metrics(self, ticker: str) -> Dict:
        """現在の株価と技術指標を取得"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 株価データ取得
            success, df, error_msg = self.data_manager.fetch_stock_data(ticker)
            if not success or df is None or df.empty:
                return {}
                
            # 技術指標計算
            df = self.data_manager.add_technical_indicators(df)
            
            latest = df.iloc[-1]
            
            return {
                'current_price': latest['Close'],
                'change_pct': ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100),
                'rsi': latest['RSI'],
                'ema20': latest['EMA20'],
                'ema50': latest['EMA50'],
                'sma200': latest['SMA200'],
                'volume': latest['Volume'],
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('forwardPE', 0),
                'profit_margin': info.get('profitMargins', 0),
                'bb_upper': latest.get('BB_upper', 0),
                'bb_lower': latest.get('BB_lower', 0),
                'atr': latest.get('ATR', 0)
            }
        except Exception as e:
            print(f"エラー: {ticker}の現在データ取得失敗 - {e}")
            return {}
    
    def get_financial_metrics(self, ticker: str) -> Dict:
        """財務指標を取得"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('forwardPE', 'N/A'),
                'roe': info.get('returnOnEquity', 0),
                'profit_margin': info.get('profitMargins', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'gross_margin': info.get('grossMargins', 0)
            }
        except Exception as e:
            print(f"エラー: {ticker}の財務データ取得失敗 - {e}")
            return {}
    
    def calculate_portfolio_optimization(self) -> Dict:
        """ポートフォリオ最適化分析"""
        optimization = {
            'current_allocation': {},
            'recommended_allocation': {},
            'risk_metrics': {},
            'expected_returns': {}
        }
        
        # 各銘柄のリスク・リターン分析
        for ticker, info in self.portfolio.items():
            # 現在の配分
            optimization['current_allocation'][ticker] = info['weight']
            
            # リスク評価（セクター別）
            risk_score = 5  # デフォルト中リスク
            if ticker in ['ASTS', 'OKLO', 'LUNR', 'RDW']:
                risk_score = 8  # 高リスク
            elif ticker in ['TSLA', 'FSLR']:
                risk_score = 4  # 低リスク
            elif ticker in ['RKLB', 'JOBY', 'OII']:
                risk_score = 6  # 中高リスク
                
            optimization['risk_metrics'][ticker] = risk_score
            
            # 期待リターン（セクター成長率ベース）
            expected_return = 15  # デフォルト15%
            if info['sector'] in ['小型ロケット', '衛星通信', 'eVTOL']:
                expected_return = 25
            elif info['sector'] in ['EV・自動運転', 'ソーラーパネル']:
                expected_return = 20
            elif info['sector'] in ['月面探査', '宇宙インフラ']:
                expected_return = 30
                
            optimization['expected_returns'][ticker] = expected_return
        
        # 推奨配分の計算（リスク調整後）
        total_score = 0
        scores = {}
        
        for ticker in self.portfolio:
            # スコア = 期待リターン / リスク
            score = optimization['expected_returns'][ticker] / optimization['risk_metrics'][ticker]
            scores[ticker] = score
            total_score += score
        
        # 正規化して推奨配分を計算
        for ticker, score in scores.items():
            recommended_pct = (score / total_score) * 100
            optimization['recommended_allocation'][ticker] = round(recommended_pct, 1)
            
        return optimization
    
    def generate_hybrid_html_report(self) -> str:
        """ハイブリッドHTMLレポートを生成"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ポートフォリオ統合レポート - {self.report_date}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ポートフォリオ統合レポート</h1>
            <div class="subtitle">全体戦略 + 9銘柄統合分析 - {self.report_date}</div>
        </div>
        
        <div class="nav-tabs">
            <div class="nav-tab active" onclick="showSection('overview')">📊 概要</div>
            <div class="nav-tab" onclick="showSection('optimization')">🎯 最適化</div>
            {self._generate_stock_tabs()}
        </div>
        
        {self._generate_overview_section()}
        {self._generate_optimization_section()}
        {self._generate_stock_sections()}
        
        <div class="footer">
            <p>本レポートは教育目的のシミュレーションです。投資判断は自己責任で行ってください。</p>
            <p>生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        {self._get_javascript_code()}
    </script>
</body>
</html>
"""
        
        return html_content
    
    def _get_css_styles(self) -> str:
        """CSSスタイルを取得"""
        return """
        :root {
            --primary-color: #1e3a8a;
            --secondary-color: #3730a3;
            --success-color: #059669;
            --warning-color: #d97706;
            --danger-color: #dc2626;
            --bg-color: #f9fafb;
            --card-bg: #ffffff;
            --text-primary: #111827;
            --text-secondary: #6b7280;
            --border-color: #e5e7eb;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .nav-tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 30px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
            overflow-x: auto;
            white-space: nowrap;
        }
        
        .nav-tab {
            padding: 12px 20px;
            background: var(--card-bg);
            border: 2px solid var(--border-color);
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9rem;
            font-weight: 500;
            min-width: 120px;
            text-align: center;
        }
        
        .nav-tab:hover {
            background: var(--primary-color);
            color: white;
            transform: translateY(-2px);
        }
        
        .nav-tab.active {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }
        
        .stock-tab {
            position: relative;
        }
        
        .stock-tab::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            border-radius: 8px 8px 0 0;
        }
        
        .content-section {
            display: none;
            animation: fadeIn 0.5s;
        }
        
        .content-section.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .portfolio-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stock-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
            border-left: 4px solid var(--primary-color);
        }
        
        .stock-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
        }
        
        .stock-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .stock-ticker {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .stock-weight {
            background: var(--secondary-color);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .stock-name {
            font-size: 1.2rem;
            color: var(--text-primary);
            margin-bottom: 5px;
        }
        
        .stock-sector {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 20px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric-item {
            background: var(--bg-color);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            font-size: 1.4rem;
            font-weight: bold;
            color: var(--text-primary);
            margin-top: 4px;
        }
        
        .analysis-section {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .analysis-section h3 {
            color: var(--primary-color);
            margin-bottom: 15px;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .expert-discussion {
            background: var(--bg-color);
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid var(--secondary-color);
        }
        
        .expert-discussion pre {
            white-space: pre-wrap;
            font-family: inherit;
            font-size: 0.9rem;
            line-height: 1.6;
        }
        
        .competitor-analysis {
            background: var(--bg-color);
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid var(--success-color);
        }
        
        .financial-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .financial-table th,
        .financial-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        .financial-table th {
            background: var(--primary-color);
            color: white;
            font-weight: 600;
        }
        
        .financial-table tr:hover {
            background: var(--bg-color);
        }
        
        .technical-indicators {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .indicator-card {
            background: var(--bg-color);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .indicator-value {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .rsi-overbought { color: var(--danger-color); }
        .rsi-oversold { color: var(--success-color); }
        .rsi-neutral { color: var(--warning-color); }
        
        .positive { color: var(--success-color); }
        .negative { color: var(--danger-color); }
        
        .optimization-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .optimization-table th,
        .optimization-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        .optimization-table th {
            background: var(--primary-color);
            color: white;
            font-weight: 600;
        }
        
        .optimization-table tr:hover {
            background: var(--bg-color);
        }
        
        .strategy-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .strategy-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid var(--secondary-color);
        }
        
        .strategy-card h4 {
            color: var(--primary-color);
            margin-bottom: 10px;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 40px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .nav-tabs {
                flex-direction: column;
                gap: 10px;
            }
            
            .nav-tab {
                min-width: auto;
            }
            
            .portfolio-grid {
                grid-template-columns: 1fr;
            }
            
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def _generate_stock_tabs(self) -> str:
        """銘柄別タブを生成"""
        tabs = ""
        for ticker, info in self.portfolio.items():
            tabs += f'<div class="nav-tab stock-tab" onclick="showSection(\'{ticker.lower()}\')" style="border-left-color: {info["color"]}">{ticker}</div>'
        return tabs
    
    def _generate_overview_section(self) -> str:
        """概要セクションを生成"""
        total_stocks = len(self.portfolio)
        sectors = list(set(info['sector'] for info in self.portfolio.values()))
        
        return f"""
        <div id="overview" class="content-section active">
            <h2>📊 ポートフォリオ概要</h2>
            
            <div class="portfolio-grid">
                <div class="stock-card">
                    <h3>🎯 投資戦略</h3>
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <div class="metric-label">総銘柄数</div>
                            <div class="metric-value">{total_stocks}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">セクター数</div>
                            <div class="metric-value">{len(sectors)}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">投資期間</div>
                            <div class="metric-value">3-5年</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">リスク水準</div>
                            <div class="metric-value">中〜高</div>
                        </div>
                    </div>
                </div>
                
                <div class="stock-card">
                    <h3>⚖️ 配分方針</h3>
                    <div class="analysis-section">
                        <div><strong>コア銘柄（20%）:</strong> TSLA, FSLR</div>
                        <div><strong>成長銘柄（10%）:</strong> RKLB, ASTS, OKLO, JOBY, OII</div>
                        <div><strong>高リスク銘柄（5%）:</strong> LUNR, RDW</div>
                    </div>
                </div>
            </div>
            
            <div class="portfolio-grid">
                {self._generate_current_portfolio_cards()}
            </div>
            
            <div class="analysis-section">
                <h3>💡 投資方針</h3>
                <p>本ポートフォリオは、次世代テクノロジーセクターへの分散投資を通じて、
                中長期的な成長を目指します。EV・再生可能エネルギーをコアとしつつ、
                宇宙・航空・海洋といった新領域への投資機会も積極的に捉えています。</p>
            </div>
        </div>
        """
    
    def _generate_current_portfolio_cards(self) -> str:
        """現在のポートフォリオカードを生成"""
        cards = ""
        for ticker, info in self.portfolio.items():
            metrics = self.get_current_metrics(ticker)
            if metrics:
                change_class = "positive" if metrics.get('change_pct', 0) >= 0 else "negative"
                change_symbol = "+" if metrics.get('change_pct', 0) >= 0 else ""
                
                cards += f"""
                <div class="stock-card" style="border-left-color: {info['color']}">
                    <div class="stock-header">
                        <div class="stock-ticker">{ticker}</div>
                        <div class="stock-weight">{info['weight']}%</div>
                    </div>
                    <div class="stock-name">{info['name']}</div>
                    <div class="stock-sector">{info['sector']}</div>
                    
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <div class="metric-label">現在価格</div>
                            <div class="metric-value">${metrics.get('current_price', 0):.2f}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">前日比</div>
                            <div class="metric-value {change_class}">{change_symbol}{metrics.get('change_pct', 0):.2f}%</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">RSI</div>
                            <div class="metric-value">{metrics.get('rsi', 0):.1f}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">時価総額</div>
                            <div class="metric-value">${metrics.get('market_cap', 0)/1e9:.1f}B</div>
                        </div>
                    </div>
                </div>
                """
        return cards
    
    def _generate_optimization_section(self) -> str:
        """最適化セクションを生成"""
        optimization = self.calculate_portfolio_optimization()
        
        # 最適化テーブルの生成
        optimization_table = ""
        for ticker, info in self.portfolio.items():
            current = optimization['current_allocation'][ticker]
            recommended = optimization['recommended_allocation'][ticker]
            change = recommended - current
            risk = optimization['risk_metrics'][ticker]
            
            change_class = "positive" if change > 0 else "negative" if change < 0 else ""
            risk_color = "color: var(--danger-color);" if risk >= 7 else "color: var(--warning-color);" if risk >= 5 else "color: var(--success-color);"
            
            optimization_table += f"""
            <tr>
                <td><strong>{ticker}</strong></td>
                <td>{info['sector']}</td>
                <td>{current}%</td>
                <td>{recommended}%</td>
                <td class="{change_class}">{'+' if change > 0 else ''}{change:.1f}%</td>
                <td style="{risk_color}">{risk}/10</td>
            </tr>
            """
        
        return f"""
        <div id="optimization" class="content-section">
            <h2>🎯 ポートフォリオ最適化</h2>
            
            <div class="analysis-section">
                <h3>📈 現在配分 vs 推奨配分</h3>
                <table class="optimization-table">
                    <thead>
                        <tr>
                            <th>銘柄</th>
                            <th>セクター</th>
                            <th>現在配分</th>
                            <th>推奨配分</th>
                            <th>変更幅</th>
                            <th>リスクレベル</th>
                        </tr>
                    </thead>
                    <tbody>
                        {optimization_table}
                    </tbody>
                </table>
            </div>
            
            <div class="strategy-cards">
                <div class="strategy-card">
                    <h4>🛡️ リスク管理</h4>
                    <p>高リスク銘柄（ASTS、OKLO、LUNR、RDW）の配分を抑制し、
                    安定成長銘柄（TSLA、FSLR）の比重を維持することで、
                    ポートフォリオ全体のリスクを管理します。</p>
                </div>
                
                <div class="strategy-card">
                    <h4>📈 成長性重視</h4>
                    <p>宇宙・航空セクター（RKLB、ASTS、LUNR）は高い成長性を持つため、
                    リスクを考慮しつつも一定の配分を維持し、
                    長期的な成長機会を捉えます。</p>
                </div>
                
                <div class="strategy-card">
                    <h4>🎯 分散投資</h4>
                    <p>9つの異なるセクターへの分散により、
                    特定セクターのリスクを軽減しつつ、
                    次世代テクノロジー全体の成長を享受します。</p>
                </div>
            </div>
            
            <div class="analysis-section">
                <h3>📌 推奨アクション</h3>
                <div class="strategy-cards">
                    <div class="strategy-card">
                        <h4>短期（1-3ヶ月）</h4>
                        <ul>
                            <li>現在の配分を維持し、各銘柄の四半期決算を注視</li>
                            <li>特にTSLA、FSLRのコア銘柄の業績動向を重点監視</li>
                        </ul>
                    </div>
                    
                    <div class="strategy-card">
                        <h4>中期（3-6ヶ月）</h4>
                        <ul>
                            <li>推奨配分に向けた段階的なリバランスを検討</li>
                            <li>高リスク銘柄の進捗を評価し、必要に応じて調整</li>
                        </ul>
                    </div>
                    
                    <div class="strategy-card">
                        <h4>長期（6ヶ月以上）</h4>
                        <ul>
                            <li>新興テクノロジーの市場成熟度を評価</li>
                            <li>ポートフォリオ全体の戦略的見直しを実施</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_stock_sections(self) -> str:
        """銘柄別セクションを生成"""
        sections = ""
        for ticker, info in self.portfolio.items():
            sections += self._generate_single_stock_section(ticker, info)
        return sections
    
    def _generate_single_stock_section(self, ticker: str, info: Dict) -> str:
        """単一銘柄セクションを生成"""
        # データ取得
        metrics = self.get_current_metrics(ticker)
        financial_metrics = self.get_financial_metrics(ticker)
        discussion = self.read_discussion_report(ticker)
        competitor_report = self.read_competitor_report(ticker)
        
        # 基本情報セクション
        change_class = "positive" if metrics.get('change_pct', 0) >= 0 else "negative"
        change_symbol = "+" if metrics.get('change_pct', 0) >= 0 else ""
        
        # RSIクラス判定
        rsi_class = "rsi-neutral"
        if metrics.get('rsi', 50) > 70:
            rsi_class = "rsi-overbought"
        elif metrics.get('rsi', 50) < 30:
            rsi_class = "rsi-oversold"
        
        # 基本情報
        basic_info = f"""
        <div class="analysis-section">
            <h3>📊 基本情報</h3>
            <div class="stock-header">
                <div class="stock-ticker">{ticker}</div>
                <div class="stock-weight">{info['weight']}%</div>
            </div>
            <div class="stock-name">{info['name']}</div>
            <div class="stock-sector">{info['sector']}</div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">現在価格</div>
                    <div class="metric-value">${metrics.get('current_price', 0):.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">前日比</div>
                    <div class="metric-value {change_class}">{change_symbol}{metrics.get('change_pct', 0):.2f}%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">時価総額</div>
                    <div class="metric-value">${metrics.get('market_cap', 0)/1e9:.1f}B</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">ポートフォリオ配分</div>
                    <div class="metric-value">{info['weight']}%</div>
                </div>
            </div>
        </div>
        """
        
        # 専門家討論
        expert_discussion = ""
        if discussion:
            summary = discussion[:1200] + "..." if len(discussion) > 1200 else discussion
            expert_discussion = f"""
            <div class="analysis-section">
                <h3>🗣️ 専門家討論</h3>
                <div class="expert-discussion">
                    <pre>{summary}</pre>
                </div>
            </div>
            """
        
        # 競合分析
        competitor_analysis = ""
        if competitor_report:
            summary = competitor_report[:1000] + "..." if len(competitor_report) > 1000 else competitor_report
            competitor_analysis = f"""
            <div class="analysis-section">
                <h3>🏆 競合分析</h3>
                <div class="competitor-analysis">
                    <pre>{summary}</pre>
                </div>
            </div>
            """
        
        # 財務分析
        financial_analysis = f"""
        <div class="analysis-section">
            <h3>💰 財務分析</h3>
            <table class="financial-table">
                <tr>
                    <th>指標</th>
                    <th>値</th>
                </tr>
                <tr>
                    <td>時価総額</td>
                    <td>${financial_metrics.get('market_cap', 0)/1e9:.1f}B</td>
                </tr>
                <tr>
                    <td>予想PER</td>
                    <td>{financial_metrics.get('pe_ratio', 'N/A')}</td>
                </tr>
                <tr>
                    <td>ROE</td>
                    <td>{financial_metrics.get('roe', 0)*100:.1f}%</td>
                </tr>
                <tr>
                    <td>利益率</td>
                    <td>{financial_metrics.get('profit_margin', 0)*100:.1f}%</td>
                </tr>
                <tr>
                    <td>売上成長率</td>
                    <td>{financial_metrics.get('revenue_growth', 0)*100:.1f}%</td>
                </tr>
            </table>
        </div>
        """
        
        # 技術指標
        technical_indicators = f"""
        <div class="analysis-section">
            <h3>📈 技術指標</h3>
            <div class="technical-indicators">
                <div class="indicator-card">
                    <div class="indicator-value {rsi_class}">{metrics.get('rsi', 0):.1f}</div>
                    <div class="metric-label">RSI (14)</div>
                </div>
                <div class="indicator-card">
                    <div class="indicator-value">${metrics.get('ema20', 0):.2f}</div>
                    <div class="metric-label">EMA 20</div>
                </div>
                <div class="indicator-card">
                    <div class="indicator-value">${metrics.get('ema50', 0):.2f}</div>
                    <div class="metric-label">EMA 50</div>
                </div>
                <div class="indicator-card">
                    <div class="indicator-value">${metrics.get('sma200', 0):.2f}</div>
                    <div class="metric-label">SMA 200</div>
                </div>
                <div class="indicator-card">
                    <div class="indicator-value">${metrics.get('bb_upper', 0):.2f}</div>
                    <div class="metric-label">BB 上限</div>
                </div>
                <div class="indicator-card">
                    <div class="indicator-value">${metrics.get('bb_lower', 0):.2f}</div>
                    <div class="metric-label">BB 下限</div>
                </div>
            </div>
        </div>
        """
        
        return f"""
        <div id="{ticker.lower()}" class="content-section">
            <h2 style="color: {info['color']};">{ticker} - {info['name']}</h2>
            {basic_info}
            {expert_discussion}
            {competitor_analysis}
            {financial_analysis}
            {technical_indicators}
        </div>
        """
    
    def _get_javascript_code(self) -> str:
        """JavaScriptコードを取得"""
        return """
        function showSection(sectionId) {
            // すべてのセクションを非表示
            const sections = document.querySelectorAll('.content-section');
            sections.forEach(section => section.classList.remove('active'));
            
            // すべてのタブを非アクティブ
            const tabs = document.querySelectorAll('.nav-tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // 選択されたセクションを表示
            document.getElementById(sectionId).classList.add('active');
            
            // 選択されたタブをアクティブ
            event.target.classList.add('active');
        }
        
        // ページ読み込み時の処理
        document.addEventListener('DOMContentLoaded', function() {
            console.log('ハイブリッドレポート読み込み完了');
        });
        """
    
    def save_report(self, output_path: str = None):
        """レポートを保存"""
        if output_path is None:
            output_path = f"reports/html/portfolio_hybrid_report_{self.report_date}.html"
        
        # ディレクトリ作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # HTMLレポート生成
        html_content = self.generate_hybrid_html_report()
        
        # ファイル保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ ハイブリッドレポート保存完了: {output_path}")
        
        return output_path


def main():
    """メイン実行関数"""
    print("🚀 ハイブリッドポートフォリオレポート生成開始...")
    
    # レポート生成
    generator = PortfolioMasterReportHybrid()
    
    # レポート保存
    output_path = generator.save_report()
    
    print(f"\n✨ レポート生成完了！")
    print(f"📄 ファイル: {output_path}")
    print(f"\n💡 ブラウザで開いてご確認ください。")
    
    # 自動的にブラウザで開く（オプション）
    try:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(output_path)}")
    except:
        pass


if __name__ == "__main__":
    main()