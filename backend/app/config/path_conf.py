from pathlib import Path

#项目根目录
BASE_DIR = Path(__file__).parent.parent.parent

#环境配置目录
ENV_DIR = BASE_DIR / 'env'

#日志文件路径
LOG_DIR = BASE_DIR / 'log'