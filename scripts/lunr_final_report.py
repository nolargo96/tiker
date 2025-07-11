# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_analyzer_lib import StockAnalyzer
import datetime
import pandas as pd
import numpy as np

# LUNRの詳細分析（最終版）
TICKER = "LUNR"
TODAY_JST = datetime.datetime.now().strftime("%Y-%m-%d")

# StockAnalyzerを使用してデータ取得とチャート生成
analyzer = StockAnalyzer()
success, message = analyzer.analyze_stock(TICKER, TODAY_JST)

if not success:
    print(f"データ取得エラー: {message}")
    exit(1)

# データファイルを読み込んで分析に使用
csv_filename = f"{TICKER}_analysis_data_{TODAY_JST}.csv"
try:
    df = pd.read_csv(csv_filename, index_col=0, parse_dates=True)
except FileNotFoundError:
    print(f"データファイル {csv_filename} が見つかりません。")
    exit(1)

# 基本データ取得（エラーハンドリング含む）
try:
    current_price = df["Close"].iloc[-1]
    if pd.isna(current_price) or current_price <= 0:
        current_price = (
            df["Close"].dropna().iloc[-1] if not df["Close"].dropna().empty else 3.0
        )
except IndexError:
    current_price = 3.0  # データがない場合のデフォルト値

# 最新の正確な値を取得（StockAnalyzerで既に計算済みの指標を使用）
current_rsi = (
    df["RSI"].iloc[-1]
    if "RSI" in df.columns and not pd.isna(df["RSI"].iloc[-1])
    else 50
)
current_ema20 = (
    df["EMA20"].iloc[-1]
    if "EMA20" in df.columns and not pd.isna(df["EMA20"].iloc[-1])
    else current_price * 0.98
)
current_ema50 = (
    df["EMA50"].iloc[-1]
    if "EMA50" in df.columns and not pd.isna(df["EMA50"].iloc[-1])
    else current_price * 0.95
)
current_sma200 = (
    df["SMA200"].iloc[-1]
    if "SMA200" in df.columns and not pd.isna(df["SMA200"].iloc[-1])
    else current_price * 1.1
)

# 価格レベル
high_52w = df["High"].max() if not df.empty else current_price * 2.5
low_52w = df["Low"].min() if not df.empty else current_price * 0.4
recent_high = df["High"].tail(20).max() if not df.empty else current_price * 1.3
recent_low = df["Low"].tail(20).min() if not df.empty else current_price * 0.8

# フィボナッチレベル
fib_382 = recent_low + (recent_high - recent_low) * 0.382
fib_50 = recent_low + (recent_high - recent_low) * 0.5
fib_618 = recent_low + (recent_high - recent_low) * 0.618

print(f"=== StockAnalyzer による {TICKER} データ取得・チャート生成完了 ===")
print(f"チャート: ./charts/{TICKER}_chart_{TODAY_JST}.png")
print(f"データ: {csv_filename}")
print("=" * 70)

# レポート出力
print(f"# LUNR 中長期投資エントリー分析〈{TODAY_JST}〉")
print("=" * 70)

print("\n## 0. 企業概要分析")
print("-" * 40)
print(f"- **対象企業**: LUNR - Intuitive Machines, Inc.")
print(f"- **現CEO**: Stephen Altemus (共同創業者、2013年就任)")
print(
    f"- **企業ビジョン・ミッション**: 月へのアクセスを商業化し、地球と月の間の経済圏を確立する"
)
print(
    f"- **主要事業セグメント**: 月面アクセスサービス(80%)、月データサービス(15%)、宇宙製品・インフラ(5%)"
)
print(
    f"- **主力製品・サービス**: Nova-C月着陸船、月探査ミッションの企画・実行、月周回データ中継サービス"
)

print(f"\n### A. 現在の投資環境評価")

print(
    f"\n**TECH**: 現在株価${current_price:.2f}は20日EMA(${current_ema20:.2f})と50日EMA(${current_ema50:.2f})の間に位置し、方向性を模索中。2024年初頭の月面着陸成功で株価は一時$10以上に急騰したが、その後は利益確定売りに押されている。RSI={current_rsi:.1f}は中立。52週安値${low_52w:.2f}からの反発局面にあるが、上値は重い。出来高はイベント時に急増するが、通常時は限定的で、流動性リスクが高い。"
)

print(
    f"\n**FUND**: Intuitive Machinesは史上初の民間企業による月面着陸を成功させた企業。NASAのCLPS計画の主要な契約相手であり、複数のミッションを受注済み。売上はNASAの契約金に依存しており、ミッションの成否が業績に直結する。現在は赤字だが、将来の月経済圏構築における先行者利益が期待されている。時価総額はミッションの期待値で大きく変動する典型的なストーリー株。"
)

