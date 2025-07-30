"""
高保真原型设计agent主应用
基于LangGraph构建的多角色协作原型设计系统
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from utils.state import PrototypeState
from utils.nodes import (
    designer_node,
    file_manager_node, 
    validator_node,
    should_continue
)


def create_prototype_agent() -> StateGraph:
    """创建原型设计agent的工作流图"""
    
    # 创建状态图
    workflow = StateGraph(PrototypeState)
    
    # 添加节点
    workflow.add_node("designer", designer_node)
    workflow.add_node("file_manager", file_manager_node)
    workflow.add_node("validator", validator_node)
    
    # 设置入口点
    workflow.add_edge(START, "designer")
    
    # 设置节点间的连接
    workflow.add_edge("designer", "file_manager")
    workflow.add_edge("file_manager", "validator")
    
    # 添加条件路由
    workflow.add_conditional_edges(
        "validator",
        should_continue,
        {
            "continue": "designer",  # 继续迭代
            "end": END              # 结束流程
        }
    )
    
    return workflow


def run_prototype_design(user_requirements: str, max_iterations: int = 5) -> Dict[str, Any]:
    """运行原型设计流程"""
    
    print("🚀 启动高保真原型设计agent")
    print(f"📝 用户需求: {user_requirements}")
    print(f"🔄 最大迭代次数: {max_iterations}")
    print("-" * 50)
    
    # 创建工作流
    workflow = create_prototype_agent()
    
    # 添加内存检查点
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    # 初始化状态
    initial_state = {
        "user_requirements": user_requirements,
        "current_prototype": {},
        "validation_feedback": "",
        "iteration_count": 0,
        "is_approved": False,
        "output_path": "",
        "server_url": "",
        "project_id": "",
        "error_message": None,
        "design_history": [],
        "max_iterations": max_iterations
    }
    
    # 配置
    config = {"configurable": {"thread_id": "prototype_design_session"}}
    
    try:
        # 运行工作流
        final_state = None
        for state in app.stream(initial_state, config):
            final_state = state
            # 可以在这里添加实时状态更新的逻辑
        
        # 提取最终状态
        if final_state:
            # 获取最后一个节点的状态
            last_node_state = list(final_state.values())[-1]
            
            print("-" * 50)
            print("🎯 原型设计完成!")
            
            # 输出结果
            result = {
                "success": not bool(last_node_state.get('error_message')),
                "project_path": last_node_state.get('output_path', ''),
                "server_url": last_node_state.get('server_url', ''),
                "project_id": last_node_state.get('project_id', ''),
                "iterations": last_node_state.get('iteration_count', 0),
                "approved": last_node_state.get('is_approved', False),
                "error": last_node_state.get('error_message'),
                "final_feedback": last_node_state.get('validation_feedback', '')
            }
            
            if result['success'] and result['server_url']:
                print(f"✅ 原型开发成功!")
                print(f"📁 项目路径: {result['project_path']}")
                print(f"🌐 访问地址: {result['server_url']}")
                print(f"🔄 迭代次数: {result['iterations']}")
                print(f"✨ 验证状态: {'通过' if result['approved'] else '未通过'}")
            else:
                print(f"❌ 原型开发失败: {result['error']}")
            
            return result
        else:
            return {
                "success": False,
                "error": "工作流执行失败，未获得最终状态"
            }
            
    except Exception as e:
        print(f"❌ 运行过程中出错: {e}")
        return {
            "success": False,
            "error": f"运行过程中出错: {str(e)}"
        }


# 创建可导出的图对象
graph = create_prototype_agent().compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    # 测试示例
    test_requirements = """
    请帮我设计一个现代化的产品展示页面，包含以下功能：
    1. 顶部导航栏，包含Logo和菜单
    2. 英雄区域，有吸引人的标题和背景图
    3. 产品卡片展示区域，至少3个产品
    4. 联系我们表单
    5. 页脚信息
    
    要求：
    - 响应式设计，支持移动端
    - 现代化的设计风格
    - 流畅的交互动画
    - 美观的配色方案
    """
    
    result = run_prototype_design(test_requirements)
    print("\n" + "="*50)
    print("最终结果:", result)
