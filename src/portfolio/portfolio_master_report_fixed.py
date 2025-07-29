"""
ポートフォリオマスターレポート（修正版）
- 4専門家討論レポートセクションは残す
- 詳細4専門家討論レポート（全文）セクションは削除
- 討論レポートの全文タブに専門家スコアを先頭に追加
- タイトルから（全文）を削除

実行方法:
    python portfolio_master_report_fixed.py
"""

import os
import glob
import re
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional
import logging
import warnings

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PortfolioMasterReportFixed:
    """修正版ポートフォリオレポート生成クラス"""
    
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
    
    def extract_expert_scores(self, detailed_report: str) -> Dict[str, float]:
        """詳細レポートから専門家スコアを抽出"""
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
                match = re.search(pattern, detailed_report, re.DOTALL)
                if match:
                    scores[expert] = float(match.group(1))
            
            # 総合スコア計算
            scores['OVERALL'] = sum(scores[k] for k in ['TECH', 'FUND', 'MACRO', 'RISK']) / 4.0
            
        except Exception as e:
            logger.warning(f"スコア抽出エラー: {e}")
        
        return scores
    
    def markdown_to_html(self, text: str) -> str:
        """MarkdownをHTMLに変換（簡易版）"""
        if not text:
            return ""
        
        # HTMLエスケープ
        html = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # ヘッダー変換
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # 太字
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # リスト項目
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # 改行をHTMLに
        html = html.replace('\n', '<br>\n')
        
        return html
    
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
        <div class="stock-section" id="{ticker_lower}-section">
            <h2 class="stock-title" style="background-color: {stock_info['color']}">
                {ticker} - {stock_info['name']} ({stock_info['weight']}%)
            </h2>
            
            <div class="stock-content">
                <!-- 基本情報 -->
                <div class="basic-info">
                    <div class="info-item">
                        <span class="label">セクター:</span>
                        <span class="value">{stock_info['sector']}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">配分:</span>
                        <span class="value">{stock_info['weight']}%</span>
                    </div>
                </div>
                
                <!-- 4専門家討論レポート（詳細レポートの内容を表示） -->
                <div class="analysis-section">
                    <h3>🎯 4専門家討論レポート</h3>
                    <div class="detailed-discussion markdown-content">
                        {self.markdown_to_html(detailed_report or "詳細レポートが見つかりません")}
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def generate_html_report(self) -> str:
        """完全なHTMLレポートを生成"""
        stocks_html = ""
        for ticker in self.portfolio:
            stocks_html += self.generate_stock_section(ticker)
        
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
            max-width: 1200px;
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
        
        .stock-section {{
            background: white;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
        }}
        
        .stock-title {{
            color: white;
            padding: 20px;
            font-size: 1.5em;
            margin: 0;
        }}
        
        .stock-content {{
            padding: 30px;
        }}
        
        .basic-info {{
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .info-item {{
            display: flex;
            gap: 10px;
        }}
        
        .label {{
            font-weight: 600;
            color: #666;
        }}
        
        .value {{
            color: #333;
        }}
        
        .analysis-section {{
            margin-top: 30px;
        }}
        
        .analysis-section h3 {{
            color: #4a5568;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}
        
        .discussion-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .tab-button {{
            padding: 10px 20px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            color: #718096;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }}
        
        .tab-button:hover {{
            color: #4a5568;
        }}
        
        .tab-button.active {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}
        
        .tab-content {{
            display: none;
            padding: 20px;
            background: #f7fafc;
            border-radius: 8px;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .markdown-content {{
            max-height: 800px;
            overflow-y: auto;
        }}
        
        .markdown-content h1 {{
            color: #2d3748;
            margin: 20px 0 15px;
            font-size: 1.8em;
        }}
        
        .markdown-content h2 {{
            color: #4a5568;
            margin: 20px 0 10px;
            font-size: 1.4em;
        }}
        
        .markdown-content h3 {{
            color: #718096;
            margin: 15px 0 10px;
            font-size: 1.2em;
        }}
        
        .markdown-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .markdown-content th,
        .markdown-content td {{
            border: 1px solid #e2e8f0;
            padding: 12px;
            text-align: left;
        }}
        
        .markdown-content th {{
            background: #edf2f7;
            font-weight: 600;
        }}
        
        .markdown-content tr:nth-child(even) {{
            background: #f7fafc;
        }}
        
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #f7fafc;
            padding: 15px;
            border-radius: 5px;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        @media print {{
            .discussion-tabs {{
                display: none;
            }}
            
            .tab-content {{
                display: block !important;
                page-break-inside: avoid;
            }}
        }}
    </style>
    <script>
        function showTab(ticker, tab) {{
            // Hide all tabs for this ticker
            document.querySelectorAll(`#${{ticker}}-full, #${{ticker}}-summary`).forEach(el => {{
                el.classList.remove('active');
            }});
            
            // Remove active class from all buttons in this section
            const section = document.getElementById(`${{ticker}}-section`);
            section.querySelectorAll('.tab-button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(`${{ticker}}-${{tab}}`).classList.add('active');
            
            // Add active class to clicked button
            event.target.classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Tiker ポートフォリオ分析レポート</h1>
            <p>生成日: {self.report_date}</p>
        </div>
        
        {stocks_html}
    </div>
</body>
</html>"""
        
        return html
    
    def save_report(self, output_path: str = None):
        """レポートを保存"""
        if output_path is None:
            output_path = f"reports/html/portfolio_report_fixed_{self.report_date}.html"
        
        # ディレクトリ作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # HTMLレポート生成
        html_content = self.generate_html_report()
        
        # ファイル保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 修正版レポート保存完了: {output_path}")
        
        return output_path


def main():
    """メイン実行関数"""
    print("🚀 修正版ポートフォリオレポート生成開始...")
    
    # レポート生成
    generator = PortfolioMasterReportFixed()
    
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