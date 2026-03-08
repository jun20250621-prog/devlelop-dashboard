# -*- coding: utf-8 -*-
"""
工具函數模組
Utility Functions Module

通用工具函數和輔助方法
"""

import os
import re
import json
import logging
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataUtils:
    """數據處理工具"""

    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """安全轉換為浮點數"""
        try:
            if isinstance(value, str):
                # 移除逗號和空格
                value = value.replace(',', '').replace(' ', '').strip()
                # 處理百分比
                if value.endswith('%'):
                    return float(value[:-1]) / 100.0
                # 處理特殊字符
                if value in ['-', '--', 'N/A', 'null', '']:
                    return default
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """安全轉換為整數"""
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace(' ', '').strip()
                if value in ['-', '--', 'N/A', 'null', '']:
                    return default
            return int(float(value))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_str(value: Any, default: str = "") -> str:
        """安全轉換為字串"""
        try:
            if value is None:
                return default
            return str(value).strip()
        except Exception:
            return default

    @staticmethod
    def format_number(value: Union[int, float], decimals: int = 2) -> str:
        """格式化數字"""
        try:
            if isinstance(value, (int, float)):
                if decimals == 0:
                    return f"{value:,.0f}"
                else:
                    return f"{value:,.{decimals}f}"
            return str(value)
        except Exception:
            return str(value)

    @staticmethod
    def format_percentage(value: Union[int, float], decimals: int = 2) -> str:
        """格式化百分比"""
        try:
            if isinstance(value, (int, float)):
                return f"{value:.{decimals}f}%"
            return str(value)
        except Exception:
            return str(value)

    @staticmethod
    def format_currency(value: Union[int, float], currency: str = "NT$") -> str:
        """格式化貨幣"""
        try:
            if isinstance(value, (int, float)):
                return f"{currency}{value:,.0f}"
            return str(value)
        except Exception:
            return str(value)

    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """計算百分比變化"""
        try:
            if old_value == 0:
                return 0.0 if new_value == 0 else (1.0 if new_value > 0 else -1.0)
            return (new_value - old_value) / abs(old_value)
        except Exception:
            return 0.0

    @staticmethod
    def calculate_moving_average(data: List[float], window: int) -> List[float]:
        """計算移動平均"""
        try:
            if len(data) < window:
                return []
            return pd.Series(data).rolling(window=window).mean().tolist()
        except Exception:
            return []

    @staticmethod
    def normalize_data(data: List[float]) -> List[float]:
        """數據標準化"""
        try:
            if not data:
                return []
            data_array = np.array(data)
            min_val = np.min(data_array)
            max_val = np.max(data_array)
            if max_val == min_val:
                return [0.5] * len(data)
            return ((data_array - min_val) / (max_val - min_val)).tolist()
        except Exception:
            return data

    @staticmethod
    def calculate_volatility(data: List[float], window: int = 20) -> float:
        """計算波動率"""
        try:
            if len(data) < window:
                return 0.0
            returns = pd.Series(data).pct_change().dropna()
            return returns.tail(window).std() * np.sqrt(252)  # 年化波動率
        except Exception:
            return 0.0

    @staticmethod
    def find_peaks_valleys(data: List[float], threshold: float = 0.05) -> Tuple[List[int], List[int]]:
        """尋找波峰和波谷"""
        try:
            peaks = []
            valleys = []

            for i in range(1, len(data) - 1):
                if data[i] > data[i-1] and data[i] > data[i+1]:
                    # 檢查是否為顯著波峰
                    if data[i] > data[i-1] * (1 + threshold):
                        peaks.append(i)
                elif data[i] < data[i-1] and data[i] < data[i+1]:
                    # 檢查是否為顯著波谷
                    if data[i] < data[i-1] * (1 - threshold):
                        valleys.append(i)

            return peaks, valleys
        except Exception:
            return [], []


