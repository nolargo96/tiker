#!/usr/bin/env python3
"""
Tiker Simple Dashboard - 最小限のWebダッシュボード
Flask + vanilla JavaScriptで実装
"""

from flask import Flask, render_template, jsonify, request, send_file
import os
import sys
import json
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.analysis.unified_analyzer import (
    calculate_tech_score, calculate_fund_score, 
    calculate_macro_score, calculate_risk_score
)
from src.analysis.expert_discussion_generator import ExpertDiscussionGenerator
from src.analysis.stock_analyzer_lib import StockAnalyzer, TechnicalIndicators

app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

# ポートフォリオ設定
PORTFOLIO = {
    'TSLA': {'name': 'Tesla', 'allocation': 20},
    'FSLR': {'name': 'First Solar', 'allocation': 20},
    'RKLB': {'name': 'Rocket Lab', 'allocation': 10},
    'ASTS': {'name': 'AST SpaceMobile', 'allocation': 10},
    'OKLO': {'name': 'Oklo', 'allocation': 10},
    'JOBY': {'name': 'Joby Aviation', 'allocation': 10},
    'OII': {'name': 'Oceaneering', 'allocation': 10},
    'LUNR': {'name': 'Intuitive Machines', 'allocation': 5},
    'RDW': {'name': 'Redwire', 'allocation': 5}
}

# 討論ジェネレーター
discussion_generator = ExpertDiscussionGenerator()

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html', portfolio=PORTFOLIO)

@app.route('/api/portfolio_summary')
def portfolio_summary():
    """ポートフォリオサマリーを取得"""
    try:
        summary = []
        total_value = 0
        
        for ticker, info in PORTFOLIO.items():
            stock = yf.Ticker(ticker)
            data = stock.history(period='1d')
            
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                prev_close = stock.info.get('previousClose', current_price)
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                summary.append({
                    'ticker': ticker,
                    'name': info['name'],
                    'allocation': info['allocation'],
                    'price': round(current_price, 2),
                    'change_pct': round(change_pct, 2),
                    'value': round(current_price * info['allocation'] * 100, 2)
                })
                total_value += current_price * info['allocation'] * 100
        
        return jsonify({
            'success': True,
            'data': summary,
            'total_value': round(total_value, 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stock/<ticker>')
def stock_detail(ticker):
    """個別銘柄の詳細情報を取得"""
    try:
        if ticker not in PORTFOLIO:
            return jsonify({'success': False, 'error': 'Invalid ticker'})
        
        # 株価データ取得
        stock = yf.Ticker(ticker)
        df = stock.history(period='6mo')
        
        if df.empty:
            return jsonify({'success': False, 'error': 'No data available'})
        
        # テクニカル指標計算
        df = TechnicalIndicators.add_all_indicators(df)
        
        # 現在のデータ
        current_data = {
            'price': df['Close'].iloc[-1],
            'ema20': df['EMA20'].iloc[-1],
            'ema50': df['EMA50'].iloc[-1],
            'sma200': df['SMA200'].iloc[-1] if 'SMA200' in df else df['Close'].mean(),
            'rsi': df['RSI'].iloc[-1],
            'bb_upper': df['BB_upper'].iloc[-1],
            'bb_lower': df['BB_lower'].iloc[-1],
            'atr': df['ATR'].iloc[-1],
            'volume': df['Volume'].iloc[-1],
            'low_52w': df['Low'].min(),
            'high_52w': df['High'].max(),
            'recent_low': df['Low'].tail(20).min(),
            'recent_high': df['High'].tail(20).max()
        }
        
        # スコア計算
        tech_score = calculate_tech_score(df)
        fund_score = calculate_fund_score(ticker, df.iloc[-1])
        macro_score = calculate_macro_score(ticker)
        risk_score = calculate_risk_score(df, PORTFOLIO[ticker]['allocation'])
        
        # 4専門家の討論生成
        analysis = discussion_generator.generate_full_analysis(
            ticker, df, datetime.now().strftime('%Y-%m-%d')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'ticker': ticker,
                'name': PORTFOLIO[ticker]['name'],
                'current_price': round(current_data['price'], 2),
                'scores': {
                    'tech': tech_score,
                    'fund': fund_score,
                    'macro': macro_score,
                    'risk': risk_score,
                    'overall': round((tech_score + fund_score + macro_score + risk_score) / 4, 2)
                },
                'technical_data': {k: round(v, 2) if isinstance(v, (int, float)) else v 
                                 for k, v in current_data.items()},
                'discussion_rounds': analysis.get('discussion_rounds', []),
                'recommendation': analysis.get('final_recommendation', {}),
                'price_targets': analysis.get('price_targets', {})
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """新しいレポートを生成"""
    try:
        data = request.json
        ticker = data.get('ticker', 'portfolio')
        
        if ticker == 'portfolio':
            # ポートフォリオ全体のレポート生成
            from src.portfolio.portfolio_master_report_hybrid import PortfolioMasterReportHybrid
            generator = PortfolioMasterReportHybrid()
            report_path = generator.generate()
        else:
            # 個別銘柄のレポート生成
            analyzer = StockAnalyzer()
            success, report_path = analyzer.generate_html_report(ticker)
            
            if not success:
                return jsonify({'success': False, 'error': report_path})
        
        return jsonify({
            'success': True,
            'report_path': report_path,
            'message': f'レポートを生成しました: {os.path.basename(report_path)}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/reports')
def list_reports():
    """生成済みレポート一覧"""
    try:
        reports_dir = Path('reports/html')
        reports = []
        
        if reports_dir.exists():
            for file in reports_dir.glob('*.html'):
                if file.name not in ['script.js', 'styles.css']:
                    reports.append({
                        'name': file.name,
                        'path': str(file),
                        'size': f"{file.stat().st_size / 1024:.1f} KB",
                        'modified': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                    })
        
        reports.sort(key=lambda x: x['modified'], reverse=True)
        return render_template('reports.html', reports=reports)
        
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/view_report/<path:filename>')
def view_report(filename):
    """レポートを表示"""
    try:
        return send_file(f'reports/html/{filename}')
    except Exception as e:
        return f"Error: {str(e)}", 404

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    print(f"Starting Tiker Simple Dashboard on http://localhost:{port}")
    app.run(debug=False, host='127.0.0.1', port=port)