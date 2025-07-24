"""
Stock Analyzer Test Suite
株式分析ライブラリのテストコード

pytest実行コマンド:
pip install pytest pandas numpy yfinance mplfinance pyyaml
python -m pytest test_stock_analyzer.py -v
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# テスト対象をインポート
from src.analysis.stock_analyzer_lib import (
    ConfigManager,
    TechnicalIndicators,
    StockDataManager,
    ChartGenerator,
    StockAnalyzer,
)


class TestConfigManager:
    """ConfigManagerのテスト"""

    def test_default_config_loading(self):
        """デフォルト設定の読み込みテスト"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
data:
  default_period_days: 365
technical:
  ema_short: 20
"""
            )
            config_path = f.name

        try:
            config = ConfigManager(config_path)
            assert config.get("data.default_period_days") == 365
            assert config.get("technical.ema_short") == 20
        finally:
            os.unlink(config_path)

    def test_missing_config_file(self):
        """存在しない設定ファイルのテスト"""
        config = ConfigManager("nonexistent.yaml")
        # デフォルト設定が使用されることを確認
        assert config.get("data.default_period_days") == 365

    def test_get_nested_config(self):
        """ネストした設定値の取得テスト"""
        config = ConfigManager("nonexistent.yaml")  # デフォルト設定使用
        assert config.get("data.default_period_days") == 365
        assert config.get("nonexistent.key", "default") == "default"


class TestTechnicalIndicators:
    """TechnicalIndicatorsのテスト"""

    @pytest.fixture
    def sample_data(self):
        """テスト用サンプルデータ"""
        dates = pd.date_range("2023-01-01", periods=100, freq="D")
        np.random.seed(42)  # 再現性のため

        # 価格データを生成（現実的な価格変動）
        close_prices = 100 + np.cumsum(np.random.randn(100) * 0.02)
        high_prices = close_prices + abs(np.random.randn(100) * 0.01)
        low_prices = close_prices - abs(np.random.randn(100) * 0.01)
        open_prices = close_prices + np.random.randn(100) * 0.005
        volumes = abs(np.random.randn(100) * 1000000)

        return pd.DataFrame(
            {
                "Open": open_prices,
                "High": high_prices,
                "Low": low_prices,
                "Close": close_prices,
                "Volume": volumes,
            },
            index=dates,
        )

    def test_moving_averages_calculation(self, sample_data):
        """移動平均線計算のテスト"""
        config = ConfigManager("nonexistent.yaml")
        result = TechnicalIndicators.calculate_moving_averages(sample_data, config)

        # 計算結果の確認
        assert "EMA20" in result.columns
        assert "EMA50" in result.columns
        assert "SMA200" in result.columns

        # 最初の期間はNaNになることを確認
        assert pd.isna(result["SMA200"].iloc[0])

        # 最後の方はNaNでないことを確認
        assert not pd.isna(result["EMA20"].iloc[-1])

    def test_rsi_calculation(self, sample_data):
        """RSI計算のテスト"""
        rsi = TechnicalIndicators.calculate_rsi(sample_data, period=14)

        # RSIの値域テスト（0-100）
        valid_rsi = rsi.dropna()
        assert all(valid_rsi >= 0)
        assert all(valid_rsi <= 100)

        # 最初の期間はNaNになることを確認
        assert pd.isna(rsi.iloc[0])

    def test_bollinger_bands_calculation(self, sample_data):
        """ボリンジャーバンド計算のテスト"""
        bb = TechnicalIndicators.calculate_bollinger_bands(
            sample_data, period=20, std_dev=2
        )

        # 必要なキーが存在することを確認
        expected_keys = ["BB_middle", "BB_upper", "BB_lower", "BB_std"]
        for key in expected_keys:
            assert key in bb

        # 上限 > 中央 > 下限の関係を確認（NaNでない部分）
        valid_indices = bb["BB_middle"].dropna().index
        for idx in valid_indices[-10:]:  # 最後の10データで確認
            assert bb["BB_upper"][idx] > bb["BB_middle"][idx]
            assert bb["BB_middle"][idx] > bb["BB_lower"][idx]

    def test_atr_calculation(self, sample_data):
        """ATR計算のテスト"""
        atr = TechnicalIndicators.calculate_atr(sample_data, period=14)

        # ATRは正の値であることを確認
        valid_atr = atr.dropna()
        assert all(valid_atr >= 0)

        # 最初の期間はNaNになることを確認
        assert pd.isna(atr.iloc[0])


class TestStockDataManager:
    """StockDataManagerのテスト"""

    @pytest.fixture
    def mock_config(self):
        """モック設定"""
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            "data.default_period_days": 365,
            "data.buffer_multiplier": 1.5,
            "data.min_trading_days": 250,
            "technical.ema_short": 20,
            "technical.ema_long": 50,
            "technical.sma_long": 200,
            "technical.rsi_period": 14,
            "technical.bb_period": 20,
            "technical.bb_std_dev": 2,
            "technical.atr_period": 14,
            "logging.level": "INFO",
            "logging.format": "%(asctime)s - %(message)s",
        }.get(key, default)
        return config

    @patch("stock_analyzer_lib.yf.Ticker")
    def test_successful_data_fetch(self, mock_ticker, mock_config):
        """正常なデータ取得のテスト"""
        # モックデータの設定
        mock_stock = Mock()
        mock_df = pd.DataFrame(
            {
                "Open": [100, 101, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [103, 104, 105],
                "Volume": [1000000, 1100000, 1200000],
            }
        )
        mock_stock.history.return_value = mock_df
        mock_ticker.return_value = mock_stock

        manager = StockDataManager(mock_config)
        success, df, message = manager.fetch_stock_data("AAPL")

        assert success is True
        assert not df.empty
        assert message == "データ取得成功"

    @patch("stock_analyzer_lib.yf.Ticker")
    def test_invalid_ticker(self, mock_ticker, mock_config):
        """無効なティッカーのテスト"""
        mock_stock = Mock()
        mock_stock.history.return_value = pd.DataFrame()  # 空のDataFrame
        mock_stock.info = {}  # 空のinfo
        mock_ticker.return_value = mock_stock

        manager = StockDataManager(mock_config)
        success, df, message = manager.fetch_stock_data("INVALID")

        assert success is False
        assert df.empty
        assert "有効な米国株ティッカーではありません" in message


class TestChartGenerator:
    """ChartGeneratorのテスト"""

    @pytest.fixture
    def sample_data_with_indicators(self):
        """テクニカル指標付きのサンプルデータ"""
        dates = pd.date_range("2023-01-01", periods=50, freq="D")
        np.random.seed(42)

        data = pd.DataFrame(
            {
                "Open": 100 + np.random.randn(50),
                "High": 102 + np.random.randn(50),
                "Low": 98 + np.random.randn(50),
                "Close": 100 + np.random.randn(50),
                "Volume": abs(np.random.randn(50) * 1000000),
                "EMA20": 100 + np.random.randn(50) * 0.5,
                "EMA50": 100 + np.random.randn(50) * 0.3,
                "SMA200": 100 + np.random.randn(50) * 0.2,
            },
            index=dates,
        )

        return data

    def test_chart_creation(self, sample_data_with_indicators):
        """チャート作成のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # モック設定
            config = Mock()
            config.get.side_effect = lambda key, default=None: {
                "directories.charts": temp_dir,
                "naming.chart_pattern": "{ticker}_chart_{date}.png",
                "chart.figure_size": [16, 9],
                "chart.dpi": 100,
                "chart.panel_ratios": [3, 1],
                "chart.colors": {
                    "up_candle": "green",
                    "down_candle": "red",
                    "ema_short": "blue",
                    "ema_long": "orange",
                    "sma_long": "purple",
                },
            }.get(key, default)

            generator = ChartGenerator(config)
            success, result = generator.create_chart(
                sample_data_with_indicators, "AAPL", "2023-12-31"
            )

            # チャートファイルが作成されることを確認
            # 実際のチャート生成はmplfinanceに依存するため、
            # エラーが発生しないことを確認
            assert isinstance(success, bool)
            assert isinstance(result, str)


