# -*- coding: utf-8 -*-
"""
核心分析模組
Core Analyzer Module

包含技術分析引擎和強勢股評分邏輯
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """技術分析引擎"""

    def __init__(self, data):
        self.data = data.copy()
        self.levels = {}
        self.trend = {}
        self.position = {}

    def calculate_indicators(self):
        """計算所有技術指標"""
        if self.data.empty:
            logger.warning("無數據可用於計算指標")
            return False

        df = self.data

        try:
            # 均線系統
            df['SMA_5'] = df['Close'].rolling(5).mean()
            df['SMA_20'] = df['Close'].rolling(20).mean()
            df['SMA_60'] = df['Close'].rolling(60).mean()

            # 波動率指標
            df['TR'] = np.maximum(
                df['High'] - df['Low'],
                np.maximum(
                    abs(df['High'] - df['Close'].shift(1)),
                    abs(df['Low'] - df['Close'].shift(1))
                )
            )
            df['ATR_14'] = df['TR'].rolling(14).mean()

            # 動能指標 - MACD
            df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['Signal']

            # RSI指標
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['RSI_14'] = 100 - (100 / (1 + rs))

            # 乖離率
            df['Bias_5'] = (df['Close'] - df['SMA_5']) / df['SMA_5'] * 100
            df['Bias_20'] = (df['Close'] - df['SMA_20']) / df['SMA_20'] * 100
            df['Bias_60'] = (df['Close'] - df['SMA_60']) / df['SMA_60'] * 100

            # 相對強度
            df['RS_5'] = df['Close'] / df['Close'].rolling(5).mean()
            df['RS_20'] = df['Close'] / df['Close'].rolling(20).mean()

            # 布林通道
            df['BB_MA_20'] = df['Close'].rolling(20).mean()
            df['BB_UPPER'] = df['BB_MA_20'] + 2 * df['Close'].rolling(20).std()
            df['BB_LOWER'] = df['BB_MA_20'] - 2 * df['Close'].rolling(20).std()

            # KD指標
            low_min = df['Low'].rolling(9).min()
            high_max = df['High'].rolling(9).max()
            rsv = (df['Close'] - low_min) / (high_max - low_min) * 100
            df['K'] = rsv.ewm(com=2).mean()
            df['D'] = df['K'].ewm(com=2).mean()
            df['KD_Cross'] = np.where(df['K'] > df['D'], 1, -1)

            # 計算KD指標狀態
            df['KD_Status'] = np.select(
                [
                    (df['K'] > 80) & (df['D'] > 80),
                    (df['K'] < 20) & (df['D'] < 20),
                    (df['K'] > df['D']) & (df['K'] < 50),
                    (df['K'] < df['D']) & (df['K'] > 50)
                ],
                ['超買區', '超賣區', '黃金交叉', '死亡交叉'],
                default='中性'
            )

            self.data = df
            return True
        except Exception as e:
            logger.error(f"計算技術指標失敗: {e}")
            return False

    def identify_key_levels(self):
        """識別關鍵支撐壓力位"""
        df = self.data
        recent = df.iloc[-90:] if len(df) >= 90 else df

        try:
            # 支撐位識別
            lows = recent['Low'].rolling(5).min().dropna()
            self.levels['support'] = round(lows.nsmallest(3).min(), 2)

            # 壓力位識別
            highs = recent['High'].rolling(5).max().dropna()
            self.levels['resistance'] = round(highs.nlargest(3).max(), 2)

            # 動態緩衝區
            atr = df['ATR_14'].iloc[-1] if not pd.isna(df['ATR_14'].iloc[-1]) else 0
            self.levels['atr'] = round(atr, 2)
            self.levels['buy_zone'] = round(self.levels['support'] + 0.3 * atr, 2)
            self.levels['sell_zone'] = round(self.levels['resistance'] - 0.3 * atr, 2)
            self.levels['stop_loss_buy'] = round(self.levels['support'] - 1.5 * atr, 2)
            self.levels['stop_loss_sell'] = round(self.levels['resistance'] + 1.5 * atr, 2)
            self.levels['target_price'] = round(self.levels['resistance'] * 1.1, 2)
            self.levels['current_price'] = round(df['Close'].iloc[-1], 2)
        except Exception as e:
            logger.error(f"識別關鍵價位失敗: {e}")
            self.levels = {
                'support': 0,
                'resistance': 0,
                'atr': 0,
                'buy_zone': 0,
                'sell_zone': 0,
                'stop_loss_buy': 0,
                'stop_loss_sell': 0,
                'target_price': 0,
                'current_price': round(df['Close'].iloc[-1], 2) if not df.empty else 0
            }

    def determine_trend(self):
        """判斷市場趨勢"""
        df = self.data
        latest = df.iloc[-1]

        try:
            # 均線排列判斷
            ma_ranking = {
                'price_sma5': latest['Close'] - latest['SMA_5'],
                'price_sma20': latest['Close'] - latest['SMA_20'],
                'price_sma60': latest['Close'] - latest['SMA_60'],
                'sma5_sma20': latest['SMA_5'] - latest['SMA_20'],
                'sma20_sma60': latest['SMA_20'] - latest['SMA_60']
            }

            # MACD判斷
            macd_bullish = latest['MACD'] > 0 and latest['MACD_Hist'] > 0
            macd_bearish = latest['MACD'] < 0 and latest['MACD_Hist'] < 0

            # RSI判斷
            rsi_status = "超買" if latest['RSI_14'] > 70 else "超賣" if latest['RSI_14'] < 30 else "中性"

            # 布林通道判斷
            bollinger_status = "突破上軌" if latest['Close'] > latest['BB_UPPER'] else "跌破下軌" if latest['Close'] < latest['BB_LOWER'] else "通道內"

            # KD指標判斷
            kd_bullish = latest['K'] > latest['D'] and latest['K'] > 50
            kd_bearish = latest['K'] < latest['D'] and latest['K'] < 50

            # 趨勢綜合判斷
            if (ma_ranking['price_sma5'] > 0 and
                ma_ranking['price_sma20'] > 0 and
                ma_ranking['price_sma60'] > 0 and
                ma_ranking['sma5_sma20'] > 0 and
                ma_ranking['sma20_sma60'] > 0):

                if macd_bullish and latest['RSI_14'] < 70 and kd_bullish:
                    self.trend['trend'] = "強勢多頭"
                    self.trend['strength'] = min(9, int(7 + latest['Bias_5'] / 1.5))
                else:
                    self.trend['trend'] = "多頭"
                    self.trend['strength'] = min(7, int(5 + latest['Bias_5'] / 2))

            elif (ma_ranking['price_sma5'] < 0 and
                  ma_ranking['price_sma20'] < 0 and
                  ma_ranking['price_sma60'] < 0 and
                  ma_ranking['sma5_sma20'] < 0 and
                  ma_ranking['sma20_sma60'] < 0):

                if macd_bearish and latest['RSI_14'] > 30 and kd_bearish:
                    self.trend['trend'] = "強勢空頭"
                    self.trend['strength'] = min(9, int(7 + abs(latest['Bias_5']) / 1.5))
                else:
                    self.trend['trend'] = "空頭"
                    self.trend['strength'] = min(7, int(5 + abs(latest['Bias_5']) / 2))

            else:
                if abs(latest['Bias_20']) < 1.5 and abs(latest['MACD_Hist']) < (self.levels['atr'] * 0.1):
                    self.trend['trend'] = "盤整"
                    self.trend['strength'] = 3
                else:
                    self.trend['trend'] = "多空拉鋸"
                    self.trend['strength'] = 5

            # 儲存輔助指標
            self.trend['rsi_status'] = rsi_status
            self.trend['rsi_value'] = round(latest['RSI_14'], 2)
            self.trend['macd_status'] = "多頭" if macd_bullish else "空頭" if macd_bearish else "中性"
            self.trend['bollinger_status'] = bollinger_status
            self.trend['kd_status'] = latest['KD_Status']
            self.trend['k_value'] = round(latest['K'], 2)
            self.trend['d_value'] = round(latest['D'], 2)
        except Exception as e:
            logger.error(f"判斷趨勢失敗: {e}")
            self.trend = {
                'trend': "未知",
                'strength': 0,
                'rsi_status': "未知",
                'rsi_value': 0,
                'macd_status': "未知",
                'bollinger_status': "未知",
                'kd_status': "未知",
                'k_value': 0,
                'd_value': 0
            }

    def analyze_position_stage(self):
        """分析股票位階"""
        df = self.data
        latest = df.iloc[-1]

        try:
            # 計算最近一年的價格分位
            yearly_low = df['Close'].min()
            yearly_high = df['Close'].max()
            current_pct = (latest['Close'] - yearly_low) / (yearly_high - yearly_low) * 100

            # 位階判斷
            if current_pct < 30:
                stage = "低檔"
                stage_desc = "長期投資價值區"
                stage_color = "green"
            elif current_pct < 70:
                stage = "中檔"
                stage_desc = "趨勢交易機會區"
                stage_color = "blue"
            else:
                stage = "高檔"
                stage_desc = "獲利了結警戒區"
                stage_color = "red"

            self.position = {
                'stage': stage,
                'stage_desc': stage_desc,
                'stage_color': stage_color,
                'yearly_low': yearly_low,
                'yearly_high': yearly_high,
                'current_pct': round(current_pct, 1)
            }
        except Exception as e:
            logger.error(f"分析位階失敗: {e}")
            self.position = {
                'stage': "未知",
                'stage_desc': "數據不足",
                'stage_color': "gray",
                'yearly_low': 0,
                'yearly_high': 0,
                'current_pct': 0
            }

    def generate_report(self):
        """生成分析報告"""
        df = self.data
        latest = df.iloc[-1]

        report = {
            'current_price': latest['Close'],
            'sma_5': latest['SMA_5'],
            'sma_20': latest['SMA_20'],
            'sma_60': latest['SMA_60'],
            'atr': self.levels['atr'],
            'macd': latest['MACD'],
            'macd_hist': latest['MACD_Hist'],
            'rsi': self.trend['rsi_value'],
            'support': self.levels['support'],
            'resistance': self.levels['resistance'],
            'trend': self.trend['trend'],
            'strength': self.trend['strength'],
            'position': self.position['stage'],
            'position_pct': self.position['current_pct'],
            'bollinger': self.trend['bollinger_status'],
            'kd_status': self.trend['kd_status'],
            'k_value': self.trend['k_value'],
            'd_value': self.trend['d_value'],
            'target_price': self.levels.get('target_price', 0),
            'stop_loss': self.levels.get('stop_loss_buy', 0)
        }

        return report

    def generate_trading_strategy(self):
        """生成交易策略建議"""
        report = self.generate_report()
        strategy = {
            'short_term': "",
            'medium_term': "",
            'long_term': ""
        }

        # 短期策略 (1-5天)
        if report['trend'] == "強勢多頭":
            strategy['short_term'] = "強力買入，目標價: {:.2f}，停損價: {:.2f}".format(
                report['resistance'] * 1.05,
                report['support'] * 0.95
            )
        elif report['trend'] == "多頭":
            strategy['short_term'] = "買入，目標價: {:.2f}，停損價: {:.2f}".format(
                report['resistance'],
                report['support'] * 0.97
            )
        elif report['trend'] == "空頭":
            strategy['short_term'] = "觀望或少量賣出，停損價: {:.2f}".format(
                report['resistance'] * 1.03
            )
        else:
            strategy['short_term'] = "觀望，等待突破方向"

        # 中期策略 (1-3個月)
        if report['position'] == "低檔":
            strategy['medium_term'] = "分批建倉，目標價: {:.2f}".format(
                self.position['yearly_high'] * 0.8 if 'yearly_high' in self.position else report['resistance']
            )
        elif report['position'] == "中檔":
            strategy['medium_term'] = "趨勢跟隨，目標價: {:.2f}，停損價: {:.2f}".format(
                report['resistance'] * 1.1,
                report['support'] * 0.9
            )
        else:
            strategy['medium_term'] = "獲利了結或等待回調"

        # 長期策略 (3個月以上)
        if report['position_pct'] < 30:
            strategy['long_term'] = "價值投資，長期持有"
        elif report['position_pct'] < 70:
            strategy['long_term'] = "趨勢投資，定期檢視"
        else:
            strategy['long_term'] = "高檔風險區，謹慎操作"

        return strategy


class StockAnalyzer:
    """股票分析主類"""

    def __init__(self):
        from data.fetcher import StockDataFetcher
        from data.indicators import TechnicalIndicators

        self.fetcher = StockDataFetcher()
        self.analyzer = None
        self.strong_stocks = []
        self.cache_expiry = 24 * 3600

    def analyze_stock(self, stock_code, hist_data):
        """分析單支股票"""
        try:
            if hist_data is None or hist_data.empty:
                return None

            # 創建技術分析器
            analyzer = TechnicalAnalyzer(hist_data)

            # 計算指標
            if not analyzer.calculate_indicators():
                return None

            # 識別關鍵價位
            analyzer.identify_key_levels()

            # 判斷趨勢
            analyzer.determine_trend()

            # 分析位階
            analyzer.analyze_position_stage()

            # 生成報告
            report = analyzer.generate_report()
            strategy = analyzer.generate_trading_strategy()

            return {
                'stock_code': stock_code,
                'technical_data': report,
                'strategy': strategy,
                'levels': analyzer.levels,
                'trend': analyzer.trend,
                'position': analyzer.position,
                'overall_score': self.calculate_overall_score(analyzer),
                'investment_recommendation': self.generate_investment_recommendation(analyzer)
            }

        except Exception as e:
            logger.error(f"分析股票 {stock_code} 失敗: {e}")
            return None

    def find_strong_stocks(self, target_date, top_n=50, min_volume=300):
        """尋找強勢股"""
        try:
            # 獲取漲幅前N名
            trading_day = self.fetcher.get_nearest_trading_day(target_date)
            if not trading_day:
                return []

            # 獲取所有股票
            all_stocks = self.fetcher.get_all_stocks()
            if not all_stocks:
                return []

            results = []

            for code, name in list(all_stocks.items())[:100]:  # 測試前100支
                try:
                    # 分析每支股票
                    analysis = self.analyze_stock(code, days=30)
                    if not analysis:
                        continue

                    # 計算強勢評分
                    score = self.evaluate_strength({
                        'trend': analysis['trend']['trend'],
                        'position': analysis['position']['stage'],
                        'volume': min_volume,  # 簡化處理
                        'kd_status': analysis['trend']['kd_status'],
                        'rsi': analysis['trend']['rsi_value']
                    })

                    if score >= 4:  # 只保留評分4分以上的
                        results.append({
                            '代碼': code,
                            '名稱': name,
                            '強勢評分': score,
                            '趨勢': analysis['trend']['trend'],
                            '位階': analysis['position']['stage'],
                            '收盤價': analysis['technical_data']['current_price'],
                            'RSI': analysis['trend']['rsi_value'],
                            'KD狀態': analysis['trend']['kd_status']
                        })

                except Exception as e:
                    logger.debug(f"分析 {code} 失敗: {e}")
                    continue

            # 按評分排序
            results.sort(key=lambda x: x['強勢評分'], reverse=True)
            return results[:top_n]

        except Exception as e:
            logger.error(f"尋找強勢股失敗: {e}")
            return []

    def evaluate_strength(self, factors):
        """評估股票強勢程度"""
        score = 0

        # 趨勢評分 (最高3分)
        trend = factors.get('trend', '')
        if '強勢多頭' in trend:
            score += 3
        elif '多頭' in trend:
            score += 2
        elif '盤整' in trend:
            score += 1

        # 位階評分 (最高2分)
        position = factors.get('position', '')
        if position == '低檔':
            score += 2
        elif position == '中檔':
            score += 1

        # 技術指標評分 (最高3分)
        kd_status = factors.get('kd_status', '')
        rsi = factors.get('rsi', 50)

        if '黃金交叉' in kd_status:
            score += 2
        if 30 <= rsi <= 70:
            score += 1

        # 成交量評分 (最高2分)
        volume = factors.get('volume', 0)
        if volume >= 1000:  # 張
            score += 2
        elif volume >= 500:
            score += 1

        return min(10, score)  # 最高10分

    def find_top_gainers(self, target_date, top_n=50, min_volume=300):
        """尋找漲幅前N名"""
        try:
            trading_day = self.fetcher.get_nearest_trading_day(target_date)
            if not trading_day:
                return []

            all_stocks = self.fetcher.get_all_stocks()
            if not all_stocks:
                return []

            changes = []

            for code, name in list(all_stocks.items())[:200]:  # 測試前200支
                try:
                    # 獲取當日數據
                    start_date = (trading_day - timedelta(days=7)).strftime('%Y-%m-%d')
                    end_date = (trading_day + timedelta(days=1)).strftime('%Y-%m-%d')

                    data = self.fetcher.fetch_historical_data(code, start_date, end_date)
                    if data is None or len(data) < 2:
                        continue

                    day_data = data[data.index.date == trading_day]
                    if day_data.empty:
                        continue

                    latest = day_data.iloc[-1]
                    prev_data = data[data.index.date < trading_day]
                    if prev_data.empty:
                        continue

                    prev_close = prev_data.iloc[-1]['Close']
                    change_pct = (latest['Close'] / prev_close - 1) * 100

                    if latest['Volume'] >= min_volume * 1000:
                        changes.append({
                            '代碼': code,
                            '名稱': name,
                            '漲幅%': round(change_pct, 2),
                            '成交量(張)': round(latest['Volume'] / 1000),
                            '收盤價': latest['Close']
                        })

                except Exception as e:
                    continue

            # 排序並返回前N名
            changes.sort(key=lambda x: x['漲幅%'], reverse=True)
            return changes[:top_n]

        except Exception as e:
            logger.error(f"尋找漲幅排行失敗: {e}")
            return []

    def calculate_overall_score(self, analyzer):
        """計算綜合評分"""
        try:
            score = 0
            max_score = 100

            # 趨勢評分 (30分)
            trend_score = 0
            if analyzer.trend.get('trend') == "強勢多頭":
                trend_score = 30
            elif analyzer.trend.get('trend') == "多頭":
                trend_score = 20
            elif analyzer.trend.get('trend') == "多空拉鋸":
                trend_score = 15
            elif analyzer.trend.get('trend') == "空頭":
                trend_score = 5
            score += trend_score

            # 技術指標評分 (30分)
            tech_score = 0
            rsi = analyzer.trend.get('rsi_value', 50)
            if 30 <= rsi <= 70:
                tech_score += 10
            elif rsi < 30 or rsi > 70:
                tech_score += 5

            kd_status = analyzer.trend.get('kd_status', '')
            if kd_status in ['黃金交叉', '多頭排列']:
                tech_score += 10
            elif kd_status in ['死亡交叉', '空頭排列']:
                tech_score -= 5

            macd_status = analyzer.trend.get('macd_status', '')
            if macd_status == "多頭":
                tech_score += 10
            elif macd_status == "空頭":
                tech_score -= 5

            score += min(tech_score, 30)

            # 位階評分 (20分)
            position_score = 0
            stage = analyzer.position.get('stage', '')
            if stage == "低檔":
                position_score = 20
            elif stage == "中檔":
                position_score = 10
            elif stage == "高檔":
                position_score = 0
            score += position_score

            # 相對強度評分 (20分)
            strength_score = min(analyzer.position.get('relative_strength', 0) * 2, 20)
            score += strength_score

            # 確定等級和評價
            if score >= 80:
                grade = "A"
                evaluation = "極力推薦"
            elif score >= 70:
                grade = "B"
                evaluation = "推薦買入"
            elif score >= 60:
                grade = "C"
                evaluation = "可考慮"
            elif score >= 50:
                grade = "D"
                evaluation = "謹慎觀望"
            else:
                grade = "F"
                evaluation = "不建議"

            return {
                '總分': score,
                '等級': grade,
                '評價': evaluation
            }

        except Exception as e:
            logger.error(f"計算綜合評分失敗: {e}")
            return {
                '總分': 0,
                '等級': 'F',
                '評價': '計算失敗'
            }

    def generate_investment_recommendation(self, analyzer):
        """生成投資建議"""
        try:
            score_data = self.calculate_overall_score(analyzer)
            trend = analyzer.trend.get('trend', '')
            position = analyzer.position.get('stage', '')

            # 操作建議
            if score_data['等級'] in ['A', 'B']:
                operation = "積極買入"
            elif score_data['等級'] == 'C':
                operation = "適度買入"
            elif score_data['等級'] == 'D':
                operation = "觀望為主"
            else:
                operation = "避免買入"

            # 倉位建議
            if position == "低檔":
                position_suggestion = "可全倉"
            elif position == "中檔":
                position_suggestion = "5-7成倉"
            else:
                position_suggestion = "輕倉或空倉"

            # 持有期間
            if trend in ["強勢多頭", "多頭"]:
                holding_period = "中長期持有"
            elif trend == "多空拉鋸":
                holding_period = "短期操作"
            else:
                holding_period = "盡快了結"

            return {
                '操作建議': operation,
                '倉位建議': position_suggestion,
                '持有期間': holding_period
            }

        except Exception as e:
            logger.error(f"生成投資建議失敗: {e}")
            return {
                '操作建議': '無法評估',
                '倉位建議': '無法評估',
                '持有期間': '無法評估'
            }