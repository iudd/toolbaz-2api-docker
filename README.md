---
title: Toolbaz-2API
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "latest"
dockerfile: "Dockerfile.hf"
app_file: app_hf_stable.py
pinned: false
license: apache-2.0
datasets: []
tags: []
# HF Spaces 专用配置
python_version: "3.10"
python_packages:
  - "fastapi==0.104.1"
  - "uvicorn[standard]==0.24.0"
  - "playwright==1.40.0"
  - "requests==2.31.0"
  - "loguru==0.7.2"
  - "httpx==0.25.2"
  - "pydantic==2.5.0"
  - "pydantic-settings==2.1.0"
  - "aiofiles==23.2.1"
  - "python-multipart==0.0.6"
---

# ⚠️ HuggingFace Spaces 部署说明

## 🚨 重要限制提醒

**HuggingFace Spaces有以下限制，可能影响此项目的正常运行：**

1. **🌐 网络访问限制**：可能无法访问外部AI网站（如Toolbaz）
2. **💾 资源限制**：Playwright浏览器需要较多内存，可能超过HF限制
3. **⏱️ 启动超时**：浏览器初始化可能超过HF的启动时间限制

## 🔧 推荐解决方案

如果遇到问题，建议：
1. 使用自己的VPS/云服务器部署
2. 使用GitHub Codespaces
3. 使用支持更多资源的平台

## 📋 HF Spaces 部署步骤

### 方案A：直接部署（有限制）
1. 创建新的HF Space
2. 选择Gradio SDK
3. 上传代码（包括app_hf.py）
4. 设置app_file为app_hf.py
5. 等待部署完成

### 方案B：自建后端 + HF前端（推荐）
1. 在自己的VPS上部署后端API
2. 在HF Spaces上部署前端界面
3. 配置跨域访问

### 方案C：GitHub Codespaces
1. 使用GitHub提供的免费云环境
2. 完整功能支持
3. 可以长时间运行

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

## 📝 项目说明

这是一个将Toolbaz网页服务转换为标准OpenAI API格式的Docker应用。

### 🚀 主要特性
- 🔄 将Toolbaz网页转换为OpenAI兼容API
- 🐳 Docker容器化部署
- 🌊 支持流式响应
- 🛡️ 内置速率限制和错误处理
- 📊 完整的监控和日志系统

### 📋 技术栈
- **后端**: FastAPI + Python 3.10+
- **浏览器自动化**: Playwright
- **部署**: Docker
- **API格式**: OpenAI兼容

### 🎯 支持的模型
- `toolbaz-v4.5-fast`
- `gemini-2.5-flash`
- `gemini-2.5-pro` 
- `claude-sonnet-4`
- `gpt-5`
- `grok-4-fast`

### 📖 使用方法

部署完成后，您可以通过以下方式访问：

1. **Web界面**: 直接访问Space主页
2. **API端点**: `POST /v1/chat/completions`
3. **模型列表**: `GET /v1/models`

### 🔑 API密钥
默认使用 `Bearer 1` 作为API密钥。

### 📝 示例请求
```bash
curl -X POST https://your-space.hf.space/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 1" \
  -d '{
    "model": "toolbaz-v4.5-fast",
    "messages": [
      {"role": "user", "content": "你好！"}
    ]
  }'
```