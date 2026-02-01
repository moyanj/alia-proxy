import random
from typing import Dict, Optional, Tuple, Type, List, Union
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .ollama import OllamaProvider
from ..config import settings, MappingConfig
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
    _mapping_indices: Dict[str, int] = {}  # 存储 mapping 轮换的当前索引

    @classmethod
    def clear_cache(cls):
        """
        清空实例缓存。用于配置重载时。
        """
        cls._instances.clear()
        cls._mapping_indices.clear()

    @classmethod
    def register(cls, provider_type: str, provider_class: Type[BaseProvider]):
        """
        动态注册新的提供商类型及其实现类。
        """
        cls._registry[provider_type] = provider_class

    @classmethod
    def resolve_model(cls, model_field: str) -> Tuple[str, str, List[str]]:
        """
        解析请求中的模型字段。
        支持从 settings.mapping 进行别名映射。
        支持多目标映射及轮换/随机策略。
        期望格式: <提供商配置名>/<模型标识符> (例如: gpt4-main/gpt-4o)
        :return: (提供商名称, 模型名称, 降级列表)
        """
        fallbacks = []
        # 1. 检查是否存在别名映射
        if model_field in settings.mapping:
            config = settings.mapping[model_field]

            # 处理 MappingConfig 对象
            if isinstance(config, MappingConfig):
                targets = config.targets
                strategy = config.strategy
                fallbacks = config.fallbacks
            # 处理 List[str] 简写
            elif isinstance(config, list):
                targets = config
                strategy = "round-robin"
            # 处理 str 简写
            else:
                targets = [config]
                strategy = "round-robin"

            if not targets:
                raise ValueError(f"No targets defined for mapping: {model_field}")

            # 根据策略选择目标
            if strategy == "random":
                target = random.choice(targets)
            else:  # round-robin
                idx = cls._mapping_indices.get(model_field, 0)
                target = targets[idx]
                cls._mapping_indices[model_field] = (idx + 1) % len(targets)

            model_field = target

        # 2. 标准解析格式
        if "/" in model_field:
            parts = model_field.split("/", 1)
            return parts[0], parts[1], fallbacks

        raise ValueError(
            f"Invalid model field format: {model_field}. Expected: <provider>/<model> or a mapped alias."
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
