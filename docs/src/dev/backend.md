# 后端开发

后端基于 **FastAPI** 框架构建，使用 Python 3.12+。

## 关键技术栈

- **Web 框架**: FastAPI
- **HTTP 客户端**: httpx (全异步)
- **ORM**: Tortoise-ORM (异步)
- **依赖管理**: uv

## 配置与环境变量

配置来源有两个（优先级从高到低）：

1. **环境变量**（前缀 `AIPROX_`）：适合容器化部署和敏感信息
2. **config.toml**：适合复杂的提供商和模型映射配置

### 环境变量

| 变量名 | 类型 | 说明 |
|--------|------|------|
| `AIPROX_DATABASE_URL` | string | 数据库连接字符串，支持 SQLite、PostgreSQL、MySQL |
| `AIPROX_MEDIA_DIR` | string | 媒体文件存储路径 |
| `AIPROX_DEBUG` | bool | 调试模式 |
| `AIPROX_HOT_RELOAD` | bool | 启用 config.toml 热重载 |

示例：
```bash
export AIPROX_DATABASE_URL="postgres://user:pass@localhost/aiprox"
export AIPROX_DEBUG="true"
```

## 核心模式

### 1. 依赖注入 (Dependency Injection)

我们在 `aiprox/routers/deps.py` 中定义了核心服务的工厂函数。

```python
# 获取 ProxyService 实例
async def get_proxy_service(
    request: Request,
    provider_factory: ProviderFactory = Depends(get_provider_factory)
) -> ProxyService:
    # ... 解析模型并初始化 Service ...
    return ProxyService(...)
```

在路由中使用：

```python
@router.post("/chat/completions")
async def chat_completions(
    request: ChatRequest,
    proxy: ProxyService = Depends(get_proxy_service)  # 注入
):
    return await proxy.chat(request)
```

这种模式使得我们可以在测试中轻松地 mock 掉 `ProxyService` 或 `ProviderFactory`。

### 2. 数据库操作

使用 `Tortoise-ORM` 进行数据库交互。它提供了类似 Django ORM 的 API，但是完全异步的。

**定义模型 (`models.py`)**:

```python
class RequestLog(Model):
    id = fields.BigIntField(pk=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    # ...
```

**查询与创建**:

```python
# 异步创建
log = await RequestLog.create(provider="openai", model="gpt-4", ...)

# 异步查询
logs = await RequestLog.filter(status_code=200).offset(0).limit(10).all()
```

### 3. 后台任务

为了不阻塞 HTTP 响应，耗时的操作（如日志写入、媒体转存）通常作为 `BackgroundTasks` 或直接使用 `asyncio.create_task` 运行。

`LoggerService.log_request` 方法就是一个典型的异步任务，它被设计为“fire-and-forget”，在主请求返回后继续执行。

## 测试

我们使用 `pytest` 进行测试。测试环境使用内存中的 SQLite 数据库，确保测试是隔离且快速的。

```bash
uv run pytest
```
