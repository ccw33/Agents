# 高保真原型设计Agent

基于LangGraph构建的智能原型设计系统，包含Designer和Validator两个AI角色，能够自动生成高质量的Web原型。

## 🎯 功能特点

- **智能设计生成**：Designer角色使用AI生成HTML/CSS/JavaScript代码
- **自动质量验证**：Validator角色验证原型是否符合需求
- **迭代优化**：支持最多5次自动迭代改进
- **实时预览**：自动启动本地服务器，提供即时预览
- **响应式设计**：生成的原型自动适配移动端
- **现代化技术栈**：使用HTML5、CSS3、ES6+等现代Web技术

## 🏗️ 系统架构

```
用户需求 → Designer节点 → 文件管理节点 → Validator节点 → 条件路由
                ↑                                        ↓
                ←←←←←←←← 继续迭代 ←←←←←←←←←←←←←←←←←←←←←
```

### 核心组件

1. **Designer节点**：负责根据需求生成原型代码
2. **Validator节点**：验证原型质量和需求匹配度
3. **文件管理节点**：保存文件并启动本地服务器
4. **条件路由**：决定是否继续迭代或结束流程

## 🚀 快速开始

### 1. 安装依赖

```bash
cd prototype_design
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，添加你的API密钥：

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here  # 可选
```

### 3. 运行示例

```python
from agent import run_prototype_design

# 定义需求
requirements = """
请设计一个现代化的产品展示页面，包含：
1. 顶部导航栏
2. 英雄区域
3. 产品展示区
4. 联系表单
5. 页脚

要求响应式设计，支持移动端。
"""

# 运行设计流程
result = run_prototype_design(requirements)

if result['success']:
    print(f"✅ 原型生成成功!")
    print(f"🌐 访问地址: {result['server_url']}")
    print(f"📁 项目路径: {result['project_path']}")
else:
    print(f"❌ 生成失败: {result['error']}")
```

### 4. 使用LangGraph CLI

```bash
# 启动开发服务器
langgraph dev

# 在浏览器中访问 LangGraph Studio
# 通常是 http://localhost:8123
```

## 📁 项目结构

```
prototype_design/
├── agent.py                 # 主应用入口
├── utils/
│   ├── __init__.py
│   ├── state.py            # 状态定义
│   ├── nodes.py            # 节点函数
│   ├── tools.py            # 工具函数
│   └── prompts.py          # 提示模板
├── templates/              # HTML模板
│   └── base.html
├── output/                 # 生成的原型输出
├── requirements.txt        # Python依赖
├── langgraph.json         # LangGraph配置
├── .env                   # 环境变量
└── README.md              # 说明文档
```

## 🎨 输出示例

生成的原型项目结构：

```
output/prototype_20241230_143022/
├── index.html              # 主页面
├── style.css              # 样式文件
└── script.js              # 交互逻辑
```

## ⚙️ 配置选项

### 最大迭代次数

```python
result = run_prototype_design(requirements, max_iterations=3)
```

### 自定义输出目录

```python
from utils.tools import PrototypeFileManager

file_manager = PrototypeFileManager(base_output_dir="custom_output")
```

## 🔧 高级功能

### 1. 自定义提示模板

编辑 `utils/prompts.py` 中的提示模板来调整AI行为。

### 2. 添加新的验证维度

在 `validator_node` 中添加更多验证逻辑。

### 3. 集成外部工具

可以集成代码格式化、压缩等外部工具。

## 🐛 故障排除

### 常见问题

1. **API密钥错误**：确保 `.env` 文件中的API密钥正确
2. **端口冲突**：系统会自动寻找可用端口
3. **代码生成失败**：检查网络连接和API配额

### 调试模式

设置环境变量启用详细日志：

```bash
export LANGSMITH_TRACING=true
```

## 📊 性能优化

- 使用缓存减少重复的API调用
- 优化提示模板长度
- 合理设置最大迭代次数

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License
