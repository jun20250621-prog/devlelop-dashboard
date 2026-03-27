FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY backend/ ./backend/
COPY frontend/dist/ ./frontend/dist/

# 啟動 - 使用完整路徑
ENTRYPOINT ["python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]