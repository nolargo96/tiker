"""
ポートフォリオ総合マスターレポート生成
すべての分析（討論、競合、財務）を統合した包括的HTMLレポート

実行方法:
    python portfolio_master_report.py
"""

import os
import glob
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional
from src.portfolio.competitor_analysis import CompetitorAnalysis
from src.portfolio.financial_comparison_extension import FinancialComparison
from src.visualization.html_report_generator import HTMLReportGenerator
from src.analysis.stock_analyzer_lib import StockDataManager, ConfigManager, TechnicalIndicators
import yfinance as yf
import warnings

warnings.filterwarnings("ignore")


class PortfolioMasterReport:
    """ポートフォリオ総合レポート生成クラス"""
    
    def __init__(self):
        self.config = ConfigManager("config/config.yaml")
        self.competitor_analyzer = CompetitorAnalysis()
        self.financial_comparison = FinancialComparison()
        self.html_generator = HTMLReportGenerator(self.config)
        self.data_manager = StockDataManager(self.config)
        
        # ポートフォリオ構成
        self.portfolio = {
            "TSLA": {"weight": 20, "name": "Tesla", "sector": "EV・自動運転"},
            "FSLR": {"weight": 20, "name": "First Solar", "sector": "ソーラーパネル"},
            "RKLB": {"weight": 10, "name": "Rocket Lab", "sector": "小型ロケット"},
            "ASTS": {"weight": 10, "name": "AST SpaceMobile", "sector": "衛星通信"},
            "OKLO": {"weight": 10, "name": "Oklo", "sector": "SMR原子炉"},
            "JOBY": {"weight": 10, "name": "Joby Aviation", "sector": "eVTOL"},
            "OII": {"weight": 10, "name": "Oceaneering", "sector": "海洋エンジニアリング"},
            "LUNR": {"weight": 5, "name": "Intuitive Machines", "sector": "月面探査"},
            "RDW": {"weight": 5, "name": "Redwire", "sector": "宇宙インフラ"}
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
            df = self.data_manager.fetch_stock_data(ticker)
            if df is None or df.empty:
                return {}
                
            # 技術指標計算
            indicators = TechnicalIndicators()
            df = indicators.add_all_indicators(df)
            
            latest = df.iloc[-1]
            
            return {
                'current_price': latest['Close'],
                'change_pct': ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100),
                'rsi': latest['RSI'],
                'ema20': latest['EMA20'],
                'ema50': latest['EMA50'],
                'volume': latest['Volume'],
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('forwardPE', 0),
                'profit_margin': info.get('profitMargins', 0)
            }
        except Exception as e:
            print(f"エラー: {ticker}の現在データ取得失敗 - {e}")
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
            metrics = self.get_current_metrics(ticker)
            
            # 現在の配分
            optimization['current_allocation'][ticker] = info['weight']
            
            # リスク評価（簡易版）
            risk_score = 5  # デフォルト中リスク
            if ticker in ['ASTS', 'OKLO', 'LUNR', 'RDW']:
                risk_score = 8  # 高リスク
            elif ticker in ['TSLA', 'FSLR']:
                risk_score = 4  # 低リスク
                
            optimization['risk_metrics'][ticker] = risk_score
            
            # 期待リターン（セクター成長率ベース）
            expected_return = 15  # デフォルト15%
            if info['sector'] in ['小型ロケット', '衛星通信', 'eVTOL']:
                expected_return = 25
            elif info['sector'] in ['EV・自動運転', 'ソーラーパネル']:
                expected_return = 20
                
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
    
    def generate_master_html_report(self) -> str:
        """総合HTMLレポートを生成"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ポートフォリオ総合マスターレポート - {self.report_date}</title>
    <style>
        :root {{
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
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .nav-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
            overflow-x: auto;
        }}
        
        .nav-tab {{
            padding: 10px 20px;
            background: var(--card-bg);
            border: 2px solid var(--border-color);
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            transition: all 0.3s;
            white-space: nowrap;
        }}
        
        .nav-tab:hover {{
            background: var(--primary-color);
            color: white;
        }}
        
        .nav-tab.active {{
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }}
        
        .content-section {{
            display: none;
            animation: fadeIn 0.5s;
        }}
        
        .content-section.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .portfolio-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stock-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .stock-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .stock-ticker {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }}
        
        .stock-weight {{
            background: var(--secondary-color);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
        }}
        
        .metric-row {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 8px;
            background: var(--bg-color);
            border-radius: 6px;
        }}
        
        .metric-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .metric-value {{
            font-weight: bold;
        }}
        
        .positive {{
            color: var(--success-color);
        }}
        
        .negative {{
            color: var(--danger-color);
        }}
        
        .discussion-section {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .discussion-section h3 {{
            color: var(--primary-color);
            margin-bottom: 15px;
            font-size: 1.3rem;
        }}
        
        .expert-comment {{
            background: var(--bg-color);
            border-left: 4px solid var(--secondary-color);
            padding: 15px;
            margin: 10px 0;
            border-radius: 0 8px 8px 0;
        }}
        
        .expert-name {{
            font-weight: bold;
            color: var(--secondary-color);
            margin-bottom: 5px;
        }}
        
        .optimization-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .optimization-table th, .optimization-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .optimization-table th {{
            background: var(--primary-color);
            color: white;
            font-weight: bold;
        }}
        
        .optimization-table tr:hover {{
            background: var(--bg-color);
        }}
        
        .chart-container {{
            width: 100%;
            height: 400px;
            margin: 20px 0;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .portfolio-grid {{
                grid-template-columns: 1fr;
            }}
            
            .nav-tabs {{
                flex-wrap: wrap;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ポートフォリオ総合マスターレポート</h1>
            <div class="subtitle">9銘柄の包括的分析と最適化提案 - {self.report_date}</div>
        </div>
        
        <div class="nav-tabs">
            <div class="nav-tab active" onclick="showSection('overview')">概要</div>
            <div class="nav-tab" onclick="showSection('current')">現在の状況</div>
            <div class="nav-tab" onclick="showSection('discussions')">専門家討論</div>
            <div class="nav-tab" onclick="showSection('financials')">財務分析</div>
            <div class="nav-tab" onclick="showSection('competitors')">競合分析</div>
            <div class="nav-tab" onclick="showSection('optimization')">最適化提案</div>
        </div>
"""
        
        # 概要セクション
        html_content += self._generate_overview_section()
        
        # 現在の状況セクション
        html_content += self._generate_current_status_section()
        
        # 専門家討論セクション
        html_content += self._generate_discussions_section()
        
        # 財務分析セクション
        html_content += self._generate_financials_section()
        
        # 競合分析セクション
        html_content += self._generate_competitors_section()
        
        # 最適化提案セクション
        html_content += self._generate_optimization_section()
        
        # フッターとスクリプト
        html_content += """
        <div class="footer">
            <p>本レポートは教育目的のシミュレーションです。投資判断は自己責任で行ってください。</p>
            <p>生成日時: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
    </div>
    
    <script>
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
        
        // チャート描画（プレースホルダー）
        function drawCharts() {
            console.log('Charts would be drawn here');
        }
        
        // ページ読み込み時の処理
        document.addEventListener('DOMContentLoaded', function() {
            drawCharts();
        });
    </script>
</body>
</html>
"""
        
        return html_content
    
    def _generate_overview_section(self) -> str:
        """概要セクションを生成"""
        total_stocks = len(self.portfolio)
        sectors = list(set(info['sector'] for info in self.portfolio.values()))
        
        return f"""
        <div id="overview" class="content-section active">
            <h2>📊 ポートフォリオ概要</h2>
            
            <div class="portfolio-grid">
                <div class="stock-card">
                    <h3>ポートフォリオ構成</h3>
                    <div class="metric-row">
                        <span class="metric-label">総銘柄数</span>
                        <span class="metric-value">{total_stocks}銘柄</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">セクター数</span>
                        <span class="metric-value">{len(sectors)}セクター</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">投資テーマ</span>
                        <span class="metric-value">次世代テクノロジー</span>
                    </div>
                </div>
                
                <div class="stock-card">
                    <h3>配分方針</h3>
                    <div class="metric-row">
                        <span class="metric-label">コア銘柄（20%）</span>
                        <span class="metric-value">TSLA, FSLR</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">成長銘柄（10%）</span>
                        <span class="metric-value">RKLB, ASTS, OKLO, JOBY, OII</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">高リスク銘柄（5%）</span>
                        <span class="metric-value">LUNR, RDW</span>
                    </div>
                </div>
                
                <div class="stock-card">
                    <h3>投資戦略</h3>
                    <div class="metric-row">
                        <span class="metric-label">投資期間</span>
                        <span class="metric-value">中長期（3-5年）</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">リバランス頻度</span>
                        <span class="metric-value">四半期毎</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">リスク許容度</span>
                        <span class="metric-value">中〜高</span>
                    </div>
                </div>
            </div>
            
            <div class="discussion-section">
                <h3>🎯 投資方針</h3>
                <p>本ポートフォリオは、次世代テクノロジーセクターへの分散投資を通じて、
                中長期的な成長を目指します。EV・再生可能エネルギーをコアとしつつ、
                宇宙・航空・海洋といった新領域への投資機会も積極的に捉えています。</p>
            </div>
        </div>
"""
    
    def _generate_current_status_section(self) -> str:
        """現在の状況セクションを生成"""
        html = """
        <div id="current" class="content-section">
            <h2>📈 現在の状況</h2>
            <div class="portfolio-grid">
"""
        
        for ticker, info in self.portfolio.items():
            metrics = self.get_current_metrics(ticker)
            
            if metrics:
                change_class = "positive" if metrics.get('change_pct', 0) >= 0 else "negative"
                change_symbol = "+" if metrics.get('change_pct', 0) >= 0 else ""
                
                html += f"""
                <div class="stock-card">
                    <div class="stock-header">
                        <span class="stock-ticker">{ticker}</span>
                        <span class="stock-weight">{info['weight']}%</span>
                    </div>
                    <h4>{info['name']}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">{info['sector']}</p>
                    
                    <div class="metric-row">
                        <span class="metric-label">現在価格</span>
                        <span class="metric-value">${metrics.get('current_price', 0):.2f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">前日比</span>
                        <span class="metric-value {change_class}">{change_symbol}{metrics.get('change_pct', 0):.2f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">RSI</span>
                        <span class="metric-value">{metrics.get('rsi', 0):.1f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">時価総額</span>
                        <span class="metric-value">${metrics.get('market_cap', 0)/1e9:.1f}B</span>
                    </div>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
        return html
    
    def _generate_discussions_section(self) -> str:
        """専門家討論セクションを生成"""
        html = """
        <div id="discussions" class="content-section">
            <h2>🗣️ 専門家討論分析</h2>
