# -*- coding: utf-8 -*-
"""
技術指標計算模組
Technical Indicators Module

從 analysis_system_v3d4.py 提取的核心技術指標計算函式
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """技術指標計算類"""

    @staticmethod
    def calculate_all_indicators(data):
        """
        計算所有技術指標

        Args:
            data: DataFrame 包含 OHLCV 數據

        Returns:
            DataFrame: 包含所有技術指標的數據
        """
        if data.empty:
            logger.warning("無數據可用於計算指標")
            return data

        df = data.copy()

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

            logger.info("技術指標計算完成")
            return df

        except Exception as e:
            logger.error(f"計算技術指標失敗: {e}")
            return data

    @staticmethod
    def calculate_moving_averages(data, periods=[5, 20, 60]):
        """
        計算移動平均線

        Args:
            data: DataFrame 包含 Close 價格
            periods: 移動平均期數列表

        Returns:
            DataFrame: 包含移動平均線的數據
        """
        df = data.copy()
        for period in periods:
            df[f'SMA_{period}'] = df['Close'].rolling(period).mean()
        return df

    @staticmethod
    def calculate_rsi(data, period=14):
        """
        計算 RSI 指標

        Args:
            data: DataFrame 包含 Close 價格
            period: RSI 計算期數

        Returns:
            Series: RSI 值
        """
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
        """
        計算 MACD 指標

        Args:
            data: DataFrame 包含 Close 價格
            fast_period: 快線期數
            slow_period: 慢線期數
            signal_period: 訊號線期數

        Returns:
            tuple: (MACD, Signal, Histogram)
        """
        fast_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram

    @staticmethod
    def calculate_kd(data, period=9):
        """
        計算 KD 指標

        Args:
            data: DataFrame 包含 High, Low, Close 價格
            period: KD 計算期數

        Returns:
            tuple: (K值, D值, KD狀態)
        """
        low_min = data['Low'].rolling(period).min()
        high_max = data['High'].rolling(period).max()
        rsv = (data['Close'] - low_min) / (high_max - low_min) * 100

        k = rsv.ewm(com=2).mean()
        d = k.ewm(com=2).mean()

        # KD狀態判斷
        kd_status = np.select(
            [
                (k > 80) & (d > 80),
                (k < 20) & (d < 20),
                (k > d) & (k < 50),
                (k < d) & (k > 50)
            ],
            ['超買區', '超賣區', '黃金交叉', '死亡交叉'],
            default='中性'
        )

        return k, d, kd_status

    @staticmethod
    def calculate_bollinger_bands(data, period=20, std_dev=2):
        """
        計算布林通道

        Args:
            data: DataFrame 包含 Close 價格
            period: 移動平均期數
            std_dev: 標準差倍數

        Returns:
            tuple: (中線, 上軌, 下軌)
        """
        ma = data['Close'].rolling(period).mean()
        std = data['Close'].rolling(period).std()
        upper = ma + std_dev * std
        lower = ma - std_dev * std
        return ma, upper, lower

    @staticmethod
    def calculate_atr(data, period=14):
        """
        計算 ATR (平均真實波幅)

        Args:
            data: DataFrame 包含 High, Low, Close 價格
            period: ATR 計算期數

        Returns:
            Series: ATR 值
        """
        tr = np.maximum(
            data['High'] - data['Low'],
            np.maximum(
                abs(data['High'] - data['Close'].shift(1)),
                abs(data['Low'] - data['Close'].shift(1))
            )
        )
        atr = tr.rolling(period).mean()
        return atr

    @staticmethod
    def calculate_bias(data, periods=[5, 20, 60]):
        """
        計算乖離率

        Args:
            data: DataFrame 包含 Close 價格
            periods: 計算期數列表

        Returns:
            dict: 各期數的乖離率
        """
        bias = {}
        for period in periods:
            ma = data['Close'].rolling(period).mean()
            bias[f'Bias_{period}'] = (data['Close'] - ma) / ma * 100
        return bias