# 图像生成

`alia_proxy` 完全支持 OpenAI 的图像生成接口 (`/v1/images/generations`)，并在此基础上增加了一层重要的**隐式处理逻辑**：自动持久化。

这意味着您生成的每一张图片都会被自动保存到服务器本地，并通过一个稳定的 URL 提供访问，极大地方便了后续的集成和展示。

## 接口用法

您可以像调用标准 OpenAI API 一样调用 `alia_proxy` 的图像生成接口。

**请求示例**:

```bash
curl http://localhost:8000/v1/images/generations \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai-dalle/dall-e-3",
    "prompt": "一只可爱的赛博朋克猫，霓虹灯背景",
    "n": 1,
    "size": "1024x1024"
  }'
```

**关键点**:
- `model`: 同样遵循 `<provider_instance_name>/<model_identifier>` 的格式。
- `prompt`: 描述您想要生成的图像内容。

## 隐式行为：自动持久化与 URL 替换

当 `alia_proxy` 收到上述请求后，会在后台执行以下一系列操作：

1.  **强制指定响应格式**: `alia_proxy` 在将请求转发给上游服务（如 OpenAI）时，会**强制注入** `"response_format": "b64_json"` 参数。这要求上游服务返回 Base64 编码的图像数据，而不是一个临时的 URL。

2.  **解码与保存**:
    - `ProxyService` 收到包含 `b64_json` 字段的响应。
    - 它会立即对 Base64 字符串进行解码，得到原始的图像二进制数据（例如 PNG 或 JPEG）。
    - `MediaService` (`save_media`) 被调用，将这些二进制数据异步保存到 `data/media/` 目录下，并为其生成一个基于 UUID 的唯一文件名，例如 `a1b2c3d4-....png`。

3.  **响应内容重写**:
    - 在将最终响应返回给客户端之前，`alia_proxy` 会修改响应体：
        - 删除原始的 `b64_json` 字段。
        - 将 `url` 字段的值**替换**为指向 `alia_proxy` 内部媒体服务的本地 URL。

**客户端收到的最终响应**:

```json
{
  "created": 1700000000,
  "data": [
    {
      "url": "/api/media/a1b2c3d4-....png"
    }
  ]
}
```

## 优势

- **数据持久性**: 您无需担心上游服务提供的临时 URL 会过期。所有生成的图像都由您自己掌控，存储在 `alia_proxy` 的本地存储中。
- **简化客户端**: 客户端应用可以直接使用 `alia_proxy` 返回的相对 URL (`/api/media/...`) 来展示图片，无需处理 Base64 解码或复杂的图片存储逻辑。
- **统一访问**: 所有媒体资源都通过统一的 `/api/media/` 端点提供服务，便于管理和鉴权。
- **日志关联**: 生成的媒体文件路径会自动记录在对应的请求日志中，方便在仪表盘中查看和溯源。

## 输入图像的处理

对于多模态聊天请求中用户输入的图像（例如，上传一张图片让模型进行描述），`alia_proxy` 同样会进行拦截和持久化处理。

- **行为**: 如果 `messages` 中包含 `data:image/...` 格式的 Base64 图片，`ProxyService` 会在请求的预处理阶段就将其保存到本地。
- **日志记录**: 为了避免数据库被巨大的 Base64 字符串撑爆，日志中只会记录一个指向本地文件的占位符，例如 `[IMAGE: a1b2c3d4-....png]`。原始的 Base64 数据仅在内存中处理并转发给上游模型，不会存入数据库。
