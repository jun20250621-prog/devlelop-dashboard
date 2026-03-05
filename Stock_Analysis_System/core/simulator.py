# -*- coding: utf-8 -*-
"""
績效模擬模組
Performance Simulator Module

回測和模擬交易策略績效
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class PerformanceSimulator:
    """績效模擬器"""

    def __init__(self):
        self.portfolio = {}
        self.trades = []
        self.performance_metrics = {}
        self.risk_metrics = {}

    def run_backtest(self, strategy_data: Dict[str, Any], initial_capital: float = 1000000,
                    start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """執行回測"""
        try:
            if not strategy_data or 'signals' not in strategy_data:
                return {'error': '無效的策略數據'}

            signals = strategy_data['signals']
            stock_code = strategy_data.get('stock_code', 'UNKNOWN')

            # 初始化投資組合
            self.portfolio = {
                'cash': initial_capital,
                'positions': {},
                'total_value': initial_capital,
                'trades': []
            }

            # 執行交易
            for signal in signals:
                self._execute_trade(signal)

            # 計算績效指標
            performance = self._calculate_performance_metrics()

            # 計算風險指標
            risk_metrics = self._calculate_risk_metrics()

            # 生成回測報告
            report = {
                '股票代碼': stock_code,
                '回測期間': f"{start_date} 至 {end_date}",
                '初始資金': initial_capital,
                '最終價值': self.portfolio['total_value'],
                '總收益率': performance.get('total_return', 0),
                '年化收益率': performance.get('annual_return', 0),
                '夏普比率': risk_metrics.get('sharpe_ratio', 0),
                '最大回撤': risk_metrics.get('max_drawdown', 0),
                '勝率': performance.get('win_rate', 0),
                '總交易次數': len(self.portfolio['trades']),
                '交易明細': self.portfolio['trades'],
                '績效指標': performance,
                '風險指標': risk_metrics
            }

            return report

        except Exception as e:
            logger.error(f"執行回測失敗: {e}")
            return {'error': str(e)}

    def _execute_trade(self, signal: Dict[str, Any]):
        """執行單筆交易"""
        try:
            action = signal.get('action', '')
            stock_code = signal.get('stock_code', '')
            price = signal.get('price', 0)
            quantity = signal.get('quantity', 0)
            date = signal.get('date', datetime.now().strftime('%Y-%m-%d'))

            if action not in ['BUY', 'SELL']:
                return

            # 計算交易金額
            trade_value = price * quantity

            if action == 'BUY':
                # 檢查資金是否足夠
                if self.portfolio['cash'] >= trade_value:
                    # 執行買入
                    self.portfolio['cash'] -= trade_value
                    if stock_code not in self.portfolio['positions']:
                        self.portfolio['positions'][stock_code] = {
                            'quantity': 0,
                            'avg_price': 0,
                            'total_cost': 0
                        }

                    # 更新持倉
                    position = self.portfolio['positions'][stock_code]
                    total_quantity = position['quantity'] + quantity
                    total_cost = position['total_cost'] + trade_value
                    avg_price = total_cost / total_quantity

                    position['quantity'] = total_quantity
                    position['avg_price'] = avg_price
                    position['total_cost'] = total_cost

                    # 記錄交易
                    trade = {
                        'date': date,
                        'action': '買入',
                        'stock_code': stock_code,
                        'price': price,
                        'quantity': quantity,
                        'value': trade_value,
                        'cash_after': self.portfolio['cash']
                    }
                    self.portfolio['trades'].append(trade)

            elif action == 'SELL':
                # 檢查是否有足夠持倉
                if stock_code in self.portfolio['positions']:
                    position = self.portfolio['positions'][stock_code]
                    if position['quantity'] >= quantity:
                        # 執行賣出
                        self.portfolio['cash'] += trade_value

                        # 更新持倉
                        position['quantity'] -= quantity
                        position['total_cost'] = position['avg_price'] * position['quantity']

                        # 如果持倉為0，刪除該持倉
                        if position['quantity'] == 0:
                            del self.portfolio['positions'][stock_code]

                        # 計算盈虧
                        cost_basis = position['avg_price'] * quantity
                        profit_loss = trade_value - cost_basis

                        # 記錄交易
                        trade = {
                            'date': date,
                            'action': '賣出',
                            'stock_code': stock_code,
                            'price': price,
                            'quantity': quantity,
                            'value': trade_value,
                            'profit_loss': profit_loss,
                            'cash_after': self.portfolio['cash']
                        }
                        self.portfolio['trades'].append(trade)

            # 更新總價值
            self._update_portfolio_value(price, stock_code)

        except Exception as e:
            logger.error(f"執行交易失敗: {e}")

    def _update_portfolio_value(self, current_price: float, stock_code: str):
        """更新投資組合價值"""
        try:
            total_value = self.portfolio['cash']

            # 計算持倉價值
            for code, position in self.portfolio['positions'].items():
                if code == stock_code:
                    # 使用當前價格更新
                    position_value = current_price * position['quantity']
                else:
                    # 對於其他持倉，使用平均價格估算（實際應用中應使用最新價格）
                    position_value = position['avg_price'] * position['quantity']
                total_value += position_value

            self.portfolio['total_value'] = total_value

        except Exception as e:
            logger.error(f"更新投資組合價值失敗: {e}")

    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """計算績效指標"""
        try:
            initial_capital = 1000000  # 假設初始資金
            final_value = self.portfolio['total_value']
            trades = self.portfolio['trades']

            # 總收益率
            total_return = (final_value - initial_capital) / initial_capital * 100

            # 年化收益率（簡化計算，假設1年）
            annual_return = total_return

            # 勝率
            winning_trades = [t for t in trades if t.get('profit_loss', 0) > 0]
            win_rate = len(winning_trades) / len(trades) * 100 if trades else 0

            # 平均盈虧
            profits = [t.get('profit_loss', 0) for t in trades if 'profit_loss' in t]
            avg_profit = sum(profits) / len(profits) if profits else 0

            # 總交易次數
            total_trades = len(trades)

            return {
                'total_return': round(total_return, 2),
                'annual_return': round(annual_return, 2),
                'win_rate': round(win_rate, 2),
                'avg_profit': round(avg_profit, 2),
                'total_trades': total_trades
            }

        except Exception as e:
            logger.error(f"計算績效指標失敗: {e}")
            return {}

    def _calculate_risk_metrics(self) -> Dict[str, Any]:
        """計算風險指標"""
        try:
            trades = self.portfolio['trades']
            if not trades:
                return {'sharpe_ratio': 0, 'max_drawdown': 0, 'volatility': 0}

            # 計算日收益率（簡化處理）
            portfolio_values = []
            current_value = 1000000  # 初始資金

            for trade in trades:
                if 'cash_after' in trade:
                    current_value = trade['cash_after']
                    # 加上持倉價值估算
                    for code, position in self.portfolio['positions'].items():
                        current_value += position['avg_price'] * position['quantity']
                portfolio_values.append(current_value)

            if len(portfolio_values) < 2:
                return {'sharpe_ratio': 0, 'max_drawdown': 0, 'volatility': 0}

            # 計算收益率
            returns = []
            for i in range(1, len(portfolio_values)):
                ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
                returns.append(ret)

            returns = np.array(returns)

            # 夏普比率（假設無風險利率為2%）
            risk_free_rate = 0.02 / 252  # 日化無風險利率
            excess_returns = returns - risk_free_rate
            sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0

            # 最大回撤
            peak = portfolio_values[0]
            max_drawdown = 0
            for value in portfolio_values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)

            # 波動率
            volatility = np.std(returns) * np.sqrt(252)

            return {
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown * 100, 2),
                'volatility': round(volatility * 100, 2)
            }

        except Exception as e:
            logger.error(f"計算風險指標失敗: {e}")
            return {'sharpe_ratio': 0, 'max_drawdown': 0, 'volatility': 0}

    def simulate_trading_strategy(self, stock_data: pd.DataFrame, strategy_params: Dict[str, Any]) -> Dict[str, Any]:
        """模擬交易策略"""
        try:
            signals = self._generate_trading_signals(stock_data, strategy_params)

            # 執行回測
            backtest_result = self.run_backtest({
                'signals': signals,
                'stock_code': strategy_params.get('stock_code', 'SIMULATION')
            })

            # 生成模擬報告
            simulation_report = {
                '策略名稱': strategy_params.get('strategy_name', '自定義策略'),
                '模擬期間': f"{stock_data.index.min()} 至 {stock_data.index.max()}",
                '總收益率': backtest_result.get('總收益率', 0),
                '年化收益率': backtest_result.get('年化收益率', 0),
                '夏普比率': backtest_result.get('夏普比率', 0),
                '最大回撤': backtest_result.get('最大回撤', 0),
                '勝率': backtest_result.get('勝率', 0),
                '總交易次數': backtest_result.get('總交易次數', 0),
                '訊號統計': self._analyze_signals(signals),
                '詳細交易': backtest_result.get('交易明細', [])
            }

            return simulation_report

        except Exception as e:
            logger.error(f"模擬交易策略失敗: {e}")
            return {'error': str(e)}

    def _generate_trading_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成交易訊號"""
        signals = []
        position = 0  # 0: 空倉, 1: 持倉

        try:
            strategy_type = params.get('strategy_type', 'moving_average')

            if strategy_type == 'moving_average':
                signals = self._ma_crossover_signals(data, params)
            elif strategy_type == 'rsi':
                signals = self._rsi_signals(data, params)
            elif strategy_type == 'macd':
                signals = self._macd_signals(data, params)
            elif strategy_type == 'bollinger_bands':
                signals = self._bollinger_signals(data, params)

        except Exception as e:
            logger.error(f"生成交易訊號失敗: {e}")

        return signals

    def _ma_crossover_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """均線交叉訊號"""
        signals = []
        fast_period = params.get('fast_ma', 5)
        slow_period = params.get('slow_ma', 20)

        data = data.copy()
        data['fast_ma'] = data['Close'].rolling(fast_period).mean()
        data['slow_ma'] = data['Close'].rolling(slow_period).mean()

        position = 0

        for i in range(1, len(data)):
            prev_fast = data['fast_ma'].iloc[i-1]
            prev_slow = data['slow_ma'].iloc[i-1]
            curr_fast = data['fast_ma'].iloc[i]
            curr_slow = data['slow_ma'].iloc[i]

            # 黃金交叉 - 買入訊號
            if prev_fast <= prev_slow and curr_fast > curr_slow and position == 0:
                signal = {
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'action': 'BUY',
                    'stock_code': params.get('stock_code', 'UNKNOWN'),
                    'price': data['Close'].iloc[i],
                    'quantity': params.get('position_size', 1000),
                    'signal_type': 'MA交叉買入'
                }
                signals.append(signal)
                position = 1

            # 死亡交叉 - 賣出訊號
            elif prev_fast >= prev_slow and curr_fast < curr_slow and position == 1:
                signal = {
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'action': 'SELL',
                    'stock_code': params.get('stock_code', 'UNKNOWN'),
                    'price': data['Close'].iloc[i],
                    'quantity': params.get('position_size', 1000),
                    'signal_type': 'MA交叉賣出'
                }
                signals.append(signal)
                position = 0

        return signals

    def _rsi_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """RSI訊號"""
        signals = []
        rsi_period = params.get('rsi_period', 14)
        overbought = params.get('overbought', 70)
        oversold = params.get('oversold', 30)

        data = data.copy()
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        position = 0

        for i in range(rsi_period, len(data)):
            rsi = data['RSI'].iloc[i]
            prev_rsi = data['RSI'].iloc[i-1]

            # RSI超賣 - 買入訊號
            if prev_rsi >= oversold and rsi < oversold and position == 0:
                signal = {
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'action': 'BUY',
                    'stock_code': params.get('stock_code', 'UNKNOWN'),
                    'price': data['Close'].iloc[i],
                    'quantity': params.get('position_size', 1000),
                    'signal_type': f'RSI超賣買入 ({rsi:.1f})'
                }
                signals.append(signal)
                position = 1

            # RSI超買 - 賣出訊號
            elif prev_rsi <= overbought and rsi > overbought and position == 1:
                signal = {
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'action': 'SELL',
                    'stock_code': params.get('stock_code', 'UNKNOWN'),
                    'price': data['Close'].iloc[i],
                    'quantity': params.get('position_size', 1000),
                    'signal_type': f'RSI超買賣出 ({rsi:.1f})'
                }
                signals.append(signal)
                position = 0

        return signals

    def _macd_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """MACD訊號"""
        signals = []

        data = data.copy()
        data['MACD'] = data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

        position = 0

        for i in range(1, len(data)):
            prev_macd = data['MACD'].iloc[i-1]
            prev_signal = data['Signal'].iloc[i-1]
            curr_macd = data['MACD'].iloc[i]
            curr_signal = data['Signal'].iloc[i]

            # MACD上穿訊號線 - 買入
            if prev_macd <= prev_signal and curr_macd > curr_signal and position == 0:
                signal = {
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'action': 'BUY',
                    'stock_code': params.get('stock_code', 'UNKNOWN'),
                    'price': data['Close'].iloc[i],
                    'quantity': params.get('position_size', 1000),
                    'signal_type': 'MACD買入訊號'
                }
                signals.append(signal)
                position = 1

            # MACD下穿訊號線 - 賣出
            elif prev_macd >= prev_signal and curr_macd < curr_signal and position == 1:
                signal = {
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'action': 'SELL',
                    'stock_code': params.get('stock_code', 'UNKNOWN'),
                    'price': data['Close'].iloc[i],
                    'quantity': params.get('position_size', 1000),
                    'signal_type': 'MACD賣出訊號'
                }
                signals.append(signal)
                position = 0

        return signals

    def _bollinger_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """布林通道訊號"""
        signals = []
        period = params.get('bb_period', 20)
        std_dev = params.get('bb_std', 2)

        data = data.copy()
        data['MA'] = data['Close'].rolling(period).mean()
        data['Upper'] = data['MA'] + std_dev * data['Close'].rolling(period).std()
        data['Lower'] = data['MA'] - std_dev * data['Close'].rolling(period).std()

        position = 0

        for i in range(period, len(data)):
            close = data['Close'].iloc[i]
            lower = data['Lower'].iloc[i]
            upper = data['Upper'].iloc[i]

            # 價格觸及下軌 - 買入訊號
            if close <= lower and position == 0:
                signal = {
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'action': 'BUY',
                    'stock_code': params.get('stock_code', 'UNKNOWN'),
                    'price': close,
                    'quantity': params.get('position_size', 1000),
                    'signal_type': '布林下軌買入'
                }
                signals.append(signal)
                position = 1

            # 價格觸及上軌 - 賣出訊號
            elif close >= upper and position == 1:
                signal = {
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'action': 'SELL',
                    'stock_code': params.get('stock_code', 'UNKNOWN'),
                    'price': close,
                    'quantity': params.get('position_size', 1000),
                    'signal_type': '布林上軌賣出'
                }
                signals.append(signal)
                position = 0

        return signals

    def _analyze_signals(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析訊號統計"""
        if not signals:
            return {'總訊號數': 0, '買入訊號': 0, '賣出訊號': 0}

        buy_signals = [s for s in signals if s.get('action') == 'BUY']
        sell_signals = [s for s in signals if s.get('action') == 'SELL']

        return {
            '總訊號數': len(signals),
            '買入訊號': len(buy_signals),
            '賣出訊號': len(sell_signals),
            '訊號類型分布': self._count_signal_types(signals)
        }

    def _count_signal_types(self, signals: List[Dict[str, Any]]) -> Dict[str, int]:
        """統計訊號類型"""
        type_count = {}
        for signal in signals:
            signal_type = signal.get('signal_type', '未知')
            type_count[signal_type] = type_count.get(signal_type, 0) + 1
        return type_count

    def optimize_strategy(self, data: pd.DataFrame, strategy_type: str, param_ranges: Dict[str, List[Any]]) -> Dict[str, Any]:
        """優化策略參數"""
        try:
            best_result = None
            best_score = -float('inf')

            # 網格搜索參數組合
            param_combinations = self._generate_param_combinations(param_ranges)

            for params in param_combinations:
                strategy_params = {
                    'strategy_type': strategy_type,
                    'stock_code': 'OPTIMIZATION',
                    **params
                }

                # 執行模擬
                result = self.simulate_trading_strategy(data, strategy_params)

                # 評估結果（使用夏普比率作為評分標準）
                score = result.get('夏普比率', 0)

                if score > best_score:
                    best_score = score
                    best_result = {
                        'parameters': params,
                        'performance': result,
                        'score': score
                    }

            return best_result if best_result else {'error': '優化失敗'}

        except Exception as e:
            logger.error(f"優化策略失敗: {e}")
            return {'error': str(e)}

    def _generate_param_combinations(self, param_ranges: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """生成參數組合"""
        import itertools

        keys = list(param_ranges.keys())
        values = list(param_ranges.values())

        combinations = []
        for combination in itertools.product(*values):
            param_dict = dict(zip(keys, combination))
            combinations.append(param_dict)

        return combinations