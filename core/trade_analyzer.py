# -*- coding: utf-8 -*-
"""
交易分析模組
Trade Analyzer Module

分析交易記錄和投資組合績效
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class TradeAnalyzer:
    """交易分析器"""

    def __init__(self):
        self.trade_records = []
        self.portfolio_history = []
        self.performance_stats = {}

    def load_trade_records(self, trade_data: List[Dict[str, Any]]) -> bool:
        """載入交易記錄"""
        try:
            self.trade_records = trade_data.copy()
            logger.info(f"成功載入 {len(trade_data)} 筆交易記錄")
            return True
        except Exception as e:
            logger.error(f"載入交易記錄失敗: {e}")
            return False

    def analyze_portfolio_performance(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析投資組合績效"""
        try:
            if not self.trade_records:
                return {'error': '無交易記錄'}

            # 計算基本統計
            total_trades = len(self.trade_records)
            winning_trades = [t for t in self.trade_records if t.get('profit_loss', 0) > 0]
            losing_trades = [t for t in self.trade_records if t.get('profit_loss', 0) < 0]

            win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0

            # 計算盈虧統計
            profits = [t.get('profit_loss', 0) for t in winning_trades]
            losses = [abs(t.get('profit_loss', 0)) for t in losing_trades]

            avg_win = sum(profits) / len(profits) if profits else 0
            avg_loss = sum(losses) / len(losses) if losses else 0

            # 計算凱利公式建議倉位
            kelly_percentage = self._calculate_kelly_percentage(win_rate, avg_win, avg_loss)

            # 計算最大連續虧損
            max_consecutive_losses = self._calculate_max_consecutive_losses()

            # 計算月度績效
            monthly_performance = self._calculate_monthly_performance()

            analysis = {
                '總交易次數': total_trades,
                '勝率': round(win_rate, 2),
                '平均獲利': round(avg_win, 2),
                '平均虧損': round(avg_loss, 2),
                '盈虧比': round(avg_win / avg_loss, 2) if avg_loss > 0 else 0,
                '凱利建議倉位': round(kelly_percentage * 100, 2),
                '最大連續虧損': max_consecutive_losses,
                '月度績效': monthly_performance,
                '績效評分': self._calculate_performance_score(win_rate, avg_win, avg_loss)
            }

            return analysis

        except Exception as e:
            logger.error(f"分析投資組合績效失敗: {e}")
            return {'error': str(e)}

    def _calculate_kelly_percentage(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """計算凱利公式建議倉位"""
        try:
            if avg_loss == 0:
                return 0

            # 凱利公式: K = (W * R - L) / R
            # 其中 W = 勝率, L = 敗率, R = 平均獲利/平均虧損
            w = win_rate / 100  # 勝率轉換為小數
            r = avg_win / avg_loss  # 盈虧比
            l = 1 - w  # 敗率

            if r > 0:
                kelly = (w * r - l) / r
                # 保守起見，取一半凱利值
                return max(0, min(kelly * 0.5, 0.25))  # 最大不超過25%
            else:
                return 0

        except Exception as e:
            logger.error(f"計算凱利倉位失敗: {e}")
            return 0

    def _calculate_max_consecutive_losses(self) -> int:
        """計算最大連續虧損次數"""
        try:
            if not self.trade_records:
                return 0

            max_losses = 0
            current_losses = 0

            for trade in self.trade_records:
                profit_loss = trade.get('profit_loss', 0)
                if profit_loss < 0:
                    current_losses += 1
                    max_losses = max(max_losses, current_losses)
                else:
                    current_losses = 0

            return max_losses

        except Exception as e:
            logger.error(f"計算連續虧損失敗: {e}")
            return 0

    def _calculate_monthly_performance(self) -> Dict[str, Any]:
        """計算月度績效"""
        try:
            if not self.trade_records:
                return {}

            # 按月份分組
            monthly_stats = defaultdict(lambda: {'trades': 0, 'profit': 0, 'wins': 0})

            for trade in self.trade_records:
                date_str = trade.get('date', '')
                if not date_str:
                    continue

                try:
                    # 解析日期
                    if isinstance(date_str, str):
                        if len(date_str) >= 7:
                            month_key = date_str[:7]  # YYYY-MM
                        else:
                            continue
                    else:
                        month_key = date_str.strftime('%Y-%m')

                    profit_loss = trade.get('profit_loss', 0)

                    monthly_stats[month_key]['trades'] += 1
                    monthly_stats[month_key]['profit'] += profit_loss
                    if profit_loss > 0:
                        monthly_stats[month_key]['wins'] += 1

                except Exception as e:
                    continue

            # 轉換為列表格式
            monthly_list = []
            for month, stats in sorted(monthly_stats.items()):
                win_rate = stats['wins'] / stats['trades'] * 100 if stats['trades'] > 0 else 0
                monthly_list.append({
                    '月份': month,
                    '交易次數': stats['trades'],
                    '總盈虧': round(stats['profit'], 2),
                    '勝率': round(win_rate, 2)
                })

            return monthly_list

        except Exception as e:
            logger.error(f"計算月度績效失敗: {e}")
            return {}

    def _calculate_performance_score(self, win_rate: float, avg_win: float, avg_loss: float) -> Dict[str, Any]:
        """計算績效評分"""
        try:
            score = 0

            # 勝率評分 (最高30分)
            if win_rate >= 70:
                score += 30
            elif win_rate >= 60:
                score += 25
            elif win_rate >= 50:
                score += 20
            elif win_rate >= 40:
                score += 15
            else:
                score += 10

            # 盈虧比評分 (最高40分)
            profit_ratio = avg_win / avg_loss if avg_loss > 0 else 0
            if profit_ratio >= 2:
                score += 40
            elif profit_ratio >= 1.5:
                score += 30
            elif profit_ratio >= 1:
                score += 20
            elif profit_ratio >= 0.8:
                score += 10

            # 平均獲利評分 (最高30分)
            if avg_win >= 10000:  # 假設單位為元
                score += 30
            elif avg_win >= 5000:
                score += 20
            elif avg_win >= 2000:
                score += 10

            grade = self._get_performance_grade(score)

            return {
                '總分': score,
                '等級': grade,
                '評價': self._get_performance_description(grade)
            }

        except Exception as e:
            logger.error(f"計算績效評分失敗: {e}")
            return {'總分': 0, '等級': 'F', '評價': '計算失敗'}

    def _get_performance_grade(self, score: int) -> str:
        """獲取績效等級"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C+'
        elif score >= 40:
            return 'C'
        elif score >= 30:
            return 'D'
        else:
            return 'F'

    def _get_performance_description(self, grade: str) -> str:
        """獲取績效描述"""
        descriptions = {
            'A+': '卓越表現，策略非常優秀',
            'A': '優秀表現，策略值得繼續',
            'B+': '良好表現，策略有改進空間',
            'B': '及格表現，策略需要優化',
            'C+': '勉強及格，需要大幅改進',
            'C': '表現不佳，建議重新評估策略',
            'D': '表現很差，需要徹底檢討',
            'F': '完全失敗，建議停止使用'
        }
        return descriptions.get(grade, '未知評價')

    def analyze_trading_patterns(self) -> Dict[str, Any]:
        """分析交易模式"""
        try:
            if not self.trade_records:
                return {'error': '無交易記錄'}

            # 分析交易時間分布
            time_distribution = self._analyze_trading_time()

            # 分析交易金額分布
            amount_distribution = self._analyze_trade_amounts()

            # 分析持倉時間
            holding_time_analysis = self._analyze_holding_time()

            # 分析進出場時機
            timing_analysis = self._analyze_entry_exit_timing()

            analysis = {
                '交易時間分布': time_distribution,
                '交易金額分布': amount_distribution,
                '持倉時間分析': holding_time_analysis,
                '進出場時機分析': timing_analysis
            }

            return analysis

        except Exception as e:
            logger.error(f"分析交易模式失敗: {e}")
            return {'error': str(e)}

    def _analyze_trading_time(self) -> Dict[str, Any]:
        """分析交易時間分布"""
        try:
            if not self.trade_records:
                return {}

            # 按小時統計
            hourly_stats = defaultdict(int)
            weekday_stats = defaultdict(int)

            for trade in self.trade_records:
                date_str = trade.get('date', '')
                if not date_str:
                    continue

                try:
                    if isinstance(date_str, str):
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        date_obj = date_str

                    # 星期統計
                    weekday = date_obj.strftime('%A')
                    weekday_stats[weekday] += 1

                except Exception as e:
                    continue

            # 轉換為中文星期名稱
            weekday_mapping = {
                'Monday': '星期一',
                'Tuesday': '星期二',
                'Wednesday': '星期三',
                'Thursday': '星期四',
                'Friday': '星期五',
                'Saturday': '星期六',
                'Sunday': '星期日'
            }

            weekday_chinese = {weekday_mapping.get(k, k): v for k, v in weekday_stats.items()}

            return {
                '星期分布': dict(sorted(weekday_chinese.items())),
                '最活躍星期': max(weekday_chinese.items(), key=lambda x: x[1])[0] if weekday_chinese else '無數據'
            }

        except Exception as e:
            logger.error(f"分析交易時間失敗: {e}")
            return {}

    def _analyze_trade_amounts(self) -> Dict[str, Any]:
        """分析交易金額分布"""
        try:
            if not self.trade_records:
                return {}

            amounts = []
            for trade in self.trade_records:
                amount = trade.get('value', 0)
                if amount > 0:
                    amounts.append(amount)

            if not amounts:
                return {}

            amounts = np.array(amounts)

            return {
                '平均交易金額': round(np.mean(amounts), 2),
                '最大交易金額': round(np.max(amounts), 2),
                '最小交易金額': round(np.min(amounts), 2),
                '交易金額中位數': round(np.median(amounts), 2),
                '金額分布': self._categorize_amounts(amounts)
            }

        except Exception as e:
            logger.error(f"分析交易金額失敗: {e}")
            return {}

    def _categorize_amounts(self, amounts: np.ndarray) -> Dict[str, int]:
        """分類交易金額"""
        categories = {
            '小額(<1萬)': 0,
            '中額(1-5萬)': 0,
            '大額(5-10萬)': 0,
            '超大額(>10萬)': 0
        }

        for amount in amounts:
            if amount < 10000:
                categories['小額(<1萬)'] += 1
            elif amount < 50000:
                categories['中額(1-5萬)'] += 1
            elif amount < 100000:
                categories['大額(5-10萬)'] += 1
            else:
                categories['超大額(>10萬)'] += 1

        return categories

    def _analyze_holding_time(self) -> Dict[str, Any]:
        """分析持倉時間"""
        try:
            # 簡化版本：假設交易記錄中有買賣配對
            # 實際應用中需要更複雜的配對邏輯

            if len(self.trade_records) < 2:
                return {'平均持倉時間': 0, '最長持倉時間': 0, '最短持倉時間': 0}

            # 假設每兩筆交易為一個完整的買賣循環
            holding_times = []
            for i in range(0, len(self.trade_records) - 1, 2):
                try:
                    buy_trade = self.trade_records[i]
                    sell_trade = self.trade_records[i + 1]

                    if buy_trade.get('action') == '買入' and sell_trade.get('action') == '賣出':
                        buy_date = datetime.strptime(buy_trade['date'], '%Y-%m-%d')
                        sell_date = datetime.strptime(sell_trade['date'], '%Y-%m-%d')
                        holding_days = (sell_date - buy_date).days
                        holding_times.append(holding_days)
                except Exception as e:
                    continue

            if not holding_times:
                return {'平均持倉時間': 0, '最長持倉時間': 0, '最短持倉時間': 0}

            return {
                '平均持倉時間': round(np.mean(holding_times), 1),
                '最長持倉時間': max(holding_times),
                '最短持倉時間': min(holding_times),
                '持倉時間分布': self._categorize_holding_times(holding_times)
            }

        except Exception as e:
            logger.error(f"分析持倉時間失敗: {e}")
            return {'平均持倉時間': 0, '最長持倉時間': 0, '最短持倉時間': 0}

    def _categorize_holding_times(self, holding_times: List[int]) -> Dict[str, int]:
        """分類持倉時間"""
        categories = {
            '當日沖銷(<1天)': 0,
            '短期(1-7天)': 0,
            '中期(1-4週)': 0,
            '長期(>1個月)': 0
        }

        for days in holding_times:
            if days < 1:
                categories['當日沖銷(<1天)'] += 1
            elif days <= 7:
                categories['短期(1-7天)'] += 1
            elif days <= 30:
                categories['中期(1-4週)'] += 1
            else:
                categories['長期(>1個月)'] += 1

        return categories

    def _analyze_entry_exit_timing(self) -> Dict[str, Any]:
        """分析進出場時機"""
        try:
            # 簡化分析：統計買入和賣出的時機
            buy_timings = []
            sell_timings = []

            for trade in self.trade_records:
                action = trade.get('action', '')
                date_str = trade.get('date', '')

                if action == '買入':
                    buy_timings.append(date_str)
                elif action == '賣出':
                    sell_timings.append(date_str)

            return {
                '買入次數': len(buy_timings),
                '賣出次數': len(sell_timings),
                '買賣配對': min(len(buy_timings), len(sell_timings)),
                '未平倉部位': abs(len(buy_timings) - len(sell_timings))
            }

        except Exception as e:
            logger.error(f"分析進出場時機失敗: {e}")
            return {}

    def generate_trading_report(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成交易報告"""
        try:
            # 基本績效分析
            performance_analysis = self.analyze_portfolio_performance(portfolio_data)

            # 交易模式分析
            pattern_analysis = self.analyze_trading_patterns()

            # 風險分析
            risk_analysis = self._analyze_trading_risks()

            # 改進建議
            improvement_suggestions = self._generate_improvement_suggestions(performance_analysis)

            report = {
                '報告生成時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '績效分析': performance_analysis,
                '交易模式分析': pattern_analysis,
                '風險分析': risk_analysis,
                '改進建議': improvement_suggestions,
                '總結評價': self._generate_overall_assessment(performance_analysis)
            }

            return report

        except Exception as e:
            logger.error(f"生成交易報告失敗: {e}")
            return {'error': str(e)}

    def _analyze_trading_risks(self) -> Dict[str, Any]:
        """分析交易風險"""
        try:
            if not self.trade_records:
                return {'風險等級': '未知', '風險因子': []}

            # 計算各種風險指標
            risk_factors = []

            # 勝率風險
            win_rate = len([t for t in self.trade_records if t.get('profit_loss', 0) > 0]) / len(self.trade_records)
            if win_rate < 0.4:
                risk_factors.append("勝率過低")

            # 連續虧損風險
            max_consecutive_losses = self._calculate_max_consecutive_losses()
            if max_consecutive_losses >= 5:
                risk_factors.append(f"最大連續虧損次數過高({max_consecutive_losses}次)")

            # 單筆損失風險
            max_loss = max([abs(t.get('profit_loss', 0)) for t in self.trade_records if t.get('profit_loss', 0) < 0] or [0])
            total_capital = 1000000  # 假設總資金
            if max_loss > total_capital * 0.1:
                risk_factors.append(f"單筆最大損失過高({max_loss:,.0f}元)")

            # 風險等級評估
            risk_level = self._assess_risk_level(risk_factors)

            return {
                '風險等級': risk_level,
                '風險因子': risk_factors,
                '風險評估': self._get_risk_assessment_description(risk_level)
            }

        except Exception as e:
            logger.error(f"分析交易風險失敗: {e}")
            return {'風險等級': '未知', '風險因子': []}

    def _assess_risk_level(self, risk_factors: List[str]) -> str:
        """評估風險等級"""
        risk_count = len(risk_factors)

        if risk_count >= 3:
            return "高風險"
        elif risk_count >= 2:
            return "中高風險"
        elif risk_count >= 1:
            return "中風險"
        else:
            return "低風險"

    def _get_risk_assessment_description(self, risk_level: str) -> str:
        """獲取風險評估描述"""
        descriptions = {
            "高風險": "交易策略存在重大風險，建議立即停止或大幅調整",
            "中高風險": "交易策略存在較高風險，需要謹慎操作並設定止損",
            "中風險": "交易策略存在一定風險，建議控制倉位並關注風險控制",
            "低風險": "交易策略風險可控，可以正常操作"
        }
        return descriptions.get(risk_level, "風險評估未知")

    def _generate_improvement_suggestions(self, performance_analysis: Dict[str, Any]) -> List[str]:
        """生成改進建議"""
        suggestions = []

        try:
            win_rate = performance_analysis.get('勝率', 0)
            profit_ratio = performance_analysis.get('盈虧比', 0)
            max_consecutive_losses = performance_analysis.get('最大連續虧損', 0)

            # 勝率建議
            if win_rate < 50:
                suggestions.append("勝率過低，建議改善進場時機或調整策略")
            elif win_rate > 70:
                suggestions.append("勝率良好，可以考慮增加倉位")

            # 盈虧比建議
            if profit_ratio < 1:
                suggestions.append("盈虧比過低，建議設定更好的止盈止損點")
            elif profit_ratio > 2:
                suggestions.append("盈虧比良好，可以考慮放寬止損讓利潤充分擴張")

            # 連續虧損建議
            if max_consecutive_losses >= 3:
                suggestions.append(f"連續虧損次數較多({max_consecutive_losses}次)，建議設定最大連續虧損限制")

            # 一般建議
            suggestions.extend([
                "建議建立完整的交易計劃和風險管理制度",
                "定期檢視和調整交易策略",
                "保持良好的資金管理和心態控制"
            ])

        except Exception as e:
            logger.error(f"生成改進建議失敗: {e}")
            suggestions = ["無法生成具體建議，請檢視交易記錄"]

        return suggestions

    def _generate_overall_assessment(self, performance_analysis: Dict[str, Any]) -> str:
        """生成總結評價"""
        try:
            win_rate = performance_analysis.get('勝率', 0)
            profit_ratio = performance_analysis.get('盈虧比', 0)
            performance_score = performance_analysis.get('績效評分', {}).get('總分', 0)

            if performance_score >= 80:
                assessment = "交易表現優秀，策略有效，值得繼續使用並可考慮擴大規模。"
            elif performance_score >= 60:
                assessment = "交易表現良好，策略基本有效，但仍有改進空間。"
            elif performance_score >= 40:
                assessment = "交易表現一般，策略需要調整和優化。"
            else:
                assessment = "交易表現不佳，建議重新評估策略或暫停交易。"

            return assessment

        except Exception as e:
            return "無法生成總結評價"