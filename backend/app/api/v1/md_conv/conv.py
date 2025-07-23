import io
import os
import tempfile
from typing import Optional, Union, BinaryIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from loguru import logger
import aiofiles

try:
    from markitdown import MarkItDown
except ImportError:
    raise ImportError("请安装 markitdown: pip install markitdown")


class MarkdownConverter:
    """Markdown 转换器服务类"""
    
    def __init__(self):
        self.markitdown = MarkItDown()
        # 支持的文件类型
        self.supported_extensions = {
            # 文档格式
            '.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
            # 图像格式
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
            # 音频格式 (需要AI服务支持)
            '.mp3', '.wav', '.m4a', '.flac',
            # 其他格式
            '.html', '.htm', '.csv', '.json', '.xml', '.txt',
            '.zip', '.epub'
        }
    
    async def convert_file_to_markdown(
        self, 
        file: Union[UploadFile, str, Path, bytes], 
        file_extension: str = None,
        **kwargs
    ) -> str:
        """
        将文件转换为 Markdown 格式
        
        Args:
            file: 上传的文件、文件路径或文件内容字节流
            file_extension: 文件扩展名（当file为bytes时需要）
            **kwargs: 额外的转换参数
            
        Returns:
            str: 转换后的 Markdown 内容
            
        Raises:
            HTTPException: 转换失败时抛出异常
        """
        try:
            if isinstance(file, UploadFile):
                return await self._convert_upload_file(file, **kwargs)
            elif isinstance(file, (str, Path)):
                return await self._convert_file_path(file, **kwargs)
            elif isinstance(file, bytes):
                return await self._convert_bytes(file, file_extension, **kwargs)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="不支持的文件类型"
                )
        except Exception as e:
            logger.error(f"文件转换失败: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"转换失败: {str(e)}"
            )
    
    async def _convert_upload_file(self, file: UploadFile, **kwargs) -> str:
        """转换上传的文件"""
        # 验证文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}. 支持的格式: {', '.join(sorted(self.supported_extensions))}"
            )
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            try:
                # 读取上传文件内容并写入临时文件
                content = await file.read()
                temp_file.write(content)
                temp_file.flush()
                
                # 转换文件
                result = self.markitdown.convert(temp_file.name, **kwargs)
                
                if result and hasattr(result, 'text_content'):
                    return result.text_content
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="转换结果为空"
                    )
                    
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file.name)
                except OSError:
                    pass
    
    async def _convert_file_path(self, file_path: Union[str, Path], **kwargs) -> str:
        """转换本地文件路径"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"文件不存在: {file_path}"
            )
        
        # 验证文件扩展名
        file_ext = file_path.suffix.lower()
        if file_ext not in self.supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}"
            )
        
        # 转换文件
        result = self.markitdown.convert(str(file_path), **kwargs)
        
        if result and hasattr(result, 'text_content'):
            return result.text_content
        else:
            raise HTTPException(
                status_code=500,
                detail="转换结果为空"
            )
    
    async def _convert_bytes(self, content: bytes, file_extension: str, **kwargs) -> str:
        """转换字节流内容"""
        if file_extension not in self.supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_extension}"
            )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            try:
                temp_file.write(content)
                temp_file.flush()
                
                # 转换文件
                result = self.markitdown.convert(temp_file.name, **kwargs)
                
                if result and hasattr(result, 'text_content'):
                    return result.text_content
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="转换结果为空"
                    )
                    
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file.name)
                except OSError:
                    pass
    
    async def convert_url_to_markdown(self, url: str, **kwargs) -> str:
        """
        将 URL 内容转换为 Markdown
        
        Args:
            url: 要转换的URL
            **kwargs: 额外的转换参数
            
        Returns:
            str: 转换后的 Markdown 内容
        """
        try:
            result = self.markitdown.convert(url, **kwargs)
            
            if result and hasattr(result, 'text_content'):
                return result.text_content
            else:
                raise HTTPException(
                    status_code=500,
                    detail="URL转换结果为空"
                )
                
        except Exception as e:
            logger.error(f"URL转换失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"URL转换失败: {str(e)}"
            )
    
    def get_supported_formats(self) -> list:
        """获取支持的文件格式列表"""
        return sorted(list(self.supported_extensions))


# 创建全局转换器实例
markdown_converter = MarkdownConverter()
