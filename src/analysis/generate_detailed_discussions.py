#!/usr/bin/env python3
"""
全9銘柄の詳細な4専門家討論レポートを生成
tiker.md形式に準拠した詳細分析
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from typing import Dict, List
import logging

# 現在のディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.expert_discussion_generator import ExpertDiscussionGenerator
from src.analysis.stock_analyzer_lib import TechnicalIndicators, ConfigManager, StockDataManager

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ポートフォリオ設定
PORTFOLIO_STOCKS = ['TSLA', 'FSLR', 'RKLB', 'ASTS', 'OKLO', 'JOBY', 'OII', 'LUNR', 'RDW']

def fetch_stock_data(ticker: str, period_days: int = 365) -> pd.DataFrame:
    """
    株価データを取得してテクニカル指標を計算
    
    Args:
        ticker: ティッカーシンボル
        period_days: 取得期間（日数）
        
    Returns:
        テクニカル指標を含むDataFrame
    """
    try:
        config = ConfigManager()
        data_manager = StockDataManager(config)
        
        # データ取得とテクニカル指標追加
        success, df, message = data_manager.fetch_stock_data(ticker, period_days)
        
        if not success:
            logger.warning(f"{ticker}: {message}")
            return pd.DataFrame()
        
        # テクニカル指標を追加
        df = data_manager.add_technical_indicators(df)
        
        return df
        
    except Exception as e:
        logger.error(f"{ticker}: エラー発生 - {str(e)}")
        return pd.DataFrame()

def generate_all_discussions():
    """全銘柄の詳細討論レポートを生成"""
    
    # レポートディレクトリ作成
    report_dir = "reports/detailed_discussions"
    os.makedirs(report_dir, exist_ok=True)
    
    # ジェネレーター初期化
    generator = ExpertDiscussionGenerator()
    
    # 現在日付
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 各銘柄の分析を実行
    for ticker in PORTFOLIO_STOCKS:
        logger.info(f"\n{'='*60}")
        logger.info(f"{ticker} の詳細分析を開始...")
        
        # データ取得
        df = fetch_stock_data(ticker)
        if df.empty:
            logger.error(f"{ticker}: データ取得失敗、スキップ")
            continue
        
        try:
            # 詳細分析を生成
            logger.info(f"{ticker}: 4専門家分析を生成中...")
            analysis_data = generator.generate_full_analysis(ticker, df, today)
            
            # レポートフォーマット
            logger.info(f"{ticker}: レポートをフォーマット中...")
            report_content = generator.format_analysis_report(analysis_data)
            
            # ファイル保存
            output_path = os.path.join(report_dir, f"{ticker}_detailed_analysis_{today}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"{ticker}: レポート保存完了 - {output_path}")
            
            # 簡易版も同時に生成（既存の形式用）
            simple_report = generate_simple_discussion(analysis_data)
            simple_path = f"reports/{ticker}_discussion_{today}.md"
            with open(simple_path, 'w', encoding='utf-8') as f:
                f.write(simple_report)
            
        except Exception as e:
            logger.error(f"{ticker}: 分析エラー - {str(e)}")
            continue
    
    logger.info(f"\n{'='*60}")
    logger.info("全銘柄の分析が完了しました")

def generate_simple_discussion(analysis_data: Dict) -> str:
    """簡易版の討論レポートを生成（既存形式）"""
    
    env = analysis_data['environment_assessment']
    scores = analysis_data['scores']
    ticker = analysis_data['company_info'].ticker
    
    # 各専門家の簡潔な評価を抽出
    tech_summary = env['TECH'].split('。')[0] + '。'
    fund_summary = env['FUND'].split('。')[0] + '。'
    macro_summary = env['MACRO'].split('。')[0] + '。'
    risk_summary = env['RISK'].split('。')[0] + '。'
    
    # 推奨アクション
    rec = analysis_data['final_recommendation']
    
    simple_report = f"""【TECH】{tech_summary}
総合スコア: {scores.tech}★/5

【FUND】{fund_summary}
総合スコア: {scores.fund}★/5

【MACRO】{macro_summary}
総合スコア: {scores.macro}★/5

【RISK】{risk_summary}
総合スコア: {scores.risk}★/5

【総合判定】{rec['judgment']}
{rec['rationale']}
"""
    
    return simple_report

def main():
    """メイン実行関数"""
    logger.info("詳細4専門家討論レポート生成を開始します")
    logger.info(f"対象銘柄: {', '.join(PORTFOLIO_STOCKS)}")
    
    generate_all_discussions()

if __name__ == "__main__":
    main()