# AutoGen框架服务实现
"""
AutoGen框架的Agent服务实现

通过子进程调用AutoGen框架中的Agent
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, Any, Optional

from app.services.agent_service import AgentService
from app.core.config import get_agent_framework_path
from app.core.exceptions import AgentExecutionError, AgentNotFoundError


class AutoGenService(AgentService):
    """AutoGen框架服务实现"""
    
    def __init__(self):
        super().__init__("autogen")
        self.framework_path = get_agent_framework_path("autogen")
    
    async def execute_agent(
        self,
        agent_type: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """执行AutoGen Agent"""
        
        # 准备执行参数
        execution_params = {
            "agent_config": agent_type,
            "message": input_data.get("message", ""),
            "participants": input_data.get("participants", []),
            "max_rounds": input_data.get("max_rounds", 10),
            "config": config or {}
        }
        
        # 创建临时输入文件
        input_file = os.path.join(self.framework_path, f"temp_input_{os.getpid()}.json")
        output_file = os.path.join(self.framework_path, f"temp_output_{os.getpid()}.json")
        
        try:
            # 写入输入参数
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(execution_params, f, ensure_ascii=False, indent=2)
            
            # 构建执行命令
            # 假设在AutoGen目录下有一个runner.py脚本来执行Agent
            cmd = [
                "python", "runner.py",
                "--input", input_file,
                "--output", output_file,
                "--agent-config", agent_type
            ]
            
            self.logger.info(
                "执行AutoGen命令",
                cmd=" ".join(cmd),
                cwd=self.framework_path
            )
            
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.framework_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            # 检查执行结果
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "未知错误"
                self.logger.error("AutoGen执行失败", error=error_msg)
                raise AgentExecutionError(f"AutoGen执行失败: {error_msg}")
            
            # 读取输出结果
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
            else:
                # 如果没有输出文件，尝试从stdout解析
                stdout_str = stdout.decode('utf-8') if stdout else ""
                if stdout_str:
                    try:
                        result = json.loads(stdout_str)
                    except json.JSONDecodeError:
                        result = {"conversation": [{"agent": "system", "message": stdout_str}]}
                else:
                    result = {"conversation": [], "final_result": "执行完成，无输出"}
            
            return result
            
        except asyncio.TimeoutError:
            # 超时时杀死进程
            if 'process' in locals():
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
            raise
            
        except FileNotFoundError:
            raise AgentNotFoundError(agent_type, "autogen")
            
        finally:
            # 清理临时文件
            for temp_file in [input_file, output_file]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
    
    async def list_available_agents(self) -> Dict[str, Any]:
        """列出可用的AutoGen Agent配置"""
        
        try:
            # 调用框架的列表命令
            cmd = ["python", "list_agents.py"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.framework_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "未知错误"
                raise AgentExecutionError(f"获取Agent列表失败: {error_msg}")
            
            # 解析输出
            agents_info = json.loads(stdout.decode('utf-8'))
            return agents_info
            
        except FileNotFoundError:
            # 如果没有list_agents.py，返回默认信息
            return {
                "framework": "autogen",
                "agents": {
                    "coding_team": {
                        "description": "编程团队，包含程序员和代码审查员",
                        "participants": ["coder", "reviewer"],
                        "input_schema": {"message": "str", "max_rounds": "int"}
                    },
                    "research_team": {
                        "description": "研究团队，包含研究员和分析师",
                        "participants": ["researcher", "analyst"],
                        "input_schema": {"message": "str", "max_rounds": "int"}
                    },
                    "chat_assistant": {
                        "description": "单一对话助手",
                        "participants": ["assistant"],
                        "input_schema": {"message": "str"}
                    }
                }
            }
        except json.JSONDecodeError:
            raise AgentExecutionError("Agent列表输出格式错误")
    
    async def validate_agent_config(
        self,
        agent_type: str,
        config: Dict[str, Any]
    ) -> bool:
        """验证AutoGen Agent配置"""
        
        # 基础验证
        if not agent_type:
            return False
        
        # 获取可用Agent列表进行验证
        try:
            available_agents = await self.list_available_agents()
            agents = available_agents.get("agents", {})
            
            if agent_type not in agents:
                return False
            
            # 验证必需的参数
            if "message" not in config and "message" not in config.get("input_data", {}):
                return False
            
            # 验证max_rounds参数
            max_rounds = config.get("max_rounds", 10)
            if not isinstance(max_rounds, int) or max_rounds < 1 or max_rounds > 100:
                return False
            
            return True
            
        except Exception:
            # 如果无法获取Agent列表，进行基础验证
            return isinstance(config, dict) and "message" in str(config)
