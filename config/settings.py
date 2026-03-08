# -*- coding: utf-8 -*-
"""
配置管理模組
Configuration Management Module

系統配置和參數管理
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import configparser

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = Path(config_file)
        self.config_dir = self.config_file.parent
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 預設配置
        self.default_config = self._get_default_config()
        self.config = self.load_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """獲取預設配置"""
        return {
            # API 配置
            "api": {
                "yahoo_finance_timeout": 30,
                "goodinfo_timeout": 30,
                "twse_timeout": 30,
                "max_retries": 3,
                "retry_delay": 1.0
            },

            # 數據配置
            "data": {
                "cache_enabled": True,
                "cache_expiry_days": 1,
                "max_cache_size_mb": 100,
                "historical_data_period": "2y",
                "historical_data_interval": "1d"
            },

            # 技術指標配置
            "indicators": {
                "ma_periods": [5, 10, 20, 60],
                "rsi_period": 14,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "kd_period": 14,
                "bb_period": 20,
                "bb_std": 2.0,
                "atr_period": 14,
                "bias_periods": [6, 12, 24]
            },

            # 分析配置
            "analysis": {
                "min_volume_threshold": 1000000,  # 最小成交量
                "min_price_threshold": 10,        # 最小股價
                "max_price_threshold": 10000,     # 最大股價
                "trend_strength_threshold": 0.6,  # 趨勢強度閾值
                "signal_confidence_threshold": 0.7,  # 訊號信心閾值
                "risk_free_rate": 0.02           # 無風險利率
            },

            # 投資組合配置
            "portfolio": {
                "max_positions": 20,             # 最大持倉數
                "max_allocation_per_stock": 0.1, # 單股最大配置比例
                "rebalance_threshold": 0.05,     # 再平衡閾值
                "stop_loss_threshold": -0.1,     # 止損閾值
                "take_profit_threshold": 0.2     # 止盈閾值
            },

            # 策略配置
            "strategy": {
                "backtest_start_date": "2020-01-01",
                "backtest_end_date": "2024-12-31",
                "initial_capital": 1000000,
                "transaction_cost": 0.001425,    # 交易成本 (0.1425%)
                "benchmark_symbol": "^TWII",     # 台灣加權指數
                "min_trade_amount": 10000        # 最小交易金額
            },

            # 輸出配置
            "output": {
                "excel_enabled": True,
                "console_enabled": True,
                "telegram_enabled": False,
                "report_language": "zh-tw",
                "decimal_places": 2,
                "date_format": "%Y-%m-%d",
                "time_format": "%H:%M:%S"
            },

            # Telegram 配置
            "telegram": {
                "bot_token": "",
                "chat_id": "",
                "enabled": False,
                "daily_report_time": "18:00",
                "weekly_report_day": "friday",
                "monthly_report_day": 1
            },

            # 日誌配置
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "console_enabled": True,
                "max_file_size_mb": 10,
                "backup_count": 5,
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },

            # 系統配置
            "system": {
                "max_workers": 4,               # 最大並發工作數
                "request_timeout": 30,          # 請求超時時間
                "memory_limit_mb": 1024,        # 記憶體限制
                "temp_dir": "temp/",            # 臨時目錄
                "data_dir": "data/",            # 數據目錄
                "output_dir": "output/",        # 輸出目錄
                "cache_dir": "cache/"           # 快取目錄
            },

            # 風險管理配置
            "risk": {
                "max_daily_loss": -0.05,        # 最大日損失
                "max_total_loss": -0.2,         # 最大總損失
                "var_confidence_level": 0.95,   # VaR 信心水準
                "stress_test_scenarios": 1000,  # 壓力測試場景數
                "correlation_threshold": 0.7    # 相關性閾值
            },

            # 市場配置
            "market": {
                "trading_days_per_year": 252,   # 年交易日數
                "market_open_time": "09:00",     # 市場開盤時間
                "market_close_time": "13:30",    # 市場收盤時間
                "timezone": "Asia/Taipei",       # 時區
                "currency": "TWD"               # 貨幣
            }
        }

    def load_config(self) -> Dict[str, Any]:
        """載入配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                logger.info(f"載入配置檔案: {self.config_file}")
            else:
                user_config = {}
                logger.info("使用預設配置")

            # 合併配置
            config = self._merge_configs(self.default_config, user_config)
            return config

        except Exception as e:
            logger.error(f"載入配置失敗: {e}")
            logger.info("使用預設配置")
            return self.default_config.copy()

    def save_config(self) -> bool:
        """儲存配置"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"配置已儲存到: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"儲存配置失敗: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> bool:
        """設定配置值"""
        keys = key.split('.')
        config = self.config

        try:
            # 導航到最後一個鍵的父級
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            # 設定值
            config[keys[-1]] = value
            logger.debug(f"設定配置: {key} = {value}")
            return True

        except Exception as e:
            logger.error(f"設定配置失敗: {key} = {value}, 錯誤: {e}")
            return False

    def reset_to_default(self, section: str = None) -> bool:
        """重置為預設配置"""
        try:
            if section:
                if section in self.default_config:
                    self.config[section] = self.default_config[section].copy()
                    logger.info(f"重置配置區段: {section}")
                else:
                    logger.warning(f"配置區段不存在: {section}")
                    return False
            else:
                self.config = self.default_config.copy()
                logger.info("重置所有配置為預設值")

            return True

        except Exception as e:
            logger.error(f"重置配置失敗: {e}")
            return False

    def validate_config(self) -> List[str]:
        """驗證配置"""
        errors = []

        # 驗證 API 配置
        api_config = self.get('api', {})
        if api_config.get('yahoo_finance_timeout', 0) <= 0:
            errors.append("API 超時時間必須大於 0")
        if api_config.get('max_retries', 0) < 0:
            errors.append("最大重試次數不能為負數")

        # 驗證數據配置
        data_config = self.get('data', {})
        if data_config.get('cache_expiry_days', 0) <= 0:
            errors.append("快取過期天數必須大於 0")
        if data_config.get('max_cache_size_mb', 0) <= 0:
            errors.append("最大快取大小必須大於 0")

        # 驗證技術指標配置
        indicators_config = self.get('indicators', {})
        if not indicators_config.get('ma_periods'):
            errors.append("MA 週期不能為空")
        if indicators_config.get('rsi_period', 0) <= 0:
            errors.append("RSI 週期必須大於 0")

        # 驗證分析配置
        analysis_config = self.get('analysis', {})
        if analysis_config.get('min_price_threshold', 0) <= 0:
            errors.append("最小股價閾值必須大於 0")
        if analysis_config.get('max_price_threshold', 0) <= analysis_config.get('min_price_threshold', 0):
            errors.append("最大股價閾值必須大於最小股價閾值")

        # 驗證投資組合配置
        portfolio_config = self.get('portfolio', {})
        if portfolio_config.get('max_positions', 0) <= 0:
            errors.append("最大持倉數必須大於 0")
        if not (0 < portfolio_config.get('max_allocation_per_stock', 0) <= 1):
            errors.append("單股最大配置比例必須在 0-1 之間")

        # 驗證策略配置
        strategy_config = self.get('strategy', {})
        if strategy_config.get('initial_capital', 0) <= 0:
            errors.append("初始資本必須大於 0")
        if not (0 <= strategy_config.get('transaction_cost', 0) <= 1):
            errors.append("交易成本必須在 0-1 之間")

        # 驗證風險管理配置
        risk_config = self.get('risk', {})
        if not (-1 <= risk_config.get('max_daily_loss', 0) <= 0):
            errors.append("最大日損失必須在 -1 到 0 之間")
        if not (0 < risk_config.get('var_confidence_level', 0) < 1):
            errors.append("VaR 信心水準必須在 0-1 之間")

        return errors

    def export_config(self, file_path: str) -> bool:
        """匯出配置"""
        try:
            export_path = Path(file_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            logger.info(f"配置已匯出到: {export_path}")
            return True

        except Exception as e:
            logger.error(f"匯出配置失敗: {e}")
            return False

    def import_config(self, file_path: str) -> bool:
        """匯入配置"""
        try:
            import_path = Path(file_path)
            if not import_path.exists():
                logger.error(f"配置檔案不存在: {import_path}")
                return False

            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # 驗證匯入的配置
            self.config = self._merge_configs(self.default_config, imported_config)
            logger.info(f"配置已從 {import_path} 匯入")
            return True

        except Exception as e:
            logger.error(f"匯入配置失敗: {e}")
            return False

    def _merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """合併配置"""
        merged = base_config.copy()

        for key, value in override_config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def get_api_config(self) -> Dict[str, Any]:
        """獲取 API 配置"""
        return self.get('api', {})

    def get_data_config(self) -> Dict[str, Any]:
        """獲取數據配置"""
        return self.get('data', {})

    def get_indicators_config(self) -> Dict[str, Any]:
        """獲取技術指標配置"""
        return self.get('indicators', {})

    def get_analysis_config(self) -> Dict[str, Any]:
        """獲取分析配置"""
        return self.get('analysis', {})

    def get_portfolio_config(self) -> Dict[str, Any]:
        """獲取投資組合配置"""
        return self.get('portfolio', {})

    def get_strategy_config(self) -> Dict[str, Any]:
        """獲取策略配置"""
        return self.get('strategy', {})

    def get_output_config(self) -> Dict[str, Any]:
        """獲取輸出配置"""
        return self.get('output', {})

    def get_telegram_config(self) -> Dict[str, Any]:
        """獲取 Telegram 配置"""
        return self.get('telegram', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """獲取日誌配置"""
        return self.get('logging', {})

    def get_system_config(self) -> Dict[str, Any]:
        """獲取系統配置"""
        return self.get('system', {})

    def get_risk_config(self) -> Dict[str, Any]:
        """獲取風險管理配置"""
        return self.get('risk', {})

    def get_market_config(self) -> Dict[str, Any]:
        """獲取市場配置"""
        return self.get('market', {})

    def update_telegram_config(self, bot_token: str = None, chat_id: str = None, enabled: bool = None) -> bool:
        """更新 Telegram 配置"""
        try:
            if bot_token is not None:
                self.set('telegram.bot_token', bot_token)
            if chat_id is not None:
                self.set('telegram.chat_id', chat_id)
            if enabled is not None:
                self.set('telegram.enabled', enabled)
                self.set('output.telegram_enabled', enabled)

            logger.info("Telegram 配置已更新")
            return True

        except Exception as e:
            logger.error(f"更新 Telegram 配置失敗: {e}")
            return False

    def enable_feature(self, feature: str, enabled: bool = True) -> bool:
        """啟用/停用功能"""
        feature_map = {
            'excel': 'output.excel_enabled',
            'console': 'output.console_enabled',
            'telegram': 'output.telegram_enabled',
            'cache': 'data.cache_enabled',
            'logging': 'logging.file_enabled'
        }

        if feature not in feature_map:
            logger.error(f"未知功能: {feature}")
            return False

        return self.set(feature_map[feature], enabled)

    def get_cache_dir(self) -> Path:
        """獲取快取目錄"""
        cache_dir = self.get('system.cache_dir', 'cache/')
        return Path(cache_dir)

    def get_data_dir(self) -> Path:
        """獲取數據目錄"""
        data_dir = self.get('system.data_dir', 'data/')
        return Path(data_dir)

    def get_output_dir(self) -> Path:
        """獲取輸出目錄"""
        output_dir = self.get('system.output_dir', 'output/')
        return Path(output_dir)

    def get_temp_dir(self) -> Path:
        """獲取臨時目錄"""
        temp_dir = self.get('system.temp_dir', 'temp/')
        return Path(temp_dir)

    def ensure_directories(self) -> bool:
        """確保必要目錄存在"""
        try:
            directories = [
                self.get_cache_dir(),
                self.get_data_dir(),
                self.get_output_dir(),
                self.get_temp_dir()
            ]

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)

            logger.info("所有必要目錄已建立")
            return True

        except Exception as e:
            logger.error(f"建立目錄失敗: {e}")
            return False

    def get_log_file_path(self) -> Path:
        """獲取日誌檔案路徑"""
        log_dir = self.get_output_dir() / "logs"
        log_dir.mkdir(exist_ok=True)
        return log_dir / "stock_analysis.log"

    def create_backup(self) -> bool:
        """建立配置備份"""
        try:
            backup_dir = self.config_dir / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = json.dumps({}, default=str).replace('"', '').replace('{', '').replace('}', '').replace(':', '').replace(',', '')
            backup_file = backup_dir / f"config_backup_{timestamp}.json"

            return self.export_config(str(backup_file))

        except Exception as e:
            logger.error(f"建立配置備份失敗: {e}")
            return False

    def list_backups(self) -> List[Path]:
        """列出所有備份檔案"""
        try:
            backup_dir = self.config_dir / "backups"
            if not backup_dir.exists():
                return []

            return list(backup_dir.glob("config_backup_*.json"))

        except Exception as e:
            logger.error(f"列出備份檔案失敗: {e}")
            return []

    def restore_backup(self, backup_file: str) -> bool:
        """從備份還原配置"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"備份檔案不存在: {backup_path}")
                return False

            return self.import_config(str(backup_path))

        except Exception as e:
            logger.error(f"還原備份失敗: {e}")
            return False


