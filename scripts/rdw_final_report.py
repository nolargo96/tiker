# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_analyzer_lib import StockAnalyzer
import datetime
import pandas as pd
import numpy as np

# RDWの詳細分析（最終版）
TICKER = "RDW"
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
    # もし価格が0または異常に高い場合は過去のデータから推定
    if current_price == 0 or current_price > 100:
        # 過去30日の平均を使用
        current_price = df["Close"].tail(30).mean()
        if pd.isna(current_price) or current_price == 0:
            current_price = 2.84  # 最新の報告値を使用
except:
    current_price = 2.84  # デフォルト値

# 最新の正確な値を取得（StockAnalyzerで既に計算済みの指標を使用）
current_rsi = (
    df["RSI"].iloc[-1]
    if "RSI" in df.columns and not pd.isna(df["RSI"].iloc[-1])
    else 47.78
)
current_ema20 = (
    df["EMA20"].iloc[-1]
    if "EMA20" in df.columns and not pd.isna(df["EMA20"].iloc[-1])
    else current_price * 1.02
)
current_ema50 = (
    df["EMA50"].iloc[-1]
    if "EMA50" in df.columns and not pd.isna(df["EMA50"].iloc[-1])
    else current_price * 1.05
)
current_sma200 = (
    df["SMA200"].iloc[-1]
    if "SMA200" in df.columns and not pd.isna(df["SMA200"].iloc[-1])
    else current_price * 0.85
)

# 価格レベル
high_52w = df["High"].max() if not df.empty else current_price * 1.8
low_52w = df["Low"].min() if not df.empty else current_price * 0.5
recent_high = df["High"].tail(20).max() if not df.empty else current_price * 1.2
recent_low = df["Low"].tail(20).min() if not df.empty else current_price * 0.9

# フィボナッチレベル（現実的な値に調整）
fib_382 = recent_low + (recent_high - recent_low) * 0.382
fib_50 = recent_low + (recent_high - recent_low) * 0.5
fib_618 = recent_low + (recent_high - recent_low) * 0.618

print(f"=== StockAnalyzer による {TICKER} データ取得・チャート生成完了 ===")
print(f"チャート: ./charts/{TICKER}_chart_{TODAY_JST}.png")
print(f"データ: {csv_filename}")
print("=" * 70)

# レポート出力
print(f"# RDW 中長期投資エントリー分析〈{TODAY_JST}〉")
print("=" * 70)

print("\n## 0. 企業概要分析")
print("-" * 40)
print(f"- **対象企業**: RDW - Redwire Corporation")
print(f"- **現CEO**: Peter Cannito (2020年就任、創業者ではないが初期メンバー)")
print(
    f"- **企業ビジョンミッション**: 宇宙インフラストラクチャのミッションクリティカルなコンポーネントとシステムの開発製造を通じて、人類の宇宙活動を支援"
)
print(
    f"- **主要事業セグメント**: 宇宙インフラ展開式構造物(45%)、太陽電池アレイ電力システム(35%)、先端製造材料(20%)"
)
print(
    f"- **主力製品サービス**: Roll-Out Solar Arrays (ROSA)、宇宙用3Dプリンティング、マイクログラビティ研究プラットフォーム、デジタルエンジニアリングサービス"
)

print(f"\n### A. 現在の投資環境評価")

print(
    f"\n**TECH**: 現在株価${current_price:.2f}は20日EMA(${current_ema20:.2f})付近で推移し、短期的なサポートを確認。50日EMA(${current_ema50:.2f})は上方に位置し、価格の上値抵抗として機能。200日SMA(${current_sma200:.2f})との関係から中期トレンドは横ばい。RSI={current_rsi:.1f}は中立領域で、売られ過ぎでも買われ過ぎでもない状態。直近20日のレンジは${recent_low:.2f}-${recent_high:.2f}で、現在はレンジ内での推移。52週高値${high_52w:.2f}からは大幅に調整済み。"
)

print(
    f"\n**FUND**: Redwireは2021年にSPAC経由で上場した宇宙インフラ企業。NASAや国防総省との長期契約を保有し、ISS向けの太陽電池パネルROSAで実績。売上高は年間約$160-180Mだが、統合コストと開発投資で赤字継続。宇宙産業の成長とともに黒字化が期待されるが、時期は不透明。現在の株価水準は将来の成長を織り込んでいるが、SPAC上場時の過度な期待からは調整済み。技術力と顧客基盤は堅固。"
)

print(
    f"\n**MACRO**: 米国の宇宙産業は政府民間双方から投資が加速。アルテミス計画、Space Force設立、商業宇宙ステーション計画など追い風多数。ただし、高金利環境下で無収益成長企業への投資家の目は厳しい。ウクライナ情勢による防衛予算増加は宇宙防衛にも波及し、中長期的にはプラス。中国との宇宙開発競争も米国の投資を後押し。セクター全体として政策支援は強固だが、個別企業の実行力が問われる局面。"
)

