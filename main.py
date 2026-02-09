import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.app.common.core import logger
from backend.app.modules.module_system.user.controller import UserRouter

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="Smart Custom AST-TTS API",
    description="智能自定义语音合成和识别服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# 挂载静态文件
static_dir = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 主页路由
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """主页 - 返回前端HTML"""
    html_file = static_dir / "index2.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return HTMLResponse(content="<h1>Smart Custom AST-TTS</h1><p>前端文件未找到</p>")

# 导入和注册路由
# 添加backend目录到系统路径
sys.path.append(str(Path(__file__).parent / "backend"))

# 注册TTS路由
try:
    from backend.app.modules.tts.controller import TTSRouter
    app.include_router(TTSRouter, prefix="/api")
    logger.info("TTS路由已成功注册")
except ImportError as e:
    logger.error(f"导入TTS模块失败: {e}")
    logger.warning("请确保所有依赖已正确安装")


# 注册ASR路由
try:
    from backend.app.modules.asr.controller import ASRRouter
    app.include_router(ASRRouter, prefix="/api")
    logger.info("ASR路由已成功注册")
except ImportError as e:
    logger.error(f"导入ASR模块失败: {e}")
    logger.warning("请确保所有依赖已正确安装")

app.include_router(UserRouter, prefix="/api")
#
# # 注册AST-TTS路由
# try:
#     from backend.app.modules.ast_tts.controller import AsrTtsRouter
#     app.include_router(AsrTtsRouter, prefix="/api")
#     logger.info("AST-TTS路由已成功注册")
# except ImportError as e:
#     logger.error(f"导入AST-TTS模块失败: {e}")
#     logger.warning("请确保所有依赖已正确安装")

# 注册AI路由
try:
    from backend.app.modules.ai.controller import AIRouter
    app.include_router(AIRouter, prefix="/api")
    logger.info("AI路由已成功注册")
except ImportError as e:
    logger.error(f"导入AI模块失败: {e}")
    logger.warning("请确保所有依赖已正确安装")

if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"🌐 启动服务器: http://{host}:{port}")
    logger.info(f"🌐 访问页面: http://localhost:{port}")
    logger.info(f"📚 API文档: http://{host}:{port}/docs")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
