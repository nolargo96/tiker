#!/bin/bash
# 仮想環境内でレポート生成を実行するスクリプト

source venv/bin/activate

if [ $# -eq 0 ]; then
    echo "使用法: $0 <command>"
    echo "例: $0 python run_analysis.py"
    echo "例: $0 python src/portfolio/portfolio_master_report_hybrid.py"
    exit 1
fi

echo "仮想環境内で実行中: $@"
exec "$@"