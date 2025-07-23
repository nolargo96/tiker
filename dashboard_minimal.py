#!/usr/bin/env python3
"""
Tiker Dashboard - 最小動作版
外部ライブラリ依存を最小化したバージョン
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random  # yfinanceの代わりにダミーデータ生成用

# ページ設定
st.set_page_config(
    page_title="🚀 Tiker Dashboard (Demo)",
    page_icon="📈",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
.entry-card {
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    text-align: center;
}
.buy-signal {
    background-color: #d4f1d4;
    border: 2px solid #28a745;
}
.hold-signal {
    background-color: #fff9e6;
    border: 2px solid #ffc107;
}
.sell-signal {
    background-color: #ffe0e0;
    border: 2px solid #dc3545;
}
</style>
""", unsafe_allow_html=True)

class DashboardDemo:
    def __init__(self):
        self.portfolio = {
            'TSLA': {'name': 'Tesla Inc', 'weight': 20, 'price': 248.50},
            'FSLR': {'name': 'First Solar', 'weight': 20, 'price': 195.30},
            'RKLB': {'name': 'Rocket Lab', 'weight': 10, 'price': 15.87},
            'ASTS': {'name': 'AST SpaceMobile', 'weight': 10, 'price': 12.45},
            'OKLO': {'name': 'Oklo Inc', 'weight': 10, 'price': 8.92},
            'JOBY': {'name': 'Joby Aviation', 'weight': 10, 'price': 6.73},
            'OII': {'name': 'Oceaneering', 'weight': 10, 'price': 21.34},
            'LUNR': {'name': 'Intuitive Machines', 'weight': 5, 'price': 4.56},
            'RDW': {'name': 'Redwire Corp', 'weight': 5, 'price': 3.21}
        }
    
    def generate_dummy_data(self, ticker, days=90):
        """ダミーデータ生成（デモ用）"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = self.portfolio[ticker]['price']
        
        # ランダムウォークで価格データ生成
        prices = [base_price]
        for _ in range(1, days):
            change = random.uniform(-0.05, 0.05) * prices[-1]
            prices.append(prices[-1] + change)
        
        df = pd.DataFrame({
            'Date': dates,
            'Close': prices,
            'Open': [p * random.uniform(0.98, 1.02) for p in prices],
            'High': [p * random.uniform(1.01, 1.05) for p in prices],
            'Low': [p * random.uniform(0.95, 0.99) for p in prices],
            'Volume': [random.randint(1000000, 5000000) for _ in range(days)]
        })
        df.set_index('Date', inplace=True)
        
        # 移動平均追加
        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()
        
        return df
    
    def calculate_signal(self, df):
        """簡易シグナル計算"""
        if df.empty:
            return 'HOLD', 2.5
        
        latest_price = df['Close'].iloc[-1]
        sma20 = df['SMA20'].iloc[-1] if 'SMA20' in df.columns else latest_price
        
        if pd.isna(sma20):
            return 'HOLD', 2.5
        
        # 価格とSMA20の関係でシグナル判定
        if latest_price > sma20 * 1.02:
            return 'BUY', 4.0
        elif latest_price < sma20 * 0.98:
            return 'SELL', 1.5
        else:
            return 'HOLD', 2.5
    
    def run(self):
        # ヘッダー
        st.markdown("""
        # 🚀 Tiker Dashboard (Demo Mode)
        ### エントリータイミング判定システム
        """)
        
        st.info("📌 デモモード: 実際の株価データの代わりにサンプルデータを表示しています")
        
        # サイドバー
        with st.sidebar:
            st.header("⚙️ 設定")
            
            period = st.selectbox("分析期間", [30, 90, 180], index=1)
            
            if st.button("🔄 データ更新"):
                st.cache_data.clear()
                st.rerun()
            
            st.divider()
            st.markdown("""
            **シグナル説明**
            - 🟢 BUY: 買い推奨
            - 🟡 HOLD: 様子見
            - 🔴 SELL: 売却検討
            """)
        
        # メインコンテンツ
        tabs = st.tabs(["📊 ポートフォリオ概要"] + [ticker for ticker in self.portfolio.keys()])
        
        # ポートフォリオ概要
        with tabs[0]:
            st.header("📊 ポートフォリオ総合分析")
            
            # シグナル一覧
            signals_data = []
            for ticker, info in self.portfolio.items():
                df = self.generate_dummy_data(ticker, period)
                signal, score = self.calculate_signal(df)
                
                signal_emoji = {'BUY': '🟢', 'HOLD': '🟡', 'SELL': '🔴'}[signal]
                
                signals_data.append({
                    'Ticker': ticker,
                    'Name': info['name'],
                    'Signal': f"{signal_emoji} {signal}",
                    'Score': score,
                    'Price': f"${df['Close'].iloc[-1]:.2f}",
                    'Change%': f"{((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100):.1f}%"
                })
            
            # データフレーム表示
            df_signals = pd.DataFrame(signals_data)
            st.dataframe(df_signals, use_container_width=True, hide_index=True)
            
            # シグナル分布
            col1, col2 = st.columns([2, 1])
            with col2:
                st.subheader("シグナル分布")
                
                signal_counts = {'BUY': 0, 'HOLD': 0, 'SELL': 0}
                for data in signals_data:
                    signal_type = data['Signal'].split()[1]
                    signal_counts[signal_type] += 1
                
                fig = go.Figure(data=[go.Pie(
                    labels=list(signal_counts.keys()),
                    values=list(signal_counts.values()),
                    marker_colors=['#28a745', '#ffc107', '#dc3545']
                )])
                fig.update_layout(height=300, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
        
        # 個別銘柄タブ
        for i, ticker in enumerate(self.portfolio.keys(), 1):
            with tabs[i]:
                self.render_stock_detail(ticker, period)
    
    def render_stock_detail(self, ticker, period):
        """個別銘柄詳細"""
        info = self.portfolio[ticker]
        st.header(f"📈 {ticker} - {info['name']}")
        
        # データ生成
        df = self.generate_dummy_data(ticker, period)
        signal, score = self.calculate_signal(df)
        
        # メトリクス
        col1, col2, col3 = st.columns(3)
        
        with col1:
            signal_class = signal.lower() + '-signal'
            signal_emoji = {'BUY': '🟢', 'HOLD': '🟡', 'SELL': '🔴'}[signal]
            
            st.markdown(f"""
            <div class="entry-card {signal_class}">
                <h3>{signal_emoji} {signal}</h3>
                <p>スコア: {score:.1f}/5.0</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            change_pct = (current_price - prev_price) / prev_price * 100
            
            st.metric(
                "現在価格",
                f"${current_price:.2f}",
                f"{change_pct:+.1f}%"
            )
        
        with col3:
            st.metric(
                "配分",
                f"{info['weight']}%",
                f"ポートフォリオ内"
            )
        
        # チャート
        st.subheader("価格チャート")
        
        fig = go.Figure()
        
        # ローソク足
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ))
        
        # 移動平均線
        if 'SMA20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA20'],
                name='SMA20',
                line=dict(color='orange', width=1)
            ))
        
        if 'SMA50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA50'],
                name='SMA50',
                line=dict(color='blue', width=1)
            ))
        
        fig.update_layout(
            title=f'{ticker} - {period}日間',
            yaxis_title='Price ($)',
            height=500,
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 出来高
        st.subheader("出来高")
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color='lightblue'
        ))
        volume_fig.update_layout(
            height=200,
            yaxis_title='Volume'
        )
        st.plotly_chart(volume_fig, use_container_width=True)

# アプリ実行
if __name__ == "__main__":
    app = DashboardDemo()
    app.run()