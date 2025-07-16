# yfinance財務データ調査レポート

**調査実行日**: 2025-07-16  
**調査対象**: yfinance v0.2.65  
**テスト銘柄**: AAPL, TSLA, FSLR, RKLB, ASTS

## 調査結果サマリー

yfinanceライブラリは**包括的な財務データ**を提供しており、tikerプロジェクトの分析フレームワークに大幅な機能拡張が可能です。

### ✅ 取得可能なデータ（確認済み）

| データカテゴリ | 詳細 | データ量例（AAPL） |
|---------------|------|------------------|
| **基本財務情報** | 180項目の包括的企業データ | MarketCap, P/E, ROE等 |
| **年次決算データ** | 損益・貸借・CF 5年分 | 39+68+53項目 |
| **四半期決算データ** | 直近5-6四半期 | 33+65+46項目 |
| **役員情報** | CEO・幹部の詳細情報 | 10名分 |
| **株主情報** | 配当・分割・大株主データ | 87件配当履歴等 |
| **アナリスト情報** | 投資推奨データ | 3件 |

## 1. 年次決算データ（財務三表）

### 📊 損益計算書 (ticker.financials)
- **データ期間**: 過去5年分
- **項目数**: 39項目
- **主要項目**:
  - Total Revenue（売上高）
  - Gross Profit（売上総利益）
  - Operating Income（営業利益）
  - Net Income（純利益）
  - EBITDA
  - Research Development（研究開発費）

**実例（AAPL 2024年）**: 
- 売上高: $391.04B
- 純利益: $93.74B
- 利益率: 24.30%

### 🏢 貸借対照表 (ticker.balance_sheet)
- **データ期間**: 過去5年分
- **項目数**: 68項目
- **主要項目**:
  - Total Assets（総資産）
  - Total Debt（総負債）
  - Total Equity（純資産）
  - Cash and Cash Equivalents（現金・現金同等物）
  - Inventory（在庫）

### 💰 キャッシュフロー (ticker.cashflow)
- **データ期間**: 過去5年分
- **項目数**: 53項目
- **主要項目**:
  - Operating Cash Flow（営業CF）
  - Investing Cash Flow（投資CF）
  - Financing Cash Flow（財務CF）
  - Free Cash Flow（フリーCF）
  - Capital Expenditure（設備投資）

**実例（AAPL）**: フリーCF $97.3B

## 2. 四半期決算データ

### 📈 四半期データの利点
- **即座の業績把握**: 年次より早い業績トレンド分析
- **季節性分析**: 四半期ごとの業績パターン
- **成長率分析**: QoQ（前四半期比）、YoY（前年同期比）

**実例（AAPL 四半期売上）**:
- 2025-Q1: $95.36B
- 2024-Q4: $124.30B（ホリデー季節効果）
- 2024-Q3: $94.93B
- 2024-Q2: $85.78B

## 3. CEO・企業情報

### 👥 役員情報 (ticker.info['companyOfficers'])
- **CEO情報**: 名前、年齢、報酬
- **役員数**: 通常10名程度
- **報酬情報**: 年間総報酬額

**実例（AAPL）**:
- CEO: Timothy D. Cook（63歳、報酬$16.5M）
- COO: Jeffrey E. Williams（60歳、報酬$5.0M）

### 🏢 企業基本情報
- 本社所在地、従業員数
- 事業概要、セクター分類
- ウェブサイト、電話番号

## 4. 主要財務指標（即座に利用可能）

### 📊 バリュエーション指標
- **P/E Ratio** (Forward/Trailing)
- **P/B Ratio** (Price to Book)
- **Enterprise Value**
- **Market Cap**

### 📈 収益性指標
- **ROE** (Return on Equity)
- **ROA** (Return on Assets)
- **Profit Margin**
- **Operating Margin**
- **Gross Margin**

### 💪 成長性指標
- **Revenue Growth**
- **Earnings Growth**
- **Earnings Quarterly Growth**

### 🛡️ 財務健全性指標
- **Debt to Equity**
- **Current Ratio**
- **Quick Ratio**
- **Total Cash/Debt**

## 5. competitor_analysis.py統合の可能性

### 🔄 既存機能との統合方法

