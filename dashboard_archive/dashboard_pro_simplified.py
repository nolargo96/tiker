#!/usr/bin/env python3
"""
Tiker Dashboard Pro - 簡素化版
9銘柄ポートフォリオ表示に特化したStreamlitダッシュボード
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import time
import warnings
warnings.filterwarnings('ignore')

# 既存システムの活用
from unified_stock_analyzer import calculate_tech_score, calculate_fund_score, calculate_macro_score, calculate_risk_score
from stock_analyzer_lib import ConfigManager

# ページ設定
st.set_page_config(
    page_title="🚀 Tiker Dashboard Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 最小限のCSS
st.markdown("""
<style>
.main { padding: 0rem 1rem; }
.metric-box {
    background: white;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.signal-strong-buy { color: #28a745; font-weight: bold; }
.signal-buy { color: #5cb85c; }
.signal-hold { color: #ffc107; }
.signal-sell { color: #dc3545; }
.signal-strong-sell { color: #8b0000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

class SimplifiedDashboardPro:
    """簡素化版ダッシュボード分析システム"""
    
    def __init__(self):
        self.config = ConfigManager()
        
        # 固定の9銘柄ポートフォリオ定義
        self.portfolio = {
            'TSLA': {'weight': 20, 'name': 'Tesla Inc', 'sector': 'EV・自動運転', 'color': '#e31837'},
            'FSLR': {'weight': 20, 'name': 'First Solar', 'sector': 'ソーラーパネル', 'color': '#ffd700'},
            'RKLB': {'weight': 10, 'name': 'Rocket Lab', 'sector': '小型ロケット', 'color': '#ff6b35'},
            'ASTS': {'weight': 10, 'name': 'AST SpaceMobile', 'sector': '衛星通信', 'color': '#4a90e2'},
            'OKLO': {'weight': 10, 'name': 'Oklo Inc', 'sector': 'SMR原子炉', 'color': '#50c878'},
            'JOBY': {'weight': 10, 'name': 'Joby Aviation', 'sector': 'eVTOL', 'color': '#9b59b6'},
            'OII': {'weight': 10, 'name': 'Oceaneering', 'sector': '海洋エンジニアリング', 'color': '#1abc9c'},
            'LUNR': {'weight': 5, 'name': 'Intuitive Machines', 'sector': '月面探査', 'color': '#34495e'},
            'RDW': {'weight': 5, 'name': 'Redwire Corp', 'sector': '宇宙製造', 'color': '#e74c3c'}
        }
        
        # シグナル定義
        self.signals = {
            'STRONG_BUY': {'label': '絶好の買い場', 'color': '#28a745', 'icon': '🟢🟢'},
            'BUY': {'label': '買い推奨', 'color': '#5cb85c', 'icon': '🟢'},
            'HOLD': {'label': '様子見', 'color': '#ffc107', 'icon': '🟡'},
            'SELL': {'label': '売却検討', 'color': '#dc3545', 'icon': '🔴'},
            'STRONG_SELL': {'label': '即売却推奨', 'color': '#8b0000', 'icon': '🔴🔴'}
        }
    
    @st.cache_data(ttl=300)
    def fetch_batch_data(_self, tickers: List[str]) -> Dict[str, pd.DataFrame]:
        """全銘柄のデータを並列で一括取得"""
        data_cache = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(_self._fetch_single_stock, ticker): ticker 
                      for ticker in tickers}
            
            for future in futures:
                ticker = futures[future]
                try:
                    df = future.result()
                    if df is not None and not df.empty:
                        data_cache[ticker] = df
                except Exception as e:
                    st.error(f"{ticker}: データ取得エラー - {str(e)}")
        
        return data_cache
    
    def _fetch_single_stock(self, ticker: str) -> Optional[pd.DataFrame]:
        """単一銘柄のデータ取得"""
        try:
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            df = stock.history(start=start_date, end=end_date)
            if df.empty:
                return None
            
            # 技術指標を追加
            df['EMA20'] = df['Close'].ewm(span=20).mean()
            df['EMA50'] = df['Close'].ewm(span=50).mean()
            df['SMA200'] = df['Close'].rolling(window=200).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            return df
            
        except Exception as e:
            return None
    
    def analyze_stock(self, ticker: str, df: pd.DataFrame) -> Dict:
        """個別銘柄の分析"""
        if df.empty or len(df) < 50:
            return self._create_empty_result(ticker)
        
        latest_data = df.iloc[-1]
        
        # 4専門家スコア計算
        tech_score = calculate_tech_score(df)
        fund_score = calculate_fund_score(ticker, latest_data)
        macro_score = calculate_macro_score(ticker)
        risk_score = calculate_risk_score(df, self.portfolio[ticker]['weight'])
        
        # 総合スコア
        total_score = (tech_score + fund_score + macro_score + risk_score) / 4
        
        # シグナル判定
        signal = self._determine_signal(total_score)
        
        # 価格変化率
        price_change_pct = 0
        if len(df) >= 2:
            price_change_pct = ((latest_data['Close'] - df.iloc[-2]['Close']) / 
                              df.iloc[-2]['Close'] * 100)
        
        return {
            'ticker': ticker,
            'name': self.portfolio[ticker]['name'],
            'sector': self.portfolio[ticker]['sector'],
            'weight': self.portfolio[ticker]['weight'],
            'current_price': latest_data['Close'],
            'price_change_pct': price_change_pct,
            'signal': signal,
            'total_score': total_score,
            'scores': {
                'TECH': tech_score,
                'FUND': fund_score,
                'MACRO': macro_score,
                'RISK': risk_score
            },
            'rsi': latest_data.get('RSI', 50),
            'volume': latest_data['Volume']
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
    
    def _create_empty_result(self, ticker: str) -> Dict:
        """空の結果を作成"""
        return {
            'ticker': ticker,
            'name': self.portfolio[ticker]['name'],
            'sector': self.portfolio[ticker]['sector'],
            'weight': self.portfolio[ticker]['weight'],
            'current_price': 0,
            'price_change_pct': 0,
            'signal': 'HOLD',
            'total_score': 2.5,
            'scores': {'TECH': 2.5, 'FUND': 2.5, 'MACRO': 2.5, 'RISK': 2.5},
            'rsi': 50,
            'volume': 0
        }

class DashboardApp:
    """簡素化版ダッシュボードアプリケーション"""
    
    def __init__(self):
        self.analyzer = SimplifiedDashboardPro()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """セッション状態の初期化"""
        if 'portfolio_data' not in st.session_state:
            st.session_state.portfolio_data = {}
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
    
    def run(self):
        """メインアプリケーション実行"""
        self._render_header()
        self._render_main_content()
        self._render_sidebar()
    
    def _render_header(self):
        """ヘッダー部分の描画"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("💎 Tiker Dashboard Pro")
            st.caption("9銘柄ポートフォリオ分析ダッシュボード")
        
        with col2:
            if st.button("🔄 データ更新", type="primary", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        with col3:
            if st.session_state.last_update:
                st.metric("最終更新", 
                         st.session_state.last_update.strftime("%H:%M:%S"))
    
    def _render_sidebar(self):
        """サイドバーの描画"""
        with st.sidebar:
            st.header("📊 ポートフォリオ構成")
            
            # ポートフォリオ配分の表示
            for ticker, info in self.analyzer.portfolio.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{ticker}** - {info['name']}")
                with col2:
                    st.write(f"{info['weight']}%")
            
            st.divider()
            
            # セクター別配分
            st.subheader("🏭 セクター配分")
            sector_weights = {}
            for ticker, info in self.analyzer.portfolio.items():
                sector = info['sector']
                sector_weights[sector] = sector_weights.get(sector, 0) + info['weight']
            
            for sector, weight in sorted(sector_weights.items(), 
                                        key=lambda x: x[1], reverse=True):
                st.write(f"{sector}: {weight}%")
    
    def _render_main_content(self):
        """メインコンテンツの描画"""
        # データ取得
        with st.spinner('データを取得中...'):
            tickers = list(self.analyzer.portfolio.keys())
            data = self.analyzer.fetch_batch_data(tickers)
            st.session_state.portfolio_data = data
            st.session_state.last_update = datetime.now()
        
        # タブ作成
        tab1, tab2, tab3 = st.tabs(["📊 銘柄一覧", "📈 パフォーマンス", "🎯 シグナル分析"])
        
        with tab1:
            self._render_stocks_overview()
        
        with tab2:
            self._render_performance_analysis()
        
        with tab3:
            self._render_signal_analysis()
    
    def _render_stocks_overview(self):
        """銘柄一覧の表示"""
        st.subheader("📊 9銘柄ポートフォリオ概要")
        
        # 分析実行
        results = []
        for ticker in self.analyzer.portfolio.keys():
            if ticker in st.session_state.portfolio_data:
                df = st.session_state.portfolio_data[ticker]
                result = self.analyzer.analyze_stock(ticker, df)
                results.append(result)
                st.session_state.analysis_results[ticker] = result
        
        # 結果を2列で表示
        cols = st.columns(2)
        for i, result in enumerate(results):
            with cols[i % 2]:
                self._render_stock_card(result)
    
    def _render_stock_card(self, result: Dict):
        """個別銘柄カードの表示"""
        signal_info = self.analyzer.signals[result['signal']]
        
        # カード表示
        with st.container():
            # ヘッダー行
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### {result['ticker']} - {result['name']}")
                st.caption(f"{result['sector']} | 配分: {result['weight']}%")
            
            with col2:
                st.metric("現在価格", 
                         f"${result['current_price']:.2f}",
                         f"{result['price_change_pct']:+.1f}%")
            
            with col3:
                st.markdown(f"""
                <div style='text-align: center; padding: 10px;'>
                    <div style='font-size: 24px;'>{signal_info['icon']}</div>
                    <div style='color: {signal_info['color']}; font-weight: bold;'>
                        {signal_info['label']}
                    </div>
                    <div>スコア: {result['total_score']:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # スコア詳細
            with st.expander("詳細スコア"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("TECH", f"{result['scores']['TECH']:.1f}")
                with col2:
                    st.metric("FUND", f"{result['scores']['FUND']:.1f}")
                with col3:
                    st.metric("MACRO", f"{result['scores']['MACRO']:.1f}")
                with col4:
                    st.metric("RISK", f"{result['scores']['RISK']:.1f}")
            
            st.divider()
    
    def _render_performance_analysis(self):
        """パフォーマンス分析の表示"""
        st.subheader("📈 ポートフォリオパフォーマンス")
        
        # パフォーマンスデータ収集
        performance_data = []
        for ticker, result in st.session_state.analysis_results.items():
            performance_data.append({
                'Ticker': ticker,
                'Name': result['name'],
                'Price': result['current_price'],
                'Change %': result['price_change_pct'],
                'Signal': self.analyzer.signals[result['signal']]['label'],
                'Score': result['total_score']
            })
        
        # データフレーム作成
        df = pd.DataFrame(performance_data)
        
        # ソート（スコアの高い順）
        df = df.sort_values('Score', ascending=False)
        
        # テーブル表示
        st.dataframe(
            df.style.format({
                'Price': '${:.2f}',
                'Change %': '{:+.1f}%',
                'Score': '{:.1f}'
            }).background_gradient(subset=['Score'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # パフォーマンスチャート
        col1, col2 = st.columns(2)
        
        with col1:
            # セクター別配分円グラフ
            sector_data = {}
            for ticker, info in self.analyzer.portfolio.items():
                sector = info['sector']
                sector_data[sector] = sector_data.get(sector, 0) + info['weight']
            
            fig = go.Figure(data=[go.Pie(
                labels=list(sector_data.keys()),
                values=list(sector_data.values()),
                hole=0.3
            )])
            fig.update_layout(title="セクター配分", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # スコア分布
            fig = go.Figure(data=[go.Bar(
                x=df['Ticker'],
                y=df['Score'],
                marker_color=['#28a745' if s >= 3.5 else '#ffc107' if s >= 2.5 else '#dc3545' 
                             for s in df['Score']]
            )])
            fig.update_layout(
                title="銘柄別総合スコア",
                xaxis_title="銘柄",
                yaxis_title="スコア",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_signal_analysis(self):
        """シグナル分析の表示"""
        st.subheader("🎯 シグナル分析")
        
        # シグナル分布を集計
        signal_counts = {}
        for result in st.session_state.analysis_results.values():
            signal = result['signal']
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
        
        # シグナル別銘柄リスト
        for signal, info in self.analyzer.signals.items():
            if signal in signal_counts:
                st.markdown(f"### {info['icon']} {info['label']} ({signal_counts[signal]}銘柄)")
                
                tickers = [r['ticker'] for r in st.session_state.analysis_results.values() 
                          if r['signal'] == signal]
                
                if tickers:
                    cols = st.columns(len(tickers))
                    for i, ticker in enumerate(tickers):
                        with cols[i]:
                            result = st.session_state.analysis_results[ticker]
                            st.metric(ticker, 
                                     f"${result['current_price']:.2f}",
                                     f"{result['price_change_pct']:+.1f}%")
                
                st.divider()

# メイン実行
if __name__ == "__main__":
    app = DashboardApp()
    app.run()