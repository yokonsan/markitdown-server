# 转换工具集后端API

> 基于FastAPI和MarkItDown的文件转换服务，集成完整的Context Engineering开发体系

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Context Engineering](https://img.shields.io/badge/Context%20Engineering-enabled-purple.svg)](https://github.com/coleam00/context-engineering-intro)

## 🎯 项目简介

这是一个现代化的文件转换服务后端，支持将各种格式的文件转换为Markdown格式。项目采用Context Engineering方法论，确保高质量的代码和一致的开发体验。

### 核心功能
- 📄 支持20+种文件格式转换
- 🌐 URL内容转换支持  
- 🔄 异步处理机制
- 🛡️ 完善的安全验证
- 📊 详细的转换报告
- 🎛️ RESTful API接口

### 支持格式
| 类型 | 格式 | 说明 |
|------|------|------|
| **文档** | PDF, DOCX, DOC, PPTX, PPT, XLSX, XLS | Office文档和PDF |
| **图像** | PNG, JPG, JPEG, GIF, BMP, TIFF, WebP | 图像内容识别 |
| **音频** | MP3, WAV, M4A, FLAC | 需要AI服务支持 |
| **Web** | HTML, HTM | 网页内容 |
| **数据** | CSV, JSON, XML | 结构化数据 |
| **其他** | TXT, ZIP, EPUB | 文本和压缩文件 |

## 🚀 快速开始

### 环境要求
- Python 3.11+
- pip 或 conda

### 安装和运行
```bash
# 克隆项目
git clone <repository-url>
cd tools-api

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 访问API
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/md-convert/health
- **支持格式**: http://localhost:8000/api/v1/md-convert/formats

## 📚 API使用示例

### 文件上传转换
```python
import requests

# 上传文件转换
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/v1/md-convert/upload', 
        files=files
    )
    result = response.json()
    print(result['markdown_content'])
```

### URL内容转换
```bash
curl -X POST "http://localhost:8000/api/v1/md-convert/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/page.html"}'
```

### 本地文件转换
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/md-convert/file-path',
    json={"file_path": "/path/to/local/file.docx"}
)
result = response.json()
```

## 🏗️ 项目架构

```
app/
├── api/                    # API层
│   ├── v1/                # API版本1
│   │   └── md_conv/       # 转换模块
│   │       ├── conv.py    # 核心转换逻辑
│   │       ├── routes.py  # API路由定义
│   │       └── schemas.py # 数据模型
│   ├── deps.py           # 依赖注入
│   ├── errors.py         # 错误处理
│   └── router.py         # 路由注册
└── utils/                # 工具函数（规划中）
```

## 🧠 Context Engineering

本项目采用先进的Context Engineering方法论，提供完整的AI辅助开发体系：

### 📁 Context Engineering文件结构
```
├── CLAUDE.md                      # 项目上下文规则
├── INITIAL.md                     # 功能请求模板  
├── CONTEXT_ENGINEERING_GUIDE.md   # 使用指南
├── .claude/                       # Claude Code配置
│   ├── settings.local.json        # 权限设置
│   └── commands/                  # 自定义命令
│       ├── generate-prp.md        # 生成PRP命令
│       └── execute-prp.md         # 执行PRP命令
├── PRPs/                          # 产品需求提示
│   └── templates/prp_base.md      # PRP基础模板
└── examples/                      # 代码示例
    ├── api_patterns.py            # API实现模式
    ├── data_models.py             # 数据模型模式
    └── README.md                  # 示例说明
```

### 🔧 开发工作流
1. **需求描述**: 编辑`INITIAL.md`描述功能需求
2. **生成PRP**: 运行`/generate-prp INITIAL.md`生成实施计划
3. **执行开发**: 运行`/execute-prp PRPs/功能名_prp.md`自动实施
4. **质量保证**: 自动化测试、代码审查、性能验证

### 📋 开发规范
- 遵循PEP 8代码风格
- 异步编程优先
- 完整的错误处理和日志记录
- 90%+测试覆盖率
- 详细的API文档

## 🧪 测试

```bash
# 运行测试示例
python app/api/v1/md_conv/test_example.py

# 运行完整测试套件（开发中）
pytest tests/

# 代码覆盖率检查
pytest --cov=app tests/
```

## 🔒 安全特性

- ✅ 严格的文件类型验证
- ✅ 文件大小限制（100MB）
- ✅ 路径注入防护
- ✅ 临时文件自动清理
- ✅ 异步处理避免阻塞
- ✅ 详细的错误日志记录

## 📈 性能指标

- 文件上传转换: < 30秒
- URL内容转换: < 10秒
- 健康检查: < 100ms
- 支持格式查询: < 50ms
- 并发处理能力: 多请求异步处理

## 🛠️ 配置选项

### 环境变量
```bash
# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# 文件处理
MAX_FILE_SIZE=104857600  # 100MB
SUPPORTED_FORMATS="pdf,docx,png,jpg,html,txt"

# AI服务（可选）
OPENAI_API_KEY=your_api_key
AZURE_SPEECH_KEY=your_speech_key
AZURE_SPEECH_REGION=your_region
```

## 📖 文档

- [API完整文档](./MARKDOWN_CONVERTER_OVERVIEW.md)
- [Context Engineering指南](./CONTEXT_ENGINEERING_GUIDE.md)
- [开发规范](./CLAUDE.md)
- [代码示例](./examples/)

## 🤝 贡献指南

### 添加新功能
1. 复制`INITIAL.md`模板，描述新功能需求
2. 运行`/generate-prp`生成实施计划
3. 运行`/execute-prp`自动实施功能
4. 提交Pull Request

### 代码贡献
1. Fork项目
2. 创建功能分支
3. 遵循项目规范开发
4. 确保测试通过
5. 提交Pull Request

## 📄 许可证

[指定许可证]

## 🙏 致谢

- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) - 核心转换引擎
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Context Engineering](https://github.com/coleam00/context-engineering-intro) - 开发方法论

## 📞 支持

- 🐛 问题报告: [GitHub Issues](./issues)
- 💬 讨论交流: [GitHub Discussions](./discussions)
- 📧 邮件联系: [联系邮箱]

---

⭐ 如果这个项目对你有帮助，请给一个Star！ 