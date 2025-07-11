#!/usr/bin/env python3
"""
Tiker Full Portfolio - ポートフォリオ全銘柄の4専門家討論分析
一気に全銘柄の完全討論分析を実行
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import mplfinance as mpf
import argparse
import os
import yaml
import time
from typing import Dict, List, Tuple, Optional
from tiker_discussion import TikerDiscussion
import concurrent.futures
from threading import Lock


class TikerFullPortfolio:
    """ポートフォリオ全銘柄の包括的分析システム"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.discussion_analyzer = TikerDiscussion(config_path)
        self.portfolio_config = self.config.get("portfolio", {})
        self.lock = Lock()

    def _load_config(self, config_path: str) -> Dict:
        """設定ファイルの読み込み"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_portfolio()

    def _get_default_portfolio(self) -> Dict:
        """デフォルトポートフォリオ設定"""
        return {
            "portfolio": {
                "name": "次世代テクノロジー・ポートフォリオ",
                "holdings": {
                    "TSLA": {
                        "allocation": 20,
                        "description": "EV・自動運転技術のリーダー",
                    },
                    "FSLR": {"allocation": 20, "description": "太陽光発電・CdTe技術"},
                    "RKLB": {
                        "allocation": 10,
                        "description": "小型ロケット・宇宙インフラ",
                    },
                    "ASTS": {
                        "allocation": 10,
                        "description": "衛星通信・スマートフォン直接接続",
                    },
                    "OKLO": {
                        "allocation": 10,
                        "description": "小型モジュール原子炉（SMR）",
                    },
                    "JOBY": {
                        "allocation": 10,
                        "description": "eVTOL・都市航空モビリティ",
                    },
                    "OII": {"allocation": 10, "description": "海洋工学・ROVサービス"},
                    "LUNR": {"allocation": 5, "description": "月面着陸・宇宙探査"},
                    "RDW": {"allocation": 5, "description": "宇宙インフラ・軌道上製造"},
                },
            }
        }

    def get_portfolio_tickers(self) -> List[str]:
        """ポートフォリオ銘柄一覧取得"""
        holdings = self.portfolio_config.get("holdings", {})
        return list(holdings.keys())

    def analyze_single_stock_detailed(self, ticker: str) -> Tuple[str, str, bool]:
        """単一銘柄の詳細討論分析"""
        try:
            with self.lock:
                print(f"🎯 {ticker} 討論分析開始...")

            # 詳細討論分析の実行
            report = self.discussion_analyzer.generate_full_analysis_report(ticker)

            with self.lock:
                print(f"✅ {ticker} 討論分析完了")

            return ticker, report, True

        except Exception as e:
            with self.lock:
                print(f"❌ {ticker} 分析エラー: {e}")

            error_report = f"""
# {ticker} 分析エラーレポート

**エラー内容**: {str(e)}
**発生時刻**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

このティッカーのデータ取得または分析中にエラーが発生しました。
以下の要因が考えられます：
- ティッカーシンボルの変更または上場廃止
- データプロバイダーの一時的な問題
- ネットワーク接続の問題

次回分析時に再試行することを推奨します。
"""
            return ticker, error_report, False

    def analyze_all_stocks_parallel(
        self, max_workers: int = 3
    ) -> Dict[str, Tuple[str, bool]]:
        """全銘柄の並列分析実行"""
        tickers = self.get_portfolio_tickers()

        print(f"🚀 ポートフォリオ全銘柄討論分析開始")
        print(f"📊 対象銘柄: {', '.join(tickers)} ({len(tickers)}銘柄)")
        print(f"⚙️  並列実行数: {max_workers}")
        print("=" * 60)

        results = {}
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 並列実行タスクの投入
            future_to_ticker = {
                executor.submit(self.analyze_single_stock_detailed, ticker): ticker
                for ticker in tickers
            }

            # 結果の回収
            for future in concurrent.futures.as_completed(future_to_ticker):
                ticker, report, success = future.result()
                results[ticker] = (report, success)

        elapsed_time = time.time() - start_time
        print("=" * 60)
        print(f"🎉 全銘柄分析完了 - 実行時間: {elapsed_time:.1f}秒")

        return results

    def generate_portfolio_master_report(
        self, individual_results: Dict[str, Tuple[str, bool]]
    ) -> str:
        """ポートフォリオマスターレポート生成"""
        portfolio_name = self.portfolio_config.get("name", "ポートフォリオ")
        analysis_date = datetime.now().strftime("%Y-%m-%d")

        # 成功・失敗の集計
        successful_analyses = {k: v for k, v in individual_results.items() if v[1]}
        failed_analyses = {k: v for k, v in individual_results.items() if not v[1]}

        report = f"""
