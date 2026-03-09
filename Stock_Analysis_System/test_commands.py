#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速命令測試指令碼"""

import sys
from stock_cli import *
from argparse import Namespace

test_results = {}

# 準備測試參數
stock_code = '2330'

print("📋 執行命令測試...\n")
print("=" * 60)

# 1. monitor 命令
print("\n✓ 1. monitor - 市場監控")
try:
    args = Namespace()
    monitor(args)
    test_results['monitor'] = '✅ PASS'
    print("   結果: ✅ PASS")
except Exception as e:
    test_results['monitor'] = f'❌ FAIL: {str(e)[:50]}'
    print(f"   結果: ❌ FAIL - {e}")

# 2. analyze 命令
print("\n✓ 2. analyze - 個股分析")
try:
    args = Namespace(stock=stock_code)
    analyze(args)
    test_results['analyze'] = '✅ PASS'
    print("   結果: ✅ PASS")
except Exception as e:
    test_results['analyze'] = f'❌ FAIL: {str(e)[:50]}'
    print(f"   結果: ❌ FAIL - {e}")

# 3. top_gainers 命令
print("\n✓ 3. top_gainers - 漲幅排行")
try:
    args = Namespace(limit=10)
    top_gainers(args)
    test_results['top_gainers'] = '✅ PASS'
    print("   結果: ✅ PASS")
except Exception as e:
    test_results['top_gainers'] = f'❌ FAIL: {str(e)[:50]}'
    print(f"   結果: ❌ FAIL - {e}")

# 4. strong_stocks 命令
print("\n✓ 4. strong_stocks - 強勢股篩選")
try:
    args = Namespace(limit=10)
    strong_stocks(args)
    test_results['strong_stocks'] = '✅ PASS'
    print("   結果: ✅ PASS")
except Exception as e:
    test_results['strong_stocks'] = f'❌ FAIL: {str(e)[:50]}'
    print(f"   結果: ❌ FAIL - {e}")

# 5. fundamental 命令
print("\n✓ 5. fundamental - 基本面選股")
try:
    args = Namespace(stock=stock_code)
    fundamental(args)
    test_results['fundamental'] = '✅ PASS'
    print("   結果: ✅ PASS")
except Exception as e:
    test_results['fundamental'] = f'❌ FAIL: {str(e)[:50]}'
    print(f"   結果: ❌ FAIL - {e}")

# 6. report 命令
print("\n✓ 6. report - 完整報告")
try:
    args = Namespace()
    report(args)
    test_results['report'] = '✅ PASS'
    print("   結果: ✅ PASS")
except Exception as e:
    test_results['report'] = f'❌ FAIL: {str(e)[:50]}'
    print(f"   結果: ❌ FAIL - {e}")

# 7. auto 命令
print("\n✓ 7. auto - 自動模式")
try:
    args = Namespace()
    auto(args)
    test_results['auto'] = '✅ PASS'
    print("   結果: ✅ PASS")
except Exception as e:
    test_results['auto'] = f'❌ FAIL: {str(e)[:50]}'
    print(f"   結果: ❌ FAIL - {e}")

# 8. portfolio 命令
print("\n✓ 8. portfolio - 持股管理")
try:
    args = Namespace()
    portfolio(args)
    test_results['portfolio'] = '✅ PASS'
    print("   結果: ✅ PASS")
except Exception as e:
    test_results['portfolio'] = f'❌ FAIL: {str(e)[:50]}'
    print(f"   結果: ❌ FAIL - {e}")

print("\n" + "=" * 60)
print("\n📊 測試總結:")
print("-" * 60)
passed = sum(1 for v in test_results.values() if 'PASS' in v)
failed = sum(1 for v in test_results.values() if 'FAIL' in v)
for cmd, result in test_results.items():
    print(f"  {cmd:<20} {result}")
print("-" * 60)
print(f"✅ 通過: {passed}, ❌ 失敗: {failed}, 總計: {len(test_results)}")
