#!/usr/bin/env python3
"""
HuggingFace Spaces 最稳定版本
避免Playwright问题，提供基本的演示功能
"""

import sys
import os
import logging
import asyncio
import json
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolbaz-hf-stable")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 启动 Toolbaz-2API HF稳定版...")
    # 不初始化Playwright，避免崩溃
    logger.info("✅ 稳定版启动完成（无浏览器）")
    yield
    logger.info("🔄 应用关闭")

app = FastAPI(title="Toolbaz-2API Stable", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 稳定版HTML页面
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toolbaz-2API 稳定版</title>
    <style>
        :root { --bg: #121212; --panel: #1E1E1E; --text: #E0E0E0; --primary: #00ff9d; --border: #333; --warning: #ffa500; --success: #4CAF50; --error: #ff4444; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: var(--bg); 
            color: var(--text); 
            margin: 0; 
            padding: 20px; 
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: var(--primary); margin: 0; }
        .header p { color: #888; margin-top: 5px; }
        .status-bar { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: var(--panel); 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px;
            border: 1px solid var(--border);
        }
        .status-item { display: flex; align-items: center; gap: 10px; }
        .status-indicator { 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            background: var(--success); 
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        .main-content { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        @media (max-width: 768px) {
            .main-content { grid-template-columns: 1fr; }
        }
        
        .chat-panel { 
            background: var(--panel); 
            padding: 20px; 
            border-radius: 8px; 
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            height: 600px;
        }
        .chat-header { margin-bottom: 15px; }
        .chat-container { 
            background: #000; 
            border: 1px solid var(--border); 
            border-radius: 8px; 
            padding: 15px; 
            flex: 1;
            overflow-y: auto; 
            margin-bottom: 15px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .msg { 
            margin-bottom: 15px; 
            padding: 12px; 
            border-radius: 8px; 
            max-width: 80%; 
            word-wrap: break-word;
        }
        .msg.user { 
            background: linear-gradient(135deg, #2196F3, #1976D2); 
            margin-left: auto; 
            text-align: right;
        }
        .msg.ai { 
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d); 
            border: 1px solid #444;
        }
        .msg.warning {
            background: linear-gradient(135deg, #5a2a1a, #8a4a2a);
            border: 1px solid #864;
        }
        .msg .model-tag { 
            font-size: 11px; 
            color: #888; 
            margin-top: 5px; 
            font-weight: bold;
        }
        
        .input-group { 
            display: flex; 
            gap: 10px; 
            margin-bottom: 15px;
        }
        .input-group input, .input-group select, .input-group button { 
            background: #333; 
            border: 1px solid #444; 
            color: #fff; 
            padding: 12px; 
            border-radius: 6px; 
            font-family: inherit;
        }
        .input-group button { 
            background: var(--primary); 
            color: #000; 
            font-weight: bold; 
            cursor: pointer; 
            border: none;
            min-width: 80px;
        }
        .input-group button:hover { opacity: 0.9; }
        
        .info-panel { 
            display: flex; 
            flex-direction: column; 
            gap: 20px; 
        }
        .info-section { 
            background: var(--panel); 
            padding: 20px; 
            border-radius: 8px; 
            border: 1px solid var(--border);
        }
        .info-section h3 { 
            color: var(--primary); 
            margin-top: 0; 
            margin-bottom: 15px;
        }
        .code-block { 
            background: #1a1a1a; 
            border: 1px solid var(--border); 
            padding: 15px; 
            border-radius: 6px; 
            overflow-x: auto; 
            font-family: 'Courier New', monospace;
            font-size: 12px;
            margin-top: 10px;
        }
        .badge { 
            display: inline-block; 
            padding: 4px 8px; 
            background: var(--warning); 
            color: #000; 
            border-radius: 4px; 
            font-size: 11px; 
            font-weight: bold;
            margin-left: 10px;
        }
        .badge.success { background: var(--success); }
        
        .status-info {
            background: #1a1a1a;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 12px;
        }
        .feature-list { list-style: none; padding: 0; margin: 10px 0; }
        .feature-list li { 
            padding: 8px 0; 
            border-bottom: 1px solid #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .feature-list li:last-child { border-bottom: none; }
        .feature-icon { color: var(--primary); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Toolbaz-2API 稳定版</h1>
            <p>专为HuggingFace Spaces优化的稳定版本</p>
        </div>

        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator"></div>
                <span>🟢 服务正常运行</span>
                <span class="badge success">稳定版</span>
            </div>
            <div class="status-item">
                <button onclick="showInfo()" style="padding: 5px 10px; font-size: 12px;">使用说明</button>
            </div>
        </div>

        <div class="main-content">
            <div class="chat-panel">
                <div class="chat-header">
                    <h3>💬 AI对话演示</h3>
                    <div class="input-group">
                        <select id="modelSelect">
                            <option value="toolbaz-v4.5-fast">toolbaz-v4.5-fast</option>
                            <option value="gemini-2.5-flash">gemini-2.5-flash</option>
                            <option value="gemini-2.5-pro">gemini-2.5-pro</option>
                            <option value="claude-sonnet-4">claude-sonnet-4</option>
                            <option value="gpt-5">gpt-5</option>
                            <option value="grok-4-fast">grok-4-fast</option>
                        </select>
                    </div>
                </div>
                
                <div class="chat-container" id="chatBox">
                    <div class="msg ai">
                        <div>🤖 欢迎使用Toolbaz-2API稳定版！</div>
                        <div style="margin-top: 10px; font-size: 13px;">
                            这是专为HuggingFace Spaces优化的稳定版本。<br>
                            由于HF环境的限制，本版本提供高质量的模拟响应展示完整功能。
                        </div>
                        <div class="model-tag">系统消息</div>
                    </div>
                </div>
                
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="输入消息体验功能..." style="flex: 1;">
                    <button onclick="sendMessage()" id="sendBtn">发送</button>
                    <button onclick="clearChat()">清空</button>
                </div>
            </div>

            <div class="info-panel">
                <div class="info-section">
                    <h3>📋 完整部署方案</h3>
                    <div class="code-block">
# Docker 一键部署
docker run -d --name toolbaz-api \\
  --restart always \\
  -p 8000:8000 \\
  iudd/toolbaz-2api:latest
                    </div>
                    <div class="code-block">
# 源码部署
git clone https://github.com/iudd/toolbaz-2api-docker
cd toolbaz-2api-docker
docker-compose up -d
                    </div>
                </div>

                <div class="info-section">
                    <h3>🔧 HF环境说明</h3>
                    <div class="status-info">
                        <div>⚠️ HuggingFace Spaces限制：</div>
                        <ul style="margin-top: 10px; padding-left: 20px;">
                            <li>浏览器资源限制</li>
                            <li>网络访问限制</li>
                            <li>内存限制（2GB）</li>
                            <li>启动超时（30分钟）</li>
                        </ul>
                        <div style="margin-top: 10px;">💡 完整功能需自有服务器部署</div>
                    </div>
                </div>

                <div class="info-section">
                    <h3>✨ 核心特性</h3>
                    <ul class="feature-list">
                        <li><span class="feature-icon">🔄</span> OpenAI API完全兼容</li>
                        <li><span class="feature-icon">🌊</span> 流式响应支持</li>
                        <li><span class="feature-icon">🤖</span> 6个AI模型支持</li>
                        <li><span class="feature-icon">📊</span> 使用统计显示</li>
                        <li><span class="feature-icon">🛡️</span> 错误自动处理</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 模拟响应生成
        const mockResponses = {
            'toolbaz-v4.5-fast': (msg) => `[Toolbaz v4.5 Fast] 您好！我收到了您的消息："${msg}"。这是通过Toolbaz-2API服务处理的回复。在真实部署环境中，这里将是来自Toolbaz网站的真实AI响应。\\n\\n本稳定版专为HuggingFace Spaces优化，避免浏览器崩溃问题。`,
            'gemini-2.5-flash': (msg) => `[Gemini 2.5 Flash] 我理解您的问题："${msg}"。作为Google的快速响应模型，我致力于提供简洁而准确的回答。\\n\\n当前运行在HuggingFace Spaces演示环境中。要获得完整的Gemini体验，请按照右侧指南在您自己的服务器上部署。`,
            'gemini-2.5-pro': (msg) => `[Gemini 2.5 Pro] 您的问题是："${msg}"。我会深入分析并给出详细的回答。作为Google的高级模型，我能够处理复杂的查询和推理任务。\\n\\n请注意：这是在HuggingFace Spaces上的演示版本。完整功能需要在自有服务器部署后才能实现。`,
            'claude-sonnet-4': (msg) => `[Claude Sonnet 4] 我收到了您的消息："${msg}"。我是Anthropic开发的Claude模型，专注于有用、无害且诚实的对话。\\n\\n当前运行在HuggingFace Spaces环境中。要体验完整的Claude功能，请参考部署指南在您的服务器上运行。`,
            'gpt-5': (msg) => `[GPT-5] 您的消息是："${msg}"。作为OpenAI的最新模型，我可以处理各种复杂的任务，从代码生成到创意写作。\\n\\n注意：这是演示环境。完整的GPT-5功能需要通过Toolbaz-2API在您自己的服务器上部署才能使用。`,
            'grok-4-fast': (msg) => `[Grok 4 Fast] 您说了："${msg}"。我是xAI的Grok模型，以实时信息和独特视角著称。\\n\\n当前在HuggingFace Spaces演示中运行。完整的Grok体验需要私有部署，请查看右侧的部署说明。`
        };
        
        // 发送消息
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const chatBox = document.getElementById('chatBox');
            const sendBtn = document.getElementById('sendBtn');
            const modelSelect = document.getElementById('modelSelect');
            
            const message = input.value.trim();
            if (!message) return;
            
            // 禁用输入
            sendBtn.disabled = true;
            sendBtn.textContent = '生成中...';
            input.value = '';
            
            // 添加用户消息
            const userMsg = document.createElement('div');
            userMsg.className = 'msg user';
            userMsg.innerHTML = `<div>${escapeHtml(message)}</div><div class="model-tag">用户</div>`;
            chatBox.appendChild(userMsg);
            
            // 添加AI消息占位
            const aiMsg = document.createElement('div');
            aiMsg.className = 'msg ai';
            aiMsg.innerHTML = '<div>🤔 正在生成回复...</div>';
            chatBox.appendChild(aiMsg);
            
            chatBox.scrollTop = chatBox.scrollHeight;
            
            // 模拟延迟和响应
            setTimeout(() => {
                const model = modelSelect.value;
                const response = mockResponses[model](message);
                
                // 计算token
                const promptTokens = message.split(' ').length * 1.3;
                const completionTokens = response.split(' ').length * 1.3;
                const totalTokens = Math.round(promptTokens + completionTokens);
                
                aiMsg.innerHTML = `
                    <div>${response}</div>
                    <div class="model-tag">${model}</div>
                    <div style="font-size: 11px; color: #666; margin-top: 5px;">
                        Tokens: ${totalTokens} (${Math.round(promptTokens)}+${Math.round(completionTokens)})
                    </div>
                `;
                
                sendBtn.disabled = false;
                sendBtn.textContent = '发送';
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 1500);
        }
        
        // 清空聊天
        function clearChat() {
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML = `
                <div class="msg ai">
                    <div>🤖 对话已清空，可以开始新的对话了。</div>
                    <div class="model-tag">系统消息</div>
                </div>
            `;
        }
        
        // 显示使用说明
        function showInfo() {
            alert('这是专为HuggingFace Spaces优化的稳定版本。\\n\\n要获得真实的AI功能，请：\\n1. 使用自己的服务器部署\\n2. 或者等待我们解决HF环境限制\\n\\n当前提供高质量的模拟响应展示完整功能。');
        }
        
        // HTML转义
        function escapeHtml(text) {
            const map = {
                '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
        
        // 回车发送
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_PAGE

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "🟢 服务正常运行",
        "success": True,
        "version": "v3.1.0",
        "environment": "HuggingFace Spaces - 稳定版",
        "note": "稳定版，避免浏览器崩溃问题"
    }

@app.post("/v1/chat/completions")
async def stable_chat_completions(request: Request):
    """稳定版聊天完成接口，提供高质量模拟响应"""
    try:
        data = await request.json()
        model = data.get("model", "toolbaz-v4.5-fast")
        messages = data.get("messages", [])
        stream = data.get("stream", False)
        
        # 获取最后一条用户消息
        user_message = "Hello"
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "Hello")
                break
        
        # 生成高质量的模拟响应
        mock_responses = {
            "toolbaz-v4.5-fast": f"[Toolbaz v4.5 Fast] 您好！我收到了您的消息：'{user_message}'。这是通过Toolbaz-2API服务处理的回复。在真实部署环境中，这里将是来自Toolbaz网站的真实AI响应。\n\n本稳定版专为HuggingFace Spaces优化，避免浏览器崩溃问题。",
            "gemini-2.5-flash": f"[Gemini 2.5 Flash] 我理解您的问题：'{user_message}'。作为Google的快速响应模型，我致力于提供简洁而准确的回答。\n\n当前运行在HuggingFace Spaces演示环境中。要获得完整的Gemini体验，请按照右侧指南在您自己的服务器上部署。",
            "gemini-2.5-pro": f"[Gemini 2.5 Pro] 您的问题是：'{user_message}'。我会深入分析并给出详细的回答。作为Google的高级模型，我能够处理复杂的查询和推理任务。\n\n请注意：这是在HuggingFace Spaces上的演示版本。完整功能需要在自有服务器部署后才能实现。",
            "claude-sonnet-4": f"[Claude Sonnet 4] 我收到了您的消息：'{user_message}'。我是Anthropic开发的Claude模型，专注于有用、无害且诚实的对话。\n\n当前运行在HuggingFace Spaces环境中。要体验完整的Claude功能，请参考部署指南在您的服务器上运行。",
            "gpt-5": f"[GPT-5] 您的消息是：'{user_message}'。作为OpenAI的最新模型，我可以处理各种复杂的任务，从代码生成到创意写作。\n\n注意：这是演示环境。完整的GPT-5功能需要通过Toolbaz-2API在您自己的服务器上部署才能使用。",
            "grok-4-fast": f"[Grok 4 Fast] 您说了：'{user_message}'。我是xAI的Grok模型，以实时信息和独特视角著称。\n\n当前在HuggingFace Spaces演示中运行。完整的Grok体验需要私有部署，请查看右侧的部署说明。"
        }
        
        response_content = mock_responses.get(model, f"[AI模型] 收到消息：'{user_message}'。这是模拟响应。完整功能需要在自有服务器部署。")
        
        # 计算token
        prompt_tokens = len(user_message.split()) * 2
        completion_tokens = len(response_content.split()) * 2
        total_tokens = prompt_tokens + completion_tokens
        
        # 构建标准OpenAI响应
        response_data = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }
        
        if stream:
            # 模拟流式响应
            async def generate_stream():
                yield "data: " + json.dumps({
                    "id": response_data["id"],
                    "object": "chat.completion.chunk",
                    "created": response_data["created"],
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {"role": "assistant", "content": ""}
                    }]
                }) + "\n\n"
                
                # 模拟打字效果
                words = response_content.split()
                for i, word in enumerate(words):
                    chunk_content = " ".join(words[:i+1])
                    if i < len(words) - 1:
                        chunk_content += " "
                    
                    yield "data: " + json.dumps({
                        "id": response_data["id"],
                        "object": "chat.completion.chunk",
                        "created": response_data["created"],
                        "model": model,
                        "choices": [{
                            "index": 0,
                            "delta": {"content": word + (" " if i < len(words) - 1 else "")}
                        }]
                    }) + "\n\n"
                    await asyncio.sleep(0.1)
                
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(generate_stream(), media_type="text/plain")
        else:
            return JSONResponse(response_data)
            
    except Exception as e:
        logger.error(f"聊天完成错误: {e}")
        return JSONResponse({"error": f"处理失败: {str(e)}"}, status_code=500)

@app.get("/v1/models")
async def list_models():
    """返回可用模型列表"""
    return {
        "object": "list",
        "data": [
            {"id": "toolbaz-v4.5-fast", "object": "model", "created": int(time.time()), "owned_by": "toolbaz"},
            {"id": "gemini-2.5-flash", "object": "model", "created": int(time.time()), "owned_by": "google"},
            {"id": "gemini-2.5-pro", "object": "model", "created": int(time.time()), "owned_by": "google"},
            {"id": "claude-sonnet-4", "object": "model", "created": int(time.time()), "owned_by": "anthropic"},
            {"id": "gpt-5", "object": "model", "created": int(time.time()), "owned_by": "openai"},
            {"id": "grok-4-fast", "object": "model", "created": int(time.time()), "owned_by": "xai"}
        ]
    }

if __name__ == "__main__":
    logger.info("🚀 启动Toolbaz-2API HF稳定版...")
    import uvicorn
    # 确保使用HF期望的7860端口
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")