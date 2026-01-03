# HF Spaces 专用 Dockerfile
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# 安装系统依赖（包括Playwright需要的核心库）
# 手动安装 Chromium 依赖，避免 playwright install-deps 的包名兼容性问题
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器（只安装chromium，不自动安装deps）
RUN python -m playwright install chromium

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /ms-playwright

USER appuser

# 暴露端口
EXPOSE 7860

# HF Spaces启动命令
CMD ["python", "main.py"]