"""
测试 App.astream 方法
LangGraph 原生按节点流式输出测试
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))
sys.path.append(str(root_path / "backend"))

# 加载环境变量
load_dotenv(root_path / "backend" / "env" / ".env")

from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.common.core.database import init_beanie_odm, async_db_session
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from backend.app.modules.workflow.api.service import AppService
from backend.app.modules.workflow.app import App


# ========== 配置 ==========
# 在这里填入你要测试的 App UUID
APP_UUID = "8488bff8-30a2-415d-8d1d-7c4fb4b6567b"
# 输入问题
INPUT_MESSAGE = "写一首关于小猫的诗"


async def test_astream():
    """测试 astream 方法"""
    print("=" * 60)
    print("测试 App.astream 方法（LangGraph 原生按节点流式输出）")
    print("=" * 60)

    # 1. 初始化 MongoDB ODM
    print("\n[1/5] 初始化数据库连接...")
    await init_beanie_odm()
    print("✓ 数据库初始化完成")

    # 2. 获取数据库会话
    print("\n[2/5] 获取数据库会话...")
    async with async_db_session() as session:
        db: AsyncSession = session

        # 这里简化处理：你需要确保有用户数据，或者根据实际情况获取用户
        # 如果需要认证，可以从 JWT 解析获取用户，这里我们假设你已经有用户 ID
        # 测试时，如果 App 是公开的，或者你有权限，请确保这里 user 正确
        from backend.app.modules.module_system.user.crud import UserCRUD
        auth = AuthSchema(db=db)

        # 这里简单起见，获取第一个用户
        # 实际使用中请替换为正确的用户
        user = await UserCRUD(auth).get_by_mobile_crud("18770335001")
        if not user:
            print("❌ 没有找到用户，请先创建用户")
            return

        print(f"✓ 使用用户: {user.username} (id={user.id})")

        # 3. 获取 App 实例
        print(f"\n[3/5] 从数据库加载 App: {APP_UUID}...")
        if APP_UUID == "YOUR_APP_UUID_HERE":
            print("❌ 请先修改 APP_UUID 为你要测试的应用 UUID")
            return

        app: App | None = await AppService.exist(auth, APP_UUID)
        if not app:
            print(f"❌ 未找到 App: {APP_UUID}")
            return

        print(f"✓ 加载成功: {app.name}")
        print(f"  节点数: {len(app.nodes)}, 边数: {len(app.edges)}")

        # 4. 编译并调用 astream
        print("\n[4/5] 开始执行 astream...")
        input_data = {"input": INPUT_MESSAGE}
        print(f"  输入: {INPUT_MESSAGE}")
        print("\n" + "-" * 60)
        print("【LangGraph astream 输出】\n")

        # 5. 迭代输出
        chunk_count = 0
        async for chunk in app.astream(input_data):
            chunk_count += 1
            print(f"[Chunk {chunk_count}]")
            print(chunk)
            print("-" * 40)

        print("\n" + "-" * 60)
        print(f"\n[5/5] 执行完成！共输出 {chunk_count} 个chunk")
        print("\n说明：")
        print("- astream 是 LangGraph 原生流式，按节点输出")
        print("- 每个chunk是一个节点执行完的完整结果")
        print("- 对比 stream_tokens 是按Token输出，粒度更细")


if __name__ == "__main__":
    asyncio.run(test_astream())
