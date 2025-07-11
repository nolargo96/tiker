#!/usr/bin/env python3
"""
TIKER プロジェクト初期化・クリーンアップスクリプト
使用方法: python3 scripts/setup_clean.py [--clean-all] [--demo]
"""

import os
import sys
import shutil
import glob
from datetime import datetime


def clean_old_files():
    """古いファイルのクリーンアップ"""
    print("🧹 古いファイルをクリーンアップ中...")

    # 7日以上古いCSVファイルを削除
    cutoff_date = datetime.now().timestamp() - (7 * 24 * 3600)  # 7日前

    # data/generated の古いファイル
    for file_path in glob.glob("./data/generated/*_analysis_data_*.csv"):
        if os.path.getmtime(file_path) < cutoff_date:
            os.remove(file_path)
            print(f"  削除: {file_path}")

    # charts の古いファイル
    for file_path in glob.glob("./charts/*_chart_*.png"):
        if os.path.getmtime(file_path) < cutoff_date:
            os.remove(file_path)
            print(f"  削除: {file_path}")

    print("✅ クリーンアップ完了")


def ensure_directories():
    """必要なディレクトリ構造を確保"""
    print("📁 ディレクトリ構造を確認中...")

    directories = [
        "./charts",
        "./data/generated",
        "./data/alerts",
        "./reports",
        "./scripts/archive",
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  作成: {directory}")
        else:
            print(f"  確認: {directory} ✓")

    print("✅ ディレクトリ構造確認完了")


def run_demo():
    """デモ実行"""
    print("\n" + "=" * 60)
    print("🚀 TIKER ポートフォリオ分析デモ開始")
    print("=" * 60)

    # 簡易レビューの実行
    print("\n📊 ポートフォリオ簡易レビューを実行中...")
    os.system("python3 scripts/portfolio_quick_review.py")

    print("\n🔔 アラートシステムをチェック中...")
    os.system("python3 scripts/portfolio_alerts.py")

    print("\n" + "=" * 60)
    print("✅ デモ完了！")
    print("=" * 60)
    print("\n📋 次のステップ:")
    print("  1. 週次レビュー: python3 scripts/portfolio_quick_review.py")
    print("  2. アラート確認: python3 scripts/portfolio_alerts.py")
    print("  3. 詳細分析: python3 unified_stock_analyzer.py --portfolio")
    print("  4. 個別分析: python3 unified_stock_analyzer.py --ticker TICKER")


def display_project_structure():
    """プロジェクト構造の表示"""
    print("\n📂 TIKER プロジェクト構造:")
    print(
        """
tiker/
├── 🎯 メインツール
│   ├── unified_stock_analyzer.py    # 統合分析エンジン
│   ├── stock_analyzer_lib.py        # 共通ライブラリ
│   └── config.yaml                  # 設定ファイル
│
├── 📊 レポート・データ
│   ├── charts/                      # チャート画像
│   ├── data/generated/              # 分析データ(CSV)
│   ├── data/alerts/                 # アラート履歴
│   └── reports/                     # 分析レポート(MD)
│
├── 🛠️ スクリプト
│   ├── portfolio_quick_review.py    # 簡易レビュー
│   ├── portfolio_alerts.py          # アラート監視
│   ├── setup_clean.py              # 初期化・整理
│   ├── archive/                    # 古いスクリプト
│   └── [銘柄別スクリプト].py
│
├── 📋 ドキュメント
│   ├── CLAUDE.md                   # プロジェクト説明
│   ├── tiker.md                    # 分析フレームワーク
│   └── README.md                   # 使い方
│
└── ⚙️ 設定
    ├── requirements.txt             # 依存関係
    ├── setup.py                    # インストール設定
    └── test_stock_analyzer.py      # テストスイート
"""
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="TIKER プロジェクト初期化・クリーンアップ"
    )
    parser.add_argument(
        "--clean-all", action="store_true", help="古いファイルを全てクリーンアップ"
    )
    parser.add_argument("--demo", action="store_true", help="デモ実行")
    parser.add_argument(
        "--structure", action="store_true", help="プロジェクト構造を表示"
    )

    args = parser.parse_args()

    print("🎯 TIKER プロジェクト管理ツール")
    print(f"📅 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ディレクトリ構造確保
    ensure_directories()

    if args.clean_all:
        clean_old_files()

    if args.structure:
        display_project_structure()

    if args.demo:
        run_demo()

    if not any([args.clean_all, args.demo, args.structure]):
        print("\n💡 使用方法:")
        print("  python3 scripts/setup_clean.py --demo        # デモ実行")
        print("  python3 scripts/setup_clean.py --clean-all   # ファイル整理")
        print("  python3 scripts/setup_clean.py --structure   # 構造確認")


if __name__ == "__main__":
    main()
