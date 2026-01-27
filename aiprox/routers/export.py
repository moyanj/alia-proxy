"""
数据导出路由。
支持将对话日志导出为 ShareGPT、CSV 或 JSONL 格式，方便模型微调或数据分析。
"""

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import json
import csv
import io
from ..models import RequestLog
from enum import StrEnum

router = APIRouter()


class ExportFormat(StrEnum):
    """
    导出格式枚举。
    """

    SHAREGPT = "sharegpt"  # ShareGPT 格式 (用于模型微调)
    CSV = "csv"  # 通用 CSV 格式
    JSONL = "jsonl"  # 原始 JSONL 格式


@router.get("/api/export")
async def export_logs(format: ExportFormat = Query(ExportFormat.JSONL)):
    """
    导出聊天日志。
    支持多种格式，通过流式响应下载。
    """
    # 只导出聊天完成类型的日志
    chat_logs = await RequestLog.filter(endpoint="chat").all()

    # 如果没有找到任何 chat 日志，返回带有说明的空文件
    if not chat_logs:
        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["message"])
            writer.writerow(["No chat logs found"])
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=export.csv"},
            )
        else:
            return StreamingResponse(
                iter([""]),
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename=export.{format}"
                },
            )

    # 导出为 CSV 格式
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "timestamp",
                "provider",
                "endpoint",
                "model",
                "prompt_tokens",
                "completion_tokens",
                "status_code",
                "media_path",
                "prompt",
                "response",
            ]
        )
        for log in chat_logs:
            writer.writerow(
                [
                    log.id,
                    log.timestamp,
                    log.provider,
                    log.endpoint,
                    log.model,
                    log.prompt_tokens,
                    log.completion_tokens,
                    log.status_code,
                    log.media_path,
                    log.prompt,
                    log.response,
                ]
            )
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=export.csv"},
        )

    # 导出为 ShareGPT 格式 (对话格式)
    elif format == "sharegpt":
        sharegpt_logs = []
        for log in chat_logs:
            if log.prompt and log.response:
                try:
                    # 尝试解析原始 prompt 消息列表
                    messages = eval(log.prompt)
                    conversations = []
                    for m in messages:
                        role = "human" if m["role"] == "user" else "gpt"
                        conversations.append({"from": role, "value": m["content"]})
                    conversations.append({"from": "gpt", "value": log.response})
                    sharegpt_logs.append({"conversations": conversations})
                except:
                    # 解析失败则回退到简单的单轮对话
                    sharegpt_logs.append(
                        {
                            "conversations": [
                                {"from": "human", "value": log.prompt},
                                {"from": "gpt", "value": log.response},
                            ]
                        }
                    )

        if not sharegpt_logs:
            return StreamingResponse(
                iter([""]),
                media_type="application/x-jsonlines",
                headers={"Content-Disposition": "attachment; filename=export.jsonl"},
            )

        output = "\n".join([json.dumps(log) for log in sharegpt_logs])
        return StreamingResponse(
            iter([output]),
            media_type="application/x-jsonlines",
            headers={"Content-Disposition": "attachment; filename=export.jsonl"},
        )

    # 导出为原始 JSONL 格式
    elif format == "jsonl":
        jsonl_logs = []
        for log in chat_logs:
            jsonl_logs.append(
                {
                    "id": log.id,
                    "timestamp": str(log.timestamp),
                    "provider": log.provider,
                    "endpoint": log.endpoint,
                    "model": log.model,
                    "prompt_tokens": log.prompt_tokens,
                    "completion_tokens": log.completion_tokens,
                    "status_code": log.status_code,
                    "media_path": log.media_path,
                    "prompt": log.prompt,
                    "response": log.response,
                }
            )

        output = "\n".join([json.dumps(log) for log in jsonl_logs])
        return StreamingResponse(
            iter([output]),
            media_type="application/x-jsonlines",
            headers={"Content-Disposition": "attachment; filename=export.jsonl"},
        )
