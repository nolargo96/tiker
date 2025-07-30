#!/usr/bin/env python3
"""
全9銘柄の詳細専門家討論レポートを生成
tiker.mdに完全準拠した形式で出力
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# パスの追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.expert_discussion_generator import ExpertDiscussionGenerator
from src.analysis.stock_analyzer_lib import StockDataManager, ConfigManager
import logging


def setup_logging():
    """ロギング設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def process_ticker(ticker: str, generator: ExpertDiscussionGenerator, 
                   data_manager: StockDataManager, logger: logging.Logger) -> bool:
    """
    個別銘柄の詳細討論レポートを生成
    
    Args:
        ticker: ティッカーシンボル
        generator: 討論生成器
        data_manager: データ管理器
        logger: ロガー
        
    Returns:
        成功した場合True
    """
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"{ticker} の詳細分析を開始...")
        
        # データ取得（1年間）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        success, df, message = data_manager.fetch_stock_data(
            ticker, start_date, end_date
        )
        
        if not success:
            logger.error(f"{ticker}: データ取得失敗 - {message}")
            return False
            
        logger.info(f"{ticker}: {len(df)}日分のデータを取得")
        
        # テクニカル指標を追加
        df = data_manager.add_technical_indicators(df)
        
        # 分析日付
        analysis_date = datetime.now().strftime('%Y-%m-%d')
        
        # 詳細分析を実行
        logger.info(f"{ticker}: 詳細分析を実行中...")
        analysis_data = generator.generate_full_analysis(
            ticker, df, analysis_date
        )
        
        # tiker.md形式のレポートを生成
        logger.info(f"{ticker}: レポートをフォーマット中...")
        full_report = generator.format_analysis_report(analysis_data)
        
        # レポートを保存
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports', 'enhanced_discussions')
        os.makedirs(reports_dir, exist_ok=True)
        
        report_path = os.path.join(reports_dir, f"{ticker}_enhanced_{analysis_date}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(full_report)
            
        logger.info(f"{ticker}: レポート保存完了 → {report_path}")
        
        # 簡易版も保存（既存のHTML表示用）
        simple_report = generate_simple_report(ticker, analysis_data)
        simple_path = os.path.join(
            os.path.dirname(__file__), 
            'reports', 
            f"{ticker}_discussion_{analysis_date}.md"
        )
        with open(simple_path, 'w', encoding='utf-8') as f:
            f.write(simple_report)
            
        logger.info(f"{ticker}: 簡易版レポート保存完了 → {simple_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"{ticker}: エラー発生 - {str(e)}", exc_info=True)
        return False


def generate_simple_report(ticker: str, analysis_data: dict) -> str:
    """既存のHTML表示用の簡易レポートを生成"""
    scores = analysis_data['scores']
    env = analysis_data['environment_assessment']
    rec = analysis_data['final_recommendation']
    
    # 簡潔な内容に要約
    simple_report = f"""【TECH】{env['TECH'][:80]}...
総合スコア: {scores.tech}★/5

【FUND】{env['FUND'][:80]}...
総合スコア: {scores.fund}★/5

【MACRO】{env['MACRO'][:80]}...
総合スコア: {scores.macro}★/5

【RISK】{env['RISK'][:80]}...
総合スコア: {scores.risk}★/5

【総合判定】{rec['judgment']}
{rec['rationale']}
"""
    
    return simple_report


def main():
    """メイン処理"""
    logger = setup_logging()
    
    # 設定とコンポーネントの初期化
    config = ConfigManager()
    data_manager = StockDataManager(config)
    generator = ExpertDiscussionGenerator()
    
    # 対象銘柄リスト
    tickers = ['TSLA', 'FSLR', 'RKLB', 'ASTS', 'OKLO', 'JOBY', 'OII', 'LUNR', 'RDW']
    
    logger.info(f"詳細専門家討論レポート生成を開始")
    logger.info(f"対象銘柄: {', '.join(tickers)}")
    
    # 各銘柄を処理
    success_count = 0
    failed_tickers = []
    
    for ticker in tickers:
        if process_ticker(ticker, generator, data_manager, logger):
            success_count += 1
        else:
            failed_tickers.append(ticker)
    
    # 結果サマリー
    logger.info(f"\n{'='*60}")
    logger.info(f"処理完了: {success_count}/{len(tickers)} 銘柄成功")
    
    if failed_tickers:
        logger.warning(f"失敗した銘柄: {', '.join(failed_tickers)}")
    
    logger.info("\n生成されたレポート:")
    logger.info("- 詳細版: reports/enhanced_discussions/")
    logger.info("- 簡易版: reports/")
    
    return success_count == len(tickers)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)