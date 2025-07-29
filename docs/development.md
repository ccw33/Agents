# AI Agent Web Service 开发文档

## 概述

本文档介绍如何开发和扩展AI Agent Web Service，包括架构设计、开发规范、测试指南等。

## 项目架构

### 整体架构

```
Agents/
├── agent-frameworks/          # 各框架的Agent实现
│   ├── langgraph/            # LangGraph框架
│   ├── autogen/              # AutoGen框架
│   └── crewai/               # CrewAI框架
├── web-service/              # 统一Web服务
│   ├── app/                  # 应用代码
│   │   ├── api/              # API路由层
│   │   ├── core/             # 核心功能
│   │   ├── models/           # 数据模型
│   │   └── services/         # 业务逻辑层
│   ├── requirements.txt      # 依赖管理
│   └── Dockerfile           # Docker配置
├── scripts/                  # 部署脚本
└── docs/                    # 项目文档
```

### 服务层架构

```
┌─────────────────┐
│   API Layer     │  ← FastAPI路由
├─────────────────┤
│ Business Logic  │  ← 服务抽象层
├─────────────────┤
│ Framework Layer │  ← 各框架适配器
├─────────────────┤
│ Agent Execution │  ← 子进程调用
└─────────────────┘
```

## 开发环境设置

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd Agents

# 运行初始化脚本
./scripts/setup.sh

