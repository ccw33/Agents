# CrewAI专用API接口
"""
CrewAI框架的专用API接口

提供针对CrewAI团队协作特性优化的接口
"""

from fastapi import APIRouter, HTTPException
import structlog

from app.models.requests import CrewAIRequest
from app.models.responses import CrewAIResponse
from app.services.agent_service import AgentServiceFactory
from app.core.exceptions import AgentException

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/execute",
    response_model=CrewAIResponse,
    summary="执行CrewAI团队",
    description="启动CrewAI团队执行任务"
)
async def execute_crewai(request: CrewAIRequest):
    """
    执行CrewAI团队
    
    - **crew_name**: Crew名称
    - **inputs**: 输入参数
    - **process_type**: 执行流程类型 (sequential/hierarchical)
    - **verbose**: 是否详细输出
    """
    try:
        logger.info("执行CrewAI团队", crew_name=request.crew_name)
        
        # 获取CrewAI服务
        service = AgentServiceFactory.get_service("crewai")
        
        # 准备输入数据
        input_data = {
            "inputs": request.inputs,
            "process_type": request.process_type,
            "verbose": request.verbose
        }
        
        # 执行Crew
        result = await service.execute_with_timeout(
            agent_type=request.crew_name,
            input_data=input_data,
            config={},
            timeout=900  # CrewAI任务可能需要更长时间
        )
        
        # 构建响应
        crew_result = result.get("result", {})
        response = CrewAIResponse(
            status=result["status"],
            result=crew_result.get("result"),
            tasks_output=crew_result.get("tasks_output", []),
            crew_name=request.crew_name,
            execution_time=result["execution_time"]
        )
        
        return response
        
    except AgentException as e:
        logger.error("CrewAI执行异常", error=str(e))
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
    except Exception as e:
        logger.error("CrewAI执行失败", error=str(e))
        raise HTTPException(status_code=500, detail="CrewAI执行失败")


@router.get(
    "/crews",
    summary="获取可用的Crew列表",
    description="返回所有可用的CrewAI团队"
)
async def list_crews():
    """获取可用的CrewAI团队列表"""
    try:
        service = AgentServiceFactory.get_service("crewai")
        crews_info = await service.list_available_agents()
        
        return crews_info
        
    except Exception as e:
        logger.error("获取Crew列表失败", error=str(e))
        raise HTTPException(status_code=500, detail="获取Crew列表失败")


@router.get(
    "/crews/{crew_name}/info",
    summary="获取Crew详情",
    description="返回指定Crew的详细信息"
)
async def get_crew_info(crew_name: str):
    """获取指定Crew的详细信息"""
    try:
        service = AgentServiceFactory.get_service("crewai")
        crews_info = await service.list_available_agents()
        
        crews = crews_info.get("crews", {})
        if crew_name not in crews:
            raise HTTPException(status_code=404, detail=f"Crew '{crew_name}' 不存在")
        
        crew_info = crews[crew_name]
        return {
            "crew_name": crew_name,
            "description": crew_info.get("description", ""),
            "agents": crew_info.get("agents", []),
            "input_schema": crew_info.get("input_schema", {}),
            "supported_processes": crew_info.get("supported_processes", ["sequential", "hierarchical"]),
            "estimated_duration": crew_info.get("estimated_duration", "未知")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取Crew信息失败", crew_name=crew_name, error=str(e))
        raise HTTPException(status_code=500, detail="获取Crew信息失败")


@router.post(
    "/validate",
    summary="验证Crew配置",
    description="验证CrewAI Crew配置是否有效"
)
async def validate_crew_config(request: CrewAIRequest):
    """验证Crew配置"""
    try:
        service = AgentServiceFactory.get_service("crewai")
        
        is_valid = await service.validate_agent_config(
            request.crew_name,
            {
                "inputs": request.inputs,
                "process_type": request.process_type,
                "verbose": request.verbose
            }
        )
        
        return {
            "valid": is_valid,
            "crew_name": request.crew_name,
            "message": "配置有效" if is_valid else "配置无效，请检查输入参数和流程类型"
        }
        
    except Exception as e:
        logger.error("验证Crew配置失败", error=str(e))
        raise HTTPException(status_code=500, detail="验证Crew配置失败")


@router.get(
    "/crews/{crew_name}/tasks",
    summary="获取Crew任务列表",
    description="返回指定Crew包含的任务信息"
)
async def get_crew_tasks(crew_name: str):
    """获取指定Crew的任务列表"""
    try:
        service = AgentServiceFactory.get_service("crewai")
        crews_info = await service.list_available_agents()
        
        crews = crews_info.get("crews", {})
        if crew_name not in crews:
            raise HTTPException(status_code=404, detail=f"Crew '{crew_name}' 不存在")
        
        crew_info = crews[crew_name]
        tasks = crew_info.get("tasks", [])
        
        return {
            "crew_name": crew_name,
            "tasks": tasks,
            "total_tasks": len(tasks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取Crew任务失败", crew_name=crew_name, error=str(e))
        raise HTTPException(status_code=500, detail="获取Crew任务失败")


@router.post(
    "/crews/{crew_name}/estimate",
    summary="估算执行时间",
    description="根据输入参数估算Crew执行时间"
)
async def estimate_execution_time(crew_name: str, inputs: dict):
    """估算Crew执行时间"""
    try:
        service = AgentServiceFactory.get_service("crewai")
        crews_info = await service.list_available_agents()
        
        crews = crews_info.get("crews", {})
        if crew_name not in crews:
            raise HTTPException(status_code=404, detail=f"Crew '{crew_name}' 不存在")
        
        # 简单的时间估算逻辑（实际实现可能更复杂）
        crew_info = crews[crew_name]
        base_time = crew_info.get("base_execution_time", 60)  # 基础时间60秒
        
        # 根据输入复杂度调整时间
        complexity_factor = 1.0
        if isinstance(inputs, dict):
            # 根据输入参数数量和内容长度估算复杂度
            param_count = len(inputs)
            content_length = sum(len(str(v)) for v in inputs.values())
            complexity_factor = 1 + (param_count * 0.1) + (content_length / 1000 * 0.2)
        
        estimated_time = int(base_time * complexity_factor)
        
        return {
            "crew_name": crew_name,
            "estimated_time_seconds": estimated_time,
            "estimated_time_minutes": round(estimated_time / 60, 1),
            "complexity_factor": round(complexity_factor, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("估算执行时间失败", crew_name=crew_name, error=str(e))
        raise HTTPException(status_code=500, detail="估算执行时间失败")
