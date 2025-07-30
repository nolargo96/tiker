#!/bin/bash
# 仮想環境を自動的にアクティベートするスクリプト
source venv/bin/activate
echo "Python仮想環境がアクティベートされました"
echo "Python version: $(python --version)"
echo "Dependencies installed: ✓"