# 激活虚拟环境
cd web-service
source venv/bin/activate
```

### 2. 开发工具配置

#### VS Code配置

创建 `.vscode/settings.json`：

```json
{
    "python.defaultInterpreterPath": "./web-service/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### 代码格式化配置

创建 `web-service/pyproject.toml`：

```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### 3. 启动开发服务器

```bash
# 使用脚本启动
./scripts/start_services.sh dev

# 或手动启动
cd web-service
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 开发规范

### 代码风格

- 使用 **Black** 进行代码格式化
- 使用 **isort** 进行导入排序
- 使用 **flake8** 进行代码检查
- 遵循 **PEP 8** 规范

```bash
# 格式化代码
black app/
isort app/

# 代码检查
flake8 app/
```

### 命名规范

- **文件名**: 使用下划线分隔 (`agent_service.py`)
- **类名**: 使用驼峰命名 (`AgentService`)
- **函数名**: 使用下划线分隔 (`execute_agent`)
- **常量**: 使用大写字母 (`MAX_TIMEOUT`)
- **私有方法**: 以下划线开头 (`_internal_method`)

### 文档规范

- 所有公共函数必须有docstring
- 使用Google风格的docstring
- 重要的类和模块需要模块级docstring

```python
def execute_agent(
    self,
    agent_type: str,
    input_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    执行指定类型的Agent
    
    Args:
        agent_type: Agent类型名称
        input_data: 输入数据字典
        config: 可选的配置参数
        
    Returns:
        包含执行结果的字典
        
    Raises:
        AgentExecutionError: 当Agent执行失败时
        AgentTimeoutError: 当执行超时时
    """
    pass
```

## 添加新框架

### 1. 创建框架目录

```bash
mkdir agent-frameworks/new-framework
cd agent-frameworks/new-framework
```

### 2. 实现框架服务

创建 `web-service/app/services/new_framework_service.py`：

```python
from app.services.agent_service import AgentService
from app.core.config import get_agent_framework_path

class NewFrameworkService(AgentService):
    """新框架服务实现"""
    
    def __init__(self):
        super().__init__("new-framework")
        self.framework_path = get_agent_framework_path("new-framework")
    
    async def execute_agent(self, agent_type: str, input_data: dict, config: dict = None, timeout: int = 300):
        # 实现具体的执行逻辑
        pass
    
    async def list_available_agents(self):
        # 实现获取可用Agent列表的逻辑
        pass
    
    async def validate_agent_config(self, agent_type: str, config: dict):
        # 实现配置验证逻辑
        pass
```

### 3. 添加API路由

创建 `web-service/app/api/v1/new_framework.py`：

```python
from fastapi import APIRouter
from app.services.agent_service import AgentServiceFactory

router = APIRouter()

@router.post("/execute")
async def execute_new_framework(request: NewFrameworkRequest):
    service = AgentServiceFactory.get_service("new-framework")
    # 实现API逻辑
    pass
```

### 4. 注册服务

在 `web-service/app/api/v1/agents.py` 中注册新服务：

```python
from app.services.new_framework_service import NewFrameworkService

def initialize_services():
    # 注册新框架服务
    new_framework_service = NewFrameworkService()
    AgentServiceFactory.register_service("new-framework", new_framework_service)
```

### 5. 更新配置

在 `web-service/app/core/config.py` 中添加配置：

```python
class Settings(BaseSettings):
    NEW_FRAMEWORK_PATH: str = "../agent-frameworks/new-framework"
```

## 测试指南

### 测试结构

```
web-service/tests/
├── __init__.py
├── conftest.py              # 测试配置
├── test_api/               # API测试
│   ├── test_agents.py
│   ├── test_langgraph.py
│   ├── test_autogen.py
│   └── test_crewai.py
├── test_services/          # 服务层测试
│   ├── test_agent_service.py
│   ├── test_langgraph_service.py
│   ├── test_autogen_service.py
│   └── test_crewai_service.py
└── test_core/              # 核心功能测试
    ├── test_config.py
    └── test_exceptions.py
```

### 编写测试

#### 单元测试示例

```python
# tests/test_services/test_agent_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.langgraph_service import LangGraphService

@pytest.mark.asyncio
async def test_execute_agent_success():
    service = LangGraphService()
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"result": "success"}'
        
        result = await service.execute_agent(
            "test_agent",
            {"message": "test"},
            timeout=30
        )
        
        assert result["status"] == "success"
```

#### API测试示例

```python
# tests/test_api/test_agents.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_execute_agent_endpoint():
    response = client.post("/api/v1/execute", json={
        "framework": "langgraph",
        "agent_type": "test_agent",
        "input_data": {"message": "test"},
        "timeout": 30
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api/test_agents.py

# 运行带覆盖率的测试
pytest --cov=app tests/

# 生成HTML覆盖率报告
pytest --cov=app --cov-report=html tests/
```

## 调试指南

### 日志配置

```python
import structlog

logger = structlog.get_logger()

# 在代码中添加日志
logger.info("执行Agent", agent_type=agent_type, framework=framework)
logger.error("执行失败", error=str(e), agent_type=agent_type)
```

### 调试技巧

#### 1. 使用调试器

```python
import pdb; pdb.set_trace()  # 设置断点
```

#### 2. 环境变量调试

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python app/main.py
```

#### 3. 查看详细错误

```python
import traceback

try:
    # 代码逻辑
    pass
except Exception as e:
    logger.error("详细错误", error=traceback.format_exc())
```

## 性能优化

### 1. 异步编程

- 使用 `async/await` 处理I/O操作
- 避免在异步函数中使用阻塞调用
- 使用 `asyncio.gather()` 并发执行

```python
async def execute_multiple_agents(requests):
    tasks = [execute_agent(req) for req in requests]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_agent_config(agent_type: str):
    # 缓存Agent配置
    pass
```

### 3. 连接池

```python
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.post(url, json=data) as response:
        return await response.json()
```

## 安全考虑

### 1. 输入验证

- 使用Pydantic模型验证输入
- 限制输入大小和类型
- 防止代码注入

### 2. 权限控制

```python
from fastapi import Depends, HTTPException
from app.core.auth import verify_api_key

@router.post("/execute")
async def execute_agent(request: AgentRequest, api_key: str = Depends(verify_api_key)):
    # 需要API密钥的端点
    pass
```

### 3. 资源限制

```python
import asyncio
from asyncio import Semaphore

# 限制并发执行数
semaphore = Semaphore(10)

async def execute_with_limit():
    async with semaphore:
        # 执行逻辑
        pass
```

## 部署和发布

### 1. 版本管理

- 使用语义化版本号 (SemVer)
- 维护CHANGELOG.md
- 使用Git标签标记版本

### 2. CI/CD流程

```yaml
# .github/workflows/ci.yml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r web-service/requirements.txt
      - name: Run tests
        run: |
          cd web-service
          pytest
```

### 3. 发布检查清单

- [ ] 所有测试通过
- [ ] 代码覆盖率 > 80%
- [ ] 文档更新
- [ ] 版本号更新
- [ ] CHANGELOG更新
- [ ] 安全扫描通过

## 故障排除

### 常见问题

#### 1. 导入错误

```bash
# 检查PYTHONPATH
export PYTHONPATH=/path/to/project/web-service
```

#### 2. 异步问题

```python
# 确保在异步上下文中运行
import asyncio

async def main():
    result = await some_async_function()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 3. 依赖冲突

```bash
# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 贡献指南

### 1. 开发流程

1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

### 2. 代码审查

- 确保代码风格一致
- 检查测试覆盖率
- 验证功能正确性
- 检查文档完整性

### 3. 提交规范

```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建过程或辅助工具的变动
```
