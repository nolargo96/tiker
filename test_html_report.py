#!/usr/bin/env python3
"""
HTMLレポート生成機能のテストスクリプト
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from html_report_generator import HTMLReportGenerator
from stock_analyzer_lib import ConfigManager


def create_test_data():
    """テスト用の株価データを作成"""
    dates = pd.date_range(start="2024-01-01", end="2025-07-03", freq="D")
    n_days = len(dates)

    # 模擬的な株価データを生成
    np.random.seed(42)
    base_price = 100
    price_changes = np.random.normal(0, 0.02, n_days)
    prices = [base_price]

    for change in price_changes[1:]:
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 1))  # 最低価格を1ドルに設定

    # OHLCVデータを生成
    data = {
        "Open": [],
        "High": [],
        "Low": [],
        "Close": prices,
        "Volume": np.random.randint(1000000, 5000000, n_days),
    }

    for i, close in enumerate(prices):
        daily_range = abs(np.random.normal(0, 0.03)) * close
        high = close + daily_range * np.random.uniform(0, 1)
        low = close - daily_range * np.random.uniform(0, 1)
        open_price = low + (high - low) * np.random.uniform(0, 1)

        data["Open"].append(open_price)
        data["High"].append(high)
        data["Low"].append(low)

    df = pd.DataFrame(data, index=dates)

    # テクニカル指標を計算
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["SMA200"] = df["Close"].rolling(window=200).mean()

    # RSI計算
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    # ボリンジャーバンド
    df["BB_middle"] = df["Close"].rolling(window=20).mean()
    df["BB_std"] = df["Close"].rolling(window=20).std()
    df["BB_upper"] = df["BB_middle"] + (df["BB_std"] * 2)
    df["BB_lower"] = df["BB_middle"] - (df["BB_std"] * 2)

    # ATR
    df["TR"] = np.maximum(
        df["High"] - df["Low"],
        np.maximum(
            abs(df["High"] - df["Close"].shift(1)),
            abs(df["Low"] - df["Close"].shift(1)),
        ),
    )
    df["ATR"] = df["TR"].rolling(window=14).mean()

    return df


def create_test_chart(ticker: str, date_str: str) -> str:
    """テスト用のチャート画像を作成"""
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # チャートディレクトリを作成
    chart_dir = Path("./charts")
    chart_dir.mkdir(exist_ok=True)

    # 簡単なテストチャートを作成
    fig, ax = plt.subplots(figsize=(16, 9))

    # 模擬的なチャートデータ
    x = range(30)
    y = [100 + i * 0.5 + np.random.normal(0, 2) for i in x]

    ax.plot(x, y, "b-", linewidth=2, label="Stock Price")
    ax.fill_between(x, y, alpha=0.3)

    # 移動平均線
    ema20 = [np.mean(y[max(0, i - 20) : i + 1]) for i in x]
    ax.plot(x, ema20, "r--", linewidth=1, label="EMA20")

    ax.set_title(f"{ticker} Stock Chart - Test Data ({date_str})", fontsize=16)
    ax.set_xlabel("Days")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ファイル保存
    chart_path = chart_dir / f"{ticker}_chart_{date_str}.png"
    plt.savefig(chart_path, dpi=100, bbox_inches="tight")
    plt.close()

    return str(chart_path)


def test_html_report_generation():
    """HTMLレポート生成機能のテスト"""
    print("=== HTMLレポート生成機能テスト開始 ===")

    # テストデータの準備
    ticker = "TSLA"
    date_str = "2025-07-03"

    print(f"1. テストデータ生成中... ({ticker})")
    test_data = create_test_data()
    print(
        f"   - データ期間: {test_data.index[0].strftime('%Y-%m-%d')} - {test_data.index[-1].strftime('%Y-%m-%d')}"
    )
    print(f"   - データ数: {len(test_data)} 日分")

    print("2. テストチャート作成中...")
    chart_path = create_test_chart(ticker, date_str)
    print(f"   - チャート保存: {chart_path}")

    print("3. HTMLレポート生成中...")
    try:
        html_generator = HTMLReportGenerator()

        # サンプルMarkdownコンテンツ
        sample_markdown = """
# TSLA 専門家分析レポート

## 現在の投資環境評価

### TECH (テクニカルアナリスト)
- 20日EMAを上回って推移
- RSIは60付近で適正圏内
- 上昇トレンドが継続中

### FUND (ファンダメンタルアナリスト)
- Q4決算は予想を上回る結果
- 電気自動車市場の拡大が追い風
- 新工場建設による生産能力向上

### MACRO (マクロストラテジスト)
- 環境政策の後押しが継続
- 金利動向に要注意
- 中国市場の動向が重要

### RISK (リスク管理専門家)
- ボラティリティが高い銘柄
- 15%の最大損失を想定
- 段階的な投資を推奨

## 投資判断
**推奨アクション: 段階的買い増し**
- エントリー価格: $210-220
- 利益確定: $280-300
- 損切りライン: $180
        """

        success, result = html_generator.generate_stock_html_report(
            ticker=ticker,
            analysis_data=test_data,
            chart_path=chart_path,
            date_str=date_str,
            markdown_content=sample_markdown,
        )

        if success:
            print(f"   ✓ HTMLレポート生成成功: {result}")

            # ファイルサイズを確認
            file_size = os.path.getsize(result)
            print(f"   - ファイルサイズ: {file_size:,} バイト")

            # HTMLファイルの内容を確認
            with open(result, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"   - HTML文字数: {len(content):,} 文字")
                print(f"   - チャート埋め込み: {'data:image/png;base64' in content}")
                print(f"   - インタラクティブチャート: {'Chart.js' in content}")
                print(f"   - 専門家分析: {'専門家分析' in content}")

            return True, result
        else:
            print(f"   ✗ HTMLレポート生成失敗: {result}")
            return False, result

    except Exception as e:
        print(f"   ✗ エラー発生: {str(e)}")
        import traceback

        traceback.print_exc()
        return False, str(e)


def test_config_integration():
    """設定ファイルとの統合テスト"""
    print("\n=== 設定ファイル統合テスト ===")

    try:
        config = ConfigManager()

        # HTML関連設定の確認
        html_enabled = config.get("html_report.enabled", False)
        html_output_dir = config.get("html_report.output_directory", "./reports/html")
        html_pattern = config.get(
            "naming.html_report_pattern", "{ticker}_analysis_{date}.html"
        )

        print(f"HTML報告機能: {'有効' if html_enabled else '無効'}")
        print(f"出力ディレクトリ: {html_output_dir}")
        print(f"ファイル命名パターン: {html_pattern}")

        # ディレクトリ作成テスト
        html_dir = Path(html_output_dir)
        html_dir.mkdir(parents=True, exist_ok=True)
        print(f"出力ディレクトリ作成: ✓")

        return True

    except Exception as e:
        print(f"設定ファイル統合テストでエラー: {str(e)}")
        return False


def main():
    """メインテスト実行"""
    print("HTMLレポート生成機能テスト開始\n")

    # テスト1: 設定ファイル統合
    config_test = test_config_integration()

    # テスト2: HTMLレポート生成
    html_test, html_result = test_html_report_generation()

    # テスト結果サマリー
    print("\n=== テスト結果サマリー ===")
    print(f"設定ファイル統合: {'✓ 成功' if config_test else '✗ 失敗'}")
    print(f"HTMLレポート生成: {'✓ 成功' if html_test else '✗ 失敗'}")

    if html_test:
        print(f"\n生成されたHTMLレポート: {html_result}")
        print("ブラウザで開いて確認してください。")

    return config_test and html_test


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
