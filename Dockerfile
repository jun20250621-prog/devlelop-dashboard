FROM python:3.11-slim

WORKDIR /app

# 複製並安裝依賴
COPY stock-web-dashboard/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製後端程式碼
COPY stock-web-dashboard/backend/ ./backend/

# 複製前端 dist
COPY stock-web-dashboard/frontend/dist/ ./frontend/dist/

# 設定 PYTHONPATH
ENV PYTHONPATH=/app/backend

# 啟動
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]