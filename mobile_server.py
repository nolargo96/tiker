#!/usr/bin/env python3
"""
ポートフォリオレポート モバイルサーバー
スマートフォンからポートフォリオレポートを閲覧するための簡易Webサーバー
"""

import os
import socket
import qrcode
import io
import base64
from flask import Flask, send_file, render_template_string, jsonify
from datetime import datetime
import glob

app = Flask(__name__)

# プロジェクトルートとレポートディレクトリの設定
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports', 'html')


def get_local_ip():
    """ローカルIPアドレスを取得"""
    try:
        # ダミー接続でローカルIPを取得
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def generate_qr_code(url):
    """URLのQRコードを生成"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 画像をBase64エンコード
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def get_latest_report():
    """最新のポートフォリオレポートのパスを取得"""
    report_pattern = os.path.join(REPORTS_DIR, 'portfolio_hybrid_report_*.html')
    report_files = glob.glob(report_pattern)
    
    if not report_files:
        return None
        
    # 最新のファイルを取得
    latest_report = max(report_files, key=os.path.getmtime)
    return latest_report


@app.route('/')
def index():
    """ホームページ - QRコードとアクセス情報を表示"""
    ip = get_local_ip()
    port = 5555
    url = f"http://{ip}:{port}/report"
    qr_code = generate_qr_code(url)
    
    # 最新レポートの確認
    latest_report = get_latest_report()
    has_report = latest_report is not None
    report_date = ""
    
    if has_report:
        # ファイル名から日付を抽出
        filename = os.path.basename(latest_report)
        try:
            date_part = filename.split('_')[-1].replace('.html', '')
            report_date = date_part
        except:
            report_date = "不明"
    
    html_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ポートフォリオレポート - モバイルアクセス</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                text-align: center;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #1e3a8a;
                margin-bottom: 10px;
            }
            .qr-container {
                margin: 30px 0;
            }
            .qr-code {
                max-width: 300px;
                height: auto;
            }
            .access-info {
                background: #f0f4ff;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .url {
                font-size: 1.2em;
                color: #1e3a8a;
                font-weight: bold;
                word-break: break-all;
                margin: 10px 0;
            }
            .button {
                display: inline-block;
                background: #1e3a8a;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 20px;
                font-weight: bold;
            }
            .button:hover {
                background: #1e4490;
            }
            .status {
                margin: 20px 0;
                padding: 15px;
                border-radius: 8px;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
            }
            .instructions {
                text-align: left;
                margin: 30px 0;
                line-height: 1.6;
            }
            .instructions h3 {
                color: #333;
                margin-bottom: 10px;
            }
            .instructions ol {
                padding-left: 20px;
            }
            .instructions li {
                margin: 8px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 ポートフォリオレポート</h1>
            <p>モバイルアクセスサーバー</p>
            
            {% if has_report %}
            <div class="status success">
                ✅ レポート準備完了<br>
                最新レポート: {{ report_date }}
            </div>
            
            <div class="qr-container">
                <h2>QRコードでアクセス</h2>
                <img src="{{ qr_code }}" alt="QR Code" class="qr-code">
            </div>
            
            <div class="access-info">
                <h3>またはURLを直接入力</h3>
                <div class="url">{{ url }}</div>
            </div>
            
            <a href="/report" class="button">レポートを表示</a>
            
            <div class="instructions">
                <h3>📱 スマホでの閲覧方法</h3>
                <ol>
                    <li>スマホが同じWi-Fiネットワークに接続されていることを確認</li>
                    <li>上記のQRコードをスマホのカメラで読み取る</li>
                    <li>または、スマホのブラウザに上記URLを直接入力</li>
                    <li>レポートが表示されます</li>
                </ol>
                
                <h3>💡 ヒント</h3>
                <ul style="padding-left: 20px; text-align: left;">
                    <li>レポートは自動的にモバイル表示に最適化されます</li>
                    <li>横スクロールで全ての情報を確認できます</li>
                    <li>タブをタップして銘柄を切り替えられます</li>
                </ul>
            </div>
            {% else %}
            <div class="status error">
                ❌ レポートが見つかりません<br>
                先にレポートを生成してください
            </div>
            
            <p>レポートを生成するには:</p>
            <pre style="text-align: left; background: #f5f5f5; padding: 10px; border-radius: 4px;">
python src/portfolio/portfolio_master_report_hybrid.py
            </pre>
            {% endif %}
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, 
                                has_report=has_report,
                                qr_code=qr_code,
                                url=url,
                                report_date=report_date)


@app.route('/report')
def report():
    """最新のポートフォリオレポートを表示"""
    latest_report = get_latest_report()
    
    if not latest_report:
        return "レポートが見つかりません。先にレポートを生成してください。", 404
    
    # HTMLファイルを読み込んで、相対パスを修正
    with open(latest_report, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # CSSとJSのパスを修正（同じディレクトリにあるため）
    html_content = html_content.replace('href="styles.css"', 'href="/static/styles.css"')
    html_content = html_content.replace('src="script.js"', 'src="/static/script.js"')
    
    return html_content


@app.route('/static/<filename>')
def static_files(filename):
    """静的ファイル（CSS、JS）を提供"""
    static_path = os.path.join(REPORTS_DIR, filename)
    if os.path.exists(static_path):
        return send_file(static_path)
    return "File not found", 404


@app.route('/api/status')
def api_status():
    """APIステータス確認"""
    latest_report = get_latest_report()
    has_report = latest_report is not None
    
    return jsonify({
        'status': 'ok',
        'has_report': has_report,
        'report_path': latest_report if has_report else None,
        'server_time': datetime.now().isoformat()
    })


def main():
    """メイン実行関数"""
    ip = get_local_ip()
    port = 5555
    
    print("\n" + "="*50)
    print("📱 ポートフォリオレポート モバイルサーバー")
    print("="*50)
    print(f"\n✅ サーバー起動中...")
    print(f"📍 ローカルIP: {ip}")
    print(f"🔗 アクセスURL: http://{ip}:{port}")
    print(f"\n💡 スマホでアクセスするには:")
    print(f"   1. スマホが同じWi-Fiに接続されていることを確認")
    print(f"   2. スマホのブラウザで上記URLにアクセス")
    print(f"   3. QRコードが表示されます")
    print(f"\n🛑 終了するには Ctrl+C を押してください")
    print("="*50 + "\n")
    
    # サーバー起動
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()