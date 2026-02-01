# 协议适配

`alia_proxy` 的核心价值之一在于其强大的协议适配能力。通过 Provider 层的抽象，`alia_proxy` 能够将来自不同 AI 提供商、具有不同 API 规范的服务，统一封装成符合 OpenAI API 标准的接口。

这意味着，您的客户端应用只需编写一次代码，就可以通过 `alia_proxy` 调用所有支持的模型，而无需关心底层 API 的差异。

本章节将详细介绍 `alia_proxy` 如何适配各个主流 AI 服务。
