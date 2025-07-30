"""
Designer Agent模块
负责根据用户需求生成高保真原型的HTML、CSS和JavaScript代码
使用通义千问qwen-coder-plus-latest模型进行代码生成
"""

import os
from typing import Dict, Any
from langsmith import traceable
from langsmith.wrappers import wrap_openai
import openai

try:
    from ..state import PrototypeState
    from .tools import parse_requirements, validate_code_syntax
    from ..config import get_config
except ImportError:
    from state import PrototypeState
    from agents.tools import parse_requirements, validate_code_syntax
    from config import get_config


class DesignerAgent:
    """
    Designer Agent类
    负责生成高保真原型代码
    使用通义千问qwen-coder-plus-latest模型
    """

    def __init__(self):
        """
        初始化Designer Agent
        """
        # 获取配置
        self.config = get_config()

        # 创建OpenAI客户端（兼容通义千问API）
        client_config = self.config.get_openai_client_config()
        self.openai_client = wrap_openai(openai.OpenAI(
            api_key=client_config["api_key"],
            base_url=client_config["base_url"]
        ))

        # 模型配置
        self.model_name = self.config.designer_model
        self.max_tokens = self.config.max_output_tokens
        self.temperature = 0.7
        
        self.system_prompt = """你是一个专业的前端开发工程师和UI/UX设计师，专门负责创建高保真原型。

你的任务是根据用户需求生成完整的HTML、CSS和JavaScript代码，创建一个功能完整、美观的原型。

要求：
1. 生成的代码必须是完整的、可运行的
2. HTML结构要语义化，使用合适的标签
3. CSS样式要现代化，支持响应式设计
4. JavaScript要提供必要的交互功能
5. 代码要规范、注释清晰
6. 设计要美观、用户体验良好

请按照以下格式输出：

```html
[HTML代码]
```

```css
[CSS代码]
```

```javascript
[JavaScript代码]
```

注意：
- 不要包含外部依赖，所有代码都应该是自包含的
- 确保代码在现代浏览器中正常运行
- 注重细节和用户体验
- 如果有反馈意见，请根据反馈进行相应的修改和优化"""

    @traceable(run_type="llm", name="Designer Agent")
    def generate_prototype(self, state: PrototypeState) -> Dict[str, Any]:
        """
        生成原型代码
        
        Args:
            state: 当前状态
            
        Returns:
            包含生成代码的字典
        """
        # 解析需求
        requirements_info = parse_requirements(state["requirements"])
        
        # 构建提示词
        user_prompt = f"""
用户需求：{state["requirements"]}

需求分析：
- 原型类型：{requirements_info['type']}
- 样式风格：{requirements_info['style']}
- 是否需要交互：{requirements_info['interactive']}
- 是否响应式：{requirements_info['responsive']}

请根据以上需求生成高保真原型代码。
"""
        
        # 如果有验证反馈，添加到提示词中
        if state.get("validation_feedback"):
            user_prompt += f"\n\n验证反馈：{state['validation_feedback']}\n请根据反馈修改和优化代码。"
        
        # 调用通义千问生成代码
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            content = response.choices[0].message.content

            # 记录token使用情况
            if self.config.enable_debug:
                print(f"🔧 Designer Token使用: {response.usage}")

        except Exception as e:
            print(f"❌ Designer调用模型失败: {e}")
            # 返回默认的错误处理代码
            content = self._get_fallback_code()
        
        # 解析生成的代码
        html_code, css_code, js_code = self._parse_generated_code(content)
        
        # 验证代码语法
        validation_result = validate_code_syntax(html_code, css_code, js_code)
        
        return {
            "html_code": html_code,
            "css_code": css_code,
            "js_code": js_code,
            "validation_result": validation_result,
            "current_agent": "designer"
        }
    
    def _parse_generated_code(self, content: str) -> tuple[str, str, str]:
        """
        从LLM响应中解析HTML、CSS和JavaScript代码
        
        Args:
            content: LLM响应内容
            
        Returns:
            (html_code, css_code, js_code)
        """
        html_code = ""
        css_code = ""
        js_code = ""
        
        # 解析HTML代码块
        if "```html" in content:
            start = content.find("```html") + 7
            end = content.find("```", start)
            if end != -1:
                html_code = content[start:end].strip()
        
        # 解析CSS代码块
        if "```css" in content:
            start = content.find("```css") + 6
            end = content.find("```", start)
            if end != -1:
                css_code = content[start:end].strip()
        
        # 解析JavaScript代码块
        if "```javascript" in content:
            start = content.find("```javascript") + 13
            end = content.find("```", start)
            if end != -1:
                js_code = content[start:end].strip()
        elif "```js" in content:
            start = content.find("```js") + 5
            end = content.find("```", start)
            if end != -1:
                js_code = content[start:end].strip()
        
        return html_code, css_code, js_code

    def _get_fallback_code(self) -> str:
        """
        获取fallback代码，当模型调用失败时使用

        Returns:
            包含基本HTML、CSS、JS的fallback内容
        """
        return """
```html
<div class="container">
    <h1>原型生成失败</h1>
    <p>抱歉，由于技术问题，无法生成您请求的原型。请稍后重试。</p>
    <button onclick="location.reload()">重新加载</button>
</div>
```

```css
.container {
    max-width: 800px;
    margin: 50px auto;
    padding: 20px;
    text-align: center;
    font-family: Arial, sans-serif;
}

h1 {
    color: #e74c3c;
    margin-bottom: 20px;
}

button {
    background-color: #3498db;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
}

button:hover {
    background-color: #2980b9;
}
```

```javascript
console.log('原型生成失败，使用fallback代码');
```
"""


# 创建Designer Agent节点函数
def designer_node(state: PrototypeState) -> Dict[str, Any]:
    """
    Designer节点函数，用于LangGraph工作流

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    designer = DesignerAgent()
    result = designer.generate_prototype(state)

    # 更新迭代计数
    iteration_count = state.get("iteration_count", 0) + 1

    return {
        **result,
        "iteration_count": iteration_count
    }
