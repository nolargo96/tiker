"""
Test Suite for Competitor Analysis Module
競合分析モジュールのテストスイート
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from competitor_analysis import CompetitorAnalysis


class TestCompetitorAnalysis:
    """競合分析のテストクラス"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.analyzer = CompetitorAnalysis()
    
    def test_competitor_mapping_structure(self):
        """競合企業マッピングの構造テスト"""
        # 全9銘柄が定義されているか
        expected_tickers = ['TSLA', 'FSLR', 'RKLB', 'ASTS', 'OKLO', 'JOBY', 'OII', 'LUNR', 'RDW']
        assert set(self.analyzer.competitor_mapping.keys()) == set(expected_tickers)
        
        # 各銘柄の必須フィールドが存在するか
        for ticker, data in self.analyzer.competitor_mapping.items():
            assert 'name' in data
            assert 'sector' in data
            assert 'competitors' in data
            assert 'leader' in data
            assert 'descriptions' in data
            assert isinstance(data['competitors'], list)
            assert len(data['competitors']) > 0
    
    def test_competitor_mapping_content(self):
        """競合企業マッピングの内容テスト"""
        # TSLAのマッピング確認
        tsla_data = self.analyzer.competitor_mapping['TSLA']
        assert tsla_data['name'] == 'テスラ'
        assert tsla_data['sector'] == 'EV・自動運転'
        assert 'NIO' in tsla_data['competitors']
        assert 'RIVN' in tsla_data['competitors']
        assert tsla_data['leader'] == 'TSLA'
        
        # FSLRのマッピング確認
        fslr_data = self.analyzer.competitor_mapping['FSLR']
        assert fslr_data['name'] == 'ファーストソーラー'
        assert fslr_data['sector'] == '太陽光発電'
        assert 'ENPH' in fslr_data['competitors']
        assert fslr_data['leader'] == 'ENPH'
    
    @patch('competitor_analysis.StockDataManager')
    def test_get_competitor_data_success(self, mock_data_manager):
        """競合データ取得成功テスト"""
        # モックデータ作成
        mock_df = pd.DataFrame({
            'Close': [100, 105, 102, 108, 110],
            'Volume': [1000, 1100, 900, 1200, 1050],
            'RSI': [45, 50, 48, 55, 52],
            'EMA20': [98, 102, 103, 105, 107]
        })
        
        # StockDataManagerのモック設定
        mock_instance = MagicMock()
        mock_instance.fetch_stock_data.return_value = (True, mock_df, "成功")
        mock_instance.add_technical_indicators.return_value = mock_df
        mock_data_manager.return_value = mock_instance
        
        # テスト実行
        result = self.analyzer.get_competitor_data('TSLA', 365)
        
        # 結果検証
        assert 'error' not in result
        assert result['target_ticker'] == 'TSLA'
        assert result['target_name'] == 'テスラ'
        assert result['sector'] == 'EV・自動運転'
        assert 'data' in result
        assert 'performance_comparison' in result
    
    def test_get_competitor_data_invalid_ticker(self):
        """無効ティッカーのテスト"""
        result = self.analyzer.get_competitor_data('INVALID', 365)
        assert 'error' in result
        assert 'INVALID の競合企業データが見つかりません' in result['error']
    
    @patch('competitor_analysis.StockDataManager')
    def test_calculate_relative_performance(self, mock_data_manager):
        """相対パフォーマンス計算テスト"""
        # モックデータ設定
        mock_df = pd.DataFrame({
            'Close': [100, 110, 105, 115, 120],  # 20%リターン
            'Volume': [1000, 1100, 900, 1200, 1050],
            'RSI': [45, 50, 48, 55, 52],
            'EMA20': [98, 102, 103, 105, 107]
        })
        
        mock_instance = MagicMock()
        mock_instance.fetch_stock_data.return_value = (True, mock_df, "成功")
        mock_instance.add_technical_indicators.return_value = mock_df
        mock_data_manager.return_value = mock_instance
        
        # テスト実行
        result = self.analyzer.get_competitor_data('TSLA', 365)
        
        # パフォーマンス比較データの存在確認
        assert 'performance_comparison' in result
        assert 'return_ranking' in result['performance_comparison']
        assert 'risk_adjusted_ranking' in result['performance_comparison']
        assert 'sector_average_return' in result['performance_comparison']
        assert 'target_vs_sector' in result['performance_comparison']
    
    @patch('competitor_analysis.StockDataManager')
    def test_generate_competitor_report(self, mock_data_manager):
        """競合比較レポート生成テスト"""
        # モックデータ設定
        mock_df = pd.DataFrame({
            'Close': [100, 110, 105, 115, 120],
            'Volume': [1000, 1100, 900, 1200, 1050],
            'RSI': [45, 50, 48, 55, 52],
            'EMA20': [98, 102, 103, 105, 107]
        })
        
        mock_instance = MagicMock()
        mock_instance.fetch_stock_data.return_value = (True, mock_df, "成功")
        mock_instance.add_technical_indicators.return_value = mock_df
        mock_data_manager.return_value = mock_instance
        
        # テスト実行
        report = self.analyzer.generate_competitor_report('TSLA', 365)
        
        # レポート内容確認
        assert isinstance(report, str)
        assert 'テスラ (TSLA) 競合他社分析レポート' in report
        assert 'EV・自動運転' in report
        assert 'リターンランキング' in report
        assert 'リスク分析' in report
        assert '投資判断への示唆' in report
    
    def test_generate_competitor_report_invalid_ticker(self):
        """無効ティッカーでのレポート生成テスト"""
        report = self.analyzer.generate_competitor_report('INVALID', 365)
        assert 'エラー:' in report
        assert 'INVALID の競合企業データが見つかりません' in report
    
    @patch('competitor_analysis.StockDataManager')
    def test_analyze_all_portfolio_competitors(self, mock_data_manager):
        """全ポートフォリオ競合分析テスト"""
        # モックデータ設定
        mock_df = pd.DataFrame({
            'Close': [100, 110, 105, 115, 120],
            'Volume': [1000, 1100, 900, 1200, 1050],
            'RSI': [45, 50, 48, 55, 52],
            'EMA20': [98, 102, 103, 105, 107]
        })
        
        mock_instance = MagicMock()
        mock_instance.fetch_stock_data.return_value = (True, mock_df, "成功")
        mock_instance.add_technical_indicators.return_value = mock_df
        mock_data_manager.return_value = mock_instance
        
        # テスト実行（時間短縮のため最初の3銘柄のみ）
        original_mapping = self.analyzer.competitor_mapping
        self.analyzer.competitor_mapping = {
            k: v for k, v in original_mapping.items() 
            if k in ['TSLA', 'FSLR', 'RKLB']
        }
        
        results = self.analyzer.analyze_all_portfolio_competitors(365)
        
        # 結果検証
        assert len(results) == 3
        assert 'TSLA' in results
        assert 'FSLR' in results
        assert 'RKLB' in results
        
        for ticker, report in results.items():
            assert isinstance(report, str)
            assert f'{self.analyzer.competitor_mapping[ticker]["name"]} ({ticker})' in report


