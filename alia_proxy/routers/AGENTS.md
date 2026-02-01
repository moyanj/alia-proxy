# ROUTERS KNOWLEDGE BASE

## OVERVIEW
OpenAI 兼容接口及系统管理 API 路由层。负责请求分发与参数校验。

## WHERE TO LOOK
| 任务 | 文件 | 描述 |
|------|------|------|
| **AI 接口** | `openai.py` | 对话、绘图、TTS (`/v1/*`) |
| **依赖注入** | `deps.py` | `get_proxy_service` (解析 `provider/model`) |
| **管理后台** | `common.py` | 日志查询、统计、配置 |
| **数据导出** | `export.py` | ShareGPT/JSONL/CSV 导出 |
| **媒体文件** | `media.py` | 本地媒体文件服务 |

## CONVENTIONS
- **动态路由**: 必须通过 `deps.get_proxy_service` 获取 Provider。
- **OpenAI 兼容**: `/v1/*` 必须严格对齐 OpenAI 规范。
- **流式响应**: AI 生成内容 (SSE) 必须使用 `StreamingResponse`。
- **依赖注入**: 核心逻辑委托给 `ProxyService`，路由层仅做参数处理。

## ANTI-PATTERNS
- **硬编码**: 严禁在路由中写特定 Provider (OpenAI/Anthropic) 的逻辑。
- **直接数据库**: 路由层禁止直接操作 DB，必须通过 Service。
- **同步 I/O**: 严禁同步文件/网络操作。
