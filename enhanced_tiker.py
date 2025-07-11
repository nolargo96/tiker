#!/usr/bin/env python3
"""
Enhanced Tiker - 包括的株式投資分析システム
GOOG形式の分析手法を統合したメイン実行ファイル
"""

import argparse
from datetime import datetime
import os
import sys
from investment_report_generator import InvestmentReportGenerator


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="Enhanced Tiker - 包括的株式投資分析システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python enhanced_tiker.py --ticker TSLA
  python enhanced_tiker.py --ticker AAPL --date 2025-07-08
  python enhanced_tiker.py --ticker GOOGL --output html
  
対応分析項目:
  - 4専門家分析（TECH, FUND, MACRO, RISK）
  - ESG分析
  - 投資テーマ分析（AI、クラウド、クリーンエネルギー等）
  - カタリスト分析（ニュースセンチメント）
  - 経営陣評価
  - 目標株価算出（DCF法、マルチプル法）
  - シナリオ分析（強気・弱気・基本）
        """,
    )

    parser.add_argument(
        "--ticker",
        "-t",
        required=True,
        help="分析対象の米国株ティッカーシンボル (例: TSLA, AAPL, GOOGL)",
    )

    parser.add_argument(
        "--date", "-d", default=None, help="分析基準日 (YYYY-MM-DD形式, 省略時は今日)"
    )

    parser.add_argument(
        "--output",
        "-o",
        choices=["markdown", "html", "both"],
        default="markdown",
        help="出力形式 (デフォルト: markdown)",
    )

    parser.add_argument(
        "--save-analysis",
        action="store_true",
        help="分析データをJSONファイルとして保存",
    )

    parser.add_argument(
        "--portfolio",
        nargs="+",
        help="複数銘柄のポートフォリオ分析 (例: --portfolio TSLA AAPL GOOGL)",
    )

    parser.add_argument(
        "--benchmark", default="SPY", help="ベンチマーク指数 (デフォルト: SPY)"
    )

    args = parser.parse_args()

    # 分析日の設定
    analysis_date = args.date if args.date else datetime.now().strftime("%Y-%m-%d")

    try:
        if args.portfolio:
            # ポートフォリオ分析
            analyze_portfolio(
                args.portfolio, analysis_date, args.output, args.save_analysis
            )
        else:
            # 単一銘柄分析
            analyze_single_stock(
                args.ticker, analysis_date, args.output, args.save_analysis
            )

    except KeyboardInterrupt:
        print("\n分析を中断しました。")
        sys.exit(1)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


def analyze_single_stock(
    ticker: str, analysis_date: str, output_format: str, save_analysis: bool
):
    """単一銘柄の分析"""
    print(f"=== Enhanced Tiker 包括的分析開始 ===")
    print(f"銘柄: {ticker}")
    print(f"分析日: {analysis_date}")
    print(f"出力形式: {output_format}")
    print()

    # レポートジェネレーターの初期化
    generator = InvestmentReportGenerator()

    # 分析実行
    print("📊 包括的分析を実行中...")
    analysis = generator.analyzer.analyze_stock(ticker, analysis_date)

    # 結果の表示
    print(f"✅ 分析完了")
    print(f"📈 総合スコア: {analysis.overall_score:.2f}/5.0")
    print(f"🎯 投資推奨: {analysis.recommendation.value}")
    print(f"💰 現在株価: ${analysis.valuation_metrics.current_price:.2f}")
    print(f"🎪 目標株価: ${analysis.valuation_metrics.target_price_basic:.2f}")
    print()

    # レポート生成
    if output_format in ["markdown", "both"]:
        print("📝 Markdownレポートを生成中...")
        report = generator.generate_full_report(ticker, analysis_date)

        # ファイル保存
        os.makedirs("./reports", exist_ok=True)
        filename = f"./reports/{ticker}_enhanced_report_{analysis_date}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📄 Markdownレポート保存: {filename}")

    if output_format in ["html", "both"]:
        print("🌐 HTMLレポートを生成中...")
        # HTML生成機能は今後実装
        print("⚠️  HTML出力機能は開発中です")

    # 分析データの保存
    if save_analysis:
        print("💾 分析データを保存中...")
        import json
        from dataclasses import asdict

        analysis_data = asdict(analysis)
        json_filename = f"./reports/{ticker}_analysis_data_{analysis_date}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
        print(f"📊 分析データ保存: {json_filename}")

    print(f"\n🎉 {ticker}の包括的分析が完了しました！")


def analyze_portfolio(
    tickers: list, analysis_date: str, output_format: str, save_analysis: bool
):
    """ポートフォリオ分析"""
    print(f"=== Enhanced Tiker ポートフォリオ分析開始 ===")
    print(f"銘柄数: {len(tickers)}")
    print(f"銘柄: {', '.join(tickers)}")
    print(f"分析日: {analysis_date}")
    print()

    generator = InvestmentReportGenerator()
    portfolio_results = []

    # 各銘柄の分析
    for i, ticker in enumerate(tickers, 1):
        print(f"📊 [{i}/{len(tickers)}] {ticker} を分析中...")
        try:
            analysis = generator.analyzer.analyze_stock(ticker, analysis_date)
            portfolio_results.append(analysis)
            print(
                f"✅ {ticker}: スコア {analysis.overall_score:.2f}, 推奨 {analysis.recommendation.value}"
            )
        except Exception as e:
            print(f"❌ {ticker}: エラー - {e}")

    # ポートフォリオサマリー
    print(f"\n📈 ポートフォリオサマリー")
    print("=" * 50)

    avg_score = sum(r.overall_score for r in portfolio_results) / len(portfolio_results)
    best_stock = max(portfolio_results, key=lambda x: x.overall_score)
    worst_stock = min(portfolio_results, key=lambda x: x.overall_score)

    print(f"平均スコア: {avg_score:.2f}/5.0")
    print(f"最高評価: {best_stock.ticker} ({best_stock.overall_score:.2f})")
    print(f"最低評価: {worst_stock.ticker} ({worst_stock.overall_score:.2f})")

    # 推奨別の集計
    recommendations = {}
    for result in portfolio_results:
        rec = result.recommendation.value
        recommendations[rec] = recommendations.get(rec, 0) + 1

    print(f"\n投資推奨の分布:")
    for rec, count in recommendations.items():
        print(f"  {rec}: {count}銘柄")

    # ポートフォリオレポート生成
    if output_format in ["markdown", "both"]:
        portfolio_report = generate_portfolio_report(portfolio_results, analysis_date)
        os.makedirs("./reports", exist_ok=True)
        filename = f"./reports/portfolio_report_{analysis_date}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(portfolio_report)
        print(f"\n📄 ポートフォリオレポート保存: {filename}")

    print(f"\n🎉 ポートフォリオ分析が完了しました！")


def generate_portfolio_report(results: list, analysis_date: str) -> str:
    """ポートフォリオレポートの生成"""

    avg_score = sum(r.overall_score for r in results) / len(results)

    report = f"""# ポートフォリオ分析レポート

