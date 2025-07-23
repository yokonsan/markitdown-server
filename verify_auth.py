#!/usr/bin/env python3
"""
验证认证中间件修复
"""

import requests
import sys

def test_auth_fix():
    """测试认证修复"""
    API_BASE_URL = "http://127.0.0.1:8000/api/v1/async"
    
    print("🔍 测试认证中间件修复...")
    
    # 测试1: 无认证头
    print("\n1. 测试无认证头:")
    try:
        response = requests.get(f"{API_BASE_URL}/task/test123")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        if response.status_code == 401:
            print("   ✅ 正确返回401")
        else:
            print("   ❌ 未返回401")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试2: 健康检查端点
    print("\n2. 测试健康检查端点:")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 健康检查正常")
        else:
            print("   ❌ 健康检查异常")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

if __name__ == "__main__":
    test_auth_fix()