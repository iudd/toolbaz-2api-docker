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
    try:
        # 使用绝对路径处理静态文件
        import os
        static_path = os.path.join(os.getcwd(), "static", "index.html")
        with open(static_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Toolbaz-2API 服务运行中</h1>
                <p class="status">✅ API服务已就绪</p>
                
                <h3>📋 可用端点：</h3>
                <div class="endpoint">
                    <strong>POST</strong> <code>/v1/chat/completions</code> - 聊天完成接口
                </div>
                <div class="endpoint">
                    <strong>GET</strong> <code>/v1/models</code> - 模型列表接口
                </div>
                
                <h3>🔑 API调用示例：</h3>
                <pre style="background: #1e1e1e; padding: 15px; border-radius: 5px;">
curl -X POST http://localhost:8000/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer 1" \\
  -d '{
    "model": "toolbaz-v4.5-fast",
    "messages": [{"role": "user", "content": "你好"}]
  }'
                </pre>
                
                <p><small>注意：静态文件未找到，显示此备用页面</small></p>
            </div>
        </body>
        </html>
        """