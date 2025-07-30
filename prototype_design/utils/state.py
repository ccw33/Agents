"""
高保真原型设计agent的状态定义
定义了整个工作流程中需要维护的状态信息
"""

from typing import Dict, TypedDict, Optional


class PrototypeState(TypedDict):
    """原型设计工作流的状态定义"""
    
    # 用户输入的需求描述
    user_requirements: str
    
    # 当前原型代码，包含HTML、CSS、JavaScript
    current_prototype: Dict[str, str]
    
    # validator的验证反馈
    validation_feedback: str
    
    # 当前迭代次数
    iteration_count: int
    
    # 是否通过验证
    is_approved: bool
    
    # 输出文件路径
    output_path: str
    
    # 本地服务器访问地址
    server_url: str
    
    # 项目唯一标识符
    project_id: str
    
    # 错误信息（如果有）
    error_message: Optional[str]
    
    # 设计历史记录
    design_history: list
    
    # 最大迭代次数
    max_iterations: int
