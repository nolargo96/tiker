#!/bin/bash
# Tiker Dashboard 起動スクリプト

echo "🚀 Tiker Interactive Dashboard を起動します..."
echo ""

# Pythonがインストールされているか確認
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3が見つかりません。インストールしてください。"
    exit 1
fi

# Streamlitがインストールされているか確認
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 必要なライブラリをインストールしています..."
    
    # pipが利用可能か確認
    if command -v pip &> /dev/null; then
        pip install -r requirements.txt
    elif command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
    else
        echo "❌ pipが見つかりません。以下のコマンドを手動で実行してください："
        echo "   python3 -m pip install -r requirements.txt"
        exit 1
    fi
fi

# ダッシュボードの選択
echo "どちらのダッシュボードを起動しますか？"
echo "1) 基本版 (dashboard.py)"
echo "2) 強化版 - 4専門家統合型 (dashboard_enhanced.py) [推奨]"
echo ""
read -p "選択してください (1 or 2): " choice

case $choice in
    1)
        echo "📊 基本版ダッシュボードを起動中..."
        python3 -m streamlit run dashboard.py
        ;;
    2)
        echo "🚀 強化版ダッシュボードを起動中..."
        python3 -m streamlit run dashboard_enhanced.py
        ;;
    *)
        echo "🚀 強化版ダッシュボードを起動中... (デフォルト)"
        python3 -m streamlit run dashboard_enhanced.py
        ;;
esac