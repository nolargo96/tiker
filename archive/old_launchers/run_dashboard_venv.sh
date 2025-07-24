#!/bin/bash

echo "========================================"
echo "Tiker Dashboard Pro - 仮想環境起動"
echo "========================================"
echo

# 仮想環境の選択
echo "利用可能な仮想環境:"
echo "1. fresh_env (最新)"
echo "2. dashboard_env"
echo "3. venv"
echo "4. .venv"
echo

read -p "使用する仮想環境を選択してください (1-4): " env_choice

case $env_choice in
    1) VENV_DIR="fresh_env";;
    2) VENV_DIR="dashboard_env";;
    3) VENV_DIR="venv";;
    4) VENV_DIR=".venv";;
    *) echo "無効な選択です"; exit 1;;
esac

# 仮想環境をアクティベート
echo "仮想環境 $VENV_DIR をアクティベートしています..."
source $VENV_DIR/bin/activate

# Pythonバージョン確認
echo
echo "Python バージョン:"
python --version
echo

# ダッシュボード選択
echo "起動するダッシュボードを選択してください:"
echo "1. Dashboard Pro Ultimate (究極版)"
echo "2. Dashboard Enhanced (強化版)"
echo "3. Dashboard Basic (基本版)"
echo "4. Dashboard Ultra Simple (超シンプル版)"
echo

read -p "番号を選択してください (1-4): " dashboard_choice

case $dashboard_choice in
    1) DASHBOARD="dashboard_pro.py";;
    2) DASHBOARD="dashboard_enhanced.py";;
    3) DASHBOARD="dashboard.py";;
    4) DASHBOARD="dashboard_ultra_simple.py";;
    *) echo "無効な選択です"; exit 1;;
esac

# 実行
echo
echo "========================================"
echo "Streamlit を起動しています..."
echo "ブラウザで http://localhost:8501 を開いてください"
echo "終了するには Ctrl+C を押してください"
echo "========================================"
echo

streamlit run $DASHBOARD