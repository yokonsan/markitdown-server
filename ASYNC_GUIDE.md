# 异步文件转换服务使用指南

## 🚀 新特性概览

本版本新增了基于MinIO和Celery的异步文件转换系统，解决了服务器压力和并发处理问题：

- 🗂️ **MinIO对象存储**：前端直接上传文件到对象存储，减轻服务器压力
- ⚡ **Celery异步处理**：后台异步处理转换任务，支持高并发
- 📊 **任务状态跟踪**：实时查询任务进度和状态
- 🔗 **预签名URL**：安全的文件上传和下载链接
- 🗑️ **自动清理**：过期文件自动清理

## 📋 API接口总览

### 异步转换流程

1. **获取上传URL** → 2. **上传文件到MinIO** → 3. **创建转换任务** → 4. **查询任务状态** → 5. **获取结果链接**

### 同步转换接口（原有）
- `POST /api/v1/md-convert/upload` - 直接上传文件转换
- `POST /api/v1/md-convert/url` - URL内容转换
- `POST /api/v1/md-convert/file-path` - 本地文件转换

### 异步转换接口（新增）
- `POST /api/v1/async/upload-url` - 获取MinIO上传链接
- `POST /api/v1/async/create-task` - 创建异步转换任务
- `GET /api/v1/async/task/{task_id}` - 查询任务状态
- `GET /api/v1/async/tasks` - 分页获取任务列表
- `GET /api/v1/async/download/{task_id}` - 获取结果下载链接
- `DELETE /api/v1/async/task/{task_id}` - 删除任务

## 🎯 异步转换使用示例

### 1. 获取上传链接
```bash
curl -X POST "http://localhost:8000/api/v1/async/upload-url" \
  -H "Content-Type: application/json" \
  -d '{"filename": "document.pdf"}'
```

返回示例：
```json
{
  "upload_url": "http://localhost:9000/markdown-converter/uploads/xxxxx.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256...",
  "object_name": "uploads/xxxxx.pdf",
  "file_id": "xxxxx",
  "expires_in": 3600
}
```

### 2. 前端上传文件到MinIO
前端可以直接使用返回的upload_url上传文件，无需经过后端：
```javascript
// 示例代码
const uploadFile = async (file, uploadUrl) => {
  const response = await fetch(uploadUrl, {
    method: 'PUT',
    body: file,
    headers: {
      'Content-Type': file.type
    }
  });
  return response.ok;
};
```

### 3. 创建转换任务
上传成功后，创建异步转换任务：
```bash
curl -X POST "http://localhost:8000/api/v1/async/create-task" \
  -H "Content-Type: application/json" \
  -d '{
    "object_name": "uploads/xxxxx.pdf",
    "original_filename": "document.pdf",
    "extract_images": false,
    "user_id": "user123"
  }'
```

返回示例：
```json
{
  "task_id": "task-uuid-here",
  "status": "pending",
  "original_filename": "document.pdf",
  "file_type": ".pdf",
  "progress": 0,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 4. 查询任务状态
```bash
curl "http://localhost:8000/api/v1/async/task/task-uuid-here"
```

返回示例：
```json
{
  "task_id": "task-uuid-here",
  "status": "completed",
  "original_filename": "document.pdf",
  "file_type": ".pdf",
  "progress": 100,
  "created_at": "2024-01-01T12:00:00Z",
  "started_at": "2024-01-01T12:00:05Z",
  "completed_at": "2024-01-01T12:00:30Z",
  "download_url": "http://localhost:9000/markdown-converter/results/task-uuid-here/document.md...",
  "result_filename": "document.md"
}
```

### 5. 获取结果下载链接
```bash
curl "http://localhost:8000/api/v1/async/download/task-uuid-here"
```

## 🛠️ 环境配置

### 必需服务
1. **MinIO** - 对象存储服务
2. **Redis** - Celery消息队列
3. **SQLite/MySQL** - 任务状态数据库

### Docker Compose配置
创建`docker-compose.yml`：
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  celery_worker:
    build: .
    command: celery -A app.core.celery worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - redis
      - minio
    volumes:
      - .:/app

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - redis
      - minio
    volumes:
      - .:/app

volumes:
  minio_data:
```

## 🚀 启动步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动基础服务
```bash
# 启动Redis
docker run -d -p 6379:6379 redis:7-alpine

# 启动MinIO
docker run -d -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置实际的连接信息
```

### 4. 启动服务
```bash
# 启动FastAPI服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动Celery worker（新终端）
celery -A app.core.celery worker --loglevel=info

# 启动Celery beat（可选，用于定时任务）
celery -A app.core.celery beat --loglevel=info
```

## 📊 性能优化建议

### 1. MinIO配置
- 使用SSD存储提高I/O性能
- 配置多个磁盘节点实现负载均衡
- 设置适当的存储桶策略

### 2. Celery优化
- 增加worker进程数：`celery -A app.core.celery worker --concurrency=4`
- 使用Redis集群处理大量任务
- 配置任务优先级队列

### 3. 数据库优化
- 使用PostgreSQL替代SQLite应对高并发
- 添加索引优化查询性能
- 定期清理过期任务记录

## 🔍 监控和日志

### Celery监控
```bash
# 安装Flower监控工具
pip install flower

# 启动监控面板
flower -A app.core.celery --port=5555
```

### 日志查看
- FastAPI日志：`logs/app.log`
- Celery日志：`logs/celery.log`
- MinIO日志：MinIO控制台

## 🔐 安全配置

### MinIO安全设置
- 修改默认的access key和secret key
- 启用HTTPS传输
- 配置访问策略和CORS规则

### API安全建议
- 添加用户认证和授权
- 限制上传文件类型和大小
- 设置任务数量限制防止滥用