#!/usr/bin/env python3
"""
API认证测试脚本
用于验证前后端加密认证系统是否正确工作
"""

import requests
import json
import time
import hashlib
import hmac
import sys

def generate_signature(secret_key: str, method: str, path: str, timestamp: int, body: str = "") -> str:
    """生成请求签名"""
    string_to_sign = f"{method.upper()}:{path}:{timestamp}:{body}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def test_api_auth():
    """测试API认证"""
    API_BASE_URL = "http://127.0.0.1:8000/api/v1/async"
    API_SECRET_KEY = "your-secret-key-change-this-in-production"
    
    # 测试健康检查端点（不需要认证）
    print("测试1: 健康检查端点（不需要认证）")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print("✅ 健康检查通过\n")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}\n")
        return False
    
    # 测试需要认证的端点 - 无签名
    print("测试2: 需要认证的端点 - 无签名")
    try:
        response = requests.get(f"{API_BASE_URL}/task/test-task-id")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        if response.status_code == 401:
            print("✅ 无签名请求被拒绝\n")
        else:
            print("❌ 无签名请求未被拒绝\n")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False
    
    # 测试需要认证的端点 - 有效签名
    print("测试3: 需要认证的端点 - 有效签名")
    try:
        method = "GET"
        path = "/api/v1/async/task/test-task-id"
        timestamp = int(time.time())
        
        signature = generate_signature(API_SECRET_KEY, method, path, timestamp)
        
        headers = {
            "X-API-Signature": signature,
            "X-API-Timestamp": str(timestamp)
        }
        
        response = requests.get(f"{API_BASE_URL}/task/test-task-id", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        if response.status_code == 404:  # 任务不存在是正常的
            print("✅ 认证成功，任务不存在是正常的\n")
        else:
            print("❌ 认证失败\n")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False
    
    # 测试过期时间戳
    print("测试4: 过期时间戳")
    try:
        method = "GET"
        path = "/api/v1/async/task/test-task-id"
        timestamp = int(time.time()) - 400  # 6分钟前
        
        signature = generate_signature(API_SECRET_KEY, method, path, timestamp)
        
        headers = {
            "X-API-Signature": signature,
            "X-API-Timestamp": str(timestamp)
        }
        
        response = requests.get(f"{API_BASE_URL}/task/test-task-id", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        if response.status_code == 401 and "expired" in response.text.lower():
            print("✅ 过期时间戳被拒绝\n")
        else:
            print("❌ 过期时间戳未被拒绝\n")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False
    
    print("🎉 所有测试通过！API认证系统正常工作")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        API_SECRET_KEY = sys.argv[1]
    else:
        API_SECRET_KEY = "your-secret-key-change-this-in-production"
    
    test_api_auth()