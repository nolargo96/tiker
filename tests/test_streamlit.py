#!/usr/bin/env python3
"""
Streamlit動作テスト
"""

import streamlit as st
import sys
import os

st.set_page_config(page_title="Streamlit Test", layout="wide")

st.title("🚀 Streamlit 動作テスト")

st.write("## 環境情報")
st.write(f"- Python バージョン: {sys.version}")
st.write(f"- Streamlit バージョン: {st.__version__}")
st.write(f"- 現在のディレクトリ: {os.getcwd()}")
st.write(f"- ファイルパス: {__file__}")

st.write("## ダッシュボードファイルの確認")

dashboard_files = [
    "dashboard_pro.py",
    "dashboard_enhanced.py", 
    "dashboard.py",
    "dashboard_ultra_simple.py"
]

for file in dashboard_files:
    if os.path.exists(file):
        st.success(f"✓ {file} が存在します")
    else:
        st.error(f"✗ {file} が見つかりません")

st.write("## 必要なモジュールの確認")

modules = [
    "pandas",
    "numpy",
    "yfinance",
    "plotly",
    "xlsxwriter",
    "reportlab",
    "matplotlib",
    "seaborn"
]

missing_modules = []
for module in modules:
    try:
        __import__(module)
        st.success(f"✓ {module}")
    except ImportError:
        st.error(f"✗ {module} がインストールされていません")
        missing_modules.append(module)

if missing_modules:
    st.warning(f"不足モジュール: {', '.join(missing_modules)}")
    st.code(f"pip install {' '.join(missing_modules)}")
else:
    st.success("すべての必要モジュールがインストールされています！")

st.write("## テスト完了")
st.info("このページが表示されていれば、Streamlitは正常に動作しています。")

if st.button("Dashboard Pro を起動"):
    st.info("コマンドラインから以下を実行してください:")
    st.code("streamlit run dashboard_pro.py")