"""
        
        for ticker, info in self.portfolio.items():
            discussion = self.read_discussion_report(ticker)
            
            if discussion:
                # 討論内容から重要部分を抽出（最初の1000文字）
                summary = discussion[:1000] + "..." if len(discussion) > 1000 else discussion
                
                html += f"""
                <div class="discussion-section">
                    <h3>{ticker} - {info['name']}</h3>
                    <div class="expert-comment">
                        <pre style="white-space: pre-wrap; font-family: inherit;">{summary}</pre>
                    </div>
                    <p style="text-align: right; font-size: 0.9rem;">
                        <a href="#" onclick="alert('完全な討論レポートは別ファイルを参照してください')">全文を読む →</a>
                    </p>
                </div>
"""
        
        html += """
        </div>
"""
        return html
    
    def _generate_financials_section(self) -> str:
        """財務分析セクションを生成"""
        # 財務比較データを取得
        comparison_df = self.financial_comparison.compare_financial_metrics(list(self.portfolio.keys()))
        
        html = """
        <div id="financials" class="content-section">
            <h2>💰 財務分析</h2>
            
            <div class="discussion-section">
                <h3>主要財務指標比較</h3>
                <table class="optimization-table">
                    <thead>
                        <tr>
                            <th>銘柄</th>
                            <th>時価総額</th>
                            <th>予想PER</th>
                            <th>ROE</th>
                            <th>利益率</th>
                            <th>売上成長率</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        if not comparison_df.empty:
            for ticker in self.portfolio.keys():
                if ticker in comparison_df.index:
                    row = comparison_df.loc[ticker]
                    html += f"""
                        <tr>
                            <td><strong>{ticker}</strong></td>
                            <td>${row.get('marketCap', 0)/1e9:.1f}B</td>
                            <td>{row.get('forwardPE', 'N/A'):.1f}</td>
                            <td>{row.get('returnOnEquity', 0)*100:.1f}%</td>
                            <td>{row.get('profitMargins', 0)*100:.1f}%</td>
                            <td>{row.get('revenueGrowth', 0)*100:.1f}%</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
"""
        return html
    
    def _generate_competitors_section(self) -> str:
        """競合分析セクションを生成"""
        html = """
        <div id="competitors" class="content-section">
            <h2>🏆 競合分析</h2>
"""
        
        for ticker, info in self.portfolio.items():
            competitor_report = self.read_competitor_report(ticker)
            
            if competitor_report:
                # 競合分析の要約を抽出
                summary = competitor_report[:800] + "..." if len(competitor_report) > 800 else competitor_report
                
                html += f"""
                <div class="discussion-section">
                    <h3>{ticker} - 競合比較</h3>
                    <pre style="white-space: pre-wrap; font-family: inherit; font-size: 0.9rem;">{summary}</pre>
                </div>
"""
        
        html += """
        </div>
"""
        return html
    
    def _generate_optimization_section(self) -> str:
        """最適化提案セクションを生成"""
        optimization = self.calculate_portfolio_optimization()
        
        html = """
        <div id="optimization" class="content-section">
            <h2>🎯 ポートフォリオ最適化提案</h2>
            
            <div class="discussion-section">
                <h3>現在配分 vs 推奨配分</h3>
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
"""
        
        for ticker, info in self.portfolio.items():
            current = optimization['current_allocation'][ticker]
            recommended = optimization['recommended_allocation'][ticker]
            change = recommended - current
            risk = optimization['risk_metrics'][ticker]
            
            change_class = "positive" if change > 0 else "negative" if change < 0 else ""
            risk_color = "color: var(--danger-color);" if risk >= 7 else "color: var(--warning-color);" if risk >= 5 else "color: var(--success-color);"
            
            html += f"""
                        <tr>
                            <td><strong>{ticker}</strong></td>
                            <td>{info['sector']}</td>
                            <td>{current}%</td>
                            <td>{recommended}%</td>
                            <td class="{change_class}">{'+' if change > 0 else ''}{change:.1f}%</td>
                            <td style="{risk_color}">{risk}/10</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <div class="discussion-section">
                <h3>💡 最適化の根拠</h3>
                <div class="portfolio-grid">
                    <div class="stock-card">
                        <h4>リスク調整の観点</h4>
                        <p>高リスク銘柄（ASTS、OKLO、LUNR、RDW）の配分を抑制し、
                        安定成長銘柄（TSLA、FSLR）の比重を維持することで、
                        ポートフォリオ全体のリスクを管理します。</p>
                    </div>
                    
                    <div class="stock-card">
                        <h4>成長性の観点</h4>
                        <p>宇宙・航空セクター（RKLB、ASTS、LUNR）は高い成長性を持つため、
                        リスクを考慮しつつも一定の配分を維持し、
                        長期的な成長機会を捉えます。</p>
                    </div>
                    
                    <div class="stock-card">
                        <h4>分散の観点</h4>
                        <p>9つの異なるセクターへの分散により、
                        特定セクターのリスクを軽減しつつ、
                        次世代テクノロジー全体の成長を享受します。</p>
                    </div>
                </div>
            </div>
            
            <div class="discussion-section">
                <h3>📌 結論と推奨アクション</h3>
                <ol>
                    <li><strong>短期（1-3ヶ月）</strong>
                        <ul>
                            <li>現在の配分を維持し、各銘柄の四半期決算を注視</li>
                            <li>特にTSLA、FSLRのコア銘柄の業績動向を重点監視</li>
                        </ul>
                    </li>
                    <li><strong>中期（3-6ヶ月）</strong>
                        <ul>
                            <li>推奨配分に向けた段階的なリバランスを検討</li>
                            <li>高リスク銘柄の進捗を評価し、必要に応じて調整</li>
                        </ul>
                    </li>
                    <li><strong>長期（6ヶ月以上）</strong>
                        <ul>
                            <li>新興テクノロジーの市場成熟度を評価</li>
                            <li>ポートフォリオ全体の戦略的見直しを実施</li>
                        </ul>
                    </li>
                </ol>
            </div>
        </div>
"""
        return html
    
    def save_report(self, output_path: str = None):
        """レポートを保存"""
        if output_path is None:
            output_path = f"reports/html/portfolio_master_report_{self.report_date}.html"
        
        # ディレクトリ作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # HTMLレポート生成
        html_content = self.generate_master_html_report()
        
        # ファイル保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 総合レポート保存完了: {output_path}")
        
        return output_path


def main():
    """メイン実行関数"""
    print("🚀 ポートフォリオ総合マスターレポート生成開始...")
    
    # レポート生成
    generator = PortfolioMasterReport()
    
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