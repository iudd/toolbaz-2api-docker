---
title: Toolbaz-2API Docker
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "latest"
app_file: main.py
pinned: false
license: apache-2.0
datasets: []
tags: []
---

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