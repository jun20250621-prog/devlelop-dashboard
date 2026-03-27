"""
報價 API
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone, timedelta

from services.cache import stock_cache

router = APIRouter()

# iTick API 設定
ITICK_API_KEY = "ae7824e15cc34160bfe303310973ea9a77ee3c6b1c314202b2ff1bd23db02729"
ITICK_BASE_URL = "https://api.itick.org"

def get_itick_price(stock_id: str) -> Optional[Dict]:
    """使用 iTick API 取得股票報價"""
    if stock_id.startswith('00') or stock_id.endswith('B'):
        return None  # 不支援 ETF
    
    try:
        url = f"{ITICK_BASE_URL}/stock/quote"
        params = urllib.parse.urlencode({"region": "TW", "code": stock_id})
        headers = {'accept': 'application/json', 'token': ITICK_API_KEY}
        
        req = urllib.request.Request(f"{url}?{params}", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('code') == 0 and data.get('data'):
                d = data['data']
                return {
                    'price': d.get('p', 0),
                    'change': d.get('ch', 0),
                    'change_pct': d.get('chp', 0),
                    'volume': d.get('v', 0),
                    'high': d.get('h', 0),
                    'low': d.get('l', 0),
                    'open': d.get('o', 0),
                    'prev_close': d.get('pc', 0),
                    'timestamp': d.get('t', 0)
                }
    except Exception as e:
        print(f"iTick Error {stock_id}: {e}")
    
    return None

def get_fallback_price(stock_id: str) -> Optional[Dict]:
    """Fallback 到 FinMind API"""
    try:
        taiwan_tz = timezone(timedelta(hours=8))
        today = datetime.now(taiwan_tz).date()
        start_date = (today - timedelta(days=60)).strftime('%Y-%m-%d')
        
        url = f"https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockPrice&data_id={stock_id}&start_date={start_date}&end_date={today.strftime('%Y-%m-%d')}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if not data.get('data') or len(data['data']) == 0:
            return None
        
        items = data['data']
        latest = items[-1]
        prev = items[-2] if len(items) >= 2 else latest
        
        price = float(latest.get('close', 0))
        prev_price = float(prev.get('close', 0))
        change = price - prev_price
        change_pct = (change / prev_price * 100) if prev_price else 0
        
        return {
            'price': price,
            'change': change,
            'change_pct': change_pct,
            'volume': latest.get('turnover_volume', 0),
            'high': latest.get('max', 0),
            'low': latest.get('min', 0),
            'open': latest.get('open', 0),
            'prev_close': prev_price,
            'timestamp': 0
        }
    except Exception as e:
        print(f"FinMind Error {stock_id}: {e}")
        return None

@router.get("/price/{code}")
async def get_price(code: str):
    """取得單一股票報價"""
    # 檢查快取
    cached = stock_cache.get_price(code)
    if cached:
        return cached
    
    # 取得新報價
    price_data = get_itick_price(code)
    if not price_data:
        price_data = get_fallback_price(code)
    
    if price_data:
        stock_cache.set_price(code, price_data)
        return price_data
    
    raise HTTPException(status_code=404, detail="無法取得報價")

@router.get("/prices")
async def get_prices(codes: str):
    """批量取得股票報價（逗號分隔）"""
    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    results = {}
    
    for code in code_list:
        # 檢查快取
        cached = stock_cache.get_price(code)
        if cached:
            results[code] = cached
            continue
        
        # 取得新報價
        price_data = get_itick_price(code)
        if not price_data:
            price_data = get_fallback_price(code)
        
        if price_data:
            stock_cache.set_price(code, price_data)
            results[code] = price_data
        else:
            results[code] = {"error": "無法取得報價"}
    
    return results

@router.get("/history/{code}")
async def get_history(code: str, days: int = 60):
    """取得股票歷史資料（K線數據）"""
    try:
        taiwan_tz = timezone(timedelta(hours=8))
        today = datetime.now(taiwan_tz).date()
        start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
        
        url = f"https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockPrice&data_id={code}&start_date={start_date}&end_date={today.strftime('%Y-%m-%d')}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if not data.get('data'):
            return []
        
        # 轉換為 TradingView 格式
        candles = []
        for item in data['data']:
            candles.append({
                'time': item.get('date', ''),
                'open': float(item.get('open', 0)),
                'high': float(item.get('max', 0)),
                'low': float(item.get('min', 0)),
                'close': float(item.get('close', 0)),
                'volume': int(item.get('turnover_volume', 0))
            })
        
        return candles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))