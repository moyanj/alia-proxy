"""
媒体文件访问路由。
负责提供通过接口生成的本地存储媒体文件 (图片、音频) 的访问。
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from ..config import settings

router = APIRouter()


@router.get("/api/media/{filename}")
async def get_media(filename: str):
    """
    通过文件名获取本地存储的媒体文件。
    """
    file_path = os.path.join(settings.media_dir, filename)
    # 判断文件是否允许访问
    if not os.path.isabs(file_path) or not os.path.commonprefix(
        [file_path, settings.media_dir]
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Media not found")
    # 返回文件响应
    return FileResponse(file_path)
