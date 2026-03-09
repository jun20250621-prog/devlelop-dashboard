# -*- coding: utf-8 -*-
"""
即時數據源測試程式
Real-time Data Source Test

測試所有即時數據源的可用性和性能
"""

import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import time
from datetime import datetime
from data.realtime_fetcher import get_realtime_fetcher
from data.fetcher import StockDataFetcher

def print_separator(char='=', length=80):
    """列印分隔線"""
    print(char * length)

def test_realtime_fetcher():
    """測試即時數據獲取器"""
    print_separator()
    print("📊 即時數據源測試程式")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # 初始化即時數據獲取器
    print("\n🔧 初始化即時數據獲取器...")
    fetcher = get_realtime_fetcher()
    print("✅ 初始化完成")
    
    # 測試數據源狀態
    print("\n📡 檢查數據源可用性...")
    print_separator('-')
    status = fetcher.get_data_source_status()
    
    sources = {
        'fugle': 'Fugle API (富果)',
        'twse': '台灣證交所 API',
        'finmind': 'FinMind API',
        'yahoo': 'Yahoo Finance'
    }
    
    available_count = 0
    for source_key, source_name in sources.items():
        is_available = status.get(source_key, False)
        status_icon = '✅' if is_available else '❌'
        print(f"{status_icon} {source_name}: {'可用' if is_available else '不可用'}")
        if is_available:
            available_count += 1
    
    print(f"\n可用數據源: {available_count}/{len(sources)}")
    
    if available_count == 0:
        print("\n⚠️ 警告：沒有可用的數據源！")
        return False
    
    # 測試即時報價
    print("\n" + "=" * 80)
    print("📈 測試即時報價功能")
    print_separator('-')
    
    test_stocks = ['2330', '2454', '2317']  # 台積電、聯發科、鴻海
    
    for stock_code in test_stocks:
        print(f"\n測試股票: {stock_code}")
        start_time = time.time()
        
        quote = fetcher.get_realtime_quote(stock_code)
        
        elapsed = (time.time() - start_time) * 1000  # 轉換為毫秒
        
        if quote:
            print(f"✅ 成功獲取報價 (耗時: {elapsed:.0f}ms)")
            print(f"   代碼: {quote['code']}")
            print(f"   名稱: {quote['name']}")
            print(f"   價格: ${quote['price']:.2f}")
            print(f"   漲跌: {quote['change']:+.2f} ({quote['change_pct']:+.2f}%)")
            print(f"   開盤: ${quote['open']:.2f}")
            print(f"   最高: ${quote['high']:.2f}")
            print(f"   最低: ${quote['low']:.2f}")
            print(f"   成交量: {quote['volume']:,.0f}")
            print(f"   數據時間: {quote.get('time', 'N/A')}")
            print(f"   數據源: {quote.get('data_source', 'unknown')}")
        else:
            print(f"❌ 獲取報價失敗 (耗時: {elapsed:.0f}ms)")
    
    # 測試市場指數
    print("\n" + "=" * 80)
    print("📊 測試市場指數功能")
    print_separator('-')
    
    start_time = time.time()
    market_data = fetcher.get_market_index_realtime()
    elapsed = (time.time() - start_time) * 1000
    
    if market_data and '加權指數' in market_data:
        index_data = market_data['加權指數']
        print(f"✅ 成功獲取市場指數 (耗時: {elapsed:.0f}ms)")
        print(f"   指數值: {index_data['price']:.2f}")
        print(f"   漲跌: {index_data['change']:+.2f} ({index_data['change_pct']:+.2f}%)")
        print(f"   數據時間: {index_data.get('time', 'N/A')}")
        print(f"   數據源: {index_data.get('data_source', 'unknown')}")
    else:
        print(f"❌ 獲取市場指數失敗 (耗時: {elapsed:.0f}ms)")
    
    # 測試批量查詢
    print("\n" + "=" * 80)
    print("🔢 測試批量查詢功能")
    print_separator('-')
    
    batch_stocks = ['2330', '2454', '2317', '2382', '3711']
    print(f"批量查詢股票: {', '.join(batch_stocks)}")
    
    start_time = time.time()
    batch_quotes = fetcher.get_batch_quotes(batch_stocks)
    elapsed = (time.time() - start_time) * 1000
    
    print(f"\n✅ 批量查詢完成 (耗時: {elapsed:.0f}ms)")
    print(f"   成功: {len(batch_quotes)}/{len(batch_stocks)} 檔")
    print(f"   平均每檔: {elapsed/len(batch_stocks):.0f}ms")
    
    for code, quote in batch_quotes.items():
        print(f"   {code}: ${quote['price']:.2f} ({quote['change_pct']:+.2f}%)")
    
    print("\n" + "=" * 80)
    print("✅ 即時數據源測試完成！")
    print_separator()
    
    return True

def test_stock_data_fetcher():
    """測試 StockDataFetcher 的即時功能整合"""
    print("\n" + "=" * 80)
    print("🔧 測試 StockDataFetcher 整合")
    print_separator('-')
    
    # 使用即時數據
    print("\n1️⃣ 測試啟用即時數據...")
    fetcher_rt = StockDataFetcher(use_realtime=True)
    status = fetcher_rt.get_data_source_status()
    print(f"   即時數據啟用: {status['realtime_enabled']}")
    
    if status['realtime_enabled']:
        # 測試獲取即時報價
        quote = fetcher_rt.get_realtime_quote('2330')
        if quote:
            print(f"   ✅ 2330 即時報價: ${quote['price']:.2f} (來源: {quote.get('data_source', 'unknown')})")
        else:
            print(f"   ❌ 無法獲取即時報價")
        
        # 測試市場指數
        market = fetcher_rt.get_market_index()
        if market and '加權指數' in market:
            index = market['加權指數']
            print(f"   ✅ 加權指數: {index['price']:.2f} (來源: {index.get('data_source', 'unknown')})")
        else:
            print(f"   ❌ 無法獲取市場指數")
    
    # 不使用即時數據
    print("\n2️⃣ 測試停用即時數據 (傳統模式)...")
    fetcher_legacy = StockDataFetcher(use_realtime=False)
    status_legacy = fetcher_legacy.get_data_source_status()
    print(f"   即時數據啟用: {status_legacy['realtime_enabled']}")
    
    quote_legacy = fetcher_legacy.get_realtime_quote('2330')
    if quote_legacy:
        print(f"   ✅ 2330 報價: ${quote_legacy['price']:.2f} (來源: {quote_legacy.get('data_source', 'unknown')})")
    
    print("\n✅ StockDataFetcher 整合測試完成！")

def main():
    """主函式"""
    try:
        # 測試即時數據獲取器
        success = test_realtime_fetcher()
        
        if success:
            # 測試整合
            test_stock_data_fetcher()
        
        print("\n🎉 所有測試完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 測試中斷")
    except Exception as e:
        print(f"\n❌ 測試發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
