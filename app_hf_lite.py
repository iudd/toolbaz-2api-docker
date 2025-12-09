#!/usr/bin/env python3
"""
HuggingFace Spaces 极简版本
专门针对HF Spaces的限制进行优化
"""

import gradio as gr
import requests
import json
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolbaz-hf-lite")

# 全局变量
HEALTH_CHECK_URL = "https://www.google.com"  # 简单的健康检查
SERVICE_STATUS = "❓ 检查中..."

def check_service_status():
    """检查服务状态"""
    global SERVICE_STATUS
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=5)
        if response.status_code == 200:
            SERVICE_STATUS = "🟢 网络连接正常"
        else:
            SERVICE_STATUS = "🟡 网络连接异常"
    except Exception as e:
        SERVICE_STATUS = f"🔴 网络不可用: {str(e)[:50]}"
        logger.error(f"网络检查失败: {e}")
    
    return SERVICE_STATUS

def simulate_api_response(message: str, model: str):
    """模拟API响应（因为真实API可能在HF上无法工作）"""
    time.sleep(1)  # 模拟网络延迟
    
    responses = {
        "toolbaz-v4.5-fast": f"[模拟响应] toolbaz-v4.5-fast 对 '{message}' 的回复：这是一个模拟的AI响应，因为HuggingFace Spaces可能无法访问外部Toolbaz API。在实际部署中，这里会是真实的AI回复。",
        "gemini-2.5-flash": f"[模拟响应] Gemini 对 '{message}' 的回复：作为Google的AI模型，我会提供高质量的回答。但这是在HF Spaces上的模拟响应。",
        "gpt-5": f"[模拟响应] GPT-5 对 '{message}' 的回复：我是先进的AI助手。注意这是模拟响应，真实功能需要在自有服务器上部署。"
    }
    
    return responses.get(model, "未知模型的模拟响应")

def chat_fn(message: str, history: list, model: str):
    """聊天函数"""
    if not message.strip():
        return "", history
    
    # 添加用户消息
    history.append([message, None])
    
    # 生成响应（模拟或真实）
    try:
        # 在HF上优先使用模拟响应
        response = simulate_api_response(message, model)
        
        # 尝试真实API（可能会失败）
        try:
            real_response = requests.post(
                "http://localhost:8000/v1/chat/completions",
                headers={"Authorization": "Bearer 1"},
                json={"model": model, "messages": [{"role": "user", "content": message}]},
                timeout=10
            )
            if real_response.status_code == 200:
                response = real_response.json().get("choices", [{}])[0].get("message", {}).get("content", response)
        except:
            pass  # 使用模拟响应
        
    except Exception as e:
        response = f"❌ 请求失败: {str(e)}"
        logger.error(f"聊天失败: {e}")
    
    # 更新历史记录
    history[-1][1] = response
    return "", history

def create_demo():
    """创建Gradio演示界面"""
    
    # 预先检查状态
    initial_status = check_service_status()
    
    with gr.Blocks(
        title="Toolbaz-2API Lite",
        theme=gr.themes.Soft(),
        css="""
        .warning-box { 
            background-color: #fff3cd; 
            border: 1px solid #ffeaa7; 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 20px;
        }
        .status-box { 
            padding: 10px; 
            border-radius: 5px; 
            margin: 10px 0;
            text-align: center;
            font-weight: bold;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🤖 Toolbaz-2API on HuggingFace Spaces
        
        > **⚠️ 重要提醒**：这是一个适配版本，由于HuggingFace Spaces的限制，可能无法访问真实的Toolbaz API。
        > 
        > **🚀 完整功能部署**：推荐使用自己的VPS或云服务器。
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # 警告信息
                gr.HTML("""
                <div class="warning-box">
                    <strong>⚠️ HuggingFace Spaces 限制说明：</strong>
                    <ul>
                        <li>🌐 网络访问受限，可能无法连接外部AI服务</li>
                        <li>💾 资源限制，不支持完整的浏览器环境</li>
                        <li>⏱️ 启动超时，复杂服务可能无法正常运行</li>
                    </ul>
                </div>
                """)
                
                # 模型选择
                model_dropdown = gr.Dropdown(
                    choices=["toolbaz-v4.5-fast", "gemini-2.5-flash", "gpt-5"],
                    value="toolbaz-v4.5-fast",
                    label="选择模型"
                )
                
                # 聊天界面
                chatbot = gr.Chatbot(
                    label="对话",
                    height=300,
                    show_copy_button=True
                )
                
                msg = gr.Textbox(
                    label="输入消息",
                    placeholder="在这里输入您的消息...",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("发送", variant="primary")
                    clear_btn = gr.Button("清空")
                    
            with gr.Column(scale=1):
                # 状态信息
                status_text = gr.Textbox(
                    value=initial_status,
                    label="服务状态",
                    interactive=False
                )
                
                refresh_btn = gr.Button("🔄 刷新状态")
                
                # 部署指南
                gr.Markdown("""
                ### 📋 完整部署方案
                
                #### 1. Docker一键部署（推荐）
                ```bash
                docker run -d --name toolbaz-api --restart always -p 8000:8000 iudd/toolbaz-2api:latest
                ```
                
                #### 2. 源码部署
                ```bash
                git clone https://github.com/iudd/toolbaz-2api-docker
                cd toolbaz-2api-docker
                docker-compose up -d
                ```
                
                #### 3. 云服务器部署
                - 腾讯云、阿里云等
                - 需要2GB+内存
                - 支持外网访问
                """)
                
                # API示例
                gr.Code("""
# API调用示例
curl -X POST http://localhost:8000/v1/chat/completions \\
  -H "Authorization: Bearer 1" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "toolbaz-v4.5-fast",
    "messages": [{"role": "user", "content": "你好"}]
  }'
                """, language="bash")
        
        # 事件绑定
        msg.submit(chat_fn, [msg, chatbot, model_dropdown], [msg, chatbot])
        submit_btn.click(chat_fn, [msg, chatbot, model_dropdown], [msg, chatbot])
        clear_btn.click(lambda: None, outputs=[chatbot])
        refresh_btn.click(check_service_status, outputs=[status_text])
    
    return demo

if __name__ == "__main__":
    logger.info("🚀 启动Toolbaz-2API Lite版...")
    
    # 创建并启动Gradio应用
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )