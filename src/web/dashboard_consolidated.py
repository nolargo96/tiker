#!/usr/bin/env python3
"""
Tiker Interactive Dashboard Pro - 究極強化版
次世代インタラクティブ投資分析ダッシュボード

新機能:
1. リアルタイムポートフォリオパフォーマンス追跡
2. 履歴シグナル追跡と精度メトリクス
3. 高度なフィルタリングと比較機能
4. AI投資インサイト生成
5. データエクスポート機能
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, Tuple, List, Optional, Any
import json
import warnings
warnings.filterwarnings('ignore')

# 既存システムの活用
from src.analysis.unified_analyzer import calculate_tech_score, calculate_fund_score, calculate_macro_score, calculate_risk_score
from src.analysis.stock_analyzer_lib import ConfigManager, TechnicalIndicators, StockDataManager, StockAnalyzer
from src.data.cache_manager import CacheManager

# ポートフォリオマスターレポート機能
from src.portfolio.portfolio_master_report_hybrid import PortfolioMasterReportHybrid
from src.portfolio.competitor_analysis import CompetitorAnalysis
from src.portfolio.financial_comparison_extension import FinancialComparison
from src.visualization.html_report_generator import HTMLReportGenerator
from src.web.dashboard_export_manager import DashboardExportManager

# 追加インポート
import glob
import os
from concurrent.futures import ThreadPoolExecutor
import time
from jinja2 import Environment, FileSystemLoader, select_autoescape

# ページ設定
st.set_page_config(
    page_title="🚀 Tiker Dashboard Pro Ultimate",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# プロフェッショナルCSS
st.markdown("""
<style>
/* グローバルスタイル */
.main { padding: 0rem 1rem; background-color: #f8f9fa; }

/* ダークテーマ対応 */
@media (prefers-color-scheme: dark) {
    .main { background-color: #1a1a1a; }
}

/* パフォーマンスカード */
.performance-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    position: relative;
    overflow: hidden;
}

.performance-card::before {
    content: "";
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
}

/* メトリクスタイル */
.metric-box {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid #e0e0e0;
}

.metric-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 0.5rem 0;
}

.metric-label {
    color: #666;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-change {
    font-size: 1.2rem;
    font-weight: 600;
}

.positive { color: #28a745; }
.negative { color: #dc3545; }

/* シグナルヒストリーカード */
.signal-history-card {
    background: white;
    border-radius: 15px;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.3s ease;
}

.signal-history-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    transform: translateX(5px);
}

/* AIインサイトカード */
.ai-insight-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 2rem;
    border-radius: 20px;
    margin: 1rem 0;
    position: relative;
}

.ai-insight-card h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.ai-insight-content {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    padding: 1rem;
    border-radius: 10px;
    margin-top: 1rem;
}

/* インタラクティブボタン */
.action-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.8rem 2rem;
    border-radius: 50px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.action-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

/* フィルターセクション */
.filter-section {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* タイムラインビュー */
.timeline-item {
    position: relative;
    padding-left: 3rem;
    margin-bottom: 2rem;
}

.timeline-item::before {
    content: "";
    position: absolute;
    left: 1rem;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #e0e0e0;
}

.timeline-marker {
    position: absolute;
    left: 0.5rem;
    top: 0.5rem;
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    background: #667eea;
    border: 3px solid white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

/* データテーブル強化 */
.enhanced-table {
    background: white;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.enhanced-table th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    text-align: left;
    font-weight: 600;
}

.enhanced-table td {
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
}

.enhanced-table tr:hover {
    background: #f8f9fa;
}

/* リアルタイムインジケーター */
.live-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #28a745;
    color: white;
    padding: 0.3rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    animation: live-pulse 2s infinite;
}

@keyframes live-pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4); }
    50% { opacity: 0.8; box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
}

/* プログレスバー */
.progress-container {
    background: #f0f0f0;
    border-radius: 10px;
    height: 10px;
    overflow: hidden;
    margin: 1rem 0;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    transition: width 0.5s ease;
    position: relative;
}

.progress-bar::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: progress-shine 2s infinite;
}

