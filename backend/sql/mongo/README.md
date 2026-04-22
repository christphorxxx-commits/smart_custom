# MongoDB 初始化数据

三个集合对应项目中的数据结构：

| 文件名 | 集合名 | 用途 |
|--------|--------|------|
| `apps.json` | `apps` | 存储工作流应用完整配置（nodes, edges） |
| `chat.json` | `chat` | 存储对话会话列表 |
| `chat_items.json` | `chat_items` | 存储单条对话消息 |

## 导入方法

### MongoDB Compass (图形界面)
1. 打开 MongoDB Compass，连接到你的 MongoDB
2. 选择 `smart_custom` 数据库（如果没有先创建）
3. 点击 **Add Data** → **Import JSON**
4. 依次选择三个 `.json` 文件导入
5. 导入完成后会自动创建集合

### 命令行导入
```bash
# 导入 apps
mongoimport --db smart_custom --collection apps --file apps.json
# 导入 chat
mongoimport --db smart_custom --collection chat --file chat.json
# 导入 chat_items
mongoimport --db smart_custom --collection chat_items --file chat_items.json
```

## 集合文档结构

### apps
```js
{
  uuid:        string  // UUID，用于跨库关联PG
  name:          string  // 应用名称
  description:   string  // 应用描述
  uuid:       string  // 创建用户ID
  icon:          string  // emoji图标
  type:          string  // 类型: workflow/ai/chat
  nodes:         array   // [{id, type, config}, ...]
  edges:         array   // [{source, target, type, condition}, ...]
  is_public:     boolean // 是否公开
  version:       int     // 版本号
}
```

### chat
```js
{
  uuid:        string  // 关联的应用UUID
  uuid:       string  // 用户ID
  title:         string  // 对话标题
  last_message:  string  // 最后一条消息摘要
  message_count: int     // 消息数量
}
```

### chat_items
```js
{
  chat_id:       string  // 所属对话ID (chat集合的ObjectId)
  role:          string  // 角色: user/assistant/system
  content:       string  // 消息内容
}
```
