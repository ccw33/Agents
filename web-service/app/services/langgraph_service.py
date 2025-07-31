# LangGraph框架服务实现
"""
LangGraph框架的Agent服务实现

通过子进程调用LangGraph框架中的Agent
支持prototype_design等专用Agent
"""

import os
import sys
import json
import asyncio
import subprocess
import uuid
from typing import Dict, Any, Optional, AsyncGenerator
from pathlib import Path

from app.services.agent_service import AgentService
from app.core.config import get_agent_framework_path
from app.core.exceptions import AgentExecutionError, AgentNotFoundError


class LangGraphService(AgentService):
    """LangGraph框架服务实现"""

    def __init__(self):
        super().__init__("langgraph")
        self.framework_path = get_agent_framework_path("langgraph")
        # prototype_design的特殊路径
        self.prototype_design_path = os.path.join(self.framework_path, "prototype_design")

    async def execute_prototype_design_stream(
        self,
        requirements: str,
        config: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式执行prototype_design agent

        Args:
            requirements: 原型设计需求
            config: 执行配置

        Yields:
            设计过程中的事件和最终结果
        """
        # 添加prototype_design路径到Python路径
        sys.path.insert(0, self.prototype_design_path)

        try:
            # 导入prototype_design模块
            from graph import PrototypeDesignWorkflow

            # 创建工作流实例
            workflow = PrototypeDesignWorkflow()
            thread_id = str(uuid.uuid4())

            # 推送开始事件
            yield {
                "type": "start",
                "message": "开始原型设计",
                "requirements": requirements,
                "thread_id": thread_id
            }

            # 流式执行并推送进度
            for event in workflow.stream_run(requirements, thread_id):
                # 转换事件格式
                for node_name, node_data in event.items():
                    if node_name == "designer":
                        yield {
                            "type": "progress",
                            "step": "designer",
                            "message": f"Designer正在工作... (第{node_data.get('iteration_count', 0)}次迭代)",
                            "data": node_data
                        }
                    elif node_name == "validator":
                        result = node_data.get('validation_result', 'UNKNOWN')
                        feedback = node_data.get('validation_feedback', '')
                        yield {
                            "type": "progress",
                            "step": "validator",
                            "message": f"Validator验证结果: {result}",
                            "validation_result": result,
                            "feedback": feedback[:200] + "..." if len(feedback) > 200 else feedback,
                            "data": node_data
                        }
                    elif node_name == "finalize":
                        yield {
                            "type": "progress",
                            "step": "finalize",
                            "message": "正在生成最终原型...",
                            "data": node_data
                        }

            # 获取最终结果
            final_result = workflow.run(requirements, thread_id)

            # 推送完成事件
            yield {
                "type": "complete",
                "message": "原型设计完成",
                "success": final_result.get("success", False),
                "result": final_result
            }

        except Exception as e:
            # 推送错误事件
            yield {
                "type": "error",
                "message": f"原型设计失败: {str(e)}",
                "error": str(e)
            }
        finally:
            # 清理Python路径
            if self.prototype_design_path in sys.path:
                sys.path.remove(self.prototype_design_path)

    async def _execute_prototype_design(
        self,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        timeout: int = 600  # prototype_design需要更长时间
    ) -> Dict[str, Any]:
        """
        执行prototype_design agent（非流式）

        Args:
            input_data: 输入数据，应包含requirements字段
            config: 执行配置
            timeout: 超时时间

        Returns:
            执行结果
        """
        requirements = input_data.get("requirements")
        if not requirements:
            raise AgentExecutionError("prototype_design需要requirements参数")

        # 添加prototype_design路径到Python路径
        sys.path.insert(0, self.prototype_design_path)

        try:
            # 导入prototype_design模块
            from graph import PrototypeDesignWorkflow

            # 创建工作流实例
            workflow = PrototypeDesignWorkflow()
            thread_id = str(uuid.uuid4())

            # 执行设计
            result = await asyncio.to_thread(workflow.run, requirements, thread_id)

            return result

        except Exception as e:
            raise AgentExecutionError(f"prototype_design执行失败: {str(e)}")
        finally:
            # 清理Python路径
            if self.prototype_design_path in sys.path:
                sys.path.remove(self.prototype_design_path)

    async def execute_agent(
        self,
        agent_type: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """执行LangGraph Agent"""

        # 特殊处理prototype_design
        if agent_type == "prototype_design":
            return await self._execute_prototype_design(input_data, config, timeout)

        # 准备执行参数
        execution_params = {
            "agent_type": agent_type,
            "input_data": input_data,
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
            # 假设在LangGraph目录下有一个runner.py脚本来执行Agent
            cmd = [
                "python", "runner.py",
                "--input", input_file,
                "--output", output_file,
                "--agent-type", agent_type
            ]
            
            self.logger.info(
                "执行LangGraph命令",
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
                self.logger.error("LangGraph执行失败", error=error_msg)
                raise AgentExecutionError(f"LangGraph执行失败: {error_msg}")
            
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
                        result = {"output": stdout_str}
                else:
                    result = {"output": "执行完成，无输出"}
            
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
            raise AgentNotFoundError(agent_type, "langgraph")
            
        finally:
            # 清理临时文件
            for temp_file in [input_file, output_file]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
    
    async def list_available_agents(self) -> Dict[str, Any]:
        """列出可用的LangGraph Agent"""
        
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
            # 如果没有list_agents.py，返回默认信息（包含prototype_design）
            agents_info = {
                "framework": "langgraph",
                "agents": {
                    "chat_agent": {
                        "description": "基础对话Agent",
                        "input_schema": {"message": "str"}
                    },
                    "research_agent": {
                        "description": "研究分析Agent",
                        "input_schema": {"query": "str", "max_results": "int"}
                    }
                }
            }

            # 检查prototype_design是否可用
            if os.path.exists(self.prototype_design_path):
                agents_info["agents"]["prototype_design"] = {
                    "description": "高保真原型设计Agent，基于LangGraph和多模态验证",
                    "input_schema": {
                        "requirements": "str"
                    },
                    "features": [
                        "智能设计生成HTML/CSS/JavaScript",
                        "多模态验证（截图分析）",
                        "迭代优化（最多5次）",
                        "本地服务器预览",
                        "响应式设计支持"
                    ],
                    "output_schema": {
                        "success": "bool",
                        "prototype_url": "str",
                        "iteration_count": "int",
                        "is_approved": "bool",
                        "html_code": "str",
                        "css_code": "str",
                        "js_code": "str"
                    }
                }

            return agents_info
        except json.JSONDecodeError:
            raise AgentExecutionError("Agent列表输出格式错误")
    
    async def validate_agent_config(
        self,
        agent_type: str,
        config: Dict[str, Any]
    ) -> bool:
        """验证LangGraph Agent配置"""
        
        # 基础验证
        if not agent_type:
            return False
        
        # 获取可用Agent列表进行验证
        try:
            available_agents = await self.list_available_agents()
            agents = available_agents.get("agents", {})
            
            if agent_type not in agents:
                return False
            
            # 可以添加更多配置验证逻辑
            return True
            
        except Exception:
            # 如果无法获取Agent列表，进行基础验证
            return isinstance(config, dict)
