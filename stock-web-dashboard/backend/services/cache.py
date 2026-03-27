"""
報價快取服務
"""

import time
import os
from typing import Dict, Optional
from pathlib import Path

class StockCache:
    """簡單的記憶體快取"""
    
    def __init__(self, ttl_seconds: int = 60):
        self._cache: Dict[str, dict] = {}
        self._timestamps: Dict[str, float] = {}
        self._portfolio = {}
        self._ttl = ttl_seconds
    
    def load_portfolio(self):
        """載入持股資料"""
        import json
        default_path = Path('/home/node/.openclaw/workspace/stock_web_deploy/config.json')
        config_path = Path(os.environ.get('CONFIG_PATH', str(default_path)))
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self._portfolio = config.get("portfolio", {})
    
    def get_portfolio_codes(self):
        """取得持股代碼列表"""
        return list(self._portfolio.keys())
    
    def get_price(self, code: str) -> Optional[dict]:
        """取得快取的報價"""
        if code in self._cache:
            # 檢查是否過期
            if time.time() - self._timestamps.get(code, 0) < self._ttl:
                return self._cache[code]
        return None
    
    def set_price(self, code: str, data: dict):
        """設定報價快取"""
        self._cache[code] = data
        self._timestamps[code] = time.time()
    
    def clear_expired(self):
        """清除過期快取"""
        now = time.time()
        expired = [k for k, t in self._timestamps.items() if now - t > self._ttl]
        for k in expired:
            self._cache.pop(k, None)
            self._timestamps.pop(k, None)

# 全域實例
stock_cache = StockCache(ttl_seconds=60)