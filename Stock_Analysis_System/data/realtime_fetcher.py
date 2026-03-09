# -*- coding: utf-8 -*-
"""
即時股票數據獲取模組
Real-time Stock Data Fetcher Module

整合多個數據源，優先使用最快的即時數據
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any, Tuple
import json
import time
from pathlib import Path
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# 載入環境變數
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)


class RealtimeDataFetcher:
    """即時數據獲取器 - 整合多個數據源"""
    
    def __init__(self):
        """初始化即時數據獲取器"""
        self.fugle_api_key = os.getenv('FUGLE_API_KEY', '')
        self.finmind_token = os.getenv('FINMIND_API_TOKEN', '')
        
        # 數據源優先順序
        priority_str = os.getenv('DATA_SOURCE_PRIORITY', 'fugle,twse,finmind,yahoo')
        self.priority = [s.strip() for s in priority_str.split(',')]
        
        # 簡單的記憶體快取
        self.cache = {}
        self.cache_expire = int(os.getenv('REALTIME_CACHE_EXPIRE_SECONDS', '30'))
        
        logger.info(f"即時數據獲取器初始化完成，數據源優先順序: {self.priority}")
    
    def get_realtime_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        獲取股票即時報價
        
        Args:
            stock_code: 股票代碼 (例如: 2330)
            
        Returns:
            包含即時報價的字典，失敗返回 None
        """
        # 檢查快取
        cache_key = f"quote_{stock_code}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_expire:
                logger.debug(f"使用快取的 {stock_code} 即時報價")
                return cached_data
        
        # 依優先順序嘗試各數據源
        for source in self.priority:
            try:
                if source == 'fugle' and self.fugle_api_key:
                    data = self._fetch_fugle_quote(stock_code)
                elif source == 'twse':
                    data = self._fetch_twse_quote(stock_code)
                elif source == 'finmind':
                    data = self._fetch_finmind_quote(stock_code)
                elif source == 'yahoo':
                    data = self._fetch_yahoo_quote(stock_code)
                else:
                    continue
                
                if data:
                    # 添加數據源標記
                    data['data_source'] = source
                    data['fetch_time'] = datetime.now()
                    
                    # 存入快取
                    self.cache[cache_key] = (data, datetime.now())
                    
                    logger.info(f"成功從 {source} 獲取 {stock_code} 即時報價")
                    return data
                    
            except Exception as e:
                logger.warning(f"從 {source} 獲取 {stock_code} 報價失敗: {e}")
                continue
        
        logger.error(f"所有數據源都無法獲取 {stock_code} 的即時報價")
        return None
    
    def _fetch_fugle_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        從 Fugle API 獲取即時報價
        
        官方文檔: https://developer.fugle.tw/
        """
        try:
            # Fugle API endpoint - 使用新版 API
            url = f"https://api.fugle.tw/marketdata/v1.0/stock/intraday/quote/{stock_code}"
            
            headers = {
                'X-API-KEY': self.fugle_api_key,
                'Content-Type': 'application/json'
            }
            
            params = None
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 解析 Fugle 數據格式 (新版 API v1.0)
                if 'data' in data:
                    result = data['data']
                    
                    # 獲取價格資訊
                    price_info = result.get('quote', {})
                    trade = price_info.get('trade', {})
                    price_high_low = price_info.get('priceHigh', {})
                    
                    # 獲取昨收價用於計算漲跌
                    reference = result.get('info', {}).get('previousClose', 0)
                    if not reference:
                        reference = result.get('quote', {}).get('reference', 0)
                    
                    current_price = trade.get('price', 0) if trade else price_info.get('lastPrice', 0)
                    change = current_price - reference if reference > 0 else 0
                    change_pct = (change / reference * 100) if reference > 0 else 0
                    
                    return {
                        'code': stock_code,
                        'name': result.get('info', {}).get('name', stock_code),
                        'price': current_price,
                        'open': price_info.get('priceOpen', 0),
                        'high': price_info.get('priceHigh', {}).get('price', 0) if isinstance(price_info.get('priceHigh'), dict) else price_info.get('priceHigh', 0),
                        'low': price_info.get('priceLow', {}).get('price', 0) if isinstance(price_info.get('priceLow'), dict) else price_info.get('priceLow', 0),
                        'volume': price_info.get('total', {}).get('volume', 0) if isinstance(price_info.get('total'), dict) else price_info.get('volume', 0),
                        'change': change,
                        'change_pct': change_pct,
                        'time': trade.get('at', datetime.now().isoformat()) if trade else datetime.now().isoformat(),
                        'bid': price_info.get('order', {}).get('bestBids', [{}])[0].get('price', 0) if price_info.get('order', {}).get('bestBids') else 0,
                        'ask': price_info.get('order', {}).get('bestAsks', [{}])[0].get('price', 0) if price_info.get('order', {}).get('bestAsks') else 0,
                    }
            elif response.status_code == 401:
                logger.error("Fugle API 認證失敗，請檢查 API Key")
            elif response.status_code == 429:
                logger.warning("Fugle API 請求過於頻繁，達到限制")
            else:
                logger.warning(f"Fugle API 返回錯誤: {response.status_code}")
            
            return None
            
        except Exception as e:
            logger.error(f"Fugle API 請求異常: {e}")
            return None
    
    def _fetch_twse_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        從台灣證券交易所 API 獲取即時報價
        
        官方網站: https://mis.twse.com.tw/
        """
        try:
            # TWSE API endpoint
            url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
            
            params = {
                'ex_ch': f'tse_{stock_code}.tw',  # 上市股票
                'json': '1',
                'delay': '0'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'msgArray' in data and len(data['msgArray']) > 0:
                    stock_data = data['msgArray'][0]
                    
                    # 解析價格（可能是字串或數字）
                    def parse_price(value):
                        try:
                            if value == '-' or value == '':
                                return 0
                            return float(value)
                        except:
                            return 0
                    
                    price = parse_price(stock_data.get('z', 0))  # 成交價
                    open_price = parse_price(stock_data.get('o', 0))  # 開盤價
                    high = parse_price(stock_data.get('h', 0))  # 最高價
                    low = parse_price(stock_data.get('l', 0))  # 最低價
                    yesterday = parse_price(stock_data.get('y', 0))  # 昨收價
                    
                    change = price - yesterday if yesterday > 0 else 0
                    change_pct = (change / yesterday * 100) if yesterday > 0 else 0
                    
                    return {
                        'code': stock_code,
                        'name': stock_data.get('n', stock_code),
                        'price': price,
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'volume': parse_price(stock_data.get('v', 0)),
                        'change': change,
                        'change_pct': change_pct,
                        'time': stock_data.get('t', datetime.now().strftime('%H:%M:%S')),
                        'bid': parse_price(stock_data.get('b', '').split('_')[0] if stock_data.get('b') else 0),
                        'ask': parse_price(stock_data.get('a', '').split('_')[0] if stock_data.get('a') else 0),
                        'yesterday': yesterday
                    }
            
            # 嘗試上櫃股票
            params['ex_ch'] = f'otc_{stock_code}.tw'
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'msgArray' in data and len(data['msgArray']) > 0:
                    stock_data = data['msgArray'][0]
                    
                    def parse_price(value):
                        try:
                            if value == '-' or value == '':
                                return 0
                            return float(value)
                        except:
                            return 0
                    
                    price = parse_price(stock_data.get('z', 0))
                    open_price = parse_price(stock_data.get('o', 0))
                    high = parse_price(stock_data.get('h', 0))
                    low = parse_price(stock_data.get('l', 0))
                    yesterday = parse_price(stock_data.get('y', 0))
                    
                    change = price - yesterday if yesterday > 0 else 0
                    change_pct = (change / yesterday * 100) if yesterday > 0 else 0
                    
                    return {
                        'code': stock_code,
                        'name': stock_data.get('n', stock_code),
                        'price': price,
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'volume': parse_price(stock_data.get('v', 0)),
                        'change': change,
                        'change_pct': change_pct,
                        'time': stock_data.get('t', datetime.now().strftime('%H:%M:%S')),
                        'bid': parse_price(stock_data.get('b', '').split('_')[0] if stock_data.get('b') else 0),
                        'ask': parse_price(stock_data.get('a', '').split('_')[0] if stock_data.get('a') else 0),
                        'yesterday': yesterday
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"TWSE API 請求異常: {e}")
            return None
    
    def _fetch_finmind_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        從 FinMind API 獲取報價
        
        官方文檔: https://finmindtrade.com/
        """
        try:
            # FinMind API endpoint
            url = "https://api.finmindtrade.com/api/v4/data"
            
            # 獲取今天日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            params = {
                'dataset': 'TaiwanStockPrice',
                'data_id': stock_code,
                'start_date': today,
                'end_date': today
            }
            
            if self.finmind_token:
                params['token'] = self.finmind_token
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    stock_data = data['data'][-1]  # 最新一筆
                    
                    price = float(stock_data.get('close', 0))
                    open_price = float(stock_data.get('open', 0))
                    high = float(stock_data.get('max', 0))
                    low = float(stock_data.get('min', 0))
                    
                    # FinMind 沒有昨收價，用開盤價估算
                    change = price - open_price
                    change_pct = (change / open_price * 100) if open_price > 0 else 0
                    
                    return {
                        'code': stock_code,
                        'name': stock_code,  # FinMind 不提供名稱
                        'price': price,
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'volume': float(stock_data.get('Trading_Volume', 0)),
                        'change': change,
                        'change_pct': change_pct,
                        'time': stock_data.get('date', today),
                        'bid': 0,  # FinMind 不提供買賣價
                        'ask': 0
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"FinMind API 請求異常: {e}")
            return None
    
    def _fetch_yahoo_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        從 Yahoo Finance 獲取即時報價（備用）
        """
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(f"{stock_code}.TW")
            info = ticker.info
            
            if not info or 'regularMarketPrice' not in info:
                return None
            
            price = info.get('regularMarketPrice', 0)
            open_price = info.get('regularMarketOpen', 0)
            high = info.get('dayHigh', 0)
            low = info.get('dayLow', 0)
            prev_close = info.get('previousClose', 0)
            
            change = price - prev_close if prev_close > 0 else 0
            change_pct = (change / prev_close * 100) if prev_close > 0 else 0
            
            return {
                'code': stock_code,
                'name': info.get('longName', stock_code),
                'price': price,
                'open': open_price,
                'high': high,
                'low': low,
                'volume': info.get('volume', 0),
                'change': change,
                'change_pct': change_pct,
                'time': datetime.now().isoformat(),
                'bid': info.get('bid', 0),
                'ask': info.get('ask', 0),
                'yesterday': prev_close
            }
            
        except Exception as e:
            logger.error(f"Yahoo Finance 請求異常: {e}")
            return None
    
    def get_market_index_realtime(self) -> Dict[str, Any]:
        """
        獲取市場指數即時數據
        
        Returns:
            包含市場指數的字典
        """
        try:
            market_data = {}
            
            # 嘗試從 TWSE 獲取加權指數
            try:
                url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
                params = {
                    'ex_ch': 'tse_t00.tw',  # 加權指數代碼
                    'json': '1',
                    'delay': '0'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'msgArray' in data and len(data['msgArray']) > 0:
                        index_data = data['msgArray'][0]
                        
                        def parse_price(value):
                            try:
                                if value == '-' or value == '':
                                    return 0
                                return float(value)
                            except:
                                return 0
                        
                        price = parse_price(index_data.get('z', 0))
                        yesterday = parse_price(index_data.get('y', 0))
                        change = price - yesterday if yesterday > 0 else 0
                        change_pct = (change / yesterday * 100) if yesterday > 0 else 0
                        
                        market_data['加權指數'] = {
                            'price': price,
                            'change': change,
                            'change_pct': change_pct,
                            'time': index_data.get('t', datetime.now().strftime('%H:%M:%S')),
                            'data_source': 'twse'
                        }
            except Exception as e:
                logger.warning(f"獲取 TWSE 指數失敗: {e}")
            
            # 如果 TWSE 失敗，使用 Yahoo Finance
            if '加權指數' not in market_data:
                try:
                    import yfinance as yf
                    taiex = yf.Ticker("^TWII")
                    taiex_data = taiex.history(period="1d")
                    
                    if not taiex_data.empty:
                        market_data['加權指數'] = {
                            'price': taiex_data['Close'].iloc[-1],
                            'change': taiex_data['Close'].iloc[-1] - taiex_data['Open'].iloc[-1],
                            'change_pct': ((taiex_data['Close'].iloc[-1] - taiex_data['Open'].iloc[-1]) / taiex_data['Open'].iloc[-1] * 100),
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'data_source': 'yahoo'
                        }
                except Exception as e:
                    logger.warning(f"獲取 Yahoo 指數失敗: {e}")
            
            return market_data
            
        except Exception as e:
            logger.error(f"獲取市場指數失敗: {e}")
            return {}
    
    def get_batch_quotes(self, stock_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        批量獲取多檔股票即時報價
        
        Args:
            stock_codes: 股票代碼列表
            
        Returns:
            股票代碼到報價數據的字典
        """
        results = {}
        
        for code in stock_codes:
            quote = self.get_realtime_quote(code)
            if quote:
                results[code] = quote
            else:
                logger.warning(f"無法獲取 {code} 的即時報價")
        
        return results
    
    def clear_cache(self):
        """清除快取"""
        self.cache.clear()
        logger.info("已清除即時數據快取")
    
    def get_data_source_status(self) -> Dict[str, bool]:
        """
        檢查各數據源的可用性
        
        Returns:
            數據源名稱到可用性的字典
        """
        status = {}
        
        # 測試 Fugle
        if self.fugle_api_key:
            try:
                result = self._fetch_fugle_quote('2330')
                status['fugle'] = result is not None
            except:
                status['fugle'] = False
        else:
            status['fugle'] = False
        
        # 測試 TWSE
        try:
            result = self._fetch_twse_quote('2330')
            status['twse'] = result is not None
        except:
            status['twse'] = False
        
        # 測試 FinMind
        try:
            result = self._fetch_finmind_quote('2330')
            status['finmind'] = result is not None
        except:
            status['finmind'] = False
        
        # 測試 Yahoo
        try:
            result = self._fetch_yahoo_quote('2330')
            status['yahoo'] = result is not None
        except:
            status['yahoo'] = False
        
        return status


# 創建全局實例
_realtime_fetcher_instance = None

def get_realtime_fetcher() -> RealtimeDataFetcher:
    """獲取即時數據獲取器的單例實例"""
    global _realtime_fetcher_instance
    if _realtime_fetcher_instance is None:
        _realtime_fetcher_instance = RealtimeDataFetcher()
    return _realtime_fetcher_instance
