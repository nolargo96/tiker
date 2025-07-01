"""
Gemini AI Integration for Tiker Stock Analyzer
無料枠内でのGemini CLI連携実装

使用方法:
1. Google AI StudioでAPI Key取得 (無料)
2. export GOOGLE_API_KEY="your-api-key" 
3. python ai_integration.py --ticker TSLA
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import tempfile

class GeminiFreeTierManager:
    """無料枠管理クラス"""
    
    def __init__(self):
        self.daily_limit = 50  # 1日50リクエストに制限（安全マージン）
        self.usage_file = "gemini_usage.json"
        self.usage_data = self._load_usage()
    
    def _load_usage(self) -> Dict[str, Any]:
        """使用量データを読み込み"""
        try:
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"requests": {}, "last_reset": str(datetime.now().date())}
    
    def _save_usage(self):
        """使用量データを保存"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_data, f)
    
    def can_make_request(self) -> bool:
        """リクエスト可能かチェック"""
        today = str(datetime.now().date())
        
        # 日付が変わったらリセット
        if self.usage_data["last_reset"] != today:
            self.usage_data["requests"] = {}
            self.usage_data["last_reset"] = today
        
        today_requests = self.usage_data["requests"].get(today, 0)
        return today_requests < self.daily_limit
    
    def record_request(self):
        """リクエスト使用を記録"""
        today = str(datetime.now().date())
        self.usage_data["requests"][today] = self.usage_data["requests"].get(today, 0) + 1
        self._save_usage()
    
    def get_remaining_requests(self) -> int:
        """残りリクエスト数を取得"""
        today = str(datetime.now().date())
        used = self.usage_data["requests"].get(today, 0)
        return max(0, self.daily_limit - used)

