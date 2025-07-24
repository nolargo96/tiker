"""
キャッシュ管理システム
株価データや計算結果を効率的にキャッシュして、開発時の待機時間を削減
"""

import os
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
import pandas as pd
from pathlib import Path


class CacheManager:
    """データキャッシュを管理するクラス"""
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        キャッシュマネージャーの初期化
        
        Args:
            cache_dir: キャッシュファイルを保存するディレクトリ
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # キャッシュタイプ別のTTL（秒）
        self.ttl = {
            "market_data": 300,      # 5分 - 市場データ
            "technical": 300,        # 5分 - テクニカル指標
            "fundamental": 86400,    # 1日 - ファンダメンタルデータ
            "portfolio": 604800,     # 1週間 - ポートフォリオ設定
            "expert_template": 2592000,  # 30日 - 専門家テンプレート
            "chart": 3600,          # 1時間 - チャート画像
        }
        
        # メタデータファイル
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """キャッシュメタデータを読み込む"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self) -> None:
        """キャッシュメタデータを保存"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def _get_cache_key(self, data_type: str, identifier: str, params: Optional[Dict] = None) -> str:
        """キャッシュキーを生成"""
        key_parts = [data_type, identifier]
        if params:
            # パラメータをソートしてハッシュ化
            params_str = json.dumps(params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            key_parts.append(params_hash)
        return "_".join(key_parts)
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """キャッシュファイルのパスを取得"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, data_type: str, identifier: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        キャッシュからデータを取得
        
        Args:
            data_type: データタイプ（market_data, technical等）
            identifier: 識別子（ティッカーシンボル等）
            params: 追加パラメータ
            
        Returns:
            キャッシュされたデータ（存在しない場合はNone）
        """
        cache_key = self._get_cache_key(data_type, identifier, params)
        cache_path = self._get_cache_path(cache_key)
        
        # キャッシュファイルが存在しない場合
        if not cache_path.exists():
            return None
        
        # 有効期限をチェック
        if cache_key in self.metadata:
            cached_time = datetime.fromisoformat(self.metadata[cache_key]["timestamp"])
            ttl_seconds = self.ttl.get(data_type, 300)  # デフォルト5分
            
            if datetime.now() - cached_time > timedelta(seconds=ttl_seconds):
                # 期限切れの場合は削除
                self.delete(data_type, identifier, params)
                return None
        
        # データを読み込む
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            return data
        except Exception as e:
            print(f"キャッシュ読み込みエラー: {e}")
            return None
    
    def set(self, data_type: str, identifier: str, data: Any, params: Optional[Dict] = None) -> bool:
        """
        データをキャッシュに保存
        
        Args:
            data_type: データタイプ
            identifier: 識別子
            data: 保存するデータ
            params: 追加パラメータ
            
        Returns:
            保存成功の可否
        """
        cache_key = self._get_cache_key(data_type, identifier, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # データを保存
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            # メタデータを更新
            self.metadata[cache_key] = {
                "timestamp": datetime.now().isoformat(),
                "data_type": data_type,
                "identifier": identifier,
                "params": params
            }
            self._save_metadata()
            
            return True
        except Exception as e:
            print(f"キャッシュ保存エラー: {e}")
            return False
    
    def delete(self, data_type: str, identifier: str, params: Optional[Dict] = None) -> bool:
        """
        キャッシュからデータを削除
        
        Args:
            data_type: データタイプ
            identifier: 識別子
            params: 追加パラメータ
            
        Returns:
            削除成功の可否
        """
        cache_key = self._get_cache_key(data_type, identifier, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            if cache_path.exists():
                cache_path.unlink()
            
            if cache_key in self.metadata:
                del self.metadata[cache_key]
                self._save_metadata()
            
            return True
        except Exception as e:
            print(f"キャッシュ削除エラー: {e}")
            return False
    
    def clear_all(self) -> None:
        """すべてのキャッシュをクリア"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        
        self.metadata = {}
        self._save_metadata()
    
    def clear_expired(self) -> int:
        """期限切れのキャッシュをクリア"""
        deleted_count = 0
        
        for cache_key, meta in list(self.metadata.items()):
            cached_time = datetime.fromisoformat(meta["timestamp"])
            data_type = meta["data_type"]
            ttl_seconds = self.ttl.get(data_type, 300)
            
            if datetime.now() - cached_time > timedelta(seconds=ttl_seconds):
                cache_path = self._get_cache_path(cache_key)
                if cache_path.exists():
                    cache_path.unlink()
                del self.metadata[cache_key]
                deleted_count += 1
        
        if deleted_count > 0:
            self._save_metadata()
        
        return deleted_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュの統計情報を取得"""
        stats = {
            "total_items": len(self.metadata),
            "by_type": {},
            "total_size_mb": 0,
            "oldest_item": None,
            "newest_item": None
        }
        
        # タイプ別の集計
        for meta in self.metadata.values():
            data_type = meta["data_type"]
            stats["by_type"][data_type] = stats["by_type"].get(data_type, 0) + 1
        
        # ファイルサイズの集計
        for cache_file in self.cache_dir.glob("*.pkl"):
            stats["total_size_mb"] += cache_file.stat().st_size / (1024 * 1024)
        
        # 最古・最新のアイテム
        if self.metadata:
            timestamps = [datetime.fromisoformat(m["timestamp"]) for m in self.metadata.values()]
            stats["oldest_item"] = min(timestamps).isoformat()
            stats["newest_item"] = max(timestamps).isoformat()
        
        return stats


# 株価データ専用のヘルパー関数
def cache_stock_data(cache_manager: CacheManager, ticker: str, df: pd.DataFrame, 
                    period_days: int) -> bool:
    """株価データをキャッシュ"""
    params = {"period_days": period_days}
    return cache_manager.set("market_data", ticker, df, params)


def get_cached_stock_data(cache_manager: CacheManager, ticker: str, 
                         period_days: int) -> Optional[pd.DataFrame]:
    """キャッシュから株価データを取得"""
    params = {"period_days": period_days}
    return cache_manager.get("market_data", ticker, params)


# テクニカル指標専用のヘルパー関数
def cache_technical_indicators(cache_manager: CacheManager, ticker: str, 
                             indicators: Dict[str, pd.Series]) -> bool:
    """テクニカル指標をキャッシュ"""
    return cache_manager.set("technical", ticker, indicators)


def get_cached_technical_indicators(cache_manager: CacheManager, 
                                  ticker: str) -> Optional[Dict[str, pd.Series]]:
    """キャッシュからテクニカル指標を取得"""
    return cache_manager.get("technical", ticker)