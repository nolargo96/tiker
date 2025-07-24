"""
キャッシュマネージャーのテストスイート
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import time
from src.data.cache_manager import CacheManager, cache_stock_data, get_cached_stock_data


class TestCacheManager:
    """CacheManagerのテストクラス"""
    
    @pytest.fixture
    def cache_manager(self, tmp_path):
        """テスト用のキャッシュマネージャーを作成"""
        cache_dir = tmp_path / "test_cache"
        return CacheManager(str(cache_dir))
    
    @pytest.fixture
    def sample_stock_data(self):
        """テスト用の株価データを作成"""
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
        data = {
            'Open': np.random.uniform(100, 200, 365),
            'High': np.random.uniform(100, 200, 365),
            'Low': np.random.uniform(100, 200, 365),
            'Close': np.random.uniform(100, 200, 365),
            'Volume': np.random.randint(1000000, 10000000, 365)
        }
        return pd.DataFrame(data, index=dates)
    
    def test_cache_initialization(self, cache_manager):
        """キャッシュマネージャーの初期化テスト"""
        assert Path(cache_manager.cache_dir).exists()
        assert cache_manager.metadata == {}
        assert "market_data" in cache_manager.ttl
    
    def test_set_and_get_data(self, cache_manager):
        """データの保存と取得のテスト"""
        test_data = {"test": "data", "number": 123}
        
        # データを保存
        success = cache_manager.set("test_type", "test_id", test_data)
        assert success is True
        
        # データを取得
        retrieved_data = cache_manager.get("test_type", "test_id")
        assert retrieved_data == test_data
    
    def test_cache_expiration(self, cache_manager):
        """キャッシュ期限切れのテスト"""
        # TTLを短く設定
        cache_manager.ttl["test_type"] = 0.1  # 0.1秒
        
        # データを保存
        cache_manager.set("test_type", "expire_test", {"data": "test"})
        
        # すぐに取得（有効期限内）
        assert cache_manager.get("test_type", "expire_test") is not None
        
        # 期限切れ後に取得
        time.sleep(0.2)
        assert cache_manager.get("test_type", "expire_test") is None
    
    def test_stock_data_caching(self, cache_manager, sample_stock_data):
        """株価データ専用関数のテスト"""
        ticker = "AAPL"
        period_days = 365
        
        # キャッシュに保存
        success = cache_stock_data(cache_manager, ticker, sample_stock_data, period_days)
        assert success is True
        
        # キャッシュから取得
        cached_df = get_cached_stock_data(cache_manager, ticker, period_days)
        assert cached_df is not None
        pd.testing.assert_frame_equal(cached_df, sample_stock_data)
    
    def test_cache_with_different_params(self, cache_manager):
        """異なるパラメータでのキャッシュテスト"""
        ticker = "TSLA"
        data1 = pd.DataFrame({"Close": [100, 101, 102]})
        data2 = pd.DataFrame({"Close": [200, 201, 202]})
        
        # 異なる期間でキャッシュ
        cache_stock_data(cache_manager, ticker, data1, 30)
        cache_stock_data(cache_manager, ticker, data2, 60)
        
        # それぞれ正しく取得できることを確認
        assert len(get_cached_stock_data(cache_manager, ticker, 30)) == 3
        assert len(get_cached_stock_data(cache_manager, ticker, 60)) == 3
        assert get_cached_stock_data(cache_manager, ticker, 30)["Close"][0] == 100
        assert get_cached_stock_data(cache_manager, ticker, 60)["Close"][0] == 200
    
    def test_cache_deletion(self, cache_manager):
        """キャッシュ削除のテスト"""
        # データを保存
        cache_manager.set("test_type", "delete_test", {"data": "test"})
        assert cache_manager.get("test_type", "delete_test") is not None
        
        # 削除
        success = cache_manager.delete("test_type", "delete_test")
        assert success is True
        
        # 削除後は取得できない
        assert cache_manager.get("test_type", "delete_test") is None
    
    def test_clear_expired(self, cache_manager):
        """期限切れキャッシュのクリアテスト"""
        # 異なるTTLでデータを保存
        cache_manager.ttl["short_ttl"] = 0.1
        cache_manager.ttl["long_ttl"] = 3600
        
        cache_manager.set("short_ttl", "item1", {"data": 1})
        cache_manager.set("long_ttl", "item2", {"data": 2})
        
        # 短いTTLのデータが期限切れになるまで待つ
        time.sleep(0.2)
        
        # 期限切れをクリア
        deleted_count = cache_manager.clear_expired()
        assert deleted_count == 1
        
        # 長いTTLのデータは残っている
        assert cache_manager.get("long_ttl", "item2") is not None
    
    def test_cache_stats(self, cache_manager, sample_stock_data):
        """キャッシュ統計情報のテスト"""
        # 複数のデータを保存
        cache_stock_data(cache_manager, "AAPL", sample_stock_data, 365)
        cache_stock_data(cache_manager, "TSLA", sample_stock_data, 365)
        cache_manager.set("technical", "RSI_AAPL", {"RSI": 50})
        
        # 統計情報を取得
        stats = cache_manager.get_cache_stats()
        
        assert stats["total_items"] == 3
        assert stats["by_type"]["market_data"] == 2
        assert stats["by_type"]["technical"] == 1
        assert stats["total_size_mb"] > 0
        assert stats["oldest_item"] is not None
        assert stats["newest_item"] is not None
    
    def test_clear_all(self, cache_manager):
        """全キャッシュクリアのテスト"""
        # 複数のデータを保存
        cache_manager.set("type1", "id1", {"data": 1})
        cache_manager.set("type2", "id2", {"data": 2})
        
        # 全クリア
        cache_manager.clear_all()
        
        # すべてのデータが削除されている
        assert cache_manager.get("type1", "id1") is None
        assert cache_manager.get("type2", "id2") is None
        assert cache_manager.metadata == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])