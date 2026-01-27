from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """
    单条聊天消息模型。
    """

    role: str  # 角色 (如: system, user, assistant)
    content: str  # 消息内容


class ChatRequest(BaseModel):
    """
    聊天完成请求模型。
    参考 OpenAI Chat Completion API 标准。
    """

    model: str  # 使用的模型
    messages: List[ChatMessage]  # 消息列表
    temperature: Optional[float] = 1.0  # 采样温度
    max_tokens: Optional[int] = None  # 最大生成 Token 数
    stream: bool = False  # 是否启用流式响应


class Usage(BaseModel):
    """
    Token 使用量统计模型。
    """

    prompt_tokens: int = 0  # 提示词 Token 数
    completion_tokens: int = 0  # 补全词 Token 数
    total_tokens: int = 0  # 总 Token 数


class ChatResponse(BaseModel):
    """
    聊天完成响应模型。
    参考 OpenAI Chat Completion API 标准。
    """

    id: str  # 响应唯一 ID
    object: str = "chat.completion"  # 对象类型
    created: int  # 创建时间戳
    model: str  # 实际使用的模型
    choices: List[Dict[str, Any]]  # 生成的选项列表
    usage: Usage  # Token 使用情况


class BaseProvider(ABC):
    """
    所有 AI 提供商的抽象基类。
    定义了统一的接口，具体提供商 (如 OpenAI, Anthropic) 需继承并实现这些方法。
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        初始化提供商。
        :param api_key: 访问 API 的密钥
        :param base_url: 可选的 API 基础 URL
        """
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        执行非流式聊天完成。
        """
        pass

    @abstractmethod
    async def stream(
        self, request: ChatRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        执行流式聊天完成。
        """
        if False:
            yield {}

    @abstractmethod
    async def image_gen(self, prompt: str, model: str) -> Dict[str, Any]:
        """
        执行图像生成。
        """
        pass

    @abstractmethod
    async def text_to_speech(self, text: str, model: str, voice: str) -> bytes:
        """
        执行文本转语音。
        """
        pass

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        获取该提供商支持的模型列表。
        """
        return []
