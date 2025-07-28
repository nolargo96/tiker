#!/usr/bin/env python3
"""
シグナル履歴トラッカー
エントリーシグナルの履歴を追跡し、精度を分析するモジュール
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf
from pathlib import Path

class SignalHistoryTracker:
    """シグナル履歴追跡クラス"""
    
    def __init__(self, history_file: str = "signal_history.json"):
        self.history_file = Path(history_file)
        self.history = self._load_history()
        
    def _load_history(self) -> Dict:
        """履歴ファイルを読み込む"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_history(self):
        """履歴をファイルに保存"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2, default=str)
    
    def record_signal(self, ticker: str, signal: str, score: float, 
                     price: float, metadata: Optional[Dict] = None):
        """新しいシグナルを記録"""
        if ticker not in self.history:
            self.history[ticker] = []
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'signal': signal,
            'score': score,
            'price': price,
            'metadata': metadata or {}
        }
        
        self.history[ticker].append(record)
        
        # 最新100件のみ保持
        self.history[ticker] = self.history[ticker][-100:]
        
        self._save_history()
    
    def update_performance(self, ticker: str, days: List[int] = [1, 7, 30]):
        """過去のシグナルのパフォーマンスを更新"""
        if ticker not in self.history:
            return
        
        # 現在の価格を取得
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.history(period="1d")['Close'].iloc[-1]
        except:
            return
        
        # 各レコードのパフォーマンスを更新
        for record in self.history[ticker]:
            timestamp = datetime.fromisoformat(record['timestamp'])
            days_passed = (datetime.now() - timestamp).days
            
            # 指定された期間のパフォーマンスを計算
            for day in days:
                if days_passed >= day and f'performance_{day}d' not in record:
                    original_price = record['price']
                    performance = ((current_price - original_price) / original_price) * 100
                    record[f'performance_{day}d'] = performance
        
        self._save_history()
    
    def calculate_signal_accuracy(self, signal_types: List[str]) -> Dict:
        """シグナルタイプごとの精度を計算"""
        accuracy_stats = {signal: {
            'total': 0,
            'correct': 0,
            'avg_return': 0,
            'win_rate': 0
        } for signal in signal_types}
        
        all_returns = {signal: [] for signal in signal_types}
        
        for ticker, records in self.history.items():
            for record in records:
                signal = record['signal']
                if signal not in signal_types:
                    continue
                
                # 7日後のパフォーマンスで判定
                if 'performance_7d' in record:
                    perf = record['performance_7d']
                    accuracy_stats[signal]['total'] += 1
                    all_returns[signal].append(perf)
                    
                    # 成功判定
                    if signal in ['STRONG_BUY', 'BUY'] and perf > 0:
                        accuracy_stats[signal]['correct'] += 1
                    elif signal in ['SELL', 'STRONG_SELL'] and perf < 0:
                        accuracy_stats[signal]['correct'] += 1
                    elif signal == 'HOLD' and -2 < perf < 2:
                        accuracy_stats[signal]['correct'] += 1
        
        # 統計を計算
        for signal in signal_types:
            stats = accuracy_stats[signal]
            returns = all_returns[signal]
            
            if stats['total'] > 0:
                stats['accuracy'] = stats['correct'] / stats['total']
                stats['avg_return'] = np.mean(returns) if returns else 0
                stats['win_rate'] = len([r for r in returns if r > 0]) / len(returns) if returns else 0
        
        return accuracy_stats
    
    def get_signal_history(self, ticker: str, limit: Optional[int] = None) -> List[Dict]:
        """特定銘柄のシグナル履歴を取得"""
        if ticker not in self.history:
            return []
        
        history = self.history[ticker]
        if limit:
            return history[-limit:]
        return history
    
    def get_signal_transitions(self, ticker: str) -> List[Dict]:
        """シグナルの遷移を分析"""
        history = self.get_signal_history(ticker)
        if len(history) < 2:
            return []
        
        transitions = []
        for i in range(1, len(history)):
            prev = history[i-1]
            curr = history[i]
            
            if prev['signal'] != curr['signal']:
                transitions.append({
                    'timestamp': curr['timestamp'],
                    'from_signal': prev['signal'],
                    'to_signal': curr['signal'],
                    'price_change': curr['price'] - prev['price'],
                    'score_change': curr['score'] - prev['score']
                })
        
        return transitions
    
    def generate_accuracy_report(self) -> pd.DataFrame:
        """精度レポートを生成"""
        signal_types = ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL']
        accuracy_stats = self.calculate_signal_accuracy(signal_types)
        
        report_data = []
        for signal, stats in accuracy_stats.items():
            report_data.append({
                'Signal': signal,
                'Total Signals': stats['total'],
                'Correct': stats['correct'],
                'Accuracy %': stats['accuracy'] * 100 if stats['total'] > 0 else 0,
                'Avg Return %': stats['avg_return'],
                'Win Rate %': stats['win_rate'] * 100
            })
        
        return pd.DataFrame(report_data)
    
    def export_history_to_csv(self, output_file: str = "signal_history.csv"):
        """履歴をCSVファイルにエクスポート"""
        all_records = []
        
        for ticker, records in self.history.items():
            for record in records:
                flat_record = {
                    'ticker': ticker,
                    'timestamp': record['timestamp'],
                    'signal': record['signal'],
                    'score': record['score'],
                    'price': record['price']
                }
                
                # パフォーマンスデータを追加
                for key in record:
                    if key.startswith('performance_'):
                        flat_record[key] = record[key]
                
                all_records.append(flat_record)
        
        df = pd.DataFrame(all_records)
        df.to_csv(output_file, index=False)
        return df


# テスト用のメイン関数
if __name__ == "__main__":
    # トラッカーのインスタンス作成
    tracker = SignalHistoryTracker()
    
    # サンプルシグナルの記録
    sample_signals = [
        ('TSLA', 'BUY', 4.2, 250.50),
        ('FSLR', 'STRONG_BUY', 4.5, 89.30),
        ('RKLB', 'HOLD', 3.0, 15.20),
        ('ASTS', 'SELL', 2.1, 8.50)
    ]
    
    for ticker, signal, score, price in sample_signals:
        tracker.record_signal(ticker, signal, score, price)
    
    # パフォーマンス更新（実際の使用時は定期的に実行）
    for ticker, _, _, _ in sample_signals:
        tracker.update_performance(ticker)
    
    # 精度レポート生成
    report = tracker.generate_accuracy_report()
    print("\n=== Signal Accuracy Report ===")
    print(report.to_string(index=False))
    
    # CSVエクスポート
    tracker.export_history_to_csv()
    print("\nHistory exported to signal_history.csv")