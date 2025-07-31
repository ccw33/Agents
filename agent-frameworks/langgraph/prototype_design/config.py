"""
配置管理模块
负责加载和管理环境变量配置
"""

import os
from pathlib import Path
from typing import Optional
import getpass

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class Config:
    """
    配置管理类
    负责加载.env文件和管理环境变量
    """
    
    def __init__(self):
        """初始化配置"""
        self._load_env_file()
        self._validate_required_config()
    
    def _load_env_file(self):
        """加载.env文件"""
        env_file = Path(__file__).parent / ".env"

        if DOTENV_AVAILABLE:
            # 使用python-dotenv加载
            load_dotenv(env_file, override=False)
        elif env_file.exists():
            # 手动解析.env文件
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # 只有当环境变量不存在时才设置
                        if key.strip() not in os.environ:
                            os.environ[key.strip()] = value.strip()
    
    def _validate_required_config(self):
        """验证必需的配置"""
        required_vars = ["DASHSCOPE_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print("⚠️  缺少必要的环境变量:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n请在.env文件中设置这些变量，或者手动设置环境变量")
            
            # 提供交互式设置选项
            if input("是否现在设置？(y/n): ").lower() == 'y':
                for var in missing_vars:
                    value = getpass.getpass(f"请输入 {var}: ")
                    os.environ[var] = value
    
    @property
    def dashscope_api_key(self) -> str:
        """DashScope API密钥"""
        return os.getenv("DASHSCOPE_API_KEY", "")
    
    @property
    def dashscope_base_url(self) -> str:
        """DashScope API基础URL"""
        return os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    @property
    def designer_model(self) -> str:
        """Designer使用的模型"""
        return os.getenv("DESIGNER_MODEL", "qwen-coder-plus-latest")
    
    @property
    def validator_model(self) -> str:
        """Validator使用的模型"""
        return os.getenv("VALIDATOR_MODEL", "qwen-vl-plus")
    
    @property
    def max_input_tokens(self) -> int:
        """最大输入token数（Designer使用）"""
        return int(os.getenv("MAX_INPUT_TOKENS", "8000"))

    @property
    def validator_max_input_tokens(self) -> int:
        """Validator最大输入token数"""
        return int(os.getenv("VALIDATOR_MAX_INPUT_TOKENS", "128000"))

    @property
    def max_output_tokens(self) -> int:
        """最大输出token数"""
        return int(os.getenv("MAX_OUTPUT_TOKENS", "4000"))
    
    @property
    def langsmith_api_key(self) -> Optional[str]:
        """LangSmith API密钥"""
        return os.getenv("LANGSMITH_API_KEY")
    
    @property
    def langsmith_tracing(self) -> bool:
        """是否启用LangSmith追踪"""
        return os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    
    @property
    def langsmith_project(self) -> str:
        """LangSmith项目名称"""
        return os.getenv("LANGSMITH_PROJECT", "prototype-design-agent")
    
    @property
    def default_server_port(self) -> int:
        """默认服务器端口"""
        return int(os.getenv("DEFAULT_SERVER_PORT", "8000"))
    
    @property
    def iteration_limit(self) -> int:
        """迭代次数限制"""
        return int(os.getenv("ITERATION_LIMIT", "5"))
    
    @property
    def enable_debug(self) -> bool:
        """是否启用调试模式"""
        return os.getenv("ENABLE_DEBUG", "false").lower() == "true"
    
    def setup_langsmith(self):
        """设置LangSmith环境变量"""
        if self.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
        
        if self.langsmith_tracing:
            os.environ["LANGSMITH_TRACING"] = "true"
            
        os.environ["LANGSMITH_PROJECT"] = self.langsmith_project
    
    def get_openai_client_config(self) -> dict:
        """获取OpenAI客户端配置"""
        return {
            "api_key": self.dashscope_api_key,
            "base_url": self.dashscope_base_url,
        }
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("🔧 当前配置:")
        print(f"   Designer模型: {self.designer_model}")
        print(f"   Validator模型: {self.validator_model}")
        print(f"   Designer最大输入Token: {self.max_input_tokens}")
        print(f"   Validator最大输入Token: {self.validator_max_input_tokens}")
        print(f"   最大输出Token: {self.max_output_tokens}")
        print(f"   迭代限制: {self.iteration_limit}")
        print(f"   服务器端口: {self.default_server_port}")
        print(f"   LangSmith追踪: {self.langsmith_tracing}")
        if self.enable_debug:
            print(f"   调试模式: 已启用")


# 全局配置实例
config = Config()

# 设置LangSmith
config.setup_langsmith()


def get_config() -> Config:
    """获取全局配置实例"""
    return config


def reload_config():
    """重新加载配置"""
    global config
    config = Config()
    config.setup_langsmith()
    return config
