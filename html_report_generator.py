"""
HTML Report Generator for Tiker Stock Analyzer
HTMLレポート生成機能 - 既存のMarkdownレポートを拡張してHTMLレポートを生成

このモジュールは、tikerプロジェクトのHTMLレポート生成機能を提供します：
- インタラクティブなチャート表示
- 専門家分析のタブ形式表示
- レスポンシブデザイン
- 印刷対応
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import base64
from stock_analyzer_lib import ConfigManager, StockDataManager, TechnicalIndicators


class HTMLReportGenerator:
    """HTMLレポート生成クラス"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        HTMLレポート生成クラスの初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config = ConfigManager(config_path)
        self.data_manager = StockDataManager(self.config)
        self.template_dir = self._ensure_template_directory()
        
    def _ensure_template_directory(self) -> Path:
        """テンプレートディレクトリを作成・確保"""
        template_dir = Path(self.config.get('directories.reports', './reports')) / 'templates'
        template_dir.mkdir(parents=True, exist_ok=True)
        return template_dir
    
    def generate_stock_html_report(self, ticker: str, analysis_data: pd.DataFrame, 
                                 chart_path: str, date_str: str, 
                                 markdown_content: Optional[str] = None) -> Tuple[bool, str]:
        """
        個別株式のHTMLレポートを生成
        
        Args:
            ticker (str): ティッカーシンボル
            analysis_data (pd.DataFrame): 分析データ
            chart_path (str): チャート画像のパス
            date_str (str): 分析基準日
            markdown_content (str, optional): 既存のMarkdownレポート内容
            
        Returns:
            Tuple[bool, str]: 成功フラグとファイルパス/エラーメッセージ
        """
        try:
            # HTMLレポートファイルパス
            reports_dir = Path(self.config.get('directories.reports', './reports'))
            html_dir = reports_dir / 'html'
            html_dir.mkdir(parents=True, exist_ok=True)
            
            html_filename = f"{ticker}_analysis_{date_str}.html"
            html_filepath = html_dir / html_filename
            
            # チャート画像をBase64エンコード
            chart_base64 = self._encode_image_to_base64(chart_path)
            
            # データ分析
            latest_data = self._extract_latest_data(analysis_data)
            technical_summary = self._generate_technical_summary(analysis_data)
            chart_data = self._prepare_chart_data(analysis_data)
            
            # HTMLコンテンツ生成
            html_content = self._generate_html_template(
                ticker=ticker,
                date_str=date_str,
                latest_data=latest_data,
                technical_summary=technical_summary,
                chart_base64=chart_base64,
                chart_data=chart_data,
                markdown_content=markdown_content
            )
            
            # ファイル保存
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True, str(html_filepath)
            
        except Exception as e:
            return False, f"HTMLレポート生成エラー: {str(e)}"
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """画像をBase64エンコード"""
        try:
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return f"data:image/png;base64,{encoded_string}"
        except Exception:
            return ""
    
    def _extract_latest_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """最新データを抽出"""
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        return {
            'date': df.index[-1].strftime('%Y-%m-%d'),
            'close': latest['Close'],
            'volume': latest['Volume'],
            'high': latest['High'],
            'low': latest['Low'],
            'open': latest['Open'],
            'ema20': latest.get('EMA20'),
            'ema50': latest.get('EMA50'),
            'sma200': latest.get('SMA200'),
            'rsi': latest.get('RSI'),
            'bb_upper': latest.get('BB_upper'),
            'bb_lower': latest.get('BB_lower'),
            'atr': latest.get('ATR')
        }
    
    def _generate_technical_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """テクニカル指標のサマリー生成"""
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        
        # トレンド分析
        trend_signals = []
        if not pd.isna(latest.get('EMA20')) and not pd.isna(latest.get('EMA50')):
            if latest['EMA20'] > latest['EMA50']:
                trend_signals.append("短期トレンド: 上昇")
            else:
                trend_signals.append("短期トレンド: 下降")
        
        if not pd.isna(latest.get('SMA200')):
            if latest['Close'] > latest['SMA200']:
                trend_signals.append("長期トレンド: 上昇")
            else:
                trend_signals.append("長期トレンド: 下降")
        
        # RSI分析
        rsi_signal = ""
        if not pd.isna(latest.get('RSI')):
            rsi_value = latest['RSI']
            if rsi_value > 70:
                rsi_signal = "過買い圏"
            elif rsi_value < 30:
                rsi_signal = "過売り圏"
            else:
                rsi_signal = "中立圏"
        
        # ボリンジャーバンド分析
        bb_signal = ""
        if not pd.isna(latest.get('BB_upper')) and not pd.isna(latest.get('BB_lower')):
            if latest['Close'] > latest['BB_upper']:
                bb_signal = "上限突破"
            elif latest['Close'] < latest['BB_lower']:
                bb_signal = "下限突破"
            else:
                bb_signal = "バンド内"
        
        return {
            'trend_signals': trend_signals,
            'rsi_signal': rsi_signal,
            'bb_signal': bb_signal,
            'volatility': latest.get('ATR', 0)
        }
    
    def _prepare_chart_data(self, df: pd.DataFrame) -> Dict[str, List]:
        """チャートデータの準備（JavaScript用）"""
        if df.empty:
            return {}
        
        # 最新30日分のデータを抽出
        df_recent = df.tail(30)
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in df_recent.index],
            'prices': df_recent['Close'].tolist(),
            'volumes': df_recent['Volume'].tolist(),
            'ema20': df_recent.get('EMA20', pd.Series()).fillna(0).tolist(),
            'ema50': df_recent.get('EMA50', pd.Series()).fillna(0).tolist(),
            'sma200': df_recent.get('SMA200', pd.Series()).fillna(0).tolist(),
            'rsi': df_recent.get('RSI', pd.Series()).fillna(0).tolist()
        }
    
    def _generate_html_template(self, ticker: str, date_str: str, 
                               latest_data: Dict[str, Any], 
                               technical_summary: Dict[str, Any],
                               chart_base64: str, chart_data: Dict[str, List],
                               markdown_content: Optional[str] = None) -> str:
        """HTMLテンプレートを生成"""
        
        # チャートデータをJSONとして埋め込み
        chart_data_json = json.dumps(chart_data, ensure_ascii=False)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ticker} 株価分析レポート - {date_str}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1><span class="ticker">{ticker}</span> 株価分析レポート</h1>
            <p class="date">分析基準日: {date_str}</p>
        </header>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>最新価格</h3>
                <div class="price">${latest_data.get('close', 0):.2f}</div>
                <div class="date">{latest_data.get('date', '')}</div>
            </div>
            
            <div class="summary-card">
                <h3>出来高</h3>
                <div class="volume">{latest_data.get('volume', 0):,.0f}</div>
            </div>
            
            <div class="summary-card">
                <h3>RSI</h3>
                <div class="rsi rsi-{self._get_rsi_class(latest_data.get('rsi'))}">{latest_data.get('rsi', 0):.1f}</div>
                <div class="signal">{technical_summary.get('rsi_signal', '')}</div>
            </div>
            
            <div class="summary-card">
                <h3>ボリンジャーバンド</h3>
                <div class="bb-signal">{technical_summary.get('bb_signal', '')}</div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab-button active" onclick="openTab(event, 'chart-tab')">チャート</button>
            <button class="tab-button" onclick="openTab(event, 'technical-tab')">テクニカル分析</button>
            <button class="tab-button" onclick="openTab(event, 'data-tab')">データ</button>
            """ + ('<button class="tab-button" onclick="openTab(event, \'expert-tab\')">専門家分析</button>' if markdown_content else '') + """
        </div>
        
        <div id="chart-tab" class="tab-content active">
            <div class="chart-section">
                <h2>価格チャート</h2>
                """ + (f'<img src="{chart_base64}" alt="{ticker} チャート" class="main-chart" onclick="toggleFullscreen(this)">' if chart_base64 else '<p>チャート画像が利用できません。</p>') + """
                
                <div class="interactive-charts">
                    <div class="chart-container">
                        <canvas id="priceChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="rsiChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="technical-tab" class="tab-content">
            <div class="technical-section">
                <h2>テクニカル指標サマリー</h2>
                
                <div class="indicators-grid">
                    <div class="indicator-card">
                        <h3>移動平均線</h3>
                        <div class="indicator-values">
                            <div>20日EMA: ${latest_data.get('ema20', 0):.2f}</div>
                            <div>50日EMA: ${latest_data.get('ema50', 0):.2f}</div>
                            <div>200日SMA: ${latest_data.get('sma200', 0):.2f}</div>
                        </div>
                    </div>
                    
                    <div class="indicator-card">
                        <h3>ボリンジャーバンド</h3>
                        <div class="indicator-values">
                            <div>上限: ${latest_data.get('bb_upper', 0):.2f}</div>
                            <div>下限: ${latest_data.get('bb_lower', 0):.2f}</div>
                            <div>状態: {technical_summary.get('bb_signal', '')}</div>
                        </div>
                    </div>
                    
                    <div class="indicator-card">
                        <h3>トレンド分析</h3>
                        <div class="trend-signals">
                            {''.join(f'<div class="trend-item">{signal}</div>' for signal in technical_summary.get('trend_signals', []))}
                        </div>
                    </div>
                    
                    <div class="indicator-card">
                        <h3>ボラティリティ</h3>
                        <div class="indicator-values">
                            <div>ATR(14): ${latest_data.get('atr', 0):.2f}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="data-tab" class="tab-content">
            <div class="data-section">
                <h2>詳細データ</h2>
                <div class="data-table">
                    <table>
                        <tr><th>項目</th><th>値</th></tr>
                        <tr><td>終値</td><td>${latest_data.get('close', 0):.2f}</td></tr>
                        <tr><td>始値</td><td>${latest_data.get('open', 0):.2f}</td></tr>
                        <tr><td>高値</td><td>${latest_data.get('high', 0):.2f}</td></tr>
                        <tr><td>安値</td><td>${latest_data.get('low', 0):.2f}</td></tr>
                        <tr><td>出来高</td><td>{latest_data.get('volume', 0):,.0f}</td></tr>
                        <tr><td>RSI(14)</td><td>{latest_data.get('rsi', 0):.2f}</td></tr>
                        <tr><td>ATR(14)</td><td>${latest_data.get('atr', 0):.2f}</td></tr>
                    </table>
                </div>
            </div>
        </div>
        
        """ + (self._generate_expert_tab_html(markdown_content) if markdown_content else '') + """
        
        <footer class="footer">
            <p>{self.config.get('disclaimer', '本情報は教育目的のシミュレーションです。')}</p>
            <p>生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
    
    <script>
        const chartData = {chart_data_json};
        
        {self._get_javascript_code()}
    </script>