class GeminiCLIConnector:
    """Gemini CLIとの接続クラス"""
    
    def __init__(self):
        self.rate_limiter = GeminiFreeTierManager()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            print("❌ GOOGLE_API_KEY環境変数が設定されていません")
            print("Google AI StudioでAPI Keyを取得し、以下を実行してください:")
            print("export GOOGLE_API_KEY='your-api-key'")
            sys.exit(1)
    
    def generate_content(self, prompt: str) -> Optional[str]:
        """Gemini CLIでコンテンツ生成"""
        
        # 無料枠チェック
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.get_remaining_requests()
            print(f"❌ 本日の無料枠を使い切りました。残り: {remaining}リクエスト")
            return None
        
        try:
            # 一時ファイルにプロンプトを保存
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # Node.js スクリプトを作成して実行
            node_script = f"""
const {{ GoogleGenerativeAI }} = require('@google/generative-ai');

async function generateContent() {{
    const genAI = new GoogleGenerativeAI('{self.api_key}');
    const model = genAI.getGenerativeModel({{ model: 'gemini-1.5-flash' }});
    
    const fs = require('fs');
    const prompt = fs.readFileSync('{prompt_file}', 'utf8');
    
    try {{
        const result = await model.generateContent(prompt);
        const response = await result.response;
        console.log(response.text());
    }} catch (error) {{
        console.error('Error:', error.message);
        process.exit(1);
    }}
}}

generateContent();
"""
            
            # 一時的なNode.jsスクリプトファイル作成
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(node_script)
                script_file = f.name
            
            # Node.jsスクリプト実行
            result = subprocess.run(
                ['node', script_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # クリーンアップ
            os.unlink(prompt_file)
            os.unlink(script_file)
            
            if result.returncode == 0:
                self.rate_limiter.record_request()
                return result.stdout.strip()
            else:
                print(f"❌ Gemini API エラー: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Gemini API タイムアウト（30秒）")
            return None
        except Exception as e:
            print(f"❌ 予期しないエラー: {str(e)}")
            return None

class TikerAIAnalyzer:
    """Tiker + Gemini AI統合分析クラス"""
    
    def __init__(self):
        self.gemini = GeminiCLIConnector()
        
        # 既存のtiker分析ライブラリがあるかチェック
        try:
            from stock_analyzer_lib import StockAnalyzer
            self.stock_analyzer = StockAnalyzer()
            self.has_stock_lib = True
        except ImportError:
            print("📌 stock_analyzer_lib.pyが見つかりません。基本分析のみ実行します。")
            self.has_stock_lib = False
    
    def create_focused_prompt(self, ticker: str, basic_data: Dict[str, Any]) -> str:
        """コスト効率的な短いプロンプトを作成"""
        
        # 簡潔なプロンプト（トークン数を抑制）
        prompt = f"""株式分析: {ticker}
データ: 価格${basic_data.get('price', 'N/A')}, RSI:{basic_data.get('rsi', 'N/A')}

以下形式で簡潔に回答（100語以内）:
1. テクニカル評価: [買い/中立/売り]
2. 理由: [1文]
3. リスク: [1文]"""
        
        return prompt
    
    def get_basic_stock_data(self, ticker: str) -> Dict[str, Any]:
        """基本的な株価データを取得"""
        if self.has_stock_lib:
            try:
                # 既存ライブラリ使用
                success, message = self.stock_analyzer.analyze_stock(ticker)
                if success:
                    # 最新の分析データから主要指標を抽出
                    # （実装は簡略化）
                    return {
                        "price": "取得済み",
                        "rsi": "計算済み", 
                        "trend": "分析済み"
                    }
            except Exception as e:
                print(f"⚠️  既存分析でエラー: {e}")
        
        # フォールバック: yfinanceで基本データのみ取得
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1mo")
            
            if not hist.empty:
                latest_price = hist['Close'].iloc[-1]
                return {
                    "price": f"{latest_price:.2f}",
                    "rsi": "計算中",
                    "volume": f"{hist['Volume'].iloc[-1]:,.0f}"
                }
        except Exception as e:
            print(f"⚠️  基本データ取得エラー: {e}")
        
        return {"price": "N/A", "rsi": "N/A", "trend": "N/A"}
    
    def analyze_with_ai(self, ticker: str) -> Optional[str]:
        """AI統合分析を実行"""
        print(f"🔍 {ticker} の分析を開始...")
        
        # 残りリクエスト数表示
        remaining = self.gemini.rate_limiter.get_remaining_requests()
        print(f"📊 本日の残りAI分析回数: {remaining}")
        
        if remaining == 0:
            print("❌ 本日のAI分析回数上限に達しました")
            return None
        
        # 1. 基本データ取得
        basic_data = self.get_basic_stock_data(ticker)
        print(f"📈 基本データ: {basic_data}")
        
        # 2. AIプロンプト作成（短縮版）
        prompt = self.create_focused_prompt(ticker, basic_data)
        
        # 3. Gemini AI分析実行
        print(f"🤖 Gemini AIに問い合わせ中...")
        ai_response = self.gemini.generate_content(prompt)
        
        if ai_response:
            print(f"✅ AI分析完了")
            return ai_response
        else:
            print(f"❌ AI分析失敗")
            return None

def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Tiker + Gemini AI 株式分析')
    parser.add_argument('--ticker', type=str, required=True, help='株式ティッカー (例: TSLA)')
    parser.add_argument('--check-usage', action='store_true', help='API使用量確認')
    
    args = parser.parse_args()
    
    analyzer = TikerAIAnalyzer()
    
    if args.check_usage:
        remaining = analyzer.gemini.rate_limiter.get_remaining_requests()
        print(f"📊 本日の残りAI分析回数: {remaining}/50")
        return
    
    # AI分析実行
    result = analyzer.analyze_with_ai(args.ticker)
    
    if result:
        print(f"\n🎯 {args.ticker} AI分析結果:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        print(f"\n💡 詳細な技術分析が必要な場合:")
        print(f"python unified_stock_analyzer.py --ticker {args.ticker}")
    else:
        print(f"\n⚠️  AI分析に失敗しました。従来の分析を実行してください:")
        print(f"python unified_stock_analyzer.py --ticker {args.ticker}")

if __name__ == "__main__":
    main()