# PrototypeDesign服务器管理服务
"""
管理prototype_design的本地服务器功能

集成现有的prototype_design服务器，提供文件访问和预览功能
"""

import os
import sys
import asyncio
import threading
import time
from typing import Optional, Dict, Any
import structlog

from app.core.config import get_agent_framework_path
from app.core.exceptions import AgentExecutionError

logger = structlog.get_logger()


class PrototypeServerService:
    """PrototypeDesign服务器管理服务"""
    
    def __init__(self):
        """初始化服务"""
        self.langgraph_path = get_agent_framework_path("langgraph")
        self.prototype_path = os.path.join(self.langgraph_path, "prototype_design")
        self.output_dir = os.path.join(self.prototype_path, "outputs")
        self._server_instance = None
        self._server_thread = None
        self._server_port = None
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def start_server(self, port: int = 8000) -> str:
        """
        启动prototype_design服务器
        
        Args:
            port: 端口号
            
        Returns:
            服务器访问地址
        """
        if self._server_instance and self._server_instance.is_running:
            return f"http://localhost:{self._server_port}"
        
        # 添加prototype_design路径到Python路径
        if self.prototype_path not in sys.path:
            sys.path.insert(0, self.prototype_path)
        
        try:
            # 导入prototype_design的服务器模块
            from server import PrototypeServer
            
            # 创建服务器实例
            self._server_instance = PrototypeServer(self.output_dir, port)
            
            # 在后台线程启动服务器
            def run_server():
                try:
                    url = self._server_instance.start()
                    self._server_port = self._server_instance.port
                    logger.info("PrototypeDesign服务器已启动", url=url)
                except Exception as e:
                    logger.error("启动PrototypeDesign服务器失败", error=str(e))
            
            self._server_thread = threading.Thread(target=run_server, daemon=True)
            self._server_thread.start()
            
            # 等待服务器启动
            await asyncio.sleep(2)
            
            # 检查服务器是否成功启动
            if self._server_instance and self._server_instance.is_running:
                return f"http://localhost:{self._server_instance.port}"
            else:
                raise AgentExecutionError("服务器启动失败")
                
        except ImportError as e:
            raise AgentExecutionError(f"无法导入prototype_design服务器模块: {str(e)}")
        except Exception as e:
            raise AgentExecutionError(f"启动服务器失败: {str(e)}")
        finally:
            # 清理Python路径
            if self.prototype_path in sys.path:
                sys.path.remove(self.prototype_path)
    
    def stop_server(self):
        """停止服务器"""
        if self._server_instance:
            try:
                self._server_instance.stop()
                logger.info("PrototypeDesign服务器已停止")
            except Exception as e:
                logger.error("停止服务器失败", error=str(e))
            finally:
                self._server_instance = None
                self._server_thread = None
                self._server_port = None
    
    def get_server_status(self) -> Dict[str, Any]:
        """
        获取服务器状态
        
        Returns:
            服务器状态信息
        """
        if self._server_instance and self._server_instance.is_running:
            return {
                "running": True,
                "port": self._server_instance.port,
                "url": f"http://localhost:{self._server_instance.port}",
                "output_dir": self.output_dir
            }
        else:
            return {
                "running": False,
                "port": None,
                "url": None,
                "output_dir": self.output_dir
            }
    
    def list_prototype_files(self) -> list:
        """
        列出所有原型文件
        
        Returns:
            原型文件列表
        """
        if not os.path.exists(self.output_dir):
            return []
        
        files = []
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(self.output_dir, filename)
                stat = os.stat(filepath)
                files.append({
                    "filename": filename,
                    "path": filepath,
                    "created_time": stat.st_ctime,
                    "modified_time": stat.st_mtime,
                    "size": stat.st_size
                })
        
        # 按修改时间排序
        files.sort(key=lambda x: x["modified_time"], reverse=True)
        return files
    
    def get_prototype_file_path(self, filename: str) -> Optional[str]:
        """
        获取原型文件的完整路径
        
        Args:
            filename: 文件名
            
        Returns:
            文件完整路径，如果文件不存在返回None
        """
        filepath = os.path.join(self.output_dir, filename)
        
        # 安全检查：确保文件在输出目录内
        if not os.path.abspath(filepath).startswith(os.path.abspath(self.output_dir)):
            return None
        
        if os.path.exists(filepath):
            return filepath
        else:
            return None
    
    async def ensure_server_running(self, port: int = 8000) -> str:
        """
        确保服务器正在运行
        
        Args:
            port: 端口号
            
        Returns:
            服务器访问地址
        """
        status = self.get_server_status()
        if status["running"]:
            return status["url"]
        else:
            return await self.start_server(port)
    
    def cleanup(self):
        """清理资源"""
        self.stop_server()


# 全局服务实例
_prototype_server_service: Optional[PrototypeServerService] = None


def get_prototype_server_service() -> PrototypeServerService:
    """
    获取全局PrototypeServerService实例
    
    Returns:
        PrototypeServerService实例
    """
    global _prototype_server_service
    
    if _prototype_server_service is None:
        _prototype_server_service = PrototypeServerService()
    
    return _prototype_server_service


async def start_prototype_server(port: int = 8000) -> str:
    """
    快速启动prototype服务器
    
    Args:
        port: 端口号
        
    Returns:
        服务器访问地址
    """
    service = get_prototype_server_service()
    return await service.start_server(port)


def stop_prototype_server():
    """停止prototype服务器"""
    service = get_prototype_server_service()
    service.stop_server()


def get_prototype_server_status() -> Dict[str, Any]:
    """获取prototype服务器状态"""
    service = get_prototype_server_service()
    return service.get_server_status()
