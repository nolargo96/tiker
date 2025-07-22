# 株式投資分析プロジェクト

このプロジェクトは、米国上場企業の中長期投資エントリータイミングを分析するためのツール群です。

## プロジェクト構造

```
tiker/
│  tiker.md                    # 主要仕様書：分析フレームワークとレポート形式の定義
│  unified_stock_analyzer.py   # メインツール：株価データ取得・チャート作成
│  README.md                   # このファイル
│
├─charts/                      # チャート画像保存ディレクトリ
│      RDW_chart_2025-06-27.png
│      tsla_chart_2025-06-26.png
│
├─data/                        # データファイル保存ディレクトリ
│      tsla_data.csv
│
├─reports/                     # レポート・ドキュメント保存ディレクトリ
│      investment_portfolio_summary.md  # ポートフォリオ提案サマリー
│      tiker.docx                       # tiker.mdのWord版
│
└─scripts/                     # 分析スクリプト保存ディレクトリ
        asts_analysis.py       # ASTS個別分析
        fslr_final_report.py   # FSLR詳細レポート
        joby_chart_*.py        # JOBY関連チャート作成スクリプト
        lunr_final_report.py   # LUNR詳細レポート
        oii_final_report.py    # OII詳細レポート
        oklo_analysis.py       # OKLO個別分析
        rdw_final_report.py    # RDW詳細レポート
        rklb_analysis.py       # RKLB個別分析
        tsla_analysis.py       # TSLA個別分析
```

## 使い方

### 1. 統合分析ツールの実行
```bash
python unified_stock_analyzer.py --ticker AAPL --date 2025-01-31
```

#### キャッシュオプション
```bash
# キャッシュを使用（デフォルト）
python unified_stock_analyzer.py --ticker TSLA

# キャッシュを無効化して最新データを取得
python unified_stock_analyzer.py --ticker TSLA --no-cache
```

### 2. 個別銘柄分析
各スクリプトは`scripts/`ディレクトリ内にあります。
```bash
python scripts/tsla_analysis.py
```

### 3. 詳細レポートの生成
`final_report.py`系のスクリプトは、tiker.mdの仕様に基づいた詳細な投資分析レポートを生成します。
```bash
python scripts/fslr_final_report.py
```

## 主要ファイルの説明

- **tiker.md**: 4人の専門家（TECH、FUND、MACRO、RISK）による投資分析フレームワークを定義
- **unified_stock_analyzer.py**: yfinanceを使用した株価データ取得とチャート生成の統合ツール
- **investment_portfolio_summary.md**: 分析済み銘柄のサマリーと1000万円ポートフォリオ提案

## 必要なライブラリ
- yfinance
- pandas
- numpy
- matplotlib
- mplfinance

## キャッシュシステム

### 概要
開発時の待機時間を削減するため、株価データや計算結果をキャッシュする機能を実装しています。

### キャッシュの種類と有効期限
- **市場データ（market_data）**: 5分
- **テクニカル指標（technical）**: 5分
- **ファンダメンタルデータ（fundamental）**: 1日
- **ポートフォリオ設定（portfolio）**: 1週間
- **専門家テンプレート（expert_template）**: 30日
- **チャート画像（chart）**: 1時間

### キャッシュの管理
```python
from cache_manager import CacheManager

# キャッシュマネージャーの初期化
cache_manager = CacheManager()

# キャッシュ統計の確認
stats = cache_manager.get_cache_stats()
print(f"キャッシュアイテム数: {stats['total_items']}")
print(f"キャッシュサイズ: {stats['total_size_mb']:.2f} MB")

# 期限切れキャッシュのクリア
deleted = cache_manager.clear_expired()
print(f"{deleted}個の期限切れアイテムを削除しました")

# 全キャッシュのクリア
cache_manager.clear_all()
```

### キャッシュの保存場所
キャッシュファイルは`./cache/`ディレクトリに保存されます。

## 注意事項
本プロジェクトは教育目的のシミュレーションであり、投資助言ではありません。
実際の投資判断は、ご自身の責任において行うようにしてください。 This is a test for learning Git.
