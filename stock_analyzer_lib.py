"""
Stock Analyzer Library
共通ライブラリ - 株式分析機能の統合

このライブラリは、tikerプロジェクトの共通機能を提供します：
- 株価データ取得
- テクニカル指標計算
- チャート生成
- 設定管理
"""

import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np
import os
import yaml
import logging
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional, Any
import warnings

warnings.filterwarnings("ignore")


def setup_logging(config_path: str = "config.yaml") -> logging.Logger:
    """
    統一ログ設定の初期化

    Args:
        config_path (str): 設定ファイルのパス

    Returns:
        logging.Logger: 設定済みのロガー
    """
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        log_config = config.get("logging", {})
        log_level = getattr(logging, log_config.get("level", "INFO"))
        log_format = log_config.get(
            "format", "%(asctime)s - %(levelname)s - %(message)s"
        )
        log_file = log_config.get("file", "stock_analyzer.log")

        # ログファイルのディレクトリを作成
        log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "."
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        logger = logging.getLogger("tiker")
        logger.info("ログ設定が初期化されました")
        return logger

    except Exception as e:
        # 設定ファイルが読めない場合のフォールバック
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logger = logging.getLogger("tiker")
        logger.warning(f"設定ファイルからのログ設定に失敗: {e}")
        return logger


class ConfigManager:
    """設定管理クラス"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logging.warning(
                f"設定ファイル {self.config_path} が見つかりません。デフォルト設定を使用します。"
            )
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "data": {
                "default_period_days": 365,
                "min_trading_days": 250,
                "buffer_multiplier": 1.5,
            },
            "technical": {
                "ema_short": 20,
                "ema_long": 50,
                "sma_long": 200,
                "rsi_period": 14,
            },
            "chart": {"figure_size": [16, 9], "dpi": 100, "panel_ratios": [3, 1]},
            "directories": {
                "charts": "./charts",
                "data": "./data",
                "reports": "./reports",
            },
            "naming": {
                "chart_pattern": "{ticker}_chart_{date}.png",
                "data_pattern": "{ticker}_analysis_data_{date}.csv",
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


class TechnicalIndicators:
    """テクニカル指標計算クラス"""

    @staticmethod
    def calculate_moving_averages(
        df: pd.DataFrame, config: ConfigManager
    ) -> pd.DataFrame:
        """移動平均線を計算"""
        df_calc = df.copy()

        ema_short = config.get("technical.ema_short", 20)
        ema_long = config.get("technical.ema_long", 50)
        sma_long = config.get("technical.sma_long", 200)

        df_calc["EMA20"] = df_calc["Close"].ewm(span=ema_short, adjust=False).mean()
        df_calc["EMA50"] = df_calc["Close"].ewm(span=ema_long, adjust=False).mean()
        df_calc["SMA200"] = df_calc["Close"].rolling(window=sma_long).mean()

        return df_calc

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """RSIを計算"""
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame, period: int = 20, std_dev: float = 2
    ) -> Dict[str, pd.Series]:
        """ボリンジャーバンドを計算"""
        middle = df["Close"].rolling(window=period).mean()
        std = df["Close"].rolling(window=period).std()

        return {
            "BB_middle": middle,
            "BB_upper": middle + (std * std_dev),
            "BB_lower": middle - (std * std_dev),
            "BB_std": std,
        }

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ATRを計算"""
        tr = np.maximum(
            df["High"] - df["Low"],
            np.maximum(
                abs(df["High"] - df["Close"].shift(1)),
                abs(df["Low"] - df["Close"].shift(1)),
            ),
        )
        return pd.Series(tr).rolling(window=period).mean()


class StockDataManager:
    """株価データ管理クラス"""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.setup_logging()

    def setup_logging(self) -> None:
        """ログ設定"""
        log_level = self.config.get("logging.level", "INFO")
        log_format = self.config.get(
            "logging.format", "%(asctime)s - %(levelname)s - %(message)s"
        )

        logging.basicConfig(level=getattr(logging, log_level), format=log_format)
        self.logger = logging.getLogger(__name__)

    def fetch_stock_data(
        self, ticker: str, days: Optional[int] = None
    ) -> Tuple[bool, pd.DataFrame, str]:
        """株価データを取得"""
        if days is None:
            days = self.config.get("data.default_period_days", 365)

        buffer_multiplier = self.config.get("data.buffer_multiplier", 1.5)
        min_trading_days = self.config.get("data.min_trading_days", 250)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(days * buffer_multiplier))

        self.logger.info(
            f"データ取得: {ticker}, 期間: "
            f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}"
        )

        try:
            stock = yf.Ticker(ticker)
            df = stock.history(
                start=start_date, end=end_date, interval="1d", auto_adjust=False
            )

            if df.empty:
                info = stock.info
                if not info or "regularMarketPrice" not in info:
                    return (
                        False,
                        pd.DataFrame(),
                        f"{ticker} は有効な米国株ティッカーではありません。",
                    )
                else:
                    return (
                        False,
                        pd.DataFrame(),
                        "データが取得できませんでした。データ不足のため簡易分析。",
                    )

            if len(df) < min_trading_days:
                self.logger.warning(
                    f"{ticker} のデータが{min_trading_days}日分ありません。取得: {len(df)}日分"
                )

            return True, df, "データ取得成功"

        except Exception as e:
            self.logger.error(f"データ取得エラー: {str(e)}")
            return False, pd.DataFrame(), f"エラー: {str(e)}"

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """全テクニカル指標を追加"""
        # 移動平均線
        df_with_ma = TechnicalIndicators.calculate_moving_averages(df, self.config)

        # RSI
        rsi_period = self.config.get("technical.rsi_period", 14)
        df_with_ma["RSI"] = TechnicalIndicators.calculate_rsi(df, rsi_period)

        # ボリンジャーバンド
        bb_period = self.config.get("technical.bb_period", 20)
        bb_std = self.config.get("technical.bb_std_dev", 2)
        bb_bands = TechnicalIndicators.calculate_bollinger_bands(df, bb_period, bb_std)
        for key, values in bb_bands.items():
            df_with_ma[key] = values

        # ATR
        atr_period = self.config.get("technical.atr_period", 14)
        df_with_ma["ATR"] = TechnicalIndicators.calculate_atr(df, atr_period)

        return df_with_ma


