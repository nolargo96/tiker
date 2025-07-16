"""
yfinance財務データ調査ツール
yfinanceライブラリで取得可能な財務データの種類と形式を調査する
"""

import yfinance as yf
import pandas as pd
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


def investigate_yfinance_data(ticker_symbol: str = "AAPL") -> Dict[str, Any]:
    """
    yfinanceで取得可能な財務データを網羅的に調査する
    
    Args:
        ticker_symbol (str): 調査対象のティッカーシンボル
        
    Returns:
        Dict[str, Any]: 取得したデータの情報をまとめた辞書
    """
    
    print(f"=== yfinance財務データ調査: {ticker_symbol} ===")
    print(f"調査実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Tickerオブジェクトを作成
    ticker = yf.Ticker(ticker_symbol)
    
    results = {}
    
    # 1. 基本情報 (info)
    print("1. 基本情報 (ticker.info)")
    try:
        info = ticker.info
        if info:
            print(f"  ✓ 基本情報取得成功: {len(info)}項目")
            
            # 重要な財務関連項目をチェック
            financial_keys = [
                'marketCap', 'enterpriseValue', 'forwardPE', 'trailingPE',
                'priceToBook', 'debtToEquity', 'returnOnEquity', 'returnOnAssets',
                'profitMargins', 'operatingMargins', 'grossMargins',
                'revenueGrowth', 'earningsGrowth', 'currentRatio', 'quickRatio',
                'totalCash', 'totalDebt', 'freeCashflow', 'operatingCashflow',
                'earningsQuarterlyGrowth', 'revenueQuarterlyGrowth'
            ]
            
            available_financial = {key: info.get(key) for key in financial_keys if key in info}
            print(f"  主要財務指標: {len(available_financial)}項目")
            
            # CEO情報をチェック
            ceo_keys = ['companyOfficers']
            available_ceo = {key: info.get(key) for key in ceo_keys if key in info}
            if available_ceo.get('companyOfficers'):
                print(f"  役員情報: {len(available_ceo['companyOfficers'])}名")
            
            results['info'] = {
                'total_items': len(info),
                'financial_metrics': available_financial,
                'ceo_info': available_ceo
            }
        else:
            print("  ✗ 基本情報取得失敗")
            results['info'] = None
    except Exception as e:
        print(f"  ✗ エラー: {str(e)}")
        results['info'] = None
    
    print()
    
    # 2. 年次決算データ (financials, balance_sheet, cashflow)
    print("2. 年次決算データ")
    
    # 損益計算書
    try:
        financials = ticker.financials
        if not financials.empty:
            print(f"  ✓ 損益計算書 (financials): {financials.shape[0]}項目 x {financials.shape[1]}年")
            results['annual_financials'] = {
                'shape': financials.shape,
                'columns': financials.columns.tolist(),
                'index': financials.index.tolist()
            }
        else:
            print("  ✗ 損益計算書取得失敗")
            results['annual_financials'] = None
    except Exception as e:
        print(f"  ✗ 損益計算書エラー: {str(e)}")
        results['annual_financials'] = None
    
    # 貸借対照表
    try:
        balance_sheet = ticker.balance_sheet
        if not balance_sheet.empty:
            print(f"  ✓ 貸借対照表 (balance_sheet): {balance_sheet.shape[0]}項目 x {balance_sheet.shape[1]}年")
            results['annual_balance_sheet'] = {
                'shape': balance_sheet.shape,
                'columns': balance_sheet.columns.tolist(),
                'index': balance_sheet.index.tolist()
            }
        else:
            print("  ✗ 貸借対照表取得失敗")
            results['annual_balance_sheet'] = None
    except Exception as e:
        print(f"  ✗ 貸借対照表エラー: {str(e)}")
        results['annual_balance_sheet'] = None
    
    # キャッシュフロー
    try:
        cashflow = ticker.cashflow
        if not cashflow.empty:
            print(f"  ✓ キャッシュフロー (cashflow): {cashflow.shape[0]}項目 x {cashflow.shape[1]}年")
            results['annual_cashflow'] = {
                'shape': cashflow.shape,
                'columns': cashflow.columns.tolist(),
                'index': cashflow.index.tolist()
            }
        else:
            print("  ✗ キャッシュフロー取得失敗")
            results['annual_cashflow'] = None
    except Exception as e:
        print(f"  ✗ キャッシュフローエラー: {str(e)}")
        results['annual_cashflow'] = None
    
    print()
    
    # 3. 四半期決算データ
    print("3. 四半期決算データ")
    
    # 四半期損益計算書
    try:
        quarterly_financials = ticker.quarterly_financials
        if not quarterly_financials.empty:
            print(f"  ✓ 四半期損益計算書: {quarterly_financials.shape[0]}項目 x {quarterly_financials.shape[1]}四半期")
            results['quarterly_financials'] = {
                'shape': quarterly_financials.shape,
                'columns': quarterly_financials.columns.tolist(),
                'index': quarterly_financials.index.tolist()
            }
        else:
            print("  ✗ 四半期損益計算書取得失敗")
            results['quarterly_financials'] = None
    except Exception as e:
        print(f"  ✗ 四半期損益計算書エラー: {str(e)}")
        results['quarterly_financials'] = None
    
    # 四半期貸借対照表
    try:
        quarterly_balance_sheet = ticker.quarterly_balance_sheet
        if not quarterly_balance_sheet.empty:
            print(f"  ✓ 四半期貸借対照表: {quarterly_balance_sheet.shape[0]}項目 x {quarterly_balance_sheet.shape[1]}四半期")
            results['quarterly_balance_sheet'] = {
                'shape': quarterly_balance_sheet.shape,
                'columns': quarterly_balance_sheet.columns.tolist(),
                'index': quarterly_balance_sheet.index.tolist()
            }
        else:
            print("  ✗ 四半期貸借対照表取得失敗")
            results['quarterly_balance_sheet'] = None
    except Exception as e:
        print(f"  ✗ 四半期貸借対照表エラー: {str(e)}")
        results['quarterly_balance_sheet'] = None
    
    # 四半期キャッシュフロー
    try:
        quarterly_cashflow = ticker.quarterly_cashflow
        if not quarterly_cashflow.empty:
            print(f"  ✓ 四半期キャッシュフロー: {quarterly_cashflow.shape[0]}項目 x {quarterly_cashflow.shape[1]}四半期")
            results['quarterly_cashflow'] = {
                'shape': quarterly_cashflow.shape,
                'columns': quarterly_cashflow.columns.tolist(),
                'index': quarterly_cashflow.index.tolist()
            }
        else:
            print("  ✗ 四半期キャッシュフロー取得失敗")
            results['quarterly_cashflow'] = None
    except Exception as e:
        print(f"  ✗ 四半期キャッシュフローエラー: {str(e)}")
        results['quarterly_cashflow'] = None
    
    print()
    
    # 4. その他の財務関連データ
    print("4. その他の財務関連データ")
    
    # 決算発表日
    try:
        earnings_dates = ticker.earnings_dates
        if earnings_dates is not None and not earnings_dates.empty:
            print(f"  ✓ 決算発表日 (earnings_dates): {len(earnings_dates)}件")
            results['earnings_dates'] = {
                'count': len(earnings_dates),
                'columns': earnings_dates.columns.tolist() if hasattr(earnings_dates, 'columns') else None
            }
        else:
            print("  ✗ 決算発表日取得失敗")
            results['earnings_dates'] = None
    except Exception as e:
        print(f"  ✗ 決算発表日エラー: {str(e)}")
        results['earnings_dates'] = None
    
    # 決算履歴
    try:
        earnings = ticker.earnings
        if earnings is not None and not earnings.empty:
            print(f"  ✓ 決算履歴 (earnings): {earnings.shape[0]}年 x {earnings.shape[1]}項目")
            results['earnings'] = {
                'shape': earnings.shape,
                'columns': earnings.columns.tolist(),
                'index': earnings.index.tolist()
            }
        else:
            print("  ✗ 決算履歴取得失敗")
            results['earnings'] = None
    except Exception as e:
        print(f"  ✗ 決算履歴エラー: {str(e)}")
        results['earnings'] = None
    
    # 四半期決算履歴
    try:
        quarterly_earnings = ticker.quarterly_earnings
        if quarterly_earnings is not None and not quarterly_earnings.empty:
            print(f"  ✓ 四半期決算履歴: {quarterly_earnings.shape[0]}四半期 x {quarterly_earnings.shape[1]}項目")
            results['quarterly_earnings'] = {
                'shape': quarterly_earnings.shape,
                'columns': quarterly_earnings.columns.tolist(),
                'index': quarterly_earnings.index.tolist()
            }
        else:
            print("  ✗ 四半期決算履歴取得失敗")
            results['quarterly_earnings'] = None
    except Exception as e:
        print(f"  ✗ 四半期決算履歴エラー: {str(e)}")
        results['quarterly_earnings'] = None
    
    # 推奨情報
    try:
        recommendations = ticker.recommendations
        if recommendations is not None and not recommendations.empty:
            print(f"  ✓ アナリスト推奨: {len(recommendations)}件")
            results['recommendations'] = {
                'count': len(recommendations),
                'columns': recommendations.columns.tolist()
            }
        else:
            print("  ✗ アナリスト推奨取得失敗")
            results['recommendations'] = None
    except Exception as e:
        print(f"  ✗ アナリスト推奨エラー: {str(e)}")
        results['recommendations'] = None
    
    print()
    
    # 5. 株主・配当関連
    print("5. 株主・配当関連データ")
    
    # 配当履歴
    try:
        dividends = ticker.dividends
        if dividends is not None and not dividends.empty:
            print(f"  ✓ 配当履歴 (dividends): {len(dividends)}件")
            results['dividends'] = {
                'count': len(dividends),
                'latest': dividends.tail(5).to_dict() if len(dividends) > 0 else None
            }
        else:
            print("  ✗ 配当履歴取得失敗")
            results['dividends'] = None
    except Exception as e:
        print(f"  ✗ 配当履歴エラー: {str(e)}")
        results['dividends'] = None
    
    # 株式分割履歴
    try:
        splits = ticker.splits
        if splits is not None and not splits.empty:
            print(f"  ✓ 株式分割履歴: {len(splits)}件")
            results['splits'] = {
                'count': len(splits),
                'history': splits.to_dict() if len(splits) > 0 else None
            }
        else:
            print("  ✗ 株式分割履歴なし")
            results['splits'] = None
    except Exception as e:
        print(f"  ✗ 株式分割履歴エラー: {str(e)}")
        results['splits'] = None
    
    # 大株主情報
    try:
        major_holders = ticker.major_holders
        if major_holders is not None and not major_holders.empty:
            print(f"  ✓ 大株主情報: {major_holders.shape[0]}項目")
            results['major_holders'] = {
                'shape': major_holders.shape,
                'data': major_holders.to_dict() if not major_holders.empty else None
            }
        else:
            print("  ✗ 大株主情報取得失敗")
            results['major_holders'] = None
    except Exception as e:
        print(f"  ✗ 大株主情報エラー: {str(e)}")
        results['major_holders'] = None
    
    # 機関投資家情報
    try:
        institutional_holders = ticker.institutional_holders
        if institutional_holders is not None and not institutional_holders.empty:
            print(f"  ✓ 機関投資家情報: {len(institutional_holders)}件")
            results['institutional_holders'] = {
                'count': len(institutional_holders),
                'columns': institutional_holders.columns.tolist()
            }
        else:
            print("  ✗ 機関投資家情報取得失敗")
            results['institutional_holders'] = None
    except Exception as e:
        print(f"  ✗ 機関投資家情報エラー: {str(e)}")
        results['institutional_holders'] = None
    
    print()
    print("=== 調査完了 ===")
    
    return results


def demonstrate_financial_data_usage(ticker_symbol: str = "AAPL"):
    """
    取得した財務データの具体的な使用例を示す
    """
    print(f"\n=== 財務データ使用例: {ticker_symbol} ===")
    
    ticker = yf.Ticker(ticker_symbol)
    
    # 1. 主要財務指標の表示
    print("1. 主要財務指標")
    try:
        info = ticker.info
        if info:
            metrics = {
                'Market Cap': info.get('marketCap'),
                'P/E Ratio (Forward)': info.get('forwardPE'),
                'P/E Ratio (Trailing)': info.get('trailingPE'),
                'Price to Book': info.get('priceToBook'),
                'Debt to Equity': info.get('debtToEquity'),
                'ROE': info.get('returnOnEquity'),
                'ROA': info.get('returnOnAssets'),
                'Profit Margin': info.get('profitMargins'),
                'Revenue Growth': info.get('revenueGrowth'),
                'Free Cash Flow': info.get('freeCashflow')
            }
            
            for key, value in metrics.items():
                if value is not None:
                    if key == 'Market Cap' or key == 'Free Cash Flow':
                        print(f"  {key}: ${value:,.0f}" if isinstance(value, (int, float)) else f"  {key}: {value}")
                    elif key in ['Profit Margin', 'Revenue Growth', 'ROE', 'ROA']:
                        print(f"  {key}: {value:.2%}" if isinstance(value, (int, float)) else f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value:.2f}" if isinstance(value, (int, float)) else f"  {key}: {value}")
                else:
                    print(f"  {key}: N/A")
    except Exception as e:
        print(f"  エラー: {str(e)}")
    
    # 2. 年次売上・利益の推移
    print("\n2. 年次売上・利益推移（直近4年）")
    try:
        financials = ticker.financials
        if not financials.empty:
            # 売上高 (Total Revenue)
            revenue_items = ['Total Revenue', 'Revenue']
            revenue = None
            for item in revenue_items:
                if item in financials.index:
                    revenue = financials.loc[item]
                    break
            
            # 純利益 (Net Income)
            income_items = ['Net Income', 'Net Income From Continuing Ops']
            net_income = None
            for item in income_items:
                if item in financials.index:
                    net_income = financials.loc[item]
                    break
            
            if revenue is not None:
                print("  売上高:")
                for date, value in revenue.items():
                    if pd.notna(value):
                        print(f"    {date.strftime('%Y')}: ${value/1e9:.2f}B")
            
            if net_income is not None:
                print("  純利益:")
                for date, value in net_income.items():
                    if pd.notna(value):
                        print(f"    {date.strftime('%Y')}: ${value/1e9:.2f}B")
    except Exception as e:
        print(f"  エラー: {str(e)}")
    
    # 3. 四半期決算トレンド
    print("\n3. 四半期決算トレンド（直近4四半期）")
    try:
        quarterly_financials = ticker.quarterly_financials
        if not quarterly_financials.empty:
            # 四半期売上高
            revenue_items = ['Total Revenue', 'Revenue']
            revenue = None
            for item in revenue_items:
                if item in quarterly_financials.index:
                    revenue = quarterly_financials.loc[item]
                    break
            
            if revenue is not None:
                print("  四半期売上高:")
                for date, value in revenue.items():
                    if pd.notna(value):
                        print(f"    {date.strftime('%Y-Q%m')}: ${value/1e9:.2f}B")
    except Exception as e:
        print(f"  エラー: {str(e)}")
    
    # 4. CEO・役員情報
    print("\n4. CEO・役員情報")
    try:
        info = ticker.info
        if info and 'companyOfficers' in info:
            officers = info['companyOfficers']
            if officers:
                for officer in officers[:3]:  # 上位3名を表示
                    name = officer.get('name', 'N/A')
                    title = officer.get('title', 'N/A')
                    age = officer.get('age', 'N/A')
                    compensation = officer.get('totalPay', 'N/A')
                    
                    print(f"  {title}: {name}")
                    if age != 'N/A':
                        print(f"    年齢: {age}")
                    if compensation != 'N/A' and compensation is not None:
                        print(f"    報酬: ${compensation:,.0f}")
            else:
                print("  役員情報なし")
        else:
            print("  役員情報取得失敗")
    except Exception as e:
        print(f"  エラー: {str(e)}")


def compare_financial_metrics(tickers: List[str]):
    """
    複数銘柄の財務指標を比較する（competitor_analysis.pyとの統合例）
    """
    print(f"\n=== 財務指標比較: {', '.join(tickers)} ===")
    
    comparison_data = []
    
    for ticker_symbol in tickers:
        print(f"\n{ticker_symbol} のデータ取得中...")
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            if info:
                data = {
                    'Ticker': ticker_symbol,
                    'Market Cap': info.get('marketCap'),
                    'P/E (Forward)': info.get('forwardPE'),
                    'P/B Ratio': info.get('priceToBook'),
                    'ROE': info.get('returnOnEquity'),
                    'Profit Margin': info.get('profitMargins'),
                    'Revenue Growth': info.get('revenueGrowth'),
                    'Debt/Equity': info.get('debtToEquity')
                }
                comparison_data.append(data)
            else:
                print(f"  {ticker_symbol}: データ取得失敗")
        except Exception as e:
            print(f"  {ticker_symbol}: エラー - {str(e)}")
    
    # 比較テーブルの表示
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        print("\n財務指標比較テーブル:")
        print(df.to_string(index=False, float_format='%.2f'))
        
        return df
    else:
        print("比較データの取得に失敗しました。")
        return None


if __name__ == "__main__":
    # メイン調査実行
    print("yfinance財務データ調査ツール")
    print("=" * 50)
    
    # 1. AAPL での詳細調査
    results_aapl = investigate_yfinance_data("AAPL")
    
    # 2. 使用例のデモンストレーション
    demonstrate_financial_data_usage("AAPL")
    
    # 3. ポートフォリオ銘柄での比較例
    portfolio_tickers = ["TSLA", "FSLR", "RKLB", "ASTS"]
    compare_financial_metrics(portfolio_tickers)
    
    # 4. 結果をJSONファイルに保存（Timestampキーの問題を修正）
    def clean_results_for_json(data):
        """JSON保存用にデータをクリーンアップ"""
        if isinstance(data, dict):
            return {str(k): clean_results_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [clean_results_for_json(item) for item in data]
        else:
            return data
    
    cleaned_results = clean_results_for_json(results_aapl)
    import json
    with open('yfinance_investigation_results.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n調査結果を 'yfinance_investigation_results.json' に保存しました。")