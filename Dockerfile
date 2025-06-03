# 使用官方 Python 3.9 簡化映像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製所有檔案進容器
COPY . .

# 安裝 Python 套件
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 啟動 FastAPI 應用（監聽所有 IP）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
