"""
ポートフォリオマスターレポート（最終版）
- 概要ダッシュボード（エントリー判定付き）
- 銘柄別タブ形式
- 4専門家討論レポートに詳細内容を統合
- シナリオ区分の表示改善

実行方法:
    python portfolio_master_report_final.py
"""

import os
import glob
import re
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import warnings
import yfinance as yf

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PortfolioMasterReportFinal:
    """最終版ポートフォリオレポート生成クラス"""
    
    def __init__(self):
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
            "RDW": {"weight": 5, "name": "Redwire", "sector": "宇宙製造", "color": "#e74c3c"}
        }
        
        self.report_date = datetime.now().strftime("%Y-%m-%d")
        
    def read_discussion_report(self, ticker: str) -> Optional[str]:
        """専門家討論レポートを読み込み"""
        try:
            patterns = [
                f"reports/{ticker.upper()}_discussion_*.md",
                f"reports/{ticker.lower()}_discussion_*.md"
            ]
            
            report_files = []
            for pattern in patterns:
                report_files.extend(glob.glob(pattern))
                
            if not report_files:
                logger.info(f"{ticker}: 専門家討論レポートが見つかりません")
                return None
                
            latest_file = max(report_files, key=os.path.getmtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            logger.info(f"{ticker}: 専門家討論レポート読み込み成功 - {latest_file}")
            return content
        except Exception as e:
            logger.warning(f"{ticker}: 専門家討論レポート読み込みエラー - {e}")
            return None
    
    def read_detailed_discussion_report(self, ticker: str) -> Optional[str]:
        """詳細討論レポートを読み込み"""
        try:
            patterns = [
                f"reports/detailed_discussions/{ticker.upper()}_detailed_analysis_*.md",
                f"reports/detailed_discussions/{ticker.lower()}_detailed_analysis_*.md"
            ]
            
            report_files = []
            for pattern in patterns:
                report_files.extend(glob.glob(pattern))
                
            if not report_files:
                logger.info(f"{ticker}: 詳細討論レポートが見つかりません")
                return None
                
            latest_file = max(report_files, key=os.path.getmtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            logger.info(f"{ticker}: 詳細討論レポート読み込み成功 - {latest_file}")
            return content
        except Exception as e:
            logger.warning(f"{ticker}: 詳細討論レポート読み込みエラー - {e}")
            return None
    
    def extract_expert_scores(self, report: str) -> Dict[str, float]:
        """レポートから専門家スコアを抽出"""
        scores = {
            'TECH': 3.0,
            'FUND': 3.0,
            'MACRO': 3.0,
            'RISK': 3.0,
            'OVERALL': 3.0
        }
        
        try:
            # スコアパターンを検索
            patterns = {
                'TECH': r'TECH.*?総合スコア:\s*(\d+\.?\d*)★/5',
                'FUND': r'FUND.*?総合スコア:\s*(\d+\.?\d*)★/5',
                'MACRO': r'MACRO.*?総合スコア:\s*(\d+\.?\d*)★/5',
                'RISK': r'RISK.*?総合スコア:\s*(\d+\.?\d*)★/5',
            }
            
            for expert, pattern in patterns.items():
                match = re.search(pattern, report, re.DOTALL)
                if match:
                    scores[expert] = float(match.group(1))
            
            # 総合スコア計算
            scores['OVERALL'] = sum(scores[k] for k in ['TECH', 'FUND', 'MACRO', 'RISK']) / 4.0
            
        except Exception as e:
            logger.warning(f"スコア抽出エラー: {e}")
        
        return scores
    
    def extract_entry_judgment(self, report: str) -> Tuple[str, str]:
        """レポートからエントリー判定を抽出"""
        try:
            # エントリー判定パターン
            judgment_match = re.search(r'【総合判定】(.+?)(?:\n|$)', report)
            if judgment_match:
                judgment = judgment_match.group(1).strip()
            else:
                # 別のパターンを試す
                judgment_match = re.search(r'エントリー判定[:\s]*(.+?)(?:\n|$)', report)
                if judgment_match:
                    judgment = judgment_match.group(1).strip()
                else:
                    judgment = "不明"
            
            # 推奨理由パターン
            reason_match = re.search(r'推奨理由[:\s]*(.+?)(?:\n|$)', report)
            if reason_match:
                reason = reason_match.group(1).strip()
            else:
                reason = ""
            
            return judgment, reason
        except Exception as e:
            logger.warning(f"エントリー判定抽出エラー: {e}")
            return "不明", ""
    
    def get_current_price(self, ticker: str) -> Tuple[float, float]:
        """現在の株価と変化率を取得"""
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(period="2d")
            if len(history) >= 2:
                current_price = history['Close'].iloc[-1]
                prev_close = history['Close'].iloc[-2]
                change_pct = ((current_price - prev_close) / prev_close) * 100
                return current_price, change_pct
            else:
                return 0.0, 0.0
        except Exception as e:
            logger.warning(f"{ticker}: 株価取得エラー - {e}")
            return 0.0, 0.0
    
    def markdown_to_html(self, text: str) -> str:
        """MarkdownをHTMLに変換（改善版）"""
        if not text:
            return ""
        
        # HTMLエスケープ
        html = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # テーブルの処理（先に行う）
        def process_table(match):
            table_text = match.group(0)
            lines = table_text.strip().split('\n')
            if len(lines) < 2:
                return table_text
            
            html_table = '<table class="data-table">\n'
            
            # ヘッダー行
            headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
            html_table += '<thead><tr>\n'
            for header in headers:
                html_table += f'<th>{header}</th>\n'
            html_table += '</tr></thead>\n<tbody>\n'
            
            # データ行（区切り行をスキップ）
            for line in lines[2:]:
                if line.strip() and not line.startswith('|:'):
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    html_table += '<tr>\n'
                    for cell in cells:
                        # 強調表示の処理
                        cell = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', cell)
                        html_table += f'<td>{cell}</td>\n'
                    html_table += '</tr>\n'
            
            html_table += '</tbody></table>\n'
            return html_table
        
        # テーブルを先に変換
        html = re.sub(r'\|[^\n]+\|(?:\n\|[:\-\|]+\|)?(?:\n\|[^\n]+\|)*', process_table, html, flags=re.MULTILINE)
        
        # ヘッダー変換
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # 太字（テーブル以外）
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # リスト項目
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # 改行処理（連続する改行は段落に）
        html = re.sub(r'\n\n+', '</p><p>', html)
        html = re.sub(r'\n', '<br>\n', html)
        html = f'<p>{html}</p>'
        
        # 空の段落を削除
        html = re.sub(r'<p>\s*</p>', '', html)
        
        return html
    
    def generate_dashboard_section(self) -> str:
        """概要ダッシュボードセクションを生成"""
        dashboard_html = """
        <div class="dashboard-section">
            <h2>📊 ポートフォリオ概要ダッシュボード</h2>
            <div class="portfolio-overview">
                <div class="overview-grid">
        """
        
        # 各銘柄のサマリーカードを生成
        for ticker, info in self.portfolio.items():
            # レポート読み込み
            discussion_report = self.read_discussion_report(ticker)
            detailed_report = self.read_detailed_discussion_report(ticker)
            
            # データ抽出
            scores = self.extract_expert_scores(discussion_report or detailed_report or "")
            judgment, reason = self.extract_entry_judgment(discussion_report or detailed_report or "")
            current_price, change_pct = self.get_current_price(ticker)
            
            # エントリー判定の色分け
            judgment_color = "#28a745"  # デフォルト: 緑
            if "待ち" in judgment or "様子見" in judgment:
                judgment_color = "#ffc107"  # 黄色
            elif "見送り" in judgment or "売り" in judgment:
                judgment_color = "#dc3545"  # 赤
            
            # 変化率の色分け
            change_color = "#28a745" if change_pct >= 0 else "#dc3545"
            
            dashboard_html += f"""
                <div class="stock-card" onclick="showStockTab('{ticker.lower()}')">
                    <div class="card-header" style="background-color: {info['color']}">
                        <h3>{ticker}</h3>
                        <span class="allocation">{info['weight']}%</span>
                    </div>
                    <div class="card-body">
                        <div class="stock-name">{info['name']}</div>
                        <div class="stock-sector">{info['sector']}</div>
                        <div class="price-info">
                            <span class="current-price">${current_price:.2f}</span>
                            <span class="price-change" style="color: {change_color}">
                                {'+' if change_pct >= 0 else ''}{change_pct:.2f}%
                            </span>
                        </div>
                        <div class="scores">
                            <div class="score-item">
                                <span class="score-label">総合</span>
                                <span class="score-value">{scores['OVERALL']:.1f}</span>
                            </div>
                            <div class="score-stars">{'★' * int(scores['OVERALL'])}</div>
                        </div>
                        <div class="entry-judgment" style="background-color: {judgment_color}">
                            {judgment}
                        </div>
                    </div>
                </div>
            """
        
        dashboard_html += """
                </div>
            </div>
        </div>
        """
        
        return dashboard_html
    
    def generate_stock_section(self, ticker: str) -> str:
        """個別銘柄セクションを生成"""
        ticker_lower = ticker.lower()
        stock_info = self.portfolio[ticker]
        
        # レポート読み込み
        discussion_report = self.read_discussion_report(ticker)
        detailed_report = self.read_detailed_discussion_report(ticker)
        
        # 専門家スコア抽出
        scores = self.extract_expert_scores(discussion_report or detailed_report or "")
        
        # 詳細レポートに専門家スコアを先頭に追加
        if detailed_report:
            score_summary = f"""
## 📊 4専門家評価スコア

| 専門家 | スコア | 評価 |
|--------|--------|------|
| TECH | {scores['TECH']:.1f}/5.0 | {'★' * int(scores['TECH'])} |
| FUND | {scores['FUND']:.1f}/5.0 | {'★' * int(scores['FUND'])} |
| MACRO | {scores['MACRO']:.1f}/5.0 | {'★' * int(scores['MACRO'])} |
| RISK | {scores['RISK']:.1f}/5.0 | {'★' * int(scores['RISK'])} |
| **総合** | **{scores['OVERALL']:.1f}/5.0** | **{'★' * int(scores['OVERALL'])}** |

---

"""
            # 詳細レポートの先頭にスコアを追加
            detailed_report = score_summary + detailed_report
        
        html = f"""
        <div class="stock-tab-content" id="{ticker_lower}-content" style="display: none;">
            <div class="stock-header-info">
                <h2 style="color: {stock_info['color']}">{ticker} - {stock_info['name']}</h2>
                <div class="stock-meta">
                    <span class="sector-badge">{stock_info['sector']}</span>
                    <span class="weight-badge">{stock_info['weight']}%</span>
                </div>
            </div>
            
            <!-- 4専門家討論レポート -->
            <div class="analysis-section">
                <h3>🎯 4専門家討論レポート</h3>
                <div class="report-content">
                    {self.markdown_to_html(detailed_report or "詳細レポートが見つかりません")}
                </div>
            </div>
        </div>
        """
        
        return html
    
    def generate_html_report(self) -> str:
        """完全なHTMLレポートを生成"""
        # ダッシュボード生成
        dashboard_html = self.generate_dashboard_section()
        
        # 銘柄タブ生成
        stock_tabs = ""
        stock_contents = ""
        
        for i, ticker in enumerate(self.portfolio):
            active_class = "active" if i == 0 else ""
            stock_tabs += f"""
                <button class="stock-tab {active_class}" onclick="showStockTab('{ticker.lower()}')" id="{ticker.lower()}-tab">
                    {ticker}
                </button>
            """
            stock_contents += self.generate_stock_section(ticker)
        
        # 最初の銘柄を表示
        first_ticker = list(self.portfolio.keys())[0].lower()
        
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tiker ポートフォリオ分析レポート - {self.report_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        /* ダッシュボードセクション */
        .dashboard-section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .dashboard-section h2 {{
            color: #4a5568;
            margin-bottom: 25px;
            font-size: 1.8em;
        }}
        
        .overview-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .stock-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .stock-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}
        
        .card-header {{
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .card-header h3 {{
            font-size: 1.3em;
            margin: 0;
        }}
        
        .allocation {{
            background: rgba(255,255,255,0.2);
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        
        .card-body {{
            padding: 20px;
        }}
        
        .stock-name {{
            font-weight: 600;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        
        .stock-sector {{
            color: #718096;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        
        .price-info {{
            display: flex;
            align-items: baseline;
            gap: 10px;
            margin-bottom: 15px;
        }}
        
        .current-price {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .price-change {{
            font-size: 1.1em;
            font-weight: 500;
        }}
        
        .scores {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .score-item {{
            display: flex;
            gap: 5px;
            align-items: center;
        }}
        
        .score-label {{
            color: #718096;
            font-size: 0.9em;
        }}
        
        .score-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .score-stars {{
            color: #ffd700;
            font-size: 1.1em;
        }}
        
        .entry-judgment {{
            text-align: center;
            padding: 8px;
            border-radius: 5px;
            color: white;
            font-weight: 600;
            font-size: 0.95em;
        }}
        
        /* タブセクション */
        .tabs-section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .stock-tabs {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: -2px;
        }}
        
        .stock-tab {{
            padding: 10px 20px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            color: #718096;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
            margin-bottom: -2px;
        }}
        
        .stock-tab:hover {{
            color: #4a5568;
            background: #f7fafc;
        }}
        
        .stock-tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: 600;
        }}
        
        /* 銘柄コンテンツ */
        .stock-tab-content {{
            animation: fadeIn 0.3s;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .stock-header-info {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .stock-header-info h2 {{
            margin-bottom: 10px;
        }}
        
        .stock-meta {{
            display: flex;
            gap: 15px;
        }}
        
        .sector-badge, .weight-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            background: #edf2f7;
            color: #4a5568;
        }}
        
        .analysis-section {{
            margin-top: 30px;
        }}
        
        .analysis-section h3 {{
            color: #4a5568;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .report-content {{
            background: #f7fafc;
            padding: 30px;
            border-radius: 8px;
            max-height: 800px;
            overflow-y: auto;
        }}
        
        /* テーブルスタイル */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .data-table th,
        .data-table td {{
            border: 1px solid #e2e8f0;
            padding: 12px 15px;
            text-align: left;
        }}
        
        .data-table th {{
            background: #edf2f7;
            font-weight: 600;
            color: #4a5568;
        }}
        
        .data-table tr:nth-child(even) {{
            background: #f7fafc;
        }}
        
        .data-table tr:hover {{
            background: #edf2f7;
        }}
        
        /* シナリオ区分の特別スタイル */
        .data-table td:first-child {{
            font-weight: 600;
            color: #4a5568;
        }}
        
        /* レポート内のヘッダー */
        .report-content h1 {{
            color: #2d3748;
            margin: 30px 0 20px;
            font-size: 2em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}
        
        .report-content h2 {{
            color: #4a5568;
            margin: 25px 0 15px;
            font-size: 1.5em;
        }}
        
        .report-content h3 {{
            color: #718096;
            margin: 20px 0 10px;
            font-size: 1.2em;
        }}
        
        .report-content p {{
            margin: 10px 0;
        }}
        
        .report-content li {{
            margin: 5px 0 5px 20px;
        }}
        
        @media print {{
            .stock-tabs {{
                display: none;
            }}
            
            .stock-tab-content {{
                display: block !important;
                page-break-before: always;
            }}
            
            .stock-card {{
                cursor: default;
            }}
        }}
        
        @media (max-width: 768px) {{
            .overview-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stock-tabs {{
                overflow-x: auto;
            }}
        }}
    </style>
    <script>
        function showStockTab(ticker) {{
            // すべてのタブコンテンツを非表示
            document.querySelectorAll('.stock-tab-content').forEach(content => {{
                content.style.display = 'none';
            }});
            
            // すべてのタブボタンから active クラスを削除
            document.querySelectorAll('.stock-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 選択されたタブコンテンツを表示
            const selectedContent = document.getElementById(ticker + '-content');
            if (selectedContent) {{
                selectedContent.style.display = 'block';
            }}
            
            // 選択されたタブボタンに active クラスを追加
            const selectedTab = document.getElementById(ticker + '-tab');
            if (selectedTab) {{
                selectedTab.classList.add('active');
            }}
            
            // タブセクションまでスクロール
            document.querySelector('.tabs-section').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
        
        // ページ読み込み時に最初のタブを表示
        window.onload = function() {{
            showStockTab('{first_ticker}');
        }};
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Tiker ポートフォリオ分析レポート</h1>
            <p>生成日: {self.report_date}</p>
        </div>
        
        {dashboard_html}
        
        <div class="tabs-section">
            <div class="stock-tabs">
                {stock_tabs}
            </div>
            
            {stock_contents}
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def save_report(self, output_path: str = None):
        """レポートを保存"""
        if output_path is None:
            output_path = f"reports/html/portfolio_report_final_{self.report_date}.html"
        
        # ディレクトリ作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # HTMLレポート生成
        html_content = self.generate_html_report()
        
        # ファイル保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 最終版レポート保存完了: {output_path}")
        
        return output_path


def main():
    """メイン実行関数"""
    print("🚀 最終版ポートフォリオレポート生成開始...")
    
    # レポート生成
    generator = PortfolioMasterReportFinal()
    
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