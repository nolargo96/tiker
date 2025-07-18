"""
詳細投資分析レポート生成機能のテストスクリプト
"""

import sys
import os
from datetime import datetime

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_detailed_report(ticker: str = "TSLA"):
    """詳細レポート生成機能をテスト"""
    
    print(f"=== {ticker} 詳細投資分析レポート生成テスト ===")
    print(f"テスト開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. unified_stock_analyzerから関数をインポート
        from unified_stock_analyzer import analyze_and_chart_stock
        
        # 2. 詳細レポート生成を有効にして分析を実行
        today_str = datetime.now().strftime("%Y-%m-%d")
        success, message = analyze_and_chart_stock(
            ticker_symbol=ticker,
            today_date_str=today_str,
            generate_detailed_report=True  # 詳細レポート生成を有効化
        )
        
        if success:
            print(f"\n✅ 詳細分析レポート生成成功!")
            print(f"メッセージ: {message}")
        else:
            print(f"\n❌ エラーが発生しました: {message}")
            
    except ImportError as e:
        print(f"\n❌ インポートエラー: {str(e)}")
        print("必要なモジュールがインストールされているか確認してください:")
        print("  - pip install yfinance pandas numpy matplotlib mplfinance")
        print("  - pip install jinja2")
        
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {str(e)}")
        import traceback
        traceback.print_exc()


def test_discussion_generator():
    """専門家討論生成機能を直接テスト"""
    
    print("\n=== 専門家討論生成機能の単体テスト ===")
    
    try:
        from expert_discussion_generator import ExpertDiscussionGenerator
        import pandas as pd
        import numpy as np
        
        # テスト用データの作成
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
        test_data = pd.DataFrame({
            'Open': np.random.randn(252).cumsum() + 100,
            'High': np.random.randn(252).cumsum() + 102,
            'Low': np.random.randn(252).cumsum() + 98,
            'Close': np.random.randn(252).cumsum() + 100,
            'Volume': np.random.randint(1000000, 10000000, 252),
            'EMA20': np.random.randn(252).cumsum() + 100,
            'EMA50': np.random.randn(252).cumsum() + 99,
            'SMA200': np.random.randn(252).cumsum() + 98,
            'RSI': np.random.uniform(20, 80, 252),
            'BB_upper': np.random.randn(252).cumsum() + 105,
            'BB_lower': np.random.randn(252).cumsum() + 95,
            'ATR': np.random.uniform(1, 5, 252)
        }, index=dates)
        
        # 討論生成のテスト
        generator = ExpertDiscussionGenerator()
        result = generator.generate_full_analysis(
            ticker="TEST",
            df=test_data,
            date_str=datetime.now().strftime("%Y-%m-%d")
        )
        
        print("\n生成された分析結果の構造:")
        for key in result.keys():
            print(f"  - {key}: {type(result[key])}")
            
        print("\n✅ 専門家討論生成機能のテスト成功!")
        
    except Exception as e:
        print(f"\n❌ 専門家討論生成エラー: {str(e)}")
        import traceback
        traceback.print_exc()


def check_dependencies():
    """必要な依存関係をチェック"""
    
    print("\n=== 依存関係チェック ===")
    
    dependencies = {
        'pandas': 'データ処理',
        'numpy': '数値計算',
        'yfinance': '株価データ取得',
        'matplotlib': 'チャート描画',
        'mplfinance': 'ローソク足チャート',
        'jinja2': 'HTMLテンプレート',
        'pathlib': 'パス操作（標準ライブラリ）'
    }
    
    missing = []
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module:<15} - {description}")
        except ImportError:
            print(f"❌ {module:<15} - {description} (未インストール)")
            missing.append(module)
    
    if missing:
        print(f"\n以下のコマンドで不足モジュールをインストールしてください:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True


def main():
    """メインテスト関数"""
    
    print("=" * 70)
    print("tiker.mdに沿った詳細分析HTMLレポート生成機能テスト")
    print("=" * 70)
    
    # 依存関係チェック
    if not check_dependencies():
        print("\n⚠️  必要なモジュールをインストールしてから再実行してください。")
        return
    
    # コマンドライン引数からティッカーを取得
    ticker = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    
    # 詳細レポート生成テスト
    test_detailed_report(ticker)
    
    # 討論生成機能の単体テスト（オプション）
    if "--test-generator" in sys.argv:
        test_discussion_generator()
    
    print("\n" + "=" * 70)
    print("テスト完了")
    print("=" * 70)


if __name__ == "__main__":
    main()