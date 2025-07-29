# 统一Agent API接口
"""
提供统一的Agent执行接口

用户可以通过这个接口调用任意框架的Agent，无需关心底层实现
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import structlog

from app.models.requests import AgentExecuteRequest, HealthCheckRequest
from app.models.responses import AgentExecuteResponse, HealthCheckResponse, ErrorResponse
from app.services.agent_service import AgentServiceFactory
from app.services.langgraph_service import LangGraphService
from app.services.autogen_service import AutoGenService
from app.services.crewai_service import CrewAIService
from app.core.exceptions import (
    AgentException, FrameworkNotFoundError, AgentNotFoundError,
    AgentExecutionError, ValidationError
)

logger = structlog.get_logger()

router = APIRouter()

# 初始化并注册所有框架服务
def initialize_services():
    """初始化所有框架服务"""
    try:
        # 注册LangGraph服务
        langgraph_service = LangGraphService()
        AgentServiceFactory.register_service("langgraph", langgraph_service)
        
        # 注册AutoGen服务
        autogen_service = AutoGenService()
        AgentServiceFactory.register_service("autogen", autogen_service)
        
        # 注册CrewAI服务
        crewai_service = CrewAIService()
        AgentServiceFactory.register_service("crewai", crewai_service)
        
        logger.info("所有框架服务初始化完成")
        
    except Exception as e:
        logger.error("框架服务初始化失败", error=str(e))
        raise

# 在模块加载时初始化服务
initialize_services()


@router.post(
    "/execute",
    response_model=AgentExecuteResponse,
    summary="执行Agent",
    description="统一的Agent执行接口，支持所有框架"
)
async def execute_agent(request: AgentExecuteRequest):
    """
    执行指定框架的Agent
    
    - **framework**: 框架类型 (langgraph/autogen/crewai)
    - **agent_type**: Agent类型/名称
    - **input_data**: 输入数据
    - **config**: 可选的执行配置
    - **timeout**: 超时时间(秒)
    """
    try:
        logger.info(
            "收到Agent执行请求",
            framework=request.framework,
            agent_type=request.agent_type
        )
        
        # 获取对应框架的服务
        service = AgentServiceFactory.get_service(request.framework.value)
        
        # 验证配置
        if request.config:
            is_valid = await service.validate_agent_config(
                request.agent_type,
                request.config
            )
            if not is_valid:
                raise ValidationError("Agent配置验证失败")
        
        # 执行Agent
        result = await service.execute_with_timeout(
            agent_type=request.agent_type,
            input_data=request.input_data,
            config=request.config,
            timeout=request.timeout
        )
        
        # 构建响应
        response = AgentExecuteResponse(
            status=result["status"],
            result=result.get("result"),
            execution_time=result["execution_time"],
            framework=result["framework"],
            agent_type=result["agent_type"]
        )
        
        logger.info(
            "Agent执行成功",
            framework=request.framework,
            agent_type=request.agent_type,
            execution_time=result["execution_time"]
        )
        
        return response
        
    except AgentException as e:
        logger.error("Agent执行异常", error=str(e))
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
    except Exception as e:
        logger.error("未处理的异常", error=str(e))
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get(
    "/frameworks",
    summary="获取支持的框架列表",
    description="返回所有已注册的框架及其状态"
)
async def list_frameworks():
    """获取支持的框架列表"""
    try:
        frameworks = AgentServiceFactory.list_frameworks()
        health_status = await AgentServiceFactory.health_check_all()
        
        return {
            "frameworks": frameworks,
            "status": health_status,
            "total": len(frameworks)
        }
        
    except Exception as e:
        logger.error("获取框架列表失败", error=str(e))
        raise HTTPException(status_code=500, detail="获取框架列表失败")


@router.get(
    "/frameworks/{framework}/agents",
    summary="获取框架的可用Agent列表",
    description="返回指定框架中所有可用的Agent"
)
async def list_framework_agents(framework: str):
    """获取指定框架的可用Agent列表"""
    try:
        service = AgentServiceFactory.get_service(framework)
        agents_info = await service.list_available_agents()
        
        return agents_info
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error("获取Agent列表失败", framework=framework, error=str(e))
        raise HTTPException(status_code=500, detail="获取Agent列表失败")


@router.post(
    "/health",
    response_model=HealthCheckResponse,
    summary="健康检查",
    description="检查服务和框架的健康状态"
)
async def health_check(request: HealthCheckRequest = HealthCheckRequest()):
    """健康检查接口"""
    try:
        response_data = {
            "status": "healthy",
            "service": "ai-agent-web-service",
            "version": "1.0.0"
        }
        
        if request.check_frameworks:
            frameworks_status = await AgentServiceFactory.health_check_all()
            response_data["frameworks"] = {
                framework: status["status"] 
                for framework, status in frameworks_status.items()
            }
        
        return HealthCheckResponse(**response_data)
        
    except Exception as e:
        logger.error("健康检查失败", error=str(e))
        return HealthCheckResponse(
            status="unhealthy",
            service="ai-agent-web-service",
            version="1.0.0"
        )
