# Tiker Stock Analyzer - 開発環境セットアップガイド

## 🚀 クイックスタート

### 前提条件
- Python 3.8+ がインストールされていること
- Git がインストールされていること
- インターネット接続（株価データ取得用）

### 1. プロジェクトクローン
```bash
git clone <your-repository-url>
cd tiker
```

### 2. 仮想環境作成・有効化
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存関係インストール
```bash
pip install -r requirements.txt
```

### 4. 動作確認
```bash
# テスト実行
python -m pytest test_stock_analyzer.py -v

# 個別銘柄分析テスト
python unified_stock_analyzer.py --ticker TSLA --date 2025-01-03

# ポートフォリオ分析テスト
python unified_stock_analyzer.py --portfolio
```

## 📁 プロジェクト構造

```
tiker/
├── unified_stock_analyzer.py      # メイン分析エンジン
├── stock_analyzer_lib.py          # 共通ライブラリ
├── html_report_generator.py       # HTMLレポート生成
├── competitor_analysis.py         # 競合分析機能（財務比較統合済み）
├── financial_comparison_extension.py # 財務比較拡張モジュール
├── test_stock_analyzer.py         # テストスイート
├── config.yaml                    # 設定ファイル
├── requirements.txt               # Python依存関係
├── CLAUDE.md                      # プロジェクトガイド
├── .gitignore                     # Git除外設定
│
├── scripts/                       # 個別分析スクリプト
│   ├── *_analysis.py              # 銘柄別分析
│   └── portfolio_*.py             # ポートフォリオ管理
│
├── reports/                       # 分析結果
│   ├── html/                      # HTMLレポート
│   └── *.md                       # Markdownレポート
│
├── charts/                        # チャート画像
└── data/                          # データ保存
    └── generated/                 # 生成されたCSVファイル
```

## ⚙️ 設定ファイル（config.yaml）

### 基本設定
```yaml
# データ取得設定
data:
  default_period_days: 365
  min_trading_days: 250
  buffer_multiplier: 1.5

# テクニカル指標設定
technical:
  ema_short: 20
  ema_long: 50
  sma_long: 200
  rsi_period: 14

# チャート設定
chart:
  figure_size: [16, 9]
  dpi: 100
  panel_ratios: [3, 1]
```

### カスタマイズ可能な項目
- データ取得期間
- テクニカル指標のパラメータ
- チャートのスタイル・サイズ
- ファイル命名規則
- ログ設定

## 📊 使用方法

### 個別銘柄分析
```bash
# 基本的な分析
python unified_stock_analyzer.py --ticker TSLA

# 特定日基準の分析
python unified_stock_analyzer.py --ticker RKLB --date 2025-01-03

# 複数銘柄の連続分析
python unified_stock_analyzer.py --ticker TSLA
python unified_stock_analyzer.py --ticker FSLR
python unified_stock_analyzer.py --ticker RKLB
```

### ポートフォリオ分析
```bash
# デフォルトポートフォリオ（9銘柄）
python unified_stock_analyzer.py --portfolio

# カスタムポートフォリオ
python unified_stock_analyzer.py --portfolio --tickers TSLA,FSLR,RKLB --weights 40,30,30
```

### テスト実行
```bash
# 全テスト実行
python -m pytest test_stock_analyzer.py -v

# カバレッジ付きテスト
python -m pytest test_stock_analyzer.py -v --cov=stock_analyzer_lib

# 特定テストクラス実行
python -m pytest test_stock_analyzer.py::TestTechnicalIndicators -v
```

### 競合・財務分析
```bash
# 個別銘柄の拡張競合分析（財務分析含む）
python competitor_analysis.py

# ポートフォリオ9銘柄の財務比較
python -c "
from competitor_analysis import CompetitorAnalysis
analyzer = CompetitorAnalysis()
df = analyzer.get_portfolio_financial_comparison()
print(df[['companyName', 'marketCap', 'forwardPE', 'returnOnEquity']].to_string())
"

# 財務比較機能単体テスト
python financial_comparison_extension.py
```

### ポートフォリオ総合マスターレポート
```bash
# すべての分析を統合した総合HTMLレポート生成
python portfolio_master_report.py

# 生成されたHTMLレポートは以下に保存されます：
# reports/html/portfolio_master_report_YYYY-MM-DD.html

# レポートには以下が含まれます：
# - 9銘柄の現在状況（価格、指標）
# - 専門家討論分析（4専門家の議論）
# - 財務パフォーマンス比較
# - 競合他社分析
# - ポートフォリオ最適化提案
```

## 🔧 開発ツール

### コード品質管理
```bash
# Black フォーマッター適用
black .

# Flake8 リント実行
flake8 . --max-line-length=88

# MyPy 型チェック
mypy unified_stock_analyzer.py
```

### Git 管理
```bash
# 現在の状況確認
git status

# 変更のステージング
git add .

# コミット作成
git commit -m "feat: Add new analysis feature"

# リモートプッシュ
git push origin feature/your-branch-name
```

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. インポートエラー
```
ModuleNotFoundError: No module named 'yfinance'
```
**解決方法**: 依存関係を再インストール
```bash
pip install -r requirements.txt
```

