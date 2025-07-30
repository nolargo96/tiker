#!/usr/bin/env python3
"""
ポートフォリオ銘柄管理ツール
銘柄の追加・削除・編集を簡単に行うためのインタラクティブツール
"""

import json
import os
import sys
from typing import Dict, List, Optional
import yfinance as yf
from datetime import datetime
import re


class PortfolioManager:
    """ポートフォリオ銘柄を管理するクラス"""
    
    def __init__(self):
        self.portfolio_file = "src/portfolio/portfolio_config.json"
        self.portfolio = self.load_portfolio()
        
        # デフォルトのカラーパレット
        self.color_palette = [
            "#e31837", "#ffd700", "#ff6b35", "#4a90e2", "#50c878",
            "#9b59b6", "#1abc9c", "#34495e", "#e74c3c", "#f39c12",
            "#3498db", "#2ecc71", "#e67e22", "#16a085", "#8e44ad"
        ]
        
    def load_portfolio(self) -> Dict:
        """ポートフォリオ設定を読み込み"""
        # 既存のコードから現在の設定を取得
        default_portfolio = {
            "TSLA": {"weight": 20, "name": "Tesla", "sector": "EV・自動運転", "color": "#e31837"},
            "FSLR": {"weight": 20, "name": "First Solar", "sector": "ソーラーパネル", "color": "#ffd700"},
            "RKLB": {"weight": 10, "name": "Rocket Lab", "sector": "小型ロケット", "color": "#ff6b35"},
            "ASTS": {"weight": 10, "name": "AST SpaceMobile", "sector": "衛星通信", "color": "#4a90e2"},
            "OKLO": {"weight": 10, "name": "Oklo", "sector": "SMR原子炉", "color": "#50c878"},
            "JOBY": {"weight": 10, "name": "Joby Aviation", "sector": "eVTOL", "color": "#9b59b6"},
            "OII": {"weight": 10, "name": "Oceaneering", "sector": "海洋エンジニアリング", "color": "#1abc9c"},
            "LUNR": {"weight": 5, "name": "Intuitive Machines", "sector": "月面探査", "color": "#34495e"},
            "RDW": {"weight": 5, "name": "Redwire", "sector": "宇宙製造", "color": "#e74c3c"}
        }
        
        # JSONファイルが存在する場合は読み込み
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_portfolio
        return default_portfolio
    
    def save_portfolio(self):
        """ポートフォリオ設定を保存"""
        os.makedirs(os.path.dirname(self.portfolio_file), exist_ok=True)
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, ensure_ascii=False, indent=2)
        print(f"\n✅ ポートフォリオ設定を保存しました: {self.portfolio_file}")
        
        # portfolio_master_report_hybrid.pyも更新
        self.update_source_file()
    
    def update_source_file(self):
        """ソースコードのポートフォリオ定義を更新"""
        source_file = "src/portfolio/portfolio_master_report_hybrid.py"
        
        # ポートフォリオ定義を生成
        portfolio_code = "        self.portfolio = {\n"
        for ticker, info in self.portfolio.items():
            portfolio_code += f'            "{ticker}": {{"weight": {info["weight"]}, "name": "{info["name"]}", "sector": "{info["sector"]}", "color": "{info["color"]}"}},\n'
        portfolio_code = portfolio_code.rstrip(",\n") + "\n        }"
        
        # ファイルを読み込み
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # ポートフォリオ定義部分を置換
        pattern = r'self\.portfolio = \{[^}]+\}'
        content = re.sub(pattern, portfolio_code, content, flags=re.DOTALL)
        
        # ファイルを保存
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ ソースファイルを更新しました: {source_file}")
    
    def validate_ticker(self, ticker: str) -> bool:
        """ティッカーシンボルが有効かチェック"""
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            return 'regularMarketPrice' in info or 'currentPrice' in info
        except:
            return False
    
    def get_stock_info(self, ticker: str) -> Optional[Dict]:
        """株式情報を取得"""
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            return {
                'name': info.get('longName', info.get('shortName', ticker)),
                'sector': info.get('sector', '不明'),
                'current_price': info.get('regularMarketPrice', info.get('currentPrice', 0))
            }
        except:
            return None
    
    def display_portfolio(self):
        """現在のポートフォリオを表示"""
        print("\n📊 現在のポートフォリオ構成")
        print("=" * 80)
        print(f"{'ティッカー':^10} | {'会社名':^25} | {'セクター':^20} | {'配分':^8} | {'色':^8}")
        print("-" * 80)
        
        total_weight = 0
        for ticker, info in sorted(self.portfolio.items()):
            total_weight += info['weight']
            print(f"{ticker:^10} | {info['name']:<25} | {info['sector']:<20} | {info['weight']:>6}% | {info['color']:^8}")
        
        print("-" * 80)
        print(f"{'合計':>58} | {total_weight:>6}%")
        
        if total_weight != 100:
            print(f"\n⚠️  警告: 配分の合計が100%ではありません（現在: {total_weight}%）")
    
    def add_stock(self):
        """銘柄を追加"""
        print("\n➕ 銘柄追加")
        
        # ティッカー入力
        while True:
            ticker = input("ティッカーシンボル (例: AAPL): ").upper().strip()
            if not ticker:
                return
                
            if ticker in self.portfolio:
                print(f"❌ {ticker} は既にポートフォリオに存在します")
                continue
                
            print(f"🔍 {ticker} の情報を確認中...")
            if self.validate_ticker(ticker):
                break
            else:
                print(f"❌ {ticker} は有効なティッカーシンボルではありません")
        
        # 株式情報を取得
        stock_info = self.get_stock_info(ticker)
        if stock_info:
            print(f"✅ 会社名: {stock_info['name']}")
            print(f"✅ セクター: {stock_info['sector']}")
            print(f"✅ 現在価格: ${stock_info['current_price']:.2f}")
            
            # 情報を使用するか確認
            use_info = input("\nこの情報を使用しますか? (Y/n): ").lower()
            if use_info != 'n':
                name = stock_info['name']
                sector = stock_info['sector']
            else:
                name = input("会社名: ").strip()
                sector = input("セクター: ").strip()
        else:
            name = input("会社名: ").strip()
            sector = input("セクター: ").strip()
        
        # 配分入力
        while True:
            try:
                weight = float(input("配分 (%): "))
                if 0 < weight <= 100:
                    break
                print("❌ 配分は0-100の範囲で入力してください")
            except ValueError:
                print("❌ 数値を入力してください")
        
        # 色を自動割り当て
        used_colors = [info['color'] for info in self.portfolio.values()]
        available_colors = [c for c in self.color_palette if c not in used_colors]
        color = available_colors[0] if available_colors else self.color_palette[len(self.portfolio) % len(self.color_palette)]
        
        # 追加
        self.portfolio[ticker] = {
            "weight": weight,
            "name": name,
            "sector": sector,
            "color": color
        }
        
        print(f"\n✅ {ticker} を追加しました")
        self.save_portfolio()
    
    def remove_stock(self):
        """銘柄を削除"""
        print("\n➖ 銘柄削除")
        self.display_portfolio()
        
        ticker = input("\n削除するティッカーシンボル: ").upper().strip()
        if ticker in self.portfolio:
            confirm = input(f"{ticker} ({self.portfolio[ticker]['name']}) を削除しますか? (y/N): ").lower()
            if confirm == 'y':
                del self.portfolio[ticker]
                print(f"✅ {ticker} を削除しました")
                self.save_portfolio()
        else:
            print(f"❌ {ticker} はポートフォリオに存在しません")
    
    def adjust_weights(self):
        """配分を調整"""
        print("\n⚖️  配分調整")
        self.display_portfolio()
        
        # 現在の合計を計算
        total_weight = sum(info['weight'] for info in self.portfolio.values())
        
        if total_weight == 100:
            print("\n✅ 現在の配分は100%です")
            return
        
        print(f"\n現在の合計: {total_weight}%")
        print("\n調整方法を選択してください:")
        print("1. 均等に調整")
        print("2. 比率を保って調整")
        print("3. 手動で調整")
        
        choice = input("\n選択 (1-3): ").strip()
        
        if choice == '1':
            # 均等に調整
            equal_weight = 100 / len(self.portfolio)
            for ticker in self.portfolio:
                self.portfolio[ticker]['weight'] = round(equal_weight, 2)
            print("✅ 均等に調整しました")
            
        elif choice == '2':
            # 比率を保って調整
            if total_weight > 0:
                ratio = 100 / total_weight
                for ticker in self.portfolio:
                    self.portfolio[ticker]['weight'] = round(self.portfolio[ticker]['weight'] * ratio, 2)
                print("✅ 比率を保って調整しました")
            
        elif choice == '3':
            # 手動で調整
            for ticker, info in self.portfolio.items():
                current = info['weight']
                new_weight = input(f"{ticker} (現在: {current}%): ").strip()
                if new_weight:
                    try:
                        self.portfolio[ticker]['weight'] = float(new_weight)
                    except ValueError:
                        print(f"❌ 無効な値: {new_weight}")
        
        self.save_portfolio()
        self.display_portfolio()
    
    def interactive_menu(self):
        """インタラクティブメニュー"""
        while True:
            print("\n" + "=" * 50)
            print("📈 ポートフォリオ管理ツール")
            print("=" * 50)
            
            print("\n1. 現在のポートフォリオを表示")
            print("2. 銘柄を追加")
            print("3. 銘柄を削除")
            print("4. 配分を調整")
            print("5. レポートを生成")
            print("0. 終了")
            
            choice = input("\n選択してください (0-5): ").strip()
            
            if choice == '0':
                print("\n👋 終了します")
                break
            elif choice == '1':
                self.display_portfolio()
            elif choice == '2':
                self.add_stock()
            elif choice == '3':
                self.remove_stock()
            elif choice == '4':
                self.adjust_weights()
            elif choice == '5':
                print("\n🚀 レポート生成中...")
                os.system("source venv/bin/activate && export PYTHONPATH=/mnt/c/Users/nolar/OneDrive/ドキュメント/code/my_dev_projects/tiker && python src/portfolio/portfolio_master_report_hybrid.py")
            else:
                print("❌ 無効な選択です")


