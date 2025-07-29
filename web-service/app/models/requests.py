# API请求数据模型
"""
定义所有API请求的Pydantic模型

确保输入数据的类型安全和验证
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from enum import Enum


class FrameworkType(str, Enum):
    """支持的框架类型"""
    LANGGRAPH = "langgraph"
    AUTOGEN = "autogen"
    CREWAI = "crewai"


class AgentExecuteRequest(BaseModel):
    """统一Agent执行请求"""
    
    framework: FrameworkType = Field(..., description="使用的框架类型")
    agent_type: str = Field(..., description="Agent类型/名称", min_length=1)
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    config: Optional[Dict[str, Any]] = Field(default=None, description="执行配置")
    timeout: Optional[int] = Field(default=300, description="超时时间(秒)", ge=1, le=3600)
    
    @validator('agent_type')
    def validate_agent_type(cls, v):
        if not v.strip():
            raise ValueError('agent_type不能为空')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "framework": "langgraph",
                "agent_type": "chat_agent",
                "input_data": {
                    "message": "你好，请帮我分析一下市场趋势",
                    "context": {}
                },
                "config": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                "timeout": 300
            }
        }


class LangGraphRequest(BaseModel):
    """LangGraph专用请求"""
    
    graph_name: str = Field(..., description="图名称", min_length=1)
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    config: Optional[Dict[str, Any]] = Field(default=None, description="图配置")
    stream: bool = Field(default=False, description="是否流式输出")
    
    class Config:
        schema_extra = {
            "example": {
                "graph_name": "research_assistant",
                "input_data": {
                    "query": "人工智能的最新发展",
                    "max_results": 5
                },
                "config": {
                    "recursion_limit": 50
                },
                "stream": False
            }
        }


class AutoGenRequest(BaseModel):
    """AutoGen专用请求"""
    
    agent_config: str = Field(..., description="Agent配置名称", min_length=1)
    message: str = Field(..., description="消息内容", min_length=1)
    participants: Optional[List[str]] = Field(default=None, description="参与的Agent列表")
    max_rounds: Optional[int] = Field(default=10, description="最大对话轮数", ge=1, le=100)
    
    class Config:
        schema_extra = {
            "example": {
                "agent_config": "coding_team",
                "message": "请帮我写一个Python函数来计算斐波那契数列",
                "participants": ["coder", "reviewer"],
                "max_rounds": 10
            }
        }


class CrewAIRequest(BaseModel):
    """CrewAI专用请求"""
    
    crew_name: str = Field(..., description="Crew名称", min_length=1)
    inputs: Dict[str, Any] = Field(..., description="输入参数")
    process_type: Optional[str] = Field(default="sequential", description="执行流程类型")
    verbose: bool = Field(default=False, description="是否详细输出")
    
    class Config:
        schema_extra = {
            "example": {
                "crew_name": "research_crew",
                "inputs": {
                    "topic": "区块链技术",
                    "depth": "detailed"
                },
                "process_type": "sequential",
                "verbose": True
            }
        }


class HealthCheckRequest(BaseModel):
    """健康检查请求"""
    
    check_frameworks: bool = Field(default=True, description="是否检查框架状态")
    
    class Config:
        schema_extra = {
            "example": {
                "check_frameworks": True
            }
        }
