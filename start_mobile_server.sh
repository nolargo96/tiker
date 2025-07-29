#!/bin/bash

echo "==============================================="
echo "   ポートフォリオ モバイルサーバー起動"
echo "==============================================="
echo

# 仮想環境をアクティベート
source venv/bin/activate

# 必要なパッケージの確認とインストール
echo "必要なパッケージを確認中..."

if ! pip show flask >/dev/null 2>&1; then
    echo "Flaskをインストール中..."
    pip install flask
fi

if ! pip show qrcode >/dev/null 2>&1; then
    echo "QRコードライブラリをインストール中..."
    pip install "qrcode[pil]"
fi

echo
echo "サーバーを起動中..."
echo

# モバイルサーバーを起動
python mobile_server.py