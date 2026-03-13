#!/usr/bin/env python3
"""
HuggingFace Spaces 版本的 Toolbaz-2API
使用Gradio界面替代FastAPI，更适合HF环境.加模型3.13
"""

import gradio as gr
import requests
import json
import os
import logging
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolbaz-hf")

class ToolbazHFInterface:
    def __init__(self):
        self.api_base = os.environ.get("API_BASE_URL", "http://localhost:8000")
        self.api_key = os.environ.get("API_KEY", "1")
        self.models = [
            "toolbaz-v4.5-fast",
            "gemini-2.5-flash",
            "gemini-3-flash", 
            "gemini-3.1-flash-lite",
            "gemini-2.5-pro",
            "claude-sonnet-4",
            "gpt-5",
            "gpt-5.2",
            "grok-4-fast"
        ]
    
    def get_models(self):
        """获取可用模型列表"""
        try:
            response = requests.get(f"{self.api_base}/v1/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model.get("id", "unknown") for model in data.get("data", [])]
            else:
                logger.warning(f"获取模型失败: {response.status_code}")
                return self.models
        except Exception as e:
            logger.error(f"获取模型异常: {e}")
            return self.models
    
    def chat_completion(self, message: str, model: str, history: List):
        """聊天完成接口"""
        try:
            # 构建请求
            messages = []
            for user_msg, assistant_msg in history:
                messages.append({"role": "user", "content": user_msg})
                if assistant_msg:
                    messages.append({"role": "assistant", "content": assistant_msg})
            
            messages.append({"role": "user", "content": message})
            
            # 发送请求
            response = requests.post(
                f"{self.api_base}/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False  # HF环境暂不支持流式
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content
            else:
                error_msg = f"API错误: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return f"❌ {error_msg}"
                
        except requests.exceptions.Timeout:
            return "❌ 请求超时，可能是网络问题或服务未启动"
        except Exception as e:
            logger.error(f"聊天完成异常: {e}")
            return f"❌ 请求失败: {str(e)}"
    
    def health_check(self):
        """健康检查"""
        try:
            response = requests.get(f"{self.api_base}/v1/models", timeout=5)
            if response.status_code == 200:
                return "✅ 服务正常运行"
            else:
                return f"⚠️ 服务异常: HTTP {response.status_code}"
        except Exception as e:
            return f"❌ 服务不可用: {str(e)}"

# 创建接口实例
interface = ToolbazHFInterface()

def create_demo():
    """创建Gradio演示界面"""
    
    with gr.Blocks(
        title="Toolbaz-2API",
        theme=gr.themes.Soft(),
        css="""
        .main-container { max-width: 800px; margin: 0 auto; }
        .status-box { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .error { background-color: #ffcccc; color: #cc0000; }
        .success { background-color: #ccffcc; color: #006600; }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🤖 Toolbaz-2API on HuggingFace Spaces
        
        > **⚠️ 注意**：由于HuggingFace Spaces的限制，此版本可能无法完全正常工作。
        > 
        > 推荐使用自己的服务器部署以获得完整功能。
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                model_dropdown = gr.Dropdown(
                    choices=interface.models,
                    value="toolbaz-v4.5-fast",
                    label="选择模型"
                )
                
                chatbot = gr.Chatbot(
                    label="对话",
                    height=400,
                    show_copy_button=True
                )
                
                msg = gr.Textbox(
                    label="输入消息",
                    placeholder="在这里输入您的消息...",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("发送", variant="primary")
                    clear_btn = gr.Button("清空对话")
                    
            with gr.Column(scale=1):
                gr.Markdown("### 📊 服务状态")
                status_text = gr.Textbox(
                    value=interface.health_check(),
                    label="健康检查",
                    interactive=False
                )
                
                refresh_btn = gr.Button("🔄 刷新状态")
                
                gr.Markdown("### 🔗 API信息")
                gr.Code(f"""
API端点: {interface.api_base}/v1/chat/completions
API密钥: {interface.api_key}
模型列表: {len(interface.models)}个
                """, language="text")
                
                gr.Markdown("### 📝 使用说明")
                gr.Markdown("""
                1. 选择模型
                2. 输入消息
                3. 点击发送
                4. 查看回复
                
                **注意**：如果遇到错误，可能是：
                - 后端服务未启动
                - 网络访问受限
                - 资源不足
                """)
        
        # 事件处理
        def respond(message, history, model):
            if not message.strip():
                return "", history
            
            # 添加用户消息
            history.append([message, None])
            
            # 调用API
            response = interface.chat_completion(message, model, history[:-1])
            
            # 添加助手回复
            history[-1][1] = response
            
            return "", history
        
        def refresh_status():
            return interface.health_check()
        
        def clear_history():
            return None, []
        
        # 绑定事件
        msg.submit(respond, [msg, chatbot, model_dropdown], [msg, chatbot])
        submit_btn.click(respond, [msg, chatbot, model_dropdown], [msg, chatbot])
        clear_btn.click(clear_history, outputs=[chatbot])
        refresh_btn.click(refresh_status, outputs=[status_text])
        
        # 页面加载时刷新状态
        demo.load(refresh_status, outputs=[status_text])
    
    return demo

if __name__ == "__main__":
    # 创建并启动Gradio应用
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )
