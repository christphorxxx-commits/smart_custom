#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MongoDB连接测试脚本"""

# 兼容性补丁必须第一个打上！
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, str(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 先导入motor，打补丁，再导入其他东西
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
# 兼容性补丁1：让 AsyncIOMotorDatabase.client 成为属性直接返回客户端
# motor 3.x 改变了 API，client 从属性变为方法，Beanie 还期望它是属性
AsyncIOMotorDatabase.client = property(lambda self: self._client)
# 兼容性补丁2：添加 append_metadata 方法，Beanie 老版本期望这个方法存在
# 新版本 motor 不需要，所以我们加个空方法就行
def append_metadata(self, metadata):
    pass
AsyncIOMotorClient.append_metadata = append_metadata

import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from backend.app.config.setting import settings
from backend.app.modules.api.ai.model import Chat, ChatItem


async def test_mongo_connection():
    """测试MongoDB连接并写入测试数据"""
    print("=" * 60)
    print("MongoDB 连接测试")
    print("=" * 60)

    # 打印配置信息
    print(f"\n当前配置:")
    print(f"  MONGO_URI: {settings.MONGO_URI if settings.MONGO_URI else '(自动构建)'}")
    print(f"  MONGO_HOST: {settings.MONGO_HOST}")
    print(f"  MONGO_PORT: {settings.MONGO_PORT}")
    print(f"  MONGO_USER: {settings.MONGO_USER if settings.MONGO_USER else '(未设置)'}")
    print(f"  MONGO_DB: {settings.MONGO_DB}")
    print(f"  最终URI: {settings.mongo_uri}")

    try:
        # 创建客户端
        print("\n🔄 正在连接MongoDB...")
        client = AsyncIOMotorClient(settings.mongo_uri)
        db = client[settings.MONGO_DB]
        print("✅ MongoDB连接成功")
        print(f"  DEBUG: db = {type(db)}")
        print(f"  DEBUG: db.client = {type(db.client)}, value={db.client}")

        # 初始化Beanie
        print("\n🔄 正在初始化Beanie ODM...")
        document_models = [Chat, ChatItem]
        await init_beanie(
            database=db,
            document_models=document_models
        )
        print("✅ Beanie 初始化完成")

        # 测试写入数据
        print("\n🔄 正在写入测试聊天会话...")
        chat = Chat(
            user_id="test_user_001",
            title="测试会话 - " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        )
        await chat.insert()
        print(f"✅ 测试会话写入成功，ID: {chat.id}")

        # 写入测试消息
        print("\n🔄 正在写入测试消息...")
        item1 = ChatItem(
            chat_id=chat.id,
            role="user",
            content="你好，这是一条来自测试脚本的用户消息"
        )
        await item1.insert()
        item2 = ChatItem(
            chat_id=chat.id,
            role="assistant",
            content="你好！我收到了你的消息，这是AI回复的测试内容。MongoDB连接正常！"
        )
        await item2.insert()
        print("✅ 测试消息写入成功")

        # 查询验证
        print("\n🔄 正在验证写入的数据...")
        all_chats = await Chat.find({"user_id": "test_user_001"}).to_list()
        print(f"  查询到 {len(all_chats)} 个测试会话")

        messages = await ChatItem.find({"chat_id": chat.id}).sort([("created_at", 1)]).to_list()
        print(f"  查询到 {len(messages)} 条测试消息")
        for msg in messages:
            print(f"    [{msg.role}] {msg.content}")

        print("\n" + "=" * 60)
        print("🎉 全部测试通过！MongoDB连接和写入正常")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_mongo_connection())
    sys.exit(0 if success else 1)
