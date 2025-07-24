#!/usr/bin/env python3
"""
Tiker Dashboard Runner
統合ダッシュボードの実行スクリプト
"""

import sys
import os

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 新しいパッケージ構造からインポート
from src.web.dashboard_consolidated import UltimateDashboardApp

if __name__ == "__main__":
    # Streamlitアプリケーションの実行
    app = UltimateDashboardApp()
    app.run()