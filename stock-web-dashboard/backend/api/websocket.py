"""
WebSocket API - 即時報價推播
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json

from services.cache import stock_cache

router = APIRouter()

class ConnectionManager:
    """WebSocket 連線管理"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """廣播訊息到所有連線"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

async def update_prices_periodically():
    """定時更新報價並推播"""
    while True:
        await asyncio.sleep(60)  # 每分鐘更新
        
        codes = stock_cache.get_portfolio_codes()
        if not codes:
            continue
        
        # 取得報價
        from api.quotes import get_itick_price, get_fallback_price
        
        prices = {}
        for code in codes:
            price_data = get_itick_price(code)
            if not price_data:
                price_data = get_fallback_price(code)
            
            if price_data:
                stock_cache.set_price(code, price_data)
                prices[code] = price_data
        
        if prices and manager.active_connections:
            await manager.broadcast({
                "type": "prices",
                "data": prices
            })

@router.websocket("/quotes")
async def websocket_quotes(websocket: WebSocket):
    """即時報價 WebSocket"""
    await manager.connect(websocket)
    
    try:
        # 初始發送持股報價
        codes = stock_cache.get_portfolio_codes()
        if codes:
            from api.quotes import get_itick_price, get_fallback_price
            
            prices = {}
            for code in codes:
                # 檢查快取
                cached = stock_cache.get_price(code)
                if cached:
                    prices[code] = cached
                else:
                    price_data = get_itick_price(code)
                    if not price_data:
                        price_data = get_fallback_price(code)
                    if price_data:
                        stock_cache.set_price(code, price_data)
                        prices[code] = price_data
            
            await websocket.send_json({
                "type": "prices",
                "data": prices
            })
        
        # 保持連線
        while True:
            # 客戶端可以發送訊息（如訂閱特定股票）
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30)
                # 處理訂閱請求
                if data.get("type") == "subscribe":
                    # TODO: 實現特定股票訂閱
                    pass
            except asyncio.TimeoutError:
                # 發送心跳
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# 啟動背景任務
import threading
def start_background_task():
    """啟動背景更新任務"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_prices_periodically())

# 注意：實際部署時需要使用 uvicorn 的 lifespan 或 BackgroundTasks