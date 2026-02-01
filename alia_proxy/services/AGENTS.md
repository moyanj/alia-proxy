# AI PROXY SERVICES

## OVERVIEW
核心业务逻辑层。负责请求编排、媒体持久化及异步日志。

## WHERE TO LOOK
| 模块 | 文件 | 职责 |
|------|------|------|
| **调度器** | `proxy.py` | `ProxyService`: 协调 Provider、Logger、Media |
| **日志** | `logger.py` | 异步写入 `RequestLog` (Token, Model, Prompt) |
| **媒体** | `media.py` | `save_media`: 非阻塞写入 `data/media/` |

## CONVENTIONS
- **异步 I/O**: 全程 `async/await` (Tortoise-ORM, aiofiles)。
- **错误隔离**: 日志/媒体保存失败不应阻塞主业务响应。
- **数据流**: Router -> ProxyService -> Provider -> (Media/Logger)。
- **解耦**: Service 层不应依赖 FastAPI 的 `Request/Response` 对象。

## ANTI-PATTERNS
- **同步阻塞**: 禁止 `time.sleep`, `open()`, `requests`。
- **逻辑泄露**: Token 计算、媒体转换逻辑不应下沉到 Router。
- **循环依赖**: `proxy.py` 依赖 `logger`/`media`，反之禁止。
