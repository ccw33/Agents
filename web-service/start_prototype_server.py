#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原型文件服务器启动脚本

为PrototypeDesign生成的HTML文件提供HTTP访问服务
"""

import os
import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path

def main():
    """启动原型文件服务器"""
    
    # 原型文件输出目录
    outputs_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "agent-frameworks", "langgraph", "prototype_design", "outputs"
    )
    outputs_dir = os.path.abspath(outputs_dir)
    
    print("🎨 PrototypeDesign 原型文件服务器")
    print("=" * 50)
    print(f"📁 原型文件目录: {outputs_dir}")
    
    # 检查目录是否存在
    if not os.path.exists(outputs_dir):
        print(f"❌ 原型文件目录不存在: {outputs_dir}")
        return
    
    # 列出可用的HTML文件
    html_files = []
    for f in os.listdir(outputs_dir):
        if f.endswith('.html'):
            html_files.append(f)
            file_path = os.path.join(outputs_dir, f)
            file_size = os.path.getsize(file_path)
            print(f"  📄 {f} ({file_size} bytes)")
    
    if not html_files:
        print("⚠️  没有找到HTML原型文件")
        print("💡 请先使用PrototypeDesign API生成原型")
        return
    
    print(f"\n✅ 找到 {len(html_files)} 个原型文件")
    
    # 切换到输出目录
    os.chdir(outputs_dir)
    
    # 选择端口
    port = 8001
    
    # 自定义HTTP处理器，添加CORS支持
    class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def log_message(self, format, *args):
            # 自定义日志格式
            print(f"🌐 [{self.address_string()}] {format % args}")
    
    try:
        # 启动HTTP服务器
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print(f"\n🚀 原型文件服务器已启动")
            print(f"🔗 服务器地址: http://localhost:{port}")
            print("=" * 50)
            
            print("🌐 可访问的原型地址:")
            for filename in html_files:
                print(f"  http://localhost:{port}/{filename}")
            
            print("\n💡 使用说明:")
            print("- 在浏览器中打开上述地址查看原型")
            print("- 按 Ctrl+C 停止服务器")
            print("- 服务器支持CORS，可在其他域名下访问")
            
            print("\n⏳ 服务器运行中...")
            print("=" * 50)
            
            # 自动打开第一个原型文件
            if html_files:
                first_prototype = f"http://localhost:{port}/{html_files[0]}"
                print(f"🌐 自动打开第一个原型: {first_prototype}")
                try:
                    webbrowser.open(first_prototype)
                except:
                    pass
            
            # 启动服务器
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {port} 已被占用")
            print("💡 请检查是否有其他服务器在运行，或使用其他端口")
        else:
            print(f"❌ 启动服务器失败: {e}")
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")

if __name__ == "__main__":
    main()
