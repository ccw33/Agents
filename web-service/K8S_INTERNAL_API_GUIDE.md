# AI Agent Web Service - K8s内部API调用指南

本文档提供AI Agent Web Service在Kubernetes集群内部的API调用指南，供其他微服务调用。

## 🌐 服务发现

### 内网域名访问

```bash
# 完整域名（推荐）
http://web-service.ai-agents.svc.cluster.local:8000

# 简化域名（同命名空间内）
http://web-service:8000

# ClusterIP直接访问
http://192.168.194.238:8000
```

### 服务信息

- **服务名称**: `web-service`
- **命名空间**: `ai-agents`
- **端口**: `8000`
- **协议**: `HTTP`
- **副本数**: `2`（负载均衡）

## 📋 API端点概览

| 端点 | 方法 | 描述 | 用途 |
|------|------|------|------|
| `/health` | GET | 健康检查 | 服务监控 |
| `/api/v1/info` | GET | 服务信息 | 服务发现 |
| `/api/v1/prototype_design/health` | GET | Agent健康检查 | Agent监控 |
| `/api/v1/prototype_design/design` | POST | 原型设计API | 业务调用 |

## 🔍 API详细说明

### 1. 健康检查

**端点**: `GET /health`

**用途**: 服务健康状态检查，用于K8s探针和服务监控

**请求示例**:
```bash
curl http://web-service.ai-agents.svc.cluster.local:8000/health
```

**响应示例**:
```json
{
    "status": "healthy",
    "service": "ai-agent-web-service",
    "version": "1.0.0",
    "timestamp": "2025-07-31T11:56:57+00:00",
    "environment": "kubernetes",
    "deployment": "nginx-based"
}
```

**响应字段**:
- `status`: 服务状态（healthy/unhealthy）
- `service`: 服务名称
- `version`: 服务版本
- `timestamp`: 响应时间戳
- `environment`: 部署环境
- `deployment`: 部署类型

### 2. 服务信息

**端点**: `GET /api/v1/info`

**用途**: 获取服务详细信息，用于服务发现和配置

**请求示例**:
```bash
curl http://web-service.ai-agents.svc.cluster.local:8000/api/v1/info
```

**响应示例**:
```json
{
    "service": "AI Agent Web Service",
    "version": "1.0.0",
    "deployment": "kubernetes",
    "namespace": "ai-agents",
    "internal_url": "http://web-service.ai-agents.svc.cluster.local:8000",
    "features": [
        "内网域名访问",
        "服务发现",
        "负载均衡",
        "健康检查",
        "多副本部署"
    ],
    "endpoints": [
        "/health",
        "/api/v1/info",
        "/api/v1/prototype_design/health",
        "/api/v1/prototype_design/design"
    ]
}
```

### 3. Agent健康检查

**端点**: `GET /api/v1/prototype_design/health`

**用途**: 检查PrototypeDesign Agent的健康状态

**请求示例**:
```bash
curl http://web-service.ai-agents.svc.cluster.local:8000/api/v1/prototype_design/health
```

**响应示例**:
```json
{
    "status": "healthy",
    "message": "PrototypeDesign服务正常",
    "agent_available": true,
    "note": "这是K8s部署的AI Agent Web Service"
}
```

### 4. 原型设计API

**端点**: `POST /api/v1/prototype_design/design`

**用途**: 调用PrototypeDesign Agent进行原型设计

**请求示例**:
```bash
curl -X POST \
  http://web-service.ai-agents.svc.cluster.local:8000/api/v1/prototype_design/design \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "创建一个用户管理页面",
    "style": "现代简约"
  }'
```

**响应示例**:
```json
{
    "status": "success",
    "success": true,
    "message": "AI Agent Web Service 在Kubernetes中运行",
    "prototype_url": "http://web-service.ai-agents.svc.cluster.local:8000/health",
    "internal_domain": "web-service.ai-agents.svc.cluster.local",
    "features": ["内网域名访问", "服务发现", "负载均衡"]
}
```

## 🔧 集成示例

### Python调用示例

```python
import requests
import json

class AIAgentClient:
    def __init__(self, base_url="http://web-service.ai-agents.svc.cluster.local:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """健康检查"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def get_service_info(self):
        """获取服务信息"""
        response = self.session.get(f"{self.base_url}/api/v1/info")
        return response.json()
    
    def check_agent_health(self):
        """检查Agent健康状态"""
        response = self.session.get(f"{self.base_url}/api/v1/prototype_design/health")
        return response.json()
    
    def create_prototype(self, requirement, style="现代简约"):
        """创建原型设计"""
        data = {
            "requirement": requirement,
            "style": style
        }
        response = self.session.post(
            f"{self.base_url}/api/v1/prototype_design/design",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return response.json()

# 使用示例
client = AIAgentClient()

# 健康检查
health = client.health_check()
print(f"服务状态: {health['status']}")

# 创建原型
result = client.create_prototype("用户登录页面", "简约风格")
print(f"设计结果: {result}")
```

### Go调用示例

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type AIAgentClient struct {
    BaseURL string
    Client  *http.Client
}

type HealthResponse struct {
    Status      string `json:"status"`
    Service     string `json:"service"`
    Version     string `json:"version"`
    Timestamp   string `json:"timestamp"`
    Environment string `json:"environment"`
}

