# Tiker - 次世代AI駆動投資分析プラットフォーム

## 概要

Tikerは、米国上場企業の中長期投資エントリータイミング分析に特化した、AI駆動の投資分析プラットフォームです。4専門家（TECH、FUND、MACRO、RISK）による包括的な投資判断フレームワークを実装しています。

## 新しいプロジェクト構造

```
tiker/
├── src/                        # ソースコード
│   ├── analysis/              # 分析エンジン
│   │   ├── unified_analyzer.py
│   │   ├── stock_analyzer_lib.py
│   │   └── expert_discussion_generator.py
│   ├── data/                  # データ管理
│   │   ├── cache_manager.py
│   │   └── signal_history_tracker.py
│   ├── visualization/         # 可視化
│   │   └── html_report_generator.py
│   ├── portfolio/             # ポートフォリオ管理
│   │   ├── portfolio_master_report_hybrid.py
│   │   ├── competitor_analysis.py
│   │   └── financial_comparison_extension.py
│   └── web/                   # Webインターフェース
│       ├── dashboard_consolidated.py
│       └── dashboard_export_manager.py
├── tests/                     # テストコード
├── scripts/                   # 個別銘柄スクリプト
├── config/                    # 設定ファイル
│   └── config.yaml
├── data/                      # データファイル
├── charts/                    # チャート出力
├── reports/                   # レポート出力
├── docs/                      # ドキュメント
├── requirements.txt           # 依存関係
├── setup.py                   # セットアップスクリプト
├── run_dashboard.py           # ダッシュボード実行
└── run_analysis.py            # 分析実行

```

## 主要機能

### 1. 統合ダッシュボード（Streamlit）
- リアルタイムポートフォリオパフォーマンス追跡
- 履歴シグナル追跡と精度メトリクス
- 高度なフィルタリングと比較機能
- AI投資インサイト生成
- データエクスポート機能（Excel/PDF）

### 2. 4専門家分析フレームワーク
- **TECH**: テクニカル分析（移動平均、RSI、MACD、フィボナッチ）
- **FUND**: ファンダメンタル分析（PER、PBR、DCF、EPS成長）
- **MACRO**: マクロ環境分析（Fed金利、CPI、セクタートレンド）
- **RISK**: リスク管理（VaR、ドローダウン分析、ポジションサイジング）

### 3. ポートフォリオ構成（9銘柄）
- **TSLA**: 20% - EV・自動運転
- **FSLR**: 20% - ソーラーパネル
- **RKLB**: 10% - 小型ロケット
- **ASTS**: 10% - 衛星通信
- **OKLO**: 10% - SMR原子炉
- **JOBY**: 10% - eVTOL
- **OII**: 10% - 海洋エンジニアリング
- **LUNR**: 5% - 月面探査
- **RDW**: 5% - 宇宙製造

## インストール

```bash
# 依存関係のインストール
pip install -r requirements.txt

# または個別にインストール
pip install streamlit yfinance pandas numpy matplotlib mplfinance seaborn PyYAML pytest
```

## 使用方法

### 1. 統合ダッシュボードの起動

```bash
# Streamlitダッシュボードを起動
streamlit run run_dashboard.py

# または直接実行
python -m streamlit run run_dashboard.py
```

### 2. 個別銘柄分析の実行

```bash
# 統一分析エンジンで個別銘柄を分析
python run_analysis.py --ticker TSLA --date 2025-01-31

# または個別スクリプトを実行
python scripts/tsla_analysis.py
```

### 3. HTMLレポート生成

ダッシュボードの「ハイブリッドレポート」タブから、包括的なHTMLレポートを生成できます。

## テスト

```bash
# 全テストを実行
python -m pytest tests/ -v

# カバレッジレポート付きで実行
python -m pytest tests/ -v --cov=src
```

## 設定

`config/config.yaml`で以下の設定が可能：
- データ期間と検証ルール
- テクニカル指標パラメータ
- チャートスタイルと寸法
- ファイル命名規則
- HTMLレポート生成設定

## 開発環境

- Python 3.8以上
- WSL2環境で動作確認済み
- 主要な依存関係：
  - streamlit >= 1.28.0
  - yfinance >= 0.2.28
  - pandas >= 2.0.0
  - numpy >= 1.24.0
  - matplotlib >= 3.7.0
  - mplfinance >= 0.12.10b0

## ライセンス

このプロジェクトは教育・研究目的のみです。実際の投資判断には使用しないでください。

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 連絡先

質問や提案がある場合は、プロジェクトのissueセクションに投稿してください。