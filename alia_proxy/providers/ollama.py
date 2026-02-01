from .openai import OpenAIProvider
from .base import ProviderConfig, Optional


class OllamaProvider(OpenAIProvider):
    """
    Ollama 提供商实现类。
    由于 Ollama 提供了完善的 OpenAI 兼容接口，我们直接继承 OpenAIProvider。
    默认基础地址设为 http://localhost:11434/v1。
    """

    class Config(ProviderConfig):
        timeout: float = 60.0

    def __init__(self, config: Config):
        # Ollama 默认不需要 API Key，但 OpenAIProvider 需要一个非空字符串
        if not config.api_key:
            config.api_key = "ollama"
        if not config.base_url:
            config.base_url = "http://localhost:11434/v1"
        super().__init__(config)
