#!/usr/bin/env python3
"""
ポートフォリオ簡易レビュースクリプト
任意のタイミングで簡単にポートフォリオの状況を確認できるツール
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unified_stock_analyzer import analyze_portfolio
from datetime import datetime
import argparse

def quick_review(custom_config=None, date_str=None):
    """
    ポートフォリオの簡易レビューを実行
    
    Args:
        custom_config (dict): カスタムポートフォリオ設定
        date_str (str): 分析日付
    """
    
    # デフォルト設定（OII追加版）
    default_portfolio = {
        "TSLA": 25,  # 30%から25%に削減
        "FSLR": 25,  # 30%から25%に削減
        "ASTS": 10,
        "OKLO": 10,
        "JOBY": 10,
        "OII": 10,   # 新規追加
        "LUNR": 5,
        "RDW": 5
    }
    
    config = custom_config or default_portfolio
    
    print("=" * 60)
    print("📊 ポートフォリオ簡易レビュー")
    print("=" * 60)
    
    # 設定表示
    print("\n🎯 分析対象ポートフォリオ:")
    total_allocation = sum(config.values())
    for ticker, weight in config.items():
        print(f"  {ticker}: {weight}% ({weight/total_allocation*100:.1f}%実配分)")
    
    if total_allocation != 100:
        print(f"\n⚠️  配分合計: {total_allocation}% (100%でない場合は要調整)")
    
    # 分析実行
    print(f"\n🔍 分析実行中... (基準日: {date_str or '今日'})")
    results = analyze_portfolio(config, date_str)
    
    if "error" in results:
        print(f"❌ エラー: {results['error']}")
        return
    
    # 結果表示
    print("\n" + "=" * 60)
    print("📈 分析結果サマリー")
    print("=" * 60)
    
    # 成功率
    summary = results["portfolio_summary"]
    print(f"\n✅ 分析成功: {summary['analysis_coverage']}")
    print(f"📊 総配分: {summary['total_allocation']}%")
    
    # 上位推奨銘柄
    print("\n🏆 総合スコア順位:")
    if results["expert_scores"]:
        sorted_scores = sorted(
            results["expert_scores"].items(), 
            key=lambda x: x[1]["OVERALL"], 
            reverse=True
        )
        
        for i, (ticker, scores) in enumerate(sorted_scores, 1):
            allocation = results["individual_analysis"][ticker]["allocation"]
            recommendation = results["recommendations"][ticker]
            print(f"  {i}. {ticker} ({allocation}%): {scores['OVERALL']:.1f}★ - {recommendation['action']}")
    
    # アクション別サマリー
    print("\n🎯 推奨アクション別:")
    action_summary = {}
    for ticker, rec in results["recommendations"].items():
        action = rec["action"]
        if action not in action_summary:
            action_summary[action] = []
        action_summary[action].append(ticker)
    
    action_names = {
        "BUY": "🟢 即時買い",
        "BUY_DIP": "🟡 押し目買い", 
        "CAUTIOUS": "🟠 慎重エントリー",
        "WAIT": "⚪ 様子見",
        "AVOID": "🔴 回避"
    }
    
    for action, tickers in action_summary.items():
        action_name = action_names.get(action, action)
        print(f"  {action_name}: {', '.join(tickers)}")
    
    # 高リスク銘柄の警告
    print("\n⚠️  高リスク銘柄:")
    high_risk_tickers = []
    for ticker, scores in results["expert_scores"].items():
        if scores["RISK"] < 2.5:
            allocation = results["individual_analysis"][ticker]["allocation"]
            high_risk_tickers.append(f"{ticker}({allocation}%)")
    
    if high_risk_tickers:
        print(f"  {', '.join(high_risk_tickers)} - 配分比率やリスク管理に注意")
    else:
        print("  なし - 良好なリスク水準")
    
    # 次回レビュー推奨
    print(f"\n📅 次回レビュー推奨:")
    print(f"  - 週次: python scripts/portfolio_quick_review.py")
    print(f"  - 詳細: python unified_stock_analyzer.py --portfolio")
    print(f"  - 個別: python unified_stock_analyzer.py --ticker TICKER")
    
    print("\n" + "=" * 60)
    print(f"📄 詳細レポート: ./reports/portfolio_review_{results['analysis_date']}.md")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='ポートフォリオ簡易レビュー')
    parser.add_argument('--date', type=str, help='分析基準日 (YYYY-MM-DD)')
    parser.add_argument('--conservative', action='store_true', help='保守的ポートフォリオを使用')
    parser.add_argument('--aggressive', action='store_true', help='積極的ポートフォリオを使用')
    parser.add_argument('--custom', type=str, help='カスタム設定 (例: TSLA:40,FSLR:30,ASTS:20,OKLO:10)')
    
    args = parser.parse_args()
    
    # ポートフォリオ設定の選択
    config = None
    
    if args.conservative:
        # 保守的設定（大型株重視、高リスク銘柄を削減）
        config = {
            "TSLA": 35,
            "FSLR": 30,
            "OII": 20,   # OII追加（安定した海洋エネルギー）
            "OKLO": 10,
            "JOBY": 5
        }
        print("🛡️  保守的ポートフォリオで分析します")
    
    elif args.aggressive:
        # 積極的設定（成長株重視）
        config = {
            "TSLA": 20,
            "FSLR": 15,
            "ASTS": 20,
            "OKLO": 15,
            "JOBY": 10,
            "OII": 10,   # OII追加
            "LUNR": 5,
            "RDW": 5
        }
        print("🚀 積極的ポートフォリオで分析します")
    
    elif args.custom:
        # カスタム設定の解析
        try:
            pairs = args.custom.split(',')
            config = {}
            for pair in pairs:
                ticker, weight = pair.split(':')
                config[ticker.strip().upper()] = float(weight.strip())
            print(f"🎛️  カスタムポートフォリオ: {config}")
        except Exception as e:
            print(f"❌ カスタム設定の解析エラー: {e}")
            print("例: --custom 'TSLA:40,FSLR:30,ASTS:20,OKLO:10'")
            return
    
    # レビュー実行
    quick_review(config, args.date)

if __name__ == "__main__":
    main()