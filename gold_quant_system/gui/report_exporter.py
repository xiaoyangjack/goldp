#!/usr/bin/env python3
"""
回测报告导出管理器
支持多格式导出：PDF、Excel/CSV、Markdown
"""

import os
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

# 导入报告模板系统
from gold_quant_system.core.report_templates import ReportTemplates


class ReportExporter:
    """报告导出管理器"""
    
    def __init__(self, export_dir=None):
        self.export_dir = export_dir or Path.home() / "Downloads" / "GoldQuant_Reports"
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.report_templates = ReportTemplates()
        logger.info(f"报告导出目录: {self.export_dir}")
    
    def _get_timestamp(self):
        """获取时间戳"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_all(self, backtest_results, analysis_results, factor_data, params=None, progress_callback=None):
        """导出所有格式的报告"""
        timestamp = self._get_timestamp()
        results = {}
        formats = ['markdown', 'csv', 'excel', 'pdf']
        total_steps = len(formats)
        
        for i, fmt in enumerate(formats):
            if progress_callback:
                progress = int((i / total_steps) * 100)
                progress_callback(progress, f"正在导出 {fmt.upper()} 格式...")
            
            try:
                if fmt == 'markdown':
                    results[fmt] = self.export_markdown(backtest_results, analysis_results, factor_data, params, timestamp)
                elif fmt == 'csv':
                    results[fmt] = self.export_csv(backtest_results, analysis_results, timestamp)
                elif fmt == 'excel':
                    results[fmt] = self.export_excel(backtest_results, analysis_results, timestamp)
                elif fmt == 'pdf':
                    results[fmt] = self.export_pdf(backtest_results, analysis_results, factor_data, params, timestamp)
            except Exception as e:
                logger.error(f"导出{fmt}失败: {e}")
                # 重试一次
                try:
                    if progress_callback:
                        progress_callback(progress, f"导出{fmt}失败，正在重试...")
                    if fmt == 'markdown':
                        results[fmt] = self.export_markdown(backtest_results, analysis_results, factor_data, params, timestamp)
                    elif fmt == 'csv':
                        results[fmt] = self.export_csv(backtest_results, analysis_results, timestamp)
                    elif fmt == 'excel':
                        results[fmt] = self.export_excel(backtest_results, analysis_results, timestamp)
                    elif fmt == 'pdf':
                        results[fmt] = self.export_pdf(backtest_results, analysis_results, factor_data, params, timestamp)
                except Exception as e2:
                    logger.error(f"重试导出{fmt}失败: {e2}")
                    results[fmt] = None
        
        if progress_callback:
            progress_callback(100, "导出完成")
        
        return results
    
    def export_standard_reports(self, backtest_results, analysis_results, factor_data, params=None):
        """导出所有标准化报告"""
        timestamp = self._get_timestamp()
        results = {}
        
        report_types = {
            'performance': '策略整体绩效评价报告',
            'trading_behavior': '策略交易行为分析报告',
            'factor_effectiveness': '因子有效性分析报告',
            'risk_attribution': '策略风险归因分析报告',
            'param_sensitivity': '策略参数敏感性分析报告',
            'out_of_sample': '策略样本外有效性验证报告',
            'portfolio_optimization': '多策略组合优化分析报告',
            'sector_adaptability': '行业与个股适配性分析报告',
            'implementation_feasibility': '策略实盘落地可行性分析报告',
            'optimization_suggestions': '策略迭代与优化建议报告'
        }
        
        for report_type, report_name in report_types.items():
            try:
                # 导出Markdown格式
                md_file = self.export_template_report(report_type, backtest_results, analysis_results, 
                                                    factor_data, params, timestamp, 'markdown')
                # 导出PDF格式
                pdf_file = self.export_template_report(report_type, backtest_results, analysis_results, 
                                                    factor_data, params, timestamp, 'pdf')
                # 导出Excel格式
                excel_file = self.export_template_report(report_type, backtest_results, analysis_results, 
                                                      factor_data, params, timestamp, 'excel')
                
                results[report_type] = {
                    'name': report_name,
                    'markdown': md_file,
                    'pdf': pdf_file,
                    'excel': excel_file
                }
                logger.info(f"{report_name} 已导出")
            except Exception as e:
                logger.error(f"导出{report_name}失败: {e}")
                results[report_type] = {
                    'name': report_name,
                    'markdown': None,
                    'pdf': None,
                    'excel': None
                }
        
        return results
    
    def export_template_report(self, report_type, backtest_results, analysis_results, factor_data, params=None, timestamp=None, format='markdown'):
        """导出指定类型的报告"""
        timestamp = timestamp or self._get_timestamp()
        report_name = self._get_report_name(report_type)
        
        if format == 'markdown':
            filename = f"GoldQuant_{report_type}_{timestamp}.md"
            filepath = self.export_dir / filename
            content = self.report_templates.generate_report(report_type, backtest_results, analysis_results, factor_data, params)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"{report_name} Markdown已导出: {filepath}")
            return str(filepath)
        
        elif format == 'pdf':
            try:
                import markdown
                import weasyprint
            except ImportError:
                logger.warning("markdown或weasyprint未安装，跳过PDF导出")
                return None
            
            md_filename = f"GoldQuant_{report_type}_{timestamp}.md"
            pdf_filename = f"GoldQuant_{report_type}_{timestamp}.pdf"
            md_filepath = self.export_dir / md_filename
            pdf_filepath = self.export_dir / pdf_filename
            
            try:
                md_content = self.report_templates.generate_report(report_type, backtest_results, analysis_results, factor_data, params)
                
                with open(md_filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                html_content = markdown.markdown(md_content, extensions=['extra', 'tables'])
                
                html_template = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>GoldQuant {report_name}</title>
                    <style>
                        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                               margin: 40px; line-height: 1.6; color: #1e293b; }}
                        h1 {{ color: #6366f1; border-bottom: 2px solid #6366f1; padding-bottom: 10px; }}
                        h2 {{ color: #4f46e5; margin-top: 30px; }}
                        h3 {{ color: #3730a3; }}
                        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                        th, td {{ border: 1px solid #e2e8f0; padding: 12px; text-align: left; }}
                        th {{ background-color: #f1f5f9; font-weight: 600; }}
                        code {{ background-color: #f1f5f9; padding: 2px 6px; border-radius: 4px; }}
                        .summary-box {{ background-color: #eff6ff; border-left: 4px solid #6366f1; 
                                       padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
                
                weasyprint.HTML(string=html_template).write_pdf(pdf_filepath)
                
                logger.info(f"{report_name} PDF已导出: {pdf_filepath}")
                return str(pdf_filepath)
            except Exception as e:
                logger.error(f"导出PDF失败: {e}")
                return None
        
        elif format == 'excel':
            try:
                import pandas as pd
            except ImportError:
                logger.warning("pandas未安装，跳过Excel导出")
                return None
            
            filename = f"GoldQuant_{report_type}_{timestamp}.xlsx"
            filepath = self.export_dir / filename
            
            try:
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    # 写入策略绩效数据
                    if backtest_results:
                        perf_data = []
                        for strategy_name, result in backtest_results.items():
                            stats = result.get('stats', {})
                            perf_data.append({
                                '策略': strategy_name,
                                '总收益': stats.get('total_return', 0) * 100,
                                '年化收益': stats.get('ann_return', 0) * 100,
                                '夏普比率': stats.get('sharpe', 0),
                                '最大回撤': stats.get('max_dd', 0) * 100,
                                '胜率': stats.get('win_rate', 0) * 100,
                                '交易次数': stats.get('n_trades', 0)
                            })
                        df_perf = pd.DataFrame(perf_data)
                        df_perf.to_excel(writer, sheet_name='绩效指标', index=False)
                    
                    # 写入交易数据
                    for strategy_name, result in backtest_results.items():
                        if 'trades' in result and result['trades'] is not None:
                            if isinstance(result['trades'], list):
                                df_trades = pd.DataFrame(result['trades'])
                            else:
                                df_trades = result['trades']
                            df_trades.to_excel(writer, sheet_name=f'{strategy_name}_交易', index=True)
                    
                    # 写入投资组合价值
                    for strategy_name, result in backtest_results.items():
                        if 'portfolio_values' in result and result['portfolio_values'] is not None:
                            df_portfolio = result['portfolio_values'].reset_index()
                            df_portfolio.columns = ['日期', '净值']
                            df_portfolio.to_excel(writer, sheet_name=f'{strategy_name}_净值', index=False)
                
                logger.info(f"{report_name} Excel已导出: {filepath}")
                return str(filepath)
            except Exception as e:
                logger.error(f"导出Excel失败: {e}")
                return None
        
        return None
    
    def _get_report_name(self, report_type):
        """获取报告名称"""
        report_names = {
            'performance': '策略整体绩效评价报告',
            'trading_behavior': '策略交易行为分析报告',
            'factor_effectiveness': '因子有效性分析报告',
            'risk_attribution': '策略风险归因分析报告',
            'param_sensitivity': '策略参数敏感性分析报告',
            'out_of_sample': '策略样本外有效性验证报告',
            'portfolio_optimization': '多策略组合优化分析报告',
            'sector_adaptability': '行业与个股适配性分析报告',
            'implementation_feasibility': '策略实盘落地可行性分析报告',
            'optimization_suggestions': '策略迭代与优化建议报告'
        }
        return report_names.get(report_type, report_type)
    
    def export_markdown(self, backtest_results, analysis_results, factor_data, params=None, timestamp=None):
        """导出Markdown格式报告"""
        timestamp = timestamp or self._get_timestamp()
        filename = f"GoldQuant_Report_{timestamp}.md"
        filepath = self.export_dir / filename
        
        content = self._generate_markdown_report(backtest_results, analysis_results, factor_data, params)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Markdown报告已导出: {filepath}")
        return str(filepath)
    
    def export_csv(self, backtest_results, analysis_results, timestamp=None):
        """导出CSV格式交易明细"""
        timestamp = timestamp or self._get_timestamp()
        files = []
        
        for strategy_name, result in backtest_results.items():
            filename = f"GoldQuant_{strategy_name}_Trades_{timestamp}.csv"
            filepath = self.export_dir / filename
            
            if 'trades' in result and result['trades'] is not None:
                if isinstance(result['trades'], list):
                    import pandas as pd
                    pd.DataFrame(result['trades']).to_csv(filepath, encoding='utf-8-sig', index=False)
                else:
                    result['trades'].to_csv(filepath, encoding='utf-8-sig')
                files.append(str(filepath))
                logger.info(f"CSV交易明细已导出: {filepath}")
        
        return files
    
    def export_excel(self, backtest_results, analysis_results, timestamp=None):
        """导出Excel格式报告"""
        try:
            import pandas as pd
        except ImportError:
            logger.warning("pandas未安装，跳过Excel导出")
            return None
        
        timestamp = timestamp or self._get_timestamp()
        filename = f"GoldQuant_Report_{timestamp}.xlsx"
        filepath = self.export_dir / filename
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for strategy_name, result in backtest_results.items():
                    if 'portfolio_values' in result and result['portfolio_values'] is not None:
                        df_portfolio = result['portfolio_values'].reset_index()
                        df_portfolio.columns = ['日期', '净值']
                        df_portfolio.to_excel(writer, sheet_name=f'{strategy_name}_净值', index=False)
                    
                    if 'trades' in result and result['trades'] is not None:
                        result['trades'].to_excel(writer, sheet_name=f'{strategy_name}_交易', index=True)
                
                logger.info(f"Excel报告已导出: {filepath}")
                return str(filepath)
        except Exception as e:
            logger.error(f"导出Excel失败: {e}")
            return None
    
    def export_pdf(self, backtest_results, analysis_results, factor_data, params=None, timestamp=None):
        """导出PDF格式报告"""
        try:
            import markdown
            import weasyprint
        except ImportError:
            logger.warning("markdown或weasyprint未安装，跳过PDF导出")
            return None
        
        timestamp = timestamp or self._get_timestamp()
        md_filename = f"GoldQuant_Report_{timestamp}.md"
        pdf_filename = f"GoldQuant_Report_{timestamp}.pdf"
        md_filepath = self.export_dir / md_filename
        pdf_filepath = self.export_dir / pdf_filename
        
        try:
            md_content = self._generate_markdown_report(backtest_results, analysis_results, factor_data, params)
            
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            html_content = markdown.markdown(md_content, extensions=['extra', 'tables'])
            
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>GoldQuant 回测报告</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                           margin: 40px; line-height: 1.6; color: #1e293b; }}
                    h1 {{ color: #6366f1; border-bottom: 2px solid #6366f1; padding-bottom: 10px; }}
                    h2 {{ color: #4f46e5; margin-top: 30px; }}
                    h3 {{ color: #3730a3; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #e2e8f0; padding: 12px; text-align: left; }}
                    th {{ background-color: #f1f5f9; font-weight: 600; }}
                    code {{ background-color: #f1f5f9; padding: 2px 6px; border-radius: 4px; }}
                    .summary-box {{ background-color: #eff6ff; border-left: 4px solid #6366f1; 
                                   padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            weasyprint.HTML(string=html_template).write_pdf(pdf_filepath)
            
            logger.info(f"PDF报告已导出: {pdf_filepath}")
            return str(pdf_filepath)
        except Exception as e:
            logger.error(f"导出PDF失败: {e}")
            return None
    
    def _generate_markdown_report(self, backtest_results, analysis_results, factor_data, params=None):
        """生成Markdown报告内容"""
        lines = []
        
        lines.append("# 📊 GoldQuant 量化策略回测报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append("## 📋 策略概览")
        lines.append("")
        lines.append(f"- **回测策略数量**: {len(backtest_results)}")
        lines.append(f"- **策略列表**: {', '.join(backtest_results.keys())}")
        lines.append("")
        
        if params:
            lines.append("## ⚙️ 回测参数")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(params, indent=2, ensure_ascii=False))
            lines.append("```")
            lines.append("")
        
        lines.append("## 📈 绩效指标汇总")
        lines.append("")
        
        table_header = "| 策略 | 年化收益 | 最大回撤 | 夏普比率 | 胜率 | 盈亏比 |"
        table_separator = "|--------|----------|----------|----------|------|--------|"
        lines.append(table_header)
        lines.append(table_separator)
        
        for strategy_name, result in backtest_results.items():
            metrics = result.get('metrics', {})
            annual_return = metrics.get('annual_return', 0) * 100
            max_drawdown = metrics.get('max_drawdown', 0) * 100
            sharpe = metrics.get('sharpe_ratio', 0)
            win_rate = metrics.get('win_rate', 0) * 100
            profit_factor = metrics.get('profit_factor', 0)
            
            lines.append(
                f"| {strategy_name} | {annual_return:.2f}% | {max_drawdown:.2f}% | "
                f"{sharpe:.2f} | {win_rate:.2f}% | {profit_factor:.2f} |"
            )
        
        lines.append("")
        
        lines.append("## 📝 详细说明")
        lines.append("")
        lines.append("本报告由 GoldQuant 量化策略回测系统自动生成。")
        lines.append("")
        lines.append("### 指标说明")
        lines.append("")
        lines.append("- **年化收益**: 策略年化收益率")
        lines.append("- **最大回撤**: 策略历史最大回撤幅度")
        lines.append("- **夏普比率**: 风险调整后收益指标")
        lines.append("- **胜率**: 盈利交易占比")
        lines.append("- **盈亏比**: 平均盈利与平均亏损的比值")
        lines.append("")
        
        return "\n".join(lines)
