# PrototypeDesign API集成文档

本文档介绍如何通过Web API使用PrototypeDesign Agent的功能。

## 概述

PrototypeDesign Agent已成功集成到AI Agent Web Service中，提供以下功能：

- 🎨 **智能原型设计**: 根据需求自动生成HTML/CSS/JavaScript代码
- 🔍 **多模态验证**: 使用截图分析验证设计质量
- 🌊 **流式响应**: 实时查看设计过程和进度
- 📁 **文件管理**: 访问和管理生成的原型文件
- 🌐 **服务器集成**: 自动启动本地服务器预览原型

## API接口

### 基础URL
```
http://localhost:8000/api/v1/prototype_design
```

### 1. 健康检查
```http
GET /health
```

**响应示例:**
```json
{
  "status": "healthy",
  "message": "PrototypeDesign服务正常",
  "path": "/path/to/prototype_design",
  "server": {
    "running": false,
    "port": null,
    "url": null,
    "output_dir": "/path/to/outputs"
  }
}
```

### 2. 同步原型设计
```http
POST /design
Content-Type: application/json

{
  "requirements": "创建一个现代化的登录页面，包含用户名和密码输入框，登录按钮，以及忘记密码链接。使用蓝色主题，要求响应式设计。",
  "config": {
    "max_iterations": 5,
    "auto_open_browser": false
  },
  "stream": false
}
```

**响应示例:**
```json
{
  "status": "success",
  "success": true,
  "prototype_url": "http://localhost:8001/prototype_abc123.html",
  "iteration_count": 2,
  "is_approved": true,
  "validation_feedback": "原型设计符合要求，界面美观，响应式设计良好",
  "html_code": "<!DOCTYPE html><html>...",
  "css_code": "body { margin: 0; padding: 0; }...",
  "js_code": "document.addEventListener('DOMContentLoaded', function() {...",
  "error": null,
  "execution_time": 125.6,
  "timestamp": "2024-01-15T10:30:00"
}
```

### 3. 流式原型设计
```http
POST /design/stream
Content-Type: application/json

{
  "requirements": "创建一个产品展示卡片，包含产品图片、标题、价格和购买按钮。要求响应式设计。",
  "config": {
    "max_iterations": 3
  },
  "stream": true
}
```

**响应格式:** Server-Sent Events (text/event-stream)

**事件示例:**
```
data: {"type": "start", "message": "开始原型设计", "timestamp": "2024-01-15T10:30:00"}

data: {"type": "progress", "step": "designer", "message": "Designer正在工作... (第1次迭代)", "timestamp": "2024-01-15T10:30:15"}

data: {"type": "progress", "step": "validator", "message": "Validator验证结果: APPROVED", "validation_result": "APPROVED", "timestamp": "2024-01-15T10:32:30"}

data: {"type": "complete", "message": "原型设计完成", "result": {...}, "timestamp": "2024-01-15T10:33:00"}
```

### 4. 获取原型列表
```http
GET /prototypes
```

**响应示例:**
```json
{
  "prototypes": [
    {
      "filename": "prototype_abc123.html",
      "created_time": 1705312200.0,
      "modified_time": 1705312200.0,
      "size": 15420,
      "url": "/api/v1/prototype_design/prototypes/prototype_abc123.html"
    }
  ]
}
```

### 5. 访问原型文件
```http
GET /prototypes/{filename}
```

直接返回HTML文件内容，可在浏览器中查看。

### 6. 服务器管理

#### 启动服务器
```http
POST /server/start?port=8001
```

#### 停止服务器
```http
POST /server/stop
```

#### 获取服务器状态
```http
GET /server/status
```

## 使用示例

### Python客户端示例

```python
import asyncio
import httpx
import json

async def design_prototype():
    async with httpx.AsyncClient(timeout=600.0) as client:
        # 同步设计
        response = await client.post(
            "http://localhost:8000/api/v1/prototype_design/design",
            json={
                "requirements": "创建一个简单的登录页面",
                "config": {"max_iterations": 3}
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"设计完成: {result['prototype_url']}")
        else:
            print(f"设计失败: {response.status_code}")

# 运行
asyncio.run(design_prototype())
```

### JavaScript客户端示例

```javascript
// 同步设计
async function designPrototype() {
    const response = await fetch('/api/v1/prototype_design/design', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            requirements: '创建一个简单的登录页面',
            config: { max_iterations: 3 }
        })
    });
    
    if (response.ok) {
        const result = await response.json();
        console.log('设计完成:', result.prototype_url);
    } else {
        console.error('设计失败:', response.status);
    }
}

// 流式设计
function streamDesign() {
    const eventSource = new EventSource('/api/v1/prototype_design/design/stream');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.type === 'start') {
            console.log('开始设计:', data.message);
        } else if (data.type === 'progress') {
            console.log('进度更新:', data.message);
        } else if (data.type === 'complete') {
            console.log('设计完成:', data.result);
            eventSource.close();
        } else if (data.type === 'error') {
            console.error('设计失败:', data.error);
            eventSource.close();
        }
    };
}
```

### cURL示例

```bash
# 健康检查
curl http://localhost:8000/api/v1/prototype_design/health

# 同步设计
curl -X POST http://localhost:8000/api/v1/prototype_design/design \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "创建一个简单的登录页面",
    "config": {"max_iterations": 3}
  }'

# 获取原型列表
curl http://localhost:8000/api/v1/prototype_design/prototypes

# 启动服务器
curl -X POST http://localhost:8000/api/v1/prototype_design/server/start?port=8001
```

## 启动服务

### 1. 使用专用启动脚本
```bash
# 基本启动
python start_with_prototype_design.py

# 指定端口
python start_with_prototype_design.py --port 8080

# 启动并运行测试
python start_with_prototype_design.py --test
```

### 2. 使用标准方式
```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 测试

### 运行完整测试
```bash
python test_prototype_design.py
```

### 运行特定测试
```bash
# 指定服务器地址
python test_prototype_design.py http://localhost:8080
```

## 配置

### 环境变量
```bash
# 框架路径配置
LANGGRAPH_PATH=../agent-frameworks/langgraph

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 超时配置
AGENT_TIMEOUT=600
```

### 配置文件
参考 `.env.example` 文件进行配置。

## 注意事项

1. **超时设置**: PrototypeDesign需要较长时间执行，建议设置10分钟以上超时
2. **并发限制**: 建议限制并发设计任务数量，避免资源耗尽
3. **文件管理**: 定期清理生成的原型文件，避免磁盘空间不足
4. **依赖检查**: 确保prototype_design的所有依赖已正确安装

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查prototype_design路径是否正确
   - 确认所有依赖文件存在

2. **设计超时**
   - 增加超时时间设置
   - 检查网络连接和API密钥

3. **文件访问失败**
   - 检查输出目录权限
   - 确认文件路径安全性

### 日志查看
服务运行时会输出详细的结构化日志，包括：
- 设计过程状态
- 验证结果
- 错误信息
- 性能指标

## API文档

启动服务后，访问以下地址查看完整API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
