#!/usr/bin/env python3
"""
Tiker Portfolio Dashboard - シンプル版
9銘柄のポートフォリオを見やすく表示
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import time

# ページ設定
st.set_page_config(
    page_title="🚀 Tiker Portfolio Dashboard",
    page_icon="📈",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
.stock-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.buy-signal { color: #28a745; font-weight: bold; }
.hold-signal { color: #ffc107; font-weight: bold; }
.sell-signal { color: #dc3545; font-weight: bold; }
.ticker-symbol { font-size: 24px; font-weight: bold; }
.price-up { color: #28a745; }
.price-down { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

class SimplePortfolioDashboard:
    def __init__(self):
        # ポートフォリオ構成（9銘柄）
        self.portfolio = {
            "TSLA": {"name": "Tesla", "weight": 20, "sector": "EV・自動運転"},
            "FSLR": {"name": "First Solar", "weight": 20, "sector": "ソーラーパネル"},
            "RKLB": {"name": "Rocket Lab", "weight": 10, "sector": "小型ロケット"},
            "ASTS": {"name": "AST SpaceMobile", "weight": 10, "sector": "衛星通信"},
            "OKLO": {"name": "Oklo", "weight": 10, "sector": "SMR原子炉"},
            "JOBY": {"name": "Joby Aviation", "weight": 10, "sector": "eVTOL"},
            "OII": {"name": "Oceaneering", "weight": 10, "sector": "海洋エンジニアリング"},
            "LUNR": {"name": "Intuitive Machines", "weight": 5, "sector": "月面探査"},
            "RDW": {"name": "Redwire", "weight": 5, "sector": "宇宙製造"}
        }
        
        # キャッシュ
        if 'stock_data' not in st.session_state:
            st.session_state.stock_data = {}
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
    
    @st.cache_data(ttl=300)  # 5分間キャッシュ
    def fetch_stock_data(_self, ticker):
        """個別銘柄のデータ取得"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1mo")
            info = stock.info
            
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
                change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price != 0 else 0
                
                # シンプルなシグナル判定
                sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
                rsi = _self.calculate_rsi(df['Close'])
                
                if current_price > sma20 and rsi < 70:
                    signal = "買い"
                    signal_icon = "🟢"
                elif rsi > 70:
                    signal = "売り"
                    signal_icon = "🔴"
                else:
                    signal = "様子見"
                    signal_icon = "🟡"
                
                return {
                    'success': True,
                    'ticker': ticker,
                    'price': current_price,
                    'change_pct': change_pct,
                    'signal': signal,
                    'signal_icon': signal_icon,
                    'df': df
                }
        except Exception as e:
            return {'success': False, 'ticker': ticker, 'error': str(e)}
    
    def calculate_rsi(self, prices, period=14):
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs)).iloc[-1]
    
    def create_mini_chart(self, df, ticker):
        """ミニチャート作成"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name=ticker,
            line=dict(color='#1f77b4', width=2)
        ))
        fig.update_layout(
            height=150,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(showticklabels=True, showgrid=True)
        )
        return fig
    
    def display_stock_card(self, data):
        """個別銘柄カード表示"""
        if data['success']:
            stock_info = self.portfolio[data['ticker']]
            price_class = "price-up" if data['change_pct'] >= 0 else "price-down"
            
            st.markdown(f"""
            <div class="stock-card">
                <div class="ticker-symbol">{data['ticker']}</div>
                <div>{stock_info['name']}</div>
                <div style="color: #666; font-size: 12px;">{stock_info['sector']} | {stock_info['weight']}%</div>
                <div style="margin: 10px 0;">
                    <span style="font-size: 20px;">${data['price']:.2f}</span>
                    <span class="{price_class}">({data['change_pct']:+.2f}%)</span>
                </div>
                <div>{data['signal_icon']} <span class="{data['signal'].lower()}-signal">{data['signal']}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            # ミニチャート
            if 'df' in data:
                st.plotly_chart(self.create_mini_chart(data['df'], data['ticker']), use_container_width=True)
        else:
            st.error(f"{data['ticker']}: データ取得エラー")
    
    def run(self):
        """メイン実行"""
        st.title("🚀 Tiker Portfolio Dashboard")
        st.markdown("### 9銘柄のリアルタイムポートフォリオ監視")
        
        # データ更新ボタン
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔄 データ更新"):
                st.session_state.stock_data = {}
                st.session_state.last_update = None
        
        with col2:
            if st.session_state.last_update:
                st.info(f"最終更新: {st.session_state.last_update}")
        
        # 全銘柄のデータ取得
        with st.spinner("データ取得中..."):
            stock_data_list = []
            for ticker in self.portfolio.keys():
                data = self.fetch_stock_data(ticker)
                stock_data_list.append(data)
            
            st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 3列レイアウトで銘柄表示
        st.markdown("### 📊 個別銘柄")
        cols = st.columns(3)
        for i, data in enumerate(stock_data_list):
            with cols[i % 3]:
                self.display_stock_card(data)
        
        # サマリーテーブル
        st.markdown("### 📋 ポートフォリオサマリー")
        summary_data = []
        total_value = 0
        
        for data in stock_data_list:
            if data['success']:
                stock_info = self.portfolio[data['ticker']]
                value = 10000 * stock_info['weight'] / 100  # 仮の投資額
                total_value += value
                summary_data.append({
                    'ティッカー': data['ticker'],
                    '銘柄名': stock_info['name'],
                    'セクター': stock_info['sector'],
                    '配分': f"{stock_info['weight']}%",
                    '現在価格': f"${data['price']:.2f}",
                    '前日比': f"{data['change_pct']:+.2f}%",
                    'シグナル': f"{data['signal_icon']} {data['signal']}",
                    '評価額': f"${value:,.0f}"
                })
        
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
        
        # 合計表示
        st.markdown(f"### 💰 ポートフォリオ合計: ${total_value:,.0f}")

if __name__ == "__main__":
    dashboard = SimplePortfolioDashboard()
    dashboard.run()