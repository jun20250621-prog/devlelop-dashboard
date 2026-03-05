# -*- coding: utf-8 -*-
"""
主程式入口
Main Entry Point

股票分析系統主程式
"""

import sys
import logging
from pathlib import Path

# 確保可以匯入專案模組
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import ConfigManager
from stock_cli import main as cli_main

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/stock_analysis.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def setup_environment():
    """設定執行環境"""
    try:
        # 載入配置
        config = ConfigManager()

        # 確保必要目錄存在
        config.ensure_directories()

        # 設定日誌等級
        logging_config = config.get_logging_config()
        log_level = getattr(logging, logging_config.get('level', 'INFO').upper())
        logging.getLogger().setLevel(log_level)

        # 如果啟用檔案日誌，更新檔案處理器
        if logging_config.get('file_enabled', True):
            log_file = config.get_log_file_path()
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(logging_config.get('log_format')))
            logging.getLogger().addHandler(file_handler)

        logger.info("環境設定完成")
        return config

    except Exception as e:
        logger.error(f"環境設定失敗: {e}")
        sys.exit(1)


def check_dependencies():
    """檢查依賴項"""
    try:
        required_modules = [
            'pandas', 'numpy', 'yfinance', 'requests', 'bs4',
            'matplotlib', 'openpyxl', 'colorama'
        ]

        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)

        if missing_modules:
            logger.error(f"缺少必要的模組: {', '.join(missing_modules)}")
            logger.info("請執行: pip install " + " ".join(missing_modules))
            return False

        logger.info("依賴項檢查通過")
        return True

    except Exception as e:
        logger.error(f"檢查依賴項失敗: {e}")
        return False


def initialize_system():
    """初始化系統"""
    try:
        logger.info("正在初始化股票分析系統...")

        # 檢查依賴項
        if not check_dependencies():
            return False

        # 設定環境
        config = setup_environment()

        # 檢查關鍵配置
        validation_errors = config.validate_config()
        if validation_errors:
            logger.warning("配置驗證發現問題:")
            for error in validation_errors:
                logger.warning(f"  - {error}")
            logger.info("系統將使用預設配置繼續運行")

        # 檢查快取目錄
        cache_dir = config.get_cache_dir()
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"建立快取目錄: {cache_dir}")

        # 清理過期的快取檔案
        from utils.helpers import CacheUtils
        cache_utils = CacheUtils(str(cache_dir))
        expired_count = cache_utils.cleanup_expired_cache()
        if expired_count > 0:
            logger.info(f"清理了 {expired_count} 個過期快取檔案")

        logger.info("系統初始化完成")
        return True

    except Exception as e:
        logger.error(f"系統初始化失敗: {e}")
        return False


def cleanup_resources():
    """清理資源"""
    try:
        logger.info("正在清理資源...")

        # 清理臨時檔案
        config = ConfigManager()
        temp_dir = config.get_temp_dir()

        from utils.helpers import FileUtils
        if temp_dir.exists():
            deleted_count = FileUtils.clean_old_files(str(temp_dir), days=1)
            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 個臨時檔案")

        logger.info("資源清理完成")

    except Exception as e:
        logger.error(f"資源清理失敗: {e}")


def main():
    """主函數"""
    try:
        # 初始化系統
        if not initialize_system():
            logger.error("系統初始化失敗，程式結束")
            sys.exit(1)

        logger.info("=" * 50)
        logger.info("股票分析系統啟動")
        logger.info("=" * 50)

        # 啟動 CLI 介面
        try:
            cli_main()
        except KeyboardInterrupt:
            logger.info("收到中斷訊號，正在關閉...")
        except Exception as e:
            logger.error(f"CLI 執行時發生錯誤: {e}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"程式執行時發生未預期的錯誤: {e}")
        sys.exit(1)

    finally:
        # 清理資源
        cleanup_resources()

        logger.info("=" * 50)
        logger.info("股票分析系統關閉")
        logger.info("=" * 50)


if __name__ == "__main__":
    main()