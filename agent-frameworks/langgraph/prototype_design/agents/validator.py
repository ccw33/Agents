"""
Validator Agent模块
负责验证Designer生成的原型是否符合用户需求
使用通义千问qwen-turbo模型进行验证
"""

from typing import Dict, Any, List
from langsmith import traceable
from langsmith.wrappers import wrap_openai
import openai

try:
    from ..state import PrototypeState
    from .tools import validate_code_syntax
    from ..config import get_config
except ImportError:
    from state import PrototypeState
    from agents.tools import validate_code_syntax
    from config import get_config


class ValidatorAgent:
    """
    Validator Agent类
    负责验证原型质量和符合度
    使用通义千问qwen-turbo模型
    """

    def __init__(self):
        """
        初始化Validator Agent
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
        self.model_name = self.config.validator_model
        self.max_tokens = min(self.config.max_output_tokens, 2000)  # Validator使用较少token
        self.temperature = 0.3
        
        self.system_prompt = """你是一个专业的产品经理和UI/UX评审专家，负责验证原型是否符合用户需求。

你需要从以下维度评估原型：

1. **功能完整性**：是否实现了用户要求的所有功能
2. **UI/UX设计**：界面是否美观、用户体验是否良好
3. **响应式设计**：是否适配不同屏幕尺寸
4. **交互体验**：交互是否流畅、符合预期
5. **代码质量**：代码是否规范、性能是否良好

请给出明确的验证结果：
- APPROVED：完全符合需求，可以通过
- REJECTED：不符合需求，需要修改

如果是REJECTED，请提供具体的修改建议，包括：
- 具体问题描述
- 改进建议
- 优先级（高/中/低）

请按照以下格式输出：

验证结果：[APPROVED/REJECTED]

问题分析：
[详细的问题分析]

修改建议：
[具体的修改建议，如果是APPROVED则说明优点]"""

    @traceable(run_type="llm", name="Validator Agent")
    def validate_prototype(self, state: PrototypeState) -> Dict[str, Any]:
        """
        验证原型
        
        Args:
            state: 当前状态
            
        Returns:
            包含验证结果的字典
        """
        # 首先进行代码语法验证
        syntax_validation = validate_code_syntax(
            state.get("html_code", ""),
            state.get("css_code", ""),
            state.get("js_code", "")
        )
        
        # 构建验证提示词
        user_prompt = f"""
用户原始需求：
{state["requirements"]}

生成的代码：

HTML代码：
```html
{state.get("html_code", "")}
```

CSS代码：
```css
{state.get("css_code", "")}
```

JavaScript代码：
```javascript
{state.get("js_code", "")}
```

代码语法验证结果：
- 是否有效：{syntax_validation['is_valid']}
- 错误：{syntax_validation['errors']}
- 警告：{syntax_validation['warnings']}

当前迭代次数：{state.get("iteration_count", 0)}

请根据用户需求验证这个原型的质量。
"""
        
        # 调用通义千问进行验证
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
                print(f"🔧 Validator Token使用: {response.usage}")

        except Exception as e:
            print(f"❌ Validator调用模型失败: {e}")
            # 返回默认的拒绝结果
            content = "验证结果：REJECTED\n\n问题分析：\n模型调用失败，无法进行验证。\n\n修改建议：\n请检查网络连接和API配置，然后重试。"
        
        # 解析验证结果
        is_approved, feedback = self._parse_validation_result(content)
        
        # 如果语法验证失败，强制拒绝
        if not syntax_validation['is_valid']:
            is_approved = False
            feedback = f"代码语法错误：{'; '.join(syntax_validation['errors'])}\n\n{feedback}"
        
        return {
            "validation_result": "APPROVED" if is_approved else "REJECTED",
            "validation_feedback": feedback,
            "is_approved": is_approved,
            "current_agent": "validator"
        }
    
    def _parse_validation_result(self, content: str) -> tuple[bool, str]:
        """
        解析验证结果
        
        Args:
            content: LLM响应内容
            
        Returns:
            (is_approved, feedback)
        """
        is_approved = False
        feedback = content
        
        # 查找验证结果
        if "验证结果：APPROVED" in content or "APPROVED" in content.upper():
            is_approved = True
        elif "验证结果：REJECTED" in content or "REJECTED" in content.upper():
            is_approved = False
        
        return is_approved, feedback


# 创建Validator Agent节点函数
def validator_node(state: PrototypeState) -> Dict[str, Any]:
    """
    Validator节点函数，用于LangGraph工作流
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    validator = ValidatorAgent()
    result = validator.validate_prototype(state)
    
    return result


# 路由函数：决定下一步操作
def should_continue(state: PrototypeState) -> str:
    """
    决定工作流的下一步

    Args:
        state: 当前状态

    Returns:
        下一个节点名称
    """
    # 获取配置中的迭代限制
    config = get_config()
    iteration_limit = config.iteration_limit

    # 如果通过验证，结束流程
    if state.get("is_approved", False):
        return "finalize"

    # 如果迭代次数达到上限，强制结束
    if state.get("iteration_count", 0) >= iteration_limit:
        return "finalize"

    # 否则返回Designer继续修改
    return "designer"
