"""
持股 API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
from pathlib import Path
import os

router = APIRouter()

# Default to workspace config, can be overridden via env
DEFAULT_CONFIG = Path('/home/node/.openclaw/workspace/stock_web_deploy/config.json')
CONFIG_PATH = Path(os.environ.get('CONFIG_PATH', str(DEFAULT_CONFIG)))

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"portfolio": {}, "watchlist": []}

def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- Models ---

class StockBase(BaseModel):
    code: str
    name: str
    cost: float
    shares: int
    stop_loss: Optional[float] = None
    stop_profit: Optional[float] = None

class StockCreate(StockBase):
    industry: Optional[str] = None
    application: Optional[str] = None
    buy_date: Optional[str] = None

class StockUpdate(BaseModel):
    name: Optional[str] = None
    cost: Optional[float] = None
    shares: Optional[int] = None
    stop_loss: Optional[float] = None
    stop_profit: Optional[float] = None

class WatchlistItem(BaseModel):
    code: str
    name: str
    industry: Optional[str] = None
    application: Optional[str] = None

# --- Routes ---

@router.get("/")
def get_portfolio():
    """取得所有持股"""
    config = load_config()
    return config.get("portfolio", {})

@router.get("/summary")
def get_portfolio_summary():
    """取得持股總覽"""
    config = load_config()
    portfolio = config.get("portfolio", {})
    
    total_cost = sum(s.get("cost", 0) * s.get("shares", 0) for s in portfolio.values())
    count = len(portfolio)
    
    return {
        "total_cost": total_cost,
        "count": count,
        "stocks": portfolio
    }

@router.post("/")
def add_stock(stock: StockCreate):
    """新增持股"""
    config = load_config()
    if "portfolio" not in config:
        config["portfolio"] = {}
    
    config["portfolio"][stock.code] = stock.model_dump()
    save_config(config)
    return {"success": True, "code": stock.code}

@router.put("/{code}")
def update_stock(code: str, stock: StockUpdate):
    """更新持股"""
    config = load_config()
    if code not in config.get("portfolio", {}):
        raise HTTPException(status_code=404, detail="持股不存在")
    
    current = config["portfolio"][code]
    update_data = stock.model_dump(exclude_unset=True)
    current.update(update_data)
    config["portfolio"][code] = current
    save_config(config)
    return {"success": True}

@router.delete("/{code}")
def delete_stock(code: str):
    """刪除持股"""
    config = load_config()
    if code in config.get("portfolio", {}):
        del config["portfolio"][code]
        save_config(config)
    return {"success": True}

# --- Watchlist ---

@router.get("/watchlist")
def get_watchlist():
    """取得觀察名單"""
    config = load_config()
    return config.get("watchlist", [])

@router.post("/watchlist")
def add_watchlist(item: WatchlistItem):
    """新增觀察名單"""
    config = load_config()
    if "watchlist" not in config:
        config["watchlist"] = []
    
    # 檢查是否已存在
    existing = [i for i in config["watchlist"] if i.get("code") == item.code]
    if existing:
        raise HTTPException(status_code=400, detail="股票已在觀察名單中")
    
    config["watchlist"].append(item.model_dump())
    save_config(config)
    return {"success": True}

@router.delete("/watchlist/{code}")
def delete_watchlist(code: str):
    """刪除觀察名單"""
    config = load_config()
    config["watchlist"] = [i for i in config.get("watchlist", []) if i.get("code") != code]
    save_config(config)
    return {"success": True}