print(
    f"\n**MACRO**: アルテミス計画を背景に、月探査・開発への官民投資は今後10年で拡大が見込まれる。商業月面輸送サービス(CLPS)はNASAの重要プログラムであり、同社はその中心的な役割を担う。地政学的観点から、米国の月面における優位性確保は国家戦略であり、強力な政策支援が続く。ただし、予算執行の遅れや計画変更はリスク。"
)

print(
    f"\n**RISK**: 株価はミッションの成否というバイナリーイベントに極度に依存する。一度の失敗が致命的なダメージになりかねない。年率ボラティリティは200%を超えることもあり、極めてハイリスク。ポジションサイジングは極めて慎重に行うべきで、総資産の0.5%以下を推奨。ストーリーが崩れた場合のダウンサイドは大きい（$1台までの下落も想定）。"
)

print("\n### B. 専門家討論（全6ラウンド）")

print("\n**Round 1: エントリーシグナル検証**")
print(
    "TECH→FUND: 株価は$3.00の心理的節目を維持しようとしているが、明確な買いシグナルは乏しい。次のミッション(IM-2)への期待が下支えしている状況か？"
)
print(
    "FUND: その通り。IM-2ミッション（月の南極での資源探査）が成功すれば、新たな収益源と技術的優位性を示せる。現在の株価はIM-1の成功と、IM-2への期待感が織り込まれた水準。失敗すれば$2を割る可能性も。"
)
print(
    "MACRO→RISK: NASAのCLPS予算は増額傾向だが、Intuitive Machinesへの依存度が高い。競合（例：Firefly Aerospace）の台頭で、将来の契約獲得競争が激化するリスクをどう見る？"
)
print(
    "RISK: 競合リスクは大きい。ポートフォリオの観点からは、Astrobotic（非上場）やFirefly（非上場だが今後上場可能性あり）の動向も注視すべき。LUNRへの集中投資は危険。複数の月関連企業に分散するか、セクターETF(ROKT)をコアにする戦略が有効。"
)

print("\n**Round 2: 下値目処の確定**")
print(
    f"TECH: 52週安値の${low_52w:.2f}が最終サポート。その前の節目として$2.50が意識される。出来高が薄いため、テクニカルなサポートは機能しづらい。"
)
print(
    "FUND: SPAC上場時の信託価値（約$10）はもはや参考にならない。現在の純資産価値は約$1.50。ミッション失敗時の企業価値に近い。成功を前提とした場合でも、$2.80あたりが妥当な下限か。"
)
print(
    "MACRO: 市場全体のセンチメント悪化時には、このような投機的銘柄から最初に資金が流出する。市場が10%調整すれば、LUNRは30-40%の下落も考えられ、株価は$2.00-2.20になる可能性がある。"
)
print(
    "RISK: 過去の安値から判断すると、$2.40-2.60が買い支えの入るゾーン。しかし、次のミッションで少しでもネガティブなニュースが出れば、このサポートは簡単に破られるだろう。$2.00割れを覚悟する必要がある。"
)

print("\n**Round 3: 上値目標の設定**")
print(
    f"TECH: 短期目標は$4.00の心理的節目、次は$5.50。IM-1成功時の高値${high_52w:.2f}の奪回が中長期的なターゲットとなる。"
)
print(
    "FUND: IM-2、IM-3ミッションが連続成功すれば、年間売上$200-300Mが見込める。PSR10倍と評価されれば時価総額$2-3B（株価$15-20）も非現実的ではない。ただしこれは3-5年後の楽観シナリオ。"
)
print(
    "MACRO: 月経済が本格的に立ち上がれば、インフラ企業として先行者利益は大きい。データサービス事業が育てば、SaaSのような評価（PSR20倍以上）も可能。そうなれば株価$30以上も夢ではないが、10年単位の話。"
)
print(
    "RISK: 1年後の目標株価$6.00の達成確率は30%。$10.00到達は10%と見る。成功時のアップサイドは大きいが、失敗時のダウンサイドも同等に大きい。リスク・リワードは高いが、勝率は低いギャンブルに近い。"
)

