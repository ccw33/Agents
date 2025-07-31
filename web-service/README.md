# AI Agent Web Service

AI Agent统一Web服务接口，提供多框架Agent的HTTP API访问。

## 🚀 功能特性

### ✅ 已实现功能

1. **PrototypeDesign Agent** - 高保真原型设计
   - 🎨 智能原型生成
   - 🌊 流式响应支持
   - 📁 原型文件管理
   - 🌐 HTTP服务器自动启动
   - 🔄 多次迭代优化

2. **统一API接口**
   - 🔗 RESTful API设计
   - 📊 结构化响应格式
   - 🛡️ CORS跨域支持
   - 📝 完整的API文档

3. **服务管理**
   - 🏥 健康检查接口
   - 📈 服务状态监控
   - 🔧 配置管理
   - 📋 日志记录

### 🚧 规划中功能

- LangGraph Agent集成
- AutoGen Agent集成  
- CrewAI Agent集成
- 统一Agent调度器

## 📁 项目结构

```
web-service/
├── app/
│   ├── main.py                 # 主应用入口（最新完整版本）
│   ├── api/v1/                 # API路由
│   ├── core/                   # 核心配置
│   ├── models/                 # 数据模型
│   ├── services/               # 业务服务
│   └── prototype_outputs/      # 原型文件输出
├── requirements.txt            # 依赖管理
└── README.md                  # 项目文档
```

## 🛠️ 安装和运行

### 1. 环境准备

```bash
# 激活虚拟环境
source /Users/chenchaowen/Desktop/Project/Agents/.venv/bin/activate

# 安装依赖
cd web-service
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 开发模式启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式启动
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. 访问服务

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **PrototypeDesign**: http://localhost:8000/api/v1/prototype_design/

## 🎨 PrototypeDesign API使用

### 流式设计接口

```bash
curl -X POST "http://localhost:8000/api/v1/prototype_design/design/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "创建一个现代化的登录页面，包含用户名和密码输入框，登录按钮，以及忘记密码链接。使用蓝色主题，要求响应式设计。",
    "config": {"max_iterations": 3}
  }'
```

### 响应格式

```json
{
  "type": "complete",
  "message": "原型设计完成",
  "result": {
    "success": true,
    "prototype_url": "http://localhost:8000/prototypes/prototype_xxx.html",
    "iteration_count": 2,
    "is_approved": true,
    "validation_feedback": "设计完成，效果良好"
  }
}
```

## 📋 API接口列表

### PrototypeDesign

- `POST /api/v1/prototype_design/design/stream` - 流式原型设计
- `POST /api/v1/prototype_design/design` - 同步原型设计
- `GET /api/v1/prototype_design/prototypes` - 获取原型列表
- `GET /api/v1/prototype_design/prototypes/{filename}` - 获取原型文件
- `POST /api/v1/prototype_design/server/start` - 启动原型服务器
- `GET /api/v1/prototype_design/server/status` - 服务器状态

### 系统

- `GET /health` - 健康检查
- `GET /docs` - API文档
- `GET /redoc` - ReDoc文档

## 🔧 配置说明

### 环境变量

```bash
# PrototypeDesign Agent配置
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 原型文件配置

- **输出目录**: `agent-frameworks/langgraph/prototype_design/outputs/`
- **访问路径**: `/prototypes/{filename}` (通过web-service统一提供)
- **文件格式**: HTML（包含CSS和JavaScript）
- **服务端口**: 与web-service相同（默认8000）

## 🧪 测试验证

### 1. 基础功能测试

```bash
# 健康检查
curl http://localhost:8000/health

# PrototypeDesign健康检查
curl http://localhost:8000/api/v1/prototype_design/health
```

### 2. 原型生成测试

```bash
# 运行完整测试
python test_real_agent.py
```

### 3. Playwright验证

```python
# 使用Playwright验证原型页面
from playwright.async_api import async_playwright

async def test_prototype():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:8004/prototype_xxx.html")
        # 验证页面功能...
```

## 📝 更新日志

### v1.1.0 (2024-01-31) - 🎉 **重大优化**

- ✅ **统一服务架构** - 原型文件现在通过web-service统一提供访问
- ✅ **静态文件服务** - 使用FastAPI的StaticFiles，不再需要独立的原型服务器
- ✅ **简化部署** - 只需要启动一个web-service，自动处理所有原型文件访问
- ✅ **优化URL结构** - 原型访问地址统一为 `http://localhost:8000/prototypes/{filename}`
- 🗑️ **移除冗余** - 删除独立的原型服务器代码，简化架构

### v1.0.0 (2024-01-31)

- ✅ **文件整理完成** - 统一使用 `main.py` 作为主入口
- ✅ **PrototypeDesign集成** - 完整的Agent调用和流式响应
- ✅ **API文档** - 完整的接口文档和使用说明
- 🗑️ **清理冗余** - 删除 `main_fixed.py` 和 `main_clean.py`

### 🚀 **v1.1.0 主要改进**

1. **🌐 统一服务架构**
   - 原型文件通过web-service的静态文件服务提供访问
   - 不再需要启动独立的原型服务器（端口8001-8010）
   - 所有访问都通过统一的web-service端口

2. **📁 静态文件服务**
   - 使用FastAPI的StaticFiles中间件
   - 自动挂载原型输出目录到 `/prototypes` 路径
   - 支持直接访问所有HTML、CSS、JS等静态资源

3. **🔗 优化的URL结构**
   ```
   旧版本: http://localhost:8001/prototype_xxx.html  (独立服务器)
   新版本: http://localhost:8000/prototypes/prototype_xxx.html  (统一服务)
   ```

4. **📊 改进的API接口**
   - 原型列表接口返回web-service的URL
   - 服务器状态接口显示统一服务信息
   - 移除不必要的服务器启动接口

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

---

**AI Agent Web Service** - 让AI Agent触手可及！ 🚀✨
