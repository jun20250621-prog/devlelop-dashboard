# 股票分析系統 (Stock Analysis System)

一個功能完整的台灣股市分析工具，提供技術分析、基本面分析、投資組合管理和策略回測等功能。

## 功能特色

### 📊 技術分析
- 完整的技術指標計算 (MA, RSI, MACD, KD, 布林通道, ATR, 乖離率等)
- 趨勢分析和形態識別
- 支撐阻力位階分析
- 動量和波動率分析

### 🏢 基本面分析
- 財務比率分析 (ROE, ROA, 毛利率, 營益率等)
- 公司基本資料查詢
- 本益比、股價淨值比分析
- 股息殖利率分析

### 📈 投資組合管理
- 持倉追蹤和績效分析
- 風險評估和分散度分析
- 再平衡建議
- 交易記錄管理

### 🎯 策略回測
- 多種內建交易策略
- 歷史資料回測
- 績效指標計算 (夏普比率、最大回撤、勝率等)
- 參數優化

### 🤖 自動化功能
- 每日市場監控
- 自動化報表生成
- Telegram 通知
- 自訂警示條件

### 📊 多元輸出
- 互動式控制台介面
- Excel 報表匯出
- Telegram 機器人通知
- 圖表視覺化

## 系統架構

```
Stock_Analysis_System/
├── config/                 # 配置管理
│   └── settings.py        # 系統配置
├── data/                  # 數據層
│   ├── indicators.py      # 技術指標計算
│   └── fetcher.py         # 數據獲取
├── core/                  # 核心邏輯
│   ├── analyzer.py        # 技術分析引擎
│   ├── reporter.py        # 專業報表生成
│   ├── simulator.py       # 策略模擬器
│   ├── trade_analyzer.py  # 交易分析
│   └── strategy_analyzer.py # 策略分析
├── output/                # 輸出模組
│   ├── console.py         # 控制台輸出
│   ├── excel.py           # Excel 匯出
│   └── telegram.py        # Telegram 通知
├── utils/                 # 工具函數
│   └── helpers.py         # 通用工具
├── stock_cli.py           # CLI 介面
├── main.py               # 主程式入口
└── README.md             # 說明文件
```

## 安裝說明

### 系統需求
- Python 3.8+
- Windows/Linux/macOS
- 網路連線 (用於獲取股市資料)

### 依賴套件
```bash
pip install pandas numpy yfinance requests beautifulsoup4 matplotlib openpyxl colorama
```

### 安裝步驟
1. 複製專案
```bash
git clone https://github.com/your-repo/stock-analysis-system.git
cd stock-analysis-system
```

2. 安裝依賴
```bash
pip install -r requirements.txt
```

3. 設定配置檔案
```bash
# 編輯 config/settings.json 或使用預設配置
python main.py --help
```

## 使用方法

### 基本使用
```bash
# 啟動系統
python main.py

# 或直接使用 CLI
python stock_cli.py
```

### CLI 命令

#### 市場監控
```bash
# 監控市場概況
python stock_cli.py monitor

# 查看強勢股
python stock_cli.py strong-stocks

# 查看漲幅排行
python stock_cli.py top-gainers
```

#### 股票分析
```bash
# 分析特定股票
python stock_cli.py analyze 2330

# 基本面分析
python stock_cli.py fundamental 2330

# 生成完整報表
python stock_cli.py report 2330
```

#### 投資組合
```bash
# 查看投資組合
python stock_cli.py portfolio

# 記錄交易
python stock_cli.py trade add 2330 buy 100 500

# 分析交易記錄
python stock_cli.py trade analyze
```

#### 策略回測
```bash
# 執行策略回測
python stock_cli.py strategy backtest ma-crossover

# 優化策略參數
python stock_cli.py strategy optimize rsi

# 比較策略
python stock_cli.py strategy compare
```

