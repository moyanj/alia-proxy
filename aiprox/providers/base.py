from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator, Union, Type
from pydantic import BaseModel
from ..config import ProviderConfig


class Function(BaseModel):
    """
    函数定义。
    """

    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class Tool(BaseModel):
    """
    工具定义。
    """

    type: str = "function"
    function: Function


class ToolCallFunction(BaseModel):
    """
    工具调用中的函数信息。
    """

    name: str
    arguments: str


class ToolCall(BaseModel):
    """
    工具调用详情。
    """

    id: str
    type: str = "function"
    function: ToolCallFunction


class ChatMessage(BaseModel):
    """
    单条聊天消息模型。
    支持多模态内容和工具调用。
    """

    role: str  # 角色 (如: system, user, assistant, tool)
    content: Optional[Union[str, List[Dict[str, Any]]]] = (
        None  # 消息内容 (字符串或多模态列表)
    )
    name: Optional[str] = None  # 对于 tool 角色，表示函数名 (旧版或某些提供商使用)
    tool_call_id: Optional[str] = None  # 对于 tool 角色，表示对应的调用 ID
    tool_calls: Optional[List[ToolCall]] = (
        None  # 对于 assistant 角色，表示模型生成的工具调用
    )


class ChatRequest(BaseModel):
    """
    聊天完成请求模型。
    参考 OpenAI Chat Completion API 标准。
    """

    model: str  # 使用的模型
    messages: List[ChatMessage]  # 消息列表
    temperature: Optional[float] = 1.0  # 采样温度
    top_p: Optional[float] = 1.0  # 核采样
    n: Optional[int] = 1  # 回复数
    max_tokens: Optional[int] = None  # 最大生成 Token 数
    stream: bool = False  # 是否启用流式响应
    stop: Optional[Union[str, List[str]]] = None  # 停止序列
    seed: Optional[int] = None  # 随机种子
    logprobs: Optional[bool] = None  # 是否返回 Logprobs
    top_logprobs: Optional[int] = None  # 返回的 Logprobs 数量
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    tools: Optional[List[Tool]] = None  # 可选的工具列表
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None  # 工具选择策略
    response_format: Optional[Dict[str, Any]] = None  # 响应格式


class Usage(BaseModel):
    """
    Token 使用量统计模型。
    """

    prompt_tokens: int = 0  # 提示词 Token 数
    completion_tokens: int = 0  # 补全词 Token 数
    total_tokens: int = 0  # 总 Token 数


class ChatCompletionChoice(BaseModel):
    """
    聊天完成响应中的单个选项。
    """

    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None
    logprobs: Optional[Any] = None


class ChatResponse(BaseModel):
    """
    聊天完成响应模型。
    参考 OpenAI Chat Completion API 标准。
    """

    id: str  # 响应唯一 ID
    object: str = "chat.completion"  # 对象类型
    created: int  # 创建时间戳
    model: str  # 实际使用的模型
    choices: List[ChatCompletionChoice]  # 生成的选项列表
    usage: Usage  # Token 使用情况


class BaseProvider(ABC):
    """
    所有 AI 提供商的抽象基类。
    定义了统一的接口，具体提供商 (如 OpenAI, Anthropic) 需继承并实现 these 方法。
    """

    Config: Type[ProviderConfig] = ProviderConfig

    def __init__(self, config: ProviderConfig):
        """
        初始化提供商。
        :param config: 提供商配置对象
        """
        self.config = config
        self.api_key = config.api_key
        self.base_url = config.base_url

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
