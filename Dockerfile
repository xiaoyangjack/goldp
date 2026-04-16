# 黄金量化交易系统 Dockerfile
# Phase 3 - 部署方案

FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p data logs

# 暴露端口
EXPOSE 5555

# 设置环境变量
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5555
ENV LOG_LEVEL=INFO
ENV DATA_REFRESH_INTERVAL=60
ENV CACHE_TIMEOUT=300

# 启动命令
CMD ["python", "web_app.py"]