import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.app.common.core.logger import log

# 加载环境变量（如果存在.env文件）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化，关闭时清理"""
    # 启动时：初始化Beanie ODM（MongoDB）
    try:
        from backend.app.common.core.database import init_beanie_odm

        await init_beanie_odm()
        log.info("✅ 应用启动初始化完成")
    except Exception as e:
        log.error(f"❌ 应用启动初始化失败: {e}")
        log.warning("⚠️ MongoDB相关功能可能不可用，但不影响主程序运行")

    yield  # 应用运行中

    # 关闭时：这里不需要额外清理，MongoDB客户端会自动处理
    log.info("🔻 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Smart Custom AST-TTS API",
    description="智能自定义语音合成和识别服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
    log.info("TTS路由已成功注册")
except ImportError as e:
    log.error(f"导入TTS模块失败: {e}")
    log.warning("请确保所有依赖已正确安装")


# 注册ASR路由
try:
    from backend.app.modules.asr.controller import ASRRouter
    app.include_router(ASRRouter, prefix="/api")
    log.info("ASR路由已成功注册")
except ImportError as e:
    log.error(f"导入ASR模块失败: {e}")
    log.warning("请确保所有依赖已正确安装")

#注册User路由
try:
    from backend.app.modules.module_system.user.controller import UserRouter
    app.include_router(UserRouter, prefix="/api")
    log.info("User路由已成功注册")
except ImportError as e:
    log.error(f"导入User模块失败{e}")
    log.warning("请确保所有依赖已经正确安装")

# 注册Auth路由
try:
    from backend.app.modules.module_system.auth.controller import AuthRouter
    app.include_router(AuthRouter, prefix="/api")
    log.info("Auth路由已成功注册")
except ImportError as e:
    log.error(f"导入Auth模块失败: {e}")
    log.warning("请确保所有依赖已正确安装")

# 注册AI路由
try:
    from backend.app.modules.api.ai.controller import AIRouter
    app.include_router(AIRouter, prefix="/api")
    log.info("AI路由已成功注册")
except ImportError as e:
    log.error(f"导入AI模块失败: {e}")
    log.warning("请确保所有依赖已正确安装")

# 注册AI路由
try:
    from backend.app.modules.workflow.controller import WorkflowRouter
    app.include_router(WorkflowRouter, prefix="/api")
    log.info("WORKFLOW路由已成功注册")
except ImportError as e:
    log.error(f"导入WORKFLOW模块失败: {e}")
    log.warning("请确保所有依赖已正确安装")

# # 注册全局异常处理器
# try:
#     from backend.app.common.core.exceptions import handle_exception
#     handle_exception(app)
#     log.info("全局异常处理器已成功注册")
# except ImportError as e:
#     log.error(f"导入异常处理器失败: {e}")
#     log.warning("请确保所有依赖已正确安装")


if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    log.info(f"🌐 启动服务器: http://{host}:{port}")
    log.info(f"🌐 访问页面: http://localhost:{port}")
    log.info(f"📚 API文档: http://{host}:{port}/docs")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
