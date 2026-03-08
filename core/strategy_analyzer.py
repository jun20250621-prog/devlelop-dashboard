# -*- coding: utf-8 -*-
"""
策略分析模組
Strategy Analyzer Module

分析和評估交易策略的績效
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import itertools

logger = logging.getLogger(__name__)


class StrategyAnalyzer:
    """策略分析器"""

    def __init__(self):
        self.strategy_results = {}
        self.market_data = {}
        self.backtest_results = []

    def analyze_strategy_performance(self, strategy_name: str, backtest_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析策略績效"""
        try:
            # 提取關鍵指標
            total_return = backtest_data.get('總收益率', 0)
            annual_return = backtest_data.get('年化收益率', 0)
            sharpe_ratio = backtest_data.get('夏普比率', 0)
            max_drawdown = backtest_data.get('最大回撤', 0)
            win_rate = backtest_data.get('勝率', 0)
            total_trades = backtest_data.get('總交易次數', 0)

            # 計算策略評分
            strategy_score = self._calculate_strategy_score(
                total_return, sharpe_ratio, max_drawdown, win_rate
            )

            # 風險調整後收益分析
            risk_adjusted_analysis = self._analyze_risk_adjusted_returns(
                total_return, max_drawdown, sharpe_ratio
            )

            # 策略穩定性分析
            stability_analysis = self._analyze_strategy_stability(backtest_data)

            # 市場適應性分析
            market_adaptability = self._analyze_market_adaptability(backtest_data)

            analysis = {
                '策略名稱': strategy_name,
                '分析日期': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '績效指標': {
                    '總收益率': total_return,
                    '年化收益率': annual_return,
                    '夏普比率': sharpe_ratio,
                    '最大回撤': max_drawdown,
                    '勝率': win_rate,
                    '總交易次數': total_trades
                },
                '策略評分': strategy_score,
                '風險調整分析': risk_adjusted_analysis,
                '穩定性分析': stability_analysis,
                '市場適應性': market_adaptability,
                '投資建議': self._generate_strategy_recommendation(strategy_score)
            }

            return analysis

        except Exception as e:
            logger.error(f"分析策略績效失敗: {e}")
            return {'error': str(e)}

    def _calculate_strategy_score(self, total_return: float, sharpe_ratio: float,
                                max_drawdown: float, win_rate: float) -> Dict[str, Any]:
        """計算策略評分"""
        try:
            score = 0

            # 總收益率評分 (最高25分)
            if total_return >= 50:
                score += 25
            elif total_return >= 30:
                score += 20
            elif total_return >= 15:
                score += 15
            elif total_return >= 5:
                score += 10
            elif total_return >= 0:
                score += 5

            # 夏普比率評分 (最高25分)
            if sharpe_ratio >= 2:
                score += 25
            elif sharpe_ratio >= 1.5:
                score += 20
            elif sharpe_ratio >= 1:
                score += 15
            elif sharpe_ratio >= 0.5:
                score += 10
            elif sharpe_ratio >= 0:
                score += 5

            # 最大回撤評分 (最高25分)
            if max_drawdown <= 10:
                score += 25
            elif max_drawdown <= 15:
                score += 20
            elif max_drawdown <= 20:
                score += 15
            elif max_drawdown <= 30:
                score += 10
            elif max_drawdown <= 50:
                score += 5

            # 勝率評分 (最高25分)
            if win_rate >= 70:
                score += 25
            elif win_rate >= 60:
                score += 20
            elif win_rate >= 50:
                score += 15
            elif win_rate >= 40:
                score += 10
            elif win_rate >= 30:
                score += 5

            grade = self._get_strategy_grade(score)

            return {
                '總分': score,
                '等級': grade,
                '評價': self._get_strategy_description(grade),
                '評分細項': {
                    '收益率評分': self._get_component_score(total_return, [0, 5, 15, 30, 50], [0, 5, 10, 15, 20, 25]),
                    '夏普比率評分': self._get_component_score(sharpe_ratio, [0, 0.5, 1, 1.5, 2], [0, 5, 10, 15, 20, 25]),
                    '回撤評分': self._get_component_score(-max_drawdown, [-50, -30, -20, -15, -10], [0, 5, 10, 15, 20, 25]),
                    '勝率評分': self._get_component_score(win_rate, [0, 30, 40, 50, 60, 70], [0, 5, 10, 15, 20, 25])
                }
            }

        except Exception as e:
            logger.error(f"計算策略評分失敗: {e}")
            return {'總分': 0, '等級': 'F', '評價': '計算失敗'}

    def _get_component_score(self, value: float, thresholds: List[float], scores: List[int]) -> int:
        """計算單項評分"""
        for i, threshold in enumerate(thresholds):
            if value >= threshold:
                return scores[i]
        return scores[0]

    def _get_strategy_grade(self, score: int) -> str:
        """獲取策略等級"""
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

    def _get_strategy_description(self, grade: str) -> str:
        """獲取策略描述"""
        descriptions = {
            'A+': '卓越策略，高度推薦使用',
            'A': '優秀策略，值得投資',
            'B+': '良好策略，可以考慮',
            'B': '及格策略，需要觀察',
            'C+': '勉強及格，建議改進',
            'C': '表現不佳，需要優化',
            'D': '表現很差，建議放棄',
            'F': '完全失敗，不建議使用'
        }
        return descriptions.get(grade, '未知評價')

    def _analyze_risk_adjusted_returns(self, total_return: float, max_drawdown: float,
                                     sharpe_ratio: float) -> Dict[str, Any]:
        """分析風險調整後收益"""
        try:
            # 計算各項風險調整指標
            if max_drawdown > 0:
                calmar_ratio = total_return / max_drawdown
                sortino_ratio = total_return / (max_drawdown / 2)  # 簡化計算
            else:
                calmar_ratio = 0
                sortino_ratio = 0

            # 評估風險調整後表現
            risk_assessment = ""
            if sharpe_ratio >= 1.5 and calmar_ratio >= 1:
                risk_assessment = "優秀的風險調整表現"
            elif sharpe_ratio >= 1 and calmar_ratio >= 0.5:
                risk_assessment = "良好的風險調整表現"
            elif sharpe_ratio >= 0.5:
                risk_assessment = "一般的風險調整表現"
            else:
                risk_assessment = "風險調整表現不佳"

            return {
                '卡瑪比率': round(calmar_ratio, 2),
                '索廷諾比率': round(sortino_ratio, 2),
                '風險評估': risk_assessment,
                '風險等級': self._assess_risk_level(sharpe_ratio, max_drawdown)
            }

        except Exception as e:
            logger.error(f"分析風險調整收益失敗: {e}")
            return {}

    def _assess_risk_level(self, sharpe_ratio: float, max_drawdown: float) -> str:
        """評估風險等級"""
        if sharpe_ratio >= 1.5 and max_drawdown <= 15:
            return "低風險"
        elif sharpe_ratio >= 1 and max_drawdown <= 25:
            return "中低風險"
        elif sharpe_ratio >= 0.5 and max_drawdown <= 35:
            return "中風險"
        elif sharpe_ratio >= 0 and max_drawdown <= 50:
            return "中高風險"
        else:
            return "高風險"

    def _analyze_strategy_stability(self, backtest_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析策略穩定性"""
        try:
            # 從交易明細中分析月度表現
            trades = backtest_data.get('交易明細', [])

            if not trades:
                return {'穩定性評分': 0, '評價': '無交易數據'}

            # 按月份統計
            monthly_returns = defaultdict(list)
            monthly_trades = defaultdict(int)

            for trade in trades:
                date_str = trade.get('date', '')
                profit_loss = trade.get('profit_loss', 0)

                if date_str and profit_loss != 0:
                    try:
                        month = date_str[:7]  # YYYY-MM
                        monthly_returns[month].append(profit_loss)
                        monthly_trades[month] += 1
                    except:
                        continue

            if not monthly_returns:
                return {'穩定性評分': 0, '評價': '無足夠數據'}

            # 計算月度統計
            monthly_stats = []
            for month, returns in monthly_returns.items():
                monthly_stats.append({
                    '月份': month,
                    '交易次數': monthly_trades[month],
                    '總收益': sum(returns),
                    '平均收益': np.mean(returns),
                    '勝率': len([r for r in returns if r > 0]) / len(returns) * 100
                })

            # 計算穩定性指標
            monthly_total_returns = [stats['總收益'] for stats in monthly_stats]
            monthly_win_rates = [stats['勝率'] for stats in monthly_stats]

            # 變異係數 (CV) - 衡量波動性
            if len(monthly_total_returns) > 1:
                cv = np.std(monthly_total_returns) / abs(np.mean(monthly_total_returns)) if np.mean(monthly_total_returns) != 0 else 0
                win_rate_cv = np.std(monthly_win_rates) / np.mean(monthly_win_rates) if np.mean(monthly_win_rates) != 0 else 0
            else:
                cv = 0
                win_rate_cv = 0

            # 穩定性評分 (0-100)
            stability_score = 100 - min(100, (cv * 50 + win_rate_cv * 50))

            stability_description = self._get_stability_description(stability_score)

            return {
                '穩定性評分': round(stability_score, 1),
                '評價': stability_description,
                '月度統計': monthly_stats,
                '變異係數': round(cv, 3),
                '勝率變異': round(win_rate_cv, 3)
            }

        except Exception as e:
            logger.error(f"分析策略穩定性失敗: {e}")
            return {'穩定性評分': 0, '評價': '分析失敗'}

    def _get_stability_description(self, score: float) -> str:
        """獲取穩定性描述"""
        if score >= 80:
            return "高度穩定，表現一致"
        elif score >= 60:
            return "較為穩定，表現良好"
        elif score >= 40:
            return "一般穩定，有波動"
        elif score >= 20:
            return "穩定性差，波動較大"
        else:
            return "極不穩定，表現不一致"

    def _analyze_market_adaptability(self, backtest_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析市場適應性"""
        try:
            # 分析策略在不同市場條件下的表現
            trades = backtest_data.get('交易明細', [])

            if not trades:
                return {'適應性評分': 0, '評價': '無交易數據'}

            # 簡化分析：根據勝率和收益評估適應性
            win_rate = backtest_data.get('勝率', 0)
            total_return = backtest_data.get('總收益率', 0)
            max_drawdown = backtest_data.get('最大回撤', 0)

            # 適應性評分算法
            adaptability_score = 0

            # 勝率適應性 (40%)
            if win_rate >= 60:
                adaptability_score += 40
            elif win_rate >= 50:
                adaptability_score += 30
            elif win_rate >= 40:
                adaptability_score += 20
            elif win_rate >= 30:
                adaptability_score += 10

            # 收益適應性 (35%)
            if total_return >= 30:
                adaptability_score += 35
            elif total_return >= 15:
                adaptability_score += 25
            elif total_return >= 5:
                adaptability_score += 15
            elif total_return >= 0:
                adaptability_score += 5

            # 回撤控制適應性 (25%)
            if max_drawdown <= 15:
                adaptability_score += 25
            elif max_drawdown <= 25:
                adaptability_score += 20
            elif max_drawdown <= 35:
                adaptability_score += 15
            elif max_drawdown <= 50:
                adaptability_score += 10

            adaptability_description = self._get_adaptability_description(adaptability_score)

            return {
                '適應性評分': adaptability_score,
                '評價': adaptability_description,
                '市場條件分析': self._analyze_market_conditions(backtest_data)
            }

        except Exception as e:
            logger.error(f"分析市場適應性失敗: {e}")
            return {'適應性評分': 0, '評價': '分析失敗'}

    def _get_adaptability_description(self, score: int) -> str:
        """獲取適應性描述"""
        if score >= 80:
            return "高度適應各種市場條件"
        elif score >= 60:
            return "良好適應多數市場條件"
        elif score >= 40:
            return "一般適應性，特定條件表現較好"
        elif score >= 20:
            return "適應性有限，需特定市場條件"
        else:
            return "適應性很差，市場條件敏感"

    def _analyze_market_conditions(self, backtest_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析市場條件表現"""
        # 簡化分析：根據總體數據給出市場條件建議
        total_return = backtest_data.get('總收益率', 0)
        win_rate = backtest_data.get('勝率', 0)

        conditions = {
            '多頭市場': '適合' if total_return > 20 and win_rate > 55 else '一般',
            '空頭市場': '適合' if win_rate > 45 else '不適合',
            '震盪市場': '適合' if win_rate > 50 else '一般',
            '單邊市場': '適合' if total_return > 15 else '一般'
        }

        best_condition = max(conditions.items(), key=lambda x: 1 if x[1] == '適合' else 0)
        worst_condition = min(conditions.items(), key=lambda x: 1 if x[1] == '適合' else 0)

        return {
            '最佳市場條件': best_condition[0],
            '最差市場條件': worst_condition[0],
            '各條件適應性': conditions
        }

    def _generate_strategy_recommendation(self, strategy_score: Dict[str, Any]) -> Dict[str, Any]:
        """生成策略建議"""
        try:
            grade = strategy_score.get('等級', 'F')
            total_score = strategy_score.get('總分', 0)

            if grade in ['A+', 'A']:
                recommendation = "強烈推薦使用"
                position_size = "可全倉或重倉"
                usage = "核心策略，可作為主要投資工具"
            elif grade in ['B+', 'B']:
                recommendation = "建議使用"
                position_size = "可半倉操作"
                usage = "輔助策略，可與其他策略配合使用"
            elif grade == 'C+':
                recommendation = "謹慎使用"
                position_size = "輕倉操作"
                usage = "測試策略，需密切監控"
            elif grade == 'C':
                recommendation = "不建議使用"
                position_size = "避免使用"
                usage = "策略需要大幅改進"
            else:
                recommendation = "強烈不建議使用"
                position_size = "禁止使用"
                usage = "策略存在重大問題"

            return {
                '使用建議': recommendation,
                '建議倉位': position_size,
                '策略定位': usage,
                '注意事項': self._get_strategy_notes(grade)
            }

        except Exception as e:
            return {'使用建議': '無法評估', '建議倉位': '未知', '策略定位': '未知'}

    def _get_strategy_notes(self, grade: str) -> List[str]:
        """獲取策略注意事項"""
        notes = {
            'A+': ['持續監控市場變化', '定期檢視策略表現', '可考慮擴大使用規模'],
            'A': ['注意風險控制', '關注市場環境變化', '適時調整參數'],
            'B+': ['控制倉位大小', '設定止損止盈', '關注策略表現變化'],
            'B': ['小額測試使用', '密切監控績效', '準備替代策略'],
            'C+': ['極小額測試', '嚴格控制風險', '尋找改進機會'],
            'C': ['暫停使用', '分析失敗原因', '重新設計策略'],
            'D': ['立即停止使用', '檢討策略邏輯', '避免進一步損失'],
            'F': ['完全放棄該策略', '尋找新的投資方法', '重新學習投資知識']
        }
        return notes.get(grade, ['無法提供具體建議'])

    def compare_strategies(self, strategy_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """比較多個策略"""
        try:
            if not strategy_results:
                return {'error': '無策略數據'}

            # 提取關鍵指標
            comparison_data = []
            for result in strategy_results:
                perf = result.get('績效指標', {})
                score = result.get('策略評分', {})

                comparison_data.append({
                    '策略名稱': result.get('策略名稱', '未知'),
                    '總收益率': perf.get('總收益率', 0),
                    '夏普比率': perf.get('夏普比率', 0),
                    '最大回撤': perf.get('最大回撤', 0),
                    '勝率': perf.get('勝率', 0),
                    '策略評分': score.get('總分', 0),
                    '等級': score.get('等級', 'F')
                })

            # 排序比較
            sorted_by_return = sorted(comparison_data, key=lambda x: x['總收益率'], reverse=True)
            sorted_by_sharpe = sorted(comparison_data, key=lambda x: x['夏普比率'], reverse=True)
            sorted_by_score = sorted(comparison_data, key=lambda x: x['策略評分'], reverse=True)

            # 統計分析
            avg_return = np.mean([s['總收益率'] for s in comparison_data])
            avg_sharpe = np.mean([s['夏普比率'] for s in comparison_data])
            avg_score = np.mean([s['策略評分'] for s in comparison_data])

            return {
                '策略數量': len(strategy_results),
                '比較數據': comparison_data,
                '收益率排名': [s['策略名稱'] for s in sorted_by_return],
                '夏普比率排名': [s['策略名稱'] for s in sorted_by_sharpe],
                '綜合評分排名': [s['策略名稱'] for s in sorted_by_score],
                '統計摘要': {
                    '平均收益率': round(avg_return, 2),
                    '平均夏普比率': round(avg_sharpe, 2),
                    '平均評分': round(avg_score, 1)
                },
                '最佳策略': sorted_by_score[0]['策略名稱'] if sorted_by_score else '無',
                '建議': self._generate_comparison_recommendation(comparison_data)
            }

        except Exception as e:
            logger.error(f"比較策略失敗: {e}")
            return {'error': str(e)}

    def _generate_comparison_recommendation(self, comparison_data: List[Dict[str, Any]]) -> str:
        """生成比較建議"""
        try:
            if not comparison_data:
                return "無比較數據"

            # 找出最佳策略
            best_strategy = max(comparison_data, key=lambda x: x['策略評分'])

            if best_strategy['策略評分'] >= 80:
                return f"推薦使用 '{best_strategy['策略名稱']}' 作為主要策略，其他策略作為輔助"
            elif best_strategy['策略評分'] >= 60:
                return f"建議優先使用 '{best_strategy['策略名稱']}'，並測試其他策略的改進版本"
            else:
                return "所有策略表現一般，建議重新設計或尋找更好的策略"

        except Exception as e:
            return "無法生成比較建議"

    def optimize_strategy_parameters(self, base_strategy: Dict[str, Any],
                                   param_ranges: Dict[str, List[Any]],
                                   optimization_metric: str = 'sharpe_ratio') -> Dict[str, Any]:
        """優化策略參數"""
        try:
            # 生成參數組合
            param_combinations = self._generate_parameter_combinations(param_ranges)

            best_result = None
            best_score = -float('inf')

            # 測試每個參數組合
            for params in param_combinations:
                # 這裡應該實際運行回測，但為了簡化，我們模擬結果
                test_result = self._simulate_strategy_with_params(base_strategy, params)

                # 評估結果
                score = self._evaluate_optimization_result(test_result, optimization_metric)

                if score > best_score:
                    best_score = score
                    best_result = {
                        'parameters': params,
                        'performance': test_result,
                        'optimization_score': score
                    }

            return best_result if best_result else {'error': '優化失敗'}

        except Exception as e:
            logger.error(f"優化策略參數失敗: {e}")
            return {'error': str(e)}

    def _generate_parameter_combinations(self, param_ranges: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """生成參數組合"""
        keys = list(param_ranges.keys())
        values = list(param_ranges.values())

        combinations = []
        for combination in itertools.product(*values):
            param_dict = dict(zip(keys, combination))
            combinations.append(param_dict)

        return combinations

    def _simulate_strategy_with_params(self, base_strategy: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """使用指定參數模擬策略"""
        # 簡化模擬：根據參數調整基礎結果
        base_return = base_strategy.get('總收益率', 10)
        base_sharpe = base_strategy.get('夏普比率', 1)
        base_drawdown = base_strategy.get('最大回撤', 20)

        # 參數調整因子（簡化邏輯）
        adjustment_factor = 1.0

        # 根據參數調整表現
        if 'fast_ma' in params and 'slow_ma' in params:
            if params['fast_ma'] < params['slow_ma']:
                adjustment_factor *= 1.1  # 合理的均線組合
            else:
                adjustment_factor *= 0.9  # 不合理的均線組合

        return {
            '總收益率': base_return * adjustment_factor,
            '夏普比率': base_sharpe * adjustment_factor,
            '最大回撤': base_drawdown / adjustment_factor,
            '勝率': 55 * adjustment_factor  # 假設基礎勝率55%
        }

    def _evaluate_optimization_result(self, result: Dict[str, Any], metric: str) -> float:
        """評估優化結果"""
        if metric == 'sharpe_ratio':
            return result.get('夏普比率', 0)
        elif metric == 'total_return':
            return result.get('總收益率', 0)
        elif metric == 'win_rate':
            return result.get('勝率', 0)
        else:
            # 綜合評分
            return (result.get('夏普比率', 0) * 0.4 +
                   result.get('總收益率', 0) * 0.3 +
                   result.get('勝率', 0) * 0.3)