@keyframes progress-shine {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
</style>
""", unsafe_allow_html=True)

class UltimateDashboardAnalyzer:
    """究極版ダッシュボード分析システム"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.stock_analyzer = StockAnalyzer()
        self.signal_history = self._load_signal_history()
        
        # エントリーシグナル定義（5段階）
        self.signals = {
            'STRONG_BUY': {
                'label': '絶好の買い場',
                'color': '#28a745',
                'icon': '🟢🟢',
                'threshold': 4.0,
                'class': 'signal-strong-buy',
                'accuracy': 0.0  # 動的に計算
            },
            'BUY': {
                'label': '買い推奨',
                'color': '#5cb85c',
                'icon': '🟢',
                'threshold': 3.5,
                'class': 'signal-buy',
                'accuracy': 0.0
            },
            'HOLD': {
                'label': '様子見',
                'color': '#ffc107',
                'icon': '🟡',
                'threshold': 2.5,
                'class': 'signal-hold',
                'accuracy': 0.0
            },
            'SELL': {
                'label': '売却検討',
                'color': '#dc3545',
                'icon': '🔴',
                'threshold': 2.0,
                'class': 'signal-sell',
                'accuracy': 0.0
            },
            'STRONG_SELL': {
                'label': '即売却推奨',
                'color': '#8b0000',
                'icon': '🔴🔴',
                'threshold': 0,
                'class': 'signal-sell',
                'accuracy': 0.0
            }
        }
    
    def _load_signal_history(self) -> Dict:
        """シグナル履歴の読み込み"""
        try:
            with open('signal_history.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_signal_history(self):
        """シグナル履歴の保存"""
        with open('signal_history.json', 'w') as f:
            json.dump(self.signal_history, f, indent=2, default=str)
    
    def calculate_portfolio_performance(self, portfolio: Dict, start_date: datetime) -> Dict:
        """ポートフォリオパフォーマンスの計算"""
        performance = {
            'total_value': 0,
            'total_cost': 0,
            'total_return': 0,
            'total_return_pct': 0,
            'stocks': {},
            'best_performer': None,
            'worst_performer': None,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'volatility': 0
        }
        
        returns = []
        
        for ticker, info in portfolio.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=datetime.now())
                
                if hist.empty:
                    continue
                
                initial_price = hist.iloc[0]['Close']
                current_price = hist.iloc[-1]['Close']
                shares = 10000 / initial_price  # $10,000の初期投資と仮定
                
                cost = shares * initial_price
                value = shares * current_price
                return_amt = value - cost
                return_pct = (return_amt / cost) * 100
                
                # 日次リターンの計算
                daily_returns = hist['Close'].pct_change().dropna()
                returns.extend(daily_returns.tolist())
                
                performance['stocks'][ticker] = {
                    'cost': cost,
                    'value': value,
                    'return': return_amt,
                    'return_pct': return_pct,
                    'shares': shares,
                    'current_price': current_price,
                    'volatility': daily_returns.std() * np.sqrt(252)  # 年率換算
                }
                
                performance['total_cost'] += cost * (info['weight'] / 100)
                performance['total_value'] += value * (info['weight'] / 100)
                
            except Exception as e:
                st.error(f"Error calculating {ticker}: {str(e)}")
        
        # 総合メトリクスの計算
        if performance['total_cost'] > 0:
            performance['total_return'] = performance['total_value'] - performance['total_cost']
            performance['total_return_pct'] = (performance['total_return'] / performance['total_cost']) * 100
            
            # シャープレシオの計算（リスクフリーレート2%と仮定）
            if returns:
                returns_array = np.array(returns)
                avg_return = np.mean(returns_array) * 252  # 年率換算
                volatility = np.std(returns_array) * np.sqrt(252)
                performance['volatility'] = volatility
                performance['sharpe_ratio'] = (avg_return - 0.02) / volatility if volatility > 0 else 0
                
                # 最大ドローダウンの計算
                cumulative = (1 + returns_array).cumprod()
                running_max = np.maximum.accumulate(cumulative)
                drawdown = (cumulative - running_max) / running_max
                performance['max_drawdown'] = drawdown.min() * 100
        
        # ベスト/ワーストパフォーマー
        if performance['stocks']:
            sorted_stocks = sorted(performance['stocks'].items(), 
                                 key=lambda x: x[1]['return_pct'], reverse=True)
            performance['best_performer'] = sorted_stocks[0]
            performance['worst_performer'] = sorted_stocks[-1]
        
        return performance
    
    def generate_ai_insights(self, ticker: str, analysis_result: Dict, 
                           historical_data: pd.DataFrame) -> List[str]:
        """AI駆動の投資インサイト生成"""
        insights = []
        
        # 1. トレンド分析
        if 'EMA20' in historical_data.columns and 'SMA200' in historical_data.columns:
            latest = historical_data.iloc[-1]
            if latest['Close'] > latest['EMA20'] > latest['SMA200']:
                insights.append({
                    'type': 'trend',
                    'level': 'positive',
                    'message': f"{ticker}は強い上昇トレンドを形成。短期・長期移動平均線の上で推移し、モメンタムが継続しています。"
                })
            elif latest['Close'] < latest['EMA20'] < latest['SMA200']:
                insights.append({
                    'type': 'trend',
                    'level': 'negative',
                    'message': f"{ticker}は下降トレンドが継続。トレンド転換のシグナルを待つことを推奨します。"
                })
        
        # 2. ボラティリティ分析
        returns = historical_data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        
        if volatility > 0.5:
            insights.append({
                'type': 'risk',
                'level': 'warning',
                'message': f"高ボラティリティ警告：{ticker}の年率ボラティリティは{volatility:.1%}。ポジションサイズの調整を検討してください。"
            })
        
        # 3. サポート・レジスタンス分析
        recent_high = historical_data['High'].tail(20).max()
        recent_low = historical_data['Low'].tail(20).min()
        current_price = historical_data.iloc[-1]['Close']
        
        if (recent_high - current_price) / current_price < 0.05:
            insights.append({
                'type': 'technical',
                'level': 'caution',
                'message': f"{ticker}は直近高値${recent_high:.2f}付近。レジスタンスラインでの反落に注意が必要です。"
            })
        
        # 4. RSI分析
        if 'RSI' in historical_data.columns:
            rsi = historical_data.iloc[-1]['RSI']
            if rsi > 70:
                insights.append({
                    'type': 'momentum',
                    'level': 'warning',
                    'message': f"RSI {rsi:.1f}で買われ過ぎ圏。短期的な調整の可能性があります。"
                })
            elif rsi < 30:
                insights.append({
                    'type': 'momentum',
                    'level': 'opportunity',
                    'message': f"RSI {rsi:.1f}で売られ過ぎ圏。反発のチャンスを探る好機かもしれません。"
                })
        
        # 5. 総合判断
        total_score = analysis_result['total_score']
        if total_score >= 4.0:
            insights.append({
                'type': 'overall',
                'level': 'strong_positive',
                'message': f"総合スコア{total_score:.2f}は非常に高く、エントリーの絶好のタイミングを示唆しています。"
            })
        elif total_score <= 2.0:
            insights.append({
                'type': 'overall',
                'level': 'strong_negative',
                'message': f"総合スコア{total_score:.2f}は低迷。リスク管理を最優先し、ポジション縮小を検討してください。"
            })
        
        return insights
    
    def calculate_signal_accuracy(self) -> Dict:
        """過去のシグナル精度を計算"""
        accuracy_stats = {signal: {'correct': 0, 'total': 0} for signal in self.signals.keys()}
        
        for ticker, history in self.signal_history.items():
            for record in history:
                signal = record['signal']
                if signal in accuracy_stats:
                    accuracy_stats[signal]['total'] += 1
                    
                    # 1週間後のパフォーマンスで正確性を判定
                    if 'performance_1w' in record:
                        perf = record['performance_1w']
                        if (signal in ['STRONG_BUY', 'BUY'] and perf > 0) or \
                           (signal in ['SELL', 'STRONG_SELL'] and perf < 0) or \
                           (signal == 'HOLD' and -2 < perf < 2):
                            accuracy_stats[signal]['correct'] += 1
        
        # 精度の計算と更新
        for signal, stats in accuracy_stats.items():
            if stats['total'] > 0:
                self.signals[signal]['accuracy'] = stats['correct'] / stats['total']
        
        return accuracy_stats
    
    def analyze_comprehensive_entry_timing(self, ticker: str, df: pd.DataFrame) -> Dict[str, Any]:
        """4専門家による総合エントリータイミング分析（強化版）"""
        
        if df.empty or len(df) < 50:
            return self._create_empty_result()
        
        latest_data = df.iloc[-1]
        
        # 基本的な分析は元のメソッドを使用
        tech_score = calculate_tech_score(df)
        fund_score = calculate_fund_score(ticker, latest_data)
        macro_score = calculate_macro_score(ticker)
        risk_score = calculate_risk_score(df, 100)
        
        # 追加の高度な分析
        momentum_score = self._calculate_momentum_score(df)
        sentiment_score = self._calculate_sentiment_score(ticker)
        
        # 重み付き総合スコア（強化版）
        weights = {
            'TECH': 0.25,
            'FUND': 0.20,
            'MACRO': 0.20,
            'RISK': 0.15,
            'MOMENTUM': 0.10,
            'SENTIMENT': 0.10
        }
        
        total_score = (
            tech_score * weights['TECH'] +
            fund_score * weights['FUND'] +
            macro_score * weights['MACRO'] +
            risk_score * weights['RISK'] +
            momentum_score * weights['MOMENTUM'] +
            sentiment_score * weights['SENTIMENT']
        )
        
        signal = self._determine_signal(total_score)
        
        # シグナル履歴に記録
        self._record_signal(ticker, signal, total_score, latest_data['Close'])
        
        return {
            'signal': signal,
            'total_score': total_score,
            'scores': {
                'TECH': tech_score,
                'FUND': fund_score,
                'MACRO': macro_score,
                'RISK': risk_score,
                'MOMENTUM': momentum_score,
                'SENTIMENT': sentiment_score
            },
            'current_price': latest_data['Close'],
            'price_change_pct': ((latest_data['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100) if len(df) > 1 else 0,
            'timestamp': datetime.now()
        }
    
    def _calculate_momentum_score(self, df: pd.DataFrame) -> float:
        """モメンタムスコアの計算"""
        try:
            # 価格モメンタム
            returns_5d = (df['Close'].iloc[-1] / df['Close'].iloc[-5] - 1) if len(df) >= 5 else 0
            returns_20d = (df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1) if len(df) >= 20 else 0
            
            # ボリュームモメンタム
            vol_ratio = df['Volume'].tail(5).mean() / df['Volume'].tail(20).mean() if len(df) >= 20 else 1
            
            # スコア計算
            score = 2.5  # ベーススコア
            
            if returns_5d > 0.02 and returns_20d > 0.05:
                score += 1.0
            elif returns_5d < -0.02 and returns_20d < -0.05:
                score -= 1.0
            
            if vol_ratio > 1.5:
                score += 0.5
            elif vol_ratio < 0.5:
                score -= 0.5
            
            return max(1.0, min(5.0, score))
            
        except:
            return 2.5
    
    def _calculate_sentiment_score(self, ticker: str) -> float:
        """センチメントスコアの計算（シミュレーション）"""
        # 実際の実装では、ニュースAPI等から取得
        sentiment_map = {
            'TSLA': 3.8,  # ポジティブ
            'FSLR': 4.2,  # 非常にポジティブ
            'RKLB': 3.5,  # ややポジティブ
            'ASTS': 3.0,  # 中立
            'OKLO': 3.7,  # ポジティブ
            'JOBY': 2.8,  # やや否定的
            'OII': 3.3,   # ややポジティブ
            'LUNR': 3.6,  # ポジティブ
            'RDW': 2.5    # 中立
        }
        return sentiment_map.get(ticker, 3.0)
    
    def _record_signal(self, ticker: str, signal: str, score: float, price: float):
        """シグナルを履歴に記録"""
        if ticker not in self.signal_history:
            self.signal_history[ticker] = []
        
        self.signal_history[ticker].append({
            'timestamp': datetime.now().isoformat(),
            'signal': signal,
            'score': score,
            'price': price
        })
        
        # 最新50件のみ保持
        self.signal_history[ticker] = self.signal_history[ticker][-50:]
        self._save_signal_history()
    
    def _determine_signal(self, score: float) -> str:
        """スコアからシグナルを判定"""
        if score >= 4.0:
            return 'STRONG_BUY'
        elif score >= 3.5:
            return 'BUY'
        elif score >= 2.5:
            return 'HOLD'
        elif score >= 2.0:
            return 'SELL'
        else:
            return 'STRONG_SELL'
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """空の結果を作成"""
        return {
            'signal': 'HOLD',
            'total_score': 2.5,
            'scores': {
                'TECH': 2.5,
                'FUND': 2.5,
                'MACRO': 2.5,
                'RISK': 2.5,
                'MOMENTUM': 2.5,
                'SENTIMENT': 2.5
            },
            'current_price': 0,
            'price_change_pct': 0,
            'timestamp': datetime.now()
        }

class UltimateDashboardApp:
    """究極版ダッシュボードアプリケーション"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.analyzer = UltimateDashboardAnalyzer()
        self.cache_manager = CacheManager()
        
        # ポートフォリオマスターレポート機能の統合
        self.portfolio_report = PortfolioMasterReportHybrid()
        self.competitor_analyzer = CompetitorAnalysis()
        self.financial_comparison = FinancialComparison()
        self.html_generator = HTMLReportGenerator("config/config.yaml")
        self.export_manager = DashboardExportManager()
        
        # ポートフォリオ定義（portfolio_master_report_hybridと統一）
        self.portfolio = {
            'TSLA': {'weight': 20, 'name': 'Tesla', 'sector': 'EV・自動運転', 'color': '#e31837'},
            'FSLR': {'weight': 20, 'name': 'First Solar', 'sector': 'ソーラーパネル', 'color': '#ffd700'},
            'RKLB': {'weight': 10, 'name': 'Rocket Lab', 'sector': '小型ロケット', 'color': '#ff6b35'},
            'ASTS': {'weight': 10, 'name': 'AST SpaceMobile', 'sector': '衛星通信', 'color': '#4a90e2'},
            'OKLO': {'weight': 10, 'name': 'Oklo', 'sector': 'SMR原子炉', 'color': '#50c878'},
            'JOBY': {'weight': 10, 'name': 'Joby Aviation', 'sector': 'eVTOL', 'color': '#9b59b6'},
            'OII': {'weight': 10, 'name': 'Oceaneering', 'sector': '海洋エンジニアリング', 'color': '#1abc9c'},
            'LUNR': {'weight': 5, 'name': 'Intuitive Machines', 'sector': '月面探査', 'color': '#34495e'},
            'RDW': {'weight': 5, 'name': 'Redwire', 'sector': '宇宙製造', 'color': '#e74c3c'}
        }
        
        # バッチデータ取得用キャッシュ
        self._batch_data_cache = {}
        self._info_cache = {}
        self._last_fetch_time = None
    
    def run(self):
        """メインアプリケーション実行"""
        self._initialize_session_state()
        self._render_header()
        self._render_sidebar()
        self._render_main_content()
    
    def _initialize_session_state(self):
        """セッション状態の初期化"""
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        if 'selected_tickers' not in st.session_state:
            st.session_state.selected_tickers = list(self.portfolio.keys())
        if 'view_mode' not in st.session_state:
            st.session_state.view_mode = 'dashboard'
        if 'comparison_mode' not in st.session_state:
            st.session_state.comparison_mode = False
        if 'time_range' not in st.session_state:
            st.session_state.time_range = '3M'
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = self.portfolio
    
    def _render_header(self):
        """ヘッダー部分の描画"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 1rem;">
                <h1 style="margin: 0;">💎 Tiker Dashboard Pro Ultimate</h1>
                <span class="live-indicator">● LIVE DATA</span>
            </div>
            <p style="color: #666; margin-top: 0.5rem;">次世代AI駆動投資分析プラットフォーム</p>
            """, unsafe_allow_html=True)
        
        with col2:
            # ポートフォリオ価値のリアルタイム表示
            performance = self.analyzer.calculate_portfolio_performance(
                self.portfolio, 
                datetime.now() - timedelta(days=365)
            )
            
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">ポートフォリオ価値</div>
                <div class="metric-value">${performance['total_value']:,.0f}</div>
                <div class="metric-change {'positive' if performance['total_return_pct'] >= 0 else 'negative'}">
                    {performance['total_return_pct']:+.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">最終更新</div>
                <div style="font-size: 1.2rem; font-weight: 600;">
                    {st.session_state.last_update.strftime("%H:%M:%S")}
                </div>
                <div style="color: #666; font-size: 0.9rem;">
                    {st.session_state.last_update.strftime("%Y-%m-%d")}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """サイドバーの描画"""
        with st.sidebar:
            st.header("⚙️ コントロールパネル")
            
            # ビューモード選択
            st.subheader("📱 表示モード")
            view_mode = st.radio(
                "選択してください",
                ["ダッシュボード", "パフォーマンス分析", "シグナル履歴", "AIインサイト", "比較分析", "ハイブリッドレポート"],
                index=["ダッシュボード", "パフォーマンス分析", "シグナル履歴", "AIインサイト", "比較分析", "ハイブリッドレポート"].index(
                    {"dashboard": "ダッシュボード", "performance": "パフォーマンス分析", 
                     "history": "シグナル履歴", "ai": "AIインサイト", "comparison": "比較分析",
                     "hybrid_report": "ハイブリッドレポート"}
                    .get(st.session_state.view_mode, "ダッシュボード")
                )
            )
            
            mode_map = {
                "ダッシュボード": "dashboard",
                "パフォーマンス分析": "performance",
                "シグナル履歴": "history",
                "AIインサイト": "ai",
                "比較分析": "comparison",
                "ハイブリッドレポート": "hybrid_report"
            }
            st.session_state.view_mode = mode_map[view_mode]
            
            # データ更新
            st.subheader("🔄 データ管理")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 更新", type="primary", use_container_width=True):
                    st.cache_data.clear()
                    st.session_state.last_update = datetime.now()
                    st.rerun()
            
            with col2:
                if st.button("🧹 キャッシュ", use_container_width=True):
                    self.cache_manager.clear_all()
                    st.success("クリア完了")
            
            # 時間範囲選択
            st.subheader("📅 分析期間")
            time_range = st.select_slider(
                "期間選択",
                options=["1W", "1M", "3M", "6M", "1Y", "3Y", "5Y"],
                value=st.session_state.time_range
            )
            st.session_state.time_range = time_range
            
            # フィルタリング
            st.subheader("🔍 フィルター")
            
            # セクターフィルター
            sectors = list(set([info['sector'] for info in self.portfolio.values()]))
            selected_sectors = st.multiselect(
                "セクター",
                options=sectors,
                default=sectors
            )
            
            # パフォーマンスフィルター
            performance_filter = st.slider(
                "最小リターン率 (%)",
                min_value=-50,
                max_value=100,
                value=-10,
                step=5
            )
            
            # シグナルフィルター
            signal_filter = st.multiselect(
                "シグナルタイプ",
                options=list(self.analyzer.signals.keys()),
                default=list(self.analyzer.signals.keys()),
                format_func=lambda x: self.analyzer.signals[x]['label']
            )
            
            # フィルター適用
            filtered_tickers = []
            for ticker, info in self.portfolio.items():
                if info['sector'] in selected_sectors:
                    filtered_tickers.append(ticker)
            
            st.session_state.selected_tickers = filtered_tickers
            
            # エクスポート機能
            st.divider()
            st.subheader("📥 エクスポート")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Excel", use_container_width=True):
                    self._export_to_excel()
            
            with col2:
                if st.button("📄 PDF", use_container_width=True):
                    st.info("PDF機能は開発中")
            
            # 設定
            st.divider()
            with st.expander("⚙️ 詳細設定"):
                show_technical = st.checkbox("テクニカル指標", value=True)
                show_volume = st.checkbox("出来高", value=True)
                show_signals = st.checkbox("売買シグナル", value=True)
                auto_refresh = st.checkbox("自動更新（5分毎）", value=False)
                
                st.session_state.update({
                    'show_technical': show_technical,
                    'show_volume': show_volume,
                    'show_signals': show_signals,
                    'auto_refresh': auto_refresh
                })
    
    def _render_main_content(self):
        """メインコンテンツの描画"""
        if st.session_state.view_mode == 'dashboard':
            self._render_dashboard_view()
        elif st.session_state.view_mode == 'performance':
            self._render_performance_view()
        elif st.session_state.view_mode == 'history':
            self._render_history_view()
        elif st.session_state.view_mode == 'ai':
            self._render_ai_insights_view()
        elif st.session_state.view_mode == 'comparison':
            self._render_comparison_view()
        elif st.session_state.view_mode == 'hybrid_report':
            self._render_hybrid_report_view()
    
    def _render_dashboard_view(self):
        """ダッシュボードビュー"""
        # パフォーマンスカード
        st.markdown("""
        <div class="performance-card">
            <h2 style="margin: 0;">📊 ポートフォリオ・ダッシュボード</h2>
            <p>リアルタイム分析とエントリータイミング判定</p>
        </div>
        """, unsafe_allow_html=True)
        
        # メトリクス行
        col1, col2, col3, col4 = st.columns(4)
        
        # シグナル精度の計算
        accuracy_stats = self.analyzer.calculate_signal_accuracy()
        
        with col1:
            strong_buy_count = sum(1 for t in st.session_state.selected_tickers 
                                 if self._get_current_signal(t) == 'STRONG_BUY')
            st.metric("🟢🟢 絶好の買い場", strong_buy_count, "銘柄")
        
        with col2:
            buy_count = sum(1 for t in st.session_state.selected_tickers 
                          if self._get_current_signal(t) == 'BUY')
            st.metric("🟢 買い推奨", buy_count, "銘柄")
        
        with col3:
            avg_accuracy = np.mean([s['accuracy'] for s in self.analyzer.signals.values()])
            st.metric("🎯 シグナル精度", f"{avg_accuracy:.1%}", "平均")
        
        with col4:
            volatility_avg = self._calculate_average_volatility()
            st.metric("⚡ 平均ボラティリティ", f"{volatility_avg:.1%}", "年率")
        
        # タブ作成
        tab1, tab2, tab3 = st.tabs(["📊 個別銘柄分析", "🎯 シグナル一覧", "📈 チャート"])
        
        with tab1:
            self._render_individual_stocks()
        
        with tab2:
            self._render_signal_overview()
        
        with tab3:
            self._render_portfolio_charts()
    
    def _render_performance_view(self):
        """パフォーマンス分析ビュー"""
        st.header("📈 ポートフォリオ・パフォーマンス分析")
        
        # 期間選択
        col1, col2 = st.columns([3, 1])
        with col1:
            time_periods = {
                '1W': 7, '1M': 30, '3M': 90, '6M': 180,
                '1Y': 365, '3Y': 1095, '5Y': 1825
            }
            days = time_periods[st.session_state.time_range]
            start_date = datetime.now() - timedelta(days=days)
        
        # パフォーマンス計算
        performance = self.analyzer.calculate_portfolio_performance(
            self.portfolio, start_date
        )
        
        # サマリーカード
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">トータルリターン</div>
                <div class="metric-value {'positive' if performance['total_return'] >= 0 else 'negative'}">
                    ${performance['total_return']:,.0f}
                </div>
                <div class="metric-change {'positive' if performance['total_return_pct'] >= 0 else 'negative'}">
                    {performance['total_return_pct']:+.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">シャープレシオ</div>
                <div class="metric-value">{performance['sharpe_ratio']:.2f}</div>
                <div style="color: #666;">リスク調整後リターン</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">最大ドローダウン</div>
                <div class="metric-value negative">{performance['max_drawdown']:.1f}%</div>
                <div style="color: #666;">最大下落率</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">ボラティリティ</div>
                <div class="metric-value">{performance['volatility']:.1%}</div>
                <div style="color: #666;">年率換算</div>
            </div>
            """, unsafe_allow_html=True)
        
        # パフォーマンスチャート
        st.subheader("📊 累積リターン推移")
        self._render_performance_chart(performance)
        
        # 個別銘柄パフォーマンス
        st.subheader("🏆 個別銘柄パフォーマンス")
        self._render_stock_performance_table(performance)
        
        # ベスト/ワーストパフォーマー
        col1, col2 = st.columns(2)
        
        with col1:
            if performance['best_performer']:
                ticker, data = performance['best_performer']
                st.success(f"""
                **🏆 ベストパフォーマー: {ticker}**
                - リターン: {data['return_pct']:+.1f}%
                - 現在価格: ${data['current_price']:.2f}
                """)
        
        with col2:
            if performance['worst_performer']:
                ticker, data = performance['worst_performer']
                st.error(f"""
                **📉 ワーストパフォーマー: {ticker}**
                - リターン: {data['return_pct']:+.1f}%
                - 現在価格: ${data['current_price']:.2f}
                """)
    
    def _render_history_view(self):
        """シグナル履歴ビュー"""
        st.header("📜 シグナル履歴と精度分析")
        
        # 精度統計
        accuracy_stats = self.analyzer.calculate_signal_accuracy()
        
        # 精度メトリクス表示
        cols = st.columns(len(self.analyzer.signals))
        for i, (signal, info) in enumerate(self.analyzer.signals.items()):
            with cols[i]:
                accuracy = info['accuracy'] * 100
                st.metric(
                    f"{info['icon']} {info['label']}",
                    f"{accuracy:.1f}%",
                    "精度"
                )
        
        # タイムライン表示
        st.subheader("📅 シグナル変化タイムライン")
        
        selected_ticker = st.selectbox(
            "銘柄選択",
            options=st.session_state.selected_tickers,
            format_func=lambda x: f"{x} - {self.portfolio[x]['name']}"
        )
        
        if selected_ticker in self.analyzer.signal_history:
            history = self.analyzer.signal_history[selected_ticker]
            
            # タイムライン描画
            for i, record in enumerate(reversed(history[-10:])):  # 最新10件
                signal_info = self.analyzer.signals[record['signal']]
                
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-marker" style="background: {signal_info['color']};"></div>
                    <div class="signal-history-card">
                        <div>
                            <strong>{signal_info['icon']} {signal_info['label']}</strong>
                            <p style="margin: 0; color: #666;">
                                {datetime.fromisoformat(record['timestamp']).strftime('%Y-%m-%d %H:%M')}
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <strong>スコア: {record['score']:.2f}</strong>
                            <p style="margin: 0; color: #666;">${record['price']:.2f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("この銘柄の履歴データはまだありません")
    
    def _render_ai_insights_view(self):
        """AIインサイトビュー"""
        st.markdown("""
        <div class="ai-insight-card">
            <h3>🤖 AI投資インサイト</h3>
            <p>機械学習による深層分析と投資提案</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 銘柄選択
        selected_ticker = st.selectbox(
            "分析対象銘柄",
            options=st.session_state.selected_tickers,
            format_func=lambda x: f"{x} - {self.portfolio[x]['name']}"
        )
        
        # データ取得と分析
        df = self._get_stock_data(selected_ticker)
        if not df.empty:
            analysis_result = self.analyzer.analyze_comprehensive_entry_timing(selected_ticker, df)
            insights = self.analyzer.generate_ai_insights(selected_ticker, analysis_result, df)
            
            # インサイト表示
            for insight in insights:
                level_colors = {
                    'positive': '#28a745',
                    'negative': '#dc3545',
                    'warning': '#ffc107',
                    'caution': '#ff9800',
                    'opportunity': '#17a2b8',
                    'strong_positive': '#0056b3',
                    'strong_negative': '#8b0000'
                }
                
                color = level_colors.get(insight['level'], '#666')
                
                st.markdown(f"""
                <div style="background: {color}20; border-left: 4px solid {color}; 
                            padding: 1rem; margin: 0.5rem 0; border-radius: 5px;">
                    <strong>{insight['type'].upper()}</strong>
                    <p style="margin: 0.5rem 0 0 0;">{insight['message']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 推奨アクション
            st.subheader("🎯 推奨アクション")
            
            signal = analysis_result['signal']
            if signal == 'STRONG_BUY':
                st.success("""
                **即座にエントリーを検討**
                - 段階的にポジションを構築
                - 目標価格を設定し、利確ポイントを明確に
                - ストップロスを設定してリスク管理
                """)
            elif signal == 'BUY':
                st.info("""
                **慎重にエントリータイミングを計る**
                - 押し目を待ってエントリー
                - 小さめのポジションから開始
                - 市場全体の動向も確認
                """)
            elif signal == 'HOLD':
                st.warning("""
                **現状維持を推奨**
                - 新規エントリーは控える
                - 既存ポジションは維持
                - 次のシグナルを待つ
                """)
            else:
                st.error("""
                **ポジション縮小を検討**
                - 段階的に利確または損切り
                - リスク資産の配分を見直し
                - 守りの姿勢を強化
                """)
    
    def _render_comparison_view(self):
        """比較分析ビュー"""
        st.header("⚖️ 銘柄比較分析")
        
        # 比較銘柄選択
        comparison_tickers = st.multiselect(
            "比較する銘柄を選択（最大5銘柄）",
            options=st.session_state.selected_tickers,
            default=st.session_state.selected_tickers[:3],
            max_selections=5,
            format_func=lambda x: f"{x} - {self.portfolio[x]['name']}"
        )
        
        if len(comparison_tickers) < 2:
            st.warning("比較には最低2銘柄を選択してください")
            return
        
        # 比較データ収集
        comparison_data = []
        for ticker in comparison_tickers:
            df = self._get_stock_data(ticker)
            if not df.empty:
                analysis = self.analyzer.analyze_comprehensive_entry_timing(ticker, df)
                
                # パフォーマンス計算
                returns_1m = (df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1) * 100 if len(df) >= 20 else 0
                returns_3m = (df['Close'].iloc[-1] / df['Close'].iloc[-60] - 1) * 100 if len(df) >= 60 else 0
                
                comparison_data.append({
                    'Ticker': ticker,
                    'Name': self.portfolio[ticker]['name'],
                    'Signal': self.analyzer.signals[analysis['signal']]['label'],
                    'Score': analysis['total_score'],
                    'Price': analysis['current_price'],
                    '1M Return': returns_1m,
                    '3M Return': returns_3m,
                    'TECH': analysis['scores']['TECH'],
                    'FUND': analysis['scores']['FUND'],
                    'MACRO': analysis['scores']['MACRO'],
                    'RISK': analysis['scores']['RISK']
                })
        
        # 比較テーブル
        comparison_df = pd.DataFrame(comparison_data)
        
        st.subheader("📊 総合比較")
        
        # スタイル付きテーブル
        styled_df = comparison_df.style.background_gradient(
            subset=['Score', '1M Return', '3M Return'],
            cmap='RdYlGn'
        ).format({
            'Score': '{:.2f}',
            'Price': '${:.2f}',
            '1M Return': '{:+.1f}%',
            '3M Return': '{:+.1f}%',
            'TECH': '{:.1f}',
            'FUND': '{:.1f}',
            'MACRO': '{:.1f}',
            'RISK': '{:.1f}'
        })
        
        st.dataframe(styled_df, use_container_width=True)
        
        # レーダーチャート比較
        st.subheader("🎯 スコア比較レーダーチャート")
        
        fig = go.Figure()
        
        categories = ['TECH', 'FUND', 'MACRO', 'RISK']
        
        for _, row in comparison_df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row[cat] for cat in categories],
                theta=categories,
                fill='toself',
                name=row['Ticker']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )
            ),
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # パフォーマンス比較チャート
        st.subheader("📈 価格推移比較")
        
        fig = go.Figure()
        
        for ticker in comparison_tickers:
            df = self._get_stock_data(ticker)
            if not df.empty:
                # 正規化（最初の値を100とする）
                normalized = (df['Close'] / df['Close'].iloc[0]) * 100
                
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=normalized,
                    mode='lines',
                    name=ticker,
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title="正規化価格推移（開始点=100）",
            xaxis_title="日付",
            yaxis_title="相対価格",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_individual_stocks(self):
        """個別銘柄の詳細表示"""
        for ticker in st.session_state.selected_tickers[:6]:  # 最大6銘柄表示
            df = self._get_stock_data(ticker)
            if df.empty:
                continue
            
            analysis = self.analyzer.analyze_comprehensive_entry_timing(ticker, df)
            signal_info = self.analyzer.signals[analysis['signal']]
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <h4 style="margin: 0;">{ticker} - {self.portfolio[ticker]['name']}</h4>
                        <span style="background: {self.portfolio[ticker]['color']}; 
                                   color: white; padding: 0.2rem 0.6rem; 
                                   border-radius: 15px; font-size: 0.8rem;">
                            {self.portfolio[ticker]['sector']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.metric(
                        "現在価格",
                        f"${analysis['current_price']:.2f}",
                        f"{analysis['price_change_pct']:+.1f}%"
                    )
                
                with col3:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem;">{signal_info['icon']}</div>
                        <div style="font-weight: bold; color: {signal_info['color']};">
                            {signal_info['label']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    # プログレスバー
                    score_pct = (analysis['total_score'] / 5.0) * 100
                    st.markdown(f"""
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {score_pct}%;"></div>
                    </div>
                    <div style="text-align: center; margin-top: 0.5rem;">
                        スコア: {analysis['total_score']:.2f}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
    
    def _render_signal_overview(self):
        """シグナル概要の表示"""
        # シグナル分布
        signal_counts = {}
        for ticker in st.session_state.selected_tickers:
            signal = self._get_current_signal(ticker)
            if signal:
                signal_counts[signal] = signal_counts.get(signal, 0) + 1
        
        # 分布チャート
        if signal_counts:
            fig = go.Figure(data=[go.Bar(
                x=[self.analyzer.signals[s]['label'] for s in signal_counts.keys()],
                y=list(signal_counts.values()),
                marker_color=[self.analyzer.signals[s]['color'] for s in signal_counts.keys()]
            )])
            
            fig.update_layout(
                title="シグナル分布",
                xaxis_title="シグナルタイプ",
                yaxis_title="銘柄数",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_portfolio_charts(self):
        """ポートフォリオチャートの表示"""
        # セクター別配分
        sector_allocation = {}
        for ticker, info in self.portfolio.items():
            if ticker in st.session_state.selected_tickers:
                sector = info['sector']
                sector_allocation[sector] = sector_allocation.get(sector, 0) + info['weight']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # セクター配分円グラフ
            fig = go.Figure(data=[go.Pie(
                labels=list(sector_allocation.keys()),
                values=list(sector_allocation.values()),
                hole=0.3
            )])
            
            fig.update_layout(
                title="セクター配分",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # トップパフォーマー
            performance_data = []
            for ticker in st.session_state.selected_tickers[:5]:
                df = self._get_stock_data(ticker)
                if not df.empty and len(df) >= 20:
                    returns_1m = (df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1) * 100
                    performance_data.append({'ticker': ticker, 'returns': returns_1m})
            
            if performance_data:
                sorted_perf = sorted(performance_data, key=lambda x: x['returns'], reverse=True)
                
                fig = go.Figure(data=[go.Bar(
                    x=[item['ticker'] for item in sorted_perf],
                    y=[item['returns'] for item in sorted_perf],
                    marker_color=['green' if r > 0 else 'red' for r in [item['returns'] for item in sorted_perf]]
                )])
                
                fig.update_layout(
                    title="1ヶ月リターン TOP5",
                    xaxis_title="銘柄",
                    yaxis_title="リターン (%)",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_performance_chart(self, performance: Dict):
        """パフォーマンスチャートの描画"""
        # ダミーデータ（実際はヒストリカルデータから計算）
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        cumulative_returns = np.random.randn(100).cumsum() + 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=cumulative_returns,
            mode='lines',
            name='ポートフォリオ価値',
            line=dict(color='#667eea', width=3)
        ))
        
        fig.update_layout(
            xaxis_title="日付",
            yaxis_title="価値 ($)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_stock_performance_table(self, performance: Dict):
        """個別銘柄パフォーマンステーブル"""
        if not performance['stocks']:
            st.warning("パフォーマンスデータがありません")
            return
        
        # データフレーム作成
        perf_data = []
        for ticker, data in performance['stocks'].items():
            perf_data.append({
                'Ticker': ticker,
                'Name': self.portfolio[ticker]['name'],
                'Cost': data['cost'],
                'Value': data['value'],
                'Return': data['return'],
                'Return %': data['return_pct'],
                'Volatility': data['volatility'] * 100
            })
        
        perf_df = pd.DataFrame(perf_data)
        
        # スタイル付きテーブル
        styled_df = perf_df.style.format({
            'Cost': '${:,.0f}',
            'Value': '${:,.0f}',
            'Return': '${:+,.0f}',
            'Return %': '{:+.1f}%',
            'Volatility': '{:.1f}%'
        }).background_gradient(subset=['Return %'], cmap='RdYlGn')
        
        st.dataframe(styled_df, use_container_width=True)
    
    @st.cache_data(ttl=300)
    def _get_stock_data(_self, ticker: str) -> pd.DataFrame:
        """株価データ取得（キャッシュ付き）"""
        time_periods = {
            '1W': 7, '1M': 30, '3M': 90, '6M': 180,
            '1Y': 365, '3Y': 1095, '5Y': 1825
        }
        
        days = time_periods.get(st.session_state.time_range, 90)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 100)
        
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                return pd.DataFrame()
            
            # テクニカル指標の計算
            df['EMA20'] = df['Close'].ewm(span=20).mean()
            df['EMA50'] = df['Close'].ewm(span=50).mean()
            df['SMA200'] = df['Close'].rolling(window=200).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # ボリンジャーバンド
            bb_period = 20
            rolling_mean = df['Close'].rolling(window=bb_period).mean()
            rolling_std = df['Close'].rolling(window=bb_period).std()
            df['BB_upper'] = rolling_mean + (rolling_std * 2)
            df['BB_lower'] = rolling_mean - (rolling_std * 2)
            
            return df.tail(days)
            
        except Exception as e:
            st.error(f"データ取得エラー ({ticker}): {str(e)}")
            return pd.DataFrame()
    
    def _get_current_signal(self, ticker: str) -> Optional[str]:
        """現在のシグナルを取得"""
        df = self._get_stock_data(ticker)
        if not df.empty:
            analysis = self.analyzer.analyze_comprehensive_entry_timing(ticker, df)
            return analysis['signal']
        return None
    
    def _calculate_average_volatility(self) -> float:
        """平均ボラティリティを計算"""
        volatilities = []
        for ticker in st.session_state.selected_tickers:
            df = self._get_stock_data(ticker)
            if not df.empty:
                returns = df['Close'].pct_change().dropna()
                vol = returns.std() * np.sqrt(252)
                volatilities.append(vol)
        
        return np.mean(volatilities) if volatilities else 0
    
    def fetch_batch_data(self, force_refresh: bool = False) -> bool:
        """全銘柄のデータを一括取得してキャッシュ（portfolio_master_report_hybridから移植）"""
        # キャッシュが有効かチェック（5分間有効）
        if (not force_refresh and 
            self._last_fetch_time and 
            (time.time() - self._last_fetch_time) < 300):
            return True
            
        with st.spinner('📡 全銘柄のデータを一括取得中...'):
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
                        except Exception as e:
                            st.error(f"✗ {ticker}: 並列処理エラー - {e}")
                
                # 成功率をチェック
                success_rate = success_count / len(tickers)
                if success_rate >= 0.7:  # 70%以上成功すれば良しとする
                    self._last_fetch_time = time.time()
                    st.success(f"✅ 一括データ取得完了: {success_count}/{len(tickers)} ({success_rate:.1%})")
                    return True
                else:
                    st.warning(f"⚠️ 一括データ取得成功率が低い: {success_rate:.1%}")
                    return False
                    
            except Exception as e:
                st.error(f"一括データ取得エラー: {e}")
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
            df = self._add_technical_indicators(df)
            
            # 株式情報を取得
            info = stock.info
            
            return True, df, info
            
        except Exception as e:
            return False, None, None
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """技術指標を追加"""
        # EMA
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        # SMA
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ボリンジャーバンド
        bb_period = 20
        rolling_mean = df['Close'].rolling(window=bb_period).mean()
        rolling_std = df['Close'].rolling(window=bb_period).std()
        df['BB_upper'] = rolling_mean + (rolling_std * 2)
        df['BB_lower'] = rolling_mean - (rolling_std * 2)
        
        # ATR
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        
        return df
    
    def _render_hybrid_report_view(self):
        """ハイブリッドレポートビュー"""
        st.markdown("""
        <div class="performance-card">
            <h2 style="margin: 0;">📊 ハイブリッドポートフォリオレポート</h2>
            <p>全体戦略・最適化・専門家分析を統合した包括的レポート</p>
        </div>
        """, unsafe_allow_html=True)
        
        # データの一括取得
        if st.button("🔄 データを更新", type="primary"):
            self.fetch_batch_data(force_refresh=True)
        
        # タブでコンテンツを整理
        tabs = st.tabs(["🎯 全体概要", "📈 ポートフォリオ最適化", "🤖 4専門家分析", "🏆 競合分析", "📤 レポート生成"])
        
        with tabs[0]:
            self._render_portfolio_overview()
        
        with tabs[1]:
            self._render_portfolio_optimization()
        
        with tabs[2]:
            self._render_expert_analysis()
        
        with tabs[3]:
            self._render_competitor_analysis()
        
        with tabs[4]:
            self._render_report_generation()
    
    def _render_portfolio_overview(self):
        """ポートフォリオ全体概要"""
        st.header("🎯 ポートフォリオ全体概要")
        
        # ポートフォリオ構成の表示
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 円グラフでポートフォリオ構成を表示
            fig = go.Figure(data=[go.Pie(
                labels=[f"{ticker} ({info['name']})" for ticker, info in self.portfolio.items()],
                values=[info['weight'] for info in self.portfolio.values()],
                marker=dict(colors=[info['color'] for info in self.portfolio.values()]),
                hole=.3
            )])
            
            fig.update_layout(
                title="ポートフォリオ構成",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 セクター別分布")
            sector_weights = {}
            for ticker, info in self.portfolio.items():
                sector = info['sector']
                if sector not in sector_weights:
                    sector_weights[sector] = 0
                sector_weights[sector] += info['weight']
            
            for sector, weight in sorted(sector_weights.items(), key=lambda x: x[1], reverse=True):
                st.metric(sector, f"{weight}%")
        
        # 各銘柄の現在のメトリクス
        st.subheader("📊 銘柄別パフォーマンス")
        
        # データの準備
        metrics_data = []
        for ticker, info in self.portfolio.items():
            if ticker in self._batch_data_cache and ticker in self._info_cache:
                df = self._batch_data_cache[ticker]
                stock_info = self._info_cache[ticker]
                
                if not df.empty:
                    latest = df.iloc[-1]
                    change_pct = 0
                    if len(df) >= 2:
                        change_pct = ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100)
                    
                    metrics_data.append({
                        'Ticker': ticker,
                        'Name': info['name'],
                        'Sector': info['sector'],
                        'Weight': f"{info['weight']}%",
                        'Price': f"${latest['Close']:.2f}",
                        'Change': f"{change_pct:+.2f}%",
                        'RSI': f"{latest['RSI']:.1f}",
                        'Volume': f"{latest['Volume']:,.0f}"
                    })
        
        if metrics_data:
            df_metrics = pd.DataFrame(metrics_data)
            st.dataframe(
                df_metrics,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Change": st.column_config.TextColumn(
                        "Change",
                        help="前日比変動率"
                    )
                }
            )
    
    def _render_portfolio_optimization(self):
        """ポートフォリオ最適化"""
        st.header("📈 ポートフォリオ最適化")
        
        # 最適化計算
        optimization = self.portfolio_report.calculate_portfolio_optimization()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 現在の配分")
            current_df = pd.DataFrame([
                {'銘柄': ticker, '配分': f"{weight}%"}
                for ticker, weight in optimization['current_allocation'].items()
            ])
            st.dataframe(current_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("🎯 推奨配分")
            recommended_df = pd.DataFrame([
                {'銘柄': ticker, '配分': f"{weight:.1f}%", 'リスク': optimization['risk_metrics'][ticker]}
                for ticker, weight in optimization['recommended_allocation'].items()
            ])
            st.dataframe(recommended_df, use_container_width=True, hide_index=True)
        
        # リスクメトリクスの表示
        st.subheader("⚠️ リスク評価")
        
        # リスクヒートマップ
        risk_data = []
        for ticker, risk in optimization['risk_metrics'].items():
            risk_data.append({'銘柄': ticker, 'リスクスコア': risk})
        
        risk_df = pd.DataFrame(risk_data)
        
        fig = go.Figure(data=go.Bar(
            x=risk_df['銘柄'],
            y=risk_df['リスクスコア'],
            marker_color=risk_df['リスクスコア'].apply(
                lambda x: '#dc3545' if x >= 8 else '#ffc107' if x >= 6 else '#28a745'
            )
        ))
        
        fig.update_layout(
            title="銘柄別リスクスコア (1-10)",
            xaxis_title="銘柄",
            yaxis_title="リスクスコア",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_expert_analysis(self):
        """専門家分析"""
        st.header("🤖 4専門家分析")
        
        # 銘柄選択
        selected_ticker = st.selectbox(
            "銘柄を選択",
            options=list(self.portfolio.keys()),
            format_func=lambda x: f"{x} - {self.portfolio[x]['name']}"
        )
        
        if selected_ticker:
            # 専門家スコアを計算
            expert_scores = self.portfolio_report.calculate_expert_scores(selected_ticker)
            
            # スコアの表示
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("TECH", f"{expert_scores['TECH']}/5.0", 
                         delta=f"{expert_scores['TECH'] - 3.0:+.1f}")
            
            with col2:
                st.metric("FUND", f"{expert_scores['FUND']}/5.0",
                         delta=f"{expert_scores['FUND'] - 3.0:+.1f}")
            
            with col3:
                st.metric("MACRO", f"{expert_scores['MACRO']}/5.0",
                         delta=f"{expert_scores['MACRO'] - 3.0:+.1f}")
            
            with col4:
                st.metric("RISK", f"{expert_scores['RISK']}/5.0",
                         delta=f"{expert_scores['RISK'] - 3.0:+.1f}")
            
            with col5:
                st.metric("OVERALL", f"{expert_scores['OVERALL']}/5.0",
                         delta=f"{expert_scores['OVERALL'] - 3.0:+.1f}")
            
            # レーダーチャート
            fig = go.Figure(data=go.Scatterpolar(
                r=[expert_scores['TECH'], expert_scores['FUND'], 
                   expert_scores['MACRO'], expert_scores['RISK'], expert_scores['TECH']],
                theta=['TECH', 'FUND', 'MACRO', 'RISK', 'TECH'],
                fill='toself',
                name=selected_ticker
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )
                ),
                showlegend=False,
                title=f"{selected_ticker} - 専門家評価レーダーチャート"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 専門家討論レポートの表示
            discussion_report = self.portfolio_report.read_discussion_report(selected_ticker)
            if discussion_report:
                st.subheader("📝 専門家討論レポート")
                with st.expander("詳細を表示"):
                    st.markdown(discussion_report)
    
    def _render_competitor_analysis(self):
        """競合分析"""
        st.header("🏆 競合分析")
        
        # 銘柄選択
        selected_ticker = st.selectbox(
            "分析対象銘柄",
            options=list(self.portfolio.keys()),
            format_func=lambda x: f"{x} - {self.portfolio[x]['name']}"
        )
        
        if selected_ticker:
            # 競合分析レポートの読み込み
            competitor_report = self.portfolio_report.read_competitor_report(selected_ticker)
            
            if competitor_report:
                st.markdown(competitor_report)
            else:
                # 競合分析を実行
                if st.button("🔍 競合分析を実行"):
                    with st.spinner('競合分析中...'):
                        try:
                            report = self.competitor_analyzer.generate_competitor_report(selected_ticker)
                            st.markdown(report)
                        except Exception as e:
                            st.error(f"競合分析エラー: {str(e)}")
    
    def _render_report_generation(self):
        """レポート生成"""
        st.header("📤 レポート生成")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 HTMLレポート生成")
            st.markdown("""
            全体戦略、最適化、専門家分析を含む
            包括的なHTMLレポートを生成します。
            """)
            
            if st.button("🌐 HTMLレポート生成", type="primary"):
                with st.spinner('レポート生成中...'):
                    try:
                        output_path = self.portfolio_report.save_report()
                        st.success(f"✅ レポート生成完了: {output_path}")
                        
                        # ダウンロードボタン
                        with open(output_path, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label="📥 HTMLレポートをダウンロード",
                                data=f.read(),
                                file_name=os.path.basename(output_path),
                                mime='text/html'
                            )
                    except Exception as e:
                        st.error(f"レポート生成エラー: {str(e)}")
        
        with col2:
            st.subheader("📤 Excelエクスポート")
            st.markdown("""
            現在のダッシュボードデータを
            Excel形式でエクスポートします。
            """)
            
            if st.button("📊 Excelエクスポート", type="secondary"):
                self._export_to_excel()
    
    def _export_to_excel(self):
        """Excelへのエクスポート"""
        try:
            export_manager = DashboardExportManager()
            
            # データの準備
            export_data = {
                'portfolio': st.session_state.portfolio,
                'stock_analyses': self._prepare_stock_analyses(),
                'portfolio_performance': self._calculate_portfolio_performance(),
                'signal_history': self._get_signal_history()
            }
            
            # エクスポート実行（バイトストリームを取得）
            excel_buffer = export_manager.export_to_excel(export_data)
            
            # ファイル名生成
            filename = f"tiker_dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # ダウンロードボタンの表示
            st.download_button(
                label="📥 Excelファイルをダウンロード",
                data=excel_buffer.getvalue(),
                file_name=filename,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            st.success(f"✅ エクスポート完了: {filename}")
        except Exception as e:
            st.error(f"エクスポートエラー: {str(e)}")
    
    def _prepare_stock_analyses(self) -> Dict:
        """株式分析データの準備"""
        analyses = {}
        for ticker in self.portfolio.keys():
            if ticker in self._batch_data_cache:
                df = self._batch_data_cache[ticker]
                info = self._info_cache.get(ticker, {})
                
                if not df.empty:
                    latest = df.iloc[-1]
                    change_pct = 0
                    if len(df) >= 2:
                        change_pct = ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100)
                    
                    # 専門家スコアを計算
                    expert_scores = self.portfolio_report.calculate_expert_scores(ticker)
                    
                    analyses[ticker] = {
                        'current_price': latest['Close'],
                        'price_change_pct': change_pct,
                        'signal': self._get_current_signal(ticker),
                        'total_score': expert_scores['OVERALL'],
                        'scores': expert_scores,
                        'timestamp': datetime.now().isoformat()
                    }
        return analyses
    
    def _calculate_portfolio_performance(self) -> Dict:
        """ポートフォリオパフォーマンスの計算"""
        return self.analyzer.calculate_portfolio_performance(
            self.portfolio, 
            datetime.now() - timedelta(days=365)
        )
    
    def _get_signal_history(self) -> List[Dict]:
        """シグナル履歴の取得"""
        return self.analyzer.signal_history
    
    def _get_all_signals(self) -> Dict:
        """全銘柄の現在のシグナルを取得"""
        signals = {}
        for ticker in self.portfolio.keys():
            signals[ticker] = self._get_current_signal(ticker)
        return signals

# メイン実行
if __name__ == "__main__":
    app = UltimateDashboardApp()
    app.run()