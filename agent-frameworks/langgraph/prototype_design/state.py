"""
状态定义模块
定义了原型设计工作流中的状态结构
"""

from typing import List, Optional, Annotated
from typing_extensions import TypedDict, NotRequired
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class PrototypeState(TypedDict):
    """
    原型设计工作流的状态

    Attributes:
        messages: 对话消息历史
        requirements: 用户的原型需求 (必填)
        html_code: 生成的HTML代码
        css_code: 生成的CSS代码
        js_code: 生成的JavaScript代码
        validation_result: 验证结果
        validation_feedback: 验证反馈
        iteration_count: 迭代次数
        is_approved: 是否通过验证
        prototype_url: 原型访问地址
        current_agent: 当前执行的agent
    """
    # 必填字段
    requirements: str

    # 可选字段（有默认值）
    messages: NotRequired[Annotated[List[BaseMessage], add_messages]]
    html_code: NotRequired[str]
    css_code: NotRequired[str]
    js_code: NotRequired[str]
    validation_result: NotRequired[str]
    validation_feedback: NotRequired[str]
    iteration_count: NotRequired[int]
    is_approved: NotRequired[bool]
    prototype_url: NotRequired[str]
    current_agent: NotRequired[str]
