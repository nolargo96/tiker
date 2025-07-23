#!/usr/bin/env python3
"""
Tiker Interactive Dashboard Enhanced - 強化版
4専門家フレームワーク統合型エントリータイミング分析

主な強化点:
1. TECH/FUND/MACRO/RISKの4専門家分析統合
2. エントリータイミングの明確な視覚化
3. 既存システム(unified_stock_analyzer)との完全統合
4. より精度の高い投資判断ロジック
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
import warnings
warnings.filterwarnings('ignore')

# 既存システムの活用
from unified_stock_analyzer import StockAnalyzer, calculate_tech_score, calculate_fund_score, calculate_macro_score, calculate_risk_score
from stock_analyzer_lib import ConfigManager, TechnicalIndicators, StockDataManager
from cache_manager import CacheManager

# ページ設定
st.set_page_config(
    page_title="🚀 Tiker Dashboard Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 強化版カスタムCSS
st.markdown("""
<style>
/* グローバルスタイル */
.main { padding: 0rem 1rem; }

/* エントリーシグナルカード */
.entry-signal-card {
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 1rem 0;
    position: relative;
    overflow: hidden;
}

.entry-signal-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
}

.signal-strong-buy {
    background: linear-gradient(135deg, #d4f1d4 0%, #a8e6a8 100%);
    border: 2px solid #28a745;
}

.signal-strong-buy::before {
    background: #28a745;
}

.signal-buy {
    background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c8 100%);
    border: 2px solid #5cb85c;
}

.signal-buy::before {
    background: #5cb85c;
}

