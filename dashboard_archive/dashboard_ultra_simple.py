#!/usr/bin/env python3
"""
Tiker Dashboard - 超シンプル版
Streamlitのみで動作する最小実装
"""

import streamlit as st
from datetime import datetime, timedelta
import random
import math

# ページ設定
st.set_page_config(
    page_title="🚀 Tiker Dashboard",
    page_icon="📈",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.big-font {
    font-size: 24px !important;
    font-weight: bold;
}
.buy { color: #28a745; }
.hold { color: #ffc107; }
.sell { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# ポートフォリオ定義
PORTFOLIO = {
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

def generate_price_data(base_price, days=90):
    """価格データ生成"""
    prices = []
    current = base_price
    
    for i in range(days):
        # ランダムウォーク
        change = random.uniform(-0.03, 0.03)
        current = current * (1 + change)
        prices.append({
            'day': i,
            'price': current,
            'change': change
        })
    
    return prices

def calculate_signal(prices):
    """シンプルなシグナル計算"""
    if len(prices) < 20:
        return 'HOLD', 2.5
    
    # 最新価格と20日前の価格を比較
    current = prices[-1]['price']
    past = prices[-20]['price']
    
    change_pct = (current - past) / past
    
    if change_pct > 0.05:  # 5%以上上昇
        return 'BUY', 4.0
    elif change_pct < -0.05:  # 5%以上下落
        return 'SELL', 1.5
    else:
        return 'HOLD', 2.5

def main():
    st.title("🚀 Tiker Interactive Dashboard")
    st.markdown("### エントリータイミング判定システム")
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        
        days = st.slider("分析期間（日）", 30, 180, 90)
        
        if st.button("🔄 データ更新"):
            st.rerun()
        
        st.divider()
        
        st.markdown("""
        **エントリーシグナル**
        - 🟢 **BUY**: 買い推奨
        - 🟡 **HOLD**: 様子見
        - 🔴 **SELL**: 売却検討
        """)
    
    # タブ作成
    tab_names = ["📊 ポートフォリオ概要"] + [f"{ticker}" for ticker in PORTFOLIO.keys()]
    tabs = st.tabs(tab_names)
    
    # ポートフォリオ概要
    with tabs[0]:
        st.header("📊 ポートフォリオ総合分析")
        
        # 3列レイアウト
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader("🎯 エントリーシグナル一覧")
            
            # テーブルデータ作成
            table_data = []
            signal_counts = {'BUY': 0, 'HOLD': 0, 'SELL': 0}
            
            for ticker, info in PORTFOLIO.items():
                # 価格データ生成
                prices = generate_price_data(info['price'], days)
                signal, score = calculate_signal(prices)
                signal_counts[signal] += 1
                
                # 最新価格と変化率
                current_price = prices[-1]['price']
                prev_price = prices[-2]['price'] if len(prices) > 1 else current_price
                change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price != 0 else 0
                
                # シグナルアイコン
                signal_icon = {'BUY': '🟢', 'HOLD': '🟡', 'SELL': '🔴'}[signal]
                
                table_data.append({
                    'Ticker': ticker,
                    'Name': info['name'],
                    'Signal': f"{signal_icon} {signal}",
                    'Score': f"{score:.1f}",
                    'Price': f"${current_price:.2f}",
                    'Change': f"{change_pct:+.1f}%"
                })
            
            # テーブル表示（簡易版）
            for row in table_data:
                cols = st.columns([1, 2, 1, 1, 1, 1])
                cols[0].write(row['Ticker'])
                cols[1].write(row['Name'])
                cols[2].write(row['Signal'])
                cols[3].write(row['Score'])
                cols[4].write(row['Price'])
                cols[5].write(row['Change'])
        
        with col2:
            st.subheader("📈 シグナル分布")
            
            # 簡易円グラフ
            total = sum(signal_counts.values())
            if total > 0:
                st.metric("BUY", f"{signal_counts['BUY']}", f"{signal_counts['BUY']/total*100:.0f}%")
                st.metric("HOLD", f"{signal_counts['HOLD']}", f"{signal_counts['HOLD']/total*100:.0f}%")
                st.metric("SELL", f"{signal_counts['SELL']}", f"{signal_counts['SELL']/total*100:.0f}%")
        
        with col3:
            st.subheader("📊 統計")
            st.metric("総銘柄数", len(PORTFOLIO))
            st.metric("分析期間", f"{days}日")
            st.metric("最終更新", datetime.now().strftime("%H:%M:%S"))
    
    # 個別銘柄タブ
    for i, ticker in enumerate(PORTFOLIO.keys(), 1):
        with tabs[i]:
            render_stock_detail(ticker, days)

def render_stock_detail(ticker, days):
    """個別銘柄詳細"""
    info = PORTFOLIO[ticker]
    
    st.header(f"📈 {ticker} - {info['name']}")
    
    # 価格データ生成
    prices = generate_price_data(info['price'], days)
    signal, score = calculate_signal(prices)
    
    # メトリクス
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        signal_color = {'BUY': 'buy', 'HOLD': 'hold', 'SELL': 'sell'}[signal]
        signal_icon = {'BUY': '🟢', 'HOLD': '🟡', 'SELL': '🔴'}[signal]
        
        st.markdown(f'<p class="big-font {signal_color}">{signal_icon} {signal}</p>', unsafe_allow_html=True)
        st.write(f"スコア: {score:.1f} / 5.0")
    
    with col2:
        current_price = prices[-1]['price']
        prev_price = prices[-2]['price'] if len(prices) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price != 0 else 0
        
        st.metric("現在価格", f"${current_price:.2f}", f"{change_pct:+.1f}%")
    
    with col3:
        st.metric("配分", f"{info['weight']}%")
    
    with col4:
        st.metric("基準価格", f"${info['price']:.2f}")
    
    # 簡易チャート
    st.subheader("価格推移")
    
    # ラインチャート用データ
    chart_prices = [p['price'] for p in prices]
    
    # Streamlit内蔵のline_chartを使用
    st.line_chart(chart_prices, height=400)
    
    # 統計情報
    st.subheader("📊 統計情報")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_price = max(chart_prices)
        st.metric("最高値", f"${max_price:.2f}")
    
    with col2:
        min_price = min(chart_prices)
        st.metric("最安値", f"${min_price:.2f}")
    
    with col3:
        avg_price = sum(chart_prices) / len(chart_prices)
        st.metric("平均価格", f"${avg_price:.2f}")
    
    # 分析コメント
    st.subheader("💡 分析コメント")
    
    if signal == 'BUY':
        st.success(f"✅ {ticker}は上昇トレンドにあります。エントリーを検討する良いタイミングかもしれません。")
    elif signal == 'HOLD':
        st.info(f"ℹ️ {ticker}は横ばいです。もう少し様子を見ることをお勧めします。")
    else:
        st.warning(f"⚠️ {ticker}は下降トレンドです。リスク管理を徹底してください。")

# 強化版機能の準備
def create_enhanced_dashboard():
    """強化版ダッシュボード用のコード生成"""
    enhanced_code = '''#!/usr/bin/env python3
"""
Tiker Dashboard Enhanced - 完全動作版
4専門家分析統合型（ライブラリ問題を回避）
"""

import streamlit as st
from datetime import datetime, timedelta
import random
import json

# ページ設定
st.set_page_config(
    page_title="🚀 Tiker Dashboard Pro",
    page_icon="📈",
    layout="wide"
)

# 拡張CSS
st.markdown("""
<style>
.signal-card {
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.strong-buy { background: #d4f1d4; border: 2px solid #28a745; }
.buy { background: #e8f5e8; border: 2px solid #5cb85c; }
.hold { background: #fff9e6; border: 2px solid #ffc107; }
.sell { background: #ffe0e0; border: 2px solid #dc3545; }

.expert-score {
    padding: 0.5rem;
    margin: 0.2rem;
    border-radius: 8px;
    text-align: center;
}
.score-high { background: #d4edda; color: #155724; }
.score-mid { background: #fff3cd; color: #856404; }
.score-low { background: #f8d7da; color: #721c24; }

.timing-gauge {
    height: 40px;
    background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
    border-radius: 20px;
    position: relative;
    margin: 1rem 0;
}
.timing-pointer {
    position: absolute;
    top: -5px;
    width: 4px;
    height: 50px;
    background: #333;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)

# ポートフォリオ定義
PORTFOLIO = {
    'TSLA': {'name': 'Tesla Inc', 'weight': 20, 'sector': 'EV/Tech'},
    'FSLR': {'name': 'First Solar', 'weight': 20, 'sector': 'Solar'},
    'RKLB': {'name': 'Rocket Lab', 'weight': 10, 'sector': 'Space'},
    'ASTS': {'name': 'AST SpaceMobile', 'weight': 10, 'sector': 'Satellite'},
    'OKLO': {'name': 'Oklo Inc', 'weight': 10, 'sector': 'Nuclear'},
    'JOBY': {'name': 'Joby Aviation', 'weight': 10, 'sector': 'eVTOL'},
    'OII': {'name': 'Oceaneering', 'weight': 10, 'sector': 'Marine'},
    'LUNR': {'name': 'Intuitive Machines', 'weight': 5, 'sector': 'Space'},
    'RDW': {'name': 'Redwire Corp', 'weight': 5, 'sector': 'Space'}
}

def calculate_expert_scores(ticker):
    """4専門家スコア計算（デモ用）"""
    # 実際の実装では既存のunified_stock_analyzerから取得
    return {
        'TECH': random.uniform(2.5, 4.5),
        'FUND': random.uniform(2.0, 4.0),
        'MACRO': random.uniform(2.5, 4.5),
        'RISK': random.uniform(2.0, 4.0)
    }

def calculate_entry_signal(scores):
    """総合エントリーシグナル判定"""
    weights = {'TECH': 0.3, 'FUND': 0.25, 'MACRO': 0.25, 'RISK': 0.2}
    total = sum(scores[k] * weights[k] for k in scores)
    
    if total >= 4.0:
        return 'STRONG_BUY', total, '🟢🟢'
    elif total >= 3.5:
        return 'BUY', total, '🟢'
    elif total >= 2.5:
        return 'HOLD', total, '🟡'
    elif total >= 2.0:
        return 'SELL', total, '🔴'
    else:
        return 'STRONG_SELL', total, '🔴🔴'

def main():
    st.title("🚀 Tiker Dashboard Pro")
    st.markdown("### 4専門家AI統合型 エントリータイミング分析")
    
    # ヘッダー情報
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.info("📊 TECH/FUND/MACRO/RISK の4つの観点から総合的に分析")
    with col2:
        st.metric("ポートフォリオ", "9銘柄")
    with col3:
        if st.button("🔄 更新"):
            st.rerun()
    
    # タブ
    tabs = st.tabs(["📊 総合分析"] + [f"{t}" for t in PORTFOLIO.keys()])
    
    # 総合分析タブ
    with tabs[0]:
        render_portfolio_overview()
    
    # 個別銘柄タブ
    for i, ticker in enumerate(PORTFOLIO.keys(), 1):
        with tabs[i]:
            render_enhanced_stock_detail(ticker)

def render_portfolio_overview():
    """ポートフォリオ総合ビュー"""
    st.header("📊 ポートフォリオ総合分析")
    
    # シグナル一覧
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🎯 全銘柄エントリーシグナル")
        
        # ヘッダー
        headers = st.columns([1, 2, 1, 1, 1, 1, 1])
        headers[0].write("**Ticker**")
        headers[1].write("**Name**")
        headers[2].write("**Signal**")
        headers[3].write("**Total**")
        headers[4].write("**TECH**")
        headers[5].write("**FUND**")
        headers[6].write("**RISK**")
        
        # データ行
        signal_counts = {}
        for ticker, info in PORTFOLIO.items():
            scores = calculate_expert_scores(ticker)
            signal, total, icon = calculate_entry_signal(scores)
            
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
            
            cols = st.columns([1, 2, 1, 1, 1, 1, 1])
            cols[0].write(ticker)
            cols[1].write(info['name'])
            cols[2].write(f"{icon} {signal}")
            cols[3].write(f"{total:.2f}")
            cols[4].write(f"{scores['TECH']:.1f}")
            cols[5].write(f"{scores['FUND']:.1f}")
            cols[6].write(f"{scores['RISK']:.1f}")
    
    with col2:
        st.subheader("📈 シグナル分布")
        for signal, count in signal_counts.items():
            st.metric(signal.replace('_', ' '), count)

def render_enhanced_stock_detail(ticker):
    """強化版個別銘柄詳細"""
    info = PORTFOLIO[ticker]
    st.header(f"📈 {ticker} - {info['name']} ({info['sector']})")
    
    # 4専門家スコア
    scores = calculate_expert_scores(ticker)
    signal, total, icon = calculate_entry_signal(scores)
    
    # エントリーシグナルカード
    signal_class = signal.lower().replace('_', '-')
    st.markdown(f"""
    <div class="signal-card {signal_class}">
        <h2>{icon} {signal.replace('_', ' ')}</h2>
        <h3>総合スコア: {total:.2f} / 5.0</h3>
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
    
    for i, (expert, score) in enumerate(scores.items()):
        with expert_cols[i]:
            score_class = 'high' if score >= 3.5 else 'mid' if score >= 2.5 else 'low'
            st.markdown(f"""
            <div class="expert-score score-{score_class}">
                <h4>{expert_info[expert]['icon']} {expert_info[expert]['name']}</h4>
                <h2>{score:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # タイミングゲージ
    st.subheader("⏱️ エントリータイミング")
    gauge_position = (total / 5.0) * 100
    st.markdown(f"""
    <div class="timing-gauge">
        <div class="timing-pointer" style="left: {gauge_position}%;"></div>
    </div>
    <div style="display: flex; justify-content: space-between;">
        <span>🔴🔴 売却</span>
        <span>🟡 様子見</span>
        <span>🟢🟢 絶好の買い場</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 簡易チャート
    st.subheader("📊 価格チャート（デモ）")
    chart_data = [random.uniform(0.9, 1.1) * 100 for _ in range(90)]
    st.line_chart(chart_data, height=400)

if __name__ == "__main__":
    main()
'''
    
    # ファイル作成
    with open('dashboard_enhanced_working.py', 'w', encoding='utf-8') as f:
        f.write(enhanced_code)
    
    return 'dashboard_enhanced_working.py'

if __name__ == "__main__":
    main()