# ROUTERS KNOWLEDGE BASE

## OVERVIEW
实现 OpenAI 兼容接口及系统管理 API 的 FastAPI 路由层，负责请求分发与初步校验。

## WHERE TO LOOK
| 任务 | 文件 | 描述 |
|------|------|------|
| 修改/新增 AI 代理接口 | `openai.py` | 包含对话 (`chat/completions`)、模型列表、图像生成及语音合成。 |
| 调整模型/提供商解析逻辑 | `deps.py` | 核心依赖 `get_proxy_service` 负责解析 `provider/model` 字符串。 |
| 开发管理后台/统计接口 | `common.py` | 提供日志查询、系统统计及提供商配置状态接口。 |
| 扩展数据导出格式 | `export.py` | 支持将请求日志导出为 ShareGPT、CSV 或 JSONL 格式。 |
| 调整媒体文件访问逻辑 | `media.py` | 负责安全地提供本地存储的 AI 生成媒体文件（图片、音频）。 |

## CONVENTIONS
- **动态路由解析**: 必须通过 `get_proxy_service` 依赖项从请求体的 `model` 字段动态解析提供商实例。
- **OpenAI 兼容性**: 所有 `/v1/*` 路径必须严格对齐 OpenAI 的 API 规范，确保客户端无缝切换。
- **流式响应**: AI 生成内容（SSE）和大数据导出必须使用 `StreamingResponse` 以优化内存占用。
- **依赖注入**: 路由层应保持极简，仅负责参数接收和响应返回，核心逻辑应委托给 `ProxyService`。
- **错误处理**: 统一使用 `HTTPException` 抛出错误，并确保返回的错误格式与 OpenAI 保持一致。

## ANTI-PATTERNS
- **硬编码提供商逻辑**: 严禁在路由中编写特定提供商（如 OpenAI vs Anthropic）的差异化逻辑。
- **直接数据库操作**: 路由不应直接读写数据库，请求日志记录应由 `ProxyService` 自动完成。
- **同步阻塞调用**: 严禁使用同步的文件 I/O 或网络请求，必须使用 `async` 驱动或 `anyio.to_thread`。
- **硬编码文件路径**: 访问媒体文件时必须使用 `settings.media_dir`，严禁使用相对路径或硬编码字符串。
- **忽略异常捕获**: 路由入口应确保异常被正确捕获并转换为标准的 API 错误响应。
