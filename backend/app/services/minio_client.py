import io
import os
from datetime import timedelta
from typing import Union
import uuid

from minio import Minio
from minio.error import S3Error
from loguru import logger

from backend.app.core.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_SECURE,
    MINIO_BUCKET_NAME,
    MINIO_PRESIGNED_EXPIRE_SECONDS,
)


class MinioClient:
    """MinIO客户端封装类"""
    
    def __init__(self):
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
        self.bucket_name = MINIO_BUCKET_NAME
        self.ensure_bucket_exists()
    
    def ensure_bucket_exists(self):
        """确保存储桶存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"创建存储桶: {self.bucket_name}")
            else:
                logger.info(f"存储桶已存在: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"检查/创建存储桶失败: {e}")
            raise
    
    def generate_upload_url(self, filename: str, content_type: str = None) -> dict:
        """
        生成文件上传的预签名URL
        
        Args:
            filename: 原始文件名
            content_type: 文件MIME类型
            
        Returns:
            dict: 包含上传URL和文件对象名的字典
        """
        try:
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(filename)[1]
            object_name = f"uploads/{file_id}{file_extension}"
            
            presigned_url = self.client.presigned_put_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=MINIO_PRESIGNED_EXPIRE_SECONDS)
            )
            
            return {
                "upload_url": presigned_url,
                "object_name": object_name,
                "file_id": file_id,
                "expires_in": MINIO_PRESIGNED_EXPIRE_SECONDS
            }
        except S3Error as e:
            logger.error(f"生成上传URL失败: {e}")
            raise
    
    def generate_download_url(self, object_name: str, filename: str = None) -> str:
        """
        生成文件下载的预签名URL
        
        Args:
            object_name: MinIO中的对象名
            filename: 下载时的文件名（可选）
            
        Returns:
            str: 预签名下载URL
        """
        try:
            response_headers = {}
            if filename:
                response_headers["response-content-disposition"] = f'attachment; filename="{filename}"'
            
            download_url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=MINIO_PRESIGNED_EXPIRE_SECONDS),
                response_headers=response_headers
            )
            return download_url
        except S3Error as e:
            logger.error(f"生成下载URL失败: {e}")
            raise
    
    def download_file_to_memory(self, object_name: str) -> bytes:
        """
        从MinIO下载文件到内存
        
        Args:
            object_name: MinIO中的对象名
            
        Returns:
            bytes: 文件内容
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            content = response.read()
            response.close()
            return content
        except S3Error as e:
            logger.error(f"下载文件失败 {object_name}: {e}")
            raise
    
    def upload_file_from_memory(self, object_name: str, content: Union[str, bytes], content_type: str = None) -> str:
        """
        上传文件到MinIO
        
        Args:
            object_name: MinIO中的对象名
            content: 文件内容
            content_type: 文件MIME类型
            
        Returns:
            str: 上传的对象名
        """
        try:
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            file_size = len(content)
            content_stream = io.BytesIO(content)
            
            self.client.put_object(
                self.bucket_name,
                object_name,
                content_stream,
                file_size,
                content_type=content_type or 'application/octet-stream'
            )
            return object_name
        except S3Error as e:
            logger.error(f"上传文件失败 {object_name}: {e}")
            raise
    
    def delete_object(self, object_name: str):
        """删除对象"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"删除对象: {object_name}")
        except S3Error as e:
            logger.error(f"删除对象失败 {object_name}: {e}")
            raise
    
    def object_exists(self, object_name: str) -> bool:
        """检查对象是否存在"""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            raise


# 创建全局MinIO客户端实例
minio_client = MinioClient()