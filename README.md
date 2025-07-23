# 转换工具集后端API

⭐ 如果这个项目对你有帮助，请给一个Star！

## 项目简介

这是一个基于 FastAPI 的异步文件转换工具集，提供 Markdown 格式转换、文件处理等功能的 RESTful API 服务。

## 功能特性

- **Markdown 格式转换**: 支持多种 Markdown 格式之间的相互转换
- **异步任务处理**: 基于 Celery 的异步任务队列，支持大文件处理
- **文件存储**: 集成 MinIO 对象存储，支持文件上传下载
- **API 文档**: 自动生成 OpenAPI 文档，提供交互式 API 测试界面
- **容器化部署**: 完整的 Docker 容器化支持

## 技术栈

- **后端**: FastAPI + Python 3.9+
- **任务队列**: Celery + Redis
- **文件存储**: MinIO
- **容器化**: Docker + Docker Compose
- **前端**: 原生 HTML/JS/CSS

## 快速开始

### 环境要求

- Docker 和 Docker Compose
- Python 3.9+ (开发环境)

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd tools-api

# 复制环境配置
cp env.example .env

# 启动所有服务
./scripts/start-services.sh
```

### 手动部署

```bash
# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

## 开发环境

### 本地开发

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API 文档

启动服务后，访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
tools-api/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── schema/         # 数据模型
│   │   ├── services/       # 业务服务
│   │   └── tasks/          # 异步任务
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端界面
├── scripts/               # 脚本工具
├── tests/                 # 测试文件
├── docker-compose.yaml    # Docker 配置
└── README.md             # 项目文档
```

## API 接口

### 主要接口

- `POST /api/v1/md-conv/async-convert` - 异步转换 Markdown 文件
- `GET /api/v1/md-conv/status/{task_id}` - 查询转换任务状态
- `GET /api/v1/md-conv/download/{task_id}` - 下载转换结果

### 使用示例

```bash
# 提交转换任务
curl -X POST "http://localhost:8000/api/v1/md-conv/async-convert" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@input.md" \
  -F "target_format=html"

# 查询任务状态
curl "http://localhost:8000/api/v1/md-conv/status/{task_id}"

# 下载结果
curl "http://localhost:8000/api/v1/md-conv/download/{task_id}" -o output.html
```

## 配置说明

### 环境变量

复制 `env.example` 为 `.env` 并配置以下参数：

```bash
# MinIO 配置
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=password
MINIO_ENDPOINT=localhost:9000

# Redis 配置
REDIS_URL=redis://localhost:6379

# 应用配置
APP_ENV=development
DEBUG=True
```

## 测试

```bash
# 运行测试
cd backend
pytest

# 运行特定测试
pytest app/api/v1/md_conv/test_example.py -v
```

## 部署指南

详细部署说明请参考 [DEPLOY.md](./DEPLOY.md)

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 支持

如有问题，请提交 [Issue](../../issues) 或联系维护者。 