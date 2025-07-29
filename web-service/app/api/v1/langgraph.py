# LangGraph专用API接口
"""
LangGraph框架的专用API接口

提供针对LangGraph特性优化的接口
"""

from fastapi import APIRouter, HTTPException
import structlog

from app.models.requests import LangGraphRequest
from app.models.responses import LangGraphResponse
from app.services.agent_service import AgentServiceFactory
from app.core.exceptions import AgentException

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/execute",
    response_model=LangGraphResponse,
    summary="执行LangGraph图",
    description="执行指定的LangGraph图"
)
async def execute_langgraph(request: LangGraphRequest):
    """
    执行LangGraph图
    
    - **graph_name**: 图名称
    - **input_data**: 输入数据
    - **config**: 图配置
    - **stream**: 是否流式输出
    """
    try:
        logger.info("执行LangGraph图", graph_name=request.graph_name)
        
        # 获取LangGraph服务
        service = AgentServiceFactory.get_service("langgraph")
        
        # 准备输入数据
        input_data = request.input_data.copy()
        if request.stream:
            input_data["_stream"] = True
        
        # 执行图
        result = await service.execute_with_timeout(
            agent_type=request.graph_name,
            input_data=input_data,
            config=request.config,
            timeout=300
        )
        
        # 构建响应
        response = LangGraphResponse(
            status=result["status"],
            output=result.get("result"),
            execution_time=result["execution_time"],
            graph_name=request.graph_name
        )
        
        # 如果结果中包含中间步骤，添加到响应中
        if isinstance(result.get("result"), dict):
            response.intermediate_steps = result["result"].get("intermediate_steps")
        
        return response
        
    except AgentException as e:
        logger.error("LangGraph执行异常", error=str(e))
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
    except Exception as e:
        logger.error("LangGraph执行失败", error=str(e))
        raise HTTPException(status_code=500, detail="LangGraph执行失败")


@router.get(
    "/graphs",
    summary="获取可用的图列表",
    description="返回所有可用的LangGraph图"
)
async def list_graphs():
    """获取可用的LangGraph图列表"""
    try:
        service = AgentServiceFactory.get_service("langgraph")
        graphs_info = await service.list_available_agents()
        
        return graphs_info
        
    except Exception as e:
        logger.error("获取图列表失败", error=str(e))
        raise HTTPException(status_code=500, detail="获取图列表失败")


@router.get(
    "/graphs/{graph_name}/schema",
    summary="获取图的输入模式",
    description="返回指定图的输入数据模式"
)
async def get_graph_schema(graph_name: str):
    """获取指定图的输入模式"""
    try:
        service = AgentServiceFactory.get_service("langgraph")
        graphs_info = await service.list_available_agents()
        
        graphs = graphs_info.get("agents", {})
        if graph_name not in graphs:
            raise HTTPException(status_code=404, detail=f"图 '{graph_name}' 不存在")
        
        graph_info = graphs[graph_name]
        return {
            "graph_name": graph_name,
            "description": graph_info.get("description", ""),
            "input_schema": graph_info.get("input_schema", {}),
            "config_schema": graph_info.get("config_schema", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取图模式失败", graph_name=graph_name, error=str(e))
        raise HTTPException(status_code=500, detail="获取图模式失败")


@router.post(
    "/validate",
    summary="验证图配置",
    description="验证LangGraph图的配置是否有效"
)
async def validate_graph_config(request: LangGraphRequest):
    """验证图配置"""
    try:
        service = AgentServiceFactory.get_service("langgraph")
        
        is_valid = await service.validate_agent_config(
            request.graph_name,
            {
                "input_data": request.input_data,
                "config": request.config
            }
        )
        
        return {
            "valid": is_valid,
            "graph_name": request.graph_name,
            "message": "配置有效" if is_valid else "配置无效"
        }
        
    except Exception as e:
        logger.error("验证图配置失败", error=str(e))
        raise HTTPException(status_code=500, detail="验证图配置失败")