class DateTimeUtils:
    """日期時間工具"""

    @staticmethod
    def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
        """解析日期字串"""
        if formats is None:
            formats = [
                '%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y',
                '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S',
                '%d/%m/%Y', '%m-%d-%Y'
            ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
        """格式化日期"""
        try:
            return date.strftime(format_str)
        except Exception:
            return str(date)

    @staticmethod
    def get_business_days(start_date: datetime, end_date: datetime) -> int:
        """計算工作日數"""
        try:
            # 簡化的工作日計算（不考慮假日）
            days = (end_date - start_date).days
            weeks = days // 7
            remaining_days = days % 7

            # 減去週末
            business_days = weeks * 5
            start_weekday = start_date.weekday()  # 0=Monday, 6=Sunday

            for i in range(remaining_days):
                weekday = (start_weekday + i) % 7
                if weekday < 5:  # Monday to Friday
                    business_days += 1

            return business_days
        except Exception:
            return 0

    @staticmethod
    def add_business_days(date: datetime, days: int) -> datetime:
        """增加工作日"""
        try:
            current_date = date
            added_days = 0

            while added_days < abs(days):
                current_date += timedelta(days=1 if days > 0 else -1)
                if current_date.weekday() < 5:  # Monday to Friday
                    added_days += 1

            return current_date
        except Exception:
            return date

    @staticmethod
    def is_market_open(current_time: datetime = None) -> bool:
        """檢查市場是否開盤"""
        if current_time is None:
            current_time = datetime.now()

        # 台灣股市交易時間：週一至週五 09:00-13:30
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday
        if weekday >= 5:  # 週末
            return False

        market_open = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
        market_close = current_time.replace(hour=13, minute=30, second=0, microsecond=0)

        return market_open <= current_time <= market_close


class FileUtils:
    """檔案處理工具"""

    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> bool:
        """確保目錄存在"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"建立目錄失敗: {path}, 錯誤: {e}")
            return False

    @staticmethod
    def get_file_size(path: Union[str, Path]) -> int:
        """獲取檔案大小（位元組）"""
        try:
            return Path(path).stat().st_size
        except Exception:
            return 0

    @staticmethod
    def calculate_directory_size(path: Union[str, Path]) -> int:
        """計算目錄大小"""
        try:
            total_size = 0
            for file_path in Path(path).rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception:
            return 0

    @staticmethod
    def clean_old_files(directory: Union[str, Path], days: int = 7) -> int:
        """清理舊檔案"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0

            for file_path in Path(directory).rglob('*'):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1

            logger.info(f"清理了 {deleted_count} 個舊檔案")
            return deleted_count
        except Exception as e:
            logger.error(f"清理舊檔案失敗: {e}")
            return 0

    @staticmethod
    def get_file_hash(path: Union[str, Path], algorithm: str = 'md5') -> str:
        """計算檔案雜湊值"""
        try:
            hash_func = hashlib.new(algorithm)
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception:
            return ""

    @staticmethod
    def safe_file_write(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
        """安全寫入檔案（先寫入臨時檔案再重新命名）"""
        try:
            path = Path(path)
            temp_path = path.with_suffix('.tmp')

            # 寫入臨時檔案
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(content)

            # 重新命名
            temp_path.replace(path)
            return True
        except Exception as e:
            logger.error(f"安全寫入檔案失敗: {path}, 錯誤: {e}")
            return False


class CacheUtils:
    """快取工具"""

    def __init__(self, cache_dir: Union[str, Path] = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, *args, **kwargs) -> str:
        """生成快取鍵"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_cache_path(self, key: str) -> Path:
        """獲取快取檔案路徑"""
        return self.cache_dir / f"{key}.pkl"

    def set_cache(self, key: str, data: Any, expiry_days: int = 1) -> bool:
        """設定快取"""
        try:
            cache_path = self.get_cache_path(key)
            cache_data = {
                'data': data,
                'timestamp': datetime.now(),
                'expiry_days': expiry_days
            }

            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)

            return True
        except Exception as e:
            logger.error(f"設定快取失敗: {key}, 錯誤: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """獲取快取"""
        try:
            cache_path = self.get_cache_path(key)
            if not cache_path.exists():
                return None

            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)

            # 檢查過期
            timestamp = cache_data.get('timestamp')
            expiry_days = cache_data.get('expiry_days', 1)

            if datetime.now() - timestamp > timedelta(days=expiry_days):
                cache_path.unlink()  # 刪除過期快取
                return None

            return cache_data.get('data')

        except Exception as e:
            logger.error(f"獲取快取失敗: {key}, 錯誤: {e}")
            return None

    def clear_cache(self, pattern: str = "*") -> int:
        """清理快取"""
        try:
            deleted_count = 0
            for cache_file in self.cache_dir.glob(f"{pattern}.pkl"):
                cache_file.unlink()
                deleted_count += 1

            logger.info(f"清理了 {deleted_count} 個快取檔案")
            return deleted_count
        except Exception as e:
            logger.error(f"清理快取失敗: {e}")
            return 0

    def get_cache_size(self) -> int:
        """獲取快取大小"""
        return FileUtils.calculate_directory_size(self.cache_dir)

    def cleanup_expired_cache(self) -> int:
        """清理過期快取"""
        try:
            deleted_count = 0
            now = datetime.now()

            for cache_file in self.cache_dir.glob("*.pkl"):
                try:
                    with open(cache_file, 'rb') as f:
                        cache_data = pickle.load(f)

                    timestamp = cache_data.get('timestamp')
                    expiry_days = cache_data.get('expiry_days', 1)

                    if now - timestamp > timedelta(days=expiry_days):
                        cache_file.unlink()
                        deleted_count += 1

                except Exception:
                    # 刪除損壞的快取檔案
                    cache_file.unlink()
                    deleted_count += 1

            logger.info(f"清理了 {deleted_count} 個過期快取檔案")
            return deleted_count
        except Exception as e:
            logger.error(f"清理過期快取失敗: {e}")
            return 0


class ValidationUtils:
    """驗證工具"""

    @staticmethod
    def validate_stock_code(code: str) -> bool:
        """驗證股票代碼"""
        # 台灣股票代碼規則：4-6位數字
        if not isinstance(code, str):
            return False
        return bool(re.match(r'^\d{4,6}$', code.strip()))

    @staticmethod
    def validate_email(email: str) -> bool:
        """驗證電子郵件"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def validate_url(url: str) -> bool:
        """驗證 URL"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url.strip()))

    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """驗證日期範圍"""
        try:
            start = DateTimeUtils.parse_date(start_date)
            end = DateTimeUtils.parse_date(end_date)

            if not start or not end:
                return False

            return start <= end
        except Exception:
            return False

    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: Union[int, float] = None,
                             max_val: Union[int, float] = None) -> bool:
        """驗證數值範圍"""
        try:
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True
        except Exception:
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理檔案名稱"""
        # 移除或替換無效字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # 移除前後空格和點
        filename = filename.strip(' .')

        # 確保不為空
        if not filename:
            filename = "unnamed_file"

        # 限制長度
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext

        return filename


class MathUtils:
    """數學工具"""

    @staticmethod
    def round_to_significant_digits(value: float, digits: int = 3) -> float:
        """四捨五入到有效位數"""
        try:
            if value == 0:
                return 0.0
            return round(value, digits - int(np.floor(np.log10(abs(value)))) - 1)
        except Exception:
            return value

    @staticmethod
    def calculate_compound_growth(initial: float, final: float, periods: int) -> float:
        """計算複合成長率"""
        try:
            if initial <= 0 or periods <= 0:
                return 0.0
            return (final / initial) ** (1 / periods) - 1
        except Exception:
            return 0.0

    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """計算夏普比率"""
        try:
            if not returns:
                return 0.0

            returns_array = np.array(returns)
            excess_returns = returns_array - risk_free_rate / 252  # 日化無風險利率

            if np.std(excess_returns) == 0:
                return 0.0

            return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        except Exception:
            return 0.0

    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> float:
        """計算最大回撤"""
        try:
            if not prices:
                return 0.0

            prices_array = np.array(prices)
            cumulative = np.maximum.accumulate(prices_array)
            drawdown = (prices_array - cumulative) / cumulative
            return abs(np.min(drawdown))
        except Exception:
            return 0.0

    @staticmethod
    def calculate_correlation(x: List[float], y: List[float]) -> float:
        """計算相關係數"""
        try:
            if len(x) != len(y) or len(x) < 2:
                return 0.0
            return np.corrcoef(x, y)[0, 1]
        except Exception:
            return 0.0


class StringUtils:
    """字串處理工具"""

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """截斷文字"""
        try:
            if len(text) <= max_length:
                return text
            return text[:max_length - len(suffix)] + suffix
        except Exception:
            return text

    @staticmethod
    def remove_html_tags(text: str) -> str:
        """移除 HTML 標籤"""
        try:
            import re
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text)
        except Exception:
            return text

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """標準化空白字符"""
        try:
            import re
            # 將多個空白字符替換為單個空格
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception:
            return text

    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """從文字中提取數字"""
        try:
            import re
            numbers = re.findall(r'-?\d+\.?\d*', text)
            return [float(num) for num in numbers]
        except Exception:
            return []

    @staticmethod
    def format_table(data: List[Dict[str, Any]], headers: List[str] = None) -> str:
        """格式化表格"""
        try:
            if not data:
                return "無數據"

            if headers is None:
                headers = list(data[0].keys())

            # 計算每列寬度
            col_widths = {}
            for header in headers:
                col_widths[header] = len(str(header))

            for row in data:
                for header in headers:
                    value = str(row.get(header, ''))
                    col_widths[header] = max(col_widths[header], len(value))

            # 建立表格
            lines = []

            # 表頭
            header_line = " | ".join(str(header).ljust(col_widths[header]) for header in headers)
            lines.append(header_line)
            lines.append("-" * len(header_line))

            # 數據行
            for row in data:
                row_line = " | ".join(str(row.get(header, '')).ljust(col_widths[header]) for header in headers)
                lines.append(row_line)

            return "\n".join(lines)

        except Exception:
            return str(data)