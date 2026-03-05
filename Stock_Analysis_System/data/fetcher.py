# -*- coding: utf-8 -*-
"""
資料獲取模組
Data Fetcher Module

負責從 Yahoo Finance 等來源獲取股票數據
"""

import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import time
import pickle
import os
import logging
from datetime import datetime, timedelta
from dateutil.parser import parse

logger = logging.getLogger(__name__)


class FundamentalDataFetcher:
    """基本面資料獲取器"""

    def __init__(self):
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_dividend_yield(self, stock_code):
        """獲取近5年平均殖利率"""
        cache_file = os.path.join(self.cache_dir, f"{stock_code}_dividend.pkl")

        # 嘗試從緩存讀取
        if os.path.exists(cache_file):
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < 7 * 24 * 3600:  # 7天緩存
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except:
                    pass

        # 從Yahoo Finance獲取數據
        try:
            stock = yf.Ticker(f"{stock_code}.TW")
            dividends = stock.dividends

            if dividends is not None and not dividends.empty:
                # 計算近5年平均殖利率
                five_years_ago = datetime.now() - timedelta(days=5*365)
                recent_dividends = dividends[dividends.index >= five_years_ago]

                if not recent_dividends.empty:
                    # 獲取當前股價
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        current_price = hist.iloc[-1]['Close']
                        total_dividend = recent_dividends.sum()
                        avg_yield = (total_dividend / current_price) * 100

                        # 保存到緩存
                        with open(cache_file, 'wb') as f:
                            pickle.dump(avg_yield, f)

                        return avg_yield

            return None
        except Exception as e:
            logger.error(f"獲取{stock_code}殖利率失敗: {e}")
            return None

    def get_roe(self, stock_code):
        """獲取近4季平均ROE"""
        cache_file = os.path.join(self.cache_dir, f"{stock_code}_roe.pkl")

        # 嘗試從緩存讀取
        if os.path.exists(cache_file):
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < 7 * 24 * 3600:  # 7天緩存
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except:
                    pass

        # 從Goodinfo獲取數據
        url = f"https://goodinfo.tw/StockInfo/StockFinDetail.asp?STOCK_ID={stock_code}&RPT_CAT=XX"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://goodinfo.tw/StockInfo/StockFinDetail.asp',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 解析ROE數據
            table = soup.find('table', {'id': 'tblFinDetail'})
            if not table:
                return None

            rows = table.find_all('tr')
            roe_data = []

            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 2:
                    continue

                if 'ROE' in cols[0].text:
                    for i in range(1, min(5, len(cols))):  # 最近4季
                        try:
                            roe = float(cols[i].text.strip().replace('%', ''))
                            roe_data.append(roe)
                        except:
                            continue
                    break

            if not roe_data:
                return None

            avg_roe = sum(roe_data) / len(roe_data)

            # 保存到緩存
            with open(cache_file, 'wb') as f:
                pickle.dump(avg_roe, f)

            return avg_roe
        except Exception as e:
            logger.error(f"獲取{stock_code}ROE失敗: {e}")
            return None

    def get_gross_margin(self, stock_code):
        """獲取最近一季毛利率"""
        cache_file = os.path.join(self.cache_dir, f"{stock_code}_gross_margin.pkl")

        # 嘗試從緩存讀取
        if os.path.exists(cache_file):
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < 7 * 24 * 3600:  # 7天緩存
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except:
                    pass

        # 從Goodinfo獲取數據
        url = f"https://goodinfo.tw/StockInfo/StockFinDetail.asp?STOCK_ID={stock_code}&RPT_CAT=XX"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://goodinfo.tw/StockInfo/StockFinDetail.asp',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 解析毛利率數據
            table = soup.find('table', {'id': 'tblFinDetail'})
            if not table:
                return None

            rows = table.find_all('tr')
            gross_margin = None

            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 2:
                    continue

                if '毛利率' in cols[0].text:
                    try:
                        gross_margin = float(cols[1].text.strip().replace('%', ''))
                    except:
                        continue
                    break

            if gross_margin is None:
                return None

            # 保存到緩存
            with open(cache_file, 'wb') as f:
                pickle.dump(gross_margin, f)

            return gross_margin
        except Exception as e:
            logger.error(f"獲取{stock_code}毛利率失敗: {e}")
            return None

    def get_company_info(self, stock_code):
        """獲取公司基本資料"""
        cache_file = os.path.join(self.cache_dir, f"{stock_code}_info.pkl")

        if os.path.exists(cache_file):
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < 30 * 24 * 3600:  # 30天緩存
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except:
                    pass

        url = f"https://goodinfo.tw/StockInfo/BasicInfo.asp?STOCK_ID={stock_code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://goodinfo.tw/StockInfo/BasicInfo.asp',
            'Accept-Language': 'zh-TW,zh;q=0.9'
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            info = {
                'industry': '--',
                'capital': '--',
                'chairman': '--',
                'ceo': '--',
                'debt_ratio': 0
            }

            # 解析產業
            tables = soup.find_all('table', {'class': 'solid_1_padding_3_3_tbl'})
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        cell_text = cols[0].text.strip()
                        if '所屬產業' in cell_text:
                            info['industry'] = cols[1].text.strip()
                        elif '資本額' in cell_text:
                            info['capital'] = cols[1].text.strip()
                        elif '董事長' in cell_text:
                            info['chairman'] = cols[1].text.strip()
                        elif '總經理' in cell_text:
                            info['ceo'] = cols[1].text.strip()

            # 獲取負債比
            debt_ratio = self.get_debt_ratio(stock_code)
            if debt_ratio:
                info['debt_ratio'] = debt_ratio

            # 保存到緩存
            with open(cache_file, 'wb') as f:
                pickle.dump(info, f)

            return info

        except Exception as e:
            logger.error(f"獲取{stock_code}公司資料失敗: {e}")
            return {
                'industry': '--',
                'capital': '--',
                'chairman': '--',
                'ceo': '--',
                'debt_ratio': 0
            }

    def get_debt_ratio(self, stock_code):
        """獲取負債比"""
        try:
            # 從Yahoo Finance獲取資產負債表數據
            stock = yf.Ticker(f"{stock_code}.TW")
            balance_sheet = stock.balance_sheet

            if balance_sheet is not None and not balance_sheet.empty:
                # 獲取最近一期的總負債和總資產
                total_liab = balance_sheet.loc['Total Liab'] if 'Total Liab' in balance_sheet.index else 0
                total_assets = balance_sheet.loc['Total Assets'] if 'Total Assets' in balance_sheet.index else 1

                if total_assets > 0:
                    return (total_liab / total_assets) * 100

            return 45.0  # 預設值
        except:
            return 45.0


