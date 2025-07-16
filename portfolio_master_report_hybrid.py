"""
ハイブリッドポートフォリオレポート生成（Jinja2テンプレート使用）
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
import logging
from concurrent.futures import ThreadPoolExecutor
import time
from jinja2 import Environment, FileSystemLoader, select_autoescape

warnings.filterwarnings("ignore")


class PortfolioMasterReportHybrid:
    """ハイブリッドポートフォリオレポート生成クラス"""
    
    def __init__(self):
        self.config = ConfigManager("config.yaml")
        self.competitor_analyzer = CompetitorAnalysis()
        self.financial_comparison = FinancialComparison()
        self.html_generator = HTMLReportGenerator("config.yaml")
        self.data_manager = StockDataManager(self.config)
        
        # ログ設定
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Jinja2環境設定
        self.env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
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
            report_files = glob.glob(f"reports/{ticker.lower()}_discussion_*.md")
            if not report_files:
                return None
                
            # 最新のファイルを選択
            latest_file = max(report_files, key=os.path.getmtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return content
        except Exception as e:
            self.logger.warning(f"{ticker}: 専門家討論レポート読み込みエラー - {e}")
            return None
    
    def read_competitor_report(self, ticker: str) -> Optional[str]:
        """競合分析レポートを読み込み"""
        try:
            report_files = glob.glob(f"reports/{ticker.lower()}_competitor_*.md")
            if not report_files:
                return None
                
            # 最新のファイルを選択
            latest_file = max(report_files, key=os.path.getmtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return content
        except Exception as e:
            self.logger.warning(f"{ticker}: 競合分析レポート読み込みエラー - {e}")
            return None
    
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
                
            # テンプレートファイルのパス
            template_dir = os.path.join(os.path.dirname(__file__), 'templates')
            
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
                'discussions': {},
                'competitors': {},
                'optimization': self.calculate_portfolio_optimization()
            }
            
            # 各銘柄のメトリクス取得
            for ticker in self.portfolio:
                template_data['stock_metrics'][ticker] = self.get_current_metrics(ticker)
                template_data['financial_metrics'][ticker] = self.get_financial_metrics(ticker)
                template_data['discussions'][ticker] = self.read_discussion_report(ticker)
                template_data['competitors'][ticker] = self.read_competitor_report(ticker)
            
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
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
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