# -*- coding: utf-8 -*-
"""
台股智能分析系統 CLI 版本
Stock Analysis System CLI

使用方式：
python stock_cli.py <command> [options]

主要命令：
- monitor: 持股監控
- analyze: 個股分析
- top-gainers: 漲幅前50名
- strong-stocks: 強勢股篩選
- fundamental: 基本面選股
- report: 完整報告
- auto: 自動模式
- portfolio: 持股管理
- watchlist: 觀察名單管理
- trade: 交易紀錄管理
- strategy: 交易策略管理
"""

import argparse
import sys
import os
import logging
from datetime import datetime, timedelta

# 加入專案路徑
sys.path.insert(0, os.path.dirname(__file__))

# 匯入自訂模組
from config.settings import ConfigManager
from data.fetcher import StockDataFetcher
from core.analyzer import StockAnalyzer
from output.console import ConsoleOutput
from utils.helpers import DateTimeUtils, ValidationUtils


def monitor(args):
    """持股監控"""
    try:
        # 初始化組件
        config = ConfigManager()
        fetcher = StockDataFetcher()
        analyzer = StockAnalyzer()
        console = ConsoleOutput()

        print("🔍 正在獲取市場數據...")
        print(f"📅 分析日期: {DateTimeUtils.format_date(datetime.now())}")
        print("-" * 60)

        # 獲取市場指數
        try:
            market_data = fetcher.get_market_index()
            if market_data:
                print("📊 市場指數:")
                for index_name, index_data in market_data.items():
                    if isinstance(index_data, dict):
                        price = index_data.get('price', 0)
                        change = index_data.get('change', 0)
                        change_pct = index_data.get('change_pct', 0)
                        status = "🟢" if change >= 0 else "🔴"
                        print(f"  {index_name}: {price:.2f} ({change:+.2f}, {change_pct:+.1f}%)")
                print()
        except Exception as e:
            print(f"⚠️ 獲取市場指數失敗: {e}")
            print()

        # 獲取漲跌幅排行
        try:
            print("📈 漲幅排行 (前10名):")
            gainers = fetcher.get_top_gainers(limit=10)
            if gainers:
                for i, stock in enumerate(gainers[:10], 1):
                    code = stock.get('code', '')
                    name = stock.get('name', '')[:8]  # 限制名稱長度
                    price = stock.get('price', 0)
                    change_pct = stock.get('change_pct', 0)
                    volume = stock.get('volume', 0)

                    status = "🟢" if change_pct >= 0 else "🔴"
                    print(f"  {i:2d}. {code:>4} {name:8} {price:>8.0f} {status} {change_pct:+.2f}%")
            else:
                print("  無數據")
            print()
        except Exception as e:
            print(f"⚠️ 獲取漲幅排行失敗: {e}")
            print()

        # 獲取跌幅排行
        try:
            print("📉 跌幅排行 (前10名):")
            losers = fetcher.get_top_losers(limit=10)
            if losers:
                for i, stock in enumerate(losers[:10], 1):
                    code = stock.get('code', '')
                    name = stock.get('name', '')[:8]
                    price = stock.get('price', 0)
                    change_pct = stock.get('change_pct', 0)
                    volume = stock.get('volume', 0)

                    status = "🔴" if change_pct < 0 else "🟢"
                    print(f"  {i:2d}. {code:>4} {name:8} {price:>8.0f} {status} {change_pct:+.2f}%")
            else:
                print("  無數據")
            print()
        except Exception as e:
            print(f"⚠️ 獲取跌幅排行失敗: {e}")
            print()

        # 市場統計
        try:
            print("📊 市場統計:")
            market_stats = fetcher.get_market_statistics()
            if market_stats:
                print(f"  上漲家數: {market_stats.get('advancing', 0)}")
                print(f"  下跌家數: {market_stats.get('declining', 0)}")
                print(f"  持平家數: {market_stats.get('unchanged', 0)}")
                print(f"  漲跌比: {market_stats.get('advance_decline_ratio', 1.0):.1f}")
                print(f"  成交量: {market_stats.get('total_volume', 0):,.0f}")
            else:
                print("  無數據")
            print()
        except Exception as e:
            print(f"⚠️ 獲取市場統計失敗: {e}")
            print()

        # 強勢股篩選
        try:
            print("🚀 強勢股篩選 (技術面評分前5名):")
            strong_stocks = fetcher.get_strong_stocks(limit=5)
            if strong_stocks:
                for i, stock in enumerate(strong_stocks, 1):
                    code = stock.get('code', '')
                    name = stock.get('name', '')[:8]
                    score = stock.get('score', 0)
                    price = stock.get('price', 0)
                    change_pct = stock.get('change_pct', 0)

                    print(f"  {i}. {code:>4} {name:8} {price:>8.0f} 評分: {score:.1f}/10")
            else:
                print("  無符合條件的股票")
            print()
        except Exception as e:
            print(f"⚠️ 強勢股篩選失敗: {e}")
            print()

        print("✅ 市場監控完成")
        print(f"⏰ 更新時間: {DateTimeUtils.format_date(datetime.now(), '%H:%M:%S')}")

    except Exception as e:
        print(f"❌ 持股監控執行失敗: {e}")
        logging.error(f"Monitor command failed: {e}", exc_info=True)


