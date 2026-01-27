import os
from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
import toml


class ProviderConfig(BaseModel):
    """
    单个 AI 提供商的配置模型。
    """

    type: str  # 提供商类型 (如: openai, anthropic, ollama)
    api_key: Optional[str] = None  # API 密钥
    base_url: Optional[str] = None  # 基础 URL (用于自建或代理服务)

    model_config = ConfigDict(extra="allow")


class Settings(BaseSettings):
    """
    应用全局设置模型。
    支持从环境变量 (前缀 AIPROX_) 加载。
    """

    debug: bool = False  # 调试模式
    database_url: str = "sqlite://data/aiprox.db"  # 数据库连接字符串
    media_dir: str = "data/media"  # 媒体文件存储目录
    providers: Dict[str, ProviderConfig] = {}  # 注册的提供商配置列表

    model_config = SettingsConfigDict(env_prefix="AIPROX_")


def load_config(config_path: str = "config.toml") -> Settings:
    """
    从指定路径加载 TOML 配置文件。
    如果文件不存在，则返回默认设置。
    """
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = toml.load(f)
            return Settings(**data)
    return Settings()


# 初始化全局设置实例
settings = load_config()
