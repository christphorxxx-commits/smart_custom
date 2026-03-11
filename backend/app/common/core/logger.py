import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 创建logger实例
logger = logging.getLogger(__name__)

# 为了保持兼容性，定义log变量
log = logger
