# 云端微信跟圈 SaaS - Docker 镜像
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8765

# 设置环境变量
ENV PORT=8765
ENV HOST=0.0.0.0
ENV DB_PATH=/app/data/weichat_sync.db

# 启动服务
CMD ["python", "backend/main.py"]