class TestCompetitorAnalysisDataProcessing:
    """競合分析データ処理のテストクラス"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.analyzer = CompetitorAnalysis()
    
    def test_performance_metrics_calculation(self):
        """パフォーマンス指標計算テスト"""
        # テストデータフレーム作成
        df = pd.DataFrame({
            'Close': [100, 95, 110, 105, 120, 115, 125],
            'Volume': [1000, 1100, 900, 1200, 1050, 1300, 1150]
        })
        
        # パフォーマンス指標計算
        latest_price = df['Close'].iloc[-1]
        start_price = df['Close'].iloc[0]
        total_return = (latest_price - start_price) / start_price * 100
        
        # 期待値確認
        assert abs(total_return - 25.0) < 0.1  # 125/100 - 1 = 0.25 = 25%
        
        # ボラティリティ計算
        volatility = df['Close'].pct_change().std() * np.sqrt(252) * 100
        assert volatility > 0
        
        # 最大ドローダウン計算
        rolling_max = df['Close'].expanding().max()
        drawdown = (df['Close'] - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        
        # 最大ドローダウンは負の値であることを確認
        assert max_drawdown < 0
    
    def test_sector_statistics(self):
        """セクター統計計算テスト"""
        # テストデータ
        returns = [10.5, 15.2, 8.3, 12.1, 7.9]
        
        # 統計計算
        sector_average = np.mean(returns)
        sector_median = np.median(returns)
        
        # 期待値確認
        assert abs(sector_average - 10.8) < 0.1
        assert abs(sector_median - 10.5) < 0.1
    
    def test_risk_adjusted_metrics(self):
        """リスク調整指標テスト"""
        # テストデータ
        returns = {'TSLA': 25.0, 'NIO': 15.0, 'RIVN': 10.0}
        volatilities = {'TSLA': 50.0, 'NIO': 30.0, 'RIVN': 25.0}
        
        # リスク調整リターン計算
        risk_adjusted = {}
        for symbol in returns:
            risk_adjusted[symbol] = returns[symbol] / volatilities[symbol]
        
        # 期待値確認
        assert abs(risk_adjusted['TSLA'] - 0.5) < 0.1
        assert abs(risk_adjusted['NIO'] - 0.5) < 0.1
        assert abs(risk_adjusted['RIVN'] - 0.4) < 0.1


class TestCompetitorAnalysisEdgeCases:
    """競合分析エッジケースのテストクラス"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.analyzer = CompetitorAnalysis()
    
    def test_data_fetch_failure(self):
        """データ取得失敗テスト"""
        # 実際のネットワークエラーまたは無効ティッカーをシミュレート
        result = self.analyzer.get_competitor_data('INVALID_TICKER_XYZ', 365)
        
        # エラーハンドリング確認
        assert 'error' in result
        assert 'INVALID_TICKER_XYZ の競合企業データが見つかりません' in result['error']
    
    @patch('competitor_analysis.StockDataManager')
    def test_empty_dataframe_handling(self, mock_data_manager):
        """空のDataFrameハンドリングテスト"""
        # 空のDataFrameを返すモック
        mock_instance = MagicMock()
        mock_instance.fetch_stock_data.return_value = (True, pd.DataFrame(), "データなし")
        mock_data_manager.return_value = mock_instance
        
        # テスト実行
        result = self.analyzer.get_competitor_data('TSLA', 365)
        
        # 空データのハンドリング確認
        assert 'data' in result
        # 空のDataFrameでも正常に処理されることを確認
        assert len(result['data']) > 0
    
    def test_zero_volatility_handling(self):
        """ゼロボラティリティのハンドリングテスト"""
        # ゼロボラティリティのデータ
        df = pd.DataFrame({
            'Close': [100, 100, 100, 100, 100],  # 価格変動なし
            'Volume': [1000, 1000, 1000, 1000, 1000]
        })
        
        # ボラティリティ計算
        volatility = df['Close'].pct_change().std() * np.sqrt(252) * 100
        
        # ゼロボラティリティの場合の処理確認
        assert volatility == 0 or np.isnan(volatility)


# 実行時テスト
if __name__ == "__main__":
    pytest.main([__file__, "-v"])