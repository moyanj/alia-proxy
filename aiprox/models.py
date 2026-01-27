from tortoise.models import Model
from tortoise import fields


class RequestLog(Model):
    """
    请求日志记录模型。
    用于记录所有经过代理的 API 请求及其响应、令牌使用量和相关媒体文件。
    """

    id = fields.IntField(pk=True)  # 请求ID
    timestamp = fields.DatetimeField(auto_now_add=True)  # 时间戳
    provider = fields.CharField(max_length=100)  # 提供商名称 (例如: gpt4-main)
    endpoint = fields.CharField(max_length=100)  # 端点名称 (例如: chat/completions)
    model = fields.CharField(max_length=100)  # 使用的底层模型名称
    prompt = fields.TextField(null=True)  # 请求的原始内容
    response = fields.TextField(
        null=True
    )  # 响应的原始内容 (流式响应则记录合并后的内容)
    prompt_tokens = fields.IntField(default=0)  # 提示词消耗的 Token 数
    completion_tokens = fields.IntField(default=0)  # 补全词消耗的 Token 数
    total_tokens = fields.IntField(default=0)  # 总消耗 Token 数
    status_code = fields.IntField()  # HTTP 状态码
    media_path = fields.CharField(max_length=255, null=True)  # 关联媒体文件的本地路径
    error = fields.TextField(null=True)  # 发生的错误详情

    class Meta:  # type: ignore
        table = "requestlog"
