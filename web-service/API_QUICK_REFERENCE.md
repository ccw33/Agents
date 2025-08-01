# AI Agent Web Service - API快速参考

## 🌐 服务地址

```bash
# 内网域名（推荐）
http://web-service.ai-agents.svc.cluster.local:8000

# 简化域名（同命名空间）
http://web-service:8000
```

## 📋 API端点

### 健康检查
```bash
GET /health
# 响应: {"status": "healthy", "service": "ai-agent-web-service", ...}
```

### 服务信息
```bash
GET /api/v1/info
# 响应: {"service": "AI Agent Web Service", "version": "1.0.0", ...}
```

### Agent健康检查
```bash
GET /api/v1/prototype_design/health
# 响应: {"status": "healthy", "agent_available": true, ...}
```

### 原型设计
```bash
POST /api/v1/prototype_design/design
Content-Type: application/json

{
  "requirement": "创建用户管理页面",
  "style": "现代简约"
}

# 响应: {"status": "success", "success": true, ...}
```

## 🔧 快速调用

### curl示例
```bash
# 健康检查
curl http://web-service.ai-agents.svc.cluster.local:8000/health

# 创建原型
curl -X POST http://web-service.ai-agents.svc.cluster.local:8000/api/v1/prototype_design/design \
  -H "Content-Type: application/json" \
  -d '{"requirement": "用户登录页面", "style": "简约风格"}'
```

### Python示例
```python
import requests

# 基础URL
base_url = "http://web-service.ai-agents.svc.cluster.local:8000"

# 健康检查
response = requests.get(f"{base_url}/health")
print(response.json())

# 创建原型
data = {"requirement": "用户管理界面", "style": "现代风格"}
response = requests.post(f"{base_url}/api/v1/prototype_design/design", json=data)
print(response.json())
```

### JavaScript示例
```javascript
const baseURL = 'http://web-service.ai-agents.svc.cluster.local:8000';

// 健康检查
fetch(`${baseURL}/health`)
  .then(response => response.json())
  .then(data => console.log(data));

// 创建原型
fetch(`${baseURL}/api/v1/prototype_design/design`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    requirement: '电商购物车',
    style: '简约风格'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🚨 错误处理

| 状态码 | 说明 | 处理 |
|--------|------|------|
| 200 | 成功 | 正常处理 |
| 404 | 端点不存在 | 检查URL |
| 500 | 服务器错误 | 重试或检查日志 |
| 503 | 服务不可用 | 等待恢复 |

## 📊 监控

```bash
# 检查服务状态
kubectl get pods -n ai-agents -l app=ai-agent-web-service

# 查看日志
kubectl logs -l app=ai-agent-web-service -n ai-agents

# 端口转发（调试用）
kubectl port-forward -n ai-agents service/web-service 8080:8000
```

---
**快速参考** | **版本**: 1.0.0 | **更新**: 2025-07-31
