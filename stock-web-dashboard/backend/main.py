"""
台股智能分析系統 - FastAPI 後端
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from pathlib import Path

from api.portfolio import router as portfolio_router
from api.quotes import router as quotes_router
from api.websocket import router as ws_router
from services.cache import StockCache

# 初始化快取
stock_cache = StockCache()

app = FastAPI(title="台股智能分析系統 API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載路由
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["持股"])
app.include_router(quotes_router, prefix="/api/quotes", tags=["報價"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])

# 靜態文件（前端build後）
static_path = Path(__file__).parent.parent / "frontend" / "dist"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")

@app.on_event("startup")
def startup():
    """啟動時載入持股資料"""
    stock_cache.load_portfolio()

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": asyncio.get_event_loop().time()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)