.signal-hold {
    background: linear-gradient(135deg, #fff9e6 0%, #ffecb3 100%);
    border: 2px solid #ffc107;
}

.signal-hold::before {
    background: #ffc107;
}

.signal-sell {
    background: linear-gradient(135deg, #ffe0e0 0%, #ffcdd2 100%);
    border: 2px solid #dc3545;
}

.signal-sell::before {
    background: #dc3545;
}

/* 専門家スコアバー */
.expert-score-bar {
    height: 30px;
    background: #f0f0f0;
    border-radius: 15px;
    overflow: hidden;
    margin: 0.5rem 0;
    position: relative;
}

.expert-score-fill {
    height: 100%;
    transition: width 0.5s ease;
    display: flex;
    align-items: center;
    padding-left: 10px;
    color: white;
    font-weight: bold;
}

.score-excellent { background: linear-gradient(90deg, #28a745, #5cb85c); }
.score-good { background: linear-gradient(90deg, #17a2b8, #5bc0de); }
.score-average { background: linear-gradient(90deg, #ffc107, #ffeb3b); color: #333; }
.score-poor { background: linear-gradient(90deg, #dc3545, #f44336); }

/* タイミングインジケーター */
.timing-indicator {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin: 1rem 0;
}

.timing-gauge {
    width: 100%;
    height: 40px;
    background: linear-gradient(90deg, 
        #dc3545 0%, 
        #ffc107 40%, 
        #28a745 60%, 
        #0056b3 100%);
    border-radius: 20px;
    position: relative;
    margin: 1rem 0;
}

.timing-pointer {
    position: absolute;
    top: -10px;
    width: 4px;
    height: 60px;
    background: #333;
    border-radius: 2px;
    transition: left 0.5s ease;
}

/* ポートフォリオサマリー */
.portfolio-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.metric-highlight {
    background: rgba(255,255,255,0.2);
    padding: 0.5rem 1rem;
    border-radius: 10px;
    display: inline-block;
    margin: 0.5rem;
}

/* リアルタイムバッジ */
.live-badge {
    display: inline-block;
    background: #28a745;
    color: white;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.6; }
    100% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

class EnhancedEntryTimingAnalyzer:
    """強化版エントリータイミング分析システム - 4専門家統合型"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.stock_analyzer = StockAnalyzer()
        
        # エントリーシグナル定義（5段階）
        self.signals = {
            'STRONG_BUY': {
                'label': '絶好の買い場',
                'color': '#28a745',
                'icon': '🟢🟢',
                'threshold': 4.0,
                'class': 'signal-strong-buy'
            },
            'BUY': {
                'label': '買い推奨',
                'color': '#5cb85c',
                'icon': '🟢',
                'threshold': 3.5,
                'class': 'signal-buy'
            },
            'HOLD': {
                'label': '様子見',
                'color': '#ffc107',
                'icon': '🟡',
                'threshold': 2.5,
                'class': 'signal-hold'
            },
            'SELL': {
                'label': '売却検討',
                'color': '#dc3545',
                'icon': '🔴',
                'threshold': 2.0,
                'class': 'signal-sell'
            },
            'STRONG_SELL': {
                'label': '即売却推奨',
                'color': '#8b0000',
                'icon': '🔴🔴',
                'threshold': 0,
                'class': 'signal-sell'
            }
        }
    
    def analyze_comprehensive_entry_timing(self, ticker: str, df: pd.DataFrame) -> Dict[str, Any]:
        """4専門家による総合エントリータイミング分析"""
        
        if df.empty or len(df) < 50:
            return self._create_empty_result()
        
        latest_data = df.iloc[-1]
        
        # 1. TECH - テクニカル分析
        tech_score = calculate_tech_score(df)
        tech_details = self._analyze_technical_details(df)
        
        # 2. FUND - ファンダメンタル分析
        fund_score = calculate_fund_score(ticker, latest_data)
        fund_details = self._analyze_fundamental_details(ticker)
        
        # 3. MACRO - マクロ環境分析
        macro_score = calculate_macro_score(ticker)
        macro_details = self._analyze_macro_details(ticker)
        
        # 4. RISK - リスク管理分析
        risk_score = calculate_risk_score(df, 100)  # 仮の配分100%として計算
        risk_details = self._analyze_risk_details(df)
        
        # 総合スコア計算（重み付き平均）
        weights = {
            'TECH': 0.30,   # テクニカル30%
            'FUND': 0.25,   # ファンダメンタル25%
            'MACRO': 0.25,  # マクロ25%
            'RISK': 0.20    # リスク20%
        }
        
        total_score = (
            tech_score * weights['TECH'] +
            fund_score * weights['FUND'] +
            macro_score * weights['MACRO'] +
            risk_score * weights['RISK']
        )
        
        # エントリーシグナル判定
        signal = self._determine_signal(total_score)
        
        # エントリータイミング要因分析
        entry_factors = self._analyze_entry_factors(
            tech_details, fund_details, macro_details, risk_details
        )
        
        return {
            'signal': signal,
            'total_score': total_score,
            'scores': {
                'TECH': tech_score,
                'FUND': fund_score,
                'MACRO': macro_score,
                'RISK': risk_score
            },
            'details': {
                'TECH': tech_details,
                'FUND': fund_details,
                'MACRO': macro_details,
                'RISK': risk_details
            },
            'entry_factors': entry_factors,
            'current_price': latest_data['Close'],
            'price_change_pct': ((latest_data['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100) if len(df) > 1 else 0,
            'timestamp': datetime.now()
        }
    
    def _analyze_technical_details(self, df: pd.DataFrame) -> Dict:
        """テクニカル詳細分析"""
        latest = df.iloc[-1]
        
        details = {
            'trend': 'UNKNOWN',
            'momentum': 'NEUTRAL',
            'support_resistance': {},
            'key_levels': [],
            'signals': []
        }
        
        # トレンド判定
        if 'EMA20' in df.columns and 'SMA200' in df.columns:
            if latest['Close'] > latest['EMA20'] > latest['SMA200']:
                details['trend'] = 'STRONG_UP'
                details['signals'].append('強い上昇トレンド')
            elif latest['Close'] > latest['SMA200']:
                details['trend'] = 'UP'
                details['signals'].append('上昇トレンド')
            else:
                details['trend'] = 'DOWN'
                details['signals'].append('下降トレンド')
        
        # RSIモメンタム
        if 'RSI' in df.columns and not pd.isna(latest['RSI']):
            rsi = latest['RSI']
            if rsi < 30:
                details['momentum'] = 'OVERSOLD'
                details['signals'].append('売られ過ぎ（RSI < 30）')
            elif rsi > 70:
                details['momentum'] = 'OVERBOUGHT'
                details['signals'].append('買われ過ぎ（RSI > 70）')
            else:
                details['momentum'] = 'NEUTRAL'
        
        # サポート・レジスタンスレベル
        recent_high = df['High'].tail(20).max()
        recent_low = df['Low'].tail(20).min()
        details['support_resistance'] = {
            'resistance': recent_high,
            'support': recent_low,
            'current_position': (latest['Close'] - recent_low) / (recent_high - recent_low)
        }
        
        return details
    
    def _analyze_fundamental_details(self, ticker: str) -> Dict:
        """ファンダメンタル詳細分析"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            details = {
                'valuation': 'UNKNOWN',
                'growth': 'UNKNOWN',
                'profitability': 'UNKNOWN',
                'signals': []
            }
            
            # バリュエーション判定
            pe_ratio = info.get('trailingPE', 0)
            if pe_ratio > 0:
                if pe_ratio < 15:
                    details['valuation'] = 'UNDERVALUED'
                    details['signals'].append(f'割安（PER: {pe_ratio:.1f}）')
                elif pe_ratio > 30:
                    details['valuation'] = 'OVERVALUED'
                    details['signals'].append(f'割高（PER: {pe_ratio:.1f}）')
                else:
                    details['valuation'] = 'FAIR'
            
            # 成長性
            revenue_growth = info.get('revenueGrowth', 0)
            if revenue_growth > 0.20:
                details['growth'] = 'HIGH'
                details['signals'].append(f'高成長（売上成長率: {revenue_growth:.1%}）')
            elif revenue_growth > 0.10:
                details['growth'] = 'MODERATE'
            else:
                details['growth'] = 'LOW'
            
            return details
            
        except Exception as e:
            return {
                'valuation': 'UNKNOWN',
                'growth': 'UNKNOWN',
                'profitability': 'UNKNOWN',
                'signals': ['ファンダメンタルデータ取得エラー']
            }
    
    def _analyze_macro_details(self, ticker: str) -> Dict:
        """マクロ環境詳細分析"""
        # セクター別のマクロ環境評価
        sector_trends = {
            'TSLA': {'sector': 'EV', 'trend': 'POSITIVE', 'factors': ['脱炭素政策支援', 'EV需要拡大']},
            'FSLR': {'sector': 'Solar', 'trend': 'POSITIVE', 'factors': ['再エネ投資拡大', 'IRA法案']},
            'RKLB': {'sector': 'Space', 'trend': 'POSITIVE', 'factors': ['小型衛星需要', '打ち上げコスト低下']},
            'ASTS': {'sector': 'Satellite', 'trend': 'NEUTRAL', 'factors': ['5G補完需要', '規制リスク']},
            'OKLO': {'sector': 'Nuclear', 'trend': 'POSITIVE', 'factors': ['SMR注目', 'エネルギー安全保障']},
            'JOBY': {'sector': 'eVTOL', 'trend': 'NEUTRAL', 'factors': ['都市交通革新', '規制整備中']},
            'OII': {'sector': 'Marine', 'trend': 'POSITIVE', 'factors': ['海洋開発需要', '油価回復']},
            'LUNR': {'sector': 'Space', 'trend': 'POSITIVE', 'factors': ['月面開発', 'NASA契約']},
            'RDW': {'sector': 'Space', 'trend': 'NEUTRAL', 'factors': ['宇宙インフラ需要', '競争激化']}
        }
        
        details = sector_trends.get(ticker, {
            'sector': 'Unknown',
            'trend': 'NEUTRAL',
            'factors': []
        })
        
        # マクロ経済指標の影響
        details['macro_indicators'] = {
            'interest_rates': 'DECLINING',  # 金利動向
            'inflation': 'MODERATING',       # インフレ動向
            'gdp_growth': 'STABLE'           # GDP成長
        }
        
        return details
    
    def _analyze_risk_details(self, df: pd.DataFrame) -> Dict:
        """リスク詳細分析"""
        returns = df['Close'].pct_change().dropna()
        
        details = {
            'volatility': 'UNKNOWN',
            'drawdown': 0,
            'var_95': 0,
            'signals': []
        }
        
        # ボラティリティ評価
        volatility = returns.std() * np.sqrt(252)  # 年率換算
        if volatility < 0.20:
            details['volatility'] = 'LOW'
            details['signals'].append('低ボラティリティ')
        elif volatility > 0.40:
            details['volatility'] = 'HIGH'
            details['signals'].append(f'高ボラティリティ（年率{volatility:.1%}）')
        else:
            details['volatility'] = 'MODERATE'
        
        # 最大ドローダウン
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = ((cumulative - running_max) / running_max).min()
        details['drawdown'] = drawdown
        
        if drawdown < -0.20:
            details['signals'].append(f'大幅下落リスク（最大DD: {drawdown:.1%}）')
        
        # VaR（95%信頼区間）
        var_95 = np.percentile(returns, 5)
        details['var_95'] = var_95
        
        return details
    
    def _analyze_entry_factors(self, tech: Dict, fund: Dict, macro: Dict, risk: Dict) -> List[Dict]:
        """エントリー判断の主要要因を分析"""
        factors = []
        
        # ポジティブ要因
        positive_factors = []
        
        # テクニカル要因
        if tech.get('trend') == 'STRONG_UP':
            positive_factors.append({
                'type': 'TECH',
                'factor': '強い上昇トレンド',
                'impact': 'HIGH',
                'icon': '📈'
            })
        
        if tech.get('momentum') == 'OVERSOLD':
            positive_factors.append({
                'type': 'TECH',
                'factor': 'RSI売られ過ぎ',
                'impact': 'MEDIUM',
                'icon': '🔄'
            })
        
        # ファンダメンタル要因
        if fund.get('valuation') == 'UNDERVALUED':
            positive_factors.append({
                'type': 'FUND',
                'factor': '割安な株価水準',
                'impact': 'HIGH',
                'icon': '💎'
            })
        
        if fund.get('growth') == 'HIGH':
            positive_factors.append({
                'type': 'FUND',
                'factor': '高い成長性',
                'impact': 'HIGH',
                'icon': '🚀'
            })
        
        # マクロ要因
        if macro.get('trend') == 'POSITIVE':
            positive_factors.append({
                'type': 'MACRO',
                'factor': 'セクター追い風',
                'impact': 'MEDIUM',
                'icon': '🌟'
            })
        
        # ネガティブ要因
        negative_factors = []
        
        if tech.get('momentum') == 'OVERBOUGHT':
            negative_factors.append({
                'type': 'TECH',
                'factor': 'RSI買われ過ぎ',
                'impact': 'MEDIUM',
                'icon': '⚠️'
            })
        
        if risk.get('volatility') == 'HIGH':
            negative_factors.append({
                'type': 'RISK',
                'factor': '高ボラティリティ',
                'impact': 'HIGH',
                'icon': '⚡'
            })
        
        return {
            'positive': positive_factors,
            'negative': negative_factors,
            'net_score': len(positive_factors) - len(negative_factors)
        }
    
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
                'RISK': 2.5
            },
            'details': {},
            'entry_factors': {'positive': [], 'negative': [], 'net_score': 0},
            'current_price': 0,
            'price_change_pct': 0,
            'timestamp': datetime.now()
        }

class EnhancedDashboardApp:
    """強化版ダッシュボードアプリケーション"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.analyzer = EnhancedEntryTimingAnalyzer()
        self.cache_manager = CacheManager()
        
        # ポートフォリオ定義
        self.portfolio = {
            'TSLA': {'weight': 20, 'name': 'Tesla Inc', 'sector': 'EV/Tech', 'color': '#e31837'},
            'FSLR': {'weight': 20, 'name': 'First Solar', 'sector': 'Solar Energy', 'color': '#ffd700'},
            'RKLB': {'weight': 10, 'name': 'Rocket Lab', 'sector': 'Space', 'color': '#ff6b35'},
            'ASTS': {'weight': 10, 'name': 'AST SpaceMobile', 'sector': 'Satellite', 'color': '#4a90e2'},
            'OKLO': {'weight': 10, 'name': 'Oklo Inc', 'sector': 'Nuclear', 'color': '#50c878'},
            'JOBY': {'weight': 10, 'name': 'Joby Aviation', 'sector': 'eVTOL', 'color': '#9b59b6'},
            'OII': {'weight': 10, 'name': 'Oceaneering', 'sector': 'Marine', 'color': '#1abc9c'},
            'LUNR': {'weight': 5, 'name': 'Intuitive Machines', 'sector': 'Space', 'color': '#34495e'},
            'RDW': {'weight': 5, 'name': 'Redwire Corp', 'sector': 'Space', 'color': '#e74c3c'}
        }
    
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
    
    def _render_header(self):
        """ヘッダー部分の描画"""
        st.markdown("""
        <div class="portfolio-header">
            <h1>🚀 Tiker Dashboard Pro</h1>
            <p>4専門家AI統合型 エントリータイミング分析システム</p>
            <div class="metric-highlight">
                <span class="live-badge">● LIVE</span>
                最終更新: """ + st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S") + """
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """サイドバーの描画"""
        with st.sidebar:
            st.header("⚙️ 分析設定")
            
            # データ更新ボタン
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 更新", type="primary", use_container_width=True):
                    st.cache_data.clear()
                    st.session_state.last_update = datetime.now()
                    st.rerun()
            
            with col2:
                if st.button("🧹 キャッシュクリア", use_container_width=True):
                    self.cache_manager.clear_all()
                    st.success("キャッシュをクリアしました")
            
            # 分析期間
            st.subheader("📅 分析期間")
            period_days = st.select_slider(
                "日数",
                options=[30, 60, 90, 180, 365],
                value=90,
                help="チャートと分析に使用する過去データの日数"
            )
            
            # 銘柄選択
            st.subheader("📊 銘柄選択")
            selected_tickers = st.multiselect(
                "分析対象",
                options=list(self.portfolio.keys()),
                default=st.session_state.selected_tickers,
                format_func=lambda x: f"{x} - {self.portfolio[x]['name']}"
            )
            st.session_state.selected_tickers = selected_tickers
            
            # 表示設定
            st.subheader("👁️ 表示設定")
            show_technical = st.checkbox("テクニカル指標", value=True)
            show_volume = st.checkbox("出来高", value=True)
            show_signals = st.checkbox("売買シグナル", value=True)
            show_expert_details = st.checkbox("専門家詳細分析", value=True)
            
            # セッション状態に保存
            st.session_state.update({
                'period_days': period_days,
                'show_technical': show_technical,
                'show_volume': show_volume,
                'show_signals': show_signals,
                'show_expert_details': show_expert_details
            })
            
            # 情報表示
            st.divider()
            st.info("""
            **エントリーシグナル説明**
            - 🟢🟢 絶好の買い場（4.0+）
            - 🟢 買い推奨（3.5+）
            - 🟡 様子見（2.5+）
            - 🔴 売却検討（2.0+）
            - 🔴🔴 即売却推奨（<2.0）
            """)
    
    def _render_main_content(self):
        """メインコンテンツの描画"""
        # タブ作成
        tab_names = ["📊 ポートフォリオ総合"] + [f"{self.portfolio[t]['name']}" for t in st.session_state.selected_tickers]
        tabs = st.tabs(tab_names)
        
        # ポートフォリオ総合タブ
        with tabs[0]:
            self._render_portfolio_overview()
        
        # 個別銘柄タブ
        for i, ticker in enumerate(st.session_state.selected_tickers, 1):
            with tabs[i]:
                self._render_stock_detail(ticker)
    
    def _render_portfolio_overview(self):
        """ポートフォリオ総合ビュー"""
        st.header("📊 ポートフォリオ エントリータイミング総合分析")
        
        # 全銘柄のシグナル一覧
        analysis_results = []
        
        for ticker in st.session_state.selected_tickers:
            df = self._get_stock_data(ticker)
            if not df.empty:
                result = self.analyzer.analyze_comprehensive_entry_timing(ticker, df)
                analysis_results.append({
                    'ticker': ticker,
                    'result': result
                })
        
        if analysis_results:
            # シグナル分布の表示
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.subheader("🎯 エントリーシグナル一覧")
                
                # シグナルテーブル作成
                signal_data = []
                for item in analysis_results:
                    ticker = item['ticker']
                    result = item['result']
                    signal_info = self.analyzer.signals[result['signal']]
                    
                    signal_data.append({
                        'Ticker': ticker,
                        'Name': self.portfolio[ticker]['name'],
                        'Signal': f"{signal_info['icon']} {signal_info['label']}",
                        'Score': f"{result['total_score']:.2f}",
                        'Price': f"${result['current_price']:.2f}",
                        'Change': f"{result['price_change_pct']:+.1f}%"
                    })
                
                signal_df = pd.DataFrame(signal_data)
                st.dataframe(
                    signal_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'Score': st.column_config.ProgressColumn(
                            'Score',
                            min_value=0,
                            max_value=5,
                            format="%.2f"
                        )
                    }
                )
            
            with col2:
                st.subheader("📈 シグナル分布")
                
                # シグナルカウント
                signal_counts = {}
                for item in analysis_results:
                    signal = item['result']['signal']
                    signal_counts[signal] = signal_counts.get(signal, 0) + 1
                
                # パイチャート作成
                fig = go.Figure(data=[go.Pie(
                    labels=[self.analyzer.signals[s]['label'] for s in signal_counts.keys()],
                    values=list(signal_counts.values()),
                    marker_colors=[self.analyzer.signals[s]['color'] for s in signal_counts.keys()],
                    hole=0.3
                )])
                
                fig.update_layout(
                    height=300,
                    showlegend=True,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                st.subheader("🏆 トップシグナル")
                
                # スコアでソート
                sorted_results = sorted(analysis_results, key=lambda x: x['result']['total_score'], reverse=True)
                
                # トップ3表示
                for i, item in enumerate(sorted_results[:3]):
                    ticker = item['ticker']
                    result = item['result']
                    signal_info = self.analyzer.signals[result['signal']]
                    
                    st.markdown(f"""
                    <div class="metric-card {signal_info['class']}">
                        <h4>{i+1}. {ticker}</h4>
                        <p>{signal_info['icon']} {signal_info['label']}</p>
                        <p>スコア: {result['total_score']:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 専門家スコア比較
            st.subheader("👥 4専門家スコア比較")
            
            # レーダーチャート用データ準備
            categories = ['TECH', 'FUND', 'MACRO', 'RISK']
            
            fig = go.Figure()
            
            for item in analysis_results[:5]:  # 最大5銘柄まで表示
                ticker = item['ticker']
                scores = item['result']['scores']
                
                fig.add_trace(go.Scatterpolar(
                    r=[scores[cat] for cat in categories],
                    theta=categories,
                    fill='toself',
                    name=ticker
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )
                ),
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_stock_detail(self, ticker: str):
        """個別銘柄詳細ビュー"""
        stock_info = self.portfolio[ticker]
        
        # ヘッダー
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header(f"{ticker} - {stock_info['name']}")
        with col2:
            st.markdown(f"<span style='background-color:{stock_info['color']};padding:5px 10px;border-radius:5px;color:white;'>{stock_info['sector']}</span>", unsafe_allow_html=True)
        
        # データ取得と分析
        df = self._get_stock_data(ticker)
        if df.empty:
            st.error(f"{ticker}のデータ取得に失敗しました")
            return
        
        analysis_result = self.analyzer.analyze_comprehensive_entry_timing(ticker, df)
        signal_info = self.analyzer.signals[analysis_result['signal']]
        
        # エントリーシグナルカード
        st.markdown(f"""
        <div class="entry-signal-card {signal_info['class']}">
            <h2>{signal_info['icon']} {signal_info['label']}</h2>
            <p style='font-size: 1.5rem;'>総合スコア: {analysis_result['total_score']:.2f} / 5.0</p>
            <p>現在価格: ${analysis_result['current_price']:.2f} ({analysis_result['price_change_pct']:+.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 4専門家スコア表示
        st.subheader("👥 4専門家分析スコア")
        
        expert_cols = st.columns(4)
        expert_info = {
            'TECH': {'name': 'テクニカル分析', 'icon': '📊'},
            'FUND': {'name': 'ファンダメンタル', 'icon': '💰'},
            'MACRO': {'name': 'マクロ環境', 'icon': '🌍'},
            'RISK': {'name': 'リスク管理', 'icon': '⚡'}
        }
        
        for i, (expert, score) in enumerate(analysis_result['scores'].items()):
            with expert_cols[i]:
                # スコアに基づくクラス決定
                if score >= 4.0:
                    score_class = 'score-excellent'
                elif score >= 3.0:
                    score_class = 'score-good'
                elif score >= 2.0:
                    score_class = 'score-average'
                else:
                    score_class = 'score-poor'
                
                st.markdown(f"""
                <div style='text-align: center;'>
                    <h4>{expert_info[expert]['icon']} {expert_info[expert]['name']}</h4>
                    <div class="expert-score-bar">
                        <div class="expert-score-fill {score_class}" style="width: {score/5*100}%;">
                            {score:.1f}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # タイミングゲージ
        st.subheader("⏱️ エントリータイミング判定")
        
        timing_position = analysis_result['total_score'] / 5.0 * 100  # 0-100%に変換
        
        st.markdown(f"""
        <div class="timing-indicator">
            <div style="width: 100%;">
                <div class="timing-gauge">
                    <div class="timing-pointer" style="left: {timing_position}%;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <span>🔴🔴 売却</span>
                    <span>🟡 様子見</span>
                    <span>🟢 買い</span>
                    <span>🟢🟢 絶好</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # エントリー要因分析
        if st.session_state.get('show_expert_details', True):
            st.subheader("🔍 エントリー判断の詳細要因")
            
            factors = analysis_result['entry_factors']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ ポジティブ要因**")
                if factors['positive']:
                    for factor in factors['positive']:
                        st.markdown(f"- {factor['icon']} **{factor['factor']}** ({factor['type']})")
                else:
                    st.markdown("- 特になし")
            
            with col2:
                st.markdown("**⚠️ ネガティブ要因**")
                if factors['negative']:
                    for factor in factors['negative']:
                        st.markdown(f"- {factor['icon']} **{factor['factor']}** ({factor['type']})")
                else:
                    st.markdown("- 特になし")
        
        # インタラクティブチャート
        st.subheader("📈 価格チャート & テクニカル指標")
        
        chart = self._create_advanced_chart(df, ticker, analysis_result)
        st.plotly_chart(chart, use_container_width=True)
        
        # 詳細データ（エキスパンダー内）
        with st.expander("📊 詳細分析データ"):
            # 各専門家の詳細
            for expert, details in analysis_result['details'].items():
                st.markdown(f"**{expert_info[expert]['name']}詳細**")
                
                if 'signals' in details:
                    for signal in details['signals']:
                        st.write(f"- {signal}")
                
                # その他の詳細情報を表示
                for key, value in details.items():
                    if key != 'signals' and isinstance(value, (str, int, float)):
                        st.write(f"- {key}: {value}")
    
    @st.cache_data(ttl=300)
    def _get_stock_data(_self, ticker: str) -> pd.DataFrame:
        """株価データ取得（キャッシュ付き）"""
        period_days = st.session_state.get('period_days', 90)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days + 100)  # 余裕を持たせる
        
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                return pd.DataFrame()
            
            # テクニカル指標の計算
            # EMA
            df['EMA20'] = df['Close'].ewm(span=20).mean()
            df['EMA50'] = df['Close'].ewm(span=50).mean()
            
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
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            df['ATR'] = true_range.rolling(window=14).mean()
            
            # 必要な期間のデータのみ返す
            return df.tail(period_days)
            
        except Exception as e:
            st.error(f"データ取得エラー ({ticker}): {str(e)}")
            return pd.DataFrame()
    
    def _create_advanced_chart(self, df: pd.DataFrame, ticker: str, analysis_result: Dict) -> go.Figure:
        """高度なインタラクティブチャート作成"""
        # サブプロット作成
        rows = 2 if not st.session_state.get('show_volume', True) else 3
        row_heights = [0.7, 0.3] if rows == 2 else [0.6, 0.2, 0.2]
        
        fig = make_subplots(
            rows=rows, 
            cols=1,
            shared_xaxis=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=(['Price', 'Volume', 'RSI'] if rows == 3 else ['Price', 'RSI'])
        )
        
        # ローソク足
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=1, col=1
        )
        
        # テクニカル指標
        if st.session_state.get('show_technical', True):
            # EMA20
            if 'EMA20' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['EMA20'],
                        name='EMA20',
                        line=dict(color='orange', width=2)
                    ),
                    row=1, col=1
                )
            
            # SMA200
            if 'SMA200' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA200'],
                        name='SMA200',
                        line=dict(color='purple', width=2, dash='dash')
                    ),
                    row=1, col=1
                )
            
            # ボリンジャーバンド
            if all(col in df.columns for col in ['BB_upper', 'BB_lower']):
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['BB_upper'],
                        name='BB Upper',
                        line=dict(color='gray', width=1),
                        showlegend=False
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['BB_lower'],
                        name='BB',
                        fill='tonexty',
                        fillcolor='rgba(128,128,128,0.1)',
                        line=dict(color='gray', width=1)
                    ),
                    row=1, col=1
                )
        
        # エントリーシグナル表示
        if st.session_state.get('show_signals', True):
            signal_info = self.analyzer.signals[analysis_result['signal']]
            latest_price = df.iloc[-1]['Close']
            
            # 最新のシグナルをマーク
            fig.add_trace(
                go.Scatter(
                    x=[df.index[-1]],
                    y=[latest_price * 1.02],  # 少し上に表示
                    mode='markers+text',
                    marker=dict(
                        symbol='triangle-down',
                        size=20,
                        color=signal_info['color']
                    ),
                    text=[signal_info['label']],
                    textposition="top center",
                    name='Current Signal'
                ),
                row=1, col=1
            )
        
        # 出来高
        if st.session_state.get('show_volume', True) and 'Volume' in df.columns:
            colors = ['red' if close < open else 'green' 
                     for close, open in zip(df['Close'], df['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['Volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.5
                ),
                row=2, col=1
            )
        
        # RSI
        rsi_row = 2 if rows == 2 else 3
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    name='RSI',
                    line=dict(color='blue', width=2)
                ),
                row=rsi_row, col=1
            )
            
            # RSIレベルライン
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="過買い", row=rsi_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         annotation_text="過売り", row=rsi_row, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", row=rsi_row, col=1)
        
        # レイアウト設定
        fig.update_layout(
            title={
                'text': f'{ticker} - {analysis_result["signal"]} Signal (Score: {analysis_result["total_score"]:.2f})',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=800,
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Y軸ラベル
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        if st.session_state.get('show_volume', True):
            fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=rsi_row, col=1)
        
        return fig

# メイン実行
if __name__ == "__main__":
    app = EnhancedDashboardApp()
    app.run()