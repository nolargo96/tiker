#!/usr/bin/env python3
"""
Tiker Portfolio Hybrid Dashboard
portfolio_hybrid_reportの主要機能をStreamlitで可視化
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import glob
from typing import Dict, List, Optional

# ページ設定
st.set_page_config(
    page_title="📊 Tiker Hybrid Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}
.score-excellent { color: #28a745; font-weight: bold; }
.score-good { color: #17a2b8; font-weight: bold; }
.score-neutral { color: #ffc107; font-weight: bold; }
.score-poor { color: #dc3545; font-weight: bold; }
.ticker-header { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

class HybridDashboard:
    def __init__(self):
        # ポートフォリオ構成（9銘柄）
        self.portfolio = {
            "TSLA": {"name": "Tesla", "weight": 20, "sector": "EV・自動運転", "color": "#e31837"},
            "FSLR": {"name": "First Solar", "weight": 20, "sector": "ソーラーパネル", "color": "#ffd700"},
            "RKLB": {"name": "Rocket Lab", "weight": 10, "sector": "小型ロケット", "color": "#ff6b35"},
            "ASTS": {"name": "AST SpaceMobile", "weight": 10, "sector": "衛星通信", "color": "#4a90e2"},
            "OKLO": {"name": "Oklo", "weight": 10, "sector": "SMR原子炉", "color": "#50c878"},
            "JOBY": {"name": "Joby Aviation", "weight": 10, "sector": "eVTOL", "color": "#9b59b6"},
            "OII": {"name": "Oceaneering", "weight": 10, "sector": "海洋エンジニアリング", "color": "#1abc9c"},
            "LUNR": {"name": "Intuitive Machines", "weight": 5, "sector": "月面探査", "color": "#34495e"},
            "RDW": {"name": "Redwire", "weight": 5, "sector": "宇宙製造", "color": "#e74c3c"}
        }
        
        # リスクメトリクス（1-10スケール）
        self.risk_metrics = {
            'TSLA': 6, 'FSLR': 5, 'RKLB': 8, 'ASTS': 9, 'OKLO': 8,
            'JOBY': 7, 'OII': 4, 'LUNR': 9, 'RDW': 8
        }
    
    @staticmethod
    @st.cache_data(ttl=300)
    def fetch_stock_data(ticker):
        """個別銘柄のデータ取得（キャッシュ対応）"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="3mo")
            info = stock.info
            
            if not df.empty:
                # 技術指標計算
                df['EMA20'] = df['Close'].ewm(span=20).mean()
                df['EMA50'] = df['Close'].ewm(span=50).mean()
                df['SMA200'] = df['Close'].rolling(window=200).mean()
                df['RSI'] = HybridDashboard.calculate_rsi(df['Close'])
                
                return {
                    'success': True,
                    'ticker': ticker,
                    'df': df,
                    'info': info,
                    'current_price': df['Close'].iloc[-1],
                    'change_pct': ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100)
                }
        except Exception as e:
            return {'success': False, 'ticker': ticker, 'error': str(e)}
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_expert_scores(self, data: Dict) -> Dict:
        """4専門家スコア評価（TECH/FUND/MACRO/RISK）"""
        if not data['success']:
            return {'TECH': 3.0, 'FUND': 3.0, 'MACRO': 3.0, 'RISK': 3.0, 'OVERALL': 3.0}
        
        df = data['df']
        info = data['info']
        latest = df.iloc[-1]
        ticker = data['ticker']
        
        # TECH スコア (1-5点)
        tech_score = 3.0
        if 'EMA20' in latest and 'EMA50' in latest:
            if latest['Close'] > latest['EMA20'] > latest['EMA50']:
                tech_score += 1.0
        if 'RSI' in latest:
            if 30 < latest['RSI'] < 70:
                tech_score += 0.5
        if 'SMA200' in latest and not pd.isna(latest['SMA200']):
            if latest['Close'] > latest['SMA200']:
                tech_score += 0.5
        
        # FUND スコア (1-5点)
        fund_score = 3.0
        pe_ratio = info.get('trailingPE', 0)
        if 0 < pe_ratio < 25:
            fund_score += 0.5
        if info.get('revenueGrowth', 0) > 0.1:
            fund_score += 0.5
        if info.get('grossMargins', 0) > 0.2:
            fund_score += 0.5
        
        # MACRO スコア (1-5点)
        macro_score = 3.0
        sector = self.portfolio.get(ticker, {}).get('sector', '')
        if sector in ['EV・自動運転', 'ソーラーパネル']:
            macro_score += 0.5
        elif sector in ['小型ロケット', '月面探査', '宇宙製造']:
            macro_score += 1.0
        
        # RISK スコア (1-5点)
        risk_score = 3.0
        volatility = df['Close'].pct_change().std() * (252**0.5)
        if volatility < 0.3:
            risk_score += 1.0
        elif volatility < 0.5:
            risk_score += 0.5
        elif volatility > 0.8:
            risk_score -= 1.0
        
        # スコアを1-5の範囲に収める
        tech_score = min(5.0, max(1.0, tech_score))
        fund_score = min(5.0, max(1.0, fund_score))
        macro_score = min(5.0, max(1.0, macro_score))
        risk_score = min(5.0, max(1.0, risk_score))
        
        overall_score = (tech_score + fund_score + macro_score + risk_score) / 4.0
        
        return {
            'TECH': round(tech_score, 1),
            'FUND': round(fund_score, 1),
            'MACRO': round(macro_score, 1),
            'RISK': round(risk_score, 1),
            'OVERALL': round(overall_score, 1)
        }
    
    def create_score_gauge(self, score: float, title: str) -> go.Figure:
        """スコアゲージチャート作成"""
        color = "#28a745" if score >= 4 else "#17a2b8" if score >= 3 else "#ffc107" if score >= 2 else "#dc3545"
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={
                'axis': {'range': [1, 5]},
                'bar': {'color': color},
                'steps': [
                    {'range': [1, 2], 'color': "lightgray"},
                    {'range': [2, 3], 'color': "lightgray"},
                    {'range': [3, 4], 'color': "lightgray"},
                    {'range': [4, 5], 'color': "lightgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 3
                }
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        return fig
    
    def create_allocation_chart(self) -> go.Figure:
        """ポートフォリオ配分円グラフ"""
        labels = [f"{ticker} ({info['name']})" for ticker, info in self.portfolio.items()]
        values = [info['weight'] for info in self.portfolio.values()]
        colors = [info['color'] for info in self.portfolio.values()]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            textposition='inside',
            textinfo='percent+label'
        )])
        
        fig.update_layout(
            title="ポートフォリオ配分",
            height=400,
            showlegend=False
        )
        return fig
    
    def display_stock_detail(self, ticker: str, data: Dict, scores: Dict):
        """個別銘柄詳細表示"""
        info = self.portfolio[ticker]
        
        st.markdown(f"<div class='ticker-header'>{ticker} - {info['name']}</div>", unsafe_allow_html=True)
        st.markdown(f"**セクター:** {info['sector']} | **配分:** {info['weight']}% | **リスク:** {self.risk_metrics[ticker]}/10")
        
        if data['success']:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # 価格チャート
                fig = go.Figure()
                df = data['df']
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='価格'
                ))
                if 'EMA20' in df.columns:
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA20', line=dict(color='orange')))
                if 'EMA50' in df.columns:
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name='EMA50', line=dict(color='blue')))
                
                fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("現在価格", f"${data['current_price']:.2f}", f"{data['change_pct']:.2f}%")
                st.metric("総合スコア", scores['OVERALL'], f"{'良好' if scores['OVERALL'] >= 3.5 else '要注意'}")
            
            with col3:
                # 専門家スコア
                st.markdown("**専門家評価**")
                for expert, score in scores.items():
                    if expert != 'OVERALL':
                        color_class = "score-excellent" if score >= 4 else "score-good" if score >= 3 else "score-neutral" if score >= 2 else "score-poor"
                        st.markdown(f"<span class='{color_class}'>{expert}: {score}</span>", unsafe_allow_html=True)
        else:
            st.error(f"データ取得エラー: {data.get('error', 'Unknown error')}")
    
    def run(self):
        """メイン実行"""
        st.title("📊 Tiker Portfolio Hybrid Dashboard")
        st.markdown("### portfolio_hybrid_reportの機能をインタラクティブに可視化")
        
        # サイドバー
        with st.sidebar:
            st.header("🎯 ナビゲーション")
            page = st.radio(
                "表示内容を選択",
                ["ポートフォリオ概要", "個別銘柄分析", "最適化提案", "レポート閲覧"]
            )
            
            st.markdown("---")
            if st.button("🔄 データ更新"):
                st.cache_data.clear()
                st.rerun()
        
        # ページ別表示
        if page == "ポートフォリオ概要":
            self.show_portfolio_overview()
        elif page == "個別銘柄分析":
            self.show_stock_analysis()
        elif page == "最適化提案":
            self.show_optimization()
        elif page == "レポート閲覧":
            self.show_reports()
    
    def show_portfolio_overview(self):
        """ポートフォリオ概要ページ"""
        st.header("📈 ポートフォリオ概要")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # 配分円グラフ
            st.plotly_chart(self.create_allocation_chart(), use_container_width=True)
        
        with col2:
            # セクター別集計
            st.subheader("セクター別配分")
            sector_weights = {}
            for ticker, info in self.portfolio.items():
                sector = info['sector']
                sector_weights[sector] = sector_weights.get(sector, 0) + info['weight']
            
            df_sector = pd.DataFrame(
                [(sector, weight) for sector, weight in sector_weights.items()],
                columns=['セクター', '配分(%)']
            ).sort_values('配分(%)', ascending=False)
            
            st.dataframe(df_sector, use_container_width=True, hide_index=True)
        
        # 全銘柄サマリー
        st.subheader("📊 全銘柄サマリー")
        with st.spinner("データ取得中..."):
            summary_data = []
            for ticker in self.portfolio.keys():
                data = HybridDashboard.fetch_stock_data(ticker)
                scores = self.calculate_expert_scores(data)
                
                if data['success']:
                    summary_data.append({
                        'ティッカー': ticker,
                        '銘柄名': self.portfolio[ticker]['name'],
                        'セクター': self.portfolio[ticker]['sector'],
                        '配分': f"{self.portfolio[ticker]['weight']}%",
                        '現在価格': f"${data['current_price']:.2f}",
                        '前日比': f"{data['change_pct']:+.2f}%",
                        'TECH': scores['TECH'],
                        'FUND': scores['FUND'],
                        'MACRO': scores['MACRO'],
                        'RISK': scores['RISK'],
                        '総合': scores['OVERALL']
                    })
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(
                df_summary.style.background_gradient(subset=['TECH', 'FUND', 'MACRO', 'RISK', '総合']),
                use_container_width=True,
                hide_index=True
            )
    
    def show_stock_analysis(self):
        """個別銘柄分析ページ"""
        st.header("🔍 個別銘柄分析")
        
        # 銘柄選択
        selected_ticker = st.selectbox(
            "銘柄を選択",
            options=list(self.portfolio.keys()),
            format_func=lambda x: f"{x} - {self.portfolio[x]['name']}"
        )
        
        # データ取得と表示
        with st.spinner(f"{selected_ticker}のデータを取得中..."):
            data = HybridDashboard.fetch_stock_data(selected_ticker)
            scores = self.calculate_expert_scores(data)
            
            # 詳細表示
            self.display_stock_detail(selected_ticker, data, scores)
            
            # 4専門家スコアゲージ
            st.subheader("専門家評価詳細")
            cols = st.columns(4)
            experts = ['TECH', 'FUND', 'MACRO', 'RISK']
            for i, expert in enumerate(experts):
                with cols[i]:
                    fig = self.create_score_gauge(scores[expert], expert)
                    st.plotly_chart(fig, use_container_width=True)
    
    def show_optimization(self):
        """最適化提案ページ"""
        st.header("🎯 ポートフォリオ最適化提案")
        
        # 現在配分と推奨配分の比較
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("現在の配分")
            current_df = pd.DataFrame([
                (ticker, info['name'], info['weight'], self.risk_metrics[ticker])
                for ticker, info in self.portfolio.items()
            ], columns=['ティッカー', '銘柄名', '配分(%)', 'リスク(1-10)'])
            st.dataframe(current_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("推奨配分（リスク調整後）")
            recommended = {}
            for ticker, weight in [(t, self.portfolio[t]['weight']) for t in self.portfolio]:
                risk = self.risk_metrics[ticker]
                if risk >= 8:
                    recommended[ticker] = max(weight - 2, 3)
                elif risk <= 4:
                    recommended[ticker] = min(weight + 2, 25)
                else:
                    recommended[ticker] = weight
            
            # 合計を100%に調整
            total = sum(recommended.values())
            if total != 100:
                adjustment = (100 - total) / len(recommended)
                for ticker in recommended:
                    recommended[ticker] += adjustment
            
            recommended_df = pd.DataFrame([
                (ticker, self.portfolio[ticker]['name'], round(weight, 1), self.risk_metrics[ticker])
                for ticker, weight in recommended.items()
            ], columns=['ティッカー', '銘柄名', '推奨配分(%)', 'リスク(1-10)'])
            st.dataframe(recommended_df, use_container_width=True, hide_index=True)
        
        # 変更提案
        st.subheader("📋 配分変更提案")
        changes = []
        for ticker in self.portfolio:
            current = self.portfolio[ticker]['weight']
            rec = recommended[ticker]
            if abs(current - rec) > 0.5:
                changes.append({
                    'ティッカー': ticker,
                    '銘柄名': self.portfolio[ticker]['name'],
                    '現在': f"{current}%",
                    '推奨': f"{rec:.1f}%",
                    '変更': f"{rec - current:+.1f}%",
                    '理由': 'リスク高' if self.risk_metrics[ticker] >= 8 else 'リスク低'
                })
        
        if changes:
            st.dataframe(pd.DataFrame(changes), use_container_width=True, hide_index=True)
        else:
            st.info("現在の配分は適切です。大きな変更は必要ありません。")
    
    def show_reports(self):
        """レポート閲覧ページ"""
        st.header("📄 レポート閲覧")
        
        # 利用可能なレポートを検索
        report_types = {
            "専門家討論": "reports/*_discussion_*.md",
            "HTMLレポート": "reports/html/portfolio_hybrid_report_*.html",
            "詳細分析": "reports/detailed_discussions/*_detailed_analysis_*.md"
        }
        
        selected_type = st.selectbox("レポートタイプを選択", list(report_types.keys()))
        
        # レポートファイルを検索
        pattern = report_types[selected_type]
        files = glob.glob(pattern)
        
        if files:
            # 最新のファイルから表示
            files.sort(reverse=True)
            selected_file = st.selectbox("ファイルを選択", files[:10])  # 最新10件
            
            if selected_file:
                try:
                    if selected_file.endswith('.html'):
                        with open(selected_file, 'r', encoding='utf-8') as f:
                            st.components.v1.html(f.read(), height=800, scrolling=True)
                    else:
                        with open(selected_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            st.markdown(content)
                except Exception as e:
                    st.error(f"ファイル読み込みエラー: {str(e)}")
        else:
            st.info(f"{selected_type}のレポートが見つかりません。")

if __name__ == "__main__":
    dashboard = HybridDashboard()
    dashboard.run()