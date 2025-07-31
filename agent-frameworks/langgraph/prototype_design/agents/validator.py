"""
Validator Agent模块
负责验证Designer生成的原型是否符合用户需求
使用通义千问qwen-vl-plus多模态模型和browser-use进行验证
"""

import os
import tempfile
import asyncio
import base64
from typing import Dict, Any, List
from pathlib import Path
from langsmith import traceable
from langsmith.wrappers import wrap_openai
import openai

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ playwright未安装，将使用文本模式验证")

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️ Pillow未安装，截图功能可能受限")

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
    使用通义千问qwen-vl-plus多模态模型和browser-use进行浏览器验证
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
        self.model_name = self.config.validator_model  # qwen-vl-plus
        self.max_input_tokens = self.config.validator_max_input_tokens  # 128000
        self.max_output_tokens = min(self.config.max_output_tokens, 50000)
        self.temperature = 0.3

        # 浏览器配置
        self.viewport = {"width": 1280, "height": 1024}
        # 是否显示浏览器窗口（调试模式下显示）
        self.headless = not self.config.enable_debug

        self.system_prompt = """你是一个专业的产品经理和UI/UX评审专家，负责验证原型是否符合用户需求。

你将收到：
1. 用户的原始需求描述
2. 原型页面的截图
3. 代码语法验证结果

请从以下维度评估原型：

1. **功能完整性**：从截图中能看到的功能是否符合用户需求（最重要）
2. **基本可用性**：界面元素是否清晰可见、基本交互是否可行
3. **视觉设计**：界面布局是否合理、基本美观度
4. **内容完整性**：是否包含了用户要求的核心内容元素

验证标准：
- 如果功能基本完整且界面可用，应该APPROVED
- 只有在功能严重缺失或界面完全不可用时才REJECTED
- 不要因为美观度不够或细节问题而拒绝，这些可以在后续迭代中改进

请给出明确的验证结果：
- APPROVED：基本符合需求，可以通过
- REJECTED：功能严重缺失或不可用，需要修改

如果是REJECTED，请提供具体的修改建议，包括：
- 具体问题描述
- 改进建议
- 优先级（高/中/低）

请按照以下格式输出：

验证结果：[APPROVED/REJECTED]

问题分析：
[基于截图的详细问题分析，重点关注功能完整性]

修改建议：
[具体的修改建议，如果是APPROVED则说明优点和可选的改进建议]"""

    def _create_html_file(self, html_code: str, css_code: str, js_code: str) -> str:
        """
        创建完整的HTML文件

        Args:
            html_code: HTML代码
            css_code: CSS代码
            js_code: JavaScript代码

        Returns:
            临时HTML文件路径
        """
        # 创建完整的HTML内容
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>原型验证</title>
    <style>
{css_code}
    </style>
</head>
<body>
{html_code}
    <script>
{js_code}
    </script>
</body>
</html>"""

        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        temp_file.write(full_html)
        temp_file.close()

        return temp_file.name

    async def _take_screenshot_with_playwright(self, html_file_path: str) -> str:
        """
        使用playwright截取页面截图

        Args:
            html_file_path: HTML文件路径

        Returns:
            截图的base64编码
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("playwright未安装，无法进行浏览器验证")

        browser = None
        try:
            # 启动playwright
            playwright = await async_playwright().start()

            # 启动浏览器
            browser = await playwright.chromium.launch(headless=self.headless)

            # 创建页面
            page = await browser.new_page(viewport=self.viewport)

            # 导航到HTML文件
            file_url = f"file://{os.path.abspath(html_file_path)}"
            await page.goto(file_url)

            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')

            # 截图
            screenshot_bytes = await page.screenshot(full_page=True)

            # 转换为base64
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

            return screenshot_base64

        except Exception as e:
            print(f"❌ 截图失败: {e}")
            raise
        finally:
            # 清理浏览器
            if browser:
                try:
                    await browser.close()
                except:
                    pass

    @traceable(run_type="llm", name="Validator Agent")
    def validate_prototype(self, state: PrototypeState) -> Dict[str, Any]:
        """
        验证原型（使用浏览器截图和多模态模型）

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

        html_file_path = None
        try:
            # 如果playwright可用，使用浏览器验证
            if PLAYWRIGHT_AVAILABLE:
                if self.config.enable_debug:
                    print("🔧 使用浏览器验证模式（Playwright）")
                    print(f"🔧 浏览器模式: {'有头模式（可见）' if not self.headless else '无头模式（不可见）'}")

                # 使用线程池来运行异步代码，避免事件循环冲突
                import concurrent.futures

                def run_async_validation():
                    return asyncio.run(self._validate_with_browser(state, syntax_validation))

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async_validation)
                    return future.result()
            else:
                if self.config.enable_debug:
                    print("⚠️ 使用文本验证模式（Playwright不可用）")
                # 降级到文本模式验证
                return self._validate_text_only(state, syntax_validation)

        except Exception as e:
            print(f"❌ 验证过程出错: {e}")
            # 返回默认的拒绝结果
            return {
                "validation_result": "REJECTED",
                "validation_feedback": f"验证过程出错：{str(e)}",
                "is_approved": False,
                "current_agent": "validator"
            }
        finally:
            # 清理临时文件
            if html_file_path and os.path.exists(html_file_path):
                try:
                    os.unlink(html_file_path)
                except:
                    pass

    async def _validate_with_browser(self, state: PrototypeState, syntax_validation: Dict) -> Dict[str, Any]:
        """
        使用浏览器和多模态模型进行验证
        """
        html_file_path = None
        try:
            # 创建HTML文件
            html_file_path = self._create_html_file(
                state.get("html_code", ""),
                state.get("css_code", ""),
                state.get("js_code", "")
            )

            if self.config.enable_debug:
                print(f"🔧 创建临时HTML文件: {html_file_path}")

            # 截图
            if self.config.enable_debug:
                print("🔧 启动浏览器进行截图...")
            screenshot_base64 = await self._take_screenshot_with_playwright(html_file_path)

            if self.config.enable_debug:
                print("✅ 截图完成，开始AI分析...")

            # 构建多模态验证提示词
            user_prompt = f"""
用户原始需求：
{state["requirements"]}

代码语法验证结果：
- 是否有效：{syntax_validation['is_valid']}
- 错误：{syntax_validation['errors']}
- 警告：{syntax_validation['warnings']}

当前迭代次数：{state.get("iteration_count", 0)}

请根据用户需求和页面截图验证这个原型的质量。
"""

            # 调用多模态模型进行验证
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
                ]}
            ]

            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_output_tokens
            )
            content = response.choices[0].message.content

            # 记录token使用情况
            if self.config.enable_debug:
                print(f"🔧 Validator Token使用: {response.usage}")

        except Exception as e:
            print(f"❌ Validator调用模型失败: {e}")
            content = "验证结果：REJECTED\n\n问题分析：\n模型调用失败，无法进行验证。\n\n修改建议：\n请检查网络连接和API配置，然后重试。"
        finally:
            # 清理临时文件
            if html_file_path and os.path.exists(html_file_path):
                try:
                    os.unlink(html_file_path)
                except:
                    pass

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

    def _validate_text_only(self, state: PrototypeState, syntax_validation: Dict) -> Dict[str, Any]:
        """
        文本模式验证（当browser-use不可用时的降级方案）
        """
        try:
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

            # 调用文本模型进行验证
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_output_tokens
            )
            content = response.choices[0].message.content

            # 记录token使用情况
            if self.config.enable_debug:
                print(f"🔧 Validator Token使用: {response.usage}")

        except Exception as e:
            print(f"❌ Validator调用模型失败: {e}")
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