</body>
</html>"""
        
        return html_content
    
    def _get_rsi_class(self, rsi_value: Optional[float]) -> str:
        """RSI値に基づくCSSクラスを取得"""
        if rsi_value is None:
            return "neutral"
        if rsi_value > 70:
            return "overbought"
        elif rsi_value < 30:
            return "oversold"
        else:
            return "neutral"
    
    def _generate_expert_tab_html(self, markdown_content: str) -> str:
        """専門家分析タブのHTMLを生成"""
        converted_html = self._convert_markdown_to_html(markdown_content)
        return f"""
        <div id="expert-tab" class="tab-content">
            <div class="expert-section">
                <h2>専門家分析</h2>
                <div class="markdown-content">
                    {converted_html}
                </div>
            </div>
        </div>
        """
    
    def _convert_markdown_to_html(self, markdown_content: Optional[str]) -> str:
        """簡単なMarkdown to HTML変換"""
        if not markdown_content:
            return ""
        
        # 基本的なMarkdown要素の変換
        html_content = markdown_content
        
        # ヘッダーの変換
        html_content = html_content.replace('### ', '<h3>').replace('\n', '</h3>\n')
        html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n')
        
        # 段落の変換
        html_content = html_content.replace('\n\n', '</p><p>')
        html_content = f'<p>{html_content}</p>'
        
        # 改行の変換
        html_content = html_content.replace('\n', '<br>')
        
        return html_content
    
    def _get_css_styles(self) -> str:
        """CSSスタイルを取得"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .ticker {
            background-color: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        
        .date {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }
        
        .summary-card h3 {
            color: #666;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .price {
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .volume {
            font-size: 1.8em;
            font-weight: bold;
            color: #27ae60;
        }
        
        .rsi {
            font-size: 2em;
            font-weight: bold;
        }
        
        .rsi-overbought { color: #e74c3c; }
        .rsi-oversold { color: #3498db; }
        .rsi-neutral { color: #f39c12; }
        
        .tabs {
            display: flex;
            border-bottom: 2px solid #ddd;
            margin-bottom: 20px;
        }
        
        .tab-button {
            background: none;
            border: none;
            padding: 15px 30px;
            cursor: pointer;
            font-size: 1.1em;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-button:hover {
            background-color: #f8f9fa;
        }
        
        .tab-content {
            display: none;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .tab-content.active {
            display: block;
        }
        
        .main-chart {
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        
        .main-chart:hover {
            transform: scale(1.02);
        }
        
        .interactive-charts {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 30px;
        }
        
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .indicators-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .indicator-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .indicator-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .indicator-values div {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        .indicator-values div:last-child {
            border-bottom: none;
        }
        
        .trend-signals {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .trend-item {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        
        .data-table {
            overflow-x: auto;
        }
        
        .data-table table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .data-table th,
        .data-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        .data-table th {
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }
        
        .data-table tr:hover {
            background-color: #f5f5f5;
        }
        
        .markdown-content {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            color: #666;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        .fullscreen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .fullscreen img {
            max-width: 95%;
            max-height: 95%;
            transform: none;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .summary-grid {
                grid-template-columns: 1fr;
            }
            
            .interactive-charts {
                grid-template-columns: 1fr;
            }
            
            .indicators-grid {
                grid-template-columns: 1fr;
            }
            
            .tabs {
                flex-wrap: wrap;
            }
            
            .tab-button {
                padding: 10px 15px;
                font-size: 1em;
            }
        }
        
        @media print {
            .tabs, .tab-button {
                display: none;
            }
            
            .tab-content {
                display: block !important;
            }
            
            .container {
                box-shadow: none;
            }
        }
        """
    
    def _get_javascript_code(self) -> str:
        """JavaScriptコードを取得"""
        return """
        // タブ切り替え機能
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].classList.remove("active");
            }
            tablinks = document.getElementsByClassName("tab-button");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].classList.remove("active");
            }
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }
        
        // 画像フルスクリーン機能
        function toggleFullscreen(img) {
            if (document.fullscreenElement) {
                document.exitFullscreen();
                img.classList.remove("fullscreen");
            } else {
                var div = document.createElement("div");
                div.className = "fullscreen";
                div.onclick = function() {
                    document.body.removeChild(div);
                };
                var newImg = img.cloneNode(true);
                newImg.onclick = function(e) {
                    e.stopPropagation();
                };
                div.appendChild(newImg);
                document.body.appendChild(div);
            }
        }
        
        // Chart.jsによるインタラクティブチャート
        document.addEventListener('DOMContentLoaded', function() {
            if (chartData && chartData.dates && chartData.prices) {
                // 価格チャート
                const priceCtx = document.getElementById('priceChart');
                if (priceCtx) {
                    new Chart(priceCtx, {
                        type: 'line',
                        data: {
                            labels: chartData.dates,
                            datasets: [{
                                label: '終値',
                                data: chartData.prices,
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                borderWidth: 2,
                                fill: true
                            }, {
                                label: '20日EMA',
                                data: chartData.ema20,
                                borderColor: '#3498db',
                                borderWidth: 1,
                                fill: false
                            }, {
                                label: '50日EMA',
                                data: chartData.ema50,
                                borderColor: '#f39c12',
                                borderWidth: 1,
                                fill: false
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: false,
                                    title: {
                                        display: true,
                                        text: '価格 (USD)'
                                    }
                                }
                            },
                            plugins: {
                                title: {
                                    display: true,
                                    text: '価格推移（最新30日）'
                                }
                            }
                        }
                    });
                }
                
                // RSIチャート
                const rsiCtx = document.getElementById('rsiChart');
                if (rsiCtx && chartData.rsi) {
                    new Chart(rsiCtx, {
                        type: 'line',
                        data: {
                            labels: chartData.dates,
                            datasets: [{
                                label: 'RSI',
                                data: chartData.rsi,
                                borderColor: '#e74c3c',
                                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                                borderWidth: 2,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    min: 0,
                                    max: 100,
                                    title: {
                                        display: true,
                                        text: 'RSI'
                                    }
                                }
                            },
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'RSI (14日)'
                                },
                                annotation: {
                                    annotations: {
                                        line1: {
                                            type: 'line',
                                            yMin: 70,
                                            yMax: 70,
                                            borderColor: 'rgba(255, 99, 132, 0.5)',
                                            borderWidth: 2,
                                        },
                                        line2: {
                                            type: 'line',
                                            yMin: 30,
                                            yMax: 30,
                                            borderColor: 'rgba(54, 162, 235, 0.5)',
                                            borderWidth: 2,
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
            }
        });
        """


# 使用例
if __name__ == '__main__':
    # HTMLレポートジェネレータのテスト
    generator = HTMLReportGenerator()
    
    # サンプルデータでテスト
    sample_data = pd.DataFrame({
        'Close': [100, 102, 98, 105, 103],
        'Volume': [1000000, 1200000, 900000, 1100000, 1050000],
        'High': [102, 104, 100, 107, 105],
        'Low': [98, 100, 95, 102, 101],
        'Open': [99, 101, 99, 103, 104],
        'EMA20': [100, 101, 99.5, 102, 102.5],
        'EMA50': [99, 100, 99.8, 101, 101.5],
        'SMA200': [98, 98.5, 98.2, 99, 99.5],
        'RSI': [45, 55, 35, 65, 60],
        'BB_upper': [105, 107, 103, 110, 108],
        'BB_lower': [95, 97, 93, 100, 98],
        'ATR': [2.5, 2.8, 2.3, 3.1, 2.9]
    })
    
    success, result = generator.generate_stock_html_report(
        ticker='TSLA',
        analysis_data=sample_data,
        chart_path='./charts/TSLA_chart_2025-07-03.png',
        date_str='2025-07-03',
        markdown_content='# サンプルMarkdownコンテンツ\n\n## 分析結果\n\nサンプルの分析結果です。'
    )
    
    print(f"HTMLレポート生成: {success}")
    print(f"結果: {result}")