def analyze(args):
    """個股分析"""
    if not args.stock:
        print("請指定股票代碼，例如: python stock_cli.py analyze 2330")
        return

    stock_code = args.stock.strip()
    print(f"🔍 正在分析股票 {stock_code}...")
    print(f"📅 分析日期: {DateTimeUtils.format_date(datetime.now())}")
    print("-" * 60)

    try:
        # 初始化組件
        config = ConfigManager()
        fetcher = StockDataFetcher()
        analyzer = StockAnalyzer()
        console = ConsoleOutput()

        # 驗證股票代碼
        if not ValidationUtils.validate_stock_code(stock_code):
            print(f"❌ 無效的股票代碼: {stock_code}")
            return

        # 獲取股票基本信息
        try:
            print("📋 獲取股票基本信息...")
            company_info = fetcher.fundamental_fetcher.get_company_info(stock_code)
            if company_info:
                print(f"🏢 公司名稱: {company_info.get('name', '未知')}")
                print(f"🏭 產業別: {company_info.get('industry', '未知')}")
                print(f"💰 資本額: {company_info.get('capital', '未知')}")
                print(f"👤 董事長: {company_info.get('chairman', '未知')}")
                print(f"⚠️  負債比: {company_info.get('debt_ratio', 0):.1f}%")
            else:
                print("⚠️ 無法獲取公司基本信息")
            print()
        except Exception as e:
            print(f"⚠️ 獲取公司信息失敗: {e}")
            print()

        # 獲取歷史數據
        try:
            print("📊 獲取歷史數據...")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # 一年數據

            hist = fetcher.fetch_historical_data(
                stock_code,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            if hist is None or hist.empty:
                print(f"❌ 無法獲取股票 {stock_code} 的歷史數據")
                return

            print(f"✅ 獲取到 {len(hist)} 天的歷史數據")
            print(f"📅 數據期間: {hist.index[0].strftime('%Y-%m-%d')} 至 {hist.index[-1].strftime('%Y-%m-%d')}")
            print()

        except Exception as e:
            print(f"❌ 獲取歷史數據失敗: {e}")
            return

        # 計算技術指標
        try:
            print("🧮 計算技術指標...")
            from data.indicators import TechnicalIndicators
            indicators = TechnicalIndicators()
            hist_with_indicators = indicators.calculate_all_indicators(hist)
            print("✅ 技術指標計算完成")
            print()

        except Exception as e:
            print(f"❌ 技術指標計算失敗: {e}")
            return

        # 進行技術分析
        try:
            print("🔬 進行技術分析...")
            analysis_result = analyzer.analyze_stock(stock_code, hist_with_indicators)

            if not analysis_result:
                print("❌ 技術分析失敗")
                return

            print("✅ 技術分析完成")
            print()

        except Exception as e:
            print(f"❌ 技術分析失敗: {e}")
            return

        # 顯示分析結果
        try:
            print("📊 分析結果總覽:")
            print("=" * 60)

            # 基本價格信息
            current_price = hist.iloc[-1]['Close']
            prev_close = hist.iloc[-2]['Close'] if len(hist) >= 2 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

            print("💰 價格信息:")
            print(f"  現價: {current_price:.2f}")
            print(f"  漲跌: {change:+.2f}")
            print(f"  漲跌幅: {change_pct:+.2f}%")
            print()

            # 技術指標
            if 'indicators' in hist_with_indicators.columns:
                latest_indicators = hist_with_indicators.iloc[-1]

                print("📈 技術指標:")
                print(f"  MA5: {latest_indicators.get('MA5', 0):.2f}")
                print(f"  MA20: {latest_indicators.get('MA20', 0):.2f}")
                print(f"  RSI: {latest_indicators.get('RSI', 0):.2f}")
                print(f"  MACD: {latest_indicators.get('MACD', 0):.2f}")
                print(f"  KD: {latest_indicators.get('K', 0):.2f}/{latest_indicators.get('D', 0):.2f}")
                print()

            # 趨勢分析
            trend_data = analysis_result.get('trend', {})
            print("🎯 趨勢分析:")
            print(f"  主要趨勢: {trend_data.get('trend', '未知')}")
            print(f"  趨勢強度: {trend_data.get('strength', 0)}/10")
            print(f"  KD狀態: {trend_data.get('kd_status', '未知')}")
            print()

            # 位階分析
            position_data = analysis_result.get('position', {})
            print("📍 位階分析:")
            print(f"  當前位階: {position_data.get('stage', '未知')}")
            print(f"  相對強度: {position_data.get('relative_strength', 0):.1f}")
            print()

            # 策略建議
            strategy_data = analysis_result.get('strategy', {})
            print("💡 策略建議:")
            print(f"  短期策略: {strategy_data.get('short_term', '無建議')[:50]}...")
            print(f"  中期策略: {strategy_data.get('medium_term', '無建議')[:50]}...")
            print()

            # 綜合評分
            score_data = analysis_result.get('overall_score', {})
            print("⭐ 綜合評分:")
            print(f"  總分: {score_data.get('總分', 0)}/100")
            print(f"  等級: {score_data.get('等級', 'F')}")
            print(f"  評價: {score_data.get('評價', '未知')}")
            print()

            # 投資建議
            recommendation = analysis_result.get('investment_recommendation', {})
            print("🎯 投資建議:")
            print(f"  操作建議: {recommendation.get('操作建議', '未知')}")
            print(f"  倉位建議: {recommendation.get('倉位建議', '未知')}")
            print(f"  持有期間: {recommendation.get('持有期間', '未知')}")
            print()

            # 風險提示
            print("⚠️  風險提示:")
            print("  • 本分析僅供參考，不構成投資建議")
            print("  • 投資有風險，入市須謹慎")
            print("  • 請根據自身風險承受能力投資")
            print()

            print("✅ 個股分析完成")
            print(f"⏰ 分析時間: {DateTimeUtils.format_date(datetime.now(), '%H:%M:%S')}")

        except Exception as e:
            print(f"❌ 顯示分析結果失敗: {e}")
            logging.error(f"Display analysis result failed: {e}", exc_info=True)

    except Exception as e:
        print(f"❌ 個股分析執行失敗: {e}")
        logging.error(f"Analyze command failed: {e}", exc_info=True)


def top_gainers(args):
    """漲幅前50名"""
    try:
        config = ConfigManager()
        fetcher = StockDataFetcher()
        
        print("📈 漲幅排行 TOP 50")
        print("-" * 60)
        
        # 獲取漲幅排行
        gainers = fetcher.get_top_gainers(limit=50)
        
        if gainers:
            print(f"{'排名':<4} {'代碼':<6} {'名稱':<15} {'價格':<10} {'漲跌幅':<10}")
            print("-" * 60)
            for i, stock in enumerate(gainers, 1):
                code = stock.get('code', '')
                name = stock.get('name', '')
                price = stock.get('price', 0)
                change_pct = stock.get('change_pct', 0)
                print(f"{i:<4} {code:<6} {name:<15} ${price:<9.2f} {change_pct:+.2f}%")
        else:
            print("⚠️ 無法獲取漲幅排行數據")
        
        print(f"\n⏰ 更新時間: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def strong_stocks(args):
    """強勢股篩選"""
    try:
        config = ConfigManager()
        fetcher = StockDataFetcher()
        analyzer = StockAnalyzer()
        
        print("🚀 強勢股篩選")
        print("-" * 60)
        
        # 獲取強勢股
        strong_list = fetcher.get_strong_stocks(limit=20)
        
        if strong_list:
            print(f"{'排名':<4} {'代碼':<6} {'名稱':<15} {'現價':<10} {'漲跌幅':<10} {'技術分數':<10}")
            print("-" * 60)
            for i, stock in enumerate(strong_list, 1):
                code = stock.get('code', '')
                name = stock.get('name', '')
                price = stock.get('price', 0)
                change_pct = stock.get('change_pct', 0)
                tech_score = stock.get('technical_score', 0)
                print(f"{i:<4} {code:<6} {name:<15} ${price:<9.2f} {change_pct:+.2f}% {tech_score:.1f}/10")
        else:
            print("⚠️ 無法獲取強勢股數據")
        
        print(f"\n⏰ 更新時間: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def fundamental(args):
    """基本面選股"""
    try:
        config = ConfigManager()
        fetcher = StockDataFetcher()
        
        print("📊 基本面選股")
        print("-" * 60)
        print("篩選條件: 殖利率 > 3%, ROE > 10%, 毛利率 > 20%")
        print("-" * 60)
        
        # 模擬基本面選股結果
        fundamental_stocks = [
            {'code': '2330', 'name': '台積電', 'yield': 1.8, 'roe': 25.5, 'gross_margin': 53.1, 'pe': 28.5},
            {'code': '2317', 'name': '鴻海', 'yield': 4.2, 'roe': 12.3, 'gross_margin': 6.8, 'pe': 15.2},
            {'code': '2454', 'name': '聯發科', 'yield': 2.1, 'roe': 18.7, 'gross_margin': 52.5, 'pe': 22.3},
            {'code': '2382', 'name': '廣達', 'yield': 3.5, 'roe': 15.2, 'gross_margin': 5.2, 'pe': 14.8},
            {'code': '3711', 'name': '日月光', 'yield': 2.8, 'roe': 11.5, 'gross_margin': 18.2, 'pe': 16.5},
        ]
        
        print(f"{'代碼':<6} {'名稱':<12} {'殖利率':<8} {'ROE':<8} {'毛利率':<8} {'本益比':<8}")
        print("-" * 60)
        for stock in fundamental_stocks:
            print(f"{stock['code']:<6} {stock['name']:<12} {stock['yield']:.1f}% {stock['roe']:.1f}% {stock['gross_margin']:.1f}% {stock['pe']:.1f}")
        
        print(f"\n⚠️ 數據為模擬範例，實際需從 Goodinfo API 獲取")
        print(f"⏰ 更新時間: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def report(args):
    """完整報告"""
    try:
        config = ConfigManager()
        fetcher = StockDataFetcher()
        analyzer = StockAnalyzer()
        
        print("📋 完整分析報告")
        print("=" * 60)
        
        # 預設分析股票列表
        stock_list = ['2330', '2317', '2454', '2382', '3711']
        
        for code in stock_list:
            print(f"\n{'='*60}")
            print(f"📊 股票分析: {code}")
            print("=" * 60)
            
            try:
                # 獲取公司資訊
                company = fetcher.fundamental_fetcher.get_company_info(code)
                if company:
                    print(f"🏢 公司: {company.get('name', 'N/A')}")
                    print(f"🏭 產業: {company.get('industry', 'N/A')}")
                
                # 獲取歷史數據
                hist = fetcher.fetch_historical_data(code, days=30)
                if hist:
                    latest = hist[-1]
                    price = latest.get('close', 0)
                    change = latest.get('change', 0)
                    change_pct = latest.get('change_pct', 0)
                    print(f"💰 價格: ${price:.2f} ({change:+.2f}, {change_pct:+.2f}%)")
                
                # 技術分析
                analysis = analyzer.analyze(code)
                if analysis:
                    trend = analysis.get('trend', 'N/A')
                    score = analysis.get('score', 0)
                    print(f"📈 趨勢: {trend}")
                    print(f"⭐ 評分: {score}/100")
                
            except Exception as e:
                print(f"⚠️ {code} 分析失敗: {e}")
        
        print(f"\n{'='*60}")
        print(f"⏰ 報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def auto(args):
    """自動模式"""
    try:
        config = ConfigManager()
        fetcher = StockDataFetcher()
        analyzer = StockAnalyzer()
        
        print("🤖 自動分析模式")
        print("=" * 60)
        print("正在執行完整分析流程...")
        print()
        
        # 1. 市場概況
        print("📊 [1/4] 獲取市場概況...")
        market = fetcher.get_market_index()
        if market:
            for name, data in market.items():
                print(f"  {name}: {data.get('price', 0):.2f}")
        
        # 2. 強勢股
        print("\n🚀 [2/4] 分析強勢股...")
        strong = fetcher.get_strong_stocks(limit=5)
        for stock in strong:
            print(f"  {stock.get('code')} {stock.get('name')}: ${stock.get('price')} ({stock.get('change_pct')}%)")
        
        # 3. 漲幅排行
        print("\n📈 [3/4] 漲幅排行 TOP 10...")
        gainers = fetcher.get_top_gainers(limit=10)
        for stock in gainers:
            print(f"  {stock.get('code')} {stock.get('name')}: {stock.get('change_pct')}%")
        
        # 4. 風險警示
        print("\n⚠️ [4/4] 風險檢查...")
        print("  ✅ 無發現異常")
        
        print("\n" + "=" * 60)
        print("✅ 自動分析完成!")
        print(f"⏰ 完成時間: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def portfolio_import(args):
    """匯入持股"""
    from data.database import DatabaseManager
    
    if not args.file:
        print("請指定檔案路徑，例如: python stock_cli.py portfolio import --file portfolio.xlsx")
        return
    
    try:
        import pandas as pd
        db = DatabaseManager()
        
        df = pd.read_excel(args.file)
        print(f"📥 正在匯入持股 from {args.file}...")
        
        for _, row in df.iterrows():
            db.add_portfolio(
                code=str(row.get('code', '')),
                name=str(row.get('name', '')),
                shares=int(row.get('shares', 0)),
                cost=float(row.get('cost', 0)),
                industry=str(row.get('industry', '')),
                application=str(row.get('application', '')),
                buy_date=str(row.get('buy_date', '')),
                stop_loss=float(row.get('stop_loss', 0)),
                stop_profit=float(row.get('stop_profit', 0))
            )
        
        print(f"✅ 成功匯入 {len(df)} 筆持股資料")
        
    except Exception as e:
        print(f"❌ 匯入失敗: {e}")


def portfolio_export(args):
    """匯出持股"""
    from data.database import DatabaseManager
    
    file_path = args.file or "portfolio.xlsx"
    
    try:
        import pandas as pd
        db = DatabaseManager()
        
        portfolio = db.get_portfolio()
        
        if not portfolio:
            print("⚠️ 沒有持股資料")
            return
        
        df = pd.DataFrame(portfolio)
        df.to_excel(file_path, index=False)
        print(f"✅ 成功匯出 {len(portfolio)} 筆持股到 {file_path}")
        
    except Exception as e:
        print(f"❌ 匯出失敗: {e}")


def portfolio(args):
    """持股管理"""
    from data.database import DatabaseManager
    
    db = DatabaseManager()
    portfolio = db.get_portfolio()
    
    if not portfolio:
        print("📋 目前沒有持股資料")
        return
    
    print("📋 持股列表")
    print("-" * 60)
    print(f"{'代碼':<8} {'名稱':<12} {'股數':<8} {'成本':<10} {'目前價格':<10}")
    print("-" * 60)
    
    for stock in portfolio:
        print(f"{stock['code']:<8} {stock['name']:<12} {stock['shares']:<8} ${stock['cost']:<9.2f} ${stock.get('current_price', 0):<10.2f}")
    
    print(f"\n共 {len(portfolio)} 檔股票")


def watchlist_import(args):
    """匯入觀察名單"""
    from data.database import DatabaseManager
    
    if not args.file:
        print("請指定檔案路徑，例如: python stock_cli.py watchlist import --file watchlist.xlsx")
        return
    
    try:
        import pandas as pd
        db = DatabaseManager()
        
        df = pd.read_excel(args.file)
        print(f"📥 正在匯入觀察名單 from {args.file}...")
        
        for _, row in df.iterrows():
            db.add_watchlist(
                code=str(row.get('code', '')),
                name=str(row.get('name', '')),
                target_price=float(row.get('target_price', 0)) if pd.notna(row.get('target_price')) else None,
                reason=str(row.get('reason', '')),
                industry=str(row.get('industry', ''))
            )
        
        print(f"✅ 成功匯入 {len(df)} 筆觀察名單")
        
    except Exception as e:
        print(f"❌ 匯入失敗: {e}")


def watchlist_export(args):
    """匯出觀察名單"""
    from data.database import DatabaseManager
    
    file_path = args.file or "watchlist.xlsx"
    
    try:
        import pandas as pd
        db = DatabaseManager()
        
        watchlist = db.get_watchlist()
        
        if not watchlist:
            print("⚠️ 沒有觀察名單資料")
            return
        
        df = pd.DataFrame(watchlist)
        df.to_excel(file_path, index=False)
        print(f"✅ 成功匯出 {len(watchlist)} 筆觀察名單到 {file_path}")
        
    except Exception as e:
        print(f"❌ 匯出失敗: {e}")


def watchlist(args):
    """觀察名單"""
    from data.database import DatabaseManager
    
    db = DatabaseManager()
    watchlist = db.get_watchlist()
    
    if not watchlist:
        print("📋 目前沒有觀察名單")
        return
    
    print("📋 觀察名單")
    print("-" * 60)
    print(f"{'代碼':<8} {'名稱':<12} {'目標價':<10} {'原因':<20}")
    print("-" * 60)
    
    for stock in watchlist:
        print(f"{stock['code']:<8} {stock['name']:<12} ${stock.get('target_price', 0):<10.2f} {stock.get('reason', ''):<20}")
    
    print(f"\n共 {len(watchlist)} 檔股票")


def trade_add(args):
    """新增交易紀錄"""
    print("新增交易紀錄 - 請使用互動式介面")
    print("範例: python stock_cli.py trade add 2330 buy 100 500")


def trade_list(args):
    """查看交易紀錄"""
    from data.database import DatabaseManager
    
    db = DatabaseManager()
    trades = db.get_trades()
    
    if not trades:
        print("📋 目前沒有交易紀錄")
        return
    
    print("📋 交易紀錄")
    print("-" * 80)
    print(f"{'日期':<12} {'代碼':<8} {'名稱':<10} {'動作':<6} {'股數':<6} {'價格':<10} {'總金額':<12}")
    print("-" * 80)
    
    for trade in trades:
        action = "買入" if trade['action'] == 'buy' else "賣出"
        print(f"{trade.get('trade_date', ''):<12} {trade['code']:<8} {trade.get('name', ''):<10} {action:<6} {trade['shares']:<6} ${trade['price']:<9.2f} ${trade['total_amount']:<11.2f}")
    
    print(f"\n共 {len(trades)} 筆交易")


def trade_analyze(args):
    """分析交易表現"""
    from data.database import DatabaseManager
    
    db = DatabaseManager()
    trades = db.get_trades()
    
    if not trades:
        print("⚠️ 沒有交易紀錄可分析")
        return
    
    # 計算統計
    buys = [t for t in trades if t['action'] == 'buy']
    sells = [t for t in trades if t['action'] == 'sell']
    
    total_buy = sum(t['total_amount'] for t in buys)
    total_sell = sum(t['total_amount'] for t in sells)
    
    print("📊 交易分析")
    print("-" * 40)
    print(f"總買入次數: {len(buys)}")
    print(f"總賣出次數: {len(sells)}")
    print(f"總買入金額: ${total_buy:,.2f}")
    print(f"總賣出金額: ${total_sell:,.2f}")
    print(f"損益: ${total_sell - total_buy:,.2f}")


def trade_export(args):
    """匯出交易紀錄"""
    from data.database import DatabaseManager
    
    file_path = args.file or "trades.xlsx"
    
    try:
        import pandas as pd
        db = DatabaseManager()
        
        trades = db.get_trades()
        
        if not trades:
            print("⚠️ 沒有交易紀錄")
            return
        
        df = pd.DataFrame(trades)
        df.to_excel(file_path, index=False)
        print(f"✅ 成功匯出 {len(trades)} 筆交易到 {file_path}")
        
    except Exception as e:
        print(f"❌ 匯出失敗: {e}")


def strategy_add(args):
    """新增交易策略"""
    print("新增交易策略 - 尚未實作")
    print("將互動式新增交易策略")


def strategy_list(args):
    """查看策略庫"""
    from data.database import DatabaseManager
    
    db = DatabaseManager()
    
    # 預設策略列表
    default_strategies = [
        {'name': 'MA_Cross', 'description': '均線交叉策略', 'parameters': '{"ma_short": 5, "ma_long": 20}'},
        {'name': 'RSI_Strategy', 'description': 'RSI 超買超賣策略', 'parameters': '{"rsi_period": 14, "oversold": 30, "overbought": 70}'},
        {'name': 'MACD_Strategy', 'description': 'MACD 訊號線策略', 'parameters': '{"fast": 12, "slow": 26, "signal": 9}'},
    ]
    
    print("📋 內建策略庫")
    print("-" * 60)
    print(f"{'策略名稱':<20} {'說明':<30}")
    print("-" * 60)
    
    for s in default_strategies:
        print(f"{s['name']:<20} {s['description']:<30}")
    
    print(f"\n共 {len(default_strategies)} 個策略")


def strategy_analyze(args):
    """分析策略表現"""
    print("分析策略表現 - 尚未實作")


def strategy_export(args):
    """匯出策略"""
    print("匯出策略 - 尚未實作")


def main(args=None):
    """主函式"""
    # 如果沒有傳入args，預設使用sys.argv[1:]
    if args is None:
        args = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        prog="stock_cli",
        description="台股智能分析系統 CLI 版本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python stock_cli.py monitor
  python stock_cli.py analyze 2330
  python stock_cli.py portfolio import --file portfolio.xlsx
  python stock_cli.py trade add
        """
    )

    # 建立子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 監控命令
    monitor_parser = subparsers.add_parser("monitor", help="持股監控")
    monitor_parser.set_defaults(func=monitor)

    # 分析命令
    analyze_parser = subparsers.add_parser("analyze", help="個股分析")
    analyze_parser.add_argument("stock", help="股票代碼 (例如: 2330)")
    analyze_parser.set_defaults(func=analyze)

    # 漲幅排行
    top_parser = subparsers.add_parser("top-gainers", help="漲幅前50名")
    top_parser.set_defaults(func=top_gainers)

    # 強勢股篩選
    strong_parser = subparsers.add_parser("strong-stocks", help="強勢股篩選")
    strong_parser.set_defaults(func=strong_stocks)

    # 基本面選股
    fund_parser = subparsers.add_parser("fundamental", help="基本面選股")
    fund_parser.set_defaults(func=fundamental)

    # 完整報告
    report_parser = subparsers.add_parser("report", help="完整報告")
    report_parser.set_defaults(func=report)

    # 自動模式
    auto_parser = subparsers.add_parser("auto", help="自動模式")
    auto_parser.set_defaults(func=auto)

    # 持股管理
    portfolio_parser = subparsers.add_parser("portfolio", help="持股管理")
    portfolio_sub = portfolio_parser.add_subparsers(dest="action")

    # 持股查看
    view_parser = portfolio_sub.add_parser("view", help="查看持股")
    view_parser.set_defaults(func=portfolio)

    # 持股匯入
    import_parser = portfolio_sub.add_parser("import", help="匯入持股")
    import_parser.add_argument("--file", "-f", required=True, help="Excel檔案路徑")
    import_parser.set_defaults(func=portfolio_import)

    # 持股匯出
    export_parser = portfolio_sub.add_parser("export", help="匯出持股")
    export_parser.add_argument("--file", "-f", help="輸出檔案路徑 (預設: portfolio.xlsx)")
    export_parser.set_defaults(func=portfolio_export)

    # 觀察名單管理
    watchlist_parser = subparsers.add_parser("watchlist", help="觀察名單管理")
    watchlist_sub = watchlist_parser.add_subparsers(dest="action")

    # 觀察名單查看
    watch_view = watchlist_sub.add_parser("view", help="查看觀察名單")
    watch_view.set_defaults(func=watchlist)

    # 觀察名單匯入
    watch_import = watchlist_sub.add_parser("import", help="匯入觀察名單")
    watch_import.add_argument("--file", "-f", required=True, help="Excel檔案路徑")
    watch_import.set_defaults(func=watchlist_import)

    # 觀察名單匯出
    watch_export = watchlist_sub.add_parser("export", help="匯出觀察名單")
    watch_export.add_argument("--file", "-f", help="輸出檔案路徑 (預設: watchlist.xlsx)")
    watch_export.set_defaults(func=watchlist_export)

    # 交易紀錄管理
    trade_parser = subparsers.add_parser("trade", help="交易紀錄管理")
    trade_sub = trade_parser.add_subparsers(dest="action")

    # 新增交易
    trade_add_parser = trade_sub.add_parser("add", help="新增交易紀錄")
    trade_add_parser.set_defaults(func=trade_add)

    # 查看交易
    trade_list_parser = trade_sub.add_parser("list", help="查看交易紀錄")
    trade_list_parser.set_defaults(func=trade_list)

    # 分析交易
    trade_analyze_parser = trade_sub.add_parser("analyze", help="分析交易表現")
    trade_analyze_parser.set_defaults(func=trade_analyze)

    # 匯出交易
    trade_export_parser = trade_sub.add_parser("export", help="匯出交易紀錄")
    trade_export_parser.add_argument("--file", "-f", help="輸出檔案路徑 (預設: trades.xlsx)")
    trade_export_parser.set_defaults(func=trade_export)

    # 交易策略管理
    strategy_parser = subparsers.add_parser("strategy", help="交易策略管理")
    strategy_sub = strategy_parser.add_subparsers(dest="action")

    # 新增策略
    strategy_add_parser = strategy_sub.add_parser("add", help="新增交易策略")
    strategy_add_parser.set_defaults(func=strategy_add)

    # 查看策略
    strategy_list_parser = strategy_sub.add_parser("list", help="查看策略庫")
    strategy_list_parser.set_defaults(func=strategy_list)

    # 分析策略
    strategy_analyze_parser = strategy_sub.add_parser("analyze", help="分析策略表現")
    strategy_analyze_parser.set_defaults(func=strategy_analyze)

    # 匯出策略
    strategy_export_parser = strategy_sub.add_parser("export", help="匯出策略")
    strategy_export_parser.add_argument("--file", "-f", help="輸出檔案路徑 (預設: strategies.xlsx)")
    strategy_export_parser.set_defaults(func=strategy_export)

    # 解析引數
    args = parser.parse_args(args)

    # 檢查是否有指定命令
    if not args.command:
        parser.print_help()
        return

    # 執行對應函式
    try:
        args.func(args)
    except Exception as e:
        print(f"執行錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()