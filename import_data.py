# -*- coding: utf-8 -*-
"""
從 stock_monitor_v7.py 導入數據到 SQLite
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.database import DatabaseManager

# 持股資料（從 stock_monitor_v7.py）
PORTFOLIO = {
    "2331": {"cost": 27.4, "name": "精英", "stop_loss": 24, "stop_profit": 35},
    "5392": {"cost": 52.6, "name": "能率", "stop_loss": 47, "stop_profit": 65},
    "3287": {"cost": 29.90, "name": "廣寰科", "stop_loss": 25.5, "stop_profit": 39},
    "2317": {"cost": 224.0, "name": "鴻海"},
    "00687B": {"cost": 29.35, "name": "國泰20年美債"},
    "1773": {"cost": 147.0, "name": "勝一"},
}

# 觀察名單
WATCH_LIST = [
    ("2543", "皇昌", "營建", "低檔黃金交叉"),
    ("3380", "明泰", "電子", "低檔黃金交叉"),
    ("2049", "上銀", "機械", "中檔黃金交叉"),
    ("6425", "易發", "電子", "低檔中性"),
    ("2485", "兆赫", "電子", "高檔黃金交叉"),
    ("6443", "元晶", "電子", "高檔中性"),
]

# 強勢股
MARKET_LEADERS = [
    ("2330", "台積電", "半導體", "AI/高效能運算"),
    ("2454", "聯發科", "IC設計", "AI/手機晶片"),
    ("2317", "鴻海", "電子", "AI伺服器/蘋果供應鏈"),
    ("2382", "廣達", "電子", "AI伺服器"),
    ("3711", "日月光", "半導體", "AI先進封裝"),
    ("3231", "緯創", "電子", "AI伺服器"),
    ("3034", "聯詠", "IC設計", "AI/顯示驅動"),
    ("4952", "凌通", "IC設計", "AI/周邊晶片"),
]

def main():
    db = DatabaseManager()
    
    # 匯入持股
    print("📥 匯入持股資料...")
    for code, stock in PORTFOLIO.items():
        db.add_portfolio(
            code=code,
            name=stock['name'],
            shares=1000,  # 預設股數
            cost=stock['cost'],
            stop_loss=stock.get('stop_loss', 0),
            stop_profit=stock.get('stop_profit', 0),
            industry=stock.get('industry', ''),
            buy_date='2026-01-01'
        )
        print(f"  ✅ {code} {stock['name']}")
    
    # 匯入觀察名單
    print("\n📥 匯入觀察名單...")
    for item in WATCH_LIST:
        db.add_watchlist(
            code=item[0],
            name=item[1],
            industry=item[2],
            reason=item[3]
        )
        print(f"  ✅ {item[0]} {item[1]}")
    
    # 匯入強勢股到觀察名單
    print("\n📥 匯入強勢股到觀察名單...")
    for item in MARKET_LEADERS:
        db.add_watchlist(
            code=item[0],
            name=item[1],
            industry=item[2],
            reason=item[3]
        )
        print(f"  ✅ {item[0]} {item[1]}")
    
    print("\n✅ 匯入完成！")
    
    # 顯示結果
    print("\n📋 持股列表:")
    for p in db.get_portfolio():
        print(f"  {p['code']} {p['name']} - ${p['cost']}")
    
    print("\n📋 觀察名單:")
    for w in db.get_watchlist():
        print(f"  {w['code']} {w['name']}")

if __name__ == '__main__':
    main()