class ChartGenerator:
    """チャート生成クラス"""

    def __init__(self, config: ConfigManager):
        self.config = config

    def create_chart(
        self, df: pd.DataFrame, ticker: str, date_str: str
    ) -> Tuple[bool, str]:
        """チャートを生成・保存"""
        try:
            # ディレクトリ設定
            chart_dir = self.config.get("directories.charts", "./charts")
            if not os.path.exists(chart_dir):
                os.makedirs(chart_dir)

            # ファイル名生成
            chart_pattern = self.config.get(
                "naming.chart_pattern", "{ticker}_chart_{date}.png"
            )
            chart_filename = chart_pattern.format(ticker=ticker, date=date_str)
            chart_filepath = os.path.join(chart_dir, chart_filename)

            # チャート設定
            figure_size = self.config.get("chart.figure_size", [16, 9])
            dpi = self.config.get("chart.dpi", 100)
            panel_ratios = self.config.get("chart.panel_ratios", [3, 1])

            # カラー設定
            colors = self.config.get("chart.colors", {})
            mc = mpf.make_marketcolors(
                up=colors.get("up_candle", "green"),
                down=colors.get("down_candle", "red"),
                inherit=True,
            )
            style = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=False)

            # 追加プロット
            addplots = [
                mpf.make_addplot(
                    df["EMA20"],
                    color=colors.get("ema_short", "blue"),
                    width=0.7,
                    panel=0,
                ),
                mpf.make_addplot(
                    df["EMA50"],
                    color=colors.get("ema_long", "orange"),
                    width=0.7,
                    panel=0,
                ),
                mpf.make_addplot(
                    df["SMA200"],
                    color=colors.get("sma_long", "purple"),
                    width=0.7,
                    panel=0,
                ),
            ]

            # チャート生成
            mpf.plot(
                df,
                type="candle",
                style=style,
                title=f"{ticker} Daily Chart (1 Year) - Data as of {date_str} JST",
                ylabel="Price (USD)",
                volume=True,
                ylabel_lower="Volume",
                addplot=addplots,
                figsize=figure_size,
                panel_ratios=panel_ratios,
                savefig=dict(fname=chart_filepath, dpi=dpi),
                show_nontrading=False,
                datetime_format="%Y-%m-%d",
            )

            return True, chart_filepath

        except Exception as e:
            return False, f"チャート生成エラー: {str(e)}"


class StockAnalyzer:
    """統合株式分析クラス"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = ConfigManager(config_path)
        self.data_manager = StockDataManager(self.config)
        self.chart_generator = ChartGenerator(self.config)
        self.logger = logging.getLogger(__name__)

    def analyze_stock(
        self, ticker: str, date_str: Optional[str] = None
    ) -> Tuple[bool, str]:
        """統合株式分析を実行"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        self.logger.info(f"=== {ticker} 株価分析開始 ===")
        self.logger.info(f"分析基準日: {date_str}")

        # 1. データ取得
        success, df, message = self.data_manager.fetch_stock_data(ticker)
        if not success:
            return False, message

        # 2. テクニカル指標計算
        df_analysis = self.data_manager.add_technical_indicators(df)

        # 3. チャート生成
        chart_success, chart_result = self.chart_generator.create_chart(
            df_analysis, ticker, date_str
        )
        if not chart_success:
            self.logger.error(chart_result)
        else:
            self.logger.info(f"チャート保存: {chart_result}")

        # 4. データ保存
        data_pattern = self.config.get(
            "naming.data_pattern", "{ticker}_analysis_data_{date}.csv"
        )
        data_filename = data_pattern.format(ticker=ticker, date=date_str)
        df_analysis.to_csv(data_filename)
        self.logger.info(f"データ保存: {data_filename}")

        # 5. 最新データ表示
        self._display_latest_data(df_analysis, ticker)

        return True, "分析完了"

    def _display_latest_data(self, df: pd.DataFrame, ticker: str) -> None:
        """最新データを表示"""
        latest = df.iloc[-1]
        print(f"\n=== {ticker} 最新データ ({df.index[-1].strftime('%Y-%m-%d')}) ===")
        print(f"終値: ${latest['Close']:.2f}")
        print(f"出来高: {latest['Volume']:,.0f}")

        if not pd.isna(latest["EMA20"]):
            print(f"20日EMA: ${latest['EMA20']:.2f}")
        if not pd.isna(latest["EMA50"]):
            print(f"50日EMA: ${latest['EMA50']:.2f}")
        if not pd.isna(latest["SMA200"]):
            print(f"200日SMA: ${latest['SMA200']:.2f}")

        print("\n=== テクニカル指標 ===")
        if not pd.isna(latest["RSI"]):
            print(f"RSI(14): {latest['RSI']:.2f}")
        if not pd.isna(latest["BB_upper"]):
            print(
                f"ボリンジャーバンド: ${latest['BB_lower']:.2f} - ${latest['BB_upper']:.2f}"
            )
        if not pd.isna(latest["ATR"]):
            print(f"ATR(14): ${latest['ATR']:.2f}")


# 使用例
if __name__ == "__main__":
    analyzer = StockAnalyzer()
    success, message = analyzer.analyze_stock("TSLA")
    print(f"結果: {message}")
