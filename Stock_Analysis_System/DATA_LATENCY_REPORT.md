# 📊 股票數據時效性報告

**生成日期**: 2026-03-09  
**系統**: Stock Analysis System v3.0

---

## ⚠️ 數據延遲確認

**結論**: 當前系統的股票數據 **不是即時的**，存在 15-20 分鐘的延遲。

---

## 🔍 延遲來源分析

### 1. 數據源問題

```python
# 當前使用: yfinance (Yahoo Finance)
ticker = yf.Ticker(f"{stock_code}.TW")
data = ticker.history(period="1d")  # 歷史數據，非即時報價
```

**Yahoo Finance 台股數據特性**:
- ✅ 免費
- ❌ 延遲 **15-20 分鐘**
- ❌ 使用 `history()` 方法獲取歷史數據
- ❌ 非串流即時報價 (Non-Real-time Quote)

### 2. 快取機制影響

```python
# 公司資訊快取: 7 天過期
if cache_file.exists():
    cached_info = pickle.load(f)
    if age_days < 7:  # 7 天內使用快取
        return cached_info
```

**影響**:
- 公司基本資訊可能使用 7 天前的數據
- 歷史價格數據也有快取

### 3. 數據類型

| 數據類型 | 當前方法 | 時效性 |
|---------|---------|--------|
| 即時報價 | ❌ 未實現 | N/A |
| 分鐘線 | ❌ 未實現 | N/A |
| 日線 (收盤價) | ✅ 支援 | 延遲 15-20 分鐘 |
| 5 日線 | ✅ 支援 | 延遲 15-20 分鐘 |
| 歷史數據 | ✅ 支援 | 延遲 15-20 分鐘 |

---

## 📍 延遲影響評估

### 市場監控命令 (`monitor`)
```python
# 獲取加權指數
taiex = yf.Ticker("^TWII")
taiex_data = taiex.history(period="1d")
# ⚠️ 延遲 15-20 分鐘
```

**影響**: 
- 看到的指數可能是 20 分鐘前的
- 無法用於盤中即時交易決策

### 個股分析命令 (`analyze`)
```python
# 獲取個股歷史數據
ticker = yf.Ticker(f"{stock_code}.TW")
hist = ticker.history(start=start_date, end=end_date)
# ⚠️ 延遲 15-20 分鐘
```

**影響**: 
- 技術指標計算基於延遲數據
- 不適合當沖交易使用
- 適合中長期投資分析

### 漲幅排行 (`top-gainers`)
```python
# 獲取近 5 日數據
data = ticker.history(period="5d")
# ⚠️ 延遲 15-20 分鐘
```

**影響**: 
- 排行榜不是即時的
- 可能錯過短期交易機會

---

## ✅ 獲取即時數據的解決方案

### 方案 1: 台灣證券交易所 API (推薦)

**優點**:
- ✅ 台股官方數據
- ✅ 延遲較低 (約 1-5 分鐘)
- ✅ 免費

**實現**:
```python
import requests

def get_realtime_twse():
    """獲取台灣證交所即時數據"""
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
    params = {
        'ex_ch': 'tse_2330.tw',  # 台積電
        'json': '1',
        'delay': '0'
    }
    response = requests.get(url, params=params)
    return response.json()
```

### 方案 2: Alpha Vantage API

**優點**:
- ✅ 即時數據
- ✅ 支援多種市場

**缺點**:
- ❌ 免費版有請求限制 (5 requests/min)
- ❌ 台股支援有限

**實現**:
```python
import requests

def get_alphavantage_data(symbol, api_key):
    """Alpha Vantage 即時報價"""
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    return response.json()
```

### 方案 3: FinMind API (台股專用 - 推薦)

**優點**:
- ✅ 專注台股市場
- ✅ 免費開放
- ✅ 數據較完整

**實現**:
```python
import requests

def get_finmind_data(stock_id):
    """FinMind 台股數據"""
    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        'dataset': 'TaiwanStockPrice',
        'data_id': stock_id,
        'start_date': '2026-03-09',
        'token': ''  # 免費使用，有限制
    }
    response = requests.get(url, params=params)
    return response.json()
```

