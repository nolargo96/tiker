#!/usr/bin/env python3
"""
ポートフォリオアラートシステム
エントリーチャンスや損切りライン接近時の通知機能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json

class PortfolioAlerts:
    def __init__(self):
        # 各銘柄の重要価格レベル（既存分析から）
        self.price_levels = {
            "TSLA": {
                "buy_zones": [(250, 280), (300, 310)],
                "stop_loss": 240,
                "target": 380,
                "support": 300,
                "resistance": 350
            },
            "FSLR": {
                "buy_zones": [(130, 140), (145, 150)],
                "stop_loss": 120,
                "target": 210,
                "support": 138,
                "resistance": 175
            },
            "ASTS": {
                "buy_zones": [(30, 33), (40, 42)],
                "stop_loss": 25,
                "target": 65,
                "support": 28,
                "resistance": 50
            },
            "OKLO": {
                "buy_zones": [(40, 45), (45, 48)],
                "stop_loss": 30,
                "target": 80,
                "support": 45,
                "resistance": 60
            },
            "JOBY": {
                "buy_zones": [(6.50, 7.50), (8.00, 8.50)],
                "stop_loss": 6.50,
                "target": 12,
                "support": 7.30,
                "resistance": 10
            },
            "LUNR": {
                "buy_zones": [(9, 10), (10, 11)],
                "stop_loss": 9,
                "target": 20,
                "support": 9.50,
                "resistance": 15
            },
            "RDW": {
                "buy_zones": [(12.50, 13.50), (14.50, 15.50)],
                "stop_loss": 12,
                "target": 22,
                "support": 12.80,
                "resistance": 18
            },
            "OII": {
                "buy_zones": [(19, 20), (20.50, 21.50)],
                "stop_loss": 18,
                "target": 25,
                "support": 20,
                "resistance": 22
            }
        }
    
    def check_alerts(self, portfolio_config):
        """
        ポートフォリオ全体のアラートをチェック
        
        Args:
            portfolio_config (dict): {"TSLA": 30, "FSLR": 25, ...}
        
        Returns:
            dict: アラート情報
        """
        alerts = {
            "buy_opportunities": [],
            "stop_loss_warnings": [],
            "target_reached": [],
            "breakout_alerts": [],
            "breakdown_alerts": [],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("🔍 ポートフォリオアラートチェック開始...")
        
        for ticker, allocation in portfolio_config.items():
            if ticker not in self.price_levels:
                print(f"⚠️  {ticker}: 価格レベル未設定")
                continue
            
            try:
                # 最新価格取得
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if hist.empty:
                    print(f"❌ {ticker}: データ取得失敗")
                    continue
                
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                levels = self.price_levels[ticker]
                
                # 各種アラートチェック
                ticker_alerts = self._check_ticker_alerts(
                    ticker, current_price, prev_price, change_pct, levels, allocation
                )
                
                # アラートを分類
                for alert in ticker_alerts:
                    alert_type = alert["type"]
                    if alert_type == "buy_opportunity":
                        alerts["buy_opportunities"].append(alert)
                    elif alert_type == "stop_loss_warning":
                        alerts["stop_loss_warnings"].append(alert)
                    elif alert_type == "target_reached":
                        alerts["target_reached"].append(alert)
                    elif alert_type == "breakout":
                        alerts["breakout_alerts"].append(alert)
                    elif alert_type == "breakdown":
                        alerts["breakdown_alerts"].append(alert)
                
            except Exception as e:
                print(f"❌ {ticker}のアラートチェック中にエラー: {e}")
        
        return alerts
    
    def _check_ticker_alerts(self, ticker, current_price, prev_price, change_pct, levels, allocation):
        """個別銘柄のアラートチェック"""
        alerts = []
        
        # 1. 買いゾーンアラート
        for buy_zone in levels["buy_zones"]:
            if buy_zone[0] <= current_price <= buy_zone[1]:
                alerts.append({
                    "type": "buy_opportunity",
                    "ticker": ticker,
                    "allocation": allocation,
                    "message": f"{ticker}: 買いゾーン到達 (${current_price:.2f})",
                    "price": current_price,
                    "zone": buy_zone,
                    "priority": "HIGH" if allocation >= 20 else "MEDIUM"
                })
        
        # 2. 損切りライン警告
        stop_distance = ((current_price - levels["stop_loss"]) / current_price) * 100
        if stop_distance <= 10:  # 損切りラインまで10%以下
            priority = "CRITICAL" if stop_distance <= 5 else "HIGH"
            alerts.append({
                "type": "stop_loss_warning",
                "ticker": ticker,
                "allocation": allocation,
                "message": f"{ticker}: 損切りライン接近 (距離: {stop_distance:.1f}%)",
                "price": current_price,
                "stop_loss": levels["stop_loss"],
                "priority": priority
            })
        
        # 3. 目標価格到達
        if current_price >= levels["target"]:
            alerts.append({
                "type": "target_reached",
                "ticker": ticker,
                "allocation": allocation,
                "message": f"{ticker}: 目標価格到達 (${current_price:.2f})",
                "price": current_price,
                "target": levels["target"],
                "priority": "HIGH"
            })
        
        # 4. レジスタンスブレイクアウト
        if current_price > levels["resistance"] and prev_price <= levels["resistance"]:
            alerts.append({
                "type": "breakout",
                "ticker": ticker,
                "allocation": allocation,
                "message": f"{ticker}: レジスタンス突破 (${current_price:.2f})",
                "price": current_price,
                "resistance": levels["resistance"],
                "priority": "MEDIUM"
            })
        
        # 5. サポートブレイクダウン
        if current_price < levels["support"] and prev_price >= levels["support"]:
            alerts.append({
                "type": "breakdown",
                "ticker": ticker,
                "allocation": allocation,
                "message": f"{ticker}: サポート割れ (${current_price:.2f})",
                "price": current_price,
                "support": levels["support"],
                "priority": "HIGH"
            })
        
        return alerts
    
    def display_alerts(self, alerts):
        """アラートの表示"""
        print("\n" + "=" * 70)
        print("🚨 ポートフォリオアラート レポート")
        print("=" * 70)
        print(f"⏰ 確認時刻: {alerts['timestamp']}")
        
        # 優先度別アラート表示
        all_alerts = []
        for category in ["stop_loss_warnings", "target_reached", "buy_opportunities", "breakout_alerts", "breakdown_alerts"]:
            all_alerts.extend(alerts[category])
        
        if not all_alerts:
            print("\n✅ 現在、重要なアラートはありません")
            return
        
        # 優先度でソート
        priority_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        all_alerts.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        # カテゴリ別表示
        categories = {
            "stop_loss_warnings": ("🔴 損切り警告", "CRITICAL"),
            "target_reached": ("🎯 目標到達", "HIGH"),
            "buy_opportunities": ("🟢 買いチャンス", "MEDIUM"),
            "breakout_alerts": ("📈 ブレイクアウト", "MEDIUM"),
            "breakdown_alerts": ("📉 ブレイクダウン", "HIGH")
        }
        
        for category, (title, _) in categories.items():
            category_alerts = alerts[category]
            if category_alerts:
                print(f"\n{title}:")
                for alert in category_alerts:
                    priority_icon = {"CRITICAL": "🆘", "HIGH": "⚠️", "MEDIUM": "💡", "LOW": "ℹ️"}
                    icon = priority_icon.get(alert["priority"], "ℹ️")
                    print(f"  {icon} {alert['message']} ({alert['allocation']}%配分)")
        
        # サマリー
        print(f"\n📊 アラートサマリー:")
        print(f"  - 緊急: {len([a for a in all_alerts if a['priority'] == 'CRITICAL'])}件")
        print(f"  - 重要: {len([a for a in all_alerts if a['priority'] == 'HIGH'])}件")
        print(f"  - 通常: {len([a for a in all_alerts if a['priority'] == 'MEDIUM'])}件")
        
        print("\n" + "=" * 70)
    
    def save_alerts_history(self, alerts, filename="./data/alerts_history.json"):
        """アラート履歴の保存"""
        try:
            # 既存履歴の読み込み
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            # 新しいアラートを追加
            history.append(alerts)
            
            # 最新30件のみ保持
            history = history[-30:]
            
            # 保存
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            print(f"📝 アラート履歴を保存: {filename}")
        
        except Exception as e:
            print(f"⚠️  履歴保存エラー: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ポートフォリオアラートチェック')
    parser.add_argument('--tickers', type=str, help='チェック対象銘柄 (カンマ区切り)')
    parser.add_argument('--weights', type=str, help='配分比率 (カンマ区切り)')
    parser.add_argument('--save-history', action='store_true', help='アラート履歴を保存')
    
    args = parser.parse_args()
    
    # ポートフォリオ設定
    if args.tickers and args.weights:
        tickers = args.tickers.split(',')
        weights = [float(w) for w in args.weights.split(',')]
        portfolio_config = dict(zip(tickers, weights))
    else:
        # デフォルトポートフォリオ（OII追加版）
        portfolio_config = {
            "TSLA": 25,
            "FSLR": 25,
            "ASTS": 10,
            "OKLO": 10,
            "JOBY": 10,
            "OII": 10,
            "LUNR": 5,
            "RDW": 5
        }
    
    # アラートシステム実行
    alert_system = PortfolioAlerts()
    alerts = alert_system.check_alerts(portfolio_config)
    alert_system.display_alerts(alerts)
    
    if args.save_history:
        alert_system.save_alerts_history(alerts)
    
    print(f"\n💡 定期チェック推奨:")
    print(f"   python scripts/portfolio_alerts.py")
    print(f"   python scripts/portfolio_quick_review.py")

if __name__ == "__main__":
    main()