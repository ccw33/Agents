# Agent服务抽象基类
"""
定义Agent服务的统一接口规范

所有框架的服务实现都应该继承这个基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import time
import structlog

from app.core.exceptions import AgentTimeoutError, AgentExecutionError
from app.core.config import settings

logger = structlog.get_logger()


class AgentService(ABC):
    """Agent服务抽象基类"""
    
    def __init__(self, framework_name: str):
        self.framework_name = framework_name
        self.logger = logger.bind(framework=framework_name)
    
    @abstractmethod
    async def execute_agent(
        self,
        agent_type: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        执行Agent
        
        Args:
            agent_type: Agent类型/名称
            input_data: 输入数据
            config: 执行配置
            timeout: 超时时间(秒)
            
        Returns:
            执行结果字典
            
        Raises:
            AgentExecutionError: Agent执行失败
            AgentTimeoutError: 执行超时
        """
        pass
    
    @abstractmethod
    async def list_available_agents(self) -> Dict[str, Any]:
        """
        列出可用的Agent类型
        
        Returns:
            可用Agent的信息字典
        """
        pass
    
    @abstractmethod
    async def validate_agent_config(
        self,
        agent_type: str,
        config: Dict[str, Any]
    ) -> bool:
        """
        验证Agent配置是否有效
        
        Args:
            agent_type: Agent类型
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        pass
    
    async def execute_with_timeout(
        self,
        agent_type: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        带超时控制的Agent执行
        
        这是一个通用的超时控制包装器，子类可以直接使用
        """
        start_time = time.time()
        
        try:
            self.logger.info(
                "开始执行Agent",
                agent_type=agent_type,
                timeout=timeout
            )
            
            # 使用asyncio.wait_for实现超时控制
            result = await asyncio.wait_for(
                self.execute_agent(agent_type, input_data, config, timeout),
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            self.logger.info(
                "Agent执行成功",
                agent_type=agent_type,
                execution_time=execution_time
            )
            
            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "framework": self.framework_name,
                "agent_type": agent_type
            }
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            self.logger.error(
                "Agent执行超时",
                agent_type=agent_type,
                timeout=timeout,
                execution_time=execution_time
            )
            raise AgentTimeoutError(timeout)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                "Agent执行失败",
                agent_type=agent_type,
                error=str(e),
                execution_time=execution_time
            )
            raise AgentExecutionError(str(e))
    
    async def health_check(self) -> Dict[str, str]:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        try:
            # 尝试列出可用的Agent来验证框架是否正常
            await self.list_available_agents()
            return {"status": "healthy", "framework": self.framework_name}
        except Exception as e:
            self.logger.error("框架健康检查失败", error=str(e))
            return {"status": "unhealthy", "framework": self.framework_name, "error": str(e)}


class AgentServiceFactory:
    """Agent服务工厂类"""
    
    _services: Dict[str, AgentService] = {}
    
    @classmethod
    def register_service(cls, framework: str, service: AgentService):
        """注册框架服务"""
        cls._services[framework] = service
    
    @classmethod
    def get_service(cls, framework: str) -> AgentService:
        """获取框架服务"""
        service = cls._services.get(framework)
        if not service:
            raise ValueError(f"未注册的框架服务: {framework}")
        return service
    
    @classmethod
    def list_frameworks(cls) -> list:
        """列出所有已注册的框架"""
        return list(cls._services.keys())
    
    @classmethod
    async def health_check_all(cls) -> Dict[str, Dict[str, str]]:
        """检查所有框架的健康状态"""
        results = {}
        for framework, service in cls._services.items():
            results[framework] = await service.health_check()
        return results
