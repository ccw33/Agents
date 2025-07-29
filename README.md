# AI Agent Web Service

一个统一的AI Agent服务平台，支持多个主流Agent框架，通过RESTful API对外提供服务。

## 🚀 特性

- **多框架支持**: 集成LangGraph、AutoGen、CrewAI三大主流Agent框架
- **统一API**: 提供一致的RESTful API接口，屏蔽底层框架差异
- **框架独立**: 各框架实现完全独立，互不干扰
- **易于扩展**: 模块化设计，轻松添加新的Agent框架
- **生产就绪**: 支持Docker部署，包含完整的监控和日志
- **类型安全**: 使用Pydantic进行数据验证和类型检查

## 📋 支持的框架

### LangGraph
- **描述**: LangChain团队开发的低级编排框架
- **特点**: 长期运行、有状态代理、持久化执行
- **文档**: https://langchain-ai.github.io/langgraph/

### AutoGen
- **描述**: 微软开发的多代理AI应用框架
- **特点**: 多代理对话、自主协作、人机交互
- **文档**: https://microsoft.github.io/autogen/

### CrewAI
- **描述**: 独立的轻量级多代理自动化框架
- **特点**: 团队协作、任务编排、流程控制
- **文档**: https://docs.crewai.com/

## 🏗️ 项目结构

```
Agents/
├── LICENSE                    # 开源协议
├── README.md                  # 项目说明
├── agent-frameworks/          # 各框架的Agent实现
│   ├── autogen/              # AutoGen框架实现
│   ├── crewai/               # CrewAI框架实现
│   └── langgraph/            # LangGraph框架实现
├── web-service/              # 统一Web服务
│   ├── app/                  # 应用代码
│   │   ├── api/              # API路由层
│   │   ├── core/             # 核心功能
│   │   ├── models/           # 数据模型
│   │   └── services/         # 业务逻辑层
│   ├── requirements.txt      # Python依赖
│   ├── Dockerfile           # Docker配置
│   └── docker-compose.yml   # Docker编排
├── scripts/                  # 部署和管理脚本
│   ├── setup.sh             # 项目初始化
│   └── start_services.sh    # 服务启动
└── docs/                     # 项目文档
    ├── api.md               # API文档
    ├── deployment.md        # 部署文档
    └── development.md       # 开发文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- Git
- Docker (可选)

### 2. 安装和配置

```bash
# 克隆项目
git clone <repository-url>
cd Agents

# 运行初始化脚本
./scripts/setup.sh

# 配置环境变量
cd web-service
cp .env.example .env
# 编辑.env文件，配置必要参数
```

### 3. 启动服务

```bash
# 开发模式
./scripts/start_services.sh dev

# Docker模式
./scripts/start_services.sh docker

# 生产模式
./scripts/start_services.sh prod
```

### 4. 验证安装

```bash
# 检查服务状态
curl http://localhost:8000/health

# 查看API文档
open http://localhost:8000/docs
```

## 📖 使用示例

### 统一API调用

```python
import requests

# 执行LangGraph Agent
response = requests.post('http://localhost:8000/api/v1/execute', json={
    "framework": "langgraph",
    "agent_type": "chat_agent",
    "input_data": {"message": "分析当前市场趋势"},
    "timeout": 300
})

result = response.json()
print(result["result"])
```

### 框架专用API

```python
# AutoGen多代理对话
response = requests.post('http://localhost:8000/api/v1/autogen/execute', json={
    "agent_config": "coding_team",
    "message": "写一个Python排序算法",
    "participants": ["coder", "reviewer"],
    "max_rounds": 5
})

# CrewAI团队执行
response = requests.post('http://localhost:8000/api/v1/crewai/execute', json={
    "crew_name": "research_crew",
    "inputs": {"topic": "人工智能发展趋势"},
    "process_type": "sequential"
})
```

## 🔧 配置说明

### 环境变量配置

```bash
# 基础配置
DEBUG=false
HOST=0.0.0.0
PORT=8000

# 框架路径
LANGGRAPH_PATH=../agent-frameworks/langgraph
AUTOGEN_PATH=../agent-frameworks/autogen
CREWAI_PATH=../agent-frameworks/crewai

# API密钥（如果需要）
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 性能配置

```bash
# Agent执行配置
AGENT_TIMEOUT=300
MAX_CONCURRENT_AGENTS=10

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 📚 文档

- [API文档](docs/api.md) - 详细的API接口说明
- [部署文档](docs/deployment.md) - 生产环境部署指南
- [开发文档](docs/development.md) - 开发和扩展指南

## 🧪 测试

```bash
cd web-service
source venv/bin/activate

# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=app tests/

# 运行特定测试
pytest tests/test_api/test_agents.py
```

## 🐳 Docker部署

```bash
# 构建和启动
cd web-service
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🔍 监控和日志

### 健康检查

```bash
# 基础健康检查
curl http://localhost:8000/health

# 详细健康检查
curl -X POST http://localhost:8000/api/v1/health \
     -H "Content-Type: application/json" \
     -d '{"check_frameworks": true}'
```

### 日志查看

```bash
# 开发模式：控制台输出
# 生产模式：/var/log/ai-agent/
# Docker模式：docker-compose logs
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 使用 Black 进行代码格式化
- 遵循 PEP 8 编码规范
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到问题或有疑问：

1. 查看 [文档](docs/)
2. 搜索现有的 [Issues](../../issues)
3. 创建新的 [Issue](../../issues/new)

## 🗺️ 路线图

- [ ] 添加更多Agent框架支持
- [ ] 实现Agent执行结果缓存
- [ ] 添加用户认证和权限管理
- [ ] 支持Agent执行流式输出
- [ ] 集成监控和告警系统
- [ ] 添加Agent性能分析工具

---

**注意**: 这是一个框架集成项目，具体的Agent实现需要在各个 `agent-frameworks/` 目录下完成。
