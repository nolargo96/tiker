#!/usr/bin/env python3
"""
Tiker Interactive Dashboard with Entry Timing Analysis
株式投資分析システム - インタラクティブWebダッシュボード

Features:
- リアルタイム株価データ表示
- エントリータイミング判定（BUY/HOLD/SELL シグナル）
- 4専門家スコア統合表示
- インタラクティブチャート（Plotly）
- ポートフォリオ全体の投資判断
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# 既存ライブラリの活用
from unified_stock_analyzer import StockAnalyzer
from stock_analyzer_lib import ConfigManager, TechnicalIndicators, StockDataManager

# ページ設定
st.set_page_config(
    page_title="Tiker Live Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(45deg, #f0f2f6, #ffffff);
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #1f77b4;
    margin: 0.5rem 0;
}

.buy-signal {
    background: linear-gradient(45deg, #d4edda, #c3e6cb);
    border-left-color: #28a745 !important;
    color: #155724;
}

.hold-signal {
    background: linear-gradient(45deg, #fff3cd, #ffeaa7);
    border-left-color: #ffc107 !important;
    color: #856404;
}

.sell-signal {
    background: linear-gradient(45deg, #f8d7da, #f5c6cb);
    border-left-color: #dc3545 !important;
    color: #721c24;
}

.expert-score {
    text-align: center;
    padding: 0.5rem;
    margin: 0.2rem;
    border-radius: 8px;
    font-weight: bold;
}

.score-excellent { background: #d4edda; color: #155724; }
.score-good { background: #d1ecf1; color: #0c5460; }
.score-average { background: #fff3cd; color: #856404; }
.score-poor { background: #f8d7da; color: #721c24; }

.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #f0f2f6;
    border-radius: 8px 8px 0 0;
    padding: 0.5rem 1rem;
}

.portfolio-summary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

class EntryTimingAnalyzer:
    """エントリータイミング判定システム"""
    
    def __init__(self):
        self.signals = {
            'BUY': {'color': '#28a745', 'icon': '🟢', 'message': '絶好の買い場'},
            'HOLD': {'color': '#ffc107', 'icon': '🟡', 'message': '様子見・継続保有'},
            'SELL': {'color': '#dc3545', 'icon': '🔴', 'message': '売却検討'}
        }
    
    def analyze_entry_timing(self, df: pd.DataFrame, ticker: str) -> Dict:
        """総合的なエントリータイミング分析"""
        if df.empty or len(df) < 50:
            return self._create_signal_result('HOLD', 0.5, 'データ不足', {})
        
        latest = df.iloc[-1]
        current_price = latest['Close']
        
        # 1. テクニカル分析スコア
        tech_score = self._calculate_technical_score(df, latest)
        
        # 2. トレンド分析スコア  
        trend_score = self._calculate_trend_score(df, latest)
        
        # 3. ボラティリティ分析
        volatility_score = self._calculate_volatility_score(df)
        
        # 4. 出来高分析
        volume_score = self._calculate_volume_score(df)
        
        # 5. サポート・レジスタンス分析
        support_resistance_score = self._calculate_support_resistance_score(df, current_price)
        
        # 総合スコア計算（重み付き）
        weights = {
            'technical': 0.25,
            'trend': 0.30,
            'volatility': 0.15,
            'volume': 0.15,
            'support_resistance': 0.15
        }
        
        total_score = (
            tech_score * weights['technical'] +
            trend_score * weights['trend'] +
            volatility_score * weights['volatility'] +
            volume_score * weights['volume'] +
            support_resistance_score * weights['support_resistance']
        )
        
        # シグナル判定
        if total_score >= 0.7:
            signal = 'BUY'
            confidence = total_score
            message = f"強い買いシグナル（スコア: {total_score:.2f}）"
        elif total_score >= 0.4:
            signal = 'HOLD'
            confidence = total_score
            message = f"中立・様子見（スコア: {total_score:.2f}）"
        else:
            signal = 'SELL'
            confidence = 1 - total_score
            message = f"売却検討推奨（スコア: {total_score:.2f}）"
        
        details = {
            'technical_score': tech_score,
            'trend_score': trend_score,
            'volatility_score': volatility_score,
            'volume_score': volume_score,
            'support_resistance_score': support_resistance_score,
            'current_price': current_price,
            'price_change_pct': ((current_price - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100) if len(df) > 1 else 0
        }
        
        return self._create_signal_result(signal, confidence, message, details)
    
    def _calculate_technical_score(self, df: pd.DataFrame, latest: pd.Series) -> float:
        """テクニカル指標総合スコア"""
        score = 0.0
        count = 0
        
        # RSI (30-70が理想、50上下でポイント)
        if 'RSI' in df.columns and not pd.isna(latest['RSI']):
            rsi = latest['RSI']
            if 30 <= rsi <= 70:
                if rsi > 50:
                    score += 0.6 + (rsi - 50) / 50 * 0.4  # 50-70: 0.6-1.0
                else:
                    score += 0.2 + (rsi - 30) / 20 * 0.4  # 30-50: 0.2-0.6
            elif rsi < 30:
                score += 0.8  # 過売り状態は買い好機
            else:  # rsi > 70
                score += 0.1  # 過買い状態
            count += 1
        
        # EMA20 vs 価格
        if 'EMA20' in df.columns and not pd.isna(latest['EMA20']):
            if latest['Close'] > latest['EMA20']:
                score += 0.7
            else:
                score += 0.3
            count += 1
        
        # ボリンジャーバンド位置
        if all(col in df.columns for col in ['BB_upper', 'BB_lower']) and \
           not pd.isna(latest['BB_upper']) and not pd.isna(latest['BB_lower']):
            bb_position = (latest['Close'] - latest['BB_lower']) / (latest['BB_upper'] - latest['BB_lower'])
            if bb_position < 0.2:  # 下限近く
                score += 0.8
            elif bb_position > 0.8:  # 上限近く
                score += 0.2
            else:
                score += 0.5
            count += 1
        
        return score / count if count > 0 else 0.5
    
    def _calculate_trend_score(self, df: pd.DataFrame, latest: pd.Series) -> float:
        """トレンド分析スコア"""
        if len(df) < 20:
            return 0.5
        
        score = 0.0
        count = 0
        
        # 短期トレンド（5日間）
        if len(df) >= 5:
            recent_trend = (latest['Close'] - df.iloc[-5]['Close']) / df.iloc[-5]['Close']
            if recent_trend > 0.02:  # +2%以上
                score += 0.8
            elif recent_trend > 0:
                score += 0.6
            elif recent_trend > -0.02:  # -2%以内
                score += 0.4
            else:
                score += 0.2
            count += 1
        
        # EMA20 vs SMA200 (ゴールデン/デッドクロス)
        if all(col in df.columns for col in ['EMA20', 'SMA200']) and \
           not pd.isna(latest['EMA20']) and not pd.isna(latest['SMA200']):
            if latest['EMA20'] > latest['SMA200']:
                score += 0.7  # ゴールデンクロス状態
            else:
                score += 0.3  # デッドクロス状態
            count += 1
        
        # 価格が移動平均線群を上抜けているか
        if all(col in df.columns for col in ['EMA20', 'SMA200']):
            if latest['Close'] > latest['EMA20'] > latest['SMA200']:
                score += 0.8  # 強い上昇トレンド
            elif latest['Close'] > latest['EMA20']:
                score += 0.6  # 中程度の上昇
            elif latest['Close'] > latest['SMA200']:
                score += 0.5  # 長期的には上昇
            else:
                score += 0.2  # 下降トレンド
            count += 1
        
        return score / count if count > 0 else 0.5
    
    def _calculate_volatility_score(self, df: pd.DataFrame) -> float:
        """ボラティリティ分析（安定性スコア）"""
        if len(df) < 20:
            return 0.5
        
        # ATR based volatility
        if 'ATR' in df.columns:
            recent_atr = df['ATR'].tail(5).mean()
            avg_atr = df['ATR'].tail(20).mean()
            
            if recent_atr < avg_atr * 0.8:  # 低ボラティリティ
                return 0.7  # 安定期は買い時
            elif recent_atr < avg_atr * 1.2:  # 通常
                return 0.5
            else:  # 高ボラティリティ
                return 0.3  # 不安定期
        
        # ATRがない場合、価格変動率で代用
        returns = df['Close'].pct_change().dropna()
        if len(returns) < 10:
            return 0.5
        
        recent_vol = returns.tail(5).std()
        avg_vol = returns.tail(20).std()
        
        if recent_vol < avg_vol * 0.8:
            return 0.7
        elif recent_vol < avg_vol * 1.2:
            return 0.5
        else:
            return 0.3
    
    def _calculate_volume_score(self, df: pd.DataFrame) -> float:
        """出来高分析スコア"""
        if 'Volume' not in df.columns or len(df) < 20:
            return 0.5
        
        recent_volume = df['Volume'].tail(5).mean()
        avg_volume = df['Volume'].tail(20).mean()
        
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 1.5:  # 出来高急増
            return 0.8  # 注目度上昇
        elif volume_ratio > 1.2:  # やや増加
            return 0.6
        elif volume_ratio > 0.8:  # 通常
            return 0.5
        else:  # 出来高減少
            return 0.3
    
    def _calculate_support_resistance_score(self, df: pd.DataFrame, current_price: float) -> float:
        """サポート・レジスタンス分析"""
        if len(df) < 50:
            return 0.5
        
        # 過去50日の高値・安値から主要レベルを特定
        recent_data = df.tail(50)
        highs = recent_data['High'].values
        lows = recent_data['Low'].values
        
        # サポートレベル（安値集中点）
        support_levels = []
        for i in range(len(lows) - 4):
            local_min = min(lows[i:i+5])
            if abs(lows[i+2] - local_min) < local_min * 0.02:  # 2%以内
                support_levels.append(local_min)
        
        # レジスタンスレベル（高値集中点）
        resistance_levels = []
        for i in range(len(highs) - 4):
            local_max = max(highs[i:i+5])
            if abs(highs[i+2] - local_max) < local_max * 0.02:  # 2%以内
                resistance_levels.append(local_max)
        
        if not support_levels and not resistance_levels:
            return 0.5
        
        # 現在価格とサポート・レジスタンスの関係
        score = 0.5
        
        if support_levels:
            nearest_support = max([s for s in support_levels if s <= current_price], default=min(support_levels))
            support_distance = (current_price - nearest_support) / nearest_support
            
            if support_distance < 0.05:  # サポート付近
                score += 0.3  # 買い好機
        
        if resistance_levels:
            nearest_resistance = min([r for r in resistance_levels if r >= current_price], default=max(resistance_levels))
            resistance_distance = (nearest_resistance - current_price) / current_price
            
            if resistance_distance < 0.05:  # レジスタンス付近
                score -= 0.2  # 売り圧力
            elif resistance_distance > 0.1:  # レジスタンスまで余裕
                score += 0.2  # 上昇余地
        
        return max(0, min(1, score))
    
    def _create_signal_result(self, signal: str, confidence: float, message: str, details: Dict) -> Dict:
        """シグナル結果の統一フォーマット"""
        return {
            'signal': signal,
            'confidence': confidence,
            'message': message,
            'color': self.signals[signal]['color'],
            'icon': self.signals[signal]['icon'],
            'details': details,
            'timestamp': datetime.now()
        }

class DashboardApp:
    """メインダッシュボードアプリケーション"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.data_manager = StockDataManager(self.config)
        self.timing_analyzer = EntryTimingAnalyzer()
        
        # ポートフォリオ構成
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
        """メインアプリケーション実行"""
        self._render_header()
        self._render_sidebar()
        self._render_main_content()
    
    def _render_header(self):
        """ヘッダー部分"""
        st.markdown("""
        <div class="portfolio-summary">
            <h1>🚀 Tiker Live Dashboard</h1>
            <p>リアルタイム株式分析 & エントリータイミング判定システム</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """サイドバー設定パネル"""
        with st.sidebar:
            st.header("📊 分析設定")
            
            # 期間設定
            period_days = st.selectbox(
                "分析期間",
                [30, 90, 180, 365],
                index=1,
                help="チャートと分析に使用する日数"
            )
            
            # データ更新
            if st.button("🔄 データ更新", type="primary"):
                st.cache_data.clear()
                st.success("キャッシュクリア完了")
                st.rerun()
            
            # 表示オプション
            st.subheader("📈 表示設定")
            show_volume = st.checkbox("出来高表示", value=True)
            show_indicators = st.checkbox("テクニカル指標", value=True)
            show_signals = st.checkbox("売買シグナル", value=True)
            
            st.session_state.update({
                'period_days': period_days,
                'show_volume': show_volume,
                'show_indicators': show_indicators,
                'show_signals': show_signals
            })
    
    def _render_main_content(self):
        """メインコンテンツエリア"""
        # タブ設定
        tabs = ["🏠 ポートフォリオ概要"] + [f"📈 {ticker}" for ticker in self.portfolio.keys()]
        selected_tab = st.tabs(tabs)
        
        # ポートフォリオ概要タブ
        with selected_tab[0]:
            self._render_portfolio_overview()
        
        # 個別銘柄タブ
        for i, ticker in enumerate(self.portfolio.keys(), 1):
            with selected_tab[i]:
                self._render_stock_analysis(ticker)
    
    @st.cache_data(ttl=300)  # 5分キャッシュ
    def _get_stock_data(_self, ticker: str, period_days: int) -> pd.DataFrame:
        """株価データ取得（キャッシュ機能付き）"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days + 50)  # 指標計算用に余裕を持たせる
        
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                return pd.DataFrame()
            
            # テクニカル指標の計算
            tech_indicators = TechnicalIndicators()
            
            # 移動平均線
            df['EMA20'] = df['Close'].ewm(span=20).mean()
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
            
            return df.tail(period_days)
            
        except Exception as e:
            st.error(f"データ取得エラー ({ticker}): {str(e)}")
            return pd.DataFrame()
    
    def _render_portfolio_overview(self):
        """ポートフォリオ全体概要"""
        st.header("🏠 ポートフォリオ全体分析")
        
        # エントリーシグナル一覧
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("📡 全銘柄エントリーシグナル")
            
            signals_data = []
            for ticker in self.portfolio.keys():
                df = self._get_stock_data(ticker, st.session_state.get('period_days', 90))
                if not df.empty:
                    signal_result = self.timing_analyzer.analyze_entry_timing(df, ticker)
                    signals_data.append({
                        'Ticker': ticker,
                        'Name': self.portfolio[ticker]['name'],
                        'Signal': f"{signal_result['icon']} {signal_result['signal']}",
                        'Confidence': f"{signal_result['confidence']:.2f}",
                        'Price': f"${df.iloc[-1]['Close']:.2f}",
                        'Change%': f"{signal_result['details'].get('price_change_pct', 0):.1f}%",
                        'Message': signal_result['message']
                    })
            
            if signals_data:
                signals_df = pd.DataFrame(signals_data)
                st.dataframe(
                    signals_df,
                    use_container_width=True,
                    hide_index=True
                )
        
        with col2:
            st.subheader("📊 シグナル分布")
            if signals_data:
                signal_counts = {}
                for data in signals_data:
                    signal = data['Signal'].split()[1]  # アイコンを除去
                    signal_counts[signal] = signal_counts.get(signal, 0) + 1
                
                fig = px.pie(
                    values=list(signal_counts.values()),
                    names=list(signal_counts.keys()),
                    color=list(signal_counts.keys()),
                    color_discrete_map={
                        'BUY': '#28a745',
                        'HOLD': '#ffc107', 
                        'SELL': '#dc3545'
                    }
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # ポートフォリオ配分
        st.subheader("🥧 現在のポートフォリオ配分")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.pie(
                values=[info['weight'] for info in self.portfolio.values()],
                names=list(self.portfolio.keys()),
                title="銘柄別配分 (%)"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**配分詳細**")
            for ticker, info in self.portfolio.items():
                st.markdown(f"**{ticker}**: {info['weight']}% - {info['name']}")
    
    def _render_stock_analysis(self, ticker: str):
        """個別銘柄分析"""
        stock_info = self.portfolio[ticker]
        st.header(f"📈 {ticker} - {stock_info['name']}")
        
        # データ取得
        df = self._get_stock_data(ticker, st.session_state.get('period_days', 90))
        
        if df.empty:
            st.error(f"{ticker} のデータを取得できませんでした")
            return
        
        # エントリータイミング分析
        signal_result = self.timing_analyzer.analyze_entry_timing(df, ticker)
        
        # 上部：シグナル表示
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card {signal_result['signal'].lower()}-signal">
                <h3>{signal_result['icon']} {signal_result['signal']}</h3>
                <p><strong>信頼度: {signal_result['confidence']:.1%}</strong></p>
                <p>{signal_result['message']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            current_price = df.iloc[-1]['Close']
            price_change = signal_result['details']['price_change_pct']
            change_color = "green" if price_change >= 0 else "red"
            
            st.metric(
                "現在価格",
                f"${current_price:.2f}",
                f"{price_change:+.1f}%",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "テクニカルスコア",
                f"{signal_result['details']['technical_score']:.2f}",
                f"トレンド: {signal_result['details']['trend_score']:.2f}"
            )
        
        with col4:
            st.metric(
                "出来高スコア", 
                f"{signal_result['details']['volume_score']:.2f}",
                f"変動性: {signal_result['details']['volatility_score']:.2f}"
            )
        
        # メイン：インタラクティブチャート
        st.subheader("📊 インタラクティブチャート")
        chart = self._create_interactive_chart(df, ticker, signal_result)
        st.plotly_chart(chart, use_container_width=True)
        
        # 詳細スコア分析
        with st.expander("🔍 詳細分析データ"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**スコア内訳**")
                scores = signal_result['details']
                score_items = [
                    ('テクニカル', scores['technical_score']),
                    ('トレンド', scores['trend_score']),
                    ('出来高', scores['volume_score']),
                    ('変動性', scores['volatility_score']),
                    ('サポート/レジスタンス', scores['support_resistance_score'])
                ]
                
                for name, score in score_items:
                    if score >= 0.7:
                        css_class = "score-excellent"
                    elif score >= 0.5:
                        css_class = "score-good"
                    elif score >= 0.3:
                        css_class = "score-average"
                    else:
                        css_class = "score-poor"
                    
                    st.markdown(f"""
                    <div class="expert-score {css_class}">
                        {name}: {score:.2f}
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**最新の指標値**")
                latest = df.iloc[-1]
                if 'RSI' in df.columns and not pd.isna(latest['RSI']):
                    st.write(f"RSI: {latest['RSI']:.1f}")
                if 'EMA20' in df.columns:
                    st.write(f"EMA20: ${latest['EMA20']:.2f}")
                if 'SMA200' in df.columns:
                    st.write(f"SMA200: ${latest['SMA200']:.2f}")
                if 'ATR' in df.columns:
                    st.write(f"ATR: ${latest['ATR']:.2f}")
    
    def _create_interactive_chart(self, df: pd.DataFrame, ticker: str, signal_result: Dict) -> go.Figure:
        """インタラクティブチャート作成"""
        # サブプロット作成
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxis=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{ticker} Stock Price', 'Volume', 'RSI'),
            row_heights=[0.6, 0.2, 0.2]
        )
        
        # ローソク足チャート
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
            
            if 'SMA200' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA200'],
                        name='SMA200',
                        line=dict(color='purple', width=2)
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
                        line=dict(color='gray', width=1, dash='dash'),
                        showlegend=False
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['BB_lower'],
                        name='Bollinger Bands',
                        fill='tonexty',
                        fillcolor='rgba(128,128,128,0.1)',
                        line=dict(color='gray', width=1, dash='dash')
                    ),
                    row=1, col=1
                )
        
        # 売買シグナル
        if st.session_state.get('show_signals', True):
            latest_date = df.index[-1]
            latest_price = df.iloc[-1]['Close']
            
            signal_color = signal_result['color']
            signal_symbol = 'triangle-up' if signal_result['signal'] == 'BUY' else \
                           'circle' if signal_result['signal'] == 'HOLD' else 'triangle-down'
            
            fig.add_trace(
                go.Scatter(
                    x=[latest_date],
                    y=[latest_price],
                    mode='markers',
                    marker=dict(
                        symbol=signal_symbol,
                        size=15,
                        color=signal_color,
                        line=dict(width=2, color='white')
                    ),
                    name=f'{signal_result["signal"]} Signal',
                    showlegend=True
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
                    opacity=0.7
                ),
                row=2, col=1
            )
        
        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    name='RSI',
                    line=dict(color='blue', width=2)
                ),
                row=3, col=1
            )
            
            # RSI の過買い・過売りライン
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="過買い", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         annotation_text="過売り", row=3, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)
        
        # レイアウト調整
        fig.update_layout(
            title=f'{ticker} - {signal_result["icon"]} {signal_result["signal"]} Signal',
            height=800,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        # Y軸の設定
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
        
        return fig

# アプリケーション実行
if __name__ == "__main__":
    app = DashboardApp()
    app.run()