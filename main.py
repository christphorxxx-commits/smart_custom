import os
import logging
from pathlib import Path
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from backend.app.modules.ast_tts.tools.constant import MODEL_PATH

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Smart Custom AST-TTS API",
    description="智能自定义语音合成和识别服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000", 
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "*",
        "Content-Type",
        "Authorization", 
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
    expose_headers=["*"]
)

# 挂载静态文件
static_dir = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 主页路由
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """主页 - 返回前端HTML"""
    html_file = static_dir / "index.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return HTMLResponse(content="<h1>Smart Custom AST-TTS</h1><p>前端文件未找到</p>")

# 导入和注册路由
try:
    # 导入AST-TTS路由
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent / "backend"))
    
    from app.modules.ast_tts.controller import ASTTTSRouter
    
    # 注册路由
    app.include_router(ASTTTSRouter, prefix="/api")
    logger.info("AST-TTS路由已成功注册")
    
except ImportError as e:
    logger.error(f"导入AST-TTS模块失败: {e}")
    logger.warning("请确保所有依赖已正确安装")

# WebSocket连接管理
connected_clients = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """通用WebSocket端点"""
    await websocket.accept()
    connected_clients[client_id] = websocket
    logger.info(f"WebSocket客户端 {client_id} 已连接")
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            logger.info(f"收到客户端 {client_id} 消息: {data}")
            
            # 处理消息并回复
            await websocket.send_text(f"服务端回复: {data}")
            
    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
    finally:
        # 清理连接
        if client_id in connected_clients:
            del connected_clients[client_id]
        logger.info(f"WebSocket客户端 {client_id} 已断开")

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Smart Custom AST-TTS",
        "version": "1.0.0"
    }

# 服务信息端点
@app.get("/api/info")
async def service_info():
    """服务信息"""
    return {
        "name": "Smart Custom AST-TTS API",
        "version": "1.0.0",
        "description": "智能自定义语音合成和识别服务",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "ast_tts": "/api/ast-tts",
            "websocket": "/ws/{client_id}"
        }
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("🚀 Smart Custom AST-TTS 服务启动中...")
    
    # 检查环境变量
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.warning("⚠️  警告: 未设置 DASHSCOPE_API_KEY 环境变量")
    else:
        logger.info("✅ 阿里云百炼API配置正常")
    
    # 检查模型文件
    model_path = os.getenv("MODEL_PATH", MODEL_PATH)
    if os.path.exists(model_path):
        logger.info(f"✅ TTS模型文件存在: {model_path}")
    else:
        logger.warning(f"⚠️  警告: TTS模型文件不存在: {model_path}")
    
    logger.info("🎉 服务启动完成！访问 http://localhost:8000 查看前端界面")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("🛑 Smart Custom AST-TTS 服务正在关闭...")
    
    # 关闭所有WebSocket连接
    for client_id, websocket in connected_clients.items():
        try:
            await websocket.close()
        except Exception as e:
            logger.error(f"关闭WebSocket连接 {client_id} 时出错: {e}")
    
    logger.info("✅ 服务已安全关闭")

if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"🌐 启动服务器: http://{host}:{port}")
    logger.info(f"📚 API文档: http://{host}:{port}/docs")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