class TestStockAnalyzer:
    """StockAnalyzerの統合テスト"""

    def test_analyzer_initialization(self):
        """アナライザーの初期化テスト"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
data:
  default_period_days: 365
technical:
  ema_short: 20
"""
            )
            config_path = f.name

        try:
            analyzer = StockAnalyzer(config_path)
            assert analyzer.config is not None
            assert analyzer.data_manager is not None
            assert analyzer.chart_generator is not None
        finally:
            os.unlink(config_path)


# パフォーマンステスト
class TestPerformance:
    """パフォーマンステスト"""

    def test_large_dataset_processing(self):
        """大量データの処理速度テスト"""
        # 1年分のデータを模擬
        dates = pd.date_range("2023-01-01", periods=365, freq="D")
        np.random.seed(42)

        data = pd.DataFrame(
            {
                "Open": 100 + np.cumsum(np.random.randn(365) * 0.01),
                "High": 100 + np.cumsum(np.random.randn(365) * 0.01) + 1,
                "Low": 100 + np.cumsum(np.random.randn(365) * 0.01) - 1,
                "Close": 100 + np.cumsum(np.random.randn(365) * 0.01),
                "Volume": abs(np.random.randn(365) * 1000000),
            },
            index=dates,
        )

        config = ConfigManager("nonexistent.yaml")

        import time

        start_time = time.time()

        # テクニカル指標計算
        result = TechnicalIndicators.calculate_moving_averages(data, config)
        result["RSI"] = TechnicalIndicators.calculate_rsi(data)

        end_time = time.time()
        processing_time = end_time - start_time

        # 1秒以内で処理されることを確認（合理的な処理速度）
        assert processing_time < 1.0
        assert len(result) == 365


# エラーハンドリングテスト
class TestErrorHandling:
    """エラーハンドリングのテスト"""

    def test_empty_dataframe_handling(self):
        """空のDataFrameの処理テスト"""
        empty_df = pd.DataFrame()
        config = ConfigManager("nonexistent.yaml")

        # エラーが発生せずに空のDataFrameが返されることを確認
        try:
            result = TechnicalIndicators.calculate_moving_averages(empty_df, config)
            assert result.empty
        except Exception as e:
            # 予期されるエラーの場合はテスト通過
            assert isinstance(e, (KeyError, ValueError))

    def test_insufficient_data_handling(self):
        """データ不足時の処理テスト"""
        # 5日分のデータ（移動平均計算には不十分）
        dates = pd.date_range("2023-01-01", periods=5, freq="D")
        data = pd.DataFrame(
            {
                "Open": [100, 101, 102, 103, 104],
                "High": [105, 106, 107, 108, 109],
                "Low": [95, 96, 97, 98, 99],
                "Close": [103, 104, 105, 106, 107],
                "Volume": [1000000, 1100000, 1200000, 1300000, 1400000],
            },
            index=dates,
        )

        config = ConfigManager("nonexistent.yaml")
        result = TechnicalIndicators.calculate_moving_averages(data, config)

        # SMA200は計算できないため、すべてNaN
        assert result["SMA200"].isna().all()

        # EMA20は計算できるはず
        assert not result["EMA20"].isna().all()


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])
