# -*- coding: utf-8 -*-
"""
控制台輸出模組
Console Output Module

格式化輸出分析結果到控制台
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import textwrap

logger = logging.getLogger(__name__)


class ConsoleOutput:
    """控制台輸出器"""

    def __init__(self, width: int = 80):
        self.width = width
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m'
        }

    def print_header(self, title: str, subtitle: str = None):
        """打印標題"""
        print("\n" + "=" * self.width)
        print(f"{self.colors['bold']}{self.colors['cyan']}{title.center(self.width)}{self.colors['reset']}")
        if subtitle:
            print(f"{self.colors['yellow']}{subtitle.center(self.width)}{self.colors['reset']}")
        print("=" * self.width)

    def print_section(self, title: str):
        """打印區段標題"""
        print(f"\n{self.colors['bold']}{self.colors['blue']}{'='*20} {title} {'='*20}{self.colors['reset']}")

    def print_subsection(self, title: str):
        """打印子區段標題"""
        print(f"\n{self.colors['bold']}{self.colors['green']}{title}{self.colors['reset']}")
        print("-" * len(title))

    def print_stock_analysis(self, analysis_data: Dict[str, Any]):
        """打印股票分析結果"""
        try:
            stock_code = analysis_data.get('stock_code', 'UNKNOWN')

            self.print_header(f"股票分析報告 - {stock_code}", f"分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # 基本信息
            self.print_section("基本信息")
            tech_data = analysis_data.get('technical_data', {})
            print(f"當前價格: {self._format_price(tech_data.get('current_price', 0))}")

            # 技術分析
            self.print_section("技術分析")
            self._print_technical_analysis(analysis_data)

            # 趨勢分析
            self.print_section("趨勢分析")
            self._print_trend_analysis(analysis_data)

            # 位階分析
            self.print_section("位階分析")
            self._print_position_analysis(analysis_data)

            # 策略建議
            self.print_section("策略建議")
            self._print_strategy_recommendation(analysis_data)

            # 風險評估
            self.print_section("風險評估")
            self._print_risk_assessment(analysis_data)

            # 綜合評分
            self.print_section("綜合評分")
            self._print_overall_score(analysis_data)

            # 投資建議
            self.print_section("投資建議")
            self._print_investment_recommendation(analysis_data)

        except Exception as e:
            logger.error(f"打印股票分析結果失敗: {e}")
            print(f"{self.colors['red']}打印分析結果時發生錯誤: {e}{self.colors['reset']}")

    def _print_technical_analysis(self, data: Dict[str, Any]):
        """打印技術分析"""
        tech_data = data.get('technical_data', {})

        print(f"均線系統:")
        print(f"  5日均線:  {self._format_price(tech_data.get('sma_5', 0))}")
        print(f"  20日均線: {self._format_price(tech_data.get('sma_20', 0))}")
        print(f"  60日均線: {self._format_price(tech_data.get('sma_60', 0))}")

        print(f"\n技術指標:")
        print(f"  RSI(14):  {tech_data.get('rsi', 0):.2f} {self._get_rsi_indicator(tech_data.get('rsi', 50))}")
        print(f"  MACD:     {tech_data.get('macd', 0):.3f}")
        print(f"  ATR:      {tech_data.get('atr', 0):.3f}")

        levels = data.get('levels', {})
        print(f"\n關鍵價位:")
        print(f"  支撐位:   {self._format_price(levels.get('support', 0))}")
        print(f"  阻力位:   {self._format_price(levels.get('resistance', 0))}")
        print(f"  買入區:   {self._format_price(levels.get('buy_zone', 0))}")
        print(f"  賣出區:   {self._format_price(levels.get('sell_zone', 0))}")

    def _print_trend_analysis(self, data: Dict[str, Any]):
        """打印趨勢分析"""
        trend_data = data.get('trend', {})

        trend = trend_data.get('trend', '未知')
        strength = trend_data.get('strength', 0)

        print(f"主要趨勢: {self._colorize_trend(trend)}")
        print(f"趨勢強度: {strength}/10 {self._get_strength_indicator(strength)}")

        print(f"\n技術指標狀態:")
        print(f"  RSI狀態:     {trend_data.get('rsi_status', '未知')}")
        print(f"  MACD狀態:    {trend_data.get('macd_status', '未知')}")
        print(f"  布林通道:    {trend_data.get('bollinger_status', '未知')}")
        print(f"  KD指標:      {trend_data.get('kd_status', '未知')} (K:{trend_data.get('k_value', 0):.1f}, D:{trend_data.get('d_value', 0):.1f})")

    def _print_position_analysis(self, data: Dict[str, Any]):
        """打印位階分析"""
        position_data = data.get('position', {})

        stage = position_data.get('stage', '未知')
        stage_desc = position_data.get('stage_desc', '')

        print(f"位階: {self._colorize_position(stage)}")
        print(f"描述: {stage_desc}")

        print(f"\n價格統計:")
        print(f"  年初最低: {self._format_price(position_data.get('yearly_low', 0))}")
        print(f"  年初最高: {self._format_price(position_data.get('yearly_high', 0))}")
        print(f"  當前位置: {position_data.get('current_pct', 0):.1f}%")

    def _print_strategy_recommendation(self, data: Dict[str, Any]):
        """打印策略建議"""
        strategy_data = data.get('strategy', {})

        print("短期策略 (1-5天):")
        print(f"  {strategy_data.get('short_term', '無建議')}")

        print("\n中期策略 (1-3個月):")
        print(f"  {strategy_data.get('medium_term', '無建議')}")

        print("\n長期策略 (3個月以上):")
        print(f"  {strategy_data.get('long_term', '無建議')}")

        levels = data.get('levels', {})
        if levels.get('target_price'):
            print(f"\n目標價位: {self._format_price(levels.get('target_price'))}")
        if levels.get('stop_loss_buy'):
            print(f"停損價位: {self._format_price(levels.get('stop_loss_buy'))}")

    def _print_risk_assessment(self, data: Dict[str, Any]):
        """打印風險評估"""
        risk_data = data.get('risk_assessment', {})

        risk_level = risk_data.get('風險等級', '未知')
        print(f"風險等級: {self._colorize_risk(risk_level)}")

        risk_factors = risk_data.get('風險因子', [])
        if risk_factors:
            print(f"\n風險因子:")
            for factor in risk_factors:
                print(f"  • {factor}")

        risk_desc = risk_data.get('風險評估', '')
        if risk_desc:
            print(f"\n風險評估: {risk_desc}")

    def _print_overall_score(self, data: Dict[str, Any]):
        """打印綜合評分"""
        score_data = data.get('overall_score', {})

        total_score = score_data.get('總分', 0)
        grade = score_data.get('等級', 'F')
        description = score_data.get('評價', '未知')

        print(f"綜合評分: {total_score}/100")
        print(f"等級: {self._colorize_grade(grade)}")
        print(f"評價: {description}")

        # 評分細項
        details = score_data.get('評分細項', {})
        if details:
            print(f"\n評分細項:")
            print(f"  收益率評分: {details.get('收益率評分', 0)}/25")
            print(f"  夏普比率評分: {details.get('夏普比率評分', 0)}/25")
            print(f"  回撤評分: {details.get('回撤評分', 0)}/25")
            print(f"  勝率評分: {details.get('勝率評分', 0)}/25")

    def _print_investment_recommendation(self, data: Dict[str, Any]):
        """打印投資建議"""
        recommendation = data.get('investment_recommendation', {})

        action = recommendation.get('操作建議', '未知')
        position = recommendation.get('倉位建議', '未知')
        holding = recommendation.get('持有期間', '未知')

        print(f"操作建議: {self._colorize_action(action)}")
        print(f"倉位建議: {position}")
        print(f"持有期間: {holding}")

        notes = recommendation.get('注意事項', [])
        if notes:
            print(f"\n注意事項:")
            for note in notes:
                wrapped_note = textwrap.fill(note, width=self.width-4)
                print(f"  {wrapped_note}")

    def print_portfolio_report(self, portfolio_data: Dict[str, Any]):
        """打印投資組合報告"""
        try:
            self.print_header("投資組合分析報告", f"分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # 績效總覽
            self.print_section("績效總覽")
            performance = portfolio_data.get('performance', {})
            print(f"總收益率: {performance.get('總收益率', 0):.2f}%")
            print(f"年化收益率: {performance.get('年化收益率', 0):.2f}%")
            print(f"勝率: {performance.get('勝率', 0):.2f}%")
            print(f"總交易次數: {performance.get('總交易次數', 0)}")

            # 風險指標
            risk = portfolio_data.get('risk_metrics', {})
            if risk:
                print(f"\n風險指標:")
                print(f"  夏普比率: {risk.get('sharpe_ratio', 0):.2f}")
                print(f"  最大回撤: {risk.get('max_drawdown', 0):.2f}%")
                print(f"  波動率: {risk.get('volatility', 0):.2f}%")

            # 持倉明細
            holdings = portfolio_data.get('holdings', [])
            if holdings:
                self.print_section("持倉明細")
                print(f"{'代碼':<10} {'名稱':<20} {'數量':<10} {'平均成本':<12} {'市值':<12} {'盈虧':<12}")
                print("-" * 80)

                for holding in holdings:
                    code = holding.get('code', '')
                    name = holding.get('name', '')[:18]  # 限制名稱長度
                    quantity = holding.get('quantity', 0)
                    avg_cost = holding.get('avg_cost', 0)
                    market_value = holding.get('market_value', 0)
                    profit_loss = holding.get('profit_loss', 0)

                    profit_color = self.colors['green'] if profit_loss > 0 else self.colors['red'] if profit_loss < 0 else ''

                    print(f"{code:<10} {name:<20} {quantity:<10,} "
                          f"{avg_cost:<12.2f} {market_value:<12,.0f} "
                          f"{profit_color}{profit_loss:<12,.0f}{self.colors['reset']}")

            # 月度績效
            monthly_perf = portfolio_data.get('monthly_performance', [])
            if monthly_perf:
                self.print_section("月度績效")
                print(f"{'月份':<10} {'交易次數':<12} {'總盈虧':<15} {'勝率':<10}")
                print("-" * 50)

                for month in monthly_perf:
                    month_name = month.get('月份', '')
                    trades = month.get('交易次數', 0)
                    profit = month.get('總盈虧', 0)
                    win_rate = month.get('勝率', 0)

                    profit_color = self.colors['green'] if profit > 0 else self.colors['red'] if profit < 0 else ''

                    print(f"{month_name:<10} {trades:<12} "
                          f"{profit_color}{profit:<15,.0f}{self.colors['reset']} "
                          f"{win_rate:<10.1f}%")

        except Exception as e:
            logger.error(f"打印投資組合報告失敗: {e}")
            print(f"{self.colors['red']}打印投資組合報告時發生錯誤: {e}{self.colors['reset']}")

    def print_strategy_backtest(self, backtest_data: Dict[str, Any]):
        """打印策略回測結果"""
        try:
            strategy_name = backtest_data.get('strategy_name', '未知策略')

            self.print_header(f"策略回測報告 - {strategy_name}", f"回測時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # 回測總結
            self.print_section("回測總結")
            print(f"回測期間: {backtest_data.get('backtest_period', '未知')}")
            print(f"初始資金: {backtest_data.get('initial_capital', 0):,.0f}")
            print(f"最終價值: {backtest_data.get('final_value', 0):,.0f}")
            print(f"總收益率: {backtest_data.get('total_return', 0):.2f}%")
            print(f"年化收益率: {backtest_data.get('annual_return', 0):.2f}%")

            # 績效指標
            self.print_section("績效指標")
            print(f"夏普比率: {backtest_data.get('sharpe_ratio', 0):.2f}")
            print(f"最大回撤: {backtest_data.get('max_drawdown', 0):.2f}%")
            print(f"勝率: {backtest_data.get('win_rate', 0):.2f}%")
            print(f"總交易次數: {backtest_data.get('total_trades', 0)}")

            # 訊號統計
            signals = backtest_data.get('signal_statistics', {})
            if signals:
                self.print_section("訊號統計")
                print(f"總訊號數: {signals.get('總訊號數', 0)}")
                print(f"買入訊號: {signals.get('買入訊號', 0)}")
                print(f"賣出訊號: {signals.get('賣出訊號', 0)}")

                signal_types = signals.get('訊號類型分布', {})
                if signal_types:
                    print(f"\n訊號類型分布:")
                    for signal_type, count in signal_types.items():
                        print(f"  {signal_type}: {count}")

            # 模擬結果評價
            self.print_section("策略評價")
            self._print_strategy_evaluation(backtest_data)

        except Exception as e:
            logger.error(f"打印策略回測結果失敗: {e}")
            print(f"{self.colors['red']}打印策略回測結果時發生錯誤: {e}{self.colors['reset']}")

    def _print_strategy_evaluation(self, backtest_data: Dict[str, Any]):
        """打印策略評價"""
        total_return = backtest_data.get('total_return', 0)
        sharpe_ratio = backtest_data.get('sharpe_ratio', 0)
        max_drawdown = backtest_data.get('max_drawdown', 0)
        win_rate = backtest_data.get('win_rate', 0)

        # 綜合評價
        evaluation = self._evaluate_strategy_performance(total_return, sharpe_ratio, max_drawdown, win_rate)
        print(f"綜合評價: {evaluation}")

        # 具體建議
        suggestions = self._get_strategy_suggestions(total_return, sharpe_ratio, max_drawdown, win_rate)
        if suggestions:
            print(f"\n改進建議:")
            for suggestion in suggestions:
                wrapped_suggestion = textwrap.fill(suggestion, width=self.width-4)
                print(f"  • {wrapped_suggestion}")

    def print_market_report(self, market_data: Dict[str, Any]):
        """打印市場總體報告"""
        try:
            self.print_header("市場分析報告", f"分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # 市場評估
            assessment = market_data.get('市場評估', {})
            if assessment:
                self.print_section("市場評估")
                print(f"市場強度: {assessment.get('市場強度', '未知')}")
                print(f"強度評分: {assessment.get('強度評分', 0)}/10")
                print(f"漲幅評估: {assessment.get('漲幅評估', '未知')}")
                print(f"綜合評分: {assessment.get('綜合評分', 0)}/10")

            # 強勢股統計
            strong_stats = market_data.get('強勢股統計', {})
            if strong_stats:
                self.print_section("強勢股統計")
                print(f"強勢股總數: {strong_stats.get('總數', 0)}")
                print(f"平均強勢評分: {strong_stats.get('平均評分', 0):.1f}")

                trend_dist = strong_stats.get('趨勢分布', {})
                if trend_dist:
                    print(f"\n趨勢分布:")
                    for trend, count in trend_dist.items():
                        print(f"  {trend}: {count}檔")

            # 漲幅排行統計
            gainers_stats = market_data.get('漲幅排行統計', {})
            if gainers_stats:
                self.print_section("漲幅排行統計")
                print(f"上漲股票數: {gainers_stats.get('總數', 0)}")
                print(f"平均漲幅: {gainers_stats.get('平均漲幅', 0):.2f}%")
                print(f"最大漲幅: {gainers_stats.get('最大漲幅', 0):.2f}%")

            # 投資建議
            advice = market_data.get('投資建議', {})
            if advice:
                self.print_section("投資建議")
                print(f"總體建議: {advice.get('總體建議', '未知')}")
                print(f"操作策略: {advice.get('操作策略', '未知')}")
                print(f"風險提示: {advice.get('風險提示', '未知')}")

        except Exception as e:
            logger.error(f"打印市場報告失敗: {e}")
            print(f"{self.colors['red']}打印市場報告時發生錯誤: {e}{self.colors['reset']}")

    def print_error(self, message: str):
        """打印錯誤信息"""
        print(f"\n{self.colors['red']}{self.colors['bold']}錯誤: {message}{self.colors['reset']}")

    def print_warning(self, message: str):
        """打印警告信息"""
        print(f"\n{self.colors['yellow']}{self.colors['bold']}警告: {message}{self.colors['reset']}")

    def print_success(self, message: str):
        """打印成功信息"""
        print(f"\n{self.colors['green']}{self.colors['bold']}成功: {message}{self.colors['reset']}")

    def print_info(self, message: str):
        """打印信息"""
        print(f"\n{self.colors['blue']}{self.colors['bold']}信息: {message}{self.colors['reset']}")

    # 輔助方法
    def _format_price(self, price: float) -> str:
        """格式化價格顯示"""
        if price >= 1000:
            return ",.0f"
        elif price >= 100:
            return ".1f"
        else:
            return ".2f"

    def _colorize_trend(self, trend: str) -> str:
        """為趨勢著色"""
        if '強勢多頭' in trend:
            return f"{self.colors['green']}{trend}{self.colors['reset']}"
        elif '多頭' in trend:
            return f"{self.colors['green']}{trend}{self.colors['reset']}"
        elif '空頭' in trend:
            return f"{self.colors['red']}{trend}{self.colors['reset']}"
        else:
            return f"{self.colors['yellow']}{trend}{self.colors['reset']}"

    def _colorize_position(self, position: str) -> str:
        """為位階著色"""
        if position == '低檔':
            return f"{self.colors['green']}{position}{self.colors['reset']}"
        elif position == '高檔':
            return f"{self.colors['red']}{position}{self.colors['reset']}"
        else:
            return f"{self.colors['yellow']}{position}{self.colors['reset']}"

    def _colorize_risk(self, risk: str) -> str:
        """為風險著色"""
        if '高風險' in risk:
            return f"{self.colors['red']}{risk}{self.colors['reset']}"
        elif '中風險' in risk:
            return f"{self.colors['yellow']}{risk}{self.colors['reset']}"
        else:
            return f"{self.colors['green']}{risk}{self.colors['reset']}"

    def _colorize_grade(self, grade: str) -> str:
        """為等級著色"""
        if grade in ['A+', 'A']:
            return f"{self.colors['green']}{grade}{self.colors['reset']}"
        elif grade in ['B+', 'B']:
            return f"{self.colors['blue']}{grade}{self.colors['reset']}"
        elif grade in ['C+', 'C']:
            return f"{self.colors['yellow']}{grade}{self.colors['reset']}"
        else:
            return f"{self.colors['red']}{grade}{self.colors['reset']}"

    def _colorize_action(self, action: str) -> str:
        """為操作建議著色"""
        if '買入' in action:
            return f"{self.colors['green']}{action}{self.colors['reset']}"
        elif '賣出' in action:
            return f"{self.colors['red']}{action}{self.colors['reset']}"
        else:
            return f"{self.colors['yellow']}{action}{self.colors['reset']}"

    def _get_rsi_indicator(self, rsi: float) -> str:
        """獲取RSI指標"""
        if rsi > 70:
            return f"{self.colors['red']}(超買){self.colors['reset']}"
        elif rsi < 30:
            return f"{self.colors['green']}(超賣){self.colors['reset']}"
        else:
            return f"{self.colors['yellow']}(正常){self.colors['reset']}"

    def _get_strength_indicator(self, strength: int) -> str:
        """獲取強度指標"""
        if strength >= 8:
            return f"{self.colors['green']}{'●'*5}{self.colors['reset']}"
        elif strength >= 6:
            return f"{self.colors['blue']}{'●'*4}{self.colors['reset']}"
        elif strength >= 4:
            return f"{self.colors['yellow']}{'●'*3}{self.colors['reset']}"
        else:
            return f"{self.colors['red']}{'●'*2}{self.colors['reset']}"

    def _evaluate_strategy_performance(self, total_return: float, sharpe_ratio: float,
                                     max_drawdown: float, win_rate: float) -> str:
        """評估策略績效"""
        score = 0

        # 收益率評分
        if total_return >= 50:
            score += 25
        elif total_return >= 30:
            score += 20
        elif total_return >= 15:
            score += 15

        # 夏普比率評分
        if sharpe_ratio >= 2:
            score += 25
        elif sharpe_ratio >= 1.5:
            score += 20
        elif sharpe_ratio >= 1:
            score += 15

        # 回撤評分
        if max_drawdown <= 10:
            score += 25
        elif max_drawdown <= 15:
            score += 20

        # 勝率評分
        if win_rate >= 70:
            score += 25
        elif win_rate >= 60:
            score += 20

        if score >= 80:
            return f"{self.colors['green']}優秀策略{self.colors['reset']}"
        elif score >= 60:
            return f"{self.colors['blue']}良好策略{self.colors['reset']}"
        elif score >= 40:
            return f"{self.colors['yellow']}一般策略{self.colors['reset']}"
        else:
            return f"{self.colors['red']}需改進策略{self.colors['reset']}"

    def _get_strategy_suggestions(self, total_return: float, sharpe_ratio: float,
                                max_drawdown: float, win_rate: float) -> List[str]:
        """獲取策略建議"""
        suggestions = []

        if total_return < 15:
            suggestions.append("收益率偏低，考慮調整進場時機或增加持股集中度")

        if sharpe_ratio < 1:
            suggestions.append("風險調整後收益不足，注意控制回撤風險")

        if max_drawdown > 20:
            suggestions.append("最大回撤過高，建議設定更嚴格的停損機制")

        if win_rate < 50:
            suggestions.append("勝率偏低，檢視交易邏輯和進出場條件")

        if not suggestions:
            suggestions.append("策略表現良好，可考慮擴大使用規模")

        return suggestions