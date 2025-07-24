#!/usr/bin/env python3
"""
Tiker Interactive Dashboard - 修正版
NumPy互換性問題を解決したバージョン
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
# plotly.expressを使わずに直接graph_objectsを使用
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

# 既存システムの活用
try:
    from unified_stock_analyzer import calculate_tech_score, calculate_fund_score, calculate_macro_score, calculate_risk_score
    from stock_analyzer_lib import ConfigManager, TechnicalIndicators, StockDataManager
    from cache_manager import CacheManager
    SYSTEM_AVAILABLE = True
except ImportError:
    SYSTEM_AVAILABLE = False
    st.warning("既存システムが見つかりません。基本機能のみで動作します。")

# ページ設定
st.set_page_config(
    page_title="🚀 Tiker Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
.main { padding: 0rem 1rem; }

.entry-signal-card {
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 1rem 0;
    border: 2px solid;
}

.signal-buy {
    background-color: #d4f1d4;
    border-color: #28a745;
    color: #155724;
}

.signal-hold {
    background-color: #fff9e6;
    border-color: #ffc107;
    color: #856404;
}

.signal-sell {
    background-color: #ffe0e0;
    border-color: #dc3545;
    color: #721c24;
}

.portfolio-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

class SimpleEntryAnalyzer:
    """シンプルなエントリータイミング分析"""
    
    def __init__(self):
        self.signals = {
            'BUY': {'label': '買い推奨', 'color': '#28a745', 'icon': '🟢'},
            'HOLD': {'label': '様子見', 'color': '#ffc107', 'icon': '🟡'},
            'SELL': {'label': '売却検討', 'color': '#dc3545', 'icon': '🔴'}
        }
    
    def analyze_entry_timing(self, ticker: str, df: pd.DataFrame) -> Dict[str, Any]:
        """エントリータイミング分析"""
        if df.empty or len(df) < 20:
            return self._create_empty_result()
        
        latest = df.iloc[-1]
        score = 2.5  # デフォルトスコア
        
        # 簡易的なテクニカル分析
        if 'Close' in df.columns:
            # 価格トレンド
            sma20 = df['Close'].rolling(20).mean().iloc[-1]
            if latest['Close'] > sma20:
                score += 0.5
            else:
                score -= 0.5
            
            # RSI計算
            if len(df) >= 14:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain.iloc[-1] / loss.iloc[-1] if loss.iloc[-1] != 0 else 0
                rsi = 100 - (100 / (1 + rs))
                
                if 30 <= rsi <= 70:
                    score += 0.3
                elif rsi < 30:
                    score += 0.8  # 売られ過ぎ
                else:
                    score -= 0.3  # 買われ過ぎ
        
        # シグナル判定
        if score >= 3.5:
            signal = 'BUY'
        elif score >= 2.5:
            signal = 'HOLD'
        else:
            signal = 'SELL'
        
        return {
            'signal': signal,
            'score': score,
            'current_price': latest['Close'],
            'price_change_pct': ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100) if len(df) > 1 else 0
        }
    
    def _create_empty_result(self) -> Dict[str, Any]:
        return {
            'signal': 'HOLD',
            'score': 2.5,
            'current_price': 0,
            'price_change_pct': 0
        }

class DashboardApp:
    """メインダッシュボードアプリケーション"""
    
    def __init__(self):
        self.analyzer = SimpleEntryAnalyzer()
        self.portfolio = {
            'TSLA': {'weight': 20, 'name': 'Tesla Inc', 'sector': 'EV/Tech'},
            'FSLR': {'weight': 20, 'name': 'First Solar', 'sector': 'Solar Energy'},
            'RKLB': {'weight': 10, 'name': 'Rocket Lab', 'sector': 'Space'},
            'ASTS': {'weight': 10, 'name': 'AST SpaceMobile', 'sector': 'Satellite'},
            'OKLO': {'weight': 10, 'name': 'Oklo Inc', 'sector': 'Nuclear'},
            'JOBY': {'weight': 10, 'name': 'Joby Aviation', 'sector': 'eVTOL'},
            'OII': {'weight': 10, 'name': 'Oceaneering', 'sector': 'Marine'},
            'LUNR': {'weight': 5, 'name': 'Intuitive Machines', 'sector': 'Space'},
            'RDW': {'weight': 5, 'name': 'Redwire Corp', 'sector': 'Space'}
        }
    
    def run(self):
        """アプリケーション実行"""
        self._render_header()
        self._render_sidebar()
        self._render_main_content()
    
    def _render_header(self):
        """ヘッダー描画"""
        st.markdown("""
        <div class="portfolio-header">
            <h1>🚀 Tiker Dashboard</h1>
            <p>リアルタイム株式分析 & エントリータイミング判定</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """サイドバー設定"""
        with st.sidebar:
            st.header("⚙️ 分析設定")
            
            # データ更新
            if st.button("🔄 データ更新", type="primary"):
                st.cache_data.clear()
                st.rerun()
            
            # 期間設定
            period_days = st.selectbox(
                "分析期間",
                [30, 90, 180, 365],
                index=1
            )
            
            # 表示設定
            st.subheader("📊 表示設定")
            show_volume = st.checkbox("出来高表示", value=True)
            show_indicators = st.checkbox("テクニカル指標", value=True)
            
            st.session_state.update({
                'period_days': period_days,
                'show_volume': show_volume,
                'show_indicators': show_indicators
            })
    
    def _render_main_content(self):
        """メインコンテンツ"""
        # タブ作成
        tabs = st.tabs(["📊 ポートフォリオ概要"] + [f"{ticker}" for ticker in self.portfolio.keys()])
        
        # ポートフォリオ概要
        with tabs[0]:
            self._render_portfolio_overview()
        
        # 個別銘柄
        for i, ticker in enumerate(self.portfolio.keys(), 1):
            with tabs[i]:
                self._render_stock_analysis(ticker)
    
    def _render_portfolio_overview(self):
        """ポートフォリオ概要表示"""
        st.header("📊 ポートフォリオ総合分析")
        
        # シグナル一覧
        st.subheader("🎯 エントリーシグナル一覧")
        
        signals_data = []
        for ticker in self.portfolio.keys():
            df = self._get_stock_data(ticker)
            if not df.empty:
                result = self.analyzer.analyze_entry_timing(ticker, df)
                signal_info = self.analyzer.signals[result['signal']]
                
                signals_data.append({
                    'Ticker': ticker,
                    'Name': self.portfolio[ticker]['name'],
                    'Signal': f"{signal_info['icon']} {signal_info['label']}",
                    'Score': f"{result['score']:.2f}",
                    'Price': f"${result['current_price']:.2f}",
                    'Change%': f"{result['price_change_pct']:+.1f}%"
                })
        
        if signals_data:
            df_signals = pd.DataFrame(signals_data)
            st.dataframe(df_signals, use_container_width=True, hide_index=True)
        
        # シグナル分布（手動で円グラフ作成）
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.subheader("📈 シグナル分布")
            if signals_data:
                # シグナルをカウント
                signal_counts = {}
                for data in signals_data:
                    signal_type = data['Signal'].split()[1]  # アイコンを除去
                    signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
                
                # Plotlyで円グラフ作成
                fig = go.Figure(data=[go.Pie(
                    labels=list(signal_counts.keys()),
                    values=list(signal_counts.values()),
                    marker=dict(colors=['#28a745', '#ffc107', '#dc3545'])
                )])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_stock_analysis(self, ticker: str):
        """個別銘柄分析"""
        stock_info = self.portfolio[ticker]
        st.header(f"📈 {ticker} - {stock_info['name']}")
        
        # データ取得
        df = self._get_stock_data(ticker)
        if df.empty:
            st.error(f"{ticker}のデータ取得に失敗しました")
            return
        
        # エントリー分析
        result = self.analyzer.analyze_entry_timing(ticker, df)
        signal_info = self.analyzer.signals[result['signal']]
        
        # シグナル表示
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="entry-signal-card signal-{result['signal'].lower()}">
                <h3>{signal_info['icon']} {signal_info['label']}</h3>
                <p>スコア: {result['score']:.2f} / 5.0</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric(
                "現在価格",
                f"${result['current_price']:.2f}",
                f"{result['price_change_pct']:+.1f}%"
            )
        
        with col3:
            st.metric(
                "分析期間",
                f"{st.session_state.get('period_days', 90)}日",
                f"データ点数: {len(df)}"
            )
        
        # チャート表示
        st.subheader("📊 価格チャート")
        chart = self._create_chart(df, ticker)
        st.plotly_chart(chart, use_container_width=True)
    
    @st.cache_data(ttl=300)
    def _get_stock_data(_self, ticker: str) -> pd.DataFrame:
        """株価データ取得"""
        period_days = st.session_state.get('period_days', 90)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days + 50)
        
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                return pd.DataFrame()
            
            # 基本的な移動平均を追加
            df['SMA20'] = df['Close'].rolling(20).mean()
            df['SMA50'] = df['Close'].rolling(50).mean()
            
            return df.tail(period_days)
            
        except Exception as e:
            st.error(f"データ取得エラー: {str(e)}")
            return pd.DataFrame()
    
    def _create_chart(self, df: pd.DataFrame, ticker: str) -> go.Figure:
        """チャート作成"""
        fig = make_subplots(
            rows=2 if st.session_state.get('show_volume', True) else 1,
            cols=1,
            shared_xaxis=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3] if st.session_state.get('show_volume', True) else [1]
        )
        
        # ローソク足
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # 移動平均線
        if st.session_state.get('show_indicators', True):
            if 'SMA20' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA20'],
                        name='SMA20',
                        line=dict(color='orange', width=1)
                    ),
                    row=1, col=1
                )
            
            if 'SMA50' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA50'],
                        name='SMA50',
                        line=dict(color='blue', width=1)
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
        
        # レイアウト
        fig.update_layout(
            title=f'{ticker} チャート',
            height=600,
            xaxis_rangeslider_visible=False,
            showlegend=True
        )
        
        # Y軸ラベル
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        if st.session_state.get('show_volume', True):
            fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig

# アプリケーション実行
if __name__ == "__main__":
    app = DashboardApp()
    app.run()