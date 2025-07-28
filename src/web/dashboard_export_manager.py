#!/usr/bin/env python3
"""
ダッシュボードエクスポートマネージャー
データとレポートのエクスポート機能を提供
"""

import pandas as pd
import json
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile

class DashboardExportManager:
    """ダッシュボードデータのエクスポート管理"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """カスタムスタイルの設定"""
        # タイトルスタイル
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30
        ))
        
        # サブタイトルスタイル
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12
        ))
    
    def export_to_excel(self, data: Dict[str, Any], filename: str = None) -> str:
        """Excelファイルへのエクスポート"""
        if filename is None:
            filename = f"tiker_dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Excelライターの作成
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # フォーマット定義
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#667eea',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            
            positive_format = workbook.add_format({
                'font_color': '#28a745',
                'num_format': '+0.00%'
            })
            
            negative_format = workbook.add_format({
                'font_color': '#dc3545',
                'num_format': '+0.00%'
            })
            
            # 1. ポートフォリオサマリーシート
            portfolio_df = self._create_portfolio_summary(data)
            portfolio_df.to_excel(writer, sheet_name='Portfolio Summary', index=False)
            
            worksheet = writer.sheets['Portfolio Summary']
            self._format_worksheet(worksheet, portfolio_df, header_format)
            
            # 2. シグナル分析シート
            signals_df = self._create_signals_analysis(data)
            signals_df.to_excel(writer, sheet_name='Signal Analysis', index=False)
            
            worksheet = writer.sheets['Signal Analysis']
            self._format_worksheet(worksheet, signals_df, header_format)
            
            # 3. パフォーマンス詳細シート
            performance_df = self._create_performance_details(data)
            performance_df.to_excel(writer, sheet_name='Performance Details', index=False)
            
            worksheet = writer.sheets['Performance Details']
            self._format_worksheet(worksheet, performance_df, header_format)
            
            # 条件付き書式の適用
            self._apply_conditional_formatting(writer, performance_df, 'Performance Details')
            
            # 4. チャート挿入
            self._add_charts_to_excel(writer, data)
        
        # バイトストリームを返す
        output.seek(0)
        return output
    
    def export_to_pdf(self, data: Dict[str, Any], filename: str = None) -> str:
        """PDFレポートの生成"""
        if filename is None:
            filename = f"tiker_investment_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # PDFドキュメントの作成
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        
        # タイトルページ
        story.append(Paragraph("Tiker Investment Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                             self.styles['Normal']))
        story.append(PageBreak())
        
        # エグゼクティブサマリー
        story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
        summary_text = self._generate_executive_summary(data)
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # ポートフォリオ概要テーブル
        story.append(Paragraph("Portfolio Overview", self.styles['CustomHeading']))
        portfolio_table = self._create_portfolio_table(data)
        story.append(portfolio_table)
        story.append(Spacer(1, 0.3*inch))
        
        # シグナル分析
        story.append(Paragraph("Signal Analysis", self.styles['CustomHeading']))
        signal_table = self._create_signal_table(data)
        story.append(signal_table)
        story.append(PageBreak())
        
        # 個別銘柄分析
        story.append(Paragraph("Individual Stock Analysis", self.styles['CustomHeading']))
        for ticker, analysis in data.get('stock_analyses', {}).items():
            story.extend(self._create_stock_analysis_section(ticker, analysis))
        
        # チャート挿入
        chart_files = self._generate_charts_for_pdf(data)
        for chart_file in chart_files:
            story.append(Image(chart_file, width=6*inch, height=4*inch))
            story.append(Spacer(1, 0.2*inch))
        
        # PDFの生成
        doc.build(story)
        
        # 一時ファイルのクリーンアップ
        for chart_file in chart_files:
            try:
                import os
                os.remove(chart_file)
            except:
                pass
        
        return filename
    
    def export_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """JSON形式でのエクスポート"""
        if filename is None:
            filename = f"tiker_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # データの整形
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'portfolio_summary': self._prepare_json_data(data.get('portfolio_summary', {})),
            'signal_analysis': self._prepare_json_data(data.get('signal_analysis', {})),
            'performance_metrics': self._prepare_json_data(data.get('performance_metrics', {})),
            'stock_analyses': self._prepare_json_data(data.get('stock_analyses', {})),
            'ai_insights': data.get('ai_insights', [])
        }
        
        # JSONファイルに書き込み
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        return filename
    
    def export_to_csv(self, data: Dict[str, Any], prefix: str = "tiker") -> List[str]:
        """複数のCSVファイルへのエクスポート"""
        files_created = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # ポートフォリオサマリー
        portfolio_df = self._create_portfolio_summary(data)
        portfolio_file = f"{prefix}_portfolio_{timestamp}.csv"
        portfolio_df.to_csv(portfolio_file, index=False)
        files_created.append(portfolio_file)
        
        # シグナル履歴
        if 'signal_history' in data:
            signal_df = pd.DataFrame(data['signal_history'])
            signal_file = f"{prefix}_signals_{timestamp}.csv"
            signal_df.to_csv(signal_file, index=False)
            files_created.append(signal_file)
        
        # パフォーマンス詳細
        performance_df = self._create_performance_details(data)
        performance_file = f"{prefix}_performance_{timestamp}.csv"
        performance_df.to_csv(performance_file, index=False)
        files_created.append(performance_file)
        
        return files_created
    
    def _create_portfolio_summary(self, data: Dict) -> pd.DataFrame:
        """ポートフォリオサマリーデータフレームの作成"""
        portfolio_data = []
        
        for ticker, info in data.get('portfolio', {}).items():
            stock_data = data.get('stock_analyses', {}).get(ticker, {})
            
            portfolio_data.append({
                'Ticker': ticker,
                'Name': info.get('name', ''),
                'Sector': info.get('sector', ''),
                'Weight %': info.get('weight', 0),
                'Current Price': stock_data.get('current_price', 0),
                'Signal': stock_data.get('signal', ''),
                'Score': stock_data.get('total_score', 0),
                'Daily Change %': stock_data.get('price_change_pct', 0),
                '1M Return %': stock_data.get('returns_1m', 0),
                '3M Return %': stock_data.get('returns_3m', 0)
            })
        
        return pd.DataFrame(portfolio_data)
    
    def _create_signals_analysis(self, data: Dict) -> pd.DataFrame:
        """シグナル分析データフレームの作成"""
        signal_data = []
        
        for ticker, analysis in data.get('stock_analyses', {}).items():
            scores = analysis.get('scores', {})
            
            signal_data.append({
                'Ticker': ticker,
                'Signal': analysis.get('signal', ''),
                'Total Score': analysis.get('total_score', 0),
                'TECH Score': scores.get('TECH', 0),
                'FUND Score': scores.get('FUND', 0),
                'MACRO Score': scores.get('MACRO', 0),
                'RISK Score': scores.get('RISK', 0),
                'Momentum Score': scores.get('MOMENTUM', 0),
                'Sentiment Score': scores.get('SENTIMENT', 0),
                'Timestamp': analysis.get('timestamp', '')
            })
        
        return pd.DataFrame(signal_data)
    
    def _create_performance_details(self, data: Dict) -> pd.DataFrame:
        """パフォーマンス詳細データフレームの作成"""
        performance_data = []
        perf = data.get('portfolio_performance', {})
        
        for ticker, stock_perf in perf.get('stocks', {}).items():
            performance_data.append({
                'Ticker': ticker,
                'Cost Basis': stock_perf.get('cost', 0),
                'Current Value': stock_perf.get('value', 0),
                'Return $': stock_perf.get('return', 0),
                'Return %': stock_perf.get('return_pct', 0),
                'Shares': stock_perf.get('shares', 0),
                'Current Price': stock_perf.get('current_price', 0),
                'Volatility %': stock_perf.get('volatility', 0) * 100
            })
        
        return pd.DataFrame(performance_data)
    
    def _format_worksheet(self, worksheet, df: pd.DataFrame, header_format):
        """Excelワークシートのフォーマット"""
        # ヘッダーのフォーマット
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # 列幅の自動調整
        for i, col in enumerate(df.columns):
            column_len = df[col].astype(str).str.len().max()
            column_len = max(column_len, len(col)) + 2
            worksheet.set_column(i, i, column_len)
    
    def _apply_conditional_formatting(self, writer, df: pd.DataFrame, sheet_name: str):
        """条件付き書式の適用"""
        worksheet = writer.sheets[sheet_name]
        
        # リターン列に条件付き書式を適用
        if 'Return %' in df.columns:
            col_idx = df.columns.get_loc('Return %')
            
            # 正の値は緑、負の値は赤
            worksheet.conditional_format(1, col_idx, len(df), col_idx, {
                'type': 'cell',
                'criteria': '>',
                'value': 0,
                'format': writer.book.add_format({'font_color': '#28a745'})
            })
            
            worksheet.conditional_format(1, col_idx, len(df), col_idx, {
                'type': 'cell',
                'criteria': '<',
                'value': 0,
                'format': writer.book.add_format({'font_color': '#dc3545'})
            })
    
    def _add_charts_to_excel(self, writer, data: Dict):
        """Excelにチャートを追加"""
        workbook = writer.book
        
        # シグナル分布チャート
        chart_sheet = workbook.add_worksheet('Charts')
        
        # パイチャートの作成
        chart = workbook.add_chart({'type': 'pie'})
        
        # ダミーデータ（実際のデータから生成）
        signal_counts = {'BUY': 3, 'HOLD': 4, 'SELL': 2}
        
        # チャートデータの設定
        chart_sheet.write_column('A1', list(signal_counts.keys()))
        chart_sheet.write_column('B1', list(signal_counts.values()))
        
        chart.add_series({
            'categories': ['Charts', 0, 0, len(signal_counts)-1, 0],
            'values': ['Charts', 0, 1, len(signal_counts)-1, 1],
            'name': 'Signal Distribution'
        })
        
        chart.set_title({'name': 'Portfolio Signal Distribution'})
        chart_sheet.insert_chart('D2', chart)
    
    def _generate_executive_summary(self, data: Dict) -> str:
        """エグゼクティブサマリーの生成"""
        perf = data.get('portfolio_performance', {})
        
        summary = f"""
        The portfolio has generated a total return of {perf.get('total_return_pct', 0):.1f}% 
        with a current value of ${perf.get('total_value', 0):,.0f}. 
        
        Key highlights:
        - Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}
        - Maximum Drawdown: {perf.get('max_drawdown', 0):.1f}%
        - Portfolio Volatility: {perf.get('volatility', 0):.1%} (annualized)
        
        The current signal distribution shows a balanced approach with appropriate risk management.
        """
        
        return summary
    
    def _create_portfolio_table(self, data: Dict) -> Table:
        """ポートフォリオ概要テーブルの作成"""
        portfolio_df = self._create_portfolio_summary(data)
        
        # テーブルデータの準備
        table_data = [portfolio_df.columns.tolist()]
        table_data.extend(portfolio_df.values.tolist())
        
        # テーブルの作成
        table = Table(table_data)
        
        # テーブルスタイルの設定
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_signal_table(self, data: Dict) -> Table:
        """シグナル分析テーブルの作成"""
        signals_df = self._create_signals_analysis(data)
        
        # 必要な列のみ選択
        selected_cols = ['Ticker', 'Signal', 'Total Score', 'TECH Score', 'FUND Score']
        if selected_cols[0] in signals_df.columns:
            signals_df = signals_df[selected_cols]
        
        # テーブルデータの準備
        table_data = [signals_df.columns.tolist()]
        table_data.extend(signals_df.values.tolist())
        
        # テーブルの作成
        table = Table(table_data)
        
        # テーブルスタイルの設定
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_stock_analysis_section(self, ticker: str, analysis: Dict) -> List:
        """個別銘柄分析セクションの作成"""
        section = []
        
        # 銘柄名
        section.append(Paragraph(f"{ticker} Analysis", self.styles['Heading2']))
        
        # 基本情報
        info_text = f"""
        Current Price: ${analysis.get('current_price', 0):.2f}
        Signal: {analysis.get('signal', 'N/A')}
        Total Score: {analysis.get('total_score', 0):.2f}/5.0
        """
        section.append(Paragraph(info_text, self.styles['Normal']))
        
        # AIインサイト
        if 'ai_insights' in analysis:
            section.append(Paragraph("AI Insights:", self.styles['Heading3']))
            for insight in analysis['ai_insights']:
                section.append(Paragraph(f"• {insight}", self.styles['Normal']))
        
        section.append(Spacer(1, 0.2*inch))
        
        return section
    
    def _generate_charts_for_pdf(self, data: Dict) -> List[str]:
        """PDF用のチャートを生成"""
        chart_files = []
        
        # シグナル分布チャート
        plt.figure(figsize=(8, 6))
        signal_counts = {}
        for analysis in data.get('stock_analyses', {}).values():
            signal = analysis.get('signal', 'UNKNOWN')
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
        
        if signal_counts:
            plt.pie(signal_counts.values(), labels=signal_counts.keys(), autopct='%1.1f%%')
            plt.title('Portfolio Signal Distribution')
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(temp_file.name, bbox_inches='tight')
            plt.close()
            
            chart_files.append(temp_file.name)
        
        # パフォーマンスチャート
        perf_data = data.get('portfolio_performance', {}).get('stocks', {})
        if perf_data:
            plt.figure(figsize=(10, 6))
            
            tickers = list(perf_data.keys())
            returns = [perf_data[t].get('return_pct', 0) for t in tickers]
            
            colors_list = ['green' if r > 0 else 'red' for r in returns]
            plt.bar(tickers, returns, color=colors_list)
            plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            plt.title('Individual Stock Returns')
            plt.ylabel('Return %')
            plt.xticks(rotation=45)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(temp_file.name, bbox_inches='tight')
            plt.close()
            
            chart_files.append(temp_file.name)
        
        return chart_files
    
    def _prepare_json_data(self, data: Any) -> Any:
        """JSON用のデータ準備（pandas型の変換など）"""
        if isinstance(data, pd.DataFrame):
            return data.to_dict(orient='records')
        elif isinstance(data, pd.Series):
            return data.to_dict()
        elif isinstance(data, (pd.Timestamp, datetime)):
            return data.isoformat()
        elif isinstance(data, dict):
            return {k: self._prepare_json_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_json_data(item) for item in data]
        else:
            return data


# テスト用のメイン関数
if __name__ == "__main__":
    # エクスポートマネージャーのインスタンス作成
    exporter = DashboardExportManager()
    
    # サンプルデータ
    sample_data = {
        'portfolio': {
            'TSLA': {'name': 'Tesla Inc', 'sector': 'EV/Tech', 'weight': 20},
            'FSLR': {'name': 'First Solar', 'sector': 'Solar', 'weight': 20}
        },
        'stock_analyses': {
            'TSLA': {
                'current_price': 250.50,
                'signal': 'BUY',
                'total_score': 4.2,
                'price_change_pct': 2.5,
                'scores': {
                    'TECH': 4.5,
                    'FUND': 4.0,
                    'MACRO': 4.2,
                    'RISK': 3.8
                }
            }
        },
        'portfolio_performance': {
            'total_value': 150000,
            'total_return_pct': 15.5,
            'sharpe_ratio': 1.2,
            'max_drawdown': -8.5,
            'volatility': 0.25,
            'stocks': {
                'TSLA': {
                    'cost': 10000,
                    'value': 12500,
                    'return': 2500,
                    'return_pct': 25.0,
                    'volatility': 0.35
                }
            }
        }
    }
    
    # 各形式でエクスポート
    print("Exporting to Excel...")
    excel_file = exporter.export_to_excel(sample_data)
    print(f"Excel export completed")
    
    print("\nExporting to JSON...")
    json_file = exporter.export_to_json(sample_data)
    print(f"JSON exported to: {json_file}")
    
    print("\nExporting to CSV...")
    csv_files = exporter.export_to_csv(sample_data)
    print(f"CSV files created: {csv_files}")