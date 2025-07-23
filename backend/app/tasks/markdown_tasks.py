import os
from datetime import datetime

from loguru import logger

from backend.app.core.worker import celery_app
from backend.app.services.minio_client import minio_client
from backend.app.api.v1.md_conv.conv import MarkdownConverter


@celery_app.task(bind=True, max_retries=3)
def convert_file_to_markdown(self, task_data: dict):
    """
    Celery任务：将文件转换为Markdown格式
    
    Args:
        task_data: 包含任务信息的字典
            - original_object_name: 原始文件对象名
            - original_filename: 原始文件名
            - extract_images: 是否提取图像
            - user_id: 用户ID (可选)
    """
    original_object_name = task_data.get('original_object_name')
    original_filename = task_data.get('original_filename')
    extract_images = task_data.get('extract_images', False)
    user_id = task_data.get('user_id')
    
    try:
        logger.info(f"开始处理任务 {self.request.id}, 文件: {original_filename}")
        
        # 更新任务进度
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': 10,
                'filename': original_filename,
                'status': 'downloading'
            }
        )
        
        # 从MinIO下载文件到内存
        logger.info(f"从MinIO下载文件: {original_object_name}")
        file_content = minio_client.download_file_to_memory(original_object_name)
        
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': 30,
                'filename': original_filename,
                'status': 'converting'
            }
        )
        
        # 获取文件扩展名
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # 创建转换器实例
        converter = MarkdownConverter()
        
        # 转换文件内容 - 使用同步版本避免async问题
        markdown_content = _convert_sync(converter, file_content, file_extension, extract_images)
        
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': 80,
                'filename': original_filename,
                'status': 'uploading_result'
            }
        )
        
        # 上传转换结果到MinIO
        result_filename = f"{os.path.splitext(original_filename)[0]}.md"
        result_object_name = f"results/{self.request.id}/{result_filename}"
        minio_client.upload_file_from_memory(
            result_object_name, 
            markdown_content, 
            content_type="text/markdown"
        )
        
        # 生成下载URL
        download_url = minio_client.generate_download_url(result_object_name, result_filename)
        
        logger.info(f"任务 {self.request.id} 完成，结果文件: {result_object_name}")
        
        return {
            'status': 'completed',
            'task_id': self.request.id,
            'result_object_name': result_object_name,
            'download_url': download_url,
            'filename': result_filename,
            'original_filename': original_filename,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"任务 {self.request.id} 处理失败: {str(e)}")
        
        # 设置任务状态为失败
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'filename': original_filename
            }
        )
        
        # 重试机制
        if self.request.retries < 3:
            logger.info(f"任务 {self.request.id} 重试 {self.request.retries + 1}/3")
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        
        return {
            'status': 'failed',
            'task_id': self.request.id,
            'error': str(e),
            'filename': original_filename
        }


def _convert_sync(converter, file_content: bytes, file_extension: str, extract_images: bool) -> str:
    """
    同步转换文件内容为Markdown
    
    Args:
        converter: MarkdownConverter实例
        file_content: 文件内容字节流
        file_extension: 文件扩展名
        extract_images: 是否提取图像
    
    Returns:
        str: 转换后的Markdown内容
    """
    import tempfile
    from markitdown import MarkItDown
    
    try:
        # 使用临时文件进行转换
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_file_path = temp_file.name
        
        try:
            # 使用MarkItDown进行转换（同步调用）
            markitdown = MarkItDown()
            result = markitdown.convert(temp_file_path)
            
            if result and hasattr(result, 'text_content'):
                return result.text_content
            else:
                raise ValueError("转换结果为空")
                
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
                
    except Exception as e:
        logger.error(f"文件转换失败: {str(e)}")
        raise ValueError(f"转换失败: {str(e)}")