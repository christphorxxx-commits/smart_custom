# -*- coding: utf-8 -*-
import asyncio
import logging

from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine, create_async_engine
from backend.app.modules.api.ai.model import Chat,ChatItem
from backend.app.modules.workflow.api.model import App

from backend.app.common.core.logger import log

# db_pg.py

load_dotenv()

# 设置Python默认编码（可选，用于兼容）
# reload(sys) if 'reload' in dir(sys) else None
# sys.setdefaultencoding('utf-8') if hasattr(sys, 'setdefaultencoding') else None

# =========================
# PostgreSQL config
# =========================
from backend.app.config.setting import settings


def create_async_engine_and_session(
        db_url: str = settings.async_db_url
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """
    创建异步数据库引擎和会话工厂。

    Returns:
        tuple[AsyncEngine, async_sessionmaker[AsyncSession]]
    """
    if not settings.SQL_DB_ENABLE:
        raise ValueError("请先开启数据库连接（设置 SQL_DB_ENABLE=True）")

    try:
        async_engine: AsyncEngine = create_async_engine(
            url=db_url,
            echo=settings.DATABASE_ECHO,
            echo_pool=settings.ECHO_POOL,
            pool_pre_ping=settings.POOL_PRE_PING,
            future=settings.FUTURE,
            pool_recycle=settings.POOL_RECYCLE,
            pool_size=settings.POOL_SIZE,
            max_overflow=settings.MAX_OVERFLOW,
            pool_timeout=settings.POOL_TIMEOUT,
            pool_use_lifo=settings.POOL_USE_LIFO,
        )
    except Exception as e:
        log.error(f'❌ 异步数据库连接失败: {e}')
        raise
    else:
        async_session_factory = async_sessionmaker(
            bind=async_engine,
            autocommit=settings.AUTOCOMMIT,
            autoflush=settings.AUTOFLUSH,  # ← 确认这里是 AUTOFLUSH
            expire_on_commit=settings.EXPIRE_ON_COMMIT,
            class_=AsyncSession
        )
        return async_engine, async_session_factory


async_engine, async_db_session = create_async_engine_and_session(settings.async_db_url)


# =========================
# MongoDB config
# =========================

def create_mongo_client(
        mongo_uri: str = settings.mongo_uri,
        db_name: str = settings.MONGO_DB
) -> tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]:
    """
    创建异步MongoDB客户端。

    Args:
        mongo_uri: MongoDB连接地址
        db_name: 默认数据库名称

    Returns:
        tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]: (全局客户端, 默认数据库)
    """
    try:

        mongo_client = AsyncIOMotorClient(mongo_uri)
        mongo_db = mongo_client[db_name]
        log.info(f'✅ MongoDB连接成功: {mongo_uri}, db: {db_name}')
        return mongo_client, mongo_db
    except Exception as e:
        logging.error(f'❌ MongoDB连接失败: {e}')
        raise

mongo_client, mongo_db = create_mongo_client()
# 全局MongoDB客户端和默认数据库
# 环境变量: MONGO_URI, MONGO_DB
# try:
#     mongo_client, mongo_db = create_mongo_client()
# except Exception as e:
#     # MongoDB可选，如果连接失败不影响PostgreSQL功能
#     log.warning(f'⚠️ MongoDB未配置或连接失败: {e}。功能将不可用，但不影响主程序运行。')
#     mongo_client = None
#     mongo_db = None

def get_sync_mongo_client(
        mongo_uri: str = settings.mongo_uri,
        db_name: str = settings.MONGO_DB
) -> tuple[MongoClient, object]:
    """
    创建同步MongoDB客户端（用于同步代码）

    Args:
        mongo_uri: MongoDB连接地址
        db_name: 默认数据库名称

    Returns:
        tuple[MongoClient, Database]: (同步客户端, 默认数据库)
    """
    try:
        # print(mongo_uri)
        sync_client = MongoClient(mongo_uri)
        sync_db = sync_client[db_name]
        logging.info(f'✅ 同步MongoDB连接成功: {mongo_uri}, db: {db_name}')
        return sync_client, sync_db
    except Exception as e:
        logging.error(f'❌ 同步MongoDB连接失败: {e}')
        raise


# 如果需要使用同步Mongo，可以取消注释下面这行
# sync_mongo_client, sync_mongo_db = get_sync_mongo_client()
# sync_mongo_client = None
# sync_mongo_db = None

async def init_beanie_odm():
    """初始化Beanie ODM，注册所有MongoDB文档模型"""
    global mongo_client, mongo_db
    if mongo_client is None or mongo_db is None:
        log.warning("⚠️ MongoDB未连接，跳过Beanie初始化")
        return

    document_models = [
        Chat,
        ChatItem,
        App
    ]

    # 兼容性补丁：兼容 motor 3.x + Beanie
    # 1. 让 AsyncIOMotorDatabase.client 成为属性直接返回客户端
    #    motor 3.x 改变了 API，client 从属性变为方法，Beanie 还期望它是属性
    from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
    AsyncIOMotorDatabase.client = property(lambda self: self._client)
    # 2. 添加 append_metadata 方法，Beanie 老版本期望这个方法存在
    #    新版本 motor 不需要，所以加个空方法
    def append_metadata(self, metadata):
        pass
    AsyncIOMotorClient.append_metadata = append_metadata

    await init_beanie(
        database=mongo_db,
        document_models=document_models
    )
    log.info("✅ Beanie ODM 初始化完成")

if __name__ == '__main__':
    asyncio.run(init_beanie_odm())
