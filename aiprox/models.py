from tortoise.models import Model
from tortoise import fields


class RequestLog(Model):
    """
    请求日志元数据模型。
    存储请求的核心统计信息，用于高性能分析。
    """

    id = fields.IntField(pk=True)  # 内部 ID
    request_id = fields.CharField(
        max_length=100, null=True, db_index=True
    )  # 提供商返回的原始请求ID
    timestamp = fields.DatetimeField(auto_now_add=True, db_index=True)  # 时间戳
    date = fields.DateField(db_index=True)  # 日期 (用于加速分析查询)
    provider = fields.CharField(max_length=100, db_index=True)  # 提供商名称
    endpoint = fields.CharField(max_length=100, db_index=True)  # 端点名称
    model = fields.CharField(max_length=100, db_index=True)  # 模型名称
    request_model = fields.CharField(
        max_length=100, null=True, db_index=True
    )  # 用户请求的原始模型名称
    prompt_tokens = fields.IntField(default=0)  # 提示词消耗的 Token 数
    completion_tokens = fields.IntField(default=0)  # 补全词消耗的 Token 数
    total_tokens = fields.IntField(default=0, db_index=True)  # 总消耗 Token 数
    status_code = fields.IntField(db_index=True)  # HTTP 状态码
    latency = fields.FloatField(default=0.0, db_index=True)  # 请求耗时 (秒)
    is_streaming = fields.BooleanField(default=False, db_index=True)  # 是否为流式请求
    ip_address = fields.CharField(max_length=45, null=True, db_index=True)  # IP 地址
    metadata = fields.JSONField(null=True)  # 额外的元数据

    content: fields.OneToOneRelation["RequestContent"]
    media: fields.ReverseRelation["MediaResource"]

    class Meta:  # type: ignore
        table = "requestlog"
        indexes = [
            ("date", "provider"),
            ("date", "model"),
        ]


class RequestContent(Model):
    """
    请求内容模型。
    存储大文本内容 (Prompt/Response)，支持单独的生命周期管理。
    """

    id = fields.IntField(pk=True)
    log = fields.OneToOneField(
        "models.RequestLog", related_name="content", on_delete=fields.CASCADE
    )
    prompt = fields.TextField(null=True)  # 请求内容
    response = fields.TextField(null=True)  # 响应内容
    error = fields.TextField(null=True)  # 错误详情

    class Meta:  # type: ignore
        table = "requestcontent"


class MediaResource(Model):
    """
    媒体资源模型。
    记录请求关联的图片、音频等文件。
    """

    id = fields.IntField(pk=True)
    log = fields.ForeignKeyField(
        "models.RequestLog", related_name="media", on_delete=fields.CASCADE
    )
    file_path = fields.CharField(max_length=255)  # 文件路径
    file_type = fields.CharField(max_length=50)  # 媒体类型 (image/audio)
    mime_type = fields.CharField(max_length=100, null=True)  # MIME 类型
    size = fields.IntField(default=0)  # 文件大小 (字节)

    class Meta:  # type: ignore
        table = "mediaresource"
