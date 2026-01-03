#!/usr/bin/env python3
"""
HuggingFace Spaces 增强版本
添加更好的超时处理、错误反馈和进度显示
"""

import sys
import os
import logging
import asyncio
from contextlib import asynccontextmanager
import time

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# 导入原始的ToolbazProvider
from app.core.config import settings
from app.providers.toolbaz_provider import ToolbazProvider

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolbaz-hf-enhanced")

provider = ToolbazProvider()

# 用于存储请求状态
request_status = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 启动 {settings.APP_NAME} - HF Spaces增强版...")
    try:
        await provider.initialize()
        logger.info("✅ ToolbazProvider初始化成功")
        yield
    except Exception as e:
        logger.error(f"❌ ToolbazProvider初始化失败: {e}")
        # 即使初始化失败，也继续运行，提供降级服务
        yield
    finally:
        logger.info("🔄 正在关闭浏览器资源...")
        try:
            await provider.close()
        except:
            pass

app = FastAPI(title="Toolbaz-2API Enhanced", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 增强版HTML页面
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toolbaz-2API 增强版</title>
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
            background: var(--warning); 
            animation: pulse 2s infinite;
        }
        .status-indicator.ready { background: var(--success); }
        .status-indicator.error { background: var(--error); }
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
        .msg.error {
            background: linear-gradient(135deg, #5a1a1a, #8a2d2d);
            border: 1px solid #844;
        }
        .msg .model-tag { 
            font-size: 11px; 
            color: #888; 
            margin-top: 5px; 
            font-weight: bold;
        }
        .msg .progress {
            margin-top: 8px;
            font-size: 11px;
            color: var(--primary);
        }
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #333;
            border-radius: 2px;
            overflow: hidden;
            margin-top: 4px;
        }
        .progress-fill {
            height: 100%;
            background: var(--primary);
            width: 0%;
            transition: width 0.3s ease;
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
        .input-group button:disabled { background: #555; cursor: not-allowed; }
        
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
        .badge.error { background: var(--error); }
        
        .status-info {
            background: #1a1a1a;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 12px;
        }
        .loading-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--primary);
            margin: 0 2px;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .loading-dot:nth-child(1) { animation-delay: -0.32s; }
        .loading-dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Toolbaz-2API 增强版</h1>
            <p>更好的超时处理、进度显示和错误反馈</p>
        </div>

        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator" id="statusIndicator"></div>
                <span id="serviceStatus">检查服务状态...</span>
                <span class="badge success" id="envBadge">增强版</span>
            </div>
            <div class="status-item">
                <button onclick="checkModels()" style="margin-right: 10px; padding: 5px 10px; font-size: 12px;">刷新模型</button>
                <button onclick="checkStatus()" style="padding: 5px 10px; font-size: 12px;">检查状态</button>
            </div>
        </div>

        <div class="main-content">
            <div class="chat-panel">
                <div class="chat-header">
                    <h3>💬 增强AI对话</h3>
                    <div class="input-group">
                        <select id="modelSelect">
                            <option value="toolbaz-v4.5-fast">toolbaz-v4.5-fast</option>
                            <option value="gemini-2.5-flash">gemini-2.5-flash</option>
                            <option value="gemini-2.5-pro">gemini-2.5-pro</option>
                            <option value="claude-sonnet-4">claude-sonnet-4</option>
                            <option value="gpt-5">gpt-5</option>
                            <option value="grok-4-fast">grok-4-fast</option>
                        </select>
                        <button onclick="toggleStream()" id="streamBtn">🌊 流式: 开</button>
                    </div>
                </div>
                
                <div class="chat-container" id="chatBox">
                    <div class="msg ai">
                        <div>🤖 欢迎使用Toolbaz-2API增强版！</div>
                        <div style="margin-top: 10px; font-size: 13px;">
                            这个版本提供了更好的进度显示和错误处理。<br>
                            如果遇到长时间等待，会显示详细的进度信息。
                        </div>
                        <div class="model-tag">系统消息</div>
                    </div>
                </div>
                
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="输入您的消息..." style="flex: 1;">
                    <button onclick="sendMessage()" id="sendBtn">发送</button>
                    <button onclick="clearChat()">清空</button>
                </div>
            </div>

            <div class="info-panel">
                <div class="info-section">
                    <h3>🔧 服务状态</h3>
                    <div id="detailedStatus">
                        <div class="status-info">
                            <div>🔄 正在检查服务状态...</div>
                        </div>
                    </div>
                </div>

                <div class="info-section">
                    <h3>📊 请求进度</h3>
                    <div id="requestProgress" style="display: none;">
                        <div class="status-info">
                            <div id="progressText">等待请求...</div>
                            <div class="progress-bar">
                                <div class="progress-fill" id="progressFill"></div>
                            </div>
                        </div>
                    </div>
                    <div id="noRequests" class="status-info">
                        <div>💤 暂无活动请求</div>
                    </div>
                </div>

                <div class="info-section">
                    <h3>⚠️ 使用提示</h3>
                    <ul style="padding-left: 20px; color: #aaa; font-size: 13px;">
                        <li>请求可能需要10-30秒时间</li>
                        <li>会显示详细的进度信息</li>
                        <li>如果超时，会显示具体原因</li>
                        <li>支持流式响应和非流式响应</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        let streamEnabled = true;
        let currentRequestId = null;
        
        // 更新进度
        function updateProgress(text, percentage) {
            const progressEl = document.getElementById('requestProgress');
            const noRequestsEl = document.getElementById('noRequests');
            const textEl = document.getElementById('progressText');
            const fillEl = document.getElementById('progressFill');
            
            progressEl.style.display = 'block';
            noRequestsEl.style.display = 'none';
            textEl.textContent = text;
            fillEl.style.width = percentage + '%';
        }
        
        // 清除进度
        function clearProgress() {
            const progressEl = document.getElementById('requestProgress');
            const noRequestsEl = document.getElementById('noRequests');
            
            progressEl.style.display = 'none';
            noRequestsEl.style.display = 'block';
        }
        
        // 检查服务状态
        async function checkStatus() {
            const statusEl = document.getElementById('serviceStatus');
            const indicatorEl = document.getElementById('statusIndicator');
            const statusInfoEl = document.getElementById('detailedStatus');
            const envBadgeEl = document.getElementById('envBadge');
            
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                if (data.success) {
                    statusEl.textContent = '🟢 服务正常运行';
                    indicatorEl.className = 'status-indicator ready';
                    envBadgeEl.textContent = '增强版';
                    envBadgeEl.className = 'badge success';
                    
                    statusInfoEl.innerHTML = `
                        <div class="status-info">
                            <div>✅ 浏览器引擎就绪</div>
                            <div>🤖 可用模型: 6个</div>
                            <div>🌐 状态: ${data.status || '正常'}</div>
                        </div>
                    `;
                } else {
                    statusEl.textContent = '🟡 服务初始化中';
                    indicatorEl.className = 'status-indicator';
                    envBadgeEl.textContent = '初始化中';
                    envBadgeEl.className = 'badge';
                    
                    statusInfoEl.innerHTML = `
                        <div class="status-info">
                            <div>⚠️ 服务启动中</div>
                            <div>🔄 正在初始化浏览器...</div>
                        </div>
                    `;
                }
            } catch (error) {
                statusEl.textContent = '🔴 服务不可用';
                indicatorEl.className = 'status-indicator error';
                envBadgeEl.textContent = '离线';
                envBadgeEl.className = 'badge error';
            }
        }
        
        // 检查模型列表
        async function checkModels() {
            try {
                const response = await fetch('/v1/models');
                const data = await response.json();
                if (data.data && data.data.length > 0) {
                    const modelList = data.data.map(m => m.id).join(', ');
                    alert(`可用模型: ${modelList}`);
                } else {
                    alert('暂无可用模型');
                }
            } catch (error) {
                alert(`获取模型失败: ${error.message}`);
            }
        }
        
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
            sendBtn.innerHTML = '<span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span>';
            input.value = '';
            
            // 生成请求ID
            currentRequestId = Date.now().toString();
            
            // 添加用户消息
            const userMsg = document.createElement('div');
            userMsg.className = 'msg user';
            userMsg.innerHTML = `<div>${escapeHtml(message)}</div><div class="model-tag">用户</div>`;
            chatBox.appendChild(userMsg);
            
            // 添加AI消息占位
            const aiMsg = document.createElement('div');
            aiMsg.className = 'msg ai';
            aiMsg.innerHTML = '<div>🤔 正在处理请求...</div>';
            chatBox.appendChild(aiMsg);
            
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try {
                updateProgress('初始化浏览器...', 10);
                
                const response = await fetch('/v1/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer 1',
                        'X-Request-ID': currentRequestId
                    },
                    body: JSON.stringify({
                        model: modelSelect.value,
                        messages: [{role: 'user', content: message}],
                        stream: streamEnabled
                    })
                });
                
                updateProgress('发送请求到API...', 30);
                
                if (streamEnabled) {
                    // 流式响应处理
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let fullText = '';
                    let lastProgressTime = Date.now();
                    
                    // 定期更新进度
                    const progressInterval = setInterval(() => {
                        const elapsed = Date.now() - lastProgressTime;
                        if (elapsed > 5000) { // 5秒无更新
                            updateProgress('等待响应中...', 50 + Math.min(20, elapsed / 1000 * 2));
                        }
                    }, 2000);
                    
                    while(true) {
                        const {done, value} = await reader.read();
                        if(done) break;
                        
                        lastProgressTime = Date.now();
                        updateProgress('接收流式响应...', 70);
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n');
                        
                        for(const line of lines) {
                            if(line.startsWith('data: ')) {
                                const data = line.slice(6);
                                if(data === '[DONE]') {
                                    updateProgress('响应完成', 100);
                                    break;
                                }
                                
                                try {
                                    const json = JSON.parse(data);
                                    const content = json.choices[0].delta.content;
                                    if(content) {
                                        fullText += content;
                                        aiMsg.innerHTML = `<div>${fullText}</div><div class="model-tag">${modelSelect.value}</div>`;
                                        chatBox.scrollTop = chatBox.scrollHeight;
                                    }
                                } catch(e) {
                                    // 忽略解析错误
                                }
                            }
                        }
                    }
                    
                    clearInterval(progressInterval);
                } else {
                    // 非流式响应处理
                    updateProgress('等待完整响应...', 60);
                    const data = await response.json();
                    
                    if (data.error) {
                        aiMsg.className = 'msg error';
                        aiMsg.innerHTML = `<div>❌ API错误: ${data.error}</div>`;
                    } else if (data.choices && data.choices[0]) {
                        updateProgress('处理响应...', 80);
                        const content = data.choices[0].message?.content || '无响应内容';
                        aiMsg.innerHTML = `<div>${content}</div><div class="model-tag">${modelSelect.value}</div>`;
                        
                        // 显示使用统计
                        if (data.usage) {
                            const usage = data.usage;
                            aiMsg.innerHTML += `<div style="font-size: 11px; color: #666; margin-top: 5px;">
                                Tokens: ${usage.total_tokens} (${usage.prompt_tokens}+${usage.completion_tokens})
                            </div>`;
                        }
                        updateProgress('响应完成', 100);
                    }
                }
                
            } catch (error) {
                aiMsg.className = 'msg error';
                aiMsg.innerHTML = `<div>❌ 请求失败: ${error.message}</div>`;
            } finally {
                // 恢复输入
                setTimeout(() => {
                    sendBtn.disabled = false;
                    sendBtn.textContent = '发送';
                    clearProgress();
                    currentRequestId = null;
                }, 1000);
                
                chatBox.scrollTop = chatBox.scrollHeight;
            }
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
        
        // 切换流式
        function toggleStream() {
            streamEnabled = !streamEnabled;
            const btn = document.getElementById('streamBtn');
            btn.textContent = `🌊 流式: ${streamEnabled ? '开' : '关'}`;
            btn.style.background = streamEnabled ? 'var(--success)' : '#555';
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
        
        // 页面加载时检查状态
        window.onload = function() {
            checkStatus();
            // 每30秒检查一次状态
            setInterval(checkStatus, 30000);
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
    """健康检查"""
    try:
        # 检查provider状态
        if hasattr(provider, 'browser_pool') and provider.browser_pool:
            return {
                "status": "🟢 服务正常运行",
                "success": True,
                "version": "v3.1.0",
                "environment": "HuggingFace Spaces - 增强版"
            }
        else:
            return {
                "status": "🟡 浏览器正在初始化",
                "success": False,
                "version": "v3.1.0",
                "environment": "HuggingFace Spaces - 初始化中"
            }
    except Exception as e:
        return {
            "status": f"🔴 服务异常: {str(e)}",
            "success": False,
            "version": "v3.1.0",
            "environment": "HuggingFace Spaces - 错误"
        }

# 增强版聊天完成接口
@app.post("/v1/chat/completions")
async def enhanced_chat_completions(request: Request):
    """增强版聊天完成接口，带更好的超时和进度处理"""
    try:
        data = await request.json()
        
        # 检查请求ID
        request_id = request.headers.get("X-Request-ID", str(int(time.time())))
        logger.info(f"🆔 处理请求 [{request_id}]: {data.get('model', 'unknown')}")
        
        # 设置超时处理
        try:
            # 使用原始provider但添加更长的超时
            result = await asyncio.wait_for(
                provider.chat_completion(data), 
                timeout=120.0  # 120秒超时
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"⏰ 请求 [{request_id}] 超时")
            return JSONResponse(
                {"error": "Request timeout. The browser may be slow or the API may be overloaded."}, 
                status_code=408
            )
        except Exception as e:
            logger.error(f"❌ 请求 [{request_id}] 失败: {e}")
            return JSONResponse(
                {"error": f"API call failed: {str(e)}. This might be due to rate limiting or network issues."}, 
                status_code=500
            )
            
    except Exception as e:
        logger.error(f"🚨 全局错误: {e}")
        return JSONResponse({"error": f"Request processing failed: {str(e)}"}, status_code=500)

@app.get("/v1/models")
async def list_models():
    """使用原始ToolbazProvider的模型列表接口"""
    return await provider.get_models()

if __name__ == "__main__":
    logger.info("🚀 启动Toolbaz-2API HF增强版...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")