# 统一异常处理
"""
自定义异常类和异常处理机制

提供统一的错误响应格式和异常处理逻辑
"""

from typing import Optional, Dict, Any


class AgentException(Exception):
    """Agent相关异常基类"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(self.message)


class FrameworkNotFoundError(AgentException):
    """框架不存在异常"""
    
    def __init__(self, framework: str):
        super().__init__(
            message=f"不支持的框架: {framework}",
            status_code=400,
            error_code="FRAMEWORK_NOT_FOUND"
        )


class AgentNotFoundError(AgentException):
    """Agent不存在异常"""
    
    def __init__(self, agent_type: str, framework: str):
        super().__init__(
            message=f"在框架 {framework} 中未找到Agent类型: {agent_type}",
            status_code=404,
            error_code="AGENT_NOT_FOUND"
        )


class AgentExecutionError(AgentException):
    """Agent执行异常"""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=f"Agent执行失败: {message}",
            status_code=500,
            detail=detail,
            error_code="AGENT_EXECUTION_ERROR"
        )


class AgentTimeoutError(AgentException):
    """Agent执行超时异常"""
    
    def __init__(self, timeout: int):
        super().__init__(
            message=f"Agent执行超时 ({timeout}秒)",
            status_code=408,
            error_code="AGENT_TIMEOUT"
        )


class ValidationError(AgentException):
    """输入验证异常"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        detail = f"字段 '{field}' 验证失败" if field else None
        super().__init__(
            message=f"输入验证失败: {message}",
            status_code=422,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class ConfigurationError(AgentException):
    """配置错误异常"""
    
    def __init__(self, message: str):
        super().__init__(
            message=f"配置错误: {message}",
            status_code=500,
            error_code="CONFIGURATION_ERROR"
        )


class ResourceLimitError(AgentException):
    """资源限制异常"""
    
    def __init__(self, message: str):
        super().__init__(
            message=f"资源限制: {message}",
            status_code=429,
            error_code="RESOURCE_LIMIT_ERROR"
        )


def format_error_response(exc: AgentException) -> Dict[str, Any]:
    """格式化错误响应"""
    response = {
        "error": exc.message,
        "status_code": exc.status_code
    }
    
    if exc.detail:
        response["detail"] = exc.detail
    
    if exc.error_code:
        response["error_code"] = exc.error_code
    
    return response
