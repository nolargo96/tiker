#!/usr/bin/env python3
"""
WSL環境でのダッシュボード起動ヘルパー
ブラウザアクセス問題を解決
"""

import subprocess
import time
import socket
import webbrowser
import sys
import os

def check_port(port):
    """ポートが使用中かチェック"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def find_available_port(start_port=8501):
    """利用可能なポートを探す"""
    for port in range(start_port, start_port + 10):
        if not check_port(port):
            return port
    return None

def launch_dashboard(dashboard_file, port):
    """ダッシュボードを起動"""
    cmd = [
        'streamlit', 'run', dashboard_file,
        '--server.port', str(port),
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false'
    ]
    
    # WSL環境でのブラウザ起動を無効化
    env = os.environ.copy()
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    return subprocess.Popen(cmd, env=env)

def main():
    print("="*50)
    print("Tiker Dashboard Launcher for WSL")
    print("="*50)
    print()
    
    # ダッシュボード選択
    dashboards = {
        '1': 'dashboard_pro.py',
        '2': 'dashboard_enhanced.py',
        '3': 'dashboard.py',
        '4': 'dashboard_ultra_simple.py'
    }
    
    print("利用可能なダッシュボード:")
    print("1. Dashboard Pro Ultimate (究極版)")
    print("2. Dashboard Enhanced (強化版)")
    print("3. Dashboard Basic (基本版)")
    print("4. Dashboard Ultra Simple (シンプル版)")
    print()
    
    choice = input("選択してください (1-4): ")
    
    if choice not in dashboards:
        print("無効な選択です")
        sys.exit(1)
    
    dashboard_file = dashboards[choice]
    
    if not os.path.exists(dashboard_file):
        print(f"エラー: {dashboard_file} が見つかりません")
        sys.exit(1)
    
    # 利用可能なポートを探す
    port = find_available_port()
    if not port:
        print("利用可能なポートが見つかりません")
        sys.exit(1)
    
    print(f"\nポート {port} でダッシュボードを起動しています...")
    
    # ダッシュボードを起動
    process = launch_dashboard(dashboard_file, port)
    
    # 起動を待つ
    print("起動を待っています", end="")
    for i in range(10):
        time.sleep(1)
        print(".", end="", flush=True)
        if check_port(port):
            break
    print()
    
    if check_port(port):
        print(f"\n✓ ダッシュボードが起動しました!")
        print(f"\n以下のURLをブラウザで開いてください:")
        print(f"http://localhost:{port}")
        print(f"\nまたは、Windows側のコマンドプロンプトで:")
        print(f"start http://localhost:{port}")
        print(f"\n終了するには Ctrl+C を押してください")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n\nダッシュボードを停止しています...")
            process.terminate()
            process.wait()
            print("停止しました")
    else:
        print("\n✗ ダッシュボードの起動に失敗しました")
        process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()