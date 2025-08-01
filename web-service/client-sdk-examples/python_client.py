#!/usr/bin/env python3
"""
AI Agent Web Service - Python客户端SDK

用于在Kubernetes集群内调用AI Agent Web Service的Python客户端库。

使用示例:
    from python_client import AIAgentClient
    
    client = AIAgentClient()
    health = client.health_check()
    print(f"服务状态: {health['status']}")
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AIAgentClientError(Exception):
    """AI Agent客户端异常"""
    pass


class AIAgentClient:
    """AI Agent Web Service客户端"""
    
    def __init__(self, 
                 base_url: str = "http://web-service.ai-agents.svc.cluster.local:8000",
                 timeout: int = 30,
                 retries: int = 3):
        """
        初始化客户端
        
        Args:
            base_url: 服务基础URL
            timeout: 请求超时时间（秒）
            retries: 重试次数
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = self._create_session_with_retries(retries)
        
        # 配置日志
        self.logger = logging.getLogger(__name__)
    
    def _create_session_with_retries(self, retries: int) -> requests.Session:
        """创建带重试策略的会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.logger.debug(f"发送请求: {method} {url}")
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {method} {url} - {e}")
            raise AIAgentClientError(f"请求失败: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            raise AIAgentClientError(f"响应格式错误: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态信息
            
        Example:
            >>> client = AIAgentClient()
            >>> health = client.health_check()
            >>> print(health['status'])
            healthy
        """
        return self._make_request("GET", "/health")
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        获取服务信息
        
        Returns:
            服务详细信息
            
        Example:
            >>> client = AIAgentClient()
            >>> info = client.get_service_info()
            >>> print(info['service'])
            AI Agent Web Service
        """
        return self._make_request("GET", "/api/v1/info")
    
    def check_agent_health(self) -> Dict[str, Any]:
        """
        检查Agent健康状态
        
        Returns:
            Agent健康状态信息
            
        Example:
            >>> client = AIAgentClient()
            >>> agent_health = client.check_agent_health()
            >>> print(agent_health['agent_available'])
            True
        """
        return self._make_request("GET", "/api/v1/prototype_design/health")
    
    def create_prototype(self, requirement: str, style: str = "现代简约") -> Dict[str, Any]:
        """
        创建原型设计
        
        Args:
            requirement: 设计需求描述
            style: 设计风格，默认为"现代简约"
            
        Returns:
            设计结果
            
        Example:
            >>> client = AIAgentClient()
            >>> result = client.create_prototype("用户登录页面", "简约风格")
            >>> print(result['status'])
            success
        """
        data = {
            "requirement": requirement,
            "style": style
        }
        
        return self._make_request(
            "POST", 
            "/api/v1/prototype_design/design",
            json=data,
            headers={"Content-Type": "application/json"}
        )
    
    def is_healthy(self) -> bool:
        """
        检查服务是否健康
        
        Returns:
            True如果服务健康，False否则
        """
        try:
            health = self.health_check()
            return health.get('status') == 'healthy'
        except AIAgentClientError:
            return False
    
    def wait_for_service(self, max_attempts: int = 30, interval: int = 2) -> bool:
        """
        等待服务就绪
        
        Args:
            max_attempts: 最大尝试次数
            interval: 检查间隔（秒）
            
        Returns:
            True如果服务就绪，False如果超时
        """
        import time
        
        for attempt in range(max_attempts):
            if self.is_healthy():
                self.logger.info(f"服务就绪，尝试次数: {attempt + 1}")
                return True
            
            self.logger.debug(f"等待服务就绪，尝试 {attempt + 1}/{max_attempts}")
            time.sleep(interval)
        
        self.logger.warning(f"服务等待超时，最大尝试次数: {max_attempts}")
        return False


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建客户端
    client = AIAgentClient()
    
    try:
        # 等待服务就绪
        print("等待服务就绪...")
        if not client.wait_for_service():
            print("❌ 服务等待超时")
            exit(1)
        
        # 健康检查
        print("\n🔍 健康检查...")
        health = client.health_check()
        print(f"✅ 服务状态: {health['status']}")
        print(f"📋 服务版本: {health['version']}")
        
        # 获取服务信息
        print("\n📊 获取服务信息...")
        info = client.get_service_info()
        print(f"🏷️  服务名称: {info['service']}")
        print(f"🌐 内网地址: {info['internal_url']}")
        print(f"🎯 支持特性: {', '.join(info['features'])}")
        
        # 检查Agent健康状态
        print("\n🤖 检查Agent状态...")
        agent_health = client.check_agent_health()
        print(f"✅ Agent可用: {agent_health['agent_available']}")
        print(f"💬 状态信息: {agent_health['message']}")
        
        # 创建原型设计
        print("\n🎨 创建原型设计...")
        result = client.create_prototype(
            requirement="用户管理界面",
            style="现代简约风格"
        )
        print(f"✅ 设计状态: {result['status']}")
        print(f"💡 设计结果: {result['message']}")
        
        print("\n🎉 所有测试完成！")

    except AIAgentClientError as e:
        print(f"❌ 客户端错误: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        exit(1)
