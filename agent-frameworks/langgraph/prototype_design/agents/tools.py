"""
工具函数模块
包含原型设计和验证过程中需要的各种工具函数
"""

import os
import uuid
import http.server
import socketserver
import threading
import time
from pathlib import Path
from typing import Dict, Any
from langsmith import traceable


@traceable(run_type="tool", name="File Writer")
def write_prototype_file(html_code: str, css_code: str, js_code: str, output_dir: str) -> str:
    """
    将生成的代码写入HTML文件
    
    Args:
        html_code: HTML代码
        css_code: CSS代码  
        js_code: JavaScript代码
        output_dir: 输出目录
        
    Returns:
        生成的文件路径
    """
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 生成唯一的文件名
    file_id = str(uuid.uuid4())[:8]
    filename = f"prototype_{file_id}.html"
    filepath = os.path.join(output_dir, filename)
    
    # 组合完整的HTML内容
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>高保真原型</title>
    <style>
{css_code}
    </style>
</head>
<body>
{html_code}
    <script>
{js_code}
    </script>
</body>
</html>"""
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    return filepath


@traceable(run_type="tool", name="Server Starter")
def start_local_server(output_dir: str, port: int = 8000) -> str:
    """
    启动本地HTTP服务器
    
    Args:
        output_dir: 服务器根目录
        port: 端口号
        
    Returns:
        服务器访问地址
    """
    def run_server():
        os.chdir(output_dir)
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"服务器启动在端口 {port}")
            httpd.serve_forever()
    
    # 在后台线程启动服务器
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(1)
    
    return f"http://localhost:{port}"


@traceable(run_type="tool", name="Code Validator")
def validate_code_syntax(html_code: str, css_code: str, js_code: str) -> Dict[str, Any]:
    """
    验证代码语法
    
    Args:
        html_code: HTML代码
        css_code: CSS代码
        js_code: JavaScript代码
        
    Returns:
        验证结果字典
    """
    errors = []
    warnings = []
    
    # 基本的HTML验证
    if not html_code.strip():
        errors.append("HTML代码为空")
    elif '<html>' not in html_code and '<div>' not in html_code and '<section>' not in html_code:
        warnings.append("HTML代码可能缺少基本结构")
    
    # 基本的CSS验证
    if css_code.strip():
        if '{' not in css_code or '}' not in css_code:
            warnings.append("CSS代码可能缺少基本语法结构")
    
    # 基本的JavaScript验证
    if js_code.strip():
        if 'function' not in js_code and '=>' not in js_code and 'addEventListener' not in js_code:
            warnings.append("JavaScript代码可能缺少交互功能")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


@traceable(run_type="tool", name="Requirements Parser")
def parse_requirements(requirements: str) -> Dict[str, Any]:
    """
    解析用户需求
    
    Args:
        requirements: 用户需求文本
        
    Returns:
        解析后的需求结构
    """
    parsed = {
        "type": "unknown",
        "features": [],
        "style": "modern",
        "responsive": True,
        "interactive": False
    }
    
    requirements_lower = requirements.lower()
    
    # 识别原型类型
    if any(word in requirements_lower for word in ["登录", "注册", "表单"]):
        parsed["type"] = "form"
    elif any(word in requirements_lower for word in ["仪表板", "dashboard", "数据"]):
        parsed["type"] = "dashboard"
    elif any(word in requirements_lower for word in ["商城", "购物", "电商"]):
        parsed["type"] = "ecommerce"
    elif any(word in requirements_lower for word in ["博客", "文章", "内容"]):
        parsed["type"] = "blog"
    elif any(word in requirements_lower for word in ["导航", "菜单", "页面"]):
        parsed["type"] = "navigation"
    
    # 识别交互需求
    if any(word in requirements_lower for word in ["点击", "交互", "动画", "效果"]):
        parsed["interactive"] = True
    
    # 识别样式偏好
    if any(word in requirements_lower for word in ["简约", "极简", "minimalist"]):
        parsed["style"] = "minimal"
    elif any(word in requirements_lower for word in ["商务", "专业", "business"]):
        parsed["style"] = "business"
    elif any(word in requirements_lower for word in ["创意", "艺术", "creative"]):
        parsed["style"] = "creative"
    
    return parsed
