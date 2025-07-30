"""
LangGraph工作流定义
定义了高保真原型设计的完整工作流程
"""

import os
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langsmith import traceable

try:
    from .state import PrototypeState
    from .agents.designer import designer_node
    from .agents.validator import validator_node, should_continue
    from .agents.tools import write_prototype_file, start_local_server
    from .config import get_config
except ImportError:
    # 如果相对导入失败，使用绝对导入
    from state import PrototypeState
    from agents.designer import designer_node
    from agents.validator import validator_node, should_continue
    from agents.tools import write_prototype_file, start_local_server
    from config import get_config


@traceable(run_type="tool", name="Finalize Prototype")
def finalize_node(state: PrototypeState) -> Dict[str, Any]:
    """
    最终化节点：生成文件并启动服务器
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    
    # 写入原型文件
    if state.get("html_code") and state.get("css_code"):
        filepath = write_prototype_file(
            state["html_code"],
            state["css_code"],
            state.get("js_code", ""),
            output_dir
        )
        
        # 启动本地服务器
        try:
            server_url = start_local_server(output_dir, port=8000)
            filename = os.path.basename(filepath)
            prototype_url = f"{server_url}/{filename}"
        except Exception as e:
            prototype_url = f"文件已生成：{filepath}，请手动启动服务器查看"
    else:
        prototype_url = "代码生成失败，无法创建原型文件"
    
    return {
        "prototype_url": prototype_url,
        "current_agent": "finalized"
    }


def initialize_state(requirements: str) -> PrototypeState:
    """
    初始化状态，为所有字段提供默认值

    Args:
        requirements: 用户需求（必填）

    Returns:
        初始化后的状态
    """
    return {
        "requirements": requirements,
        "messages": [],
        "html_code": "",
        "css_code": "",
        "js_code": "",
        "validation_result": "",
        "validation_feedback": "",
        "iteration_count": 0,
        "is_approved": False,
        "prototype_url": "",
        "current_agent": "start"
    }


def create_prototype_graph() -> StateGraph:
    """
    创建原型设计工作流图

    Returns:
        编译后的StateGraph
    """
    # 创建内存检查点保存器
    checkpointer = MemorySaver()

    # 创建状态图
    workflow = StateGraph(PrototypeState)

    # 添加节点
    workflow.add_node("designer", designer_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("finalize", finalize_node)

    # 添加边
    workflow.add_edge(START, "designer")
    workflow.add_edge("designer", "validator")

    # 添加条件边
    workflow.add_conditional_edges(
        "validator",
        should_continue,
        {
            "designer": "designer",
            "finalize": "finalize"
        }
    )

    workflow.add_edge("finalize", END)

    # 编译图
    graph = workflow.compile(checkpointer=checkpointer)

    return graph


# 为LangGraph Studio导出图形
graph = create_prototype_graph()


def visualize_graph(save_path: str = None, show_xray: bool = False):
    """
    可视化工作流图

    Args:
        save_path: 保存图片的路径
        show_xray: 是否显示详细的内部结构
    """
    try:
        from IPython.display import Image, display

        if show_xray:
            image_data = graph.get_graph(xray=True).draw_mermaid_png()
        else:
            image_data = graph.get_graph().draw_mermaid_png()

        if save_path:
            with open(save_path, 'wb') as f:
                f.write(image_data)
            print(f"✅ 图形已保存到: {save_path}")

        # 在Jupyter环境中显示
        display(Image(image_data))

    except ImportError:
        print("⚠️  需要在Jupyter/IPython环境中运行，或安装相关依赖")
        print("或者使用 LangGraph Studio 进行可视化")
    except Exception as e:
        print(f"❌ 可视化失败: {e}")
        print("💡 建议使用 LangGraph Studio: langgraph dev")


def get_graph_mermaid():
    """
    获取图形的Mermaid代码

    Returns:
        Mermaid图形代码
    """
    try:
        return graph.get_graph().draw_mermaid()
    except Exception as e:
        print(f"❌ 获取Mermaid代码失败: {e}")
        return None


class PrototypeDesignWorkflow:
    """
    原型设计工作流类
    """
    
    def __init__(self):
        """初始化工作流"""
        self.graph = create_prototype_graph()
    
    @traceable(run_type="chain", name="Prototype Design Workflow")
    def run(self, requirements: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        运行原型设计工作流
        
        Args:
            requirements: 用户需求
            thread_id: 线程ID，用于状态管理
            
        Returns:
            最终结果
        """
        # 初始状态
        initial_state = initialize_state(requirements)
        initial_state["messages"] = [HumanMessage(content=f"用户需求：{requirements}")]
        
        # 配置
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        # 运行工作流
        try:
            final_state = self.graph.invoke(initial_state, config=config)
            
            return {
                "success": True,
                "prototype_url": final_state.get("prototype_url"),
                "iteration_count": final_state.get("iteration_count", 0),
                "is_approved": final_state.get("is_approved", False),
                "validation_feedback": final_state.get("validation_feedback"),
                "html_code": final_state.get("html_code"),
                "css_code": final_state.get("css_code"),
                "js_code": final_state.get("js_code")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prototype_url": None
            }
    
    def stream_run(self, requirements: str, thread_id: str = "default"):
        """
        流式运行工作流，可以观察中间过程
        
        Args:
            requirements: 用户需求
            thread_id: 线程ID
            
        Yields:
            中间状态更新
        """
        # 初始状态
        initial_state = {
            "messages": [HumanMessage(content=f"用户需求：{requirements}")],
            "requirements": requirements,
            "html_code": None,
            "css_code": None,
            "js_code": None,
            "validation_result": None,
            "validation_feedback": None,
            "iteration_count": 0,
            "is_approved": False,
            "prototype_url": None,
            "current_agent": "start"
        }
        
        # 配置
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        # 流式运行
        for event in self.graph.stream(initial_state, config=config):
            yield event
