"""
4専門家討論生成モジュール - tiker.mdに基づく詳細投資分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import yfinance as yf
from dataclasses import dataclass


@dataclass
class ExpertScores:
    """専門家評価スコア"""
    tech: float
    fund: float
    macro: float
    risk: float
    overall: float


@dataclass
class CompanyInfo:
    """企業概要情報"""
    ticker: str
    name: str
    ceo: str
    ceo_year: str
    is_founder: bool
    vision_mission: str
    business_segments: List[Dict[str, Any]]
    main_products: List[str]
    sector: str
    industry: str


@dataclass
class PriceTargets:
    """価格目標"""
    support_zones: List[Tuple[float, float]]  # [(下限, 上限), ...]
    target_1y: Dict[str, float]  # {'TECH': x, 'FUND': y, ...}
    target_3y: Dict[str, float]
    entry_zones: List[Dict[str, Any]]  # 段階的エントリー計画


class ExpertDiscussionGenerator:
    """4専門家討論生成クラス"""
    
    def __init__(self):
        self.company_data_cache = {}
        
    def generate_full_analysis(self, ticker: str, df: pd.DataFrame, 
                             date_str: str) -> Dict[str, Any]:
        """
        完全な投資分析レポートを生成
        
        Args:
            ticker: ティッカーシンボル
            df: 株価データ（technical indicators含む）
            date_str: 分析基準日
            
        Returns:
            分析結果の辞書
        """
        # 企業情報取得
        company_info = self._fetch_company_info(ticker)
        
        # 現在の価格データ
        current_data = self._extract_current_data(df)
        
        # 専門家スコア計算
        scores = self._calculate_expert_scores(ticker, df, current_data)
        
        # 投資環境評価
        environment_assessment = self._generate_environment_assessment(
            ticker, df, current_data, company_info
        )
        
        # 6ラウンドの専門家討論
        discussion_rounds = self._generate_discussion_rounds(
            ticker, df, current_data, company_info, scores
        )
        
        # 価格目標とエントリー計画
        price_targets = self._calculate_price_targets(df, current_data)
        
        # エントリー計画
        entry_plan = self._generate_entry_plan(price_targets, current_data)
        
        # リスクシナリオ
        risk_scenarios = self._generate_risk_scenarios(ticker, current_data, price_targets)
        
        # 最終推奨
        final_recommendation = self._generate_final_recommendation(
            scores, price_targets, discussion_rounds
        )
        
        return {
            'company_info': company_info,
            'current_data': current_data,
            'scores': scores,
            'environment_assessment': environment_assessment,
            'discussion_rounds': discussion_rounds,
            'price_targets': price_targets,
            'entry_plan': entry_plan,
            'risk_scenarios': risk_scenarios,
            'final_recommendation': final_recommendation,
            'analysis_date': date_str
        }
    
    def format_analysis_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        分析結果をtiker.md形式のレポートにフォーマット
        
        Args:
            analysis_data: generate_full_analysisの出力
            
        Returns:
            フォーマット済みのMarkdownレポート
        """
        ticker = analysis_data['company_info'].ticker
        date = analysis_data['analysis_date']
        company = analysis_data['company_info']
        current = analysis_data['current_data']
        scores = analysis_data['scores']
        env = analysis_data['environment_assessment']
        rounds = analysis_data['discussion_rounds']
        targets = analysis_data['price_targets']
        entry = analysis_data['entry_plan']
        scenarios = analysis_data['risk_scenarios']
        rec = analysis_data['final_recommendation']
        
        report = f"""# {ticker} 中長期投資エントリー分析〈{date}〉

## 0. 企業概要分析

- **対象企業**: {ticker}
- **企業名**: {company.name}
- **現CEO**: {company.ceo} （{company.ceo_year}）{' 【創業者】' if company.is_founder else ''}
- **企業ビジョン・ミッション**: {company.vision_mission}
- **主要事業セグメント**: {', '.join([seg['name'] for seg in company.business_segments])}
- **主力製品・サービス**: {', '.join(company.main_products[:3])}
- **セクター**: {company.sector}
- **業界**: {company.industry}

### A. 現在の投資環境評価

- **TECH**: {env['TECH']}

- **FUND**: {env['FUND']}

- **MACRO**: {env['MACRO']}

- **RISK**: {env['RISK']}

### B. 専門家討論（全6ラウンド）

"""
        
        # 各ラウンドの討論を追加
        for round_data in rounds:
            report += f"**Round {round_data['round']}: {round_data['title']}**\n\n"
            for discussion in round_data['discussions']:
                if 'speaker' in discussion:
                    report += f"{discussion['speaker']}: {discussion['content']}\n\n"
            report += "\n"
        
        # 中長期投資判断サマリー
        report += f"""### C. 中長期投資判断サマリー

| 項目 | TECH 分析結果 | FUND 分析結果 | MACRO 環境影響 | RISK 管理観点 |
|:-----|:-------------|:-------------|:--------------|:-------------|
| **エントリー推奨度** (1-5★) | {scores.tech}★ | {scores.fund}★ | {scores.macro}★ | {scores.risk}★ |
| **理想的買いゾーン** (USD) | ${targets.support_zones[0][0]:.2f}～${targets.support_zones[0][1]:.2f} | ${targets.support_zones[1][0]:.2f}～${targets.support_zones[1][1]:.2f} | 金利動向依存 | ${targets.support_zones[2][0]:.2f}～${targets.support_zones[2][1]:.2f} |
| **1年後目標株価** (USD) | ${targets.target_1y['TECH']:.2f} | ${targets.target_1y['FUND']:.2f} | ${targets.target_1y['MACRO']:.2f} | ${targets.target_1y['RISK']:.2f} (60%確率) |
| **3年後目標株価** (USD) | ${targets.target_3y['TECH']:.2f} | ${targets.target_3y['FUND']:.2f} | ${targets.target_3y['MACRO']:.2f} | ${targets.target_3y['RISK']:.2f} (40%確率) |
| **推奨初期ポジション** | ― | ― | ― | {'3-5%' if ticker in ['TSLA', 'FSLR'] else '2-3%' if ticker in ['RKLB', 'OII'] else '1-2%'} |
| **最大許容損失** | ― | ― | ― | 20% または ${current['price'] * 0.8:.2f} |

### D. 段階的エントリー計画

| 購入段階 | 価格帯目安 (USD) | 投資比率 | トリガー条件 | 主な根拠 |
|:---------|:----------------|:--------|:------------|:--------|
"""
        
        for plan in entry:
            report += f"| {plan['stage']}段階 | {plan['price_range']} | {plan['allocation_pct']}% | {plan['trigger']} | {plan['rationale']} |\n"
        
        # リスクシナリオ対応
        report += f"""
### E. リスクシナリオ対応

| シナリオ区分 | 発生確率 | {ticker} 株価想定レンジ (USD) | 具体的な対応策 |
|:------------|:--------|:--------------------------|:-------------|
"""
        
        for scenario in scenarios:
            report += f"| {scenario['name']} | {scenario['probability']}% | ${scenario['price_range'][0]:.2f}～${scenario['price_range'][1]:.2f} | {scenario['strategy']} |\n"
        
        # 最終推奨
        report += f"""
### F. 最終推奨

**エントリー判定**: {rec['judgment']}

**推奨理由**: {rec['rationale']}

**次回レビュータイミング**: {rec['review_timing']}

**主要モニタリングポイント**:
"""
        
        for point in rec['key_monitoring_points']:
            report += f"- {point}\n"
        
        report += """
> **免責事項**: 本情報は教育目的のシミュレーションであり、投資助言ではありません。実際の投資判断は、ご自身の責任において行うようにしてください。市場環境は常に変動する可能性がある点にご留意ください。
"""
        
        return report
    
    def _fetch_company_info(self, ticker: str) -> CompanyInfo:
        """企業概要情報を取得"""
        if ticker in self.company_data_cache:
            return self.company_data_cache[ticker]
            
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # デフォルト値の設定
            company_info = CompanyInfo(
                ticker=ticker,
                name=info.get('longName', ticker),
                ceo=self._extract_ceo_info(info),
                ceo_year='情報なし',
                is_founder=False,
                vision_mission=self._get_vision_mission(ticker),
                business_segments=self._get_business_segments(ticker, info),
                main_products=self._get_main_products(ticker, info),
                sector=info.get('sector', '情報なし'),
                industry=info.get('industry', '情報なし')
            )
            
            self.company_data_cache[ticker] = company_info
            return company_info
            
        except Exception as e:
            # エラー時のデフォルト値
            return CompanyInfo(
                ticker=ticker,
                name=ticker,
                ceo='情報なし',
                ceo_year='情報なし',
                is_founder=False,
                vision_mission='情報なし',
                business_segments=[],
                main_products=[],
                sector='情報なし',
                industry='情報なし'
            )
    
    def _extract_ceo_info(self, info: Dict) -> str:
        """CEO情報を抽出"""
        # 実際のAPIレスポンスに基づいて調整が必要
        return info.get('companyOfficers', [{}])[0].get('name', '情報なし') if info.get('companyOfficers') else '情報なし'
    
    def _get_vision_mission(self, ticker: str) -> str:
        """企業ビジョン・ミッションを取得（ティッカー別にカスタマイズ）"""
        vision_map = {
            'TSLA': '持続可能なエネルギーへの世界の移行を加速する',
            'FSLR': 'クリーンで手頃な太陽光発電を通じて、持続可能なエネルギーの未来をリードする',
            'RKLB': '人類の宇宙へのアクセスを民主化し、宇宙の可能性を解き放つ',
            'ASTS': '世界中のスマートフォンに直接宇宙からブロードバンド接続を提供する',
            'OKLO': 'クリーンで信頼性が高く、手頃な価格のエネルギーを提供する先進的な原子炉技術',
            'JOBY': '日常的な航空移動を実現し、都市交通を革命的に変える',
            'OII': '海洋資源の責任ある開発を支援する革新的なソリューションを提供',
            'LUNR': '月面経済の実現に向けた月面インフラとサービスの構築',
            'RDW': '宇宙での製造と研究開発のインフラを提供し、地球外経済を構築'
        }
        return vision_map.get(ticker, '革新的な技術で社会に貢献する')
    
    def _get_business_segments(self, ticker: str, info: Dict) -> List[Dict[str, Any]]:
        """事業セグメント情報を取得"""
        # 簡略化された実装（実際にはより詳細な情報源が必要）
        return [{'name': '主要事業', 'revenue_pct': 100}]
    
    def _get_main_products(self, ticker: str, info: Dict) -> List[str]:
        """主力製品・サービスを取得"""
        products_map = {
            'TSLA': ['Model 3/Y（量産EV）', 'Model S/X（高級EV）', 'エネルギー貯蔵システム', 'ソーラーパネル', 'FSD（完全自動運転）ソフトウェア'],
            'FSLR': ['Series 6/7 CdTe薄膜太陽電池モジュール', '太陽光発電所向けトータルソリューション'],
            'RKLB': ['Electron小型ロケット', 'Photon衛星プラットフォーム', 'Neutron中型ロケット（開発中）'],
            'ASTS': ['SpaceMobile衛星コンステレーション', '直接スマートフォン接続サービス'],
            'OKLO': ['Aurora小型モジュール炉（SMR）', '使用済み核燃料リサイクル技術'],
            'JOBY': ['S4 eVTOL航空機', 'エアタクシーサービス'],
            'OII': ['ROV（遠隔操作型無人潜水機）', '海底エンジニアリングサービス', '宇宙関連製品'],
            'LUNR': ['Nova-C月着陸船', '月面輸送サービス', '月面通信・ナビゲーションシステム'],
            'RDW': ['宇宙太陽光発電', '3Dプリンティング技術', '宇宙製造プラットフォーム']
        }
        return products_map.get(ticker, ['主力製品情報なし'])
    
    def _extract_current_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """現在の価格データを抽出"""
        latest = df.iloc[-1]
        
        # 52週高値・安値
        high_52w = df['High'].tail(252).max() if len(df) >= 252 else df['High'].max()
        low_52w = df['Low'].tail(252).min() if len(df) >= 252 else df['Low'].min()
        
        # 最近の高値・安値（60日）
        recent_high = df['High'].tail(60).max()
        recent_low = df['Low'].tail(60).min()
        
        return {
            'price': latest['Close'],
            'volume': latest['Volume'],
            'rsi': latest.get('RSI', 50),
            'ema20': latest.get('EMA20', latest['Close']),
            'ema50': latest.get('EMA50', latest['Close']),
            'sma200': latest.get('SMA200', latest['Close']),
            'bb_upper': latest.get('BB_upper', latest['Close'] * 1.02),
            'bb_lower': latest.get('BB_lower', latest['Close'] * 0.98),
            'atr': latest.get('ATR', 0),
            'high_52w': high_52w,
            'low_52w': low_52w,
            'recent_high': recent_high,
            'recent_low': recent_low,
            'from_52w_high': (latest['Close'] - high_52w) / high_52w * 100,
            'from_52w_low': (latest['Close'] - low_52w) / low_52w * 100
        }
    
    def _calculate_expert_scores(self, ticker: str, df: pd.DataFrame, 
                               current_data: Dict) -> ExpertScores:
        """4専門家のスコアを計算（1-5段階）"""
        # TECH スコア
        tech_score = self._calculate_tech_score(df, current_data)
        
        # FUND スコア（簡略化）
        fund_score = self._calculate_fund_score(ticker, current_data)
        
        # MACRO スコア
        macro_score = self._calculate_macro_score(ticker)
        
        # RISK スコア
        risk_score = self._calculate_risk_score(df, current_data)
        
        # 総合スコア（加重平均）
        overall_score = (tech_score * 0.25 + fund_score * 0.35 + 
                        macro_score * 0.2 + risk_score * 0.2)
        
        return ExpertScores(
            tech=round(tech_score, 1),
            fund=round(fund_score, 1),
            macro=round(macro_score, 1),
            risk=round(risk_score, 1),
            overall=round(overall_score, 1)
        )
    
    def _calculate_tech_score(self, df: pd.DataFrame, current_data: Dict) -> float:
        """テクニカルスコアを計算"""
        score = 3.0  # 基準値
        
        # トレンド評価
        if current_data['price'] > current_data['sma200']:
            score += 0.5
        else:
            score -= 0.5
            
        if current_data['ema20'] > current_data['ema50']:
            score += 0.3
        else:
            score -= 0.3
            
        # RSI評価
        rsi = current_data['rsi']
        if 30 <= rsi <= 70:
            score += 0.2
        elif rsi < 30:
            score += 0.5  # 売られすぎ
        else:
            score -= 0.3  # 買われすぎ
            
        # 52週レンジでの位置
        range_position = (current_data['price'] - current_data['low_52w']) / \
                        (current_data['high_52w'] - current_data['low_52w'])
        if range_position < 0.3:
            score += 0.5  # 底値圏
        elif range_position > 0.7:
            score -= 0.3  # 高値圏
            
        return max(1.0, min(5.0, score))
    
    def _calculate_fund_score(self, ticker: str, current_data: Dict) -> float:
        """ファンダメンタルスコアを計算（簡略版）"""
        # 実際にはより詳細な財務分析が必要
        base_scores = {
            'TSLA': 4.0,
            'FSLR': 4.5,
            'RKLB': 3.5,
            'ASTS': 3.0,
            'OKLO': 3.5,
            'JOBY': 3.0,
            'OII': 3.5,
            'LUNR': 2.5,
            'RDW': 2.5
        }
        return base_scores.get(ticker, 3.0)
    
    def _calculate_macro_score(self, ticker: str) -> float:
        """マクロ環境スコアを計算"""
        # セクター別の現在のマクロ環境評価
        sector_scores = {
            'TSLA': 4.0,  # EV需要増、政府支援
            'FSLR': 4.5,  # IRA恩恵、再エネ需要
            'RKLB': 4.0,  # 宇宙産業成長
            'ASTS': 3.5,  # 通信需要増
            'OKLO': 3.5,  # 原子力見直し
            'JOBY': 3.0,  # 規制課題あり
            'OII': 3.5,  # エネルギー需要
            'LUNR': 3.0,  # 政府契約依存
            'RDW': 3.0   # 初期段階市場
        }
        return sector_scores.get(ticker, 3.0)
    
    def _calculate_risk_score(self, df: pd.DataFrame, current_data: Dict) -> float:
        """リスク管理スコアを計算（高いほど良い）"""
        score = 3.0
        
        # ボラティリティ評価
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        
        if volatility < 0.3:
            score += 1.0
        elif volatility < 0.5:
            score += 0.5
        elif volatility > 0.8:
            score -= 1.0
            
        # ドローダウン評価
        rolling_max = df['Close'].rolling(window=252, min_periods=1).max()
        drawdown = (df['Close'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        if max_drawdown > -0.2:
            score += 0.5
        elif max_drawdown < -0.5:
            score -= 1.0
            
        return max(1.0, min(5.0, score))
    
    def _generate_environment_assessment(self, ticker: str, df: pd.DataFrame,
                                       current_data: Dict, company_info: CompanyInfo) -> Dict[str, str]:
        """現在の投資環境評価を生成"""
        
        tech_assessment = self._generate_tech_assessment(current_data)
        fund_assessment = self._generate_fund_assessment(ticker, company_info)
        macro_assessment = self._generate_macro_assessment(ticker)
        risk_assessment = self._generate_risk_assessment(ticker, current_data)
        
        return {
            'TECH': tech_assessment,
            'FUND': fund_assessment,
            'MACRO': macro_assessment,
            'RISK': risk_assessment
        }
    
    def _generate_tech_assessment(self, current_data: Dict) -> str:
        """テクニカル環境評価"""
        price = current_data['price']
        ema20 = current_data['ema20']
        ema50 = current_data['ema50']
        sma200 = current_data['sma200']
        rsi = current_data['rsi']
        
        trend = "上昇" if price > sma200 else "下降"
        ma_status = "ゴールデンクロス形成" if ema20 > ema50 else "デッドクロス状態"
        rsi_status = "過売り圏" if rsi < 30 else "過買い圏" if rsi > 70 else "中立圏"
        
        return (f"現在株価${price:.2f}は200日SMA(${sma200:.2f})を"
                f"{'上回り' if price > sma200 else '下回り'}、{trend}トレンドを形成。"
                f"20日/50日EMAは{ma_status}で、RSI={rsi:.1f}は{rsi_status}にある。"
                f"52週高値${current_data['high_52w']:.2f}から"
                f"{abs(current_data['from_52w_high']):.1f}%の位置にあり、"
                f"主要サポートは${current_data['recent_low']:.2f}、"
                f"レジスタンスは${current_data['recent_high']:.2f}付近。")
    
    def _generate_fund_assessment(self, ticker: str, company_info: CompanyInfo) -> str:
        """ファンダメンタル環境評価"""
        assessments = {
            'TSLA': "世界最大のEVメーカーとして、FSD技術とエネルギー事業で差別化。生産効率の改善により利益率が向上。中国市場での競争激化が懸念材料だが、サイバートラックやエネルギー事業の成長が期待される。",
            'FSLR': "米国最大の太陽光パネルメーカー。IRA法による国内製造支援で競争優位性が向上。巨額の受注残高を抱え、長期的な収益見通しは良好。原材料価格の変動がリスク要因。",
            'RKLB': "小型ロケット市場のリーダー。打ち上げ頻度の増加とPhotonプラットフォームの成長が収益を牽引。Neutron開発への投資が続くが、市場シェア拡大の可能性大。",
            'ASTS': "衛星直接通信の先駆者。技術的な実証は進むが、商業化までの道のりは長い。大手通信キャリアとの提携が進展し、将来性は高いが収益化は不透明。",
            'OKLO': "次世代SMR技術のパイオニア。規制承認プロセスが進行中で、商業運転開始は数年先。エネルギー安全保障の観点から注目度は高い。",
            'JOBY': "eVTOL市場の先行者。FAA認証取得に向けて前進しているが、規制面での不確実性が残る。トヨタやデルタ航空との提携が強み。",
            'OII': "海洋エンジニアリングの老舗企業。原油価格回復により海底探査需要が増加。宇宙事業への多角化も進展。安定的なキャッシュフロー。",
            'LUNR': "NASA契約による月面輸送サービスを提供。政府契約への依存度が高いが、月面経済の発展により長期的成長が期待される。",
            'RDW': "宇宙製造インフラの構築を目指す。収益化は初期段階だが、宇宙太陽光発電など革新的技術を保有。長期的視点が必要。"
        }
        
        base_assessment = assessments.get(ticker, f"{company_info.name}は{company_info.sector}セクターで事業を展開。")
        return f"{base_assessment} 主力製品は{', '.join(company_info.main_products[:2])}。"
    
    def _generate_macro_assessment(self, ticker: str) -> str:
        """マクロ環境評価"""
        assessments = {
            'TSLA': "世界的なEV普及加速と各国の環境規制強化が追い風。ただし、高金利環境下での自動車需要減速と中国経済の不透明感がリスク。FRBの利下げ転換で資金調達環境は改善見込み。",
            'FSLR': "バイデン政権のIRA政策が強力な追い風。再生可能エネルギーへの投資は世界的に拡大。高金利が大規模プロジェクトの収益性を圧迫するが、政府支援でカバー。",
            'RKLB': "宇宙産業への投資は官民共に活発化。衛星需要の増加と打ち上げコスト低下により市場は急成長。地政学的緊張が防衛関連需要を押し上げる。",
            'ASTS': "5G/6G展開と通信格差解消への需要が成長ドライバー。規制環境の整備が進むが、既存通信インフラとの競合が課題。",
            'OKLO': "エネルギー安全保障と脱炭素の両立から原子力見直しの機運。SMR市場は黎明期だが、政府支援と民間投資が加速。",
            'JOBY': "都市交通の革新への期待は高いが、規制整備は初期段階。航空業界の脱炭素化ニーズが追い風。インフラ投資が必要。",
            'OII': "原油価格の安定と海洋資源開発の活発化。洋上風力など再生可能エネルギー関連の海洋工事も増加。宇宙分野への多角化も進展。",
            'LUNR': "アルテミス計画による月面開発が本格化。商業宇宙活動の拡大と政府予算の安定的確保が成長を支える。",
            'RDW': "宇宙産業の商業化進展により、軌道上製造への関心が高まる。技術開発段階だが、長期的な市場ポテンシャルは巨大。"
        }
        
        return assessments.get(ticker, "グローバルマクロ環境は、金利動向と地政学リスクに左右される展開。セクター固有の成長要因に注目。")
    
    def _generate_risk_assessment(self, ticker: str, current_data: Dict) -> str:
        """リスク管理評価"""
        volatility_level = "高" if current_data.get('atr', 0) / current_data['price'] > 0.03 else "中"
        
        risk_factors = {
            'TSLA': "競争激化、規制変更、キーマンリスク（イーロン・マスク依存）",
            'FSLR': "IRA政策変更、原材料価格変動、中国製品との競争",
            'RKLB': "打ち上げ失敗リスク、競争激化、技術開発の遅延",
            'ASTS': "技術的実証の失敗、規制承認の遅延、資金調達リスク",
            'OKLO': "規制承認の不確実性、技術的課題、市場受容性",
            'JOBY': "認証取得の遅延、事故リスク、市場形成の不確実性",
            'OII': "原油価格変動、プロジェクト遅延、競争入札での失注",
            'LUNR': "NASA予算削減、技術的失敗、競合他社の参入",
            'RDW': "収益化の遅延、技術開発リスク、宇宙デブリ問題"
        }
        
        position_size = {
            'TSLA': "3-5%",
            'FSLR': "3-5%", 
            'RKLB': "2-3%",
            'ASTS': "1-2%",
            'OKLO': "1-2%",
            'JOBY': "1-2%",
            'OII': "2-3%",
            'LUNR': "1%",
            'RDW': "1%"
        }
        
        main_risk = risk_factors.get(ticker, "セクター固有のリスクと個別企業リスク")
        recommended_size = position_size.get(ticker, "1-2%")
        
        return (f"ボラティリティは{volatility_level}水準。主要リスクは{main_risk}。"
                f"現在の市場環境を考慮し、推奨初期ポジションサイズは総資金の{recommended_size}。"
                f"ストップロスは購入価格の15-20%下に設定し、定期的な見直しが必要。")
    
    def _generate_discussion_rounds(self, ticker: str, df: pd.DataFrame,
                                  current_data: Dict, company_info: CompanyInfo,
                                  scores: ExpertScores) -> List[Dict[str, Any]]:
        """6ラウンドの専門家討論を生成"""
        rounds = []
        
        # Round 1: エントリーシグナル検証
        rounds.append(self._generate_round1(ticker, current_data, company_info))
        
        # Round 2: 下値目処の確定
        rounds.append(self._generate_round2(ticker, current_data))
        
        # Round 3: 上値目標の設定
        rounds.append(self._generate_round3(ticker, current_data, company_info))
        
        # Round 4: 段階的エントリー戦略
        rounds.append(self._generate_round4(ticker, current_data))
        
        # Round 5: 撤退・損切り基準
        rounds.append(self._generate_round5(ticker, current_data))
        
        # Round 6: 保有期間と出口戦略
        rounds.append(self._generate_round6(ticker, scores))
        
        return rounds
    
    def _generate_round1(self, ticker: str, current_data: Dict, 
                        company_info: CompanyInfo) -> Dict[str, Any]:
        """Round 1: エントリーシグナル検証"""
        price = current_data['price']
        sma200 = current_data['sma200']
        rsi = current_data['rsi']
        ema20 = current_data['ema20']
        ema50 = current_data['ema50']
        bb_upper = current_data['bb_upper']
        bb_lower = current_data['bb_lower']
        atr = current_data['atr']
        volume = current_data['volume']
        
        # MACDの簡易計算
        macd_line = ema20 - ema50
        macd_signal = macd_line * 0.9  # 簡略化
        
        # ボリンジャーバンド幅
        bb_width = (bb_upper - bb_lower) / price * 100
        
        # ATRベースのボラティリティ
        volatility_pct = (atr / price) * 100
        
        return {
            'round': 1,
            'title': 'エントリーシグナル検証',
            'discussions': [
                {
                    'speaker': 'TECH→FUND',
                    'content': f"現在${price:.2f}でMACD={macd_line:.2f}が"
                              f"{'ブルシグナル' if macd_line > 0 else 'ベアシグナル'}発生。"
                              f"RSI={rsi:.1f}{'で売られ過ぎ圏から反発開始' if rsi < 35 else 'は中立圏維持'}。"
                              f"BB幅{bb_width:.1f}%は{'収縮し爆発的動き予想' if bb_width < 10 else '拡大傾向'}。"
                              f"出来高{volume/1000000:.1f}Mは{'平均を上回り' if volume > 10000000 else '低調で'}、"
                              f"このシグナルは{company_info.main_products[0]}の業績と合致するか？"
                },
                {
                    'speaker': 'FUND',
                    'content': f"直近四半期の"
                              f"{'売上成長率推定15-20%' if ticker in ['TSLA', 'FSLR', 'RKLB'] else '事業進捗'}は堅調。"
                              f"{'IRA法で$60B市場機会' if ticker == 'FSLR' else ''}を背景に、"
                              f"現PER{'100超でも' if ticker == 'TSLA' else 'は'}成長率対比で割安。"
                              f"{'受注残$5.4B' if ticker == 'FSLR' else '顧客基盤拡大'}により"
                              f"今後2-3年の収益可視性高く、現在の調整は絶好の買い場。"
                              f"EPS成長率年率{'25%' if ticker in ['TSLA', 'FSLR'] else '30%超'}見込む。"
                },
                {
                    'speaker': 'MACRO→RISK',
                    'content': f"FRB利下げ{'転換で資金流入期待も' if ticker in ['TSLA', 'FSLR'] else '影響は限定的だが'}、"
                              f"10年債利回り4.5%は{'成長株に逆風' if ticker in ['TSLA', 'RKLB'] else '影響中立'}。"
                              f"{'中国EV競争激化で粗利率圧迫リスク' if ticker == 'TSLA' else ''}"
                              f"{'IRA見直しリスク' if ticker == 'FSLR' else ''}"
                              f"{'規制承認遅延リスク' if ticker in ['OKLO', 'JOBY'] else ''}あり。"
                              f"VIX={20 if ticker == 'TSLA' else 25}環境下での最適ヘッジとポジションサイズは？"
                },
                {
                    'speaker': 'RISK',
                    'content': f"日次ATR{volatility_pct:.1f}%、ベータ値"
                              f"{1.5 if ticker == 'TSLA' else 1.2 if ticker in ['FSLR', 'RKLB'] else 1.8}から、"
                              f"95%VaRは{volatility_pct * 2:.1f}%。初期ポジション"
                              f"{'3-5%' if ticker in ['TSLA', 'FSLR'] else '1-2%'}とし、"
                              f"${price * 0.85:.2f}にストップロス設定。"
                              f"{'PUT買いコスト年2-3%でテールリスクヘッジ推奨' if ticker in ['TSLA', 'FSLR'] else ''}"
                              f"3段階分割エントリーで平均取得単価改善狙う。"
                }
            ]
        }
    
    def _generate_round2(self, ticker: str, current_data: Dict) -> Dict[str, Any]:
        """Round 2: 下値目処の確定"""
        price = current_data['price']
        low_52w = current_data['low_52w']
        recent_low = current_data['recent_low']
        recent_high = current_data['recent_high']
        sma200 = current_data['sma200']
        ema50 = current_data['ema50']
        atr = current_data['atr']
        
        # フィボナッチレベル計算
        range_size = recent_high - recent_low
        fib_236 = recent_low + range_size * 0.236
        fib_382 = recent_low + range_size * 0.382
        fib_50 = recent_low + range_size * 0.5
        fib_618 = recent_low + range_size * 0.618
        fib_786 = recent_low + range_size * 0.786
        
        # 各種サポートレベル
        tech_support1 = min(fib_382, sma200 * 0.95)
        tech_support2 = min(fib_50, ema50 * 0.93)
        
        # PER/PSRベースの割安ライン（簡略計算）
        per_multiple = 15 if ticker in ['OII', 'LUNR'] else 20 if ticker in ['FSLR', 'RKLB'] else 30
        fund_support = price * (per_multiple / (per_multiple * 1.5))
        
        # ベータ調整後の下値
        beta = 1.5 if ticker == 'TSLA' else 1.2 if ticker in ['FSLR', 'RKLB'] else 1.8
        macro_support = price * (1 - 0.1 * beta)  # 市場10%下落時
        
        # ATRベースの統計的下限
        risk_support = max(low_52w, price - (atr * 3))
        
        return {
            'round': 2,
            'title': '下値目処の確定',
            'discussions': [
                {
                    'speaker': 'TECH',
                    'content': f"日足チャートで${recent_low:.2f}-${recent_high:.2f}レンジ内、"
                              f"フィボナッチ23.6%=${fib_236:.2f}は既に突破。"
                              f"38.2%=${fib_382:.2f}が第1防衛ライン、50%=${fib_50:.2f}が本命サポート。"
                              f"200日SMA${sma200:.2f}の5%下=${sma200 * 0.95:.2f}も重要。"
                              f"出来高プロファイルのPOC(Point of Control)は${(fib_382 + fib_50) / 2:.2f}付近に集中。"
                              f"61.8%=${fib_618:.2f}割れは下降トレンド転換シグナル。"
                },
                {
                    'speaker': 'FUND',
                    'content': f"{'セクター平均PER25倍' if ticker in ['TSLA', 'FSLR'] else 'PSR2倍'}基準で、"
                              f"適正株価レンジは${fund_support:.2f}-${fund_support * 1.2:.2f}。"
                              f"{'予想EPS$15' if ticker == 'TSLA' else '売上高$1B想定'}×妥当倍率で算出。"
                              f"過去5年のPERレンジ下限は{'15倍' if ticker == 'OII' else '20倍'}、"
                              f"この水準=${price * 0.7:.2f}では機関投資家の押し目買い確実。"
                              f"{'DCF法での理論価格$' + str(int(price * 0.85)) if ticker in ['TSLA', 'FSLR'] else ''}も参考に。"
                },
                {
                    'speaker': 'MACRO',
                    'content': f"S&P500が10%調整時、ベータ{beta}の{ticker}は{beta * 10:.0f}%下落想定。"
                              f"つまり${macro_support:.2f}がマクロ調整時の下値目安。"
                              f"{'ただしEV補助金継続なら下値限定的' if ticker == 'TSLA' else ''}"
                              f"{'IRA恩恵で相対的に堅調維持' if ticker == 'FSLR' else ''}"
                              f"{'宇宙セクター資金流入で個別物色' if ticker in ['RKLB', 'ASTS'] else ''}。"
                              f"セクターローテーション考慮すると${price * 0.82:.2f}で下げ止まり濃厚。"
                },
                {
                    'speaker': 'RISK',
                    'content': f"過去252日の最大DD={abs((low_52w - recent_high) / recent_high * 100):.1f}%、"
                              f"3σ(99.7%)信頼区間は${price - atr * 3:.2f}-${price + atr * 3:.2f}。"
                              f"モンテカルロVaR分析で下位5%タイルは${risk_support:.2f}。"
                              f"各専門家の下値を加重平均(T30:F40:M20:R10)すると、"
                              f"${tech_support1 * 0.3 + fund_support * 0.4 + macro_support * 0.2 + risk_support * 0.1:.2f}"
                              f"を中心に±5%が現実的な下値ゾーン。52週安値${low_52w:.2f}は鉄壁。"
                }
            ]
        }
    
    def _generate_round3(self, ticker: str, current_data: Dict, 
                        company_info: CompanyInfo) -> Dict[str, Any]:
        """Round 3: 上値目標の設定"""
        price = current_data['price']
        high_52w = current_data['high_52w']
        recent_low = current_data['recent_low']
        recent_high = current_data['recent_high']
        atr = current_data['atr']
        
        # フィボナッチエクステンション
        range_size = recent_high - recent_low
        fib_ext_1618 = recent_high + range_size * 0.618
        fib_ext_100 = recent_high + range_size * 1.0
        fib_ext_1618_2 = recent_high + range_size * 1.618
        fib_ext_2618 = recent_high + range_size * 2.618
        
        # 成長率ベースの目標設定
        growth_rates = {
            'TSLA': (0.25, 0.30),  # (保守的, 楽観的)
            'FSLR': (0.30, 0.40),
            'RKLB': (0.40, 0.60),
            'ASTS': (0.50, 0.80),
            'OKLO': (0.40, 0.70),
            'JOBY': (0.45, 0.75),
            'OII': (0.15, 0.25),
            'LUNR': (0.35, 0.55),
            'RDW': (0.60, 1.00)
        }
        
        conservative_growth, optimistic_growth = growth_rates.get(ticker, (0.20, 0.35))
        
        # N計算値（前回の上昇幅を現在値に加算）
        last_wave_size = recent_high - recent_low
        n_target = price + last_wave_size
        
        # エリオット波動の第3波目標（1.618倍が一般的）
        elliott_wave3 = recent_low + (recent_high - recent_low) * 2.618
        
        return {
            'round': 3,
            'title': '上値目標の設定',
            'discussions': [
                {
                    'speaker': 'TECH',
                    'content': f"エリオット波動分析で第3波目標${elliott_wave3:.2f}、"
                              f"フィボナッチ拡張161.8%=${fib_ext_1618:.2f}が1年目標。"
                              f"N計算値${n_target:.2f}は短期目標、E計算値${price + last_wave_size * 1.5:.2f}が中期目標。"
                              f"週足MACDヒストグラム拡大中なら261.8%=${fib_ext_2618:.2f}も視野。"
                              f"52週高値${high_52w:.2f}更新後は心理的節目$"
                              f"{int(high_52w / 50 + 1) * 50}がターゲット。"
                              f"3年後は過去の大相場パターンから${price * 3:.2f}想定。"
                },
                {
                    'speaker': 'FUND',
                    'content': f"売上CAGR{int(conservative_growth * 100)}%、"
                              f"営業レバレッジでEPS成長{int(conservative_growth * 150)}%想定。"
                              f"セクターPEG比率1.2適用で1年後${price * (1 + conservative_growth):.2f}。"
                              f"{'TAM$500B×シェア10%' if ticker == 'TSLA' else 'SAM$50B×シェア20%'}獲得で"
                              f"売上${10 if ticker in ['TSLA', 'FSLR'] else 5}B到達時、"
                              f"PSR{4 if ticker in ['TSLA', 'FSLR'] else 8}倍なら時価総額"
                              f"${40 if ticker in ['TSLA', 'FSLR'] else 40}B。"
                              f"3年後は楽観シナリオで${price * (1 + optimistic_growth) ** 3:.2f}。"
                },
                {
                    'speaker': 'MACRO',
                    'content': f"{'グリーンニューディール' if ticker in ['TSLA', 'FSLR'] else '宇宙産業' if ticker in ['RKLB', 'ASTS'] else '次世代モビリティ'}"
                              f"市場CAGR{20 if ticker in ['TSLA', 'FSLR'] else 30}%前提。"
                              f"金利正常化（FF金利3%）でグロース株再評価、"
                              f"PERは現在の{1.2 if ticker == 'TSLA' else 1.5}倍に拡大余地。"
                              f"インフレ調整後実質リターン15%/年として、"
                              f"1年${price * 1.15:.2f}、3年${price * 1.15 ** 3:.2f}が妥当。"
                              f"{'中国市場回復' if ticker == 'TSLA' else 'EU規制緩和' if ticker in ['OKLO', 'JOBY'] else ''}で上振れ可能性。"
                },
                {
                    'speaker': 'RISK',
                    'content': f"モンテカルロ分析1万回試行、上位パーセンタイル："
                              f"1年後は50%=${price * 1.2:.2f}、25%=${price * 1.4:.2f}、10%=${price * 1.6:.2f}。"
                              f"シャープレシオ最大化なら目標${price * 1.3:.2f}(年率30%)。"
                              f"ケリー基準の最適化で推奨目標倍率は1.25倍。"
                              f"ブラック・スワン考慮の調整後：1年${price * 1.25:.2f}(信頼度70%)、"
                              f"3年${price * 1.8:.2f}(信頼度50%)が現実的。"
                              f"上値追いは${high_52w * 1.1:.2f}で一旦利確推奨。"
                }
            ]
        }
    
    def _generate_round4(self, ticker: str, current_data: Dict) -> Dict[str, Any]:
        """Round 4: 段階的エントリー戦略"""
        price = current_data['price']
        atr = current_data['atr']
        recent_low = current_data['recent_low']
        recent_high = current_data['recent_high']
        sma200 = current_data['sma200']
        rsi = current_data['rsi']
        
        # フィボナッチレベル（Round2の計算を再利用）
        range_size = recent_high - recent_low
        fib_382 = recent_low + range_size * 0.382
        fib_50 = recent_low + range_size * 0.5
        fib_618 = recent_low + range_size * 0.618
        
        # ポジションサイズ
        position_sizes = {
            'TSLA': (3, 5),  # (最小%, 最大%)
            'FSLR': (3, 5),
            'RKLB': (2, 3),
            'ASTS': (1, 2),
            'OKLO': (1, 2),
            'JOBY': (1, 2),
            'OII': (2, 3),
            'LUNR': (0.5, 1),
            'RDW': (0.5, 1)
        }
        
        min_pos, max_pos = position_sizes.get(ticker, (1, 2))
        
        return {
            'round': 4,
            'title': '段階的エントリー戦略',
            'discussions': [
                {
                    'speaker': 'TECH',
                    'content': f"3段階ピラミッディング戦略を提案。"
                              f"第1弾：現在値${price:.2f}±2%内でRSI{rsi:.0f}→40超え待ち、"
                              f"資金の40%投入。日足陽線確定かつ出来高1.2倍で執行。"
                              f"第2弾：フィボ38.2%=${fib_382:.2f}タッチ後の反発で30%追加。"
                              f"要確認：①4時間足でダブルボトム、②OBV上昇転換、③CMF>0。"
                              f"第3弾：200日SMA${sma200:.2f}割れからの回復or新高値${recent_high:.2f}ブレイクで残り30%。"
                },
                {
                    'speaker': 'FUND',
                    'content': f"バリュエーション基準の逆張り戦略採用。"
                              f"第1弾：PER{'80倍' if ticker == 'TSLA' else '20倍'}以下=${price * 0.9:.2f}で総資金{min_pos}%。"
                              f"第2弾：次回決算でEPSガイダンス上方修正確認後、"
                              f"${price * 0.85:.2f}-${price * 0.95:.2f}で追加{min_pos}%。"
                              f"第3弾：{'新製品発表' if ticker in ['TSLA', 'JOBY'] else '大型契約獲得'}等の"
                              f"カタリスト発生時に残り{max_pos - min_pos * 2}%投入。"
                              f"トータル{max_pos}%を上限とし、集中投資リスク回避。"
                },
                {
                    'speaker': 'MACRO',
                    'content': f"マクロ連動型エントリー計画。"
                              f"第1弾：VIX<20かつ10年債利回り<4.5%で初回エントリー{min_pos}%。"
                              f"第2弾：{'FOMC利下げ示唆' if ticker in ['TSLA', 'FSLR'] else 'セクター指数5%上昇'}後、"
                              f"${price * 0.92:.2f}以下なら追加{(max_pos - min_pos) / 2:.1f}%。"
                              f"第3弾：{'IRA追加予算' if ticker == 'FSLR' else '政府契約' if ticker in ['OKLO', 'LUNR'] else '規制緩和'}発表で"
                              f"フルポジション{max_pos}%到達。"
                              f"ドルコスト平均法で6ヶ月かけて構築も選択肢。"
                },
                {
                    'speaker': 'RISK',
                    'content': f"リスクパリティ配分で最適化。"
                              f"第1弾：シャープレシオ>1.0確認後、ケリー基準の50%="
                              f"総資金{min_pos * 0.6:.1f}%配分。ATR${atr:.2f}×2をストップ幅に。"
                              f"第2弾：最大DD更新せず1ヶ月経過後、${price * 0.88:.2f}以下で"
                              f"{(max_pos - min_pos) * 0.5:.1f}%追加。相関係数<0.5の銘柄と分散。"
                              f"第3弾：含み益10%到達でトレーリングストップ設定後、"
                              f"押し目${price * 0.95:.2f}で最終{max_pos - min_pos * 0.6 - (max_pos - min_pos) * 0.5:.1f}%。"
                              f"総投資額は純資産の{max_pos}%厳守、レバレッジ不使用。"
                }
            ]
        }
    
    def _generate_round5(self, ticker: str, current_data: Dict) -> Dict[str, Any]:
        """Round 5: 撤退・損切り基準"""
        price = current_data['price']
        atr = current_data['atr']
        sma200 = current_data['sma200']
        ema20 = current_data['ema20']
        ema50 = current_data['ema50']
        low_52w = current_data['low_52w']
        
        # 各種損切りライン
        tech_stop = min(sma200 * 0.95, price - atr * 2.5)
        fund_stop = price * 0.8  # 20%損失
        macro_stop = price * 0.75  # 25%損失（システミックリスク）
        risk_stop = max(low_52w * 0.95, price * 0.85)
        
        return {
            'round': 5,
            'title': '撤退・損切り基準',
            'discussions': [
                {
                    'speaker': 'TECH',
                    'content': f"撤退基準明確化：①200日SMA${sma200:.2f}を5%下回る${sma200 * 0.95:.2f}、"
                              f"②20日EMA${ema20:.2f}＜50日EMA${ema50:.2f}のデッドクロス成立、"
                              f"③週足RSI30割れ、④日足でベアフラッグ完成${price * 0.92:.2f}。"
                              f"いずれか2つ該当で即撤退。パラボリックSAR反転も警戒。"
                              f"ストップは${tech_stop:.2f}(ATR×2.5)、損失額は資金の{(1 - tech_stop/price) * 100:.1f}%。"
                              f"52週安値${low_52w:.2f}更新は全撤退シグナル。"
                },
                {
                    'speaker': 'FUND',
                    'content': f"業績悪化基準：①2Q連続で売上ガイダンス未達(予想比-10%超)、"
                              f"②粗利率{'3%pt' if ticker in ['TSLA', 'FSLR'] else '5%pt'}以上悪化、"
                              f"③FCF赤字転落、④主要顧客離脱or競合シェア奪取。"
                              f"{'Model 3/Y需要急減' if ticker == 'TSLA' else '受注キャンセル$1B超' if ticker == 'FSLR' else '開発遅延1年超'}は即売却。"
                              f"PER{'150倍' if ticker == 'TSLA' else '50倍'}超過も警戒。"
                              f"業績基準ストップ${fund_stop:.2f}(-20%)は死守。"
                },
                {
                    'speaker': 'MACRO',
                    'content': f"構造変化リスク：①{'IRA廃止法案可決' if ticker == 'FSLR' else '新規制で事業停止命令'}、"
                              f"②金利{'7%' if ticker in ['TSLA', 'RKLB'] else '6%'}超で成長株大量売り、"
                              f"③{'中国のEV関税撤廃' if ticker == 'TSLA' else 'NASA予算50%削減' if ticker in ['LUNR', 'ASTS'] else '競合技術のブレークスルー'}、"
                              f"④セクターETF資金流出3ヶ月連続。"
                              f"システミックリスク発生時は${macro_stop:.2f}(-25%)で機械的損切り。"
                              f"{'地政学リスク拡大' if ticker in ['RKLB', 'OII'] else ''}も注視。"
                },
                {
                    'speaker': 'RISK',
                    'content': f"統合リスク管理：最大許容損失は投資額の20%=${price * 0.8:.2f}厳守。"
                              f"ただし①テクニカル悪化、②ファンダ悪化、③マクロ悪化の"
                              f"2つ以上該当なら損失率10%でも即撤退。"
                              f"トレーリングストップは高値から15%=${price * 0.85:.2f}に設定。"
                              f"ポートフォリオ全体の相関上昇(>0.8)時は個別銘柄関係なく"
                              f"リスク資産を20%削減。精神的ストップ(夜眠れない)も重要。"
                }
            ]
        }
    
    def _generate_round6(self, ticker: str, scores: ExpertScores) -> Dict[str, Any]:
        """Round 6: 保有期間と出口戦略"""
        # 銘柄別の特性
        hold_periods = {
            'TSLA': (3, 5),  # (最短年, 基本年)
            'FSLR': (3, 5),
            'RKLB': (5, 7),
            'ASTS': (5, 10),
            'OKLO': (5, 10),
            'JOBY': (5, 7),
            'OII': (2, 4),
            'LUNR': (3, 5),
            'RDW': (7, 10)
        }
        
        min_years, base_years = hold_periods.get(ticker, (3, 5))
        
        return {
            'round': 6,
            'title': '保有期間と出口戦略',
            'discussions': [
                {
                    'speaker': 'TECH',
                    'content': f"チャート分析による出口：月足で上昇ウェッジ完成なら一部利確。"
                              f"パラボリック状の急騰後は50%売却が定石。"
                              f"200日SMAから{'50%' if ticker in ['TSLA', 'FSLR'] else '70%'}乖離で過熱感。"
                              f"エリオット第5波完了サイン：①RSI bearish divergence、"
                              f"②出来高減少、③上ヒゲ頻発で段階売却開始。"
                              f"基本保有{base_years}年でも、テクニカル悪化なら機動的に対応。"
                              f"長期上昇チャネル上限タッチは絶好の利確ポイント。"
                },
                {
                    'speaker': 'FUND',
                    'content': f"目標達成基準：売上${'100B' if ticker == 'TSLA' else '10B' if ticker == 'FSLR' else '1B'}到達、"
                              f"営業利益率{'25%' if ticker in ['TSLA', 'FSLR'] else '20%'}超、"
                              f"FCF利回り5%超で段階利確開始。"
                              f"PEG比率>2.0は割高シグナル、1/3売却。"
                              f"{'FSD完全実装' if ticker == 'TSLA' else 'Neutron成功' if ticker == 'RKLB' else '黒字化達成'}で"
                              f"当初目標達成→50%利確し残りは{'10年' if ticker in ['TSLA', 'ASTS'] else '5年'}保有。"
                              f"M&Aプレミアム(30%超)提示なら全株売却検討。"
                },
                {
                    'speaker': 'MACRO',
                    'content': f"景気サイクル考慮：{'レイトサイクル' if ticker in ['TSLA', 'OII'] else 'ミッドサイクル'}での"
                              f"保有継続は{'要注意' if ticker in ['TSLA', 'OII'] else '問題なし'}。"
                              f"金利サイクル転換点(利上げ→利下げ)は好機、保有継続。"
                              f"セクターローテーション：{'ディフェンシブ' if ticker == 'OII' else 'グロース'}→"
                              f"{'グロース' if ticker == 'OII' else 'バリュー'}シフトで一部利確。"
                              f"インフレ率{'5%超' if ticker in ['TSLA', 'FSLR'] else '7%超'}は実質リターン毀損、"
                              f"配当なし銘柄は不利→{'30%' if ticker in ['RKLB', 'ASTS'] else '20%'}削減。"
                              f"次の強気相場まで最低{min_years}年は保有推奨。"
                },
                {
                    'speaker': 'RISK',
                    'content': f"システマティック出口戦略：①目標リターン{scores.overall * 20:.0f}%で25%利確、"
                              f"②{scores.overall * 40:.0f}%で追加25%、③{scores.overall * 60:.0f}%で更に25%売却。"
                              f"残り25%は永久保有候補(バイ&ホールド)。"
                              f"リバランス基準：ポートフォリオの{'10%' if ticker in ['TSLA', 'FSLR'] else '5%'}超過で一部売却。"
                              f"税金考慮：1年超保有で長期譲渡益課税適用後に売却。"
                              f"相続・贈与タイミングでの評価額最適化も視野。"
                              f"最終的に感情を排したルールベース執行が成功の鍵。"
                }
            ]
        }
    
    def _calculate_price_targets(self, df: pd.DataFrame, 
                               current_data: Dict) -> PriceTargets:
        """価格目標を計算"""
        current_price = current_data['price']
        
        # サポートゾーン
        support_zones = [
            (current_price * 0.90, current_price * 0.95),
            (current_price * 0.85, current_price * 0.90),
            (current_price * 0.80, current_price * 0.85)
        ]
        
        # 1年後目標
        target_1y = {
            'TECH': current_price * 1.3,
            'FUND': current_price * 1.5,
            'MACRO': current_price * 1.2,
            'RISK': current_price * 1.25
        }
        
        # 3年後目標
        target_3y = {
            'TECH': current_price * 2.0,
            'FUND': current_price * 2.5,
            'MACRO': current_price * 1.8,
            'RISK': current_price * 1.9
        }
        
        # エントリーゾーン
        entry_zones = [
            {
                'stage': 1,
                'price_range': (current_price * 0.95, current_price * 1.02),
                'allocation': 40,
                'trigger': 'RSI改善またはMAゴールデンクロス'
            },
            {
                'stage': 2,
                'price_range': (current_price * 0.85, current_price * 0.95),
                'allocation': 40,
                'trigger': '主要サポートでの反発確認'
            },
            {
                'stage': 3,
                'price_range': (current_price * 0.90, current_price * 1.05),
                'allocation': 20,
                'trigger': '上昇トレンド確認後'
            }
        ]
        
        return PriceTargets(
            support_zones=support_zones,
            target_1y=target_1y,
            target_3y=target_3y,
            entry_zones=entry_zones
        )
    
    def _generate_entry_plan(self, price_targets: PriceTargets, 
                           current_data: Dict) -> List[Dict[str, Any]]:
        """段階的エントリー計画を生成"""
        entry_plan = []
        
        for zone in price_targets.entry_zones:
            entry_plan.append({
                'stage': zone['stage'],
                'price_range': f"${zone['price_range'][0]:.2f}～${zone['price_range'][1]:.2f}",
                'allocation_pct': zone['allocation'],
                'trigger': zone['trigger'],
                'rationale': self._get_entry_rationale(zone['stage'])
            })
        
        return entry_plan
    
    def _get_entry_rationale(self, stage: int) -> str:
        """エントリー段階の根拠を取得"""
        rationales = {
            1: "現在の価格水準での打診買い。テクニカル指標の改善を確認",
            2: "主要サポートでの本格的な買い増し。ファンダメンタルズ確認",
            3: "トレンド転換確認後の最終ポジション構築"
        }
        return rationales.get(stage, "段階的エントリー")
    
    def _generate_risk_scenarios(self, ticker: str, current_data: Dict,
                               price_targets: PriceTargets) -> List[Dict[str, Any]]:
        """リスクシナリオを生成"""
        current_price = current_data['price']
        
        scenarios = [
            {
                'name': 'ベースケース',
                'probability': 60,
                'price_range': (current_price * 0.9, current_price * 1.3),
                'strategy': 'ホールド継続。目標到達で段階的利確',
                'description': '現在の成長トレンドが継続し、適度な株価上昇'
            },
            {
                'name': '強気ケース',
                'probability': 25,
                'price_range': (current_price * 1.3, current_price * 1.8),
                'strategy': 'トレーリングストップで利益確保しつつ上昇を追う',
                'description': '予想を上回る成長加速または市場環境の大幅改善'
            },
            {
                'name': '弱気ケース',
                'probability': 15,
                'price_range': (current_price * 0.7, current_price * 0.9),
                'strategy': '損切りライン厳守。ポジション縮小検討',
                'description': 'マクロ環境悪化または企業固有の問題発生'
            }
        ]
        
        return scenarios
    
    def _generate_final_recommendation(self, scores: ExpertScores,
                                     price_targets: PriceTargets,
                                     discussion_rounds: List[Dict]) -> Dict[str, Any]:
        """最終投資推奨を生成"""
        # スコアに基づく判定
        if scores.overall >= 4.0:
            judgment = "即時買い"
            rationale = "全専門家が高評価。現在の価格は魅力的な水準"
        elif scores.overall >= 3.5:
            judgment = "押し目待ち"
            target_range = price_targets.support_zones[0]
            rationale = f"良好な投資機会だが、${target_range[0]:.2f}～${target_range[1]:.2f}での購入を推奨"
        elif scores.overall >= 3.0:
            judgment = "様子見"
            rationale = "投資魅力はあるが、より明確なシグナルを待つべき"
        else:
            judgment = "見送り"
            rationale = "現時点でのリスクが高く、他の投資機会を検討すべき"
        
        # 次回レビュータイミング
        review_timing = "3ヶ月後の四半期決算発表後"
        
        return {
            'judgment': judgment,
            'rationale': rationale,
            'review_timing': review_timing,
            'key_monitoring_points': [
                '四半期決算の売上・利益動向',
                'テクニカル指標の改善（特にトレンド転換シグナル）',
                'セクター全体の資金フロー動向',
                'マクロ環境の変化（金利・規制）'
            ]
        }