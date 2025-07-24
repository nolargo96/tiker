"""
ハイブリッドポートフォリオレポート生成（Jinja2テンプレート使用）
全体戦略（概要・最適化）+ 9銘柄別統合タブ構成

実行方法:
    python portfolio_master_report_hybrid.py
"""

import os
import glob
import re
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional
from src.portfolio.competitor_analysis import CompetitorAnalysis
from src.portfolio.financial_comparison_extension import FinancialComparison
from src.visualization.html_report_generator import HTMLReportGenerator
from src.analysis.stock_analyzer_lib import StockDataManager, ConfigManager, TechnicalIndicators
import yfinance as yf
import warnings
import logging
from concurrent.futures import ThreadPoolExecutor
import time
from jinja2 import Environment, FileSystemLoader, select_autoescape

warnings.filterwarnings("ignore")


class PortfolioMasterReportHybrid:
    """ハイブリッドポートフォリオレポート生成クラス"""
    
    def __init__(self):
        self.config = ConfigManager("config/config.yaml")
        self.competitor_analyzer = CompetitorAnalysis()
        self.financial_comparison = FinancialComparison()
        self.html_generator = HTMLReportGenerator("config/config.yaml")
        self.data_manager = StockDataManager(self.config)
        
        # ログ設定
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Jinja2環境設定
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        template_dir = os.path.join(project_root, 'templates')
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # カスタムフィルタ追加
        self.env.filters['extract_expert'] = self._extract_expert_discussion
        self.env.filters['markdown_to_html'] = self._markdown_to_html
        
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
        
        # バッチデータ取得用キャッシュ
        self._batch_data_cache = {}
        self._info_cache = {}
        self._last_fetch_time = None
        
    def fetch_batch_data(self, force_refresh: bool = False) -> bool:
        """全銘柄のデータを一括取得してキャッシュ"""
        # キャッシュが有効かチェック（5分間有効）
        if (not force_refresh and 
            self._last_fetch_time and 
            (time.time() - self._last_fetch_time) < 300):
            return True
            
        self.logger.info("全銘柄のデータを一括取得中...")
        
        try:
            # 全銘柄のティッカーリストを準備
            tickers = list(self.portfolio.keys())
            
            # 並列処理で全銘柄のデータを取得
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(self._fetch_single_stock_data, ticker): ticker for ticker in tickers}
                
                success_count = 0
                for future in futures:
                    ticker = futures[future]
                    try:
                        success, df, info = future.result()
                        if success:
                            self._batch_data_cache[ticker] = df
                            self._info_cache[ticker] = info
                            success_count += 1
                            self.logger.info(f"✓ {ticker}: データ取得成功")
                        else:
                            self.logger.error(f"✗ {ticker}: データ取得失敗")
                    except Exception as e:
                        self.logger.error(f"✗ {ticker}: 並列処理エラー - {e}")
            
            # 成功率をチェック
            success_rate = success_count / len(tickers)
            if success_rate >= 0.7:  # 70%以上成功すれば良しとする
                self._last_fetch_time = time.time()
                self.logger.info(f"一括データ取得完了: {success_count}/{len(tickers)} ({success_rate:.1%})")
                return True
            else:
                self.logger.warning(f"一括データ取得成功率が低い: {success_rate:.1%}")
                return False
                
        except Exception as e:
            self.logger.error(f"一括データ取得エラー: {e}")
            return False
    
    def _fetch_single_stock_data(self, ticker: str) -> tuple:
        """単一銘柄のデータを取得"""
        try:
            stock = yf.Ticker(ticker)
            
            # 1年分のデータを取得
            end_date = datetime.now()
            start_date = end_date - pd.DateOffset(days=365)
            
            df = stock.history(start=start_date, end=end_date)
            if df.empty:
                return False, None, None
            
            # 技術指標を追加
            df = self.data_manager.add_technical_indicators(df)
            
            # 株式情報を取得
            info = stock.info
            
            return True, df, info
            
        except Exception as e:
            self.logger.error(f"{ticker}: 個別データ取得エラー - {e}")
            return False, None, None
    
    def get_current_metrics(self, ticker: str) -> Optional[Dict]:
        """現在の株価と技術指標を取得（キャッシュ使用）"""
        try:
            # キャッシュからデータを取得
            df = self._batch_data_cache.get(ticker)
            info = self._info_cache.get(ticker, {})
            
            if df is None or df.empty:
                self.logger.warning(f"{ticker}: キャッシュにデータが存在しません")
                return None
                
            latest = df.iloc[-1]
            
            # 前日比計算（データが2日分以上ある場合）
            change_pct = 0
            if len(df) >= 2:
                change_pct = ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100)
            
            return {
                'current_price': latest['Close'],
                'change_pct': change_pct,
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
            self.logger.error(f"{ticker}: 現在データ取得エラー - {e}")
            return None
    
    def get_financial_metrics(self, ticker: str) -> Optional[Dict]:
        """財務指標を取得（キャッシュ使用）"""
        try:
            info = self._info_cache.get(ticker, {})
            
            if not info:
                self.logger.warning(f"{ticker}: 財務情報がキャッシュに存在しません")
                return None
            
            return {
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('forwardPE', 'N/A'),
                'roe': info.get('returnOnEquity', 0),
                'profit_margin': info.get('profitMargins', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'gross_margin': info.get('grossMargins', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'book_value': info.get('bookValue', 0)
            }
        except Exception as e:
            self.logger.error(f"{ticker}: 財務データ取得エラー - {e}")
            return None
    
    def read_discussion_report(self, ticker: str) -> Optional[str]:
        """専門家討論レポートを読み込み"""
        try:
            # 複数のパターンでレポートファイルを検索
            patterns = [
                f"reports/{ticker.upper()}_discussion_*.md",
                f"reports/{ticker.lower()}_discussion_*.md",
                f"reports/{ticker.upper()}_analysis_*.md",
                f"reports/{ticker.lower()}_analysis_*.md"
            ]
            
            report_files = []
            for pattern in patterns:
                report_files.extend(glob.glob(pattern))
                
            if not report_files:
                self.logger.info(f"{ticker}: 専門家討論レポートが見つかりません")
                return None
                
            # 最新のファイルを選択
            latest_file = max(report_files, key=os.path.getmtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.logger.info(f"{ticker}: 専門家討論レポート読み込み成功 - {latest_file}")
            return content
        except Exception as e:
            self.logger.warning(f"{ticker}: 専門家討論レポート読み込みエラー - {e}")
            return None
    
    def read_detailed_discussion_report(self, ticker: str) -> Optional[str]:
        """詳細討論レポートを読み込み"""
        try:
            # 詳細討論レポートを検索
            patterns = [
                f"reports/detailed_discussions/{ticker.upper()}_detailed_analysis_*.md",
                f"reports/detailed_discussions/{ticker.lower()}_detailed_analysis_*.md"
            ]
            
            report_files = []
            for pattern in patterns:
                report_files.extend(glob.glob(pattern))
                
            if not report_files:
                self.logger.info(f"{ticker}: 詳細討論レポートが見つかりません")
                return None
                
            # 最新のファイルを選択
            latest_file = max(report_files, key=os.path.getmtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.logger.info(f"{ticker}: 詳細討論レポート読み込み成功 - {latest_file}")
            return content
        except Exception as e:
            self.logger.warning(f"{ticker}: 詳細討論レポート読み込みエラー - {e}")
            return None
    
    def read_competitor_report(self, ticker: str) -> Optional[str]:
        """競合分析レポートを読み込み"""
        try:
            # 複数のパターンでレポートファイルを検索
            patterns = [
                f"reports/competitor_analysis_{ticker.upper()}_*.md",
                f"reports/competitor_analysis_{ticker.lower()}_*.md",
                f"reports/{ticker.upper()}_competitor_*.md",
                f"reports/{ticker.lower()}_competitor_*.md"
            ]
            
            report_files = []
            for pattern in patterns:
                report_files.extend(glob.glob(pattern))
                
            if not report_files:
                self.logger.info(f"{ticker}: 競合分析レポートが見つかりません")
                return None
                
            # 最新のファイルを選択
            latest_file = max(report_files, key=os.path.getmtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.logger.info(f"{ticker}: 競合分析レポート読み込み成功 - {latest_file}")
            return content
        except Exception as e:
            self.logger.warning(f"{ticker}: 競合分析レポート読み込みエラー - {e}")
            return None
    
    def _extract_expert_discussion(self, discussion_text: str, expert_type: str) -> str:
        """特定の専門家の発言を抽出"""
        try:
            if not discussion_text:
                return ""
            
            # 専門家タイプのマッピング
            expert_markers = {
                'TECH': ['【TECH】', 'TECH:', 'テクニカル分析'],
                'FUND': ['【FUND】', 'FUND:', 'ファンダメンタル分析'],
                'MACRO': ['【MACRO】', 'MACRO:', 'マクロ環境'],
                'RISK': ['【RISK】', 'RISK:', 'リスク管理']
            }
            
            if expert_type not in expert_markers:
                return discussion_text
            
            # 該当専門家の発言を抽出
            lines = discussion_text.split('\n')
            extracted_lines = []
            in_expert_section = False
            
            for line in lines:
                # 専門家マーカーを確認
                for marker in expert_markers[expert_type]:
                    if marker in line:
                        in_expert_section = True
                        break
                
                # 他の専門家のマーカーがあれば終了
                for other_expert, markers in expert_markers.items():
                    if other_expert != expert_type:
                        for marker in markers:
                            if marker in line:
                                in_expert_section = False
                                break
                
                if in_expert_section:
                    extracted_lines.append(line)
            
            return '\n'.join(extracted_lines) if extracted_lines else f"{expert_type}専門家の発言が見つかりません"
            
        except Exception as e:
            self.logger.error(f"専門家討論抽出エラー: {e}")
            return discussion_text
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """MarkdownテキストをHTMLに変換（シンプル版）"""
        try:
            if not markdown_text:
                return ""
            
            # 基本的なMarkdown変換
            html = markdown_text
            
            # ヘッダー変換
            html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
            html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
            html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
            
            # 太字
            html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
            
            # リスト項目
            html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
            
            # テーブル（簡易版）
            lines = html.split('\n')
            in_table = False
            new_lines = []
            
            for line in lines:
                if '|' in line and not line.strip().startswith('<'):
                    if not in_table:
                        new_lines.append('<table>')
                        in_table = True
                    
                    # ヘッダー行の判定
                    if ':--' in line:
                        continue
                    
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    if cells:
                        row_html = '<tr>'
                        cell_tag = 'th' if not any('<tr>' in l for l in new_lines[-5:]) else 'td'
                        for cell in cells:
                            row_html += f'<{cell_tag}>{cell}</{cell_tag}>'
                        row_html += '</tr>'
                        new_lines.append(row_html)
                else:
                    if in_table:
                        new_lines.append('</table>')
                        in_table = False
                    new_lines.append(line)
            
            if in_table:
                new_lines.append('</table>')
            
            return '\n'.join(new_lines)
            
        except Exception as e:
            self.logger.error(f"Markdown変換エラー: {e}")
            return markdown_text
    
    def calculate_expert_scores(self, ticker: str) -> Dict:
        """4専門家スコア評価を計算（TECH/FUND/MACRO/RISK）"""
        try:
            # キャッシュからデータを取得
            df = self._batch_data_cache.get(ticker)
            info = self._info_cache.get(ticker, {})
            
            if df is None or df.empty:
                self.logger.warning(f"{ticker}: 専門家スコア計算用データが不足")
                return {
                    'TECH': 3.0, 'FUND': 3.0, 'MACRO': 3.0, 'RISK': 3.0, 'OVERALL': 3.0
                }
            
            latest = df.iloc[-1]
            
            # TECH スコア (1-5点)
            tech_score = 3.0
            if latest['Close'] > latest['EMA20'] > latest['EMA50']:
                tech_score += 1.0
            if latest['RSI'] > 30 and latest['RSI'] < 70:
                tech_score += 0.5
            if latest['Close'] > latest['SMA200']:
                tech_score += 0.5
            tech_score = min(5.0, max(1.0, tech_score))
            
            # FUND スコア (1-5点)
            fund_score = 3.0
            pe_ratio = info.get('trailingPE', 0)
            if pe_ratio > 0 and pe_ratio < 25:
                fund_score += 0.5
            if info.get('revenueGrowth', 0) > 0.1:
                fund_score += 0.5
            if info.get('grossMargins', 0) > 0.2:
                fund_score += 0.5
            if info.get('currentRatio', 0) > 1.5:
                fund_score += 0.5
            fund_score = min(5.0, max(1.0, fund_score))
            
            # MACRO スコア (1-5点) - セクター別調整
            macro_score = 3.0
            sector = self.portfolio.get(ticker, {}).get('sector', '')
            if sector in ['EV・自動運転', 'ソーラーパネル']:
                macro_score += 0.5  # 成長セクター
            elif sector in ['宇宙インフラ', '月面探査']:
                macro_score += 1.0  # 高成長期待
            elif sector in ['衛星通信', 'eVTOL']:
                macro_score += 0.5  # 新興市場
            
            # 市場全体のセンチメント調整
            if latest['Close'] > df['Close'].rolling(50).mean().iloc[-1]:
                macro_score += 0.5
            macro_score = min(5.0, max(1.0, macro_score))
            
            # RISK スコア (1-5点) - 高いほど低リスク
            risk_score = 3.0
            volatility = df['Close'].pct_change().std() * (252**0.5)  # 年率ボラティリティ
            if volatility < 0.3:
                risk_score += 1.0
            elif volatility < 0.5:
                risk_score += 0.5
            elif volatility > 0.8:
                risk_score -= 1.0
            
            # 流動性評価
            avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
            if avg_volume > 1000000:
                risk_score += 0.5
            
            risk_score = min(5.0, max(1.0, risk_score))
            
            # 総合スコア
            overall_score = (tech_score + fund_score + macro_score + risk_score) / 4.0
            
            return {
                'TECH': round(tech_score, 1),
                'FUND': round(fund_score, 1),
                'MACRO': round(macro_score, 1),
                'RISK': round(risk_score, 1),
                'OVERALL': round(overall_score, 1)
            }
            
        except Exception as e:
            self.logger.error(f"{ticker}: 専門家スコア計算エラー - {e}")
            return {
                'TECH': 3.0, 'FUND': 3.0, 'MACRO': 3.0, 'RISK': 3.0, 'OVERALL': 3.0
            }
    
    def calculate_portfolio_optimization(self) -> Dict:
        """ポートフォリオ最適化計算"""
        try:
            # 現在の配分
            current_allocation = {ticker: info['weight'] for ticker, info in self.portfolio.items()}
            
            # 推奨配分（リスクベースの調整）
            recommended_allocation = current_allocation.copy()
            
            # リスクメトリクス（1-10スケール）
            risk_metrics = {
                'TSLA': 6, 'FSLR': 5, 'RKLB': 8, 'ASTS': 9, 'OKLO': 8,
                'JOBY': 7, 'OII': 4, 'LUNR': 9, 'RDW': 8
            }
            
            # 高リスク銘柄の配分を微調整
            for ticker, risk in risk_metrics.items():
                if risk >= 8:
                    recommended_allocation[ticker] = max(current_allocation[ticker] - 1, 3)
                elif risk <= 4:
                    recommended_allocation[ticker] = min(current_allocation[ticker] + 1, 25)
            
            # 合計が100%になるように調整
            total = sum(recommended_allocation.values())
            if total != 100:
                adjustment = (100 - total) / len(recommended_allocation)
                for ticker in recommended_allocation:
                    recommended_allocation[ticker] += adjustment
            
            return {
                'current_allocation': current_allocation,
                'recommended_allocation': recommended_allocation,
                'risk_metrics': risk_metrics
            }
            
        except Exception as e:
            self.logger.error(f"ポートフォリオ最適化計算エラー: {e}")
            return {
                'current_allocation': {ticker: info['weight'] for ticker, info in self.portfolio.items()},
                'recommended_allocation': {ticker: info['weight'] for ticker, info in self.portfolio.items()},
                'risk_metrics': {ticker: 5 for ticker in self.portfolio.keys()}
            }
    
    def generate_hybrid_html_report(self) -> str:
        """ハイブリッド形式のHTMLレポートを生成（Jinja2テンプレート使用）"""
        try:
            # 一括データ取得を実行
            if not self.fetch_batch_data():
                self.logger.error("一括データ取得に失敗しました")
                
            # テンプレートファイルのパス（プロジェクトルートのtemplatesディレクトリ）
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            template_dir = os.path.join(project_root, 'templates')
            
            # Jinja2環境設定を使用
            self.env.loader = FileSystemLoader(template_dir)
            
            # メインテンプレート読み込み
            template = self.env.get_template('hybrid_report.html')
            
            # テンプレート用データ準備
            template_data = self._prepare_template_data()
            
            # テンプレート適用
            html_content = template.render(**template_data)
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"HTMLレポート生成エラー: {str(e)}")
            return f"<html><body><h1>レポート生成エラー</h1><p>{str(e)}</p></body></html>"
    
    def _prepare_template_data(self) -> Dict:
        """テンプレート用データを準備"""
        try:
            # 基本データ
            template_data = {
                'report_date': self.report_date,
                'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'portfolio': self.portfolio,
                'sectors': list(set(info['sector'] for info in self.portfolio.values())),
                'stock_metrics': {},
                'financial_metrics': {},
                'discussion_reports': {},
                'detailed_discussion_reports': {},
                'competitor_reports': {},
                'expert_scores': {},
                'optimization': self.calculate_portfolio_optimization()
            }
            
            # 各銘柄のメトリクス取得
            for ticker in self.portfolio:
                template_data['stock_metrics'][ticker] = self.get_current_metrics(ticker)
                template_data['financial_metrics'][ticker] = self.get_financial_metrics(ticker)
                template_data['expert_scores'][ticker] = self.calculate_expert_scores(ticker)
                template_data['discussion_reports'][ticker] = self.read_discussion_report(ticker)
                template_data['detailed_discussion_reports'][ticker] = self.read_detailed_discussion_report(ticker)
                template_data['competitor_reports'][ticker] = self.read_competitor_report(ticker)
                
                self.logger.info(f"{ticker}: データ収集完了")
            
            return template_data
            
        except Exception as e:
            self.logger.error(f"テンプレートデータ準備エラー: {e}")
            return {}
    
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
        
        # CSS、JSファイルをコピー
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        template_dir = os.path.join(project_root, 'templates')
        output_dir = os.path.dirname(output_path)
        
        try:
            import shutil
            shutil.copy(os.path.join(template_dir, 'styles.css'), os.path.join(output_dir, 'styles.css'))
            shutil.copy(os.path.join(template_dir, 'script.js'), os.path.join(output_dir, 'script.js'))
        except Exception as e:
            self.logger.warning(f"CSS/JSファイルコピーエラー: {e}")
        
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