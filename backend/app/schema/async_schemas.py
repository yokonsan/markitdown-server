from typing import Optional, List
from pydantic import BaseModel, Field


class UploadUrlRequest(BaseModel):
    """获取上传链接请求模型"""
    filename: str = Field(..., description="文件名")
    content_type: Optional[str] = Field(None, description="文件MIME类型")


class UploadUrlResponse(BaseModel):
    """上传链接响应模型"""
    upload_url: str = Field(..., description="预签名上传URL")
    object_name: str = Field(..., description="MinIO中的对象名")
    file_id: str = Field(..., description="文件ID")
    expires_in: int = Field(..., description="URL过期时间（秒）")


class CreateTaskRequest(BaseModel):
    """创建转换任务请求模型"""
    object_name: str = Field(..., description="MinIO中的对象名")
    original_filename: str = Field(..., description="原始文件名")
    extract_images: bool = Field(False, description="是否提取图像内容")
    user_id: Optional[str] = Field(None, description="用户ID")


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    result: Optional[dict] = Field(None, description="任务结果数据")
    error: Optional[str] = Field(None, description="错误信息")
    filename: Optional[str] = Field(None, description="原始文件名")
    progress: Optional[int] = Field(None, description="进度百分比")


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    filename: str = Field(..., description="原始文件名")
    progress: int = Field(..., description="进度百分比")


class DownloadResponse(BaseModel):
    """下载响应模型"""
    download_url: str = Field(..., description="下载链接")
    filename: str = Field(..., description="文件名")
    expires_in: int = Field(..., description="过期时间（秒）")
