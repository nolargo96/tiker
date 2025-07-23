# Tiker Dashboard Pro Ultimate - 究極強化版

次世代AI駆動投資分析プラットフォーム

## 🚀 新機能概要

### 1. **リアルタイムポートフォリオ分析**
- 💰 ポートフォリオ価値のリアルタイム追跡
- 📊 P&L（損益）計算と表示
- 📈 シャープレシオ、最大ドローダウン、ボラティリティ分析
- 🏆 ベスト/ワーストパフォーマー自動識別

### 2. **履歴シグナル追跡システム**
- 📜 全シグナルの履歴を自動記録
- 🎯 シグナル精度の自動計算
- 📅 タイムライン表示での変化追跡
- 📊 精度レポートの生成

### 3. **高度なフィルタリング機能**
- 🔍 セクター別フィルター
- 💹 パフォーマンスベースのフィルター
- 🚦 シグナルタイプ別フィルター
- ⏱️ 時間範囲の柔軟な選択（1週間〜5年）

### 4. **AI投資インサイト**
- 🤖 機械学習による深層分析
- 💡 トレンド、モメンタム、リスクの自動検出
- 📝 具体的なアクション提案
- ⚠️ リスク警告とアラート

### 5. **比較分析ツール**
- ⚖️ 最大5銘柄の同時比較
- 🎯 レーダーチャートでのスコア比較
- 📈 正規化価格チャートでの推移比較
- 📊 総合比較テーブル

### 6. **エクスポート機能**
- 📊 Excel形式（条件付き書式、チャート付き）
- 📄 PDFレポート（プロフェッショナルレイアウト）
- 📋 CSV形式（データ分析用）
- 🔧 JSON形式（API連携用）

## 📦 必要なパッケージ

```bash
# 基本パッケージ（既存）
pip install streamlit pandas numpy yfinance plotly

# 新規追加パッケージ
pip install xlsxwriter reportlab matplotlib seaborn
```

## 🚀 起動方法

### 強化版ダッシュボード（新）
```bash
streamlit run dashboard_pro.py
```

### 従来版ダッシュボード
```bash
streamlit run dashboard_enhanced.py
```

## 📱 使用方法

### 1. **表示モード選択**
サイドバーから以下のモードを選択：
- **ダッシュボード**: 総合的な概要表示
- **パフォーマンス分析**: 詳細な損益分析
- **シグナル履歴**: 過去のシグナル追跡
- **AIインサイト**: AI による投資提案
- **比較分析**: 銘柄間の比較

### 2. **フィルタリング**
- セクター選択
- 最小リターン率設定
- シグナルタイプ選択

### 3. **時間範囲設定**
1週間から5年まで柔軟に選択可能

### 4. **データエクスポート**
サイドバーのエクスポートボタンから：
- Excel: 詳細データとチャート
- PDF: プロフェッショナルレポート

## 🏗️ アーキテクチャ

### メインコンポーネント

#### `dashboard_pro.py`
究極強化版ダッシュボードのメインファイル

```python
class UltimateDashboardAnalyzer:
    """究極版分析システム"""
    - calculate_portfolio_performance()  # ポートフォリオ分析
    - generate_ai_insights()            # AIインサイト生成
    - calculate_signal_accuracy()       # シグナル精度計算
    
class UltimateDashboardApp:
    """究極版アプリケーション"""
    - _render_dashboard_view()         # ダッシュボード表示
    - _render_performance_view()       # パフォーマンス分析
    - _render_ai_insights_view()       # AIインサイト表示
```

#### `signal_history_tracker.py`
シグナル履歴追跡モジュール

```python
class SignalHistoryTracker:
    - record_signal()              # シグナル記録
    - update_performance()         # パフォーマンス更新
    - calculate_signal_accuracy()  # 精度計算
    - generate_accuracy_report()   # レポート生成
```

#### `dashboard_export_manager.py`
エクスポート管理モジュール

```python
class DashboardExportManager:
    - export_to_excel()   # Excel出力
    - export_to_pdf()     # PDF生成
    - export_to_json()    # JSON出力
    - export_to_csv()     # CSV出力
```

## 📊 データ構造

### シグナル履歴
```json
{
  "TSLA": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "signal": "BUY",
      "score": 4.2,
      "price": 250.50,
      "performance_7d": 3.5
    }
  ]
}
```

### ポートフォリオパフォーマンス
```python
{
  'total_value': 150000,
  'total_cost': 130000,
  'total_return': 20000,
  'total_return_pct': 15.38,
  'sharpe_ratio': 1.2,
  'max_drawdown': -8.5,
  'volatility': 0.25
}
```

## 🎨 UIカスタマイズ

### カスタムCSS
- グラデーション背景
- アニメーション効果
- レスポンシブデザイン
- ダークテーマ対応

### インタラクティブ要素
- リアルタイムデータ更新
- ホバー効果
- プログレスバーアニメーション
- ライブインジケーター

## 🔧 設定オプション

### 詳細設定（サイドバー）
- テクニカル指標表示
- 出来高表示
- 売買シグナル表示
- 自動更新（5分毎）

## 🚨 注意事項

1. **データ使用量**: リアルタイムデータ取得により通信量が増加
2. **計算負荷**: AI分析により処理時間が必要
3. **ブラウザ要件**: 最新のChrome/Firefox推奨
4. **画面サイズ**: 1920x1080以上推奨

## 🔄 今後の拡張予定

1. **アラート機能**
   - メール/Slack通知
   - 価格アラート
   - シグナル変更通知

2. **バックテスト機能**
   - 過去データでの戦略検証
   - パフォーマンス評価

3. **ポートフォリオ最適化**
   - AIによるリバランス提案
   - リスク最適化

4. **マルチユーザー対応**
   - ユーザー認証
   - 個別ポートフォリオ管理

## 📝 ライセンス

このプロジェクトは教育目的のみ。投資判断は自己責任でお願いします。

## 🤝 コントリビューション

改善提案やバグ報告は大歓迎です！

---

**Created with ❤️ by Tiker Development Team**