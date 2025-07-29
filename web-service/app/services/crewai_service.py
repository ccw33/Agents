# CrewAI框架服务实现
"""
CrewAI框架的Agent服务实现

通过子进程调用CrewAI框架中的Crew
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, Any, Optional

from app.services.agent_service import AgentService
from app.core.config import get_agent_framework_path
from app.core.exceptions import AgentExecutionError, AgentNotFoundError


class CrewAIService(AgentService):
    """CrewAI框架服务实现"""
    
    def __init__(self):
        super().__init__("crewai")
        self.framework_path = get_agent_framework_path("crewai")
    
    async def execute_agent(
        self,
        agent_type: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """执行CrewAI Crew"""
        
        # 准备执行参数
        execution_params = {
            "crew_name": agent_type,
            "inputs": input_data.get("inputs", {}),
            "process_type": input_data.get("process_type", "sequential"),
            "verbose": input_data.get("verbose", False),
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
            # 假设在CrewAI目录下有一个runner.py脚本来执行Crew
            cmd = [
                "python", "runner.py",
                "--input", input_file,
                "--output", output_file,
                "--crew-name", agent_type
            ]
            
            self.logger.info(
                "执行CrewAI命令",
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
                self.logger.error("CrewAI执行失败", error=error_msg)
                raise AgentExecutionError(f"CrewAI执行失败: {error_msg}")
            
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
                        result = {"result": stdout_str, "tasks_output": []}
                else:
                    result = {"result": "执行完成，无输出", "tasks_output": []}
            
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
            raise AgentNotFoundError(agent_type, "crewai")
            
        finally:
            # 清理临时文件
            for temp_file in [input_file, output_file]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
    
    async def list_available_agents(self) -> Dict[str, Any]:
        """列出可用的CrewAI Crew"""
        
        try:
            # 调用框架的列表命令
            cmd = ["python", "list_crews.py"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.framework_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "未知错误"
                raise AgentExecutionError(f"获取Crew列表失败: {error_msg}")
            
            # 解析输出
            crews_info = json.loads(stdout.decode('utf-8'))
            return crews_info
            
        except FileNotFoundError:
            # 如果没有list_crews.py，返回默认信息
            return {
                "framework": "crewai",
                "crews": {
                    "research_crew": {
                        "description": "研究团队，包含研究员和报告分析师",
                        "agents": ["researcher", "reporting_analyst"],
                        "input_schema": {"topic": "str", "depth": "str"}
                    },
                    "content_crew": {
                        "description": "内容创作团队，包含作家和编辑",
                        "agents": ["writer", "editor"],
                        "input_schema": {"topic": "str", "style": "str", "length": "int"}
                    },
                    "analysis_crew": {
                        "description": "数据分析团队，包含分析师和可视化专家",
                        "agents": ["analyst", "visualizer"],
                        "input_schema": {"data_source": "str", "analysis_type": "str"}
                    }
                }
            }
        except json.JSONDecodeError:
            raise AgentExecutionError("Crew列表输出格式错误")
    
    async def validate_agent_config(
        self,
        agent_type: str,
        config: Dict[str, Any]
    ) -> bool:
        """验证CrewAI Crew配置"""
        
        # 基础验证
        if not agent_type:
            return False
        
        # 获取可用Crew列表进行验证
        try:
            available_crews = await self.list_available_agents()
            crews = available_crews.get("crews", {})
            
            if agent_type not in crews:
                return False
            
            # 验证inputs参数
            inputs = config.get("inputs", {})
            if not isinstance(inputs, dict):
                return False
            
            # 验证process_type参数
            process_type = config.get("process_type", "sequential")
            if process_type not in ["sequential", "hierarchical"]:
                return False
            
            return True
            
        except Exception:
            # 如果无法获取Crew列表，进行基础验证
            return isinstance(config, dict) and "inputs" in config
