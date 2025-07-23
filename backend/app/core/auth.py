import hashlib
import hmac
import time
from typing import Optional
from fastapi import HTTPException, Request
from loguru import logger

from app.core.config import API_SECRET_KEY, API_AUTH_ENABLED, API_AUTH_HEADER, API_TIMESTAMP_HEADER


class APIAuthMiddleware:
    """API认证中间件 - 使用HMAC-SHA256进行请求签名验证"""
    
    def __init__(self):
        self.secret_key = API_SECRET_KEY.encode('utf-8')
        self.auth_enabled = API_AUTH_ENABLED
        self.auth_header = API_AUTH_HEADER
        self.timestamp_header = API_TIMESTAMP_HEADER
        self.request_timeout = 300  # 5分钟
    
    def generate_signature(self, method: str, path: str, timestamp: int, body: bytes = b'') -> str:
        """生成请求签名"""
        # 构建签名字符串
        string_to_sign = f"{method.upper()}:{path}:{timestamp}:{body.decode('utf-8')}"
        
        # 使用HMAC-SHA256生成签名
        signature = hmac.new(
            self.secret_key,
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, signature: str, method: str, path: str, timestamp: int, body: bytes = b'') -> bool:
        """验证请求签名"""
        expected_signature = self.generate_signature(method, path, timestamp, body)
        return hmac.compare_digest(signature, expected_signature)
    
    def verify_timestamp(self, timestamp: int) -> bool:
        """验证时间戳是否在有效范围内"""
        current_time = int(time.time())
        return abs(current_time - timestamp) <= self.request_timeout
    
    async def __call__(self, request: Request):
        """中间件调用"""
        if not self.auth_enabled:
            return
        
        # 跳过健康检查端点
        if request.url.path.endswith("/health"):
            return
        
        # 获取签名和时间戳
        signature = request.headers.get(self.auth_header)
        timestamp_str = request.headers.get(self.timestamp_header)
        
        if not signature or not timestamp_str:
            raise HTTPException(
                status_code=401,
                detail="Missing authentication headers"
            )
        
        try:
            timestamp = int(timestamp_str)
        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Invalid timestamp format"
            )
        
        # 验证时间戳
        if not self.verify_timestamp(timestamp):
            raise HTTPException(
                status_code=401,
                detail="Request timestamp expired"
            )
        
        # 读取请求体
        body = await request.body()
        
        # 验证签名
        if not self.verify_signature(signature, request.method, request.url.path, timestamp, body):
            logger.warning(
                f"Invalid API signature for {request.method} {request.url.path} "
                f"from {request.client.host}"
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid API signature"
            )
        
        logger.debug(f"API authentication successful for {request.method} {request.url.path}")


# 创建中间件实例
api_auth_middleware = APIAuthMiddleware()


def generate_api_signature(method: str, path: str, body: str = "", secret_key: str = None) -> tuple[str, int]:
    """为前端生成API签名"""
    if secret_key is None:
        secret_key = API_SECRET_KEY
    
    timestamp = int(time.time())
    secret = secret_key.encode('utf-8')
    
    string_to_sign = f"{method.upper()}:{path}:{timestamp}:{body}"
    signature = hmac.new(
        secret,
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature, timestamp