# {portfolio_name} - 完全討論分析レポート

**分析実行日**: {analysis_date}
**分析銘柄数**: {len(individual_results)}
**成功分析**: {len(successful_analyses)}銘柄
**失敗分析**: {len(failed_analyses)}銘柄

---

## 📋 ポートフォリオ概要

"""

        # ポートフォリオ構成表
        report += """
### 銘柄構成と配分

| ティッカー | 配分 | 企業名・事業内容 | 分析状況 |
|:---:|:---:|:---|:---:|
"""

        holdings = self.portfolio_config.get("holdings", {})
        for ticker in individual_results.keys():
            allocation = holdings.get(ticker, {}).get("allocation", 0)
            description = holdings.get(ticker, {}).get("description", "情報なし")
            status = "✅ 完了" if individual_results[ticker][1] else "❌ エラー"

            report += f"| {ticker} | {allocation}% | {description} | {status} |\n"

        # 分析サマリー
        if successful_analyses:
            report += f"""

---

## 🎯 分析成功銘柄の概要

以下の{len(successful_analyses)}銘柄について、4専門家による完全討論分析を実行しました：

"""
            for ticker in successful_analyses.keys():
                allocation = holdings.get(ticker, {}).get("allocation", 0)
                description = holdings.get(ticker, {}).get("description", "情報なし")
                report += f"- **{ticker}** ({allocation}%): {description}\n"

        if failed_analyses:
            report += f"""

---

## ⚠️ 分析失敗銘柄

以下の{len(failed_analyses)}銘柄で分析エラーが発生しました：

"""
            for ticker in failed_analyses.keys():
                report += f"- **{ticker}**: データ取得または分析処理でエラー\n"

        # 詳細レポートへのリンク
        report += f"""

---

## 📊 個別銘柄詳細分析

各銘柄の詳細な4専門家討論分析は、以下の個別レポートをご確認ください：

"""

        for ticker, (_, success) in individual_results.items():
            if success:
                report += f"- [{ticker} 詳細討論分析](./reports/{ticker}_discussion_analysis_{analysis_date}.md)\n"
            else:
                report += f"- {ticker}: 分析エラーのため詳細レポートなし\n"

        # 次回分析予定
        next_analysis_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        report += f"""

---

## 📅 次回分析予定

**推奨更新頻度**: 月次（重要なマーケットイベント後は随時）
**次回予定日**: {next_analysis_date}

### 定期レビューのタイミング
- 毎月第1営業日
- 四半期決算シーズン後
- FOMCなど重要な金融政策発表後
- 各銘柄の重要なニュース・イベント後

---

## 🔄 分析実行方法

このレポートの再生成は以下のコマンドで実行できます：

```bash
# 全銘柄一括分析
python tiker_full_portfolio.py --all

# 特定銘柄のみ再分析
python tiker_full_portfolio.py --ticker TSLA FSLR

# 並列実行数指定
python tiker_full_portfolio.py --all --workers 5
```

---

> **免責事項**: 本情報は教育目的のシミュレーションであり、投資助言ではありません。実際の投資判断は、ご自身の責任において行うようにしてください。

