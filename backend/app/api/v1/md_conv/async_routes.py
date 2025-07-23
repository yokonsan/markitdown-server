from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger
from celery.result import AsyncResult

from app.services.minio_client import minio_client
from app.schema.async_schemas import UploadUrlRequest, UploadUrlResponse, CreateTaskRequest, TaskResponse, DownloadResponse
from app.tasks.markdown_tasks import convert_file_to_markdown

router = APIRouter(
    prefix="/async",
    tags=["异步转换"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/upload-url",
    response_model=UploadUrlResponse,
    summary="获取文件上传预签名URL",
    description="获取用于直接上传到MinIO的预签名URL，前端可以直接上传到对象存储"
)
async def get_upload_url(request: UploadUrlRequest):
    """
    获取文件上传预签名URL
    
    - 前端使用返回的upload_url直接上传文件到MinIO
    - 上传成功后，调用/create-task接口创建转换任务
    - 支持的文件格式参考/markdown/formats接口
    """
    try:
        result = minio_client.generate_upload_url(
            filename=request.filename,
            content_type=request.content_type
        )
        return UploadUrlResponse(**result)
    except Exception as e:
        logger.error(f"生成上传URL失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成上传URL失败: {str(e)}")


@router.post(
    "/create-task",
    response_model=dict,
    summary="创建转换任务",
    description="上传文件到MinIO后，创建异步转换任务"
)
async def create_conversion_task(request: CreateTaskRequest):
    """
    创建Markdown转换任务
    
    - 前端上传文件到MinIO后，调用此接口创建转换任务
    - 任务将在后台异步处理
    - 使用/task/{task_id}接口查询任务状态
    """
    try:
        # 检查文件是否存在
        # if not minio_client.object_exists(request.object_name):
        #     raise HTTPException(status_code=404, detail="文件不存在于对象存储")
        
        # 提交Celery任务
        task_data = {
            "original_object_name": request.object_name,
            "original_filename": request.original_filename,
            "extract_images": request.extract_images,
            "user_id": request.user_id,
        }
        task = convert_file_to_markdown.delay(task_data)
        
        logger.info(f"创建转换任务: {task.id}, 文件: {request.original_filename}")
        
        return {
            "task_id": task.id,
            "status": "pending",
            "filename": request.original_filename,
            "message": "任务已创建，正在处理中"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建转换任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建转换任务失败: {str(e)}")


@router.get(
    "/task/{task_id}",
    response_model=TaskResponse,
    summary="查询任务状态",
    description="根据任务ID查询转换任务的详细状态和进度"
)
async def get_task_status(task_id: str):
    """
    查询任务状态
    - PENDING: 等待处理
    - PROCESSING: 正在处理
    - SUCCESS: 处理完成
    - FAILURE: 处理失败
    - RETRY: 重试中
    """
    try:
        task = AsyncResult(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 构建响应
        response = {
            "task_id": task_id,
            "status": task.status,
            "filename": None,
            "progress": None,
            "result": None,
            "error": None
        }
        
        # 获取任务信息
        if task.status == 'PENDING':
            response.update({
                "status": "pending",
                "message": "任务等待处理"
            })
        elif task.status == 'PROCESSING':
            meta = task.info or {}
            response.update({
                "status": "processing",
                "filename": meta.get('filename'),
                "progress": meta.get('progress', 0),
                "message": meta.get('status', '正在处理')
            })
        elif task.status == 'SUCCESS':
            result = task.result or {}
            response.update({
                "status": "completed",
                "filename": result.get('original_filename'),
                "result": result,
                "message": "任务处理完成"
            })
        elif task.status == 'FAILURE':
            response.update({
                "status": "failed",
                "error": str(task.result) if task.result else "任务处理失败",
                "message": "任务处理失败"
            })
        elif task.status == 'RETRY':
            response.update({
                "status": "retry",
                "message": "任务重试中"
            })
        
        return response
    except Exception as e:
        logger.error(f"查询任务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询任务状态失败: {str(e)}")


@router.get(
    "/download/{task_id}",
    response_model=DownloadResponse,
    summary="获取结果下载链接",
    description="获取转换结果的下载链接"
)
async def get_download_url(task_id: str):
    """获取转换结果下载链接"""
    try:
        task = AsyncResult(task_id)
        
        if not task or task.status != 'SUCCESS':
            raise HTTPException(status_code=404, detail="任务不存在或未完成")
        
        result = task.result
        if not result or 'download_url' not in result:
            raise HTTPException(status_code=404, detail="结果文件不存在")
        
        # 重新生成下载URL（防止过期）
        download_url = minio_client.generate_download_url(
            result['result_object_name'],
            result['filename']
        )
        
        return DownloadResponse(
            download_url=download_url,
            filename=result['filename'],
            expires_in=3600  # 1小时
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取下载链接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取下载链接失败: {str(e)}")


@router.delete(
    "/task/{task_id}",
    summary="删除任务",
    description="删除转换任务及其相关文件"
)
async def delete_task(task_id: str, background_tasks: BackgroundTasks):
    """删除转换任务及其文件"""
    try:
        task = AsyncResult(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 如果是成功完成的任务，清理结果文件
        if task.status == 'SUCCESS':
            result = task.result
            if result and 'result_object_name' in result:
                try:
                    minio_client.delete_object(result['result_object_name'])
                except Exception as e:
                    logger.warning(f"清理结果文件失败: {str(e)}")
        
        # 清理原始文件（需要知道原始对象名，这里简化处理）
        # 实际应用中可能需要额外信息
        
        # 取消正在执行的任务
        if task.status in ['PENDING', 'PROCESSING']:
            task.revoke(terminate=True)
        
        logger.info(f"删除任务: {task_id}")
        return {"message": "任务已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@router.get(
    "/health",
    summary="异步服务健康检查",
    description="检查异步转换服务是否正常运行"
)
async def health_check():
    """异步服务健康检查"""
    try:
        # 检查Celery连接
        from app.core.worker import celery_app
        result = celery_app.control.inspect()
        
        return {
            "status": "healthy",
            "service": "async-markdown-converter",
            "celery_status": "connected" if result else "disconnected",
            "supported_formats": [
                ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
                ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp",
                ".mp3", ".wav", ".m4a", ".flac", ".html", ".htm", ".csv",
                ".json", ".xml", ".txt", ".zip", ".epub"
            ]
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="异步转换服务不可用"
        )