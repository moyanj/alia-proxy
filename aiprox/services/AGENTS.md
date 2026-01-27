# AI PROXY SERVICES

## OVERVIEW
核心业务逻辑层，负责请求编排、多媒体持久化及异步日志记录。

## WHERE TO LOOK
- **proxy.py**: 
    - `ProxyService`: 核心调度器。负责解析 Provider 响应，并协调日志记录与媒体保存。
    - `chat`: 处理非流式聊天请求，同步等待响应后记录日志。
    - `chat_stream`: 处理流式响应，并在流结束时聚合完整内容进行异步日志补录。
    - `image_gen` / `text_to_speech`: 处理多媒体请求，将 Base64 或二进制流转换为本地 URL。
- **logger.py**: 
    - `log_request`: 统一日志入口。封装了对 `RequestLog` 模型的异步创建操作。
    - 负责记录：Provider 实例名、Endpoint、模型、Prompt、响应内容、Token 消耗及错误信息。
- **media.py**: 
    - `save_media`: 媒体持久化工具。使用 `aiofiles` 实现非阻塞磁盘写入。
    - 自动管理 `data/media/` 目录的创建及基于 UUID 的文件名生成。

## CONVENTIONS
- **异步 I/O**: 必须使用 `async/await` 处理所有外部交互。数据库使用 Tortoise-ORM，文件使用 `aiofiles`。
- **错误处理**: Service 层应捕获并记录业务异常，确保即使日志记录失败也不影响主流程响应。
- **数据流向**: Router -> ProxyService -> Provider -> (MediaService) -> (LoggerService) -> Response。
- **路径管理**: 媒体文件路径在数据库中存储为相对路径（文件名），由 Router 层负责拼接完整访问 URL。
- **解耦设计**: Service 层不应感知具体的 HTTP 框架（如 FastAPI 的 `Request/Response` 对象）。
- **资源清理**: 确保在流式传输中断等异常情况下，仍能尝试记录已产生的日志。

## ANTI-PATTERNS
- **同步阻塞**: 严禁在 Service 层使用 `time.sleep`、`open()` 或 `requests` 等同步阻塞调用。
- **逻辑下沉**: 禁止将复杂的业务逻辑（如 Token 计算、媒体转换）直接写在 Router 中。
- **硬编码**: 严禁硬编码存储路径或 Provider 名称，必须通过 `config.py` 或 `factory.py` 获取。
- **循环依赖**: 避免 `services` 内部模块间的循环引用，通常 `proxy.py` 依赖其他两个模块。
- **直接操作模型**: 外部模块应通过 `logger.py` 记录日志，而非直接调用 `RequestLog.create`。
