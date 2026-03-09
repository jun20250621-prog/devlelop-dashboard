#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis System - 簡化命令測試
Simplified CLI Command Test
"""

import sys
import os
from argparse import Namespace
from datetime import datetime

# 加入專案路徑
sys.path.insert(0, os.path.dirname(__file__))

# 導入命令函數
from stock_cli import (
    monitor, analyze, top_gainers, strong_stocks, fundamental, auto,
    portfolio, watchlist, trade_list, strategy_list, strategy_analyze
)

print("\n" + "="*70)
print("📊 Stock Analysis System - 完整命令列表與測試".center(70))
print("="*70 + "\n")

# 定義所有命令
commands = [
    ('1. monitor', '市場監控'),
    ('2. analyze', '個股分析'),
    ('3. top-gainers', '漲幅排行'),
    ('4. strong-stocks', '強勢股篩選'),
    ('5. fundamental', '基本面分析'),
    ('6. report', '完整報告'),
    ('7. auto', '自動分析'),
    ('8. portfolio', '持股管理'),
    ('9. watchlist', '觀察名單'),
    ('10. trade-list', '交易紀錄'),
    ('11. strategy-list', '策略庫'),
    ('12. strategy-analyze', '策略回測'),
]

# 列出所有命令
print("📋 可用命令列表 (12個):\n")
for cmd, desc in commands:
    print(f"  {cmd:<20} - {desc}")

print("\n" + "-"*70)
print("🧪 開始測試核心命令...\n")

test_results = {}

# 1. 測試 monitor
print("[1/11] 測試 monitor 命令")
try:
    monitor(Namespace())
    test_results['monitor'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['monitor'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 2. 測試 analyze
print("[2/11] 測試 analyze 命令")
try:
    analyze(Namespace(stock='2330'))
    test_results['analyze'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['analyze'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 3. 測試 top_gainers
print("[3/11] 測試 top-gainers 命令")
try:
    top_gainers(Namespace(limit=10))
    test_results['top-gainers'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['top-gainers'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 4. 測試 strong_stocks
print("[4/11] 測試 strong-stocks 命令")
try:
    strong_stocks(Namespace(limit=10))
    test_results['strong-stocks'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['strong-stocks'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 5. 測試 fundamental
print("[5/11] 測試 fundamental 命令")
try:
    fundamental(Namespace(stock='2330'))
    test_results['fundamental'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['fundamental'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 6. 測試 auto
print("[6/11] 測試 auto 命令")
try:
    auto(Namespace())
    test_results['auto'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['auto'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 7. 測試 portfolio
print("[7/11] 測試 portfolio 命令")
try:
    portfolio(Namespace())
    test_results['portfolio'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['portfolio'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 8. 測試 watchlist
print("[8/11] 測試 watchlist 命令")
try:
    watchlist(Namespace())
    test_results['watchlist'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['watchlist'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 9. 測試 trade_list
print("[9/11] 測試 trade-list 命令")
try:
    trade_list(Namespace())
    test_results['trade-list'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['trade-list'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 10. 測試 strategy_list
print("[10/11] 測試 strategy-list 命令")
try:
    strategy_list(Namespace())
    test_results['strategy-list'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['strategy-list'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 11. 測試 strategy_analyze
print("[11/11] 測試 strategy-analyze 命令")
try:
    strategy_analyze(Namespace(stock='2330', strategy='MA_Cross'))
    test_results['strategy-analyze'] = 'PASS'
    print("✓ PASS\n")
except Exception as e:
    test_results['strategy-analyze'] = f'FAIL: {str(e)[:50]}'
    print(f"✗ FAIL: {e}\n")

# 測試摘要
print("="*70)
print("📊 測試結果摘要".center(70))
print("="*70 + "\n")

passed = sum(1 for r in test_results.values() if r == 'PASS')
failed = sum(1 for r in test_results.values() if r != 'PASS')
total = len(test_results)

print(f"總測試命令數: {total}")
print(f"✓ 通過: {passed}")
print(f"✗ 失敗: {failed}")
print(f"成功率: {(passed/total*100):.1f}%\n")

if failed > 0:
    print("❌ 失敗的命令:")
    for cmd, result in test_results.items():
        if result != 'PASS':
            print(f"  • {cmd}: {result}")

print("\n" + "-"*70)
print("詳細結果表:")
print("-"*70)
print(f"{'命令名稱':<20} {'狀態':<10} {'備註':<40}")
print("-"*70)

for cmd, result in test_results.items():
    status = "✓ PASS" if result == 'PASS' else "✗ FAIL"
    remark = "正常運行" if result == 'PASS' else result
    print(f"{cmd:<20} {status:<10} {remark:<40}")

print("-"*70)

# 最終輸出
print(f"\n完成度: {(passed/total*100):.1f}% ({passed}/{total})")
if failed == 0:
    print("\n🎉 所有命令測試通過！系統運行正常！")
else:
    print(f"\n⚠️  檢測到 {failed} 個失敗命令，建議檢查")

print(f"\n測試完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