---
*レポート生成時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*生成システム: Tiker Full Portfolio Analysis*
"""

        return report

    def save_all_reports(
        self, individual_results: Dict[str, Tuple[str, bool]], master_report: str
    ) -> List[str]:
        """全レポートの保存"""
        os.makedirs("./reports", exist_ok=True)

        analysis_date = datetime.now().strftime("%Y-%m-%d")
        saved_files = []

        # 個別レポートの保存
        for ticker, (report, success) in individual_results.items():
            if success:
                filename = f"./reports/{ticker}_discussion_analysis_{analysis_date}.md"
            else:
                filename = f"./reports/{ticker}_error_report_{analysis_date}.md"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)

            saved_files.append(filename)

        # マスターレポートの保存
        master_filename = f"./reports/portfolio_master_analysis_{analysis_date}.md"
        with open(master_filename, "w", encoding="utf-8") as f:
            f.write(master_report)

        saved_files.append(master_filename)

        return saved_files

    def run_full_portfolio_analysis(
        self, max_workers: int = 3, specific_tickers: List[str] = None
    ) -> Tuple[Dict, str, List[str]]:
        """完全ポートフォリオ分析の実行"""

        # 分析対象銘柄の決定
        if specific_tickers:
            target_tickers = [
                t for t in specific_tickers if t in self.get_portfolio_tickers()
            ]
            if not target_tickers:
                raise ValueError("指定された銘柄がポートフォリオに含まれていません")
            print(f"🎯 指定銘柄のみ分析: {', '.join(target_tickers)}")
        else:
            target_tickers = self.get_portfolio_tickers()
            print(f"🌟 ポートフォリオ全銘柄分析")

        # 個別銘柄分析の実行
        individual_results = {}

        if len(target_tickers) == 1:
            # 単一銘柄の場合は並列化不要
            ticker = target_tickers[0]
            ticker, report, success = self.analyze_single_stock_detailed(ticker)
            individual_results[ticker] = (report, success)
        else:
            # 複数銘柄の場合は並列実行
            # 並列実行用に一時的にself.get_portfolio_tickers()をオーバーライド
            original_method = self.get_portfolio_tickers
            self.get_portfolio_tickers = lambda: target_tickers

            individual_results = self.analyze_all_stocks_parallel(max_workers)

            # メソッドを元に戻す
            self.get_portfolio_tickers = original_method

        # マスターレポート生成
        master_report = self.generate_portfolio_master_report(individual_results)

        # レポート保存
        saved_files = self.save_all_reports(individual_results, master_report)

        return individual_results, master_report, saved_files


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="Tiker Full Portfolio - ポートフォリオ全銘柄討論分析",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python tiker_full_portfolio.py --all                    # 全銘柄一括分析
  python tiker_full_portfolio.py --ticker TSLA FSLR       # 指定銘柄のみ
  python tiker_full_portfolio.py --all --workers 5        # 並列数指定
  python tiker_full_portfolio.py --ticker TSLA --no-save  # 保存せず表示のみ
        """,
    )

    parser.add_argument("--all", "-a", action="store_true", help="全銘柄の討論分析実行")
    parser.add_argument(
        "--ticker", "-t", nargs="+", help="特定銘柄のみ分析 (複数指定可)"
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=3, help="並列実行数 (デフォルト: 3)"
    )
    parser.add_argument("--no-save", action="store_true", help="ファイル保存をスキップ")
    parser.add_argument(
        "--config", "-c", default="config.yaml", help="設定ファイルパス"
    )

    args = parser.parse_args()

    if not args.all and not args.ticker:
        print("❌ --all または --ticker のいずれかを指定してください")
        return 1

    try:
        analyzer = TikerFullPortfolio(args.config)

        # 分析実行
        individual_results, master_report, saved_files = (
            analyzer.run_full_portfolio_analysis(
                max_workers=args.workers, specific_tickers=args.ticker
            )
        )

        # 結果表示
        success_count = sum(1 for _, success in individual_results.values() if success)
        total_count = len(individual_results)

        print(f"\n🎉 分析完了サマリー")
        print(f"成功: {success_count}/{total_count}銘柄")

        if not args.no_save:
            print(f"\n📄 保存されたファイル ({len(saved_files)}件):")
            for filename in saved_files:
                print(f"  - {filename}")

            print(
                f"\n📊 マスターレポート: ./reports/portfolio_master_analysis_{datetime.now().strftime('%Y-%m-%d')}.md"
            )
        else:
            print("\n" + "=" * 80)
            print(master_report)
            print("=" * 80)

    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