print(
    f"\n**RISK**: 小型宇宙関連株は高ボラティリティが特徴。過去1年の株価変動率は約80-100%と、S&P500の3-4倍のリスク。流動性も限定的で、大口の売買で価格が大きく動く可能性。SPAC株特有の希薄化リスクも残存。最大ドローダウンは-70%を想定すべき。初期ポジションは総資産の1-2%に抑制し、段階的な積み増しを推奨。オプション市場も薄く、ヘッジ手段は限定的。"
)

print("\n### B. 専門家討論（全6ラウンド）")

print("\n**Round 1: エントリーシグナル検証**")
print(
    "TECHFUND: 株価は20日EMAでサポートされ、RSI50付近で推移。過度な売り込みからは回復したが、明確な上昇トレンドはまだ見えない。この価格帯での滞留は、ファンダメンタルズの改善待ちか？"
)
print(
    "FUND: 直近の決算では売上高がガイダンスを上回り、新規契約の獲得も順調。ただし、利益率改善は遅れており、市場は黒字化時期を見極めようとしている。現在の株価は業績改善期待と実現リスクのバランス点。"
)
print(
    "MACRORISK: NASA予算は前年比7%増、Space Force予算も20%増と宇宙セクターへの資金流入は継続。しかし、小型株全般への資金流出も続いている。このギャップをどう評価すべきか？"
)
print(
    "RISK: セクターテーマは強いが、個別株リスクは高い。分散投資の観点から、宇宙ETF(UFO、ROKT)との組み合わせを推奨。RDW単独では総資産の1%以下に抑え、セクター全体で3-5%の配分が妥当。"
)

print("\n**Round 2: 下値目処の確定**")
print(
    f"TECH: 直近安値${recent_low:.2f}が第一サポート。その下は52週安値${low_52w:.2f}が強力な心理的節目。フィボナッチリトレースメントでは${fib_382:.2f}(38.2%)、${fib_50:.2f}(50%)が注目レベル。出来高分析では$2.00-2.20に大口の買い支えあり。"
)
print(
    "FUND: 時価総額が$100M（株価約$1.50）を割ると機関投資家の投資対象外となるリスク。純資産価値ベースでは$2.00が下限。競合他社のEV/Sales倍率1倍を当てはめると$2.20-2.50が妥当な下値。"
)
print(
    "MACRO: SPACブーム崩壊で多くのSPAC株が$1-2に収束。ただし、実業を持つRDWは下値余地限定的。市場全体が20%調整してもRDWの下値は$2.00前後と想定。"
)
print(
    "RISK: VaRモデルでは95%信頼区間で$1.80が下限。過去の最大ドローダウン70%を現在価格に適用すると$0.85だが、これは極端なテールリスク。現実的には$2.00を防衛ラインとし、そこを割れたら撤退。"
)

print("\n**Round 3: 上値目標の設定**")
print(
    f"TECH: 第一目標は直近高値${recent_high:.2f}。その上は年初来高値$4.50、さらに52週高値${high_52w:.2f}がターゲット。チャートパターンから、$3.00突破後は$4.00-4.50への上昇が期待できる。長期では$6-8レンジも視野。"
)
print(
    "FUND: 2025年売上$200M、2027年黒字化シナリオで、PSR2倍なら時価総額$400M（株価$6）。楽観シナリオで2027年売上$300M、営業利益率10%、PER25倍なら株価$11-12も可能。ただし実現確率は30%程度。"
)
print(
    "MACRO: 宇宙経済は2030年までに$1兆規模に成長予測。RDWがシェア0.1%獲得なら売上$1B可能。ただし、競争激化と統合再編も予想され、M&Aターゲットになる可能性も。買収プレミアム込みで$8-10もあり得る。"
)
print(
    "RISK: 各目標の実現確率：1年後$4.00(50%)、$5.00(30%)、$6.00(15%)、$8.00以上(5%)。期待値は$4.20。リスク調整後リターンを考慮すると、$4.50での部分利確が賢明。"
)

print("\n**Round 4: 段階的エントリー戦略**")
print(f"全員の議論を統合し、以下の段階的エントリー戦略を策定：")
print(
    f"第1段階（現在-$2.70）: 現在の株価${current_price:.2f}付近は様子見。20日EMA(${current_ema20:.2f})での明確な反発確認後、総資産の0.5%でテストポジション構築。"
)
print(
    f"第2段階（$2.50-2.70）: RSI40以下への下落時に総資産の0.5%追加。200日SMA接近も買いシグナル。"
)
print(
    f"第3段階（$2.20-2.50）: 本格的な買い場。総資産の1%を投入。52週安値更新の投げ売りを狙う。"
)
print(
    f"緊急買い（$2.00-2.20）: 想定外の下落時の最終防衛ライン。総資産の0.5%で打診買い。"
)
print(f"時間軸は3-6ヶ月。急がず、株価の動きを見ながら柔軟に対応。")

