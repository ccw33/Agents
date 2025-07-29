# API响应数据模型
"""
定义所有API响应的Pydantic模型

确保输出数据的一致性和类型安全
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """执行状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RUNNING = "running"


class AgentExecuteResponse(BaseModel):
    """统一Agent执行响应"""
    
    status: ExecutionStatus = Field(..., description="执行状态")
    result: Optional[Dict[str, Any]] = Field(default=None, description="执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    execution_time: float = Field(..., description="执行时间(秒)")
    framework: str = Field(..., description="使用的框架")
    agent_type: str = Field(..., description="Agent类型")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "result": {
                    "output": "根据市场分析，当前科技股表现良好...",
                    "confidence": 0.85,
                    "sources": ["财经新闻", "市场数据"]
                },
                "error": None,
                "execution_time": 15.6,
                "framework": "langgraph",
                "agent_type": "market_analyst",
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class LangGraphResponse(BaseModel):
    """LangGraph专用响应"""
    
    status: ExecutionStatus = Field(..., description="执行状态")
    output: Optional[Dict[str, Any]] = Field(default=None, description="图输出")
    intermediate_steps: Optional[List[Dict[str, Any]]] = Field(default=None, description="中间步骤")
    error: Optional[str] = Field(default=None, description="错误信息")
    execution_time: float = Field(..., description="执行时间(秒)")
    graph_name: str = Field(..., description="图名称")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "output": {
                    "final_answer": "人工智能在2024年的主要发展包括...",
                    "research_results": []
                },
                "intermediate_steps": [
                    {"step": "search", "result": "找到10篇相关文章"},
                    {"step": "analyze", "result": "分析完成"}
                ],
                "error": None,
                "execution_time": 25.3,
                "graph_name": "research_assistant"
            }
        }


class AutoGenResponse(BaseModel):
    """AutoGen专用响应"""
    
    status: ExecutionStatus = Field(..., description="执行状态")
    conversation: Optional[List[Dict[str, Any]]] = Field(default=None, description="对话历史")
    final_result: Optional[str] = Field(default=None, description="最终结果")
    participants: List[str] = Field(default_factory=list, description="参与的Agent")
    rounds: int = Field(default=0, description="对话轮数")
    error: Optional[str] = Field(default=None, description="错误信息")
    execution_time: float = Field(..., description="执行时间(秒)")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "conversation": [
                    {"agent": "user", "message": "请写一个斐波那契函数"},
                    {"agent": "coder", "message": "我来写一个Python函数..."},
                    {"agent": "reviewer", "message": "代码看起来不错，建议..."}
                ],
                "final_result": "def fibonacci(n): ...",
                "participants": ["coder", "reviewer"],
                "rounds": 3,
                "error": None,
                "execution_time": 18.7
            }
        }


class CrewAIResponse(BaseModel):
    """CrewAI专用响应"""
    
    status: ExecutionStatus = Field(..., description="执行状态")
    result: Optional[str] = Field(default=None, description="Crew执行结果")
    tasks_output: Optional[List[Dict[str, Any]]] = Field(default=None, description="任务输出详情")
    crew_name: str = Field(..., description="Crew名称")
    error: Optional[str] = Field(default=None, description="错误信息")
    execution_time: float = Field(..., description="执行时间(秒)")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "result": "# 区块链技术研究报告\n\n## 概述\n区块链技术作为...",
                "tasks_output": [
                    {"task": "research", "output": "收集了20篇相关论文"},
                    {"task": "analyze", "output": "完成技术分析"},
                    {"task": "report", "output": "生成最终报告"}
                ],
                "crew_name": "research_crew",
                "error": None,
                "execution_time": 45.2
            }
        }


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    
    status: str = Field(..., description="服务状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    frameworks: Optional[Dict[str, str]] = Field(default=None, description="框架状态")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "ai-agent-web-service",
                "version": "1.0.0",
                "frameworks": {
                    "langgraph": "available",
                    "autogen": "available",
                    "crewai": "available"
                },
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应"""
    
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(default=None, description="错误详情")
    error_code: Optional[str] = Field(default=None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Agent执行失败",
                "detail": "输入参数格式不正确",
                "error_code": "VALIDATION_ERROR",
                "timestamp": "2024-01-15T10:30:00"
            }
        }