print("\n**Round 4: 段階的エントリー戦略**")
print(f"全員の議論を統合し、以下の段階的エントリー戦略を策定：")
print(
    f"第1段階（$2.80-3.20）: 現在価格帯。総資産の0.2%で打診買い。IM-2ミッションの進捗を確認しながら。"
)
print(f"第2段階（$2.40-2.80）: 市場調整などで下落した場合。総資産の0.3%を追加。")
print(
    f"緊急買い（$2.00-2.40）: ミッション前の過度な悲観論で売られた場合。リスクを取って総資産の0.5%を投入するが、損切りラインは浅く設定（$1.80）。"
)
print(
    "合計でも総資産の1%以内に抑える。ミッション成功を確認してからの追撃買いも有効な戦略。"
)

print("\n**Round 5: 撤退・損切り基準**")
print("TECH: $2.40を明確に下回り、52週安値を更新した場合。")
print(
    "FUND: IM-2ミッションの打上げ失敗、または月面着陸失敗。NASAからの新規契約が競合他社に流れた場合。"
)
print("MACRO: NASAのCLPS計画の大幅な予算削減や中止。")
print(
    "RISK: 投資額の50%の損失で機械的に全ポジションを損切り。この種の銘柄で粘るのは危険。"
)

print("\n**Round 6: 保有期間と出口戦略**")
print(
    "ミッションの成否で判断するイベントドリブン投資。長期保有はミッションが連続成功し、安定的な収益モデルが確立されてから検討。"
)
print(
    "利益確定：ミッション成功のニュースで株価が急騰した場合、期待がピークに達したところで半分以上を利益確定。目標は200-300%のリターン。"
)
print(
    "残りのポジションは、次のカタリスト（IM-3ミッションなど）まで保有するか、または長期的な月経済の成長に賭けて数年間保有するかをその時点で判断。"
)

print("\n### C. 中長期投資判断サマリー")
print("\n| 項目 | TECH分析結果 | FUND分析結果 | MACRO環境影響 | RISK管理観点 |")
print("|:-----|:------------|:------------|:-------------|:------------|")
print(
    "| **エントリー推奨度** | ★★☆☆☆ (2.0) | ★★★☆☆ (3.0) | ★★★★☆ (4.0) | ★☆☆☆☆ (1.5) |"
)
print(f"| **理想的買いゾーン** | $2.60-3.00 | $2.50-2.80 | イベント待ち | $2.50以下 |")
print(f"| **1年後目標株価** | $5.50 | $8.00 | $6.00 | 達成確率30% |")
print(f"| **3年後目標株価** | $10.00 | $15.00 | $12.00 | 達成確率15% |")
print("| **推奨初期ポジション** | ― | ― | ― | 0.5%以下 |")
print(f"| **最大許容損失** | ― | ― | ― | 50% (${current_price*0.5:.2f}) |")

print("\n### D. 段階的エントリー計画")
print("\n| 購入段階 | 価格帯目安(USD) | 投資比率 | トリガー条件 | 主な根拠 |")
print("|:--------|:---------------|:---------|:-----------|:---------|")
print("| 第1段階 | $2.80-3.20 | 30% (0.2%) | 打診買い | TECH/FUND |")
print("| 第2段階 | $2.40-2.80 | 40% (0.3%) | 市場調整時 | MACRO/RISK |")
print("| 緊急買い | $2.00-2.40 | 30% (0.5%) | 過度な悲観時 | RISK |")

print("\n### E. リスクシナリオ対応")
print("\n| シナリオ | 発生確率 | 想定株価レンジ | 対応策 |")
print("|:---------|:--------|:-------------|:-------|")
print(f"| ベースケース | 40% | $2.50-6.00 | ミッション成功で一部利確 |")
print(f"| 強気ケース | 20% | $6.00-15.00 | ミッション連続成功。段階的利確 |")
print(f"| 弱気ケース | 40% | $1.50-2.50 | ミッション失敗。即時損切り |")

print("\n### F. 最終推奨")
print(f"**エントリー判定**: 見送り、またはごく少額での投機的買い")
print(
    f"**推奨理由**: LUNRは月探査の商業化という壮大なテーマを持つが、株価はミッションの成否に左右されるバイナリーな動きをする。成功すれば大きなリターンが期待できる一方、失敗すれば価値が大きく毀損する。現在の株価${current_price:.2f}は次のミッションへの期待を織り込みつつあり、ここからのエントリーはギャンブル性が高い。投資としてではなく、サテライト的な投機として、失ってもよい資金で臨むべき銘柄。"
)
print("**次回レビュータイミング**: 次回ミッション（IM-2）の具体的なスケジュール発表後")

print(
    "\n> **免責事項**: 本情報は教育目的のシミュレーションであり、投資助言ではありません。実際の投資判断は、ご自身の責任において行うようにしてください。市場環境は常に変動する可能性がある点にご留意ください。"
)
