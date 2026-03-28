#!/usr/bin/env python3
"""
股票資料取得模組 - 優化版 (多備用源 + 增強穩定性)
Stock Data Fetcher - Enhanced with Multiple Backup Sources
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

logger = logging.getLogger(__name__)


class StockDataCache:
    """智慧型快取機制 - 優化版"""
    
    def __init__(self, cache_dir='stock_cache', cache_duration=7200):
        self.cache_dir = cache_dir
        self.cache_duration = cache_duration  # 預設2小時 (優化)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, symbol: str, period: str = '1mo') -> str:
        return f"{self.cache_dir}/{symbol}_{period}.json"
    
    def get_cached_data(self, symbol: str, period: str = '1mo') -> Optional[Dict]:
        """取得快取數據"""
        cache_file = self._get_cache_path(symbol, period)
        
        if os.path.exists(cache_file):
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                if datetime.now() - file_time < timedelta(seconds=self.cache_duration):
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        # 檢查資料完整性
                        if data and 'price' in data and data['price'] > 0:
                            logger.debug(f"從快取取得 {symbol}")
                            return data
            except Exception as e:
                logger.debug(f"讀取快取失敗: {e}")
        
        return None
    
    def save_cache(self, symbol: str, data: Dict, period: str = '1mo') -> None:
        """儲存快取"""
        if not data or data.get('price', 0) <= 0:
            return
            
        cache_file = self._get_cache_path(symbol, period)
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            logger.debug(f"快取 {symbol} 成功")
        except Exception as e:
            logger.debug(f"儲存快取失敗: {e}")


class StockDataFetcher:
    """股票資料取得器 - 多備用源 + 增強穩定性版"""
    
    def __init__(self, cache_timeout: int = 7200):
        self.cache = StockDataCache(cache_duration=cache_timeout)
        self.cache_timeout = cache_timeout
        self.request_count = 0
        self.last_request_time = 0
        self.max_retries = 5  # 優化：增加到 5 次
        self.executor = ThreadPoolExecutor(max_workers=3)
        
    def _rate_limit(self):
        """頻率限制：每分鐘最多 10 個請求"""
        current_time = time.time()
        
        # 每 6 秒一個請求
        if current_time - self.last_request_time < 0.6:
            time.sleep(0.6 - (current_time - self.last_request_time))
        
        self.last_request_time = current_time
        self.request_count += 1
        
        # 每分鐘重置計數
        if self.request_count >= 10:
            time.sleep(6)
            self.request_count = 0
    
    def _fetch_yahoo_tw(self, symbol: str) -> Optional[Dict]:
        """Yahoo Finance - 台灣上市"""
        try:
            stock = yf.Ticker(f"{symbol}.TW")
            info = stock.info
            
            if info and 'currentPrice' in info and info['currentPrice']:
                return {
                    'code': symbol,
                    'source': 'yahoo_tw',
                    'price': info.get('currentPrice', 0),
                    'change': info.get('regularMarketChange', 0),
                    'change_pct': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('volume', 0),
                    'high': info.get('regularMarketDayHigh', 0),
                    'low': info.get('regularMarketDayLow', 0),
                    'open': info.get('regularMarketOpen', 0),
                    'prev_close': info.get('regularMarketPreviousClose', 0),
                    'name': info.get('shortName', ''),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.debug(f"Yahoo TW {symbol} 失敗: {e}")
        return None
    
    def _fetch_yahoo_two(self, symbol: str) -> Optional[Dict]:
        """Yahoo Finance - 台灣上櫃"""
        try:
            stock = yf.Ticker(f"{symbol}.TWO")
            info = stock.info
            
            if info and 'currentPrice' in info and info['currentPrice']:
                return {
                    'code': symbol,
                    'source': 'yahoo_two',
                    'price': info.get('currentPrice', 0),
                    'change': info.get('regularMarketChange', 0),
                    'change_pct': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('volume', 0),
                    'high': info.get('regularMarketDayHigh', 0),
                    'low': info.get('regularMarketDayLow', 0),
                    'open': info.get('regularMarketOpen', 0),
                    'prev_close': info.get('regularMarketPreviousClose', 0),
                    'name': info.get('shortName', ''),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.debug(f"Yahoo TWO {symbol} 失敗: {e}")
        return None
    
    def _fetch_fugle(self, symbol: str, api_key: str = None) -> Optional[Dict]:
        """Fugle API - 備用來源"""
        if not api_key:
            return None
            
        try:
            url = f"https://api.fugle.tw/realtime/v0.2/intraday/quote?symbolId={symbol}"
            headers = {"Authorization": f"Bearer {api_key}"}
            resp = requests.get(url, headers=headers, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data'):
                    quote = data['data']['quote']
                    return {
                        'code': symbol,
                        'source': 'fugle',
                        'price': quote.get('lastPrice', 0),
                        'change': quote.get('change', 0),
                        'change_pct': quote.get('changePercent', 0),
                        'volume': quote.get('totalVolume', 0),
                        'high': quote.get('highPrice', 0),
                        'low': quote.get('lowPrice', 0),
                        'open': quote.get('openPrice', 0),
                        'prev_close': quote.get('previousClose', 0),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            logger.debug(f"Fugle {symbol} 失敗: {e}")
        return None
    
    def _fetch_with_retry(self, symbol: str, max_retries: int = 5) -> Optional[Dict]:
        """多備用源取價機制"""
        
        # 1. 檢查快取
        cached = self.cache.get_cached_data(symbol, '1mo')
        if cached:
            return cached
        
        # 2. 嘗試多個來源
        sources = [
            ('yahoo_tw', lambda: self._fetch_yahoo_tw(symbol)),
            ('yahoo_two', lambda: self._fetch_yahoo_two(symbol)),
        ]
        
        for source_name, fetch_func in sources:
            for attempt in range(max_retries):
                try:
                    self._rate_limit()
                    result = fetch_func()
                    
                    if result and result.get('price', 0) > 0:
                        # 儲存快取
                        self.cache.save_cache(symbol, result, '1mo')
                        logger.info(f"從 {result.get('source')} 取得 {symbol}: {result.get('price')}")
                        return result
                        
                except Exception as e:
                    error_msg = str(e)
                    if '429' in error_msg or 'Too Many Requests' in error_msg:
                        wait_time = (attempt + 1) * 5
                        logger.warning(f"{source_name} {symbol} 被限流，等待 {wait_time}秒")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.debug(f"{source_name} {symbol} 嘗試 {attempt+1} 失敗: {e}")
                        
                # 失敗後稍等再試
                time.sleep(1)
        
        return None
    
    def get_price(self, stock_code: str) -> Optional[Dict]:
        """取得即時股價"""
        return self._fetch_with_retry(stock_code, self.max_retries)
    
    def get_prices_batch(self, stock_codes: List[str]) -> Dict[str, Optional[Dict]]:
        """批次取得多檔股票股價"""
        results = {}
        
        for code in stock_codes:
            results[code] = self.get_price(code)
            
        return results
    
    def get_historical(self, stock_code: str, days: int = 90) -> Optional[Dict]:
        """取得歷史資料"""
        cache_key = f"hist_{stock_code}_{days}"
        cached = self.cache.get_cached_data(cache_key, f'{days}d')
        
        if cached:
            return cached
        
        try:
            self._rate_limit()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 嘗試上市
            stock = yf.Ticker(f"{stock_code}.TW")
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                # 嘗試上櫃
                stock = yf.Ticker(f"{stock_code}.TWO")
                hist = stock.history(start=start_date, end=end_date)
            
            if not hist.empty:
                data = {
                    'code': stock_code,
                    'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                    'open': hist['Open'].tolist(),
                    'high': hist['High'].tolist(),
                    'low': hist['Low'].tolist(),
                    'close': hist['Close'].tolist(),
                    'volume': hist['Volume'].tolist(),
                    'timestamp': datetime.now().isoformat()
                }
                self.cache.save_cache(cache_key, data, f'{days}d')
                return data
                
        except Exception as e:
            logger.error(f"取得歷史資料 {stock_code} 失敗: {e}")
            
        return None
    
    def get_indicators(self, stock_code: str, days: int = 60) -> Optional[Dict]:
        """取得技術指標"""
        hist_data = self.get_historical(stock_code, days)
        
        if not hist_data or not hist_data.get('close'):
            return None
            
        closes = hist_data['close']
        
        # MA
        ma5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else None
        ma10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else None
        ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
        ma60 = sum(closes[-60:]) / 60 if len(closes) >= 60 else None
        
        # RSI (14日)
        gains = []
        losses = []
        for i in range(1, min(15, len(closes))):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        
        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        return {
            'code': stock_code,
            'price': closes[-1] if closes else None,
            'ma5': round(ma5, 2) if ma5 else None,
            'ma10': round(ma10, 2) if ma10 else None,
            'ma20': round(ma20, 2) if ma20 else None,
            'ma60': round(ma60, 2) if ma60 else None,
            'rsi': round(rsi, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def __del__(self):
        """清理資源"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# ==================== 獨立測試 ====================
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    fetcher = StockDataFetcher(cache_timeout=3600)
    
    test_codes = ["2317", "2330", "0050"]
    
    print("=== 測試股票取價 ===")
    for code in test_codes:
        result = fetcher.get_price(code)
        if result:
            print(f"{code}: ${result.get('price')} ({result.get('change_pct')}%) - 來源: {result.get('source')}")
        else:
            print(f"{code}: 取價失敗")
    
    print("\n=== 測試技術指標 ===")
    for code in test_codes:
        indicators = fetcher.get_indicators(code)
        if indicators:
            print(f"{code} - MA5: {indicators.get('ma5')}, MA20: {indicators.get('ma20')}, RSI: {indicators.get('rsi')}")