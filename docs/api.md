# AI Agent Web Service API 文档

## 概述

AI Agent Web Service 提供统一的RESTful API接口，支持调用LangGraph、AutoGen、CrewAI三个AI Agent框架。

**基础URL**: `http://localhost:8000`

**API版本**: v1

## 认证

目前API不需要认证，后续可以通过配置API_KEY启用认证。

## 统一接口

### 执行Agent

**POST** `/api/v1/execute`

执行指定框架的Agent。

#### 请求体

```json
{
  "framework": "langgraph",
  "agent_type": "chat_agent",
  "input_data": {
    "message": "你好，请帮我分析一下市场趋势",
    "context": {}
  },
  "config": {
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "timeout": 300
}
```

#### 响应

```json
{
  "status": "success",
  "result": {
    "output": "根据市场分析，当前科技股表现良好...",
    "confidence": 0.85,
    "sources": ["财经新闻", "市场数据"]
  },
  "error": null,
  "execution_time": 15.6,
  "framework": "langgraph",
  "agent_type": "chat_agent",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 获取框架列表

**GET** `/api/v1/frameworks`

获取所有支持的框架及其状态。

#### 响应

```json
{
  "frameworks": ["langgraph", "autogen", "crewai"],
  "status": {
    "langgraph": {"status": "healthy"},
    "autogen": {"status": "healthy"},
    "crewai": {"status": "healthy"}
  },
  "total": 3
}
```

### 获取框架Agent列表

**GET** `/api/v1/frameworks/{framework}/agents`

获取指定框架的可用Agent列表。

#### 响应

```json
{
  "framework": "langgraph",
  "agents": {
    "chat_agent": {
      "description": "基础对话Agent",
      "input_schema": {"message": "str"}
    },
    "research_agent": {
      "description": "研究分析Agent",
      "input_schema": {"query": "str", "max_results": "int"}
    }
  }
}
```

### 健康检查

**POST** `/api/v1/health`

检查服务和框架的健康状态。

#### 请求体

```json
{
  "check_frameworks": true
}
```

#### 响应

```json
{
  "status": "healthy",
  "service": "ai-agent-web-service",
  "version": "1.0.0",
  "frameworks": {
    "langgraph": "available",
    "autogen": "available",
    "crewai": "available"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## LangGraph专用接口

### 执行图

**POST** `/api/v1/langgraph/execute`

执行LangGraph图。

#### 请求体

```json
{
  "graph_name": "research_assistant",
  "input_data": {
    "query": "人工智能的最新发展",
    "max_results": 5
  },
  "config": {
    "recursion_limit": 50
  },
  "stream": false
}
```

### 获取图列表

**GET** `/api/v1/langgraph/graphs`

### 获取图模式

**GET** `/api/v1/langgraph/graphs/{graph_name}/schema`

### 验证图配置

**POST** `/api/v1/langgraph/validate`

## AutoGen专用接口

### 执行多代理对话

**POST** `/api/v1/autogen/execute`

启动AutoGen多代理对话。

#### 请求体

```json
{
  "agent_config": "coding_team",
  "message": "请帮我写一个Python函数来计算斐波那契数列",
  "participants": ["coder", "reviewer"],
  "max_rounds": 10
}
```

### 获取Agent配置列表

**GET** `/api/v1/autogen/configs`

### 获取配置详情

**GET** `/api/v1/autogen/configs/{config_name}/info`

### 继续对话

**POST** `/api/v1/autogen/chat/continue`

### 验证配置

**POST** `/api/v1/autogen/validate`

## CrewAI专用接口

### 执行团队

**POST** `/api/v1/crewai/execute`

启动CrewAI团队执行任务。

#### 请求体

```json
{
  "crew_name": "research_crew",
  "inputs": {
    "topic": "区块链技术",
    "depth": "detailed"
  },
  "process_type": "sequential",
  "verbose": true
}
```

### 获取Crew列表

**GET** `/api/v1/crewai/crews`

### 获取Crew详情

**GET** `/api/v1/crewai/crews/{crew_name}/info`

### 获取任务列表

**GET** `/api/v1/crewai/crews/{crew_name}/tasks`

### 估算执行时间

**POST** `/api/v1/crewai/crews/{crew_name}/estimate`

### 验证配置

**POST** `/api/v1/crewai/validate`

## 错误处理

所有API都使用统一的错误响应格式：

```json
{
  "error": "错误信息",
  "detail": "详细错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 常见错误代码

- `FRAMEWORK_NOT_FOUND`: 框架不存在
- `AGENT_NOT_FOUND`: Agent不存在
- `AGENT_EXECUTION_ERROR`: Agent执行失败
- `AGENT_TIMEOUT`: 执行超时
- `VALIDATION_ERROR`: 输入验证失败
- `CONFIGURATION_ERROR`: 配置错误
- `RESOURCE_LIMIT_ERROR`: 资源限制

## 状态码

- `200`: 成功
- `400`: 请求错误
- `404`: 资源不存在
- `408`: 请求超时
- `422`: 输入验证失败
- `429`: 请求过于频繁
- `500`: 服务器内部错误

## 限制

- 单次请求超时时间：最大3600秒
- 并发Agent执行数：最大10个
- 请求体大小：最大10MB

## 示例代码

### Python

```python
import requests

# 执行Agent
response = requests.post('http://localhost:8000/api/v1/execute', json={
    "framework": "langgraph",
    "agent_type": "chat_agent",
    "input_data": {"message": "Hello"},
    "timeout": 300
})

result = response.json()
print(result)
```

### JavaScript

```javascript
// 执行Agent
const response = await fetch('http://localhost:8000/api/v1/execute', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        framework: 'langgraph',
        agent_type: 'chat_agent',
        input_data: { message: 'Hello' },
        timeout: 300
    })
});

const result = await response.json();
console.log(result);
```

### cURL

```bash
# 执行Agent
curl -X POST "http://localhost:8000/api/v1/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "framework": "langgraph",
       "agent_type": "chat_agent",
       "input_data": {"message": "Hello"},
       "timeout": 300
     }'
```