### 方案 4: Fugle API (富果 API)

**優點**:
- ✅ 台股專業數據商
- ✅ 延遲低 (< 1 分鐘)
- ✅ 支援即時報價、技術指標

**缺點**:
- ❌ 需要付費 (有免費額度)
- ❌ 需要申請 API Key

**實現**:
```python
from fugle_realtime import RestClient

def get_fugle_data(api_key):
    """Fugle 即時報價"""
    client = RestClient(api_key=api_key)
    stock = client.stock.intraday.quote(symbol='2330')
    return stock
```

### 方案 5: WebSocket 即時串流 (最即時)

**優點**:
- ✅ 真正即時 (< 1 秒)
- ✅ 推送式更新

**缺點**:
- ❌ 實現複雜
- ❌ 通常需要付費

---

## 🎯 建議改進方案

### 短期改進 (立即可行)

1. **降低快取時間**
```python
# 修改 fetcher.py
if age_days < 1:  # 改為 1 天過期
    return cached_info
```

2. **添加數據時間戳顯示**
```python
print(f"📊 數據時間: {data.index[-1]} (延遲約 15-20 分鐘)")
```

3. **清除快取命令**
```bash
# 添加新命令
python main.py clear-cache
```

### 中期改進 (建議實現)

1. **整合台灣證交所 API**
   - 實現即時報價功能
   - 延遲降至 1-5 分鐘

2. **整合 FinMind API**
   - 完整台股數據
   - 基本面資料更準確

3. **雙數據源策略**
   - 歷史分析: Yahoo Finance (免費)
   - 即時報價: TWSE API (免費)

### 長期改進 (進階功能)

1. **付費 API 整合**
   - Fugle API (富果)
   - 券商 API

2. **WebSocket 即時推送**
   - 真正即時報價
   - 適合當沖交易

3. **混合數據源架構**
   - 自動切換最佳數據源
   - 失敗容錯機制

---

## 💡 當前系統適用場景

### ✅ 適合使用
- ✅ 中長期投資分析
- ✅ 技術指標回測
- ✅ 歷史數據研究
- ✅ 每日收盤後分析
- ✅ 策略回測驗證

### ❌ 不適合使用
- ❌ 當沖交易 (Day Trading)
- ❌ 即時盤中決策
- ❌ 高頻交易 (HFT)
- ❌ 秒級交易策略
- ❌ 搶開盤/收盤

---

## 📝 改進計劃

### Phase 1: 立即改進 (本週)
- [ ] 添加數據時間戳顯示
- [ ] 降低快取過期時間至 1 天
- [ ] 添加清除快取命令
- [ ] 更新文檔說明數據延遲

### Phase 2: 短期改進 (1 個月內)
- [ ] 整合台灣證交所 API
- [ ] 實現即時報價模組
- [ ] 添加數據源切換功能
- [ ] 實現數據源降級策略

### Phase 3: 中期改進 (3 個月內)
- [ ] 整合 FinMind API
- [ ] 實現多數據源架構
- [ ] 添加數據品質監控
- [ ] 實現自動數據源選擇

---

## 🔗 參考資源

### 免費數據源
- **台灣證券交易所**: https://mis.twse.com.tw/
- **FinMind**: https://finmindtrade.com/
- **Yahoo Finance**: https://finance.yahoo.com/

### 付費數據源
- **Fugle 富果**: https://www.fugle.tw/
- **XQ 全球贏家**: https://www.xq.com.tw/
- **台灣證券集保**: https://www.tdcc.com.tw/

---

## 📊 結論

**當前狀態**: 數據延遲 15-20 分鐘，不適合即時交易決策

**建議行動**:
1. ✅ 立即在 UI 顯示數據延遲警告
2. ✅ 整合台灣證交所 API 降低延遲
3. ✅ 實現雙數據源架構

**最終目標**: 實現 < 1 分鐘延遲的即時報價系統

---

**報告生成**: 2026-03-09  
**版本**: 1.0  
**狀態**: ✅ 已確認數據延遲問題