class ConfigValidator:
    """配置驗證器"""

    @staticmethod
    def validate_api_config(config: Dict[str, Any]) -> List[str]:
        """驗證 API 配置"""
        errors = []

        timeout = config.get('yahoo_finance_timeout', 30)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("yahoo_finance_timeout 必須是正數")

        max_retries = config.get('max_retries', 3)
        if not isinstance(max_retries, int) or max_retries < 0:
            errors.append("max_retries 必須是非負整數")

        return errors

    @staticmethod
    def validate_data_config(config: Dict[str, Any]) -> List[str]:
        """驗證數據配置"""
        errors = []

        cache_expiry = config.get('cache_expiry_days', 1)
        if not isinstance(cache_expiry, (int, float)) or cache_expiry <= 0:
            errors.append("cache_expiry_days 必須是正數")

        max_cache_size = config.get('max_cache_size_mb', 100)
        if not isinstance(max_cache_size, (int, float)) or max_cache_size <= 0:
            errors.append("max_cache_size_mb 必須是正數")

        return errors

    @staticmethod
    def validate_indicators_config(config: Dict[str, Any]) -> List[str]:
        """驗證技術指標配置"""
        errors = []

        ma_periods = config.get('ma_periods', [5, 10, 20, 60])
        if not isinstance(ma_periods, list) or not all(isinstance(p, int) and p > 0 for p in ma_periods):
            errors.append("ma_periods 必須是正整數列表")

        rsi_period = config.get('rsi_period', 14)
        if not isinstance(rsi_period, int) or rsi_period <= 0:
            errors.append("rsi_period 必須是正整數")

        return errors

    @staticmethod
    def validate_portfolio_config(config: Dict[str, Any]) -> List[str]:
        """驗證投資組合配置"""
        errors = []

        max_positions = config.get('max_positions', 20)
        if not isinstance(max_positions, int) or max_positions <= 0:
            errors.append("max_positions 必須是正整數")

        max_allocation = config.get('max_allocation_per_stock', 0.1)
        if not isinstance(max_allocation, (int, float)) or not (0 < max_allocation <= 1):
            errors.append("max_allocation_per_stock 必須在 0-1 之間")

        return errors