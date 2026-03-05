# -*- coding: utf-8 -*-
"""
Telegram 輸出模組
Telegram Output Module

發送分析結果到 Telegram 機器人
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import json

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram 通知器"""

    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.enabled = bool(bot_token and chat_id)

        if not self.enabled:
            logger.warning("Telegram 機器人未配置，將跳過 Telegram 通知")

    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """發送訊息"""
        if not self.enabled:
            logger.debug("Telegram 未啟用，跳過發送訊息")
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                logger.info("Telegram 訊息發送成功")
                return True
            else:
                logger.error(f"Telegram 訊息發送失敗: {result.get('description', '未知錯誤')}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"發送 Telegram 訊息時發生網路錯誤: {e}")
            return False
        except Exception as e:
            logger.error(f"發送 Telegram 訊息時發生錯誤: {e}")
            return False

    def send_stock_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """發送股票分析結果"""
        try:
            stock_code = analysis_data.get('stock_code', 'UNKNOWN')
            message = self._format_stock_analysis_message(analysis_data)

            # 訊息過長時分段發送
            if len(message) > 4000:
                messages = self._split_message(message, 4000)
                success = True
                for msg in messages:
                    if not self.send_message(msg):
                        success = False
                return success
            else:
                return self.send_message(message)

        except Exception as e:
            logger.error(f"發送股票分析訊息失敗: {e}")
            return False

    def send_portfolio_report(self, portfolio_data: Dict[str, Any]) -> bool:
        """發送投資組合報告"""
        try:
            message = self._format_portfolio_message(portfolio_data)
            return self.send_message(message)
        except Exception as e:
            logger.error(f"發送投資組合報告失敗: {e}")
            return False

    def send_strategy_backtest(self, backtest_data: Dict[str, Any]) -> bool:
        """發送策略回測結果"""
        try:
            message = self._format_backtest_message(backtest_data)
            return self.send_message(message)
        except Exception as e:
            logger.error(f"發送策略回測結果失敗: {e}")
            return False

    def send_market_report(self, market_data: Dict[str, Any]) -> bool:
        """發送市場分析報告"""
        try:
            message = self._format_market_message(market_data)
            return self.send_message(message)
        except Exception as e:
            logger.error(f"發送市場報告失敗: {e}")
            return False

    def send_alert(self, alert_type: str, message: str, stock_code: str = None) -> bool:
        """發送警報訊息"""
        try:
            emoji_map = {
                'buy': '🟢',
                'sell': '🔴',
                'warning': '⚠️',
                'info': 'ℹ️',
                'success': '✅',
                'error': '❌'
            }

            emoji = emoji_map.get(alert_type.lower(), '📢')

            title = f"{emoji} 交易警報"
            if stock_code:
                title += f" - {stock_code}"

            full_message = f"<b>{title}</b>\n\n{message}"

            # 添加時間戳
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_message += f"\n\n<i>發送時間: {timestamp}</i>"

            return self.send_message(full_message)

        except Exception as e:
            logger.error(f"發送警報訊息失敗: {e}")
            return False

    def _format_stock_analysis_message(self, data: Dict[str, Any]) -> str:
        """格式化股票分析訊息"""
        stock_code = data.get('stock_code', 'UNKNOWN')
        tech_data = data.get('technical_data', {})
        trend_data = data.get('trend', {})
        position_data = data.get('position', {})
        strategy_data = data.get('strategy', {})
        score_data = data.get('overall_score', {})
        recommendation = data.get('investment_recommendation', {})

        message = f"""
<b>📊 股票分析報告 - {stock_code}</b>

<b>💰 基本信息</b>
• 當前價格: {tech_data.get('current_price', 0):.2f}
• 分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<b>📈 技術指標</b>
• RSI(14): {tech_data.get('rsi', 0):.2f}
• MACD: {tech_data.get('macd', 0):.3f}
• ATR: {tech_data.get('atr', 0):.3f}

<b>🎯 趨勢分析</b>
• 主要趨勢: {trend_data.get('trend', '未知')}
• 趨勢強度: {trend_data.get('strength', 0)}/10
• KD狀態: {trend_data.get('kd_status', '未知')}

<b>📍 位階分析</b>
• 位階: {position_data.get('stage', '未知')}
• 當前位置: {position_data.get('current_pct', 0):.1f}%

<b>💡 策略建議</b>
• 短期: {strategy_data.get('short_term', '無建議')[:100]}
• 中期: {strategy_data.get('medium_term', '無建議')[:100]}

<b>⭐ 綜合評分</b>
• 總分: {score_data.get('總分', 0)}/100
• 等級: {score_data.get('等級', 'F')}
• 評價: {score_data.get('評價', '未知')}

<b>🎯 投資建議</b>
• 操作建議: {recommendation.get('操作建議', '未知')}
• 倉位建議: {recommendation.get('倉位建議', '未知')}
• 持有期間: {recommendation.get('持有期間', '未知')}
"""

        return message.strip()

    def _format_portfolio_message(self, data: Dict[str, Any]) -> str:
        """格式化投資組合訊息"""
        performance = data.get('performance', {})
        holdings = data.get('holdings', [])[:10]  # 只顯示前10個持倉

        message = f"""
<b>📊 投資組合報告</b>

<b>💰 績效總覽</b>
• 總收益率: {performance.get('總收益率', 0):.2f}%
• 年化收益率: {performance.get('年化收益率', 0):.2f}%
• 勝率: {performance.get('勝率', 0):.2f}%
• 總交易次數: {performance.get('總交易次數', 0)}

<b>📈 持倉明細</b>
"""

        if holdings:
            for holding in holdings:
                code = holding.get('code', '')
                name = holding.get('name', '')[:10]  # 限制名稱長度
                quantity = holding.get('quantity', 0)
                profit_loss = holding.get('profit_loss', 0)

                profit_emoji = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
                message += f"• {code} {name}: {quantity:,}股 {profit_emoji}{profit_loss:,.0f}\n"
        else:
            message += "• 無持倉記錄\n"

        message += f"\n<i>報告時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"

        return message.strip()

    def _format_backtest_message(self, data: Dict[str, Any]) -> str:
        """格式化回測訊息"""
        strategy_name = data.get('strategy_name', '未知策略')

        message = f"""
<b>📊 策略回測報告 - {strategy_name}</b>

<b>💰 回測結果</b>
• 總收益率: {data.get('total_return', 0):.2f}%
• 年化收益率: {data.get('annual_return', 0):.2f}%
• 夏普比率: {data.get('sharpe_ratio', 0):.2f}
• 最大回撤: {data.get('max_drawdown', 0):.2f}%

<b>📈 交易統計</b>
• 勝率: {data.get('win_rate', 0):.2f}%
• 總交易次數: {data.get('total_trades', 0)}
• 平均獲利: {data.get('avg_profit', 0):.2f}

<b>🎯 訊號統計</b>
"""

        signals = data.get('signal_statistics', {})
        if signals:
            message += f"• 總訊號數: {signals.get('總訊號數', 0)}\n"
            message += f"• 買入訊號: {signals.get('買入訊號', 0)}\n"
            message += f"• 賣出訊號: {signals.get('賣出訊號', 0)}\n"

        message += f"\n<i>回測時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"

        return message.strip()

    def _format_market_message(self, data: Dict[str, Any]) -> str:
        """格式化市場訊息"""
        assessment = data.get('市場評估', {})
        strong_stats = data.get('強勢股統計', {})
        gainers_stats = data.get('漲幅排行統計', {})
        advice = data.get('投資建議', {})

        message = f"""
<b>🌍 市場分析報告</b>

<b>📊 市場評估</b>
• 市場強度: {assessment.get('市場強度', '未知')}
• 強度評分: {assessment.get('強度評分', 0)}/10
• 漲幅評估: {assessment.get('漲幅評估', '未知')}
• 綜合評分: {assessment.get('綜合評分', 0)}/10

<b>🚀 強勢股統計</b>
• 強勢股總數: {strong_stats.get('總數', 0)}
• 平均評分: {strong_stats.get('平均評分', 0):.1f}

<b>📈 漲幅排行</b>
• 上漲股票數: {gainers_stats.get('總數', 0)}
• 平均漲幅: {gainers_stats.get('平均漲幅', 0):.2f}%
• 最大漲幅: {gainers_stats.get('最大漲幅', 0):.2f}%

<b>💡 投資建議</b>
• 總體建議: {advice.get('總體建議', '未知')}
• 操作策略: {advice.get('操作策略', '未知')}

<i>分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""

        return message.strip()

    def _split_message(self, message: str, max_length: int) -> List[str]:
        """將長訊息分割成多個部分"""
        messages = []
        current_message = ""

        lines = message.split('\n')
        for line in lines:
            if len(current_message + line + '\n') > max_length:
                if current_message:
                    messages.append(current_message.strip())
                    current_message = ""
                # 如果單行過長，強制分割
                if len(line) > max_length:
                    chunks = [line[i:i+max_length] for i in range(0, len(line), max_length)]
                    messages.extend(chunks[:-1])  # 除了最後一個chunk
                    current_message = chunks[-1] + '\n'
                else:
                    current_message = line + '\n'
            else:
                current_message += line + '\n'

        if current_message:
            messages.append(current_message.strip())

        return messages

    def test_connection(self) -> bool:
        """測試 Telegram 連接"""
        if not self.enabled:
            return False

        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                bot_info = result.get('result', {})
                logger.info(f"Telegram 連接成功，機器人: {bot_info.get('first_name', 'Unknown')}")
                return True
            else:
                logger.error(f"Telegram 連接失敗: {result.get('description', '未知錯誤')}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"測試 Telegram 連接時發生網路錯誤: {e}")
            return False
        except Exception as e:
            logger.error(f"測試 Telegram 連接時發生錯誤: {e}")
            return False

    def send_daily_report(self, daily_data: Dict[str, Any]) -> bool:
        """發送每日報告"""
        try:
            message = self._format_daily_report(daily_data)
            return self.send_message(message)
        except Exception as e:
            logger.error(f"發送每日報告失敗: {e}")
            return False

    def _format_daily_report(self, data: Dict[str, Any]) -> str:
        """格式化每日報告"""
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        message = f"""
<b>📅 每日投資報告 - {date}</b>

<b>💰 投資組合概況</b>
• 總資產: {data.get('total_assets', 0):,.0f}
• 今日盈虧: {data.get('daily_pnl', 0):+,.0f}
• 累計收益率: {data.get('total_return', 0):+.2f}%

<b>📊 市場概況</b>
• 大盤指數: {data.get('market_index', 0):.2f}
• 大盤漲跌: {data.get('market_change', 0):+.2f}%
• 上漲家數: {data.get('advancing_stocks', 0)}
• 下跌家數: {data.get('declining_stocks', 0)}

<b>🎯 今日操作</b>
• 新增持倉: {data.get('new_positions', 0)}
• 平倉部位: {data.get('closed_positions', 0)}
• 交易金額: {data.get('trading_volume', 0):,.0f}

<b>⚠️ 風險提醒</b>
• 最大回撤: {data.get('max_drawdown', 0):.2f}%
• 風險等級: {data.get('risk_level', '未知')}

<i>報告生成時間: {datetime.now().strftime('%H:%M:%S')}</i>
"""

        return message.strip()

    def send_weekly_report(self, weekly_data: Dict[str, Any]) -> bool:
        """發送週報"""
        try:
            message = self._format_weekly_report(weekly_data)
            return self.send_message(message)
        except Exception as e:
            logger.error(f"發送週報失敗: {e}")
            return False

    def _format_weekly_report(self, data: Dict[str, Any]) -> str:
        """格式化週報"""
        week = data.get('week', f"{datetime.now().strftime('%Y年第%W週')}")

        message = f"""
<b>📊 週度投資報告 - {week}</b>

<b>💰 績效回顧</b>
• 週收益率: {data.get('weekly_return', 0):+.2f}%
• 累計收益率: {data.get('cumulative_return', 0):+.2f}%
• 最佳單日: {data.get('best_day', 0):+.2f}%
• 最差單日: {data.get('worst_day', 0):+.2f}%

<b>📈 交易統計</b>
• 交易次數: {data.get('total_trades', 0)}
• 勝率: {data.get('win_rate', 0):.2f}%
• 平均獲利: {data.get('avg_profit', 0):+.2f}
• 平均虧損: {data.get('avg_loss', 0):+.2f}

<b>🎯 策略表現</b>
• 訊號準確率: {data.get('signal_accuracy', 0):.2f}%
• 策略勝率: {data.get('strategy_win_rate', 0):.2f}%
• 風險調整收益: {data.get('risk_adjusted_return', 0):+.2f}

<b>💡 下週計劃</b>
• 關注行業: {data.get('focus_sectors', '待定')}
• 風險控制: {data.get('risk_management', '維持現有')}
• 投資策略: {data.get('investment_strategy', '觀望')}

<i>報告時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""

        return message.strip()

    def send_monthly_report(self, monthly_data: Dict[str, Any]) -> bool:
        """發送月報"""
        try:
            message = self._format_monthly_report(monthly_data)
            return self.send_message(message)
        except Exception as e:
            logger.error(f"發送月報失敗: {e}")
            return False

    def _format_monthly_report(self, data: Dict[str, Any]) -> str:
        """格式化月報"""
        month = data.get('month', datetime.now().strftime('%Y年%m月'))

        message = f"""
<b>📊 月度投資報告 - {month}</b>

<b>💰 投資回顧</b>
• 月收益率: {data.get('monthly_return', 0):+.2f}%
• 年化收益率: {data.get('annualized_return', 0):+.2f}%
• 最大回撤: {data.get('max_drawdown', 0):.2f}%
• 夏普比率: {data.get('sharpe_ratio', 0):.2f}

<b>📊 資產配置</b>
• 股票投資: {data.get('stock_allocation', 0):.1f}%
• 現金持有: {data.get('cash_allocation', 0):.1f}%
• 其他資產: {data.get('other_allocation', 0):.1f}%

<b>🎯 交易分析</b>
• 總交易次數: {data.get('total_trades', 0)}
• 月均交易次數: {data.get('avg_daily_trades', 0):.1f}
• 最佳交易日: {data.get('best_trading_day', '無')}
• 最差交易日: {data.get('worst_trading_day', '無')}

<b>📈 市場環境</b>
• 大盤表現: {data.get('market_performance', 0):+.2f}%
• 市場波動率: {data.get('market_volatility', 0):.2f}%
• 資金流向: {data.get('capital_flow', '中性')}

<b>💡 投資總結與展望</b>
{data.get('investment_summary', '本月投資表現穩定，繼續執行既定策略。')}

<i>報告生成時間: {datetime.now().strftime('%Y-%m-%d')}</i>
"""

        return message.strip()