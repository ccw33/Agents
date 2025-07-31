# 应用配置管理
"""
配置管理模块

使用pydantic-settings管理应用配置
支持环境变量和.env文件
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "AI Agent Web Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Agent框架路径配置
    AGENT_FRAMEWORKS_PATH: str = "../agent-frameworks"
    LANGGRAPH_PATH: str = "../agent-frameworks/langgraph"
    AUTOGEN_PATH: str = "../agent-frameworks/autogen"
    CREWAI_PATH: str = "../agent-frameworks/crewai"
    
    # Agent执行配置
    AGENT_TIMEOUT: int = 300  # 5分钟超时
    MAX_CONCURRENT_AGENTS: int = 10
    
    # 可选：数据库配置
    DATABASE_URL: str = ""

    # 可选：Redis配置
    REDIS_URL: str = ""

    # API密钥配置（如果需要认证）
    API_KEY: str = ""
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # LLM API配置（可选）
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量


# 创建全局配置实例
settings = Settings()


def get_agent_framework_path(framework: str) -> str:
    """获取指定框架的路径"""
    framework_paths = {
        "langgraph": settings.LANGGRAPH_PATH,
        "autogen": settings.AUTOGEN_PATH,
        "crewai": settings.CREWAI_PATH
    }
    
    path = framework_paths.get(framework)
    if not path:
        raise ValueError(f"不支持的框架: {framework}")
    
    # 转换为绝对路径
    if not os.path.isabs(path):
        # 从web-service目录开始计算相对路径
        web_service_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(web_service_dir, path)

    return os.path.abspath(path)


def validate_framework_paths():
    """验证所有框架路径是否存在"""
    frameworks = ["langgraph", "autogen", "crewai"]
    missing_paths = []
    
    for framework in frameworks:
        try:
            path = get_agent_framework_path(framework)
            if not os.path.exists(path):
                missing_paths.append(f"{framework}: {path}")
        except ValueError as e:
            missing_paths.append(str(e))
    
    if missing_paths:
        raise RuntimeError(f"以下框架路径不存在: {', '.join(missing_paths)}")
    
    return True
