#!/usr/bin/env python3
"""
HuggingFace Spaces 极简稳定版本
使用纯HTML+JavaScript，避免Gradio依赖问题
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import requests
import time
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolbaz-hf-simple")

app = FastAPI(title="Toolbaz-2API HF Simple")

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML页面
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toolbaz-2API on HuggingFace Spaces</title>
    <style>
        :root { --bg: #121212; --panel: #1E1E1E; --text: #E0E0E0; --primary: #00ff9d; --border: #333; --warning: #ffa500; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: var(--bg); 
            color: var(--text); 
            margin: 0; 
            padding: 20px; 
            line-height: 1.6;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        .warning-box { 
            background: var(--warning); 
            color: #000; 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 20px;
            font-weight: bold;
        }
        .panel { background: var(--panel); padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid var(--border); }
        h1, h2, h3 { color: var(--primary); margin-top: 0; }
        .status { 
            padding: 10px; 
            border-radius: 5px; 
            margin: 10px 0;
            text-align: center;
            font-weight: bold;
            background: var(--panel);
            border: 1px solid var(--border);
        }
        .chat-container { 
            background: #000; 
            border: 1px solid var(--border); 
            border-radius: 8px; 
            padding: 15px; 
            height: 300px; 
            overflow-y: auto; 
            margin-bottom: 15px;
            font-family: monospace;
            font-size: 14px;
        }
        .msg { 
            margin-bottom: 10px; 
            padding: 10px; 
            border-radius: 4px; 
            max-width: 80%; 
        }
        .msg.user { 
            background: #333; 
            margin-left: auto; 
            text-align: right;
        }
        .msg.ai { 
            background: #1a1a1a; 
            border: 1px solid #333; 
        }
        input, select, button { 
            background: #333; 
            border: 1px solid #444; 
            color: #fff; 
            padding: 10px; 
            border-radius: 4px; 
            font-family: inherit;
        }
        button { 
            background: var(--primary); 
            color: #000; 
            font-weight: bold; 
            cursor: pointer; 
            border: none;
        }
        button:hover { opacity: 0.9; }
        button:disabled { background: #555; cursor: not-allowed; }
        .input-group { display: flex; gap: 10px; margin-bottom: 15px; }
        .code-block { 
            background: #1a1a1a; 
            border: 1px solid var(--border); 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto; 
            font-family: monospace;
            font-size: 12px;
        }
        .two-column { display: flex; gap: 20px; }
        .two-column > div { flex: 1; }
        @media (max-width: 768px) {
            .two-column { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="warning-box">
            ⚠️ <strong>HuggingFace Spaces 限制说明</strong><br>
            由于HF Spaces的网络和资源限制，此版本主要用于演示和指导。
            完整功能请使用自己的服务器部署。
        </div>

        <div class="panel">
            <h1>🤖 Toolbaz-2API on HuggingFace Spaces</h1>
            <div class="status" id="status">🔍 检查服务状态...</div>
        </div>

        <div class="two-column">
            <div class="panel">
                <h2>💬 演示聊天</h2>
                
                <div class="input-group">
                    <select id="model" style="flex: 1;">
                        <option value="toolbaz-v4.5-fast">toolbaz-v4.5-fast</option>
                        <option value="gemini-2.5-flash">gemini-2.5-flash</option>
                        <option value="gpt-5">gpt-5</option>
                    </select>
                </div>
                
                <div class="chat-container" id="chatBox">
                    <div class="msg ai">🤖 欢迎使用Toolbaz-2API演示版！由于HF限制，这是模拟响应。</div>
                </div>
                
                <div class="input-group">
                    <input type="text" id="message" placeholder="输入消息..." style="flex: 1;">
                    <button onclick="sendMessage()" id="sendBtn">发送</button>
                </div>
                
                <button onclick="clearChat()" style="width: 100%; margin-top: 10px;">清空对话</button>
            </div>

            <div class="panel">
                <h2>🚀 完整部署方案</h2>
                
                <h3>1. Docker一键部署（推荐）</h3>
                <div class="code-block">docker run -d --name toolbaz-api --restart always -p 8000:8000 iudd/toolbaz-2api:latest</div>
                
                <h3>2. 源码部署</h3>
                <div class="code-block">git clone https://github.com/iudd/toolbaz-2api-docker
cd toolbaz-2api-docker
docker-compose up -d</div>
                
                <h3>3. 云服务器要求</h3>
                <ul>
                    <li>内存：2GB+</li>
                    <li>系统：Linux/Windows</li>
                    <li>网络：可访问外网</li>
                    <li>Docker：已安装</li>
                </ul>
            </div>
        </div>

        <div class="panel">
            <h2>📋 API调用示例</h2>
            <div class="code-block">
curl -X POST http://localhost:8000/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer 1" \\
  -d '{
    "model": "toolbaz-v4.5-fast",
    "messages": [{"role": "user", "content": "你好"}]
  }'
            </div>
            
            <h3>🌊 流式响应示例</h3>
            <div class="code-block">
curl -X POST http://localhost:8000/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer 1" \\
  -d '{
    "model": "toolbaz-v4.5-fast",
    "messages": [{"role": "user", "content": "写一首诗"}],
    "stream": true
  }'
            </div>
        </div>
    </div>

    <script>
        // 检查服务状态
        async function checkStatus() {
            const statusEl = document.getElementById('status');
            try {
                const response = await fetch('/health');
                const data = await response.json();
                statusEl.textContent = data.status;
                statusEl.style.background = data.success ? '#1a5f1a' : '#5f1a1a';
            } catch (error) {
                statusEl.textContent = '❌ 状态检查失败';
                statusEl.style.background = '#5f1a1a';
            }
        }

        // 发送消息
        async function sendMessage() {
            const messageEl = document.getElementById('message');
            const modelEl = document.getElementById('model');
            const chatBox = document.getElementById('chatBox');
            const sendBtn = document.getElementById('sendBtn');
            
            const message = messageEl.value.trim();
            if (!message) return;

            // 禁用发送按钮
            sendBtn.disabled = true;
            sendBtn.textContent = '发送中...';
            messageEl.value = '';

            // 添加用户消息
            const userMsg = document.createElement('div');
            userMsg.className = 'msg user';
            userMsg.textContent = message;
            chatBox.appendChild(userMsg);

            // 添加AI消息占位
            const aiMsg = document.createElement('div');
            aiMsg.className = 'msg ai';
            aiMsg.textContent = '🤔 思考中...';
            chatBox.appendChild(aiMsg);
            
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                // 尝试真实API调用
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        model: modelEl.value,
                        message: message
                    })
                });

                const data = await response.json();
                aiMsg.textContent = data.response;
            } catch (error) {
                // 模拟响应
                const mockResponses = {
                    'toolbaz-v4.5-fast': `[模拟响应] toolbaz-v4.5-fast对"${message}"的回复：这是在HF Spaces上的模拟回复。完整功能需要自有服务器部署。`,
                    'gemini-2.5-flash': `[模拟响应] Gemini对"${message}"的回复：作为Google的AI模型，我会提供高质量的回答。但这是演示版本。`,
                    'gpt-5': `[模拟响应] GPT-5对"${message}"的回复：我是先进的AI助手。完整功能请查看右侧部署指南。`
                };
                aiMsg.textContent = mockResponses[modelEl.value] || '模型响应模拟失败。';
            }

            // 恢复发送按钮
            sendBtn.disabled = false;
            sendBtn.textContent = '发送';
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // 清空聊天
        function clearChat() {
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML = '<div class="msg ai">🤖 对话已清空，可以开始新的对话了。</div>';
        }

        // 回车发送
        document.getElementById('message').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // 页面加载时检查状态
        window.onload = function() {
            checkStatus();
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_PAGE

@app.get("/health")
async def health():
    """健康检查端点"""
    try:
        # 简单的网络检查
        response = requests.get("https://www.google.com", timeout=3)
        return {
            "status": "🟢 服务正常运行" if response.status_code == 200 else "🟡 网络异常",
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "status": f"🔴 服务异常: {str(e)[:50]}",
            "success": False
        }

@app.post("/chat")
async def chat_endpoint(request: Request):
    """聊天端点"""
    try:
        data = await request.json()
        message = data.get("message", "")
        model = data.get("model", "toolbaz-v4.5-fast")
        
        # 模拟响应（在HF环境中）
        await asyncio.sleep(1)  # 模拟网络延迟
        
        responses = {
            "toolbaz-v4.5-fast": f"[HF模拟] toolbaz-v4.5-fast 对 '{message}' 的回复：由于HuggingFace Spaces限制，这是模拟响应。完整功能需要自有服务器部署。",
            "gemini-2.5-flash": f"[HF模拟] Gemini 对 '{message}' 的回复：作为Google AI的模拟响应，在实际环境中会提供更准确的回答。",
            "gpt-5": f"[HF模拟] GPT-5 对 '{message}' 的回复：这是模拟的GPT-5响应。完整功能请参考右侧部署指南。"
        }
        
        return {"response": responses.get(model, "未知模型的模拟响应。")}
        
    except Exception as e:
        logger.error(f"聊天端点错误: {e}")
        return {"response": f"❌ 处理失败: {str(e)}"}

if __name__ == "__main__":
    import asyncio
    logger.info("🚀 启动Toolbaz-2API HF Simple版本...")
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")