# AutoGen专用API接口
"""
AutoGen框架的专用API接口

提供针对AutoGen多代理对话特性优化的接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import structlog

from app.models.requests import AutoGenRequest
from app.models.responses import AutoGenResponse
from app.services.agent_service import AgentServiceFactory
from app.core.exceptions import AgentException

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/execute",
    response_model=AutoGenResponse,
    summary="执行AutoGen多代理对话",
    description="启动AutoGen多代理对话会话"
)
async def execute_autogen(request: AutoGenRequest):
    """
    执行AutoGen多代理对话
    
    - **agent_config**: Agent配置名称
    - **message**: 初始消息
    - **participants**: 参与的Agent列表
    - **max_rounds**: 最大对话轮数
    """
    try:
        logger.info("执行AutoGen对话", agent_config=request.agent_config)
        
        # 获取AutoGen服务
        service = AgentServiceFactory.get_service("autogen")
        
        # 准备输入数据
        input_data = {
            "message": request.message,
            "participants": request.participants or [],
            "max_rounds": request.max_rounds
        }
        
        # 执行对话
        result = await service.execute_with_timeout(
            agent_type=request.agent_config,
            input_data=input_data,
            config={},
            timeout=600  # AutoGen对话可能需要更长时间
        )
        
        # 构建响应
        agent_result = result.get("result", {})
        response = AutoGenResponse(
            status=result["status"],
            conversation=agent_result.get("conversation", []),
            final_result=agent_result.get("final_result"),
            participants=agent_result.get("participants", request.participants or []),
            rounds=agent_result.get("rounds", 0),
            execution_time=result["execution_time"]
        )
        
        return response
        
    except AgentException as e:
        logger.error("AutoGen执行异常", error=str(e))
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
    except Exception as e:
        logger.error("AutoGen执行失败", error=str(e))
        raise HTTPException(status_code=500, detail="AutoGen执行失败")


@router.get(
    "/configs",
    summary="获取可用的Agent配置",
    description="返回所有可用的AutoGen Agent配置"
)
async def list_agent_configs():
    """获取可用的AutoGen Agent配置列表"""
    try:
        service = AgentServiceFactory.get_service("autogen")
        configs_info = await service.list_available_agents()
        
        return configs_info
        
    except Exception as e:
        logger.error("获取Agent配置列表失败", error=str(e))
        raise HTTPException(status_code=500, detail="获取Agent配置列表失败")


@router.get(
    "/configs/{config_name}/info",
    summary="获取Agent配置详情",
    description="返回指定Agent配置的详细信息"
)
async def get_agent_config_info(config_name: str):
    """获取指定Agent配置的详细信息"""
    try:
        service = AgentServiceFactory.get_service("autogen")
        configs_info = await service.list_available_agents()
        
        agents = configs_info.get("agents", {})
        if config_name not in agents:
            raise HTTPException(status_code=404, detail=f"Agent配置 '{config_name}' 不存在")
        
        config_info = agents[config_name]
        return {
            "config_name": config_name,
            "description": config_info.get("description", ""),
            "participants": config_info.get("participants", []),
            "input_schema": config_info.get("input_schema", {}),
            "recommended_max_rounds": config_info.get("recommended_max_rounds", 10)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取Agent配置信息失败", config_name=config_name, error=str(e))
        raise HTTPException(status_code=500, detail="获取Agent配置信息失败")


@router.post(
    "/validate",
    summary="验证Agent配置",
    description="验证AutoGen Agent配置是否有效"
)
async def validate_agent_config(request: AutoGenRequest):
    """验证Agent配置"""
    try:
        service = AgentServiceFactory.get_service("autogen")
        
        is_valid = await service.validate_agent_config(
            request.agent_config,
            {
                "message": request.message,
                "participants": request.participants,
                "max_rounds": request.max_rounds
            }
        )
        
        return {
            "valid": is_valid,
            "config_name": request.agent_config,
            "message": "配置有效" if is_valid else "配置无效，请检查消息内容和参数"
        }
        
    except Exception as e:
        logger.error("验证Agent配置失败", error=str(e))
        raise HTTPException(status_code=500, detail="验证Agent配置失败")


class ContinueConversationRequest(BaseModel):
    """继续对话请求"""
    config_name: str = Field(..., description="Agent配置名称")
    message: str = Field(..., description="新消息")
    conversation_history: List[Dict[str, Any]] = Field(..., description="对话历史")
    max_additional_rounds: int = Field(default=5, description="最大额外轮数")

@router.post(
    "/chat/continue",
    summary="继续对话",
    description="在现有对话基础上继续多代理对话"
)
async def continue_conversation(request: ContinueConversationRequest):
    """继续现有的对话"""
    try:
        logger.info("继续AutoGen对话", config_name=request.config_name)

        service = AgentServiceFactory.get_service("autogen")

        # 准备输入数据，包含历史对话
        input_data = {
            "message": request.message,
            "conversation_history": request.conversation_history,
            "max_rounds": request.max_additional_rounds,
            "continue_mode": True
        }

        # 执行对话
        result = await service.execute_with_timeout(
            agent_type=request.config_name,
            input_data=input_data,
            config={},
            timeout=600
        )
        
        # 构建响应
        agent_result = result.get("result", {})
        response = AutoGenResponse(
            status=result["status"],
            conversation=agent_result.get("conversation", []),
            final_result=agent_result.get("final_result"),
            participants=agent_result.get("participants", []),
            rounds=agent_result.get("rounds", 0),
            execution_time=result["execution_time"]
        )
        
        return response
        
    except AgentException as e:
        logger.error("继续对话异常", error=str(e))
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
    except Exception as e:
        logger.error("继续对话失败", error=str(e))
        raise HTTPException(status_code=500, detail="继续对话失败")
