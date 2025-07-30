"""
高保真原型设计agent的工具函数
包含文件操作、服务器管理等功能
"""

import os
import uuid
import socket
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Tuple, Optional
import re


class PrototypeFileManager:
    """原型文件管理器"""
    
    def __init__(self, base_output_dir: str = "output"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
    def create_project_directory(self) -> Tuple[str, str]:
        """创建项目目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_id = f"prototype_{timestamp}"
        project_path = self.base_output_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        return str(project_path), project_id
    
    def save_prototype_files(self, project_path: str, prototype_code: Dict[str, str]) -> bool:
        """保存原型文件"""
        try:
            project_dir = Path(project_path)
            
            # 保存HTML文件
            if 'html' in prototype_code:
                html_file = project_dir / "index.html"
                html_file.write_text(prototype_code['html'], encoding='utf-8')
            
            # 保存CSS文件
            if 'css' in prototype_code:
                css_file = project_dir / "style.css"
                css_file.write_text(prototype_code['css'], encoding='utf-8')
            
            # 保存JavaScript文件
            if 'js' in prototype_code:
                js_file = project_dir / "script.js"
                js_file.write_text(prototype_code['js'], encoding='utf-8')
            
            return True
        except Exception as e:
            print(f"保存文件时出错: {e}")
            return False
    
    def extract_code_from_response(self, response: str) -> Dict[str, str]:
        """从LLM响应中提取代码"""
        code_dict = {}
        
        # 提取HTML代码
        html_pattern = r'```html\s*(?:<!--.*?-->\s*)?(.*?)```'
        html_match = re.search(html_pattern, response, re.DOTALL | re.IGNORECASE)
        if html_match:
            code_dict['html'] = html_match.group(1).strip()
        
        # 提取CSS代码
        css_pattern = r'```css\s*(?:/\*.*?\*/\s*)?(.*?)```'
        css_match = re.search(css_pattern, response, re.DOTALL | re.IGNORECASE)
        if css_match:
            code_dict['css'] = css_match.group(1).strip()
        
        # 提取JavaScript代码
        js_pattern = r'```javascript\s*(?://.*?\n\s*)?(.*?)```'
        js_match = re.search(js_pattern, response, re.DOTALL | re.IGNORECASE)
        if js_match:
            code_dict['js'] = js_match.group(1).strip()
        
        return code_dict


class LocalServerManager:
    """本地服务器管理器"""
    
    def __init__(self):
        self.servers = {}  # 存储运行中的服务器
    
    def find_free_port(self, start_port: int = 8080) -> int:
        """查找可用端口"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("无法找到可用端口")
    
    def start_server(self, project_path: str, port: Optional[int] = None) -> str:
        """启动本地服务器"""
        if port is None:
            port = self.find_free_port()
        
        try:
            # 切换到项目目录
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            # 创建服务器
            handler = SimpleHTTPRequestHandler
            httpd = HTTPServer(('localhost', port), handler)
            
            # 在后台线程中运行服务器
            server_thread = threading.Thread(
                target=httpd.serve_forever,
                daemon=True
            )
            server_thread.start()
            
            # 恢复原始工作目录
            os.chdir(original_cwd)
            
            # 存储服务器信息
            server_url = f"http://localhost:{port}"
            self.servers[project_path] = {
                'httpd': httpd,
                'thread': server_thread,
                'url': server_url,
                'port': port
            }
            
            return server_url
            
        except Exception as e:
            print(f"启动服务器时出错: {e}")
            return ""
    
    def stop_server(self, project_path: str) -> bool:
        """停止指定项目的服务器"""
        if project_path in self.servers:
            try:
                self.servers[project_path]['httpd'].shutdown()
                del self.servers[project_path]
                return True
            except Exception as e:
                print(f"停止服务器时出错: {e}")
                return False
        return False
    
    def stop_all_servers(self):
        """停止所有服务器"""
        for project_path in list(self.servers.keys()):
            self.stop_server(project_path)


def validate_code_syntax(code_dict: Dict[str, str]) -> Tuple[bool, str]:
    """验证代码语法"""
    errors = []
    
    # 简单的HTML验证
    if 'html' in code_dict:
        html = code_dict['html']
        if not html.strip():
            errors.append("HTML代码为空")
        elif '<html' not in html.lower() and '<!doctype' not in html.lower():
            errors.append("HTML代码缺少基本结构")
    
    # 简单的CSS验证
    if 'css' in code_dict:
        css = code_dict['css']
        if css.strip() and css.count('{') != css.count('}'):
            errors.append("CSS代码括号不匹配")
    
    # JavaScript语法检查（基础）
    if 'js' in code_dict:
        js = code_dict['js']
        if js.strip():
            # 检查基本的括号匹配
            if js.count('(') != js.count(')'):
                errors.append("JavaScript代码圆括号不匹配")
            if js.count('{') != js.count('}'):
                errors.append("JavaScript代码花括号不匹配")
    
    if errors:
        return False, "; ".join(errors)
    return True, "代码语法检查通过"
