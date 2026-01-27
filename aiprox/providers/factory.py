from typing import Dict, Optional, Tuple, Type
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .ollama import OllamaProvider
from ..config import settings
from .base import BaseProvider


class ProviderFactory:
    """
    提供商工厂类。
    实现单例管理模式，按需实例化提供商并进行缓存。
    """

    _instances: Dict[str, BaseProvider] = {}  # 缓存已创建的提供商实例
    _registry: Dict[str, Type[BaseProvider]] = {  # 类型到实现类的映射注册表
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    @classmethod
    def register(cls, provider_type: str, provider_class: Type[BaseProvider]):
        """
        动态注册新的提供商类型及其实现类。
        """
        cls._registry[provider_type] = provider_class

    @classmethod
    def resolve_model(cls, model_field: str) -> Tuple[str, str]:
        """
        解析请求中的模型字段。
        期望格式: <提供商配置名>/<模型标识符> (例如: gpt4-main/gpt-4o)
        :return: (提供商名称, 模型名称)
        """
        if "/" in model_field:
            parts = model_field.split("/", 1)
            return parts[0], parts[1]

        raise ValueError(
            f"Invalid model field format: {model_field}. Expected: <provider>/<model>"
        )

    @classmethod
    def get_provider(cls, name: str) -> BaseProvider:
        """
        根据配置名称获取对应的提供商实例。
        如果实例不存在则根据 config.toml 中的配置进行创建。
        """
        if name in cls._instances:
            return cls._instances[name]

        # 从全局设置中查找指定名称的配置
        config = settings.providers.get(name)
        if not config:
            raise ValueError(f"Provider instance '{name}' not found in config.")

        provider_type = config.type

        # 从注册表中查找对应的实现类
        provider_cls = cls._registry.get(provider_type)
        if not provider_cls:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        # 使用提供商自定义的 Config 模型进行验证
        validated_config = provider_cls.Config(**config.model_dump())

        # 实例化并缓存
        provider = provider_cls(config=validated_config)
        cls._instances[name] = provider
        return provider
