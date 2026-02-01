# 语音合成 (TTS)

`aiprox` 支持 OpenAI 的文本转语音 (Text-to-Speech, TTS) 接口 (`/v1/audio/speech`)，同样集成了自动持久化功能，使得生成的音频文件可以被轻松管理和回放。

## 接口用法

调用方式与标准 OpenAI TTS 接口完全一致。

**请求示例**:

```bash
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai-tts/tts-1",
    "input": "你好，欢迎使用 aiprox 语音合成服务。",
    "voice": "alloy"
  }' \
  --output speech.mp3
```

- `model`: 指定 TTS 模型，遵循 `<provider_instance_name>/<model_identifier>` 格式。
- `input`: 要转换为语音的文本。
- `voice`: 选择一种声音（如 `alloy`, `echo`, `nova` 等）。

## 隐式行为：流式处理与持久化

与图像生成类似，`aiprox` 在处理 TTS 请求时，会在后台执行关键的增强操作：

1.  **转发请求**: `ProxyService` 将请求转发给上游的 TTS 服务。
2.  **接收音频流**: 上游服务会返回一个音频数据流（例如 MP3 格式）。
3.  **异步保存**:
    - `ProxyService` 接收到完整的音频二进制数据。
    - `MediaService` (`save_media`) 被调用，将这些二进制数据异步写入 `data/media/` 目录，并生成一个唯一的 UUID 文件名，例如 `b2c3d4e5-....mp3`。
4.  **日志记录**: 生成的音频文件名 `b2c3d4e5-....mp3` 会被自动记录到本次请求的日志条目中。
5.  **返回音频流**: 同时，原始的音频数据流会通过 FastAPI 的 `StreamingResponse` 直接返回给客户端。

客户端会收到纯粹的音频文件内容，可以将其保存为 `speech.mp3` 或直接在浏览器中播放。而服务器端则已经完成了该音频的归档和记录工作。

## 优势

- **自动归档**: 所有生成的语音片段都会被自动保存，无需开发者手动处理。
- **可追溯性**: 在 Web 仪表盘的日志详情页，您可以直接看到与该次 TTS 请求关联的音频文件，并支持在线播放，极大地提升了调试和审计的效率。
- **统一管理**: 与图片文件一样，所有音频文件都存储在统一的媒体目录下，并通过统一的 API 接口访问，简化了系统管理。