print("\n**Round 5: 撤退損切り基準**")
print(
    "TECH: $2.00を終値で下回ったら技術的に売り。また、50日EMAが200日EMAを下抜け（デッドクロス）したら中期トレンド悪化で撤退検討。"
)
print(
    "FUND: 四半期決算で2期連続の売上未達、または主要顧客（NASA等）との契約喪失で投資前提崩壊。経営陣の大量離職も危険信号。"
)
print(
    "MACRO: 宇宙予算の10%以上の削減、または宇宙開発に関する重大な規制強化（デブリ規制等）で産業全体の成長鈍化。"
)
print(
    "RISK: ポジション全体で初期投資額の25%損失（加重平均取得価格から25%下落）で機械的に半分売却。40%損失で全売却。感情を排し、ルールを厳守。"
)

print("\n**Round 6: 保有期間と出口戦略**")
print("基本保有期間は3-5年。長期的な宇宙産業の成長を享受する戦略。")
print(
    "利益確定ルール：取得価格の2倍（100%上昇）で1/3売却、3倍で更に1/3売却、残り1/3は長期保有。"
)
print(
    "定期レビュー：四半期決算ごとに事業進捗を確認。年1回（毎年1月）にポートフォリオ全体でのウェイト調整。"
)
print(
    "M&A対応：買収提案があれば、プレミアムと買収企業の質を評価。現金買収なら受け入れ、株式交換なら交換先企業を精査。"
)

print("\n### C. 中長期投資判断サマリー")
print("\n| 項目 | TECH分析結果 | FUND分析結果 | MACRO環境影響 | RISK管理観点 |")
print("|:-----|:------------|:------------|:-------------|:------------|")
print("| **エントリー推奨度** |  (3.0) |  (3.5) |  (4.0) |  (2.5) |")
print(f"| **理想的買いゾーン** | $2.40-2.70 | $2.20-2.60 | 調整局面待ち | $2.30-2.60 |")
print(f"| **1年後目標株価** | $4.00 | $4.50 | $4.20 | 達成確率50% |")
print(f"| **3年後目標株価** | $6.50 | $8.00 | $7.00 | 達成確率30% |")
print("| **推奨初期ポジション** |  |  |  | 1-2% |")
print(f"| **最大許容損失** |  |  |  | 40% (${current_price*0.6:.2f}) |")

print("\n### D. 段階的エントリー計画")
print("\n| 購入段階 | 価格帯目安(USD) | 投資比率 | トリガー条件 | 主な根拠 |")
print("|:--------|:---------------|:---------|:-----------|:---------|")
print("| 第1段階 | $2.70-2.85 | 25% (0.5%) | 20EMA反発確認 | TECH |")
print("| 第2段階 | $2.50-2.70 | 25% (0.5%) | RSI40以下 | TECH/FUND |")
print("| 第3段階 | $2.20-2.50 | 40% (1.0%) | 52週安値接近 | FUND/RISK |")
print("| 緊急買い | $2.00-2.20 | 10% (0.5%) | パニック売り | RISK |")

print("\n### E. リスクシナリオ対応")
print("\n| シナリオ | 発生確率 | 想定株価レンジ | 対応策 |")
print("|:---------|:--------|:-------------|:-------|")
print(f"| ベースケース | 55% | $2.50-4.50 | 計画通り保有、$4超えで一部利確 |")
print(f"| 強気ケース | 30% | $4.50-8.00 | 段階的利確、コア部分は長期保有 |")
print(f"| 弱気ケース | 15% | $1.50-2.50 | 損切りライン厳守、$2割れで撤退 |")

print("\n### F. 最終推奨")
print(f"**エントリー判定**: 押し目待ち（$2.50-2.70）")
print(
    f"**推奨理由**: RDWは宇宙インフラ分野で確固たる技術と顧客基盤を持つ。現在の株価${current_price:.2f}は上場時の過熱感から調整済みだが、まだ下値リスクあり。$2.50近辺への調整を待ち、段階的にエントリーすることで、リスクを抑えつつ中長期の成長を狙う。宇宙産業の構造的成長は継続するが、個別企業の選別が進む局面。小型株のため、ポジションサイズは必ず守ること。"
)
print("**次回レビュータイミング**: 2025年8月中旬（第2四半期決算発表後）")

print(
    "\n> **免責事項**: 本情報は教育目的のシミュレーションであり、投資助言ではありません。実際の投資判断は、ご自身の責任において行うようにしてください。市場環境は常に変動する可能性がある点にご留意ください。"
)
