FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY stock-web-dashboard/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY stock-web-dashboard/backend/ ./backend/
COPY stock-web-dashboard/frontend/dist/ ./frontend/dist/

# 設定 PYTHONPATH
ENV PYTHONPATH=/app/backend

# 啟動
ENTRYPOINT ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]