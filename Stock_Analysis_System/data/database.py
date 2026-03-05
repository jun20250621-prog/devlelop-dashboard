# -*- coding: utf-8 -*-
"""
SQLite 資料庫管理模組
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class DatabaseManager:
    """SQLite 資料庫管理器"""
    
    def __init__(self, db_path: str = None):
        """初始化資料庫"""
        if db_path is None:
            # 預設路徑
            project_root = Path(__file__).parent.parent
            db_dir = project_root / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = db_dir / "stock_data.db"
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _get_connection(self):
        """取得資料庫連線"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """初始化資料庫表格"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 持股資料表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT,
                shares INTEGER,
                cost REAL,
                current_price REAL,
                stop_loss REAL,
                stop_profit REAL,
                industry TEXT,
                application TEXT,
                buy_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 觀察名單資料表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT,
                target_price REAL,
                reason TEXT,
                industry TEXT,
                add_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 交易紀錄資料表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT,
                action TEXT NOT NULL,
                shares INTEGER,
                price REAL,
                total_amount REAL,
                trade_date TEXT,
                strategy TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 策略資料表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                parameters TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 快取資料表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ==================== 持股管理 ====================
    
    def get_portfolio(self) -> List[Dict]:
        """取得所有持股"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM portfolio ORDER BY code")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_portfolio(self, code: str, name: str, shares: int, cost: float, **kwargs) -> bool:
        """新增持股"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO portfolio (code, name, shares, cost, industry, application, buy_date, stop_loss, stop_profit, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, name, shares, cost, 
                  kwargs.get('industry', ''),
                  kwargs.get('application', ''),
                  kwargs.get('buy_date', ''),
                  kwargs.get('stop_loss', 0),
                  kwargs.get('stop_profit', 0),
                  kwargs.get('notes', '')))
            conn.commit()
            return True
        except Exception as e:
            print(f"新增持股失敗: {e}")
            return False
        finally:
            conn.close()
    
    def update_portfolio_price(self, code: str, price: float) -> bool:
        """更新持股價格"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE portfolio SET current_price = ?, updated_at = ? WHERE code = ?",
                      (price, datetime.now().isoformat(), code))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def remove_portfolio(self, code: str) -> bool:
        """移除持股"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM portfolio WHERE code = ?", (code,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    # ==================== 觀察名單管理 ====================
    
    def get_watchlist(self) -> List[Dict]:
        """取得觀察名單"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM watchlist ORDER BY code")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_watchlist(self, code: str, name: str, target_price: float = None, **kwargs) -> bool:
        """新增觀察股票"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO watchlist (code, name, target_price, reason, industry, add_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (code, name, target_price,
                  kwargs.get('reason', ''),
                  kwargs.get('industry', ''),
                  kwargs.get('add_date', datetime.now().strftime('%Y-%m-%d'))))
            conn.commit()
            return True
        except Exception as e:
            print(f"新增觀察名單失敗: {e}")
            return False
        finally:
            conn.close()
    
    def remove_watchlist(self, code: str) -> bool:
        """移除觀察股票"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM watchlist WHERE code = ?", (code,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    # ==================== 交易紀錄管理 ====================
    
    def get_trades(self, filters: Dict = None) -> List[Dict]:
        """取得交易紀錄"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM trades"
        params = []
        
        if filters:
            conditions = []
            if filters.get('code'):
                conditions.append("code = ?")
                params.append(filters['code'])
            if filters.get('action'):
                conditions.append("action = ?")
                params.append(filters['action'])
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY trade_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_trade(self, code: str, action: str, shares: int, price: float, **kwargs) -> bool:
        """新增交易紀錄"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            total = shares * price
            cursor.execute("""
                INSERT INTO trades (code, name, action, shares, price, total_amount, trade_date, strategy, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, kwargs.get('name', ''), action, shares, price, total,
                  kwargs.get('trade_date', datetime.now().strftime('%Y-%m-%d')),
                  kwargs.get('strategy', ''),
                  kwargs.get('notes', '')))
            conn.commit()
            return True
        except Exception as e:
            print(f"新增交易紀錄失敗: {e}")
            return False
        finally:
            conn.close()
    
    # ==================== 快取管理 ====================
    
    def set_cache(self, key: str, value: Any, expires_hours: int = 24):
        """設定快取"""
        conn = self._get_connection()
        cursor = conn.cursor()
        expires = datetime.now().timestamp() + (expires_hours * 3600)
        cursor.execute("""
            INSERT OR REPLACE INTO cache (key, value, expires_at)
            VALUES (?, ?, ?)
        """, (key, json.dumps(value), datetime.fromtimestamp(expires).isoformat()))
        conn.commit()
        conn.close()
    
    def get_cache(self, key: str) -> Optional[Any]:
        """取得快取"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            expires_at = datetime.fromisoformat(row['expires_at'])
            if expires_at > datetime.now():
                return json.loads(row['value'])
        return None
    
    def clear_expired_cache(self):
        """清除過期快取"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE expires_at < ?", (datetime.now().isoformat(),))
        conn.commit()
        conn.close()


# 全域資料庫管理器
db = DatabaseManager()
