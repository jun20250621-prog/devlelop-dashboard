#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis System - 完整命令測試套件
Comprehensive CLI Command Test Suite
"""

import sys
import os
from argparse import Namespace
from datetime import datetime
import json

# 加入專案路徑
sys.path.insert(0, os.path.dirname(__file__))

# 導入所有命令函數
from stock_cli import (
    monitor, analyze, top_gainers, strong_stocks, fundamental, report, auto,
    portfolio, watchlist, portfolio_import, watchlist_import,
    trade_add, trade_list, trade_analyze, trade_export,
    strategy_add, strategy_list, strategy_analyze, strategy_export
)

class Colors:
    """ANSI 顏色代碼"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """打印標題"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_command(num, name, desc):
    """打印命令信息"""
    print(f"{Colors.BOLD}[{num:2d}] {name:<20} - {desc}{Colors.RESET}")

def test_command(cmd_num, cmd_name, cmd_func, args, expected_output=None):
    """執行單個命令測試"""
    print(f"\n{Colors.YELLOW}➤ 測試命令 {cmd_num}: {cmd_name}{Colors.RESET}")
    print(f"   參數: {args.__dict__}")
    print("   " + "-" * 65)
    
    try:
        # 執行命令
        cmd_func(args)
        print(f"   {Colors.GREEN}✓ 執行成功{Colors.RESET}")
        return {'status': 'PASS', 'error': None}
    except Exception as e:
        error_msg = str(e)[:80]
        print(f"   {Colors.RED}✗ 執行失敗: {error_msg}{Colors.RESET}")
        return {'status': 'FAIL', 'error': error_msg}

def main():
    """主測試函數"""
    print_header("📊 Stock Analysis System - 完整命令測試")
    
    # 定義所有命令及其測試參數
    test_cases = [
        # 市場監控命令
        {'num': 1, 'name': 'monitor', 'func': monitor, 'args': Namespace(), 'desc': '市場監控'},
        
        # 個股分析命令
        {'num': 2, 'name': 'analyze', 'func': analyze, 'args': Namespace(stock='2330'), 'desc': '個股分析'},
        
        # 排行榜命令
        {'num': 3, 'name': 'top-gainers', 'func': top_gainers, 'args': Namespace(limit=10), 'desc': '漲幅排行'},
        
        # 強勢股篩選
        {'num': 4, 'name': 'strong-stocks', 'func': strong_stocks, 'args': Namespace(limit=10), 'desc': '強勢股篩選'},
        
        # 基本面分析
        {'num': 5, 'name': 'fundamental', 'func': fundamental, 'args': Namespace(stock='2330'), 'desc': '基本面分析'},
        
        # 完整報告
        {'num': 6, 'name': 'report', 'func': report, 'args': Namespace(), 'desc': '完整報告'},
        
        # 自動模式
        {'num': 7, 'name': 'auto', 'func': auto, 'args': Namespace(), 'desc': '自動分析'},
        
        # 持股管理
        {'num': 8, 'name': 'portfolio', 'func': portfolio, 'args': Namespace(), 'desc': '持股管理'},
        
        # 觀察名單
        {'num': 9, 'name': 'watchlist', 'func': watchlist, 'args': Namespace(), 'desc': '觀察名單'},
        
        # 交易紀錄
        {'num': 10, 'name': 'trade-list', 'func': trade_list, 'args': Namespace(), 'desc': '交易紀錄'},
        
        # 策略列表
        {'num': 11, 'name': 'strategy-list', 'func': strategy_list, 'args': Namespace(), 'desc': '策略列表'},
        
        # 策略分析
        {'num': 12, 'name': 'strategy-analyze', 'func': strategy_analyze, 'args': Namespace(stock='2330', strategy='MA_Cross'), 'desc': '策略回測'},
    ]
    
    # 列出所有命令
    print_header("📋 所有可用命令列表 (12個)")
    for test in test_cases:
        print_command(test['num'], test['name'], test['desc'])
    
    # 執行測試
    print_header("🧪 開始執行命令測試")
    
    results = {}
    for test in test_cases:
        result = test_command(
            test['num'],
            test['name'],
            test['func'],
            test['args'],
            test['desc']
        )
        results[test['name']] = result
    
    # 測試摘要
    print_header("📊 測試結果摘要")
    
    passed = sum(1 for r in results.values() if r['status'] == 'PASS')
    failed = sum(1 for r in results.values() if r['status'] == 'FAIL')
    total = len(results)
    
    print(f"{Colors.BOLD}測試總數: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}✓ 通過: {passed}{Colors.RESET}")
    print(f"{Colors.RED}{Colors.BOLD}✗ 失敗: {failed}{Colors.RESET}")
    
    if failed > 0:
        print(f"\n{Colors.YELLOW}失敗的命令:{Colors.RESET}")
        for cmd, result in results.items():
            if result['status'] == 'FAIL':
                print(f"  {Colors.RED}✗ {cmd}: {result['error']}{Colors.RESET}")
    
    # 詳細結果表格
    print(f"\n{Colors.BOLD}詳細結果表:{Colors.RESET}")
    print("-" * 70)
    print(f"{'命令名稱':<20} {'狀態':<10} {'備註':<40}")
    print("-" * 70)
    
    for test in test_cases:
        cmd_name = test['name']
        result = results[cmd_name]
        status_display = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result['status'] == 'PASS' else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        error = result['error'] if result['error'] else '正常運行'
        print(f"{cmd_name:<20} {status_display:<15} {error:<40}")
    
    print("-" * 70)
    
    # 最終統計
    completion_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n{Colors.BOLD}完成度: {completion_rate:.1f}% ({passed}/{total}){Colors.RESET}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有命令測試通過！{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  檢測到 {failed} 個失敗的命令，請檢查{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}測試完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
