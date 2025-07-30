#!/usr/bin/env python3
"""
Test script to regenerate portfolio report and verify FSLR is included
"""

import sys
import os

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_portfolio_report():
    """ポートフォリオレポートを再生成してFSLRが含まれているか確認"""
    
    print("=== ポートフォリオレポート再生成テスト ===")
    
    try:
        from src.portfolio.portfolio_master_report_hybrid import PortfolioMasterReportHybrid
        
        # レポート生成器を作成
        print("レポート生成器を初期化中...")
        generator = PortfolioMasterReportHybrid()
        
        # レポートを生成・保存
        print("レポートを生成中...")
        output_path = generator.save_report()
        
        print(f"\n✅ レポート生成完了: {output_path}")
        
        # 生成されたHTMLファイルを読み込んでFSLRが含まれているか確認
        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # FSLRのstock-cardが存在するか確認
        fslr_card_count = html_content.count('class="stock-ticker">FSLR</div>')
        
        print(f"\n📊 検証結果:")
        print(f"  - FSLRのstock-card: {'✅ 発見' if fslr_card_count > 0 else '❌ 見つかりません'} ({fslr_card_count}個)")
        
        # 全銘柄の確認
        tickers = ["TSLA", "FSLR", "RKLB", "ASTS", "OKLO", "JOBY", "OII", "LUNR", "RDW"]
        print(f"\n📊 全銘柄の確認:")
        for ticker in tickers:
            count = html_content.count(f'class="stock-ticker">{ticker}</div>')
            status = '✅' if count > 0 else '❌'
            print(f"  - {ticker}: {status} ({count}個)")
            
        # データ取得エラーメッセージの確認
        error_count = html_content.count('データ取得エラー')
        if error_count > 0:
            print(f"\n⚠️  データ取得エラーが {error_count} 件発生しています")
            
        return output_path
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    output_path = test_portfolio_report()
    
    if output_path:
        print(f"\n💡 ブラウザで以下のファイルを開いて確認してください:")
        print(f"   {os.path.abspath(output_path)}")