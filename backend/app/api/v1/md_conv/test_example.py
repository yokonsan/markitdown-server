"""
Markdown 转换功能测试示例

运行此文件之前，请确保：
1. 已安装 markitdown: pip install markitdown
2. 服务器正在运行: uvicorn main:app --reload
3. 有测试文件可用
"""

import asyncio
import requests
import json
from pathlib import Path

BASE_URL = "https://api.any2md.cc/api/v1/md-convert"


def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_supported_formats():
    """测试获取支持格式列表"""
    print("📋 测试获取支持格式列表...")
    response = requests.get(f"{BASE_URL}/formats")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"支持的格式数量: {data['total_count']}")
    print(f"支持的格式: {', '.join(data['supported_formats'][:10])}..." if len(data['supported_formats']) > 10 else f"支持的格式: {', '.join(data['supported_formats'])}")
    print()


def test_url_conversion():
    """测试URL转换"""
    print("🌐 测试URL转换...")
    test_url = "https://httpbin.org/html"  # 测试用HTML页面
    
    payload = {
        "url": test_url,
        "extract_images": False
    }
    
    response = requests.post(f"{BASE_URL}/url", json=payload)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ 转换成功!")
            print(f"原始URL: {data['original_filename']}")
            print(f"Markdown内容 (前200字符): {data['markdown_content'][:200]}...")
        else:
            print(f"❌ 转换失败: {data['error_message']}")
    else:
        print(f"❌ 请求失败: {response.text}")
    print()


def test_file_upload():
    """测试文件上传转换"""
    print("📁 测试文件上传转换...")
    
    # 创建一个简单的HTML测试文件
    test_file_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>测试文档</title>
    </head>
    <body>
        <h1>这是一个测试标题</h1>
        <p>这是一个测试段落，包含一些<strong>粗体文本</strong>和<em>斜体文本</em>。</p>
        <ul>
            <li>列表项 1</li>
            <li>列表项 2</li>
            <li>列表项 3</li>
        </ul>
    </body>
    </html>
    """
    
    # 写入临时文件
    test_file_path = "test_document.html"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_file_content)
    
    try:
        # 上传文件
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/html')}
            data = {'extract_images': False}
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ 文件上传转换成功!")
                print(f"原始文件名: {result['original_filename']}")
                print(f"文件类型: {result['file_type']}")
                print(f"Markdown内容:\n{result['markdown_content']}")
            else:
                print(f"❌ 转换失败: {result['error_message']}")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    finally:
        # 清理测试文件
        try:
            Path(test_file_path).unlink()
        except FileNotFoundError:
            pass
    print()


def test_file_path_conversion():
    """测试本地文件路径转换"""
    print("📂 测试本地文件路径转换...")
    
    # 创建一个JSON测试文件
    test_data = {
        "title": "测试文档",
        "content": "这是一个测试JSON文件",
        "items": [
            {"name": "项目1", "value": 100},
            {"name": "项目2", "value": 200},
            {"name": "项目3", "value": 300}
        ],
        "metadata": {
            "created": "2024-01-01",
            "author": "测试作者"
        }
    }
    
    test_file_path = "test_data.json"
    
    # 写入测试文件
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    try:
        # 转换文件
        payload = {
            "file_path": test_file_path,
            "extract_images": False
        }
        
        response = requests.post(f"{BASE_URL}/file-path", json=payload)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ 本地文件转换成功!")
                print(f"文件名: {result['original_filename']}")
                print(f"文件类型: {result['file_type']}")
                print(f"Markdown内容:\n{result['markdown_content']}")
            else:
                print(f"❌ 转换失败: {result['error_message']}")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    finally:
        # 清理测试文件
        try:
            Path(test_file_path).unlink()
        except FileNotFoundError:
            pass
    print()


def main():
    """运行所有测试"""
    print("🚀 开始测试 Markdown 转换功能...")
    print("=" * 50)
    
    try:
        test_health_check()
        test_supported_formats()
        test_url_conversion()
        test_file_upload()
        test_file_path_conversion()
        
        print("✅ 所有测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行:")
        print("   uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    main() 