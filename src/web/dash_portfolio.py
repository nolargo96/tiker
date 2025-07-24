#!/usr/bin/env python3
"""
Tiker Dash Portfolio - Plotly Dash版ポートフォリオダッシュボード
Streamlitから移行した、より軽量で高速なダッシュボード実装

主要機能:
1. ハイブリッドポートフォリオメインビュー
2. リアルタイムパフォーマンス追跡
3. 高速なデータ更新とレスポンス
4. カスタマイズ可能なUIコンポーネント
5. 既存分析機能との完全統合
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
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

# Dashアプリケーション初期化
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)
app.title = "🚀 Tiker Dashboard - Dash Edition"

# カスタムCSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* カスタムスタイル */
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                background-color: #f8f9fa;
            }
            .navbar {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                box-shadow: 0 2px 4px rgba(0,0,0,.1);
            }
            .card {
                border: none;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,.1);
                transition: transform 0.2s;
            }
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,.15);
            }
            .metric-card {
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                border-left: 4px solid #667eea;
            }
            .portfolio-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# グローバル変数
PORTFOLIO_CONFIG = {
    "TSLA": 20, "FSLR": 20, "RKLB": 10, "ASTS": 10,
    "OKLO": 10, "JOBY": 10, "OII": 10, "LUNR": 5, "RDW": 5
}

# キャッシュマネージャー
cache_manager = CacheManager()

# ポートフォリオデータ取得関数
def get_portfolio_data() -> pd.DataFrame:
    """ポートフォリオデータを取得"""
    portfolio_data = []
    
    for ticker, allocation in PORTFOLIO_CONFIG.items():
        try:
            # キャッシュから取得または新規取得
            stock_data = cache_manager.get_or_fetch(ticker, lambda: yf.Ticker(ticker).history(period="1y"))
            if not stock_data.empty:
                current_price = stock_data['Close'].iloc[-1]
                prev_close = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
                change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
                
                # スコア計算
                tech_score = calculate_tech_score(stock_data)
                fund_score = calculate_fund_score(ticker, stock_data.iloc[-1])
                macro_score = calculate_macro_score(ticker)
                risk_score = calculate_risk_score(stock_data, allocation)
                overall_score = (tech_score + fund_score + macro_score + risk_score) / 4
                
                portfolio_data.append({
                    'Ticker': ticker,
                    'Allocation': allocation,
                    'Current Price': current_price,
                    'Change %': change_pct,
                    'Tech Score': tech_score,
                    'Fund Score': fund_score,
                    'Macro Score': macro_score,
                    'Risk Score': risk_score,
                    'Overall Score': overall_score,
                    'Signal': 'BUY' if overall_score >= 3.5 else 'HOLD' if overall_score >= 2.5 else 'SELL'
                })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            
    return pd.DataFrame(portfolio_data)

# ナビゲーションバー
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("ポートフォリオ", href="#portfolio", className="text-white")),
        dbc.NavItem(dbc.NavLink("分析", href="#analysis", className="text-white")),
        dbc.NavItem(dbc.NavLink("エクスポート", href="#export", className="text-white")),
    ],
    brand="🚀 Tiker Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
    className="mb-4"
)

# ポートフォリオヘッダー
def create_portfolio_header():
    """ポートフォリオヘッダーを作成"""
    return html.Div([
        html.Div([
            html.H1("ハイブリッドポートフォリオ", className="mb-3"),
            html.P("AI駆動の投資分析ダッシュボード", className="lead"),
            html.Hr(className="my-4"),
            html.Div([
                html.Span("最終更新: ", className="text-light"),
                html.Span(id="last-update", className="text-warning font-weight-bold"),
                dbc.Button("更新", id="refresh-btn", color="light", className="ml-3", size="sm")
            ])
        ], className="portfolio-header")
    ])

# メトリクスカード
def create_metric_card(title, value, change=None, icon=None):
    """メトリクスカードを作成"""
    change_color = "text-success" if change and change > 0 else "text-danger" if change and change < 0 else "text-muted"
    change_icon = "fa-arrow-up" if change and change > 0 else "fa-arrow-down" if change and change < 0 else ""
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H6(title, className="text-muted mb-2"),
                html.H3(value, className="mb-0"),
                html.Div([
                    html.I(className=f"fas {change_icon} {change_color} mr-1") if change else None,
                    html.Span(f"{change:.2f}%" if change else "", className=change_color)
                ]) if change is not None else None
            ])
        ])
    ], className="metric-card h-100")

# ポートフォリオテーブル
def create_portfolio_table(df):
    """ポートフォリオテーブルを作成"""
    return dash_table.DataTable(
        id='portfolio-table',
        columns=[
            {"name": "銘柄", "id": "Ticker", "type": "text"},
            {"name": "配分(%)", "id": "Allocation", "type": "numeric"},
            {"name": "現在価格($)", "id": "Current Price", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "変化率(%)", "id": "Change %", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "総合スコア", "id": "Overall Score", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "シグナル", "id": "Signal", "type": "text"},
        ],
        data=df.to_dict('records'),
        style_cell={
            'textAlign': 'center',
            'padding': '10px',
            'fontFamily': 'Arial'
        },
        style_header={
            'backgroundColor': 'rgb(102, 126, 234)',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'Change %', 'filter_query': '{Change %} > 0'},
                'color': 'green',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'Change %', 'filter_query': '{Change %} < 0'},
                'color': 'red',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'Signal', 'filter_query': '{Signal} = BUY'},
                'backgroundColor': '#d4edda',
                'color': '#155724',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'Signal', 'filter_query': '{Signal} = SELL'},
                'backgroundColor': '#f8d7da',
                'color': '#721c24',
                'fontWeight': 'bold'
            }
        ],
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_size=10
    )

# ポートフォリオチャート
def create_portfolio_charts(df):
    """ポートフォリオチャートを作成"""
    # アロケーションパイチャート
    allocation_fig = px.pie(
        df, 
        values='Allocation', 
        names='Ticker',
        title="ポートフォリオ配分",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    allocation_fig.update_traces(textposition='inside', textinfo='percent+label')
    allocation_fig.update_layout(height=400)
    
    # スコア比較レーダーチャート
    score_columns = ['Tech Score', 'Fund Score', 'Macro Score', 'Risk Score']
    radar_fig = go.Figure()
    
    for _, row in df.iterrows():
        radar_fig.add_trace(go.Scatterpolar(
            r=[row[col] for col in score_columns],
            theta=score_columns,
            fill='toself',
            name=row['Ticker']
        ))
    
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True,
        title="スコア比較",
        height=400
    )
    
    return allocation_fig, radar_fig

# メインレイアウト
app.layout = html.Div([
    navbar,
    dbc.Container([
        create_portfolio_header(),
        
        # サマリーメトリクス
        dbc.Row([
            dbc.Col([
                html.Div(id="summary-metrics", className="mb-4")
            ])
        ]),
        
        # ポートフォリオテーブル
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("ポートフォリオ詳細")),
                    dbc.CardBody([
                        html.Div(id="portfolio-table-container")
                    ])
                ])
            ], className="mb-4")
        ]),
        
        # チャート
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="allocation-chart")
            ], md=6),
            dbc.Col([
                dcc.Graph(id="score-chart")
            ], md=6)
        ]),
        
        # 更新インターバル
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # 60秒ごとに更新
            n_intervals=0
        ),
        
        # データストア
        dcc.Store(id='portfolio-data-store')
        
    ], fluid=True)
])

# コールバック: データ更新
@app.callback(
    Output('portfolio-data-store', 'data'),
    Output('last-update', 'children'),
    [Input('refresh-btn', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_data(n_clicks, n_intervals):
    """データを更新"""
    df = get_portfolio_data()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df.to_dict('records'), timestamp

# コールバック: サマリーメトリクス更新
@app.callback(
    Output('summary-metrics', 'children'),
    [Input('portfolio-data-store', 'data')]
)
def update_summary_metrics(data):
    """サマリーメトリクスを更新"""
    if not data:
        return html.Div("データ読み込み中...")
    
    df = pd.DataFrame(data)
    
    # メトリクス計算
    total_score = df['Overall Score'].mean()
    buy_signals = len(df[df['Signal'] == 'BUY'])
    avg_change = df['Change %'].mean()
    
    return dbc.Row([
        dbc.Col([
            create_metric_card("総合スコア", f"{total_score:.2f}", None, "fa-chart-line")
        ], md=3),
        dbc.Col([
            create_metric_card("買いシグナル", f"{buy_signals}/{len(df)}", None, "fa-signal")
        ], md=3),
        dbc.Col([
            create_metric_card("平均変化率", f"{avg_change:.2f}%", avg_change, "fa-percentage")
        ], md=3),
        dbc.Col([
            create_metric_card("ポートフォリオ数", str(len(df)), None, "fa-briefcase")
        ], md=3)
    ])

# コールバック: テーブル更新
@app.callback(
    Output('portfolio-table-container', 'children'),
    [Input('portfolio-data-store', 'data')]
)
def update_table(data):
    """テーブルを更新"""
    if not data:
        return html.Div("データ読み込み中...")
    
    df = pd.DataFrame(data)
    return create_portfolio_table(df)

# コールバック: チャート更新
@app.callback(
    Output('allocation-chart', 'figure'),
    Output('score-chart', 'figure'),
    [Input('portfolio-data-store', 'data')]
)
def update_charts(data):
    """チャートを更新"""
    if not data:
        empty_fig = go.Figure()
        return empty_fig, empty_fig
    
    df = pd.DataFrame(data)
    return create_portfolio_charts(df)

# メイン実行
if __name__ == '__main__':
    import sys
    port = 8050
    
    # コマンドライン引数からポート番号を取得
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        try:
            port = int(sys.argv[2])
        except ValueError:
            pass
    
    # 環境変数からポート番号を取得
    import os
    if 'DASH_PORT' in os.environ:
        try:
            port = int(os.environ['DASH_PORT'])
        except ValueError:
            pass
    
    app.run_server(debug=True, host='0.0.0.0', port=port)