**分析日**: {analysis_date}
**銘柄数**: {len(results)}
**平均スコア**: {avg_score:.2f}/5.0

## 銘柄別サマリー

| ティッカー | 企業名 | 総合スコア | 投資推奨 | 現在株価 | 目標株価 |
|:---|:---|:---:|:---|---:|---:|
"""

    for result in sorted(results, key=lambda x: x.overall_score, reverse=True):
        report += f"| {result.ticker} | {result.company_name} | {result.overall_score:.2f} | {result.recommendation.value} | ${result.valuation_metrics.current_price:.2f} | ${result.valuation_metrics.target_price_basic:.2f} |\n"

    # セクター別分析
    report += f"\n## 分析サマリー\n\n"

    # 推奨別分析
    buy_stocks = [r for r in results if r.recommendation.value in ["買い", "強い買い"]]
    hold_stocks = [r for r in results if r.recommendation.value == "ホールド"]
    sell_stocks = [r for r in results if r.recommendation.value in ["売り", "強い売り"]]

    report += f"### 投資推奨別\n"
    report += f"- **買い推奨**: {len(buy_stocks)}銘柄\n"
    report += f"- **ホールド**: {len(hold_stocks)}銘柄\n"
    report += f"- **売り推奨**: {len(sell_stocks)}銘柄\n\n"

    if buy_stocks:
        report += f"**買い推奨銘柄**: {', '.join([r.ticker for r in buy_stocks])}\n\n"

    report += f"---\n*本レポートは教育目的のみに提供され、投資助言ではありません。*\n"

    return report


if __name__ == "__main__":
    main()