#### A. 財務比較機能の追加
```python
def compare_financial_fundamentals(tickers: List[str]) -> pd.DataFrame:
    \"\"\"複数銘柄の財務指標を比較\"\"\"
    comparison_data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        data = {
            'Ticker': ticker,
            'Market Cap': info.get('marketCap'),
            'P/E (Forward)': info.get('forwardPE'),
            'ROE': info.get('returnOnEquity'),
            'Profit Margin': info.get('profitMargins'),
            'Revenue Growth': info.get('revenueGrowth')
        }
        comparison_data.append(data)
    return pd.DataFrame(comparison_data)
```

#### B. FUND専門家スコアの強化
現在のFUND分析を以下の実データで強化可能：
- **実際のP/E, P/B比較**: 競合他社との相対評価
- **成長率トレンド**: 四半期・年次データ比較
- **財務健全性**: 負債比率・流動性指標

#### C. セクター分析の追加
```python
def analyze_sector_performance(ticker: str) -> Dict:
    \"\"\"セクター内相対パフォーマンス分析\"\"\"
    stock = yf.Ticker(ticker)
    info = stock.info
    sector = info.get('sector')
    # セクター内企業との財務指標比較
    return sector_analysis
```

## 6. 実装における注意点

### ⚠️ API制限・エラーハンドリング
1. **レート制限**: yfinanceは無料だが過度なリクエストは制限される
2. **データ品質**: 一部項目が取得できない場合がある
3. **非推奨メソッド**: `ticker.earnings`は廃止予定

### 📊 データ形式
- **日付インデックス**: pandas Timestampオブジェクト
- **通貨単位**: USD（ドル）
- **NULL値処理**: pd.isna()でのチェックが必要

### 🔧 推奨実装パターン
```python
def safe_get_financial_data(ticker: str, data_type: str):
    \"\"\"安全な財務データ取得\"\"\"
    try:
        stock = yf.Ticker(ticker)
        if data_type == 'financials':
            data = stock.financials
        elif data_type == 'balance_sheet':
            data = stock.balance_sheet
        elif data_type == 'cashflow':
            data = stock.cashflow
        
        if data.empty:
            return None, f"{ticker}: {data_type}データなし"
        
        return data, "取得成功"
    except Exception as e:
        return None, f"エラー: {str(e)}"
```

## 7. 具体的な活用提案

### 🎯 tikerプロジェクトへの統合案

#### Phase 1: FUND専門家の強化
- 競合他社との財務比較機能
- 業界平均との比較
- 成長トレンド分析の定量化

#### Phase 2: 新しい分析機能
- セクター相対評価
- 財務健全性スコア
- 経営陣評価（CEO tenure, 報酬等）

#### Phase 3: HTMLレポート機能拡張
- インタラクティブ財務チャート
- 四半期トレンドグラフ
- 競合比較テーブル

## 8. 競合分析機能との統合サンプル

### 実測データ（ポートフォリオ4銘柄比較）

| Ticker | Market Cap | P/E (Forward) | P/B Ratio | ROE | Profit Margin | Revenue Growth | Debt/Equity |
|--------|------------|---------------|-----------|-----|---------------|----------------|-------------|
| TSLA   | $1.00T     | 95.92         | 13.40     | 9%  | 6%            | -9%            | 17.41       |
| FSLR   | $18.4B     | 8.24          | 2.25      | 17% | 30%           | 6%             | 7.70        |
| RKLB   | $21.4B     | -193.91*      | 47.65     | -45%| -44%          | 32%            | 113.54      |
| ASTS   | $17.3B     | -72.00*       | 21.30     | -105%| 0%           | 44%            | 62.58       |

*負のP/Eは利益が赤字のため

### 分析インサイト
1. **FSLR**: 最も安定した収益性（利益率30%、ROE17%）
2. **TSLA**: 高いマーケットキャップだが成長鈍化
3. **RKLB/ASTS**: 高成長だが赤字フェーズ

## 結論

yfinanceライブラリは**tikerプロジェクトの分析精度を大幅に向上**できる包括的な財務データを提供します。特に：

1. ✅ **年次・四半期決算データ**: 3-5年の財務諸表完全取得可能
2. ✅ **CEO・役員情報**: 報酬・年齢等の詳細データあり  
3. ✅ **競合比較**: 既存のcompetitor_analysis.pyと完全統合可能
4. ✅ **即座に利用可能**: 20の主要財務指標がinfo経由で即取得

次のステップとして、これらのデータを活用したFUND専門家スコアの定量化と、competitor_analysis.pyの機能拡張を推奨します。