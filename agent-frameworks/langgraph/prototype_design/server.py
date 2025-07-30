"""
本地服务器模块
提供HTTP服务器功能，用于预览生成的原型
"""

import os
import http.server
import socketserver
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional
from langsmith import traceable
try:
    from .config import get_config
except ImportError:
    from config import get_config


class PrototypeServer:
    """
    原型服务器类
    管理本地HTTP服务器的启动和停止
    """
    
    def __init__(self, output_dir: str, port: int = 8000):
        """
        初始化服务器
        
        Args:
            output_dir: 服务器根目录
            port: 端口号
        """
        self.output_dir = output_dir
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False
    
    @traceable(run_type="tool", name="Start Server")
    def start(self) -> str:
        """
        启动服务器
        
        Returns:
            服务器访问地址
        """
        if self.is_running:
            return f"http://localhost:{self.port}"
        
        # 确保输出目录存在
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # 创建服务器
        def run_server():
            os.chdir(self.output_dir)
            handler = http.server.SimpleHTTPRequestHandler
            
            # 自定义处理器，添加CORS头
            class CORSHTTPRequestHandler(handler):
                def end_headers(self):
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    super().end_headers()
                
                def log_message(self, format, *args):
                    # 减少日志输出
                    pass
            
            try:
                with socketserver.TCPServer(("", self.port), CORSHTTPRequestHandler) as httpd:
                    self.server = httpd
                    print(f"✅ 原型服务器已启动: http://localhost:{self.port}")
                    self.is_running = True
                    httpd.serve_forever()
            except OSError as e:
                if e.errno == 48:  # Address already in use
                    print(f"⚠️  端口 {self.port} 已被占用，尝试使用其他端口")
                    self.port += 1
                    return self.start()
                else:
                    raise e
        
        # 在后台线程启动服务器
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        time.sleep(1)
        
        return f"http://localhost:{self.port}"
    
    def stop(self):
        """停止服务器"""
        if self.server and self.is_running:
            self.server.shutdown()
            self.is_running = False
            print("🛑 原型服务器已停止")
    
    @traceable(run_type="tool", name="Open Browser")
    def open_browser(self, filename: Optional[str] = None):
        """
        在浏览器中打开原型
        
        Args:
            filename: 要打开的文件名，如果为None则打开根目录
        """
        if not self.is_running:
            self.start()
        
        url = f"http://localhost:{self.port}"
        if filename:
            url += f"/{filename}"
        
        try:
            webbrowser.open(url)
            print(f"🌐 已在浏览器中打开: {url}")
        except Exception as e:
            print(f"❌ 无法打开浏览器: {e}")
            print(f"请手动访问: {url}")
    
    def list_files(self) -> list:
        """
        列出输出目录中的所有HTML文件
        
        Returns:
            HTML文件列表
        """
        if not os.path.exists(self.output_dir):
            return []
        
        html_files = []
        for file in os.listdir(self.output_dir):
            if file.endswith('.html'):
                html_files.append(file)
        
        return sorted(html_files)


# 全局服务器实例
_global_server: Optional[PrototypeServer] = None


def get_server(output_dir: str = None, port: int = None) -> PrototypeServer:
    """
    获取全局服务器实例
    
    Args:
        output_dir: 输出目录
        port: 端口号
        
    Returns:
        服务器实例
    """
    global _global_server
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "outputs")

    if port is None:
        config = get_config()
        port = config.default_server_port

    if _global_server is None:
        _global_server = PrototypeServer(output_dir, port)
    
    return _global_server


@traceable(run_type="tool", name="Quick Start Server")
def quick_start_server(output_dir: str = None, port: int = None, open_browser: bool = True) -> str:
    """
    快速启动服务器
    
    Args:
        output_dir: 输出目录
        port: 端口号
        open_browser: 是否自动打开浏览器
        
    Returns:
        服务器地址
    """
    server = get_server(output_dir, port)
    url = server.start()
    
    if open_browser:
        # 列出可用的HTML文件
        files = server.list_files()
        if files:
            # 打开最新的文件
            latest_file = files[-1]
            server.open_browser(latest_file)
        else:
            server.open_browser()
    
    return url


if __name__ == "__main__":
    # 测试服务器
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    server = PrototypeServer(output_dir)
    
    try:
        url = server.start()
        print(f"服务器运行在: {url}")
        print("按 Ctrl+C 停止服务器")
        
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("服务器已停止")
