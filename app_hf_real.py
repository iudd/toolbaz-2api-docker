#!/usr/bin/env python3
"""
HuggingFace Spaces 真实功能版本
直接接入原始ToolbazProvider，提供真实AI功能
"""

import sys
import os
import logging
import asyncio
from contextlib import asynccontextmanager

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 导入原始的ToolbazProvider
from app.core.config import settings
from app.providers.toolbaz_provider import ToolbazProvider

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolbaz-hf-real")

provider = ToolbazProvider()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 启动 {settings.APP_NAME} - HF Spaces真实功能版...")
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

app = FastAPI(title="Toolbaz-2API Real", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML页面（真实功能版）
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toolbaz-2API 真实功能版</title>
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Toolbaz-2API 真实功能版</h1>
            <p>直接接入原始Toolbaz API，提供真实的AI响应</p>
        </div>

        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator" id="statusIndicator"></div>
                <span id="serviceStatus">检查服务状态...</span>
                <span class="badge success" id="envBadge">真实API</span>
            </div>
            <div class="status-item">
                <button onclick="installBrowsers()" style="margin-right: 10px; padding: 5px 10px; font-size: 12px; background: var(--warning);">📦 安装浏览器</button>
                <button onclick="checkModels()" style="margin-right: 10px; padding: 5px 10px; font-size: 12px;">刷新模型</button>
                <button onclick="checkStatus()" style="padding: 5px 10px; font-size: 12px;">检查状态</button>
            </div>
        </div>

        <div class="main-content">
            <div class="chat-panel">
                <div class="chat-header">
                    <h3>💬 真实AI对话</h3>
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
                        <div>🤖 欢迎使用Toolbaz-2API真实功能版！</div>
                        <div style="margin-top: 10px; font-size: 13px;">
                            这个版本直接接入原始Toolbaz API，提供真实的AI响应。<br>
                            如果看到这个消息，说明系统正在初始化浏览器引擎...
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
                    <h3>🌐 API调用</h3>
                    <div class="code-block">
curl -X POST /v1/chat/completions \\
  -H "Authorization: Bearer 1" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "toolbaz-v4.5-fast",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": true
  }'
                    </div>
                </div>

                <div class="info-section">
                    <h3>⚠️ 使用说明</h3>
                    <ul style="padding-left: 20px; color: #aaa;">
                        <li>首次使用需要启动浏览器引擎（可能需要1-2分钟）</li>
                        <li>真实API调用受网站速率限制（约4-5次/分钟）</li>
                        <li>如果遇到错误，请等待后重试</li>
                        <li>HF环境可能有限制，建议自有服务器部署</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        let streamEnabled = true;
        let isRealAPI = false;
        
        // 检查服务状态
        async function checkStatus() {
            const statusEl = document.getElementById('serviceStatus');
            const indicatorEl = document.getElementById('statusIndicator');
            const statusInfoEl = document.getElementById('detailedStatus');
            const envBadgeEl = document.getElementById('envBadge');
            
            try {
                // 检查健康状态
                const healthResponse = await fetch('/health');
                const healthData = await healthResponse.json();
                
                // 检查模型列表（验证真实API）
                const modelsResponse = await fetch('/v1/models');
                const modelsData = await modelsResponse.json();
                
                if (modelsData.data && modelsData.data.length > 0) {
                    // 真实API可用
                    isRealAPI = true;
                    statusEl.textContent = '🟢 真实API正常运行';
                    indicatorEl.className = 'status-indicator ready';
                    envBadgeEl.textContent = '真实API';
                    envBadgeEl.className = 'badge success';
                    
                    statusInfoEl.innerHTML = `
                        <div class="status-info">
                            <div>✅ 真实Toolbaz API可用</div>
                            <div>🤖 可用模型: ${modelsData.data.length}个</div>
                            <div>🌐 状态: ${healthData.status || '正常'}</div>
                        </div>
                    `;
                } else {
                    // 降级到模拟模式
                    isRealAPI = false;
                    statusEl.textContent = '🟡 模拟模式运行';
                    indicatorEl.className = 'status-indicator';
                    envBadgeEl.textContent = '模拟模式';
                    envBadgeEl.className = 'badge';
                    
                    statusInfoEl.innerHTML = `
                        <div class="status-info">
                            <div>⚠️ 真实API不可用</div>
                            <div>🔄 使用模拟响应</div>
                            <div>💡 建议自有服务器部署</div>
                        </div>
                    `;
                }
                
            } catch (error) {
                // 错误状态
                isRealAPI = false;
                statusEl.textContent = '🔴 服务检查失败';
                indicatorEl.className = 'status-indicator error';
                envBadgeEl.textContent = '离线模式';
                envBadgeEl.className = 'badge error';
                
                statusInfoEl.innerHTML = `
                    <div class="status-info">
                        <div>❌ 服务不可用</div>
                        <div>📝 错误: ${error.message}</div>
                    </div>
                `;
            }
        }
        
        // 安装浏览器
        async function installBrowsers() {
            const installBtn = event.target;
            const originalText = installBtn.textContent;
            
            installBtn.disabled = true;
            installBtn.textContent = '📦 安装中...';
            
            try {
                const response = await fetch('/install-browsers', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('✅ 浏览器安装成功！');
                    // 重新检查状态
                    setTimeout(checkStatus, 2000);
                } else {
                    alert(`❌ 安装失败: ${result.message}`);
                }
            } catch (error) {
                alert(`❌ 安装异常: ${error.message}`);
            } finally {
                installBtn.disabled = false;
                installBtn.textContent = originalText;
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
            sendBtn.textContent = '发送中...';
            input.value = '';
            
            // 添加用户消息
            const userMsg = document.createElement('div');
            userMsg.className = 'msg user';
            userMsg.innerHTML = `<div>${escapeHtml(message)}</div><div class="model-tag">用户</div>`;
            chatBox.appendChild(userMsg);
            
            // 添加AI消息占位
            const aiMsg = document.createElement('div');
            aiMsg.className = 'msg ai';
            aiMsg.innerHTML = '<div>🤔 正在调用真实API...</div>';
            chatBox.appendChild(aiMsg);
            
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try {
                // 首先尝试标准OpenAI API路径
                let response = await fetch('/v1/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer 1'
                    },
                    body: JSON.stringify({
                        model: modelSelect.value,
                        messages: [{role: 'user', content: message}],
                        stream: streamEnabled
                    })
                });
                
                // 如果404，尝试备用路径
                if (response.status === 404) {
                    response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message: message,
                            model: modelSelect.value
                        })
                    });
                }
                
                if (streamEnabled) {
                    // 流式响应处理
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let fullText = '';
                    
                    while(true) {
                        const {done, value} = await reader.read();
                        if(done) break;
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n');
                        
                        for(const line of lines) {
                            if(line.startsWith('data: ')) {
                                const data = line.slice(6);
                                if(data === '[DONE]') break;
                                
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
                } else {
                    // 非流式响应处理
                    const data = await response.json();
                    
                    if (data.error) {
                        aiMsg.className = 'msg error';
                        aiMsg.innerHTML = `<div>❌ API错误: ${data.error}</div>`;
                    } else if (data.choices && data.choices[0]) {
                        const content = data.choices[0].message?.content || '无响应内容';
                        aiMsg.innerHTML = `<div>${content}</div><div class="model-tag">${modelSelect.value}</div>`;
                        
                        // 显示使用统计
                        if (data.usage) {
                            const usage = data.usage;
                            aiMsg.innerHTML += `<div style="font-size: 11px; color: #666; margin-top: 5px;">
                                Tokens: ${usage.total_tokens} (${usage.prompt_tokens}+${usage.completion_tokens})
                            </div>`;
                        }
                    }
                }
                
            } catch (error) {
                aiMsg.className = 'msg error';
                aiMsg.innerHTML = `<div>❌ 请求失败: ${error.message}</div>`;
            }
            
            // 恢复输入
            sendBtn.disabled = false;
            sendBtn.textContent = '发送';
            chatBox.scrollTop = chatBox.scrollHeight;
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
                "environment": "HuggingFace Spaces - 真实API"
            }
        else:
            return {
                "status": "🟡 浏览器正在初始化",
                "success": False,
                "version": "v3.1.0",
                "environment": "HuggingFace Spaces - 初始化中",
                "note": "HF环境中Playwright可能需要手动安装"
            }
    except Exception as e:
        return {
            "status": f"🔴 服务异常: {str(e)}",
            "success": False,
            "version": "v3.1.0",
            "environment": "HuggingFace Spaces - 错误"
        }

@app.post("/install-browsers")
async def install_browsers():
    """安装Playwright浏览器（仅限HF环境）"""
    try:
        import subprocess
        import sys
        
        logger.info("🔄 开始安装Playwright浏览器...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✅ Playwright浏览器安装成功")
            # 尝试重新初始化provider
            try:
                await provider.initialize()
                return {"success": True, "message": "浏览器安装成功并已初始化"}
            except Exception as e:
                return {"success": False, "message": f"浏览器安装成功但初始化失败: {str(e)}"}
        else:
            logger.error(f"❌ 浏览器安装失败: {result.stderr}")
            return {"success": False, "message": f"安装失败: {result.stderr}"}
            
    except Exception as e:
        logger.error(f"❌ 安装过程异常: {e}")
        return {"success": False, "message": f"安装异常: {str(e)}"}

# 添加一个简单的聊天端点作为备用
@app.post("/chat")
async def simple_chat(request: Request):
    """简单的聊天端点，用于测试"""
    try:
        data = await request.json()
        message = data.get("message", "")
        model = data.get("model", "toolbaz-v4.5-fast")
        
        # 如果真实API可用，使用真实API
        try:
            response = await provider.chat_completion({
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "stream": False
            })
            return response
        except Exception as e:
            # 如果真实API失败，返回说明
            return {
                "response": f"❌ 真实API不可用: {str(e)}\n\n💡 在HF环境中，Playwright浏览器可能无法正常工作。\n建议:\n1. 点击'安装浏览器'按钮\n2. 使用自有服务器部署\n3. 等待我们修复HF环境问题",
                "error": str(e)
            }
            
    except Exception as e:
        return {"error": f"请求处理失败: {str(e)}"}

# 使用原始的API端点
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """使用原始ToolbazProvider的聊天完成接口"""
    try:
        data = await request.json()
        return await provider.chat_completion(data)
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/v1/models")
async def list_models():
    """使用原始ToolbazProvider的模型列表接口"""
    return await provider.get_models()

if __name__ == "__main__":
    logger.info("🚀 启动Toolbaz-2API HF真实功能版...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")