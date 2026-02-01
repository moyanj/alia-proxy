import os
import uuid
import aiofiles
from ..config import settings


async def save_media(content: bytes, extension: str) -> str:
    """
    保存二进制媒体内容到本地磁盘。
    :param content: 文件的二进制数据
    :param extension: 文件扩展名 (如 png, mp3)
    :return: 生成的唯一文件名
    """
    # 确保存储目录存在
    if not os.path.exists(settings.media_dir):
        os.makedirs(settings.media_dir, exist_ok=True)

    # 生成唯一的 UUID 文件名
    filename = f"{uuid.uuid4()}.{extension.strip('.')}"
    file_path = os.path.join(settings.media_dir, filename)

    # 异步写入文件内容
    async with aiofiles.open(file_path, mode="wb") as f:
        await f.write(content)

    return filename
