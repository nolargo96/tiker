#!/usr/bin/env python3
"""
Tiker Dashboard - テスト用簡易版
実行環境のテストと基本動作確認用
"""

import sys
import os

print("=== Tiker Dashboard 起動テスト ===")
print(f"Python バージョン: {sys.version}")
print(f"実行ディレクトリ: {os.getcwd()}")

# 必要なライブラリのインポートテスト
required_modules = {
    'streamlit': 'Streamlit (Webフレームワーク)',
    'plotly': 'Plotly (インタラクティブチャート)',
    'pandas': 'Pandas (データ処理)',
    'numpy': 'NumPy (数値計算)',
    'yfinance': 'yfinance (株価データ取得)',
}

print("\n📦 ライブラリ確認:")
missing_modules = []

for module, description in required_modules.items():
    try:
        __import__(module)
        print(f"✅ {module}: {description} - OK")
    except ImportError:
        print(f"❌ {module}: {description} - 未インストール")
        missing_modules.append(module)

if missing_modules:
    print(f"\n⚠️  以下のライブラリが不足しています: {', '.join(missing_modules)}")
    print("\n📋 インストール方法:")
    print("1) pip を使用:")
    print("   pip install " + " ".join(missing_modules))
    print("\n2) uv を使用 (高速):")
    print("   uv pip install " + " ".join(missing_modules))
    print("\n3) requirements.txt を使用:")
    print("   pip install -r requirements.txt")
else:
    print("\n✅ すべてのライブラリが正常にインストールされています！")
    
    # Streamlitアプリの基本テスト
    try:
        import streamlit as st
        print("\n🚀 Streamlitダッシュボードを起動できます:")
        print("   streamlit run dashboard_enhanced.py")
        print("\nまたは簡易起動:")
        print("   ./run_dashboard.sh  (Linux/Mac)")
        print("   run_dashboard.bat   (Windows)")
        
        # 既存ファイルの確認
        print("\n📁 ダッシュボードファイル:")
        dashboard_files = [
            'dashboard.py',
            'dashboard_enhanced.py',
            'DASHBOARD_README.md'
        ]
        
        for file in dashboard_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"   ✅ {file} ({size:,} bytes)")
            else:
                print(f"   ❌ {file} - 見つかりません")
                
    except Exception as e:
        print(f"\n❌ エラー: {e}")

# 既存の分析システムファイル確認
print("\n📊 既存の分析システム:")
core_files = [
    'unified_stock_analyzer.py',
    'stock_analyzer_lib.py',
    'cache_manager.py',
    'config.yaml'
]

for file in core_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - 見つかりません")

print("\n" + "="*50)