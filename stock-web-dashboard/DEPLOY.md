# Zeabur 部署指南

## 部署方式：Monorepo（後端 serving 前端）

這個專案設計成一個服務同時提供 API + 前端靜態檔案。

### Step 1: 建立 Zeabur 服務

1. 登入 [Zeabur Dashboard](https://dash.zeabur.com/)
2. 點擊 **Create New Service**
3. 選擇 **Deploy from GitHub**
4. 選擇 repository: `jun20250621-prog/stock-web-dashboard`
5. Branch: `phase1-frontend-refactor`

### Step 2: 設定 Build 指令

**Build Command:**
```bash
pip install -r backend/requirements.txt
```

**Start Command:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```
PYTHONUNBUFFERED=1
```

### Step 3: 部署完成

部署成功後會得到一個網域，例如：
```
https://develop-dashboard.zeabur.app
```

### 驗證運作

1. 打開網域，應該看到 React 前端
2. 測試 API: `https://develop-dashboard.zeabur.app/api/portfolio`
3. 檢查 WebSocket: `wss://develop-dashboard.zeabur.app/ws/quotes`

---

## 本地測試

```bash
cd stock-web-dashboard

# 安裝依賴
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build && cd ..

# 啟動
python -m uvicorn backend.main:app --reload
```

然後打開 http://localhost:8000