#### 自動化
```bash
# 自動分析
python stock_cli.py auto daily

# 設定監控清單
python stock_cli.py watchlist add 2330 2454 2317

# 管理警示
python stock_cli.py alert set 2330 price_above 600
```

### 配置設定

編輯 `config/settings.json` 來自訂系統行為：

```json
{
  "api": {
    "yahoo_finance_timeout": 30,
    "max_retries": 3
  },
  "analysis": {
    "min_volume_threshold": 1000000,
    "trend_strength_threshold": 0.6
  },
  "telegram": {
    "bot_token": "your_bot_token",
    "chat_id": "your_chat_id",
    "enabled": true
  }
}
```

## 資料來源

- **Yahoo Finance**: 歷史股價資料
- **Goodinfo.tw**: 基本面財務資料
- **台灣證券交易所**: 股票基本資料
- **公開資訊觀測站**: 財務報表資料

## 技術指標說明

### 趨勢指標
- **MA (移動平均)**: 5日、10日、20日、60日
- **MACD**: 快線12日、慢線26日、訊號線9日
- **趨勢強度**: 綜合多項指標評估

### 動量指標
- **RSI (相對強弱指標)**: 14日週期
- **KD (隨機指標)**: K值14日、D值3日
- **威廉指標**: 14日週期

### 波動率指標
- **布林通道**: 20日週期、2倍標準差
- **ATR (平均真實波幅)**: 14日週期
- **乖離率**: 6日、12日、24日

## 投資策略

### 內建策略
1. **MA 穿越策略**: 金叉買入、死叉賣出
2. **RSI 策略**: 超買超賣反轉
3. **MACD 策略**: 訊號線穿越
4. **均線糾結策略**: 多空均線排列
5. **量價策略**: 配合成交量確認

### 自訂策略
支援透過配置檔案定義自訂策略邏輯。

## 風險管理

### 風險控制
- **單股持倉限制**: 預設不超過總資產20%
- **總損失限制**: 單日損失不超過總資產5%
- **止損機制**: 動態止損點設定
- **分散投資**: 建議持有5-10檔股票

### 風險指標
- **VaR (風險價值)**: 95%信心水準
- **最大回撤**: 歷史最大虧損幅度
- **夏普比率**: 風險調整後收益
- **Beta 係數**: 市場相關性

## Telegram 通知

設定 Telegram 機器人接收即時通知：

1. 建立 Telegram Bot (@BotFather)
2. 取得 bot_token 和 chat_id
3. 在配置中啟用 Telegram
4. 接收分析結果和警示通知

## 效能優化

### 快取機制
- 自動快取 API 回應資料
- 可設定快取過期時間
- 智慧清理過期快取

### 並發處理
- 多執行緒資料獲取
- 非同步任務處理
- 資源使用優化

## 故障排除

### 常見問題
1. **網路連線問題**
   - 檢查網路連線
   - 調整 API 超時設定

2. **資料獲取失敗**
   - 檢查股票代碼正確性
   - 確認資料來源可用性

3. **模組匯入錯誤**
   - 重新安裝依賴套件
   - 檢查 Python 版本相容性

### 日誌查看
```bash
# 查看應用程式日誌
tail -f logs/stock_analysis.log

# 設定詳細日誌
python main.py --log-level DEBUG
```

## 版本歷史

### v1.0.0 (2024-01-XX)
- 初始版本發佈
- 基本技術分析功能
- CLI 介面
- Excel 報表匯出

### 未來規劃
- [ ] Web 介面開發
- [ ] 機器學習預測模型
- [ ] 更多資料來源整合
- [ ] 即時資料串流
- [ ] 行動應用程式

## 授權條款

本專案採用 MIT 授權條款，詳見 LICENSE.txt

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 聯絡資訊

- 專案維護者: [您的姓名]
- Email: [您的Email]
- GitHub: [您的GitHub帳號]

## 免責聲明

本系統僅供參考，不構成任何投資建議。投資有風險，入市須謹慎。使用者應自行承擔所有投資風險和責任。