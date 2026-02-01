# 在线演练场 (Playground)

Playground 是一个集成的开发环境，允许您直接在浏览器中与配置好的模型进行交互。这对于测试新模型效果、调试 Prompt 或验证 API 配置非常有用。

## 双模式编辑器

Playground 提供了两种互通的编辑模式：

1.  **Visual (可视化模式)**:
    - 类似 ChatGPT 的图形化界面。
    - 可以直观地添加 User、Assistant 消息，设置 System Prompt。
    - 支持拖拽排序和删除消息。

2.  **JSON (代码模式)**:
    - 直接编辑发送给 API 的 JSON `messages` 数组。
    - 适合粘贴现有的 Payload 进行复现，或者进行精细的字段调整。
    - **实时同步**: 在 JSON 模式下的修改会立即反映在 Visual 模式中，反之亦然。

## 功能特性

- **模型选择**: 下拉框会自动列出当前系统中所有可用的模型（按 Provider 分组）。
- **参数调整**: 支持调整 `Temperature` 和 `Stream`（流式输出）开关。
- **流式响应**: 完美支持打字机效果的流式输出展示，并实时显示已接收的 Token 数和响应时间。
- **一键复现**: 在“日志详情”页，点击 **"Playground"** 按钮，系统会将该条日志的完整上下文（System Prompt, User Messages, Parameters）自动加载到 Playground 中。这使得复现 Bug 或优化 Prompt 变得极其简单。

## 调试辅助

- **Output 面板**: 不仅显示模型的回复，还会显示最终的 HTTP 状态码、总耗时和 Token 统计。
- **错误展示**: 如果请求失败，面板会显示详细的错误信息（包括上游返回的原始错误信息），帮助快速定位问题（是 Key 余额不足？还是参数错误？）。