class StockDataFetcher:
    """股票數據獲取器"""

    def __init__(self):
        self.holidays = set()
        self.stock_list_cache = {}
        self.cache_expiry = 7 * 24 * 3600  # 7天緩存
        self.fundamental_fetcher = FundamentalDataFetcher()
        self.load_holidays()

    def is_market_open(self, date):
        """判斷指定日期是否為台灣股市開盤日"""
        try:
            if isinstance(date, str):
                date = pd.Timestamp(date).date()
            elif isinstance(date, datetime):
                date = date.date()
            elif isinstance(date, pd.Timestamp):
                date = date.date()

            # 檢查是否為週末
            if date.weekday() >= 5:  # 5=星期六, 6=星期日
                return False

            # 檢查是否為休市日
            if date in self.holidays:
                return False

            # 特殊節日檢查（台灣股市休市日）
            month_day = (date.month, date.day)
            taiwan_holidays = [
                (1, 1),   # 元旦
                (2, 28),  # 228紀念日
                (4, 4),   # 清明節（可能變動）
                (5, 1),   # 勞動節
                (10, 10), # 國慶日
            ]

            if month_day in taiwan_holidays:
                return False

            return True
        except Exception as e:
            logger.error(f"檢查市場開放狀態失敗 {date}: {e}")
            return False

    def get_trading_days(self, start_date, end_date):
        """獲取指定日期範圍內的交易日"""
        trading_days = []
        current_date = start_date

        while current_date <= end_date:
            if self.is_market_open(current_date):
                trading_days.append(current_date)
            current_date += timedelta(days=1)

        return trading_days

    def load_holidays(self, years=None):
        """加載休市日數據"""
        if years is None:
            years = [datetime.now().year, datetime.now().year-1]

        for year in years:
            # 加入基本的台灣股市休市日
            # 農曆新年（每年變動，這裡用近似值）
            chinese_new_year = [
                datetime(year, 1, date).date() for date in [28, 29, 30, 31]  # 除夕到初三
            ]
            self.holidays.update(chinese_new_year)

            # 中秋節（農曆8月15日，用陽曆近似）
            if year == 2023:
                self.holidays.add(datetime(2023, 9, 29).date())
            elif year == 2024:
                self.holidays.add(datetime(2024, 9, 17).date())

            # 從證交所獲取休市日
            try:
                twse_holidays = self.get_trading_holidays(year)
                if twse_holidays:
                    self.holidays.update(twse_holidays)
            except Exception as e:
                logger.warning(f"無法從證交所獲取{year}年休市日: {e}")

        logger.info(f"已加載 {len(self.holidays)} 個休市日")

    def get_trading_holidays(self, year):
        """獲取台灣股市休市日"""
        # 簡化版：返回常見休市日
        holidays = []
        # 可以從證交所API獲取，這裡用簡化版本
        return holidays

    def fetch_historical_data(self, stock_code, start_date, end_date):
        """獲取指定日期範圍的歷史數據"""
        max_retries = 5
        retry_delay = 3

        for attempt in range(max_retries):
            try:
                # 嘗試.TW（上市股票）
                stock = yf.Ticker(f"{stock_code}.TW")
                hist = stock.history(start=start_date, end=end_date, auto_adjust=False)

                if hist.empty:
                    # 如果.TW沒有數據，嘗試.TWO（上櫃股票）
                    stock = yf.Ticker(f"{stock_code}.TWO")
                    hist = stock.history(start=start_date, end=end_date, auto_adjust=False)
                    if hist.empty:
                        # 嘗試增加時間範圍
                        start_date = (parse(start_date) - timedelta(days=7)).strftime('%Y-%m-%d')
                        hist = stock.history(start=start_date, end=end_date, auto_adjust=False)
                        if hist.empty:
                            continue

                # 標準化數據格式
                hist = hist[['Open', 'High', 'Low', 'Close', 'Volume']]
                hist.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                return hist[-90:]  # 只返回最近90天數據
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"獲取{stock_code}歷史數據失敗: {e}")
                time.sleep(retry_delay)
        return None

    def get_nearest_trading_day(self, target_date):
        """獲取最近的一個交易日"""
        if not self.holidays:
            self.load_holidays()

        delta = timedelta(days=1)
        current_date = pd.Timestamp(target_date).date()

        # 先檢查當天是否為交易日
        if self.is_market_open(current_date):
            return current_date

        # 往前找10天
        for i in range(1, 11):
            check_date = current_date - i * delta
            if self.is_market_open(check_date):
                return check_date

        # 往後找10天
        for i in range(1, 11):
            check_date = current_date + i * delta
            if self.is_market_open(check_date):
                return check_date

        logger.error(f"無法找到{target_date}附近的交易日")
        return None

    def get_all_stocks(self, use_cache=True, force_update=False):
        """獲取所有股票清單（帶緩存功能）"""
        cache_file = "stock_list_cache.pkl"

        if not force_update and use_cache and os.path.exists(cache_file):
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < self.cache_expiry:
                try:
                    with open(cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                        if cached_data:  # 確認緩存數據有效
                            logger.info("從緩存加載股票清單")
                            return cached_data
                except Exception as e:
                    logger.error(f"讀取緩存失敗: {e}")

        logger.info("從網絡獲取最新股票清單...")
        max_retries = 2
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                # 嘗試主要來源
                twse_stocks = self.get_twse_stock_list()
                otc_stocks = self.get_otc_stock_list()

                # 如果主要來源失敗，嘗試備用來源
                if not twse_stocks or not otc_stocks:
                    logger.warning("主要來源獲取失敗，嘗試備用來源...")
                    moneydj_stocks = self.get_stock_list_from_moneydj()
                    if moneydj_stocks:
                        all_stocks = {code: name for code, name in moneydj_stocks}
                    else:
                        raise Exception("所有來源獲取失敗")
                else:
                    all_stocks = {code: name for code, name in (twse_stocks + otc_stocks)}

                # 驗證數據完整性
                if len(all_stocks) < 1000:  # 正常應該有超過1000支股票
                    raise Exception(f"獲取的股票數量不足: {len(all_stocks)}")

                # 保存到緩存
                with open(cache_file, 'wb') as f:
                    pickle.dump(all_stocks, f)

                logger.info(f"成功獲取 {len(all_stocks)} 支股票清單")
                return all_stocks

            except Exception as e:
                logger.error(f"獲取股票清單失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)

        # 如果所有嘗試都失敗，返回空字典或緩存
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    logger.warning("使用過期緩存數據")
                    return pickle.load(f)
            except:
                return {}
        return {}

    def get_twse_stock_list(self):
        """從證交所獲取上市股票清單"""
        url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'big5'

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'h4'})

            if not table:
                logger.error("無法找到上市股票清單表格")
                return []

            rows = table.find_all('tr')
            stock_list = []

            for row in rows[2:]:  # 跳過前兩行標題
                cols = row.find_all('td')
                if len(cols) < 7:
                    continue

                code_name = cols[0].text.strip().split('\u3000')  # 分割代碼和名稱
                if len(code_name) != 2:
                    continue

                code = code_name[0].strip()
                name = code_name[1].strip()

                # 檢查是否為股票 (排除ETF、權證等)
                if len(code) == 4 and code.isdigit():
                    stock_list.append([code, name])

            logger.info(f"從證交所獲取 {len(stock_list)} 支上市股票")
            return stock_list
        except Exception as e:
            logger.error(f"獲取上市股票清單失敗: {e}")
            return []

    def get_otc_stock_list(self):
        """從櫃買中心獲取上櫃股票清單"""
        url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'big5'

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'h4'})

            if not table:
                logger.error("無法找到上櫃股票清單表格")
                return []

            rows = table.find_all('tr')
            stock_list = []

            for row in rows[2:]:  # 跳過前兩行標題
                cols = row.find_all('td')
                if len(cols) < 7:
                    continue

                code_name = cols[0].text.strip().split('\u3000')  # 分割代碼和名稱
                if len(code_name) != 2:
                    continue

                code = code_name[0].strip()
                name = code_name[1].strip()

                # 檢查是否為股票 (排除ETF、權證等)
                if len(code) == 4 and code.isdigit():
                    stock_list.append([code, name])

            logger.info(f"從櫃買中心獲取 {len(stock_list)} 支上櫃股票")
            return stock_list
        except Exception as e:
            logger.error(f"獲取上櫃股票清單失敗: {e}")
            return []

    def get_market_index(self):
        """獲取主要市場指數"""
        try:
            indices = {
                '台股加權指數': '^TWII',
                '台灣50': '0050.TW',  # 台灣50 ETF
                '高股息': '0056.TW'   # 高股息ETF
            }

            market_data = {}
            for name, symbol in indices.items():
                try:
                    index = yf.Ticker(symbol)
                    hist = index.history(period='1d')

                    if not hist.empty:
                        current_price = hist.iloc[-1]['Close']
                        prev_close = hist.iloc[-1]['Open']  # 使用開盤價作為前收

                        change = current_price - prev_close
                        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

                        market_data[name] = {
                            'price': current_price,
                            'change': change,
                            'change_pct': change_pct
                        }
                except Exception as e:
                    logger.warning(f"獲取 {name} 數據失敗: {e}")
                    continue

            return market_data

        except Exception as e:
            logger.error(f"獲取市場指數失敗: {e}")
            return {}

    def get_top_gainers(self, limit=50):
        """獲取漲幅前N名股票"""
        try:
            # 從台灣證券交易所獲取當日交易數據
            url = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'

            # 解析數據 (這裡簡化處理，實際需要根據證交所API格式解析)
            # 由於證交所API可能有變化，這裡使用模擬數據作為示例

            # 獲取台股主要股票列表
            stock_list = self.get_twse_stock_list()[:100]  # 取前100支股票作為樣本

            gainers = []
            for stock_info in stock_list[:limit]:
                code = stock_info[0]
                name = stock_info[1]

                try:
                    # 獲取個股數據
                    stock = yf.Ticker(f"{code}.TW")
                    hist = stock.history(period='2d')  # 獲取最近2天數據

                    if len(hist) >= 2:
                        current_price = hist.iloc[-1]['Close']
                        prev_close = hist.iloc[-2]['Close']
                        volume = hist.iloc[-1]['Volume']

                        change_pct = ((current_price - prev_close) / prev_close) * 100

                        gainers.append({
                            'code': code,
                            'name': name,
                            'price': current_price,
                            'change_pct': change_pct,
                            'volume': volume
                        })

                except Exception as e:
                    continue

            # 按漲幅降序排序
            gainers.sort(key=lambda x: x['change_pct'], reverse=True)
            return gainers[:limit]

        except Exception as e:
            logger.error(f"獲取漲幅排行失敗: {e}")
            return []

    def get_top_losers(self, limit=50):
        """獲取跌幅前N名股票"""
        try:
            # 類似 get_top_gainers，但返回跌幅最大的股票
            gainers = self.get_top_gainers(limit=200)  # 獲取更多數據

            # 過濾出下跌的股票並按跌幅降序排列
            losers = [stock for stock in gainers if stock['change_pct'] < 0]
            losers.sort(key=lambda x: x['change_pct'])  # 升序排列（跌幅最大的在前）

            return losers[:limit]

        except Exception as e:
            logger.error(f"獲取跌幅排行失敗: {e}")
            return []

    def get_market_statistics(self):
        """獲取市場統計數據"""
        try:
            # 獲取樣本股票數據來計算統計
            stock_list = self.get_twse_stock_list()[:200]  # 取樣本

            advancing = 0
            declining = 0
            unchanged = 0
            total_volume = 0

            for stock_info in stock_list:
                code = stock_info[0]

                try:
                    stock = yf.Ticker(f"{code}.TW")
                    hist = stock.history(period='2d')

                    if len(hist) >= 2:
                        current_price = hist.iloc[-1]['Close']
                        prev_close = hist.iloc[-2]['Close']
                        volume = hist.iloc[-1]['Volume']

                        total_volume += volume

                        if current_price > prev_close:
                            advancing += 1
                        elif current_price < prev_close:
                            declining += 1
                        else:
                            unchanged += 1

                except Exception:
                    continue

            return {
                'advancing': advancing,
                'declining': declining,
                'unchanged': unchanged,
                'total_volume': total_volume,
                'total_stocks': advancing + declining + unchanged
            }

        except Exception as e:
            logger.error(f"獲取市場統計失敗: {e}")
            return {}

    def get_strong_stocks(self, limit=20):
        """獲取技術面強勢股"""
        try:
            from data.indicators import TechnicalIndicators
            from core.analyzer import StockAnalyzer

            indicators = TechnicalIndicators()
            analyzer = StockAnalyzer()

            stock_list = self.get_twse_stock_list()[:100]  # 取樣本
            strong_stocks = []

            for stock_info in stock_list:
                code = stock_info[0]
                name = stock_info[1]

                try:
                    # 獲取歷史數據
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=365)
                    hist = self.fetch_historical_data(code, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

                    if hist is not None and not hist.empty and len(hist) >= 60:
                        # 計算技術指標
                        hist_with_indicators = indicators.calculate_all_indicators(hist)

                        # 進行技術分析
                        analysis = analyzer.analyze_stock(code, hist_with_indicators)

                        if analysis and 'overall_score' in analysis:
                            score = analysis['overall_score'].get('總分', 0)

                            # 只保留評分高的股票
                            if score >= 70:
                                current_price = hist.iloc[-1]['Close']
                                prev_close = hist.iloc[-2]['Close'] if len(hist) >= 2 else current_price
                                change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0

                                strong_stocks.append({
                                    'code': code,
                                    'name': name,
                                    'score': score,
                                    'price': current_price,
                                    'change_pct': change_pct
                                })

                except Exception as e:
                    continue

            # 按評分降序排序
            strong_stocks.sort(key=lambda x: x['score'], reverse=True)
            return strong_stocks[:limit]

        except Exception as e:
            logger.error(f"獲取強勢股失敗: {e}")
            return []

    def get_stock_list_from_moneydj(self):
        """從MoneyDJ獲取股票清單 (備用數據源)"""
        url = "https://www.moneydj.com/Exchange/XQStockList.aspx"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.moneydj.com/',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')
            select = soup.find('select', {'id': 'selStock'})

            if not select:
                logger.error("無法找到MoneyDJ股票清單下拉選單")
                return []

            options = select.find_all('option')
            stock_list = []

            for opt in options:
                value = opt.get('value')
                if value and len(value) == 4 and value.isdigit():
                    stock_list.append([value, opt.text.strip()])

            logger.info(f"從MoneyDJ獲取 {len(stock_list)} 支股票")
            return stock_list
        except Exception as e:
            logger.error(f"從MoneyDJ獲取股票清單失敗: {e}")
            return []