# -*- coding: utf-8 -*-
"""
專業報告生成模組
Professional Report Generator Module

生成詳細的股票分析報告
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ProfessionalReportGenerator:
    """專業報告生成器"""

    def __init__(self):
        self.report_data = {}
        self.analysis_results = {}

    def generate_comprehensive_report(self, stock_code: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成綜合分析報告"""
        try:
            self.report_data = {
                'stock_code': stock_code,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'technical_data': analysis_data.get('technical_data', {}),
                'strategy': analysis_data.get('strategy', {}),
                'levels': analysis_data.get('levels', {}),
                'trend': analysis_data.get('trend', {}),
                'position': analysis_data.get('position', {})
            }

            # 生成各項分析
            technical_analysis = self._generate_technical_analysis()
            trend_analysis = self._generate_trend_analysis()
            position_analysis = self._generate_position_analysis()
            strategy_recommendation = self._generate_strategy_recommendation()
            risk_assessment = self._generate_risk_assessment()

            # 綜合評分
            overall_score = self._calculate_overall_score()

            report = {
                '股票代碼': stock_code,
                '分析日期': self.report_data['analysis_date'],
                '技術分析': technical_analysis,
                '趨勢分析': trend_analysis,
                '位階分析': position_analysis,
                '策略建議': strategy_recommendation,
                '風險評估': risk_assessment,
                '綜合評分': overall_score,
                '投資建議': self._get_investment_recommendation(overall_score)
            }

            return report

        except Exception as e:
            logger.error(f"生成綜合報告失敗: {e}")
            return {}

    def _generate_technical_analysis(self) -> Dict[str, Any]:
        """生成技術分析報告"""
        tech_data = self.report_data.get('technical_data', {})

        analysis = {
            '當前價格': tech_data.get('current_price', 0),
            '均線系統': {
                '5日均線': tech_data.get('sma_5', 0),
                '20日均線': tech_data.get('sma_20', 0),
                '60日均線': tech_data.get('sma_60', 0)
            },
            '動能指標': {
                'MACD': tech_data.get('macd', 0),
                'MACD柱狀圖': tech_data.get('macd_hist', 0),
                'RSI': tech_data.get('rsi', 0)
            },
            '波動指標': {
                'ATR': tech_data.get('atr', 0)
            },
            '關鍵價位': {
                '支撐位': self.report_data.get('levels', {}).get('support', 0),
                '壓力位': self.report_data.get('levels', {}).get('resistance', 0),
                '買入區': self.report_data.get('levels', {}).get('buy_zone', 0),
                '賣出區': self.report_data.get('levels', {}).get('sell_zone', 0)
            }
        }

        return analysis

    def _generate_trend_analysis(self) -> Dict[str, Any]:
        """生成趨勢分析報告"""
        trend_data = self.report_data.get('trend', {})

        analysis = {
            '主要趨勢': trend_data.get('trend', '未知'),
            '趨勢強度': trend_data.get('strength', 0),
            'RSI狀態': trend_data.get('rsi_status', '未知'),
            'RSI數值': trend_data.get('rsi_value', 0),
            'MACD狀態': trend_data.get('macd_status', '未知'),
            '布林通道': trend_data.get('bollinger_status', '未知'),
            'KD指標': {
                '狀態': trend_data.get('kd_status', '未知'),
                'K值': trend_data.get('k_value', 0),
                'D值': trend_data.get('d_value', 0)
            }
        }

        return analysis

    def _generate_position_analysis(self) -> Dict[str, Any]:
        """生成位階分析報告"""
        position_data = self.report_data.get('position', {})

        analysis = {
            '位階': position_data.get('stage', '未知'),
            '位階描述': position_data.get('stage_desc', ''),
            '年度最低價': position_data.get('yearly_low', 0),
            '年度最高價': position_data.get('yearly_high', 0),
            '當前位置百分比': position_data.get('current_pct', 0)
        }

        return analysis

    def _generate_strategy_recommendation(self) -> Dict[str, Any]:
        """生成策略建議"""
        strategy_data = self.report_data.get('strategy', {})

        recommendation = {
            '短期策略': strategy_data.get('short_term', ''),
            '中期策略': strategy_data.get('medium_term', ''),
            '長期策略': strategy_data.get('long_term', ''),
            '目標價位': self.report_data.get('levels', {}).get('target_price', 0),
            '停損價位': self.report_data.get('levels', {}).get('stop_loss_buy', 0)
        }

        return recommendation

    def _generate_risk_assessment(self) -> Dict[str, Any]:
        """生成風險評估"""
        tech_data = self.report_data.get('technical_data', {})
        trend_data = self.report_data.get('trend', {})
        position_data = self.report_data.get('position', {})

        # 風險評估邏輯
        risk_factors = []

        # RSI風險
        rsi = trend_data.get('rsi_value', 50)
        if rsi > 80:
            risk_factors.append("RSI超買，存在回調風險")
        elif rsi < 20:
            risk_factors.append("RSI超賣，可能存在反彈機會")

        # 位階風險
        position_pct = position_data.get('current_pct', 50)
        if position_pct > 80:
            risk_factors.append("高檔區，獲利回吐風險較高")
        elif position_pct < 20:
            risk_factors.append("低檔區，投資價值較高但波動較大")

        # 趨勢風險
        trend = trend_data.get('trend', '')
        if '空頭' in trend:
            risk_factors.append("趨勢偏空，操作需謹慎")

        # ATR風險
        atr = tech_data.get('atr', 0)
        current_price = tech_data.get('current_price', 0)
        if current_price > 0:
            volatility_ratio = (atr / current_price) * 100
            if volatility_ratio > 5:
                risk_factors.append(f"波動率較高 ({volatility_ratio:.1f}%)")
            elif volatility_ratio < 1:
                risk_factors.append(f"波動率較低 ({volatility_ratio:.1f}%)")

        assessment = {
            '風險等級': self._calculate_risk_level(risk_factors),
            '風險因子': risk_factors,
            '風險描述': self._get_risk_description(risk_factors)
        }

        return assessment

    def _calculate_risk_level(self, risk_factors: List[str]) -> str:
        """計算風險等級"""
        risk_count = len(risk_factors)

        if risk_count >= 3:
            return "高風險"
        elif risk_count >= 2:
            return "中高風險"
        elif risk_count >= 1:
            return "中風險"
        else:
            return "低風險"

    def _get_risk_description(self, risk_factors: List[str]) -> str:
        """獲取風險描述"""
        if not risk_factors:
            return "整體風險較低，適合積極操作"

        descriptions = {
            "RSI超買": "技術指標顯示超買現象，短期內可能出現回調",
            "RSI超賣": "技術指標顯示超賣現象，可能存在反彈機會",
            "高檔區": "價格位於年度高檔區，獲利回吐風險較高",
            "低檔區": "價格位於年度低檔區，投資價值較高但波動較大",
            "趨勢偏空": "整體趨勢偏向空頭，操作需謹慎",
            "波動率較高": "價格波動幅度較大，適合有經驗的投資者",
            "波動率較低": "價格波動幅度較小，適合保守型投資者"
        }

        descriptions_list = []
        for factor in risk_factors:
            for key, desc in descriptions.items():
                if key in factor:
                    descriptions_list.append(desc)
                    break

        return "；".join(descriptions_list) if descriptions_list else "風險因素不明顯"

    def _calculate_overall_score(self) -> Dict[str, Any]:
        """計算綜合評分"""
        tech_data = self.report_data.get('technical_data', {})
        trend_data = self.report_data.get('trend', {})
        position_data = self.report_data.get('position', {})

        score = 5  # 基礎分數

        # 趨勢評分 (最高3分)
        trend = trend_data.get('trend', '')
        if '強勢多頭' in trend:
            score += 3
        elif '多頭' in trend:
            score += 2
        elif '盤整' in trend:
            score += 1
        elif '空頭' in trend:
            score -= 1
        elif '強勢空頭' in trend:
            score -= 2

        # 技術指標評分 (最高2分)
        rsi = trend_data.get('rsi_value', 50)
        if 30 <= rsi <= 70:
            score += 1
        elif rsi > 80 or rsi < 20:
            score -= 1

        kd_status = trend_data.get('kd_status', '')
        if '黃金交叉' in kd_status:
            score += 1
        elif '死亡交叉' in kd_status:
            score -= 1

        # 位階評分 (最高2分)
        position_pct = position_data.get('current_pct', 50)
        if position_pct < 30:
            score += 2  # 低檔價值高
        elif position_pct > 70:
            score -= 1  # 高檔風險高

        # 確保分數在合理範圍
        final_score = max(1, min(10, score))

        score_description = self._get_score_description(final_score)

        return {
            '總分': final_score,
            '評分描述': score_description,
            '評分標準': '1-10分，10分為最佳'
        }

    def _get_score_description(self, score: int) -> str:
        """獲取評分描述"""
        if score >= 9:
            return "極度看好，強烈建議買入"
        elif score >= 7:
            return "看好，建議買入"
        elif score >= 5:
            return "中性，可適度關注"
        elif score >= 3:
            return "謹慎觀望，建議減倉"
        else:
            return "極度悲觀，建議賣出"

    def _get_investment_recommendation(self, score_data: Dict[str, Any]) -> Dict[str, Any]:
        """獲取投資建議"""
        score = score_data.get('總分', 5)

        if score >= 8:
            action = "積極買入"
            position_size = "可全倉或重倉"
            holding_period = "中長期持有"
        elif score >= 6:
            action = "適度買入"
            position_size = "可半倉或適度倉位"
            holding_period = "中期持有"
        elif score >= 4:
            action = "觀望"
            position_size = "輕倉或不操作"
            holding_period = "短期觀察"
        else:
            action = "減倉或賣出"
            position_size = "減倉或空倉"
            holding_period = "盡快了結"

        return {
            '操作建議': action,
            '倉位建議': position_size,
            '持有期間': holding_period,
            '注意事項': self._get_investment_notes(score)
        }

    def _get_investment_notes(self, score: int) -> str:
        """獲取投資注意事項"""
        if score >= 8:
            return "強勢股，適合積極投資者；注意風險控制，設定適當停損"
        elif score >= 6:
            return "有投資價值，但需關注市場整體趨勢；建議分批建倉"
        elif score >= 4:
            return "處於觀望階段，等待更好時機；可小額試探性操作"
        else:
            return "風險較高，建議減倉或離場；等待更明確的轉折訊號"

    def generate_market_report(self, strong_stocks: List[Dict[str, Any]], top_gainers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成市場總體報告"""
        try:
            # 強勢股統計
            strong_stats = self._analyze_strong_stocks(strong_stocks)

            # 漲幅排行統計
            gainers_stats = self._analyze_top_gainers(top_gainers)

            # 市場總體評估
            market_assessment = self._assess_market_condition(strong_stocks, top_gainers)

            report = {
                '分析日期': datetime.now().strftime('%Y-%m-%d'),
                '強勢股統計': strong_stats,
                '漲幅排行統計': gainers_stats,
                '市場評估': market_assessment,
                '投資建議': self._generate_market_investment_advice(market_assessment)
            }

            return report

        except Exception as e:
            logger.error(f"生成市場報告失敗: {e}")
            return {}

    def _analyze_strong_stocks(self, strong_stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析強勢股統計"""
        if not strong_stocks:
            return {'總數': 0, '平均評分': 0, '行業分布': {}, '趨勢分布': {}}

        total_count = len(strong_stocks)
        avg_score = sum(stock.get('強勢評分', 0) for stock in strong_stocks) / total_count

        # 趨勢分布
        trend_distribution = {}
        for stock in strong_stocks:
            trend = stock.get('趨勢', '未知')
            trend_distribution[trend] = trend_distribution.get(trend, 0) + 1

        return {
            '總數': total_count,
            '平均評分': round(avg_score, 1),
            '趨勢分布': trend_distribution
        }

    def _analyze_top_gainers(self, top_gainers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析漲幅排行統計"""
        if not top_gainers:
            return {'總數': 0, '平均漲幅': 0, '最大漲幅': 0, '成交量統計': {}}

        total_count = len(top_gainers)
        gains = [stock.get('漲幅%', 0) for stock in top_gainers]
        avg_gain = sum(gains) / total_count
        max_gain = max(gains)

        # 成交量統計
        volumes = [stock.get('成交量(張)', 0) for stock in top_gainers]
        avg_volume = sum(volumes) / total_count

        return {
            '總數': total_count,
            '平均漲幅': round(avg_gain, 2),
            '最大漲幅': round(max_gain, 2),
            '平均成交量': round(avg_volume, 0)
        }

    def _assess_market_condition(self, strong_stocks: List[Dict[str, Any]], top_gainers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """評估市場狀況"""
        # 強勢股數量評估
        strong_count = len(strong_stocks)
        if strong_count >= 30:
            market_strength = "極度強勢"
            strength_score = 9
        elif strong_count >= 20:
            market_strength = "強勢"
            strength_score = 7
        elif strong_count >= 10:
            market_strength = "中等強勢"
            strength_score = 5
        elif strong_count >= 5:
            market_strength = "弱勢"
            strength_score = 3
        else:
            market_strength = "極度弱勢"
            strength_score = 1

        # 漲幅評估
        if top_gainers:
            avg_gain = sum(stock.get('漲幅%', 0) for stock in top_gainers) / len(top_gainers)
            if avg_gain >= 5:
                gain_assessment = "大幅上漲"
                gain_score = 8
            elif avg_gain >= 2:
                gain_assessment = "溫和上漲"
                gain_score = 6
            elif avg_gain >= -1:
                gain_assessment = "小幅波動"
                gain_score = 4
            else:
                gain_assessment = "下跌"
                gain_score = 2
        else:
            gain_assessment = "數據不足"
            gain_score = 4

        overall_score = (strength_score + gain_score) / 2

        return {
            '市場強度': market_strength,
            '強度評分': strength_score,
            '漲幅評估': gain_assessment,
            '漲幅評分': gain_score,
            '綜合評分': round(overall_score, 1)
        }

    def _generate_market_investment_advice(self, market_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """生成市場投資建議"""
        score = market_assessment.get('綜合評分', 5)

        if score >= 7:
            advice = "市場處於強勢，多頭行情明顯，適合積極進場"
            strategy = "可加大倉位，重點關注強勢股"
        elif score >= 5:
            advice = "市場表現中等，可適度參與"
            strategy = "均衡配置，關注有業績支撐的個股"
        elif score >= 3:
            advice = "市場偏弱，建議謹慎操作"
            strategy = "輕倉操作，重點關注防禦性個股"
        else:
            advice = "市場極度弱勢，建議減倉觀望"
            strategy = "降低倉位，等待轉折訊號"

        return {
            '總體建議': advice,
            '操作策略': strategy,
            '風險提示': "市場狀況瞬息萬變，請根據個人風險承受能力操作"
        }