type DesignRequest struct {
    Requirement string `json:"requirement"`
    Style       string `json:"style"`
}

type DesignResponse struct {
    Status    string `json:"status"`
    Success   bool   `json:"success"`
    Message   string `json:"message"`
    Features  []string `json:"features"`
}

func NewAIAgentClient() *AIAgentClient {
    return &AIAgentClient{
        BaseURL: "http://web-service.ai-agents.svc.cluster.local:8000",
        Client:  &http.Client{},
    }
}

func (c *AIAgentClient) HealthCheck() (*HealthResponse, error) {
    resp, err := c.Client.Get(c.BaseURL + "/health")
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var health HealthResponse
    err = json.NewDecoder(resp.Body).Decode(&health)
    return &health, err
}

func (c *AIAgentClient) CreatePrototype(requirement, style string) (*DesignResponse, error) {
    reqData := DesignRequest{
        Requirement: requirement,
        Style:       style,
    }
    
    jsonData, err := json.Marshal(reqData)
    if err != nil {
        return nil, err
    }

    resp, err := c.Client.Post(
        c.BaseURL+"/api/v1/prototype_design/design",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result DesignResponse
    err = json.NewDecoder(resp.Body).Decode(&result)
    return &result, err
}

func main() {
    client := NewAIAgentClient()
    
    // 健康检查
    health, err := client.HealthCheck()
    if err != nil {
        fmt.Printf("健康检查失败: %v\n", err)
        return
    }
    fmt.Printf("服务状态: %s\n", health.Status)
    
    // 创建原型
    result, err := client.CreatePrototype("用户管理界面", "现代风格")
    if err != nil {
        fmt.Printf("创建原型失败: %v\n", err)
        return
    }
    fmt.Printf("设计结果: %+v\n", result)
}
```

### Node.js调用示例

```javascript
const axios = require('axios');

class AIAgentClient {
    constructor(baseURL = 'http://web-service.ai-agents.svc.cluster.local:8000') {
        this.baseURL = baseURL;
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async healthCheck() {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error) {
            throw new Error(`健康检查失败: ${error.message}`);
        }
    }

    async getServiceInfo() {
        try {
            const response = await this.client.get('/api/v1/info');
            return response.data;
        } catch (error) {
            throw new Error(`获取服务信息失败: ${error.message}`);
        }
    }

    async checkAgentHealth() {
        try {
            const response = await this.client.get('/api/v1/prototype_design/health');
            return response.data;
        } catch (error) {
            throw new Error(`Agent健康检查失败: ${error.message}`);
        }
    }

    async createPrototype(requirement, style = '现代简约') {
        try {
            const response = await this.client.post('/api/v1/prototype_design/design', {
                requirement,
                style
            });
            return response.data;
        } catch (error) {
            throw new Error(`创建原型失败: ${error.message}`);
        }
    }
}

// 使用示例
async function main() {
    const client = new AIAgentClient();
    
    try {
        // 健康检查
        const health = await client.healthCheck();
        console.log('服务状态:', health.status);
        
        // 获取服务信息
        const info = await client.getServiceInfo();
        console.log('服务信息:', info);
        
        // 创建原型
        const result = await client.createPrototype('电商购物车页面', '简约风格');
        console.log('设计结果:', result);
        
    } catch (error) {
        console.error('调用失败:', error.message);
    }
}

main();
```

## 🚨 错误处理

### 常见错误码

| 状态码 | 描述 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常处理响应 |
| 404 | 端点不存在 | 检查API路径 |
| 500 | 服务器内部错误 | 检查服务状态，重试 |
| 503 | 服务不可用 | 等待服务恢复 |

### 重试策略

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session
```

## 📊 监控和日志

### 健康检查监控

```yaml
# K8s监控配置示例
apiVersion: v1
kind: Service
metadata:
  name: ai-agent-monitor
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/health"
```

### 日志格式

服务日志采用结构化JSON格式：

```json
{
    "timestamp": "2025-07-31T12:00:00Z",
    "level": "INFO",
    "service": "ai-agent-web-service",
    "endpoint": "/api/v1/prototype_design/design",
    "method": "POST",
    "status_code": 200,
    "response_time_ms": 150,
    "client_ip": "192.168.194.67"
}
```

## 🔒 安全考虑

### 网络策略

```yaml
# 网络策略示例 - 限制访问来源
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-agent-access-policy
  namespace: ai-agents
spec:
  podSelector:
    matchLabels:
      app: ai-agent-web-service
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: trusted-services
    ports:
    - protocol: TCP
      port: 8000
```

### 认证建议

对于生产环境，建议添加：
- **API密钥认证**
- **JWT令牌验证**
- **请求限流**
- **IP白名单**

## 📞 技术支持

- **服务监控**: 通过 `/health` 端点
- **问题排查**: 查看Pod日志 `kubectl logs -l app=ai-agent-web-service -n ai-agents`
- **性能监控**: 通过Prometheus指标收集
- **故障恢复**: 服务自动重启和负载均衡

---

**更新时间**: 2025-07-31  
**文档版本**: 1.0.0  
**维护团队**: AI Agent开发团队
