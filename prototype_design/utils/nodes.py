"""
高保真原型设计agent的节点函数
包含designer、validator、file_manager等核心节点
"""

import os
from typing import Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from .state import PrototypeState
from .prompts import DESIGNER_PROMPT, VALIDATOR_PROMPT, FEEDBACK_TEMPLATE
from .tools import PrototypeFileManager, LocalServerManager, validate_code_syntax


# 初始化LLM
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0.1,
    max_tokens=4000
)

# 初始化工具
file_manager = PrototypeFileManager()
server_manager = LocalServerManager()


def designer_node(state: PrototypeState) -> Dict[str, Any]:
    """Designer节点：根据需求生成原型代码"""
    print(f"🎨 Designer开始工作... (第 {state['iteration_count'] + 1} 次迭代)")
    
    try:
        # 准备提示
        feedback_section = ""
        if state.get('validation_feedback') and state['iteration_count'] > 0:
            feedback_section = FEEDBACK_TEMPLATE.format(
                validation_feedback=state['validation_feedback'],
                iteration_count=state['iteration_count']
            )
        
        prompt = DESIGNER_PROMPT.format(
            user_requirements=state['user_requirements'],
            feedback_section=feedback_section
        )
        
        # 调用LLM生成代码
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # 提取代码
        prototype_code = file_manager.extract_code_from_response(response.content)
        
        if not prototype_code:
            return {
                "error_message": "Designer无法生成有效的代码",
                "current_prototype": state.get('current_prototype', {})
            }
        
        # 验证代码语法
        is_valid, validation_msg = validate_code_syntax(prototype_code)
        if not is_valid:
            print(f"⚠️ 代码语法警告: {validation_msg}")
        
        print("✅ Designer完成代码生成")
        
        return {
            "current_prototype": prototype_code,
            "iteration_count": state['iteration_count'] + 1,
            "error_message": None
        }
        
    except Exception as e:
        print(f"❌ Designer节点出错: {e}")
        return {
            "error_message": f"Designer节点出错: {str(e)}",
            "current_prototype": state.get('current_prototype', {})
        }


def file_manager_node(state: PrototypeState) -> Dict[str, Any]:
    """文件管理节点：保存文件并启动服务器"""
    print("📁 文件管理器开始工作...")
    
    try:
        # 如果还没有项目路径，创建新项目
        if not state.get('output_path') or not state.get('project_id'):
            project_path, project_id = file_manager.create_project_directory()
        else:
            project_path = state['output_path']
            project_id = state['project_id']
        
        # 保存原型文件
        if state.get('current_prototype'):
            success = file_manager.save_prototype_files(
                project_path, 
                state['current_prototype']
            )
            
            if not success:
                return {
                    "error_message": "保存文件失败",
                    "output_path": project_path,
                    "project_id": project_id
                }
        
        # 启动或重启服务器
        server_url = server_manager.start_server(project_path)
        
        if not server_url:
            return {
                "error_message": "启动服务器失败",
                "output_path": project_path,
                "project_id": project_id
            }
        
        print(f"✅ 文件已保存到: {project_path}")
        print(f"🌐 服务器已启动: {server_url}")
        
        return {
            "output_path": project_path,
            "project_id": project_id,
            "server_url": server_url,
            "error_message": None
        }
        
    except Exception as e:
        print(f"❌ 文件管理节点出错: {e}")
        return {
            "error_message": f"文件管理节点出错: {str(e)}",
            "output_path": state.get('output_path', ""),
            "project_id": state.get('project_id', "")
        }


def validator_node(state: PrototypeState) -> Dict[str, Any]:
    """Validator节点：验证原型是否符合需求"""
    print("🔍 Validator开始验证...")
    
    try:
        if not state.get('current_prototype'):
            return {
                "validation_feedback": "没有可验证的原型代码",
                "is_approved": False
            }
        
        # 准备验证提示
        prototype = state['current_prototype']
        prompt = VALIDATOR_PROMPT.format(
            user_requirements=state['user_requirements'],
            html_code=prototype.get('html', ''),
            css_code=prototype.get('css', ''),
            js_code=prototype.get('js', '')
        )
        
        # 调用LLM进行验证
        response = llm.invoke([HumanMessage(content=prompt)])
        feedback = response.content
        
        # 判断是否通过验证
        is_approved = "APPROVED" in feedback.upper()
        
        if is_approved:
            print("✅ Validator验证通过")
        else:
            print("❌ Validator要求修改")
        
        return {
            "validation_feedback": feedback,
            "is_approved": is_approved
        }
        
    except Exception as e:
        print(f"❌ Validator节点出错: {e}")
        return {
            "validation_feedback": f"验证过程出错: {str(e)}",
            "is_approved": False,
            "error_message": f"Validator节点出错: {str(e)}"
        }


def should_continue(state: PrototypeState) -> str:
    """条件路由：决定下一步操作"""
    
    # 检查是否有错误
    if state.get('error_message'):
        print(f"❌ 发现错误，流程结束: {state['error_message']}")
        return "end"
    
    # 检查是否通过验证
    if state.get('is_approved'):
        print("🎉 原型通过验证，流程完成")
        return "end"
    
    # 检查是否超过最大迭代次数
    max_iterations = state.get('max_iterations', 5)
    if state.get('iteration_count', 0) >= max_iterations:
        print(f"⏰ 已达到最大迭代次数 ({max_iterations})，流程结束")
        return "end"
    
    # 继续迭代
    print("🔄 继续下一轮迭代")
    return "continue"