#### 2. データ取得エラー
```
データが取得できませんでした
```
**解決方法**: 
- インターネット接続を確認
- ティッカーシンボルが正しいか確認
- yfinance APIの制限に引っかかっていないか確認

#### 3. チャート生成エラー
```
チャート生成エラー
```
**解決方法**: 
- `charts/` ディレクトリの存在確認
- 書き込み権限の確認
- データの妥当性確認

#### 4. テスト失敗
```
FAILED test_stock_analyzer.py
```
**解決方法**: 
- 個別テストを実行して問題を特定
- データ取得の問題なら一時的にスキップ
- 環境固有の問題なら設定を調整

### デバッグ方法
```python
# ログレベルを DEBUG に設定
import logging
logging.basicConfig(level=logging.DEBUG)

# データフレームの中身確認
print(df.head())
print(df.info())

# エラー詳細表示
import traceback
traceback.print_exc()
```

## 🎨 カスタマイズガイド

### 新しい銘柄の追加
1. `calculate_fund_score()` にスコア追加
2. `calculate_macro_score()` にスコア追加
3. `expert_discussions` に討論テンプレート追加
4. テストケース作成

### 新しいテクニカル指標の追加
1. `TechnicalIndicators` クラスに計算メソッド追加
2. `add_technical_indicators()` で指標を統合
3. HTMLレポートの表示に追加
4. テストケース作成

### UIのカスタマイズ
1. `html_report_generator.py` のCSSスタイル修正
2. チャートの色・レイアウト調整
3. `config.yaml` でデフォルト設定変更

## 📚 参考資料

### 主要ライブラリドキュメント
- [yfinance](https://pypi.org/project/yfinance/): 株価データ取得
- [mplfinance](https://pypi.org/project/mplfinance/): 金融チャート生成
- [pandas](https://pandas.pydata.org/): データ分析
- [pytest](https://docs.pytest.org/): テストフレームワーク

### 金融分析リソース
- [Investopedia](https://www.investopedia.com/): 金融用語解説
- [TradingView](https://tradingview.com/): チャート分析参考
- [SEC EDGAR](https://www.sec.gov/edgar): 企業財務情報

## 🤝 コントリビューション

### プルリクエストの流れ
1. フィーチャーブランチ作成
2. 変更実装とテスト作成
3. コード品質チェック実行
4. プルリクエスト作成

### コーディング規約
- PEP8 準拠（Black フォーマッター使用）
- 型注釈必須
- docstring 記述必須
- テストカバレッジ維持

---

**更新日**: 2025年1月3日  
**対象バージョン**: v1.0.0  
**サポート**: 開発進捗レポートとロードマップも参照してください

---

## 詳細分析

### 主要なタスク
- npmでインストールしたClaude CLI（または類似ツール）の実行ファイルが、コマンドラインから認識されるようにする。

### 重要な要件・制約
- Windows環境（PowerShell）
- npmグローバルインストールのパスがPATHに含まれていること

### 潜在的な課題
- npmのグローバルパスがPATHに自動追加されていない
- PowerShellの再起動が必要な場合がある
- 複数のNode.jsバージョン管理ツール（nvm等）を使っている場合、パスが競合している可能性

---

## ステップバイステップ確認・対応

### 1. npmグローバルパスの確認

PowerShellで以下を実行してください：

```powershell
npm config get prefix
```

この出力例（例: `C:\Users\ユーザー名\AppData\Roaming\npm`）の下に`claude.cmd`や`claude`という実行ファイルがあるか確認します。

```powershell
dir (npm config get prefix)
```

### 2. PATHに含まれているか確認

PowerShellで以下を実行：

```powershell
$env:PATH
```

この中に、上記npmのprefixパス（例: `C:\Users\ユーザー名\AppData\Roaming\npm`）が含まれているか確認してください。

### 3. 含まれていない場合の対処

#### 一時的にPATHを追加（PowerShellのこのセッションのみ）

```powershell
$env:PATH += ";C:\Users\ユーザー名\AppData\Roaming\npm"
```
（上記パスはnpm config get prefixの出力に合わせてください）

#### 永続的にPATHを追加（今後も有効）

「システム環境変数」または「ユーザー環境変数」のPATHに、npmのprefixパスを追加してください。

1. Windowsの「システムのプロパティ」→「環境変数」
2. 「ユーザー環境変数」または「システム環境変数」のPATHを編集
3. 先ほどのnpm prefixパスを追加
4. PowerShellを再起動

---

## 4. 動作確認

再度PowerShellを開き、下記を実行：

```powershell
claude --help
```
または
```powershell
claude
```

---

## まとめ

- npmでエラーがなければ、**パスの問題**がほぼ確実です。
- 上記手順でPATHを修正すれば、`claude`コマンドが認識されるはずです。

---

### もし上記で解決しない場合

- `claude`実行ファイルがnpmのprefixディレクトリに存在するか確認
- `claude.cmd`や`claude.ps1`など、Windows用のラッパーが生成されているか確認
- それでも動かない場合は、`npm uninstall -g claude` → `npm install -g claude`で再インストール

---

**進捗や追加のエラー内容があれば、出力を貼り付けてください。さらに詳しくサポートします。**