def main():
    """メイン関数"""
    manager = PortfolioManager()
    
    # コマンドライン引数がある場合
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'list':
            manager.display_portfolio()
        elif command == 'add' and len(sys.argv) >= 5:
            ticker = sys.argv[2].upper()
            name = sys.argv[3]
            sector = sys.argv[4]
            weight = float(sys.argv[5]) if len(sys.argv) > 5 else 10
            
            # 色を自動割り当て
            used_colors = [info['color'] for info in manager.portfolio.values()]
            available_colors = [c for c in manager.color_palette if c not in used_colors]
            color = available_colors[0] if available_colors else manager.color_palette[len(manager.portfolio) % len(manager.color_palette)]
            
            manager.portfolio[ticker] = {
                "weight": weight,
                "name": name,
                "sector": sector,
                "color": color
            }
            manager.save_portfolio()
            print(f"✅ {ticker} を追加しました")
            
        elif command == 'remove' and len(sys.argv) >= 3:
            ticker = sys.argv[2].upper()
            if ticker in manager.portfolio:
                del manager.portfolio[ticker]
                manager.save_portfolio()
                print(f"✅ {ticker} を削除しました")
            else:
                print(f"❌ {ticker} は存在しません")
        else:
            print("使用方法:")
            print("  python portfolio_manager.py          # インタラクティブモード")
            print("  python portfolio_manager.py list     # 一覧表示")
            print("  python portfolio_manager.py add TICKER \"会社名\" \"セクター\" [配分]")
            print("  python portfolio_manager.py remove TICKER")
    else:
        # インタラクティブモード
        manager.interactive_menu()


if __name__ == "__main__":
    main()