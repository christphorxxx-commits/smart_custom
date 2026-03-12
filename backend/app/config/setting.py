from pydantic_settings import BaseSettings,SettingsConfigDict
from backend.app.config.path_conf import ENV_DIR
from typing import Literal
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=ENV_DIR / f".env",
        env_file_encoding="utf-8",
        extra='ignore',
        case_sensitive=True,  # 区分大小写
    )

    # ================================================= #
    # ******************* 服务器配置 ****************** #
    # ================================================= #
    SERVER_HOST: str = '0.0.0.0'  # 允许访问的IP地址
    SERVER_PORT: int = 8001  # 服务端口

    # ================================================= #
    # ******************** 数据库配置 ******************* #
    # ================================================= #
    SQL_DB_ENABLE: bool = True  # 是否启用数据库
    DATABASE_ECHO: bool | Literal['debug'] = False  # 是否显示SQL日志
    ECHO_POOL: bool | Literal['debug'] = False  # 是否显示连接池日志
    POOL_SIZE: int = 10  # 连接池大小
    MAX_OVERFLOW: int = 20  # 最大溢出连接数
    POOL_TIMEOUT: int = 30  # 连接超时时间(秒)
    POOL_RECYCLE: int = 1800  # 连接回收时间(秒)
    POOL_USE_LIFO: bool = True  # 是否使用LIFO连接池
    POOL_PRE_PING: bool = True  # 是否开启连接预检
    FUTURE: bool = True  # 是否使用SQLAlchemy 2.0特性
    AUTOCOMMIT: bool = False  # 是否自动提交
    AUTOFLUSH: bool = False  # 是否自动刷新
    EXPIRE_ON_COMMIT: bool = False  # 是否在提交时过期

    # 数据库类型
    DATABASE_TYPE: Literal['mysql', 'postgres'] = 'postgres'

    # MySQL/PostgreSQL数据库连接
    DATABASE_HOST: str = os.getenv('DATABASE_HOST')
    DATABASE_PORT: int = os.getenv('DATABASE_PORT')
    DATABASE_USER: str = os.getenv('DATABASE_USER')
    DATABASE_PASSWORD: str = os.getenv('DATABASE_PASSWORD')
    DATABASE_NAME: str = os.getenv('DATABASE_NAME')

    #JWT过期时间
    ACCESS_TOKEN_EXPIRE_TIME : int = 60 * 60 * 24 * 1                     # access_token过期时间(秒)1 天
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 60 * 24 * 7
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY')
    ALGORITHM: str = "HS256"
    TOKEN_TYPE: str = "bearer"

    #AI配置
    DASHSCOPE_API_KEY: str = os.getenv('DASHSCOPE_API_KEY')

    @property
    def async_db_url(self) -> str:
        """获取异步数据库连接"""
        if self.DATABASE_TYPE == "mysql":
            return f"mysql+asyncmy://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?charset=utf8mb4"
        elif self.DATABASE_TYPE == "postgres":
            return f"postgresql+asyncpg://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        elif self.DATABASE_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.DATABASE_NAME}"
        elif self.DATABASE_TYPE == "dm":
            return f"dm+dmPython://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        else:
            raise ValueError(f"数据库驱动不支持: {self.DATABASE_TYPE}, 请选择 请选择 mysql、postgres")

    @property
    def db_url(self) -> str:
        """获取同步数据库连接"""
        if self.DATABASE_TYPE == "mysql":
            return f"mysql+pymysql://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?charset=utf8mb4"
        elif self.DATABASE_TYPE == "postgres":
            return f"postgresql+psycopg2://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        elif self.DATABASE_TYPE == "sqlite":
            return f"sqlite+pysqlite:///{self.DATABASE_NAME}"
        elif self.DATABASE_TYPE == "dm":
            return f"dm+dmPython://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        else:
            raise ValueError(f"数据库驱动不支持: {self.DATABASE_TYPE}, 请选择 请选择 mysql、postgres")

settings = Settings()