# AI Agent Web Service - 客户端SDK示例

本目录包含了在Kubernetes集群内调用AI Agent Web Service的各种语言客户端SDK示例。

## 📁 文件说明

| 文件 | 语言 | 描述 |
|------|------|------|
| `python_client.py` | Python | Python客户端SDK，支持重试和错误处理 |
| `go_client.go` | Go | Go客户端SDK，类型安全的API调用 |
| `nodejs_client.js` | Node.js | JavaScript客户端SDK，支持异步操作 |

## 🚀 快速开始

### Python客户端

```python
from python_client import AIAgentClient

# 创建客户端
client = AIAgentClient()

# 健康检查
health = client.health_check()
print(f"服务状态: {health['status']}")

# 创建原型
result = client.create_prototype("用户登录页面", "简约风格")
print(f"设计结果: {result['message']}")
```

**运行示例:**
```bash
python python_client.py
```

**依赖安装:**
```bash
pip install requests
```

### Go客户端

```go
package main

import (
    "fmt"
    "log"
)

func main() {
    // 创建客户端
    client := NewAIAgentClient()
    
    // 健康检查
    health, err := client.HealthCheck()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("服务状态: %s\n", health.Status)
    
    // 创建原型
    result, err := client.CreatePrototype("用户登录页面", "简约风格")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("设计结果: %s\n", result.Message)
}
```

**运行示例:**
```bash
go run go_client.go
```

**依赖管理:**
```bash
go mod init ai-agent-client
go mod tidy
```

### Node.js客户端

```javascript
const { AIAgentClient } = require('./nodejs_client');

async function main() {
    // 创建客户端
    const client = new AIAgentClient();
    
    // 健康检查
    const health = await client.healthCheck();
    console.log(`服务状态: ${health.status}`);
    
    // 创建原型
    const result = await client.createPrototype('用户登录页面', '简约风格');
    console.log(`设计结果: ${result.message}`);
}

main().catch(console.error);
```

**运行示例:**
```bash
node nodejs_client.js
```

**依赖安装:**
```bash
npm install axios
```

## 🔧 配置选项

### 服务地址配置

所有客户端都支持自定义服务地址：

```python
# Python
client = AIAgentClient(base_url="http://web-service:8000")
```

```go
// Go
client := NewAIAgentClientWithConfig("http://web-service:8000", 30*time.Second)
```

```javascript
// Node.js
const client = new AIAgentClient('http://web-service:8000');
```

### 超时和重试配置

```python
# Python - 30秒超时，3次重试
client = AIAgentClient(timeout=30, retries=3)
```

```go
// Go - 30秒超时
client := NewAIAgentClientWithConfig(baseURL, 30*time.Second)
```

```javascript
// Node.js - 30秒超时，3次重试
const client = new AIAgentClient(baseURL, 30000, 3);
```

## 📋 API方法

### 通用方法

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `health_check()` / `HealthCheck()` / `healthCheck()` | 健康检查 | 健康状态信息 |
| `get_service_info()` / `GetServiceInfo()` / `getServiceInfo()` | 获取服务信息 | 服务详细信息 |
| `check_agent_health()` / `CheckAgentHealth()` / `checkAgentHealth()` | 检查Agent状态 | Agent健康信息 |
| `create_prototype()` / `CreatePrototype()` / `createPrototype()` | 创建原型设计 | 设计结果 |

### 辅助方法

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `is_healthy()` / `IsHealthy()` / `isHealthy()` | 检查服务是否健康 | boolean |
| `wait_for_service()` / `WaitForService()` / `waitForService()` | 等待服务就绪 | boolean |

## 🚨 错误处理

### Python
```python
from python_client import AIAgentClient, AIAgentClientError

try:
    client = AIAgentClient()
    result = client.create_prototype("需求描述")
except AIAgentClientError as e:
    print(f"客户端错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

### Go
```go
client := NewAIAgentClient()
result, err := client.CreatePrototype("需求描述", "风格")
if err != nil {
    log.Printf("请求失败: %v", err)
    return
}
```

### Node.js
```javascript
const { AIAgentClient, AIAgentClientError } = require('./nodejs_client');

try {
    const client = new AIAgentClient();
    const result = await client.createPrototype('需求描述');
} catch (error) {
    if (error instanceof AIAgentClientError) {
        console.error(`客户端错误: ${error.message}`);
    } else {
        console.error(`未知错误: ${error.message}`);
    }
}
```

## 🔍 调试和日志

### Python
```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

client = AIAgentClient()
```

### Go
```go
import "log"

// Go使用标准log包输出调试信息
log.SetFlags(log.LstdFlags | log.Lshortfile)
```

### Node.js
```javascript
// Node.js客户端会自动输出重试和等待信息
const client = new AIAgentClient();
```

## 🌐 网络配置

### 内网域名

在Kubernetes集群内，推荐使用以下域名：

```bash
# 完整域名（跨命名空间）
http://web-service.ai-agents.svc.cluster.local:8000

# 简化域名（同命名空间内）
http://web-service:8000
```

### 服务发现

客户端会自动处理服务发现，无需手动配置IP地址。

## 📊 性能优化

### 连接复用

所有客户端都支持HTTP连接复用：

- **Python**: 使用`requests.Session`
- **Go**: 使用`http.Client`
- **Node.js**: 使用`axios`实例

### 重试策略

- **指数退避**: 重试间隔逐渐增加
- **状态码过滤**: 只对特定错误码重试（429, 500, 502, 503, 504）
- **最大重试次数**: 默认3次，可配置

### 超时设置

- **默认超时**: 30秒
- **可配置**: 根据业务需求调整
- **分层超时**: 连接超时 + 读取超时

## 🔒 安全考虑

### 网络安全

- 使用内网域名，避免外网暴露
- 支持HTTPS（如果服务配置了TLS）
- 遵循最小权限原则

### 认证授权

当前版本为内网调用，未实现认证。生产环境建议添加：

- API密钥认证
- JWT令牌验证
- 服务间mTLS

## 📞 技术支持

### 常见问题

1. **连接超时**: 检查服务是否运行，网络是否通畅
2. **DNS解析失败**: 确认在正确的命名空间内
3. **API错误**: 检查请求参数和服务日志

### 调试命令

```bash
# 检查服务状态
kubectl get pods -n ai-agents -l app=ai-agent-web-service

# 查看服务日志
kubectl logs -l app=ai-agent-web-service -n ai-agents

# 测试网络连通性
kubectl exec -it <pod-name> -n ai-agents -- curl http://web-service:8000/health
```

---

**更新时间**: 2025-07-31  
**SDK版本**: 1.0.0  
**维护团队**: AI Agent开发团队
