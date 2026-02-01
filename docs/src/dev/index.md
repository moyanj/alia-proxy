# 开发指南

本章专为希望对 `alia_proxy` 进行二次开发或贡献代码的开发者准备。

我们致力于维护一个代码整洁、架构清晰且易于扩展的项目。在开始之前，请先熟悉本项目的技术栈和代码规范。

## 项目结构

```
.
├── alia_proxy/           # 后端核心代码 (Python package)
│   ├── providers/        # AI 提供商实现 (OpenAI, Anthropic 等)
│   ├── routers/          # FastAPI 路由定义
│   ├── services/         # 核心业务逻辑 (Proxy, Log, Media)
│   ├── models.py         # 数据库模型 (Tortoise-ORM)
│   └── main.py           # 程序入口
├── frontend/             # 前端代码 (Vue 3)
│   ├── src/views/        # 页面视图组件
│   ├── src/stores/       # Pinia 状态管理
│   └── src/api/          # API 客户端封装
├── data/                 # 数据存储目录 (SQLite DB, Media files)
├── tests/                # 自动化测试用例
└── config.toml           # 配置文件
```

## 开发哲学

1.  **异步优先**: 后端全面拥抱 `asyncio`。所有 I/O 操作（数据库、网络请求、文件读写）必须是异步的，严禁使用阻塞调用。
2.  **类型安全**: 后端使用 Python Type Hints，前端使用 TypeScript。这是为了提高代码的可读性和减少运行时错误。
3.  **依赖注入**: FastAPI 的依赖注入系统 (`Depends`) 是模块间解耦的核心。不要在模块间直接导入具体的服务实例，而是通过依赖注入获取。
4.  **配置驱动**: 所有的行为差异（如超时、重试、模型映射）都应通过 `config.toml` 配置，而不是硬编码在业务逻辑中。
