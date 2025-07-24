"""
ポートフォリオ総合マスターレポート生成（簡易版）
依存パッケージを最小限にしたバージョン

実行方法:
    python3 portfolio_master_report_simple.py
"""

import os
import glob
from datetime import datetime
import json


class PortfolioMasterReportSimple:
    """ポートフォリオ総合レポート生成クラス（簡易版）"""
    
    def __init__(self):
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
        
    def read_report_file(self, pattern: str) -> str:
        """レポートファイルを読み込む"""
        files = glob.glob(pattern)
        if files:
            latest_file = max(files)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # HTMLエスケープ
                    content = content.replace('&', '&amp;')
                    content = content.replace('<', '&lt;')
                    content = content.replace('>', '&gt;')
                    return content
            except Exception as e:
                return f"読み込みエラー: {e}"
        return "レポートファイルが見つかりません"
        
    def read_discussion_reports(self) -> dict:
        """討論形式レポートを読み込む"""
        reports = {}
        for ticker in self.portfolio.keys():
            pattern = f"reports/{ticker}_discussion_analysis_*.md"
            content = self.read_report_file(pattern)
            if content:
                reports[ticker] = content[:2000] + "..." if len(content) > 2000 else content
        return reports
        
    def read_competitor_reports(self) -> dict:
        """競合分析レポートを読み込む"""
        reports = {}
        for ticker in self.portfolio.keys():
            pattern = f"reports/competitor_analysis_{ticker}_*.md"
            content = self.read_report_file(pattern)
            if content:
                reports[ticker] = content[:1500] + "..." if len(content) > 1500 else content
        return reports
    
    def calculate_portfolio_optimization(self) -> dict:
        """簡易的なポートフォリオ最適化分析"""
        optimization = {
            'current_allocation': {},
            'recommended_allocation': {},
            'risk_metrics': {},
            'expected_returns': {}
        }
        
        # リスクスコアの設定
        risk_scores = {
            "TSLA": 4, "FSLR": 4, "RKLB": 6, "ASTS": 8,
            "OKLO": 8, "JOBY": 7, "OII": 5, "LUNR": 9, "RDW": 9
        }
        
        # 期待リターンの設定
        expected_returns = {
            "TSLA": 20, "FSLR": 20, "RKLB": 25, "ASTS": 30,
            "OKLO": 25, "JOBY": 25, "OII": 15, "LUNR": 35, "RDW": 30
        }
        
        # 現在の配分と最適化計算
        total_score = 0
        scores = {}
        
        for ticker, info in self.portfolio.items():
            optimization['current_allocation'][ticker] = info['weight']
            optimization['risk_metrics'][ticker] = risk_scores[ticker]
            optimization['expected_returns'][ticker] = expected_returns[ticker]
            
            # スコア = 期待リターン / リスク
            score = expected_returns[ticker] / risk_scores[ticker]
            scores[ticker] = score
            total_score += score
        
        # 推奨配分の計算
        for ticker, score in scores.items():
            recommended_pct = (score / total_score) * 100
            optimization['recommended_allocation'][ticker] = round(recommended_pct, 1)
            
        return optimization
    
    def generate_html_report(self) -> str:
        """HTMLレポートを生成"""
        # レポートデータの読み込み
        discussion_reports = self.read_discussion_reports()
        competitor_reports = self.read_competitor_reports()
        optimization = self.calculate_portfolio_optimization()
        
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
        }}
        
        .content-section.active {{
            display: block;
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
        }}
        
        .report-content {{
            background: var(--bg-color);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 0.9rem;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background: var(--primary-color);
            color: white;
            font-weight: bold;
        }}
        
        tr:hover {{
            background: var(--bg-color);
        }}
        
        .positive {{
            color: var(--success-color);
        }}
        
        .negative {{
            color: var(--danger-color);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ポートフォリオ総合マスターレポート</h1>
            <div>9銘柄の包括的分析と最適化提案 - {self.report_date}</div>
        </div>
        
        <div class="nav-tabs">
            <div class="nav-tab active" onclick="showSection('overview')">概要</div>
            <div class="nav-tab" onclick="showSection('portfolio')">ポートフォリオ構成</div>
            <div class="nav-tab" onclick="showSection('discussions')">専門家討論</div>
            <div class="nav-tab" onclick="showSection('competitors')">競合分析</div>
            <div class="nav-tab" onclick="showSection('optimization')">最適化提案</div>
        </div>
        
        <!-- 概要セクション -->
        <div id="overview" class="content-section active">
            <h2>📊 ポートフォリオ概要</h2>
            
            <div class="portfolio-grid">
                <div class="stock-card">
                    <h3>投資テーマ</h3>
                    <p>次世代テクノロジーへの分散投資</p>
                    <ul>
                        <li>EV・再生可能エネルギー（コア）</li>
                        <li>宇宙・航空（成長）</li>
                        <li>海洋・インフラ（安定）</li>
                    </ul>
                </div>
                
                <div class="stock-card">
                    <h3>リスク管理</h3>
                    <p>段階的なリスク配分</p>
                    <ul>
                        <li>低リスク（40%）: TSLA, FSLR</li>
                        <li>中リスク（50%）: RKLB, ASTS, OKLO, JOBY, OII</li>
                        <li>高リスク（10%）: LUNR, RDW</li>
                    </ul>
                </div>
                
                <div class="stock-card">
                    <h3>投資期間</h3>
                    <p>中長期投資（3-5年）</p>
                    <ul>
                        <li>四半期毎のリバランス</li>
                        <li>年次戦略見直し</li>
                        <li>継続的なモニタリング</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- ポートフォリオ構成セクション -->
        <div id="portfolio" class="content-section">
            <h2>💼 ポートフォリオ構成</h2>
            
            <div class="portfolio-grid">
"""
        
        # 各銘柄のカードを生成
        for ticker, info in self.portfolio.items():
            html_content += f"""
                <div class="stock-card">
                    <div class="stock-header">
                        <span class="stock-ticker">{ticker}</span>
                        <span class="stock-weight">{info['weight']}%</span>
                    </div>
                    <h4>{info['name']}</h4>
                    <p style="color: var(--text-secondary);">{info['sector']}</p>
                </div>
"""
        
        html_content += """
            </div>
        </div>
        
        <!-- 専門家討論セクション -->
        <div id="discussions" class="content-section">
            <h2>🗣️ 専門家討論分析</h2>
"""
        
        # 討論レポートを追加
        for ticker, content in discussion_reports.items():
            info = self.portfolio[ticker]
            html_content += f"""
            <div class="discussion-section">
                <h3>{ticker} - {info['name']}</h3>
                <div class="report-content">{content}</div>
            </div>
"""
        
        html_content += """
        </div>
        
        <!-- 競合分析セクション -->
        <div id="competitors" class="content-section">
            <h2>🏆 競合分析</h2>
"""
        
        # 競合分析レポートを追加
        for ticker, content in competitor_reports.items():
            info = self.portfolio[ticker]
            html_content += f"""
            <div class="discussion-section">
                <h3>{ticker} - 競合比較</h3>
                <div class="report-content">{content}</div>
            </div>
"""
        
        html_content += """
        </div>
        
        <!-- 最適化提案セクション -->
        <div id="optimization" class="content-section">
            <h2>🎯 ポートフォリオ最適化提案</h2>
            
            <div class="discussion-section">
                <h3>現在配分 vs 推奨配分</h3>
                <table>
                    <thead>
                        <tr>
                            <th>銘柄</th>
                            <th>セクター</th>
                            <th>現在配分</th>
                            <th>推奨配分</th>
                            <th>変更幅</th>
                            <th>リスクレベル</th>
                            <th>期待リターン</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # 最適化テーブルを追加
        for ticker, info in self.portfolio.items():
            current = optimization['current_allocation'][ticker]
            recommended = optimization['recommended_allocation'][ticker]
            change = recommended - current
            risk = optimization['risk_metrics'][ticker]
            returns = optimization['expected_returns'][ticker]
            
            change_class = "positive" if change > 0 else "negative" if change < 0 else ""
            
            html_content += f"""
                        <tr>
                            <td><strong>{ticker}</strong></td>
                            <td>{info['sector']}</td>
                            <td>{current}%</td>
                            <td>{recommended}%</td>
                            <td class="{change_class}">{'+' if change > 0 else ''}{change:.1f}%</td>
                            <td>{risk}/10</td>
                            <td>{returns}%</td>
                        </tr>
"""
        
        html_content += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="discussion-section">
                <h3>💡 最適化の根拠と推奨アクション</h3>
                <ol>
                    <li><strong>リスク調整の観点</strong>
                        <ul>
                            <li>高リスク銘柄（LUNR, RDW）の配分を抑制</li>
                            <li>安定成長銘柄（TSLA, FSLR）の比重維持</li>
                        </ul>
                    </li>
                    <li><strong>成長性の観点</strong>
                        <ul>
                            <li>宇宙・航空セクターの高い成長性を活用</li>
                            <li>リスク許容度に応じた配分調整</li>
                        </ul>
                    </li>
                    <li><strong>分散の観点</strong>
                        <ul>
                            <li>9つの異なるセクターへの適切な分散</li>
                            <li>相関の低い銘柄組み合わせ</li>
                        </ul>
                    </li>
                </ol>
            </div>
        </div>
    </div>
    
    <script>
        function showSection(sectionId) {{
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
        }}
    </script>
</body>
</html>
"""
        
        return html_content
    
    def save_report(self, output_path: str = None):
        """レポートを保存"""
        if output_path is None:
            output_path = f"reports/html/portfolio_master_report_{self.report_date}.html"
        
        # ディレクトリ作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # HTMLレポート生成
        html_content = self.generate_html_report()
        
        # ファイル保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 総合レポート保存完了: {output_path}")
        
        return output_path


def main():
    """メイン実行関数"""
    print("🚀 ポートフォリオ総合マスターレポート生成開始...")
    
    # レポート生成
    generator = PortfolioMasterReportSimple()
    
    # レポート保存
    output_path = generator.save_report()
    
    print(f"\n✨ レポート生成完了！")
    print(f"📄 ファイル: {output_path}")
    print(f"\n💡 ブラウザで開いてご確認ください。")


if __name__ == "__main__":
    main()