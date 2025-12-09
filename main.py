import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.providers.toolbaz_provider import ToolbazProvider

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolbaz-api")

provider = ToolbazProvider()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"启动 {settings.APP_NAME}...")
    await provider.initialize()
    yield
    logger.info("正在关闭浏览器资源...")
    await provider.close()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

async def verify_key(authorization: str = Header(None)):
    if settings.API_MASTER_KEY and settings.API_MASTER_KEY != "1":
        if not authorization or authorization != f"Bearer {settings.API_MASTER_KEY}":
            raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post("/v1/chat/completions", dependencies=[Depends(verify_key)])
async def chat_completions(request: Request):
    try:
        data = await request.json()
        return await provider.chat_completion(data)
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/v1/models")
async def list_models():
    return await provider.get_models()

@app.get("/", response_class=HTMLResponse)
async def root():
    import os
    logger.info(f"🔍 调试信息：当前工作目录 = {os.getcwd()}")
    logger.info(f"🔍 调试信息：static目录是否存在 = {os.path.exists('static')}")
    logger.info(f"🔍 调试信息：static/index.html是否存在 = {os.path.exists('static/index.html')}")
    
    # 列出当前目录下的所有文件
    try:
        files = os.listdir('.')
        logger.info(f"🔍 调试信息：当前目录文件 = {files}")
    except Exception as e:
        logger.error(f"🔍 调试信息：列出文件失败 = {e}")
    
    # 首先尝试使用FastAPI的静态文件系统
    try:
        from fastapi.staticfiles import StaticFiles
        static_path = os.path.join(os.getcwd(), "static", "index.html")
        logger.info(f"🔍 调试信息：尝试读取文件路径 = {static_path}")
        
        if os.path.exists(static_path):
            with open(static_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.info("🔍 调试信息：成功读取static/index.html")
                return content
        else:
            logger.warning(f"🔍 调试信息：文件不存在 {static_path}")
    except Exception as e:
        logger.error(f"🔍 调试信息：读取文件异常 = {e}")
    
    # 返回备用页面
    logger.info("🔍 调试信息：返回备用HTML页面")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Toolbaz-2API Running</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #121212; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            .status { color: #00ff9d; font-weight: bold; }
            .endpoint { background: #1e1e1e; padding: 10px; margin: 10px 0; border-radius: 5px; }
            code { background: #333; padding: 2px 5px; border-radius: 3px; }
            .debug { background: #2a2a2a; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Toolbaz-2API 服务运行中</h1>
            <p class="status">✅ API服务已就绪</p>
            
            <div class="debug">
                <strong>🔍 调试信息：</strong><br>
                • 服务正在 http://0.0.0.0:8000 运行<br>
                • 如有访问问题，请检查容器日志
            </div>
            
            <h3>📋 可用端点：</h3>
            <div class="endpoint">
                <strong>POST</strong> <code>/v1/chat/completions</code> - 聊天完成接口
            </div>
            <div class="endpoint">
                <strong>GET</strong> <code>/v1/models</code> - 模型列表接口
            </div>
            
            <h3>🔑 API调用示例：</h3>
            <pre style="background: #1e1e1e; padding: 15px; border-radius: 5px;">
curl -X POST """ + f"http://{os.environ.get('HOSTNAME', 'localhost')}:8000" + """/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer 1" \\
  -d '{
    "model": "toolbaz-v4.5-fast",
    "messages": [{"role": "user", "content": "你好"}]
  }'
            </pre>
            
            <h3>🌊 流式响应测试：</h3>
            <pre style="background: #1e1e1e; padding: 15px; border-radius: 5px;">
curl -X POST """ + f"http://{os.environ.get('HOSTNAME', 'localhost')}:8000" + """/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer 1" \\
  -d '{
    "model": "toolbaz-v4.5-fast",
    "messages": [{"role": "user", "content": "写一首诗"}],
    "stream": true
  }'
            </pre>
            
            <p><small>⚠️ 静态文件未找到，显示此备用页面</small></p>
        </div>
    </body>
    </html>
    """