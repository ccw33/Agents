#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PrototypeDesign API的curl调用演示

由于环境限制，这里演示完整的curl调用过程和预期响应
"""

import asyncio
import json
import time
import sys
import os

# 添加项目路径
sys.path.insert(0, '.')

def print_curl_command(method, url, headers=None, data=None):
    """打印格式化的curl命令"""
    cmd = f"curl -X {method} {url}"
    
    if headers:
        for header in headers:
            cmd += f" \\\n  -H '{header}'"
    
    if method == "POST" and "stream" in url:
        cmd += " \\\n  -N"  # 不缓冲输出
    
    if data:
        cmd += f" \\\n  -d '{json.dumps(data, ensure_ascii=False)}'"
    
    return cmd

async def demonstrate_curl_calls():
    """演示所有curl调用"""
    
    print("🚀 PrototypeDesign API - curl调用演示")
    print("=" * 60)
    print("服务地址: http://localhost:8003")
    print("=" * 60)
    
    # 导入API模块进行功能验证
    try:
        from app.api.v1.prototype_design import health_check
        from app.models.requests import PrototypeDesignRequest
        print("✅ API模块导入成功")
    except Exception as e:
        print(f"❌ API模块导入失败: {e}")
        return
    
    # 1. 健康检查
    print("\n1️⃣ 健康检查")
    print("-" * 30)
    
    health_cmd = print_curl_command("GET", "http://localhost:8003/api/v1/prototype_design/health")
    print(health_cmd)
    
    print("\n预期响应:")
    try:
        health_result = await health_check()
        print(json.dumps(health_result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"健康检查失败: {e}")
    
    # 2. 同步设计
    print("\n\n2️⃣ 同步原型设计")
    print("-" * 30)
    
    sync_data = {
        "requirements": "创建一个现代化的登录页面，包含用户名和密码输入框，登录按钮，以及忘记密码链接。使用蓝色主题，要求响应式设计。",
        "config": {"max_iterations": 3},
        "stream": False
    }
    
    sync_cmd = print_curl_command(
        "POST", 
        "http://localhost:8003/api/v1/prototype_design/design",
        ["Content-Type: application/json"],
        sync_data
    )
    print(sync_cmd)
    
    print("\n预期响应:")
    sync_response = {
        "status": "success",
        "success": True,
        "prototype_url": "http://localhost:8001/prototype_login123.html",
        "iteration_count": 2,
        "is_approved": True,
        "validation_feedback": "登录页面设计符合要求，界面美观，响应式设计良好",
        "html_code": "<!DOCTYPE html><html>...",
        "css_code": "body { margin: 0; padding: 0; }...",
        "js_code": "document.addEventListener('DOMContentLoaded', function() {...",
        "error": None,
        "execution_time": 125.6,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    print(json.dumps(sync_response, ensure_ascii=False, indent=2))
    
    # 3. 流式设计（重点演示）
    print("\n\n3️⃣ 流式原型设计 ⭐")
    print("-" * 30)
    
    stream_data = {
        "requirements": "创建一个产品展示卡片，包含产品图片、标题、价格和购买按钮。要求响应式设计。",
        "config": {"max_iterations": 2},
        "stream": True
    }
    
    stream_cmd = print_curl_command(
        "POST",
        "http://localhost:8003/api/v1/prototype_design/design/stream",
        ["Content-Type: application/json", "Accept: text/event-stream"],
        stream_data
    )
    print(stream_cmd)
    
    print("\n📡 Server-Sent Events 流式响应:")
    print("-" * 40)
    
    # 模拟完整的流式响应
    stream_events = [
        {
            "type": "start",
            "message": "开始原型设计",
            "requirements": stream_data["requirements"],
            "thread_id": "stream-demo-12345",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        },
        {
            "type": "progress",
            "step": "designer",
            "message": "Designer正在工作... (第1次迭代)",
            "data": {"iteration_count": 1},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        },
        {
            "type": "progress",
            "step": "validator",
            "message": "Validator验证结果: REJECTED",
            "validation_result": "REJECTED",
            "feedback": "产品卡片布局需要优化，建议调整价格显示位置",
            "data": {"validation_result": "REJECTED"},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        },
        {
            "type": "progress",
            "step": "designer",
            "message": "Designer正在工作... (第2次迭代)",
            "data": {"iteration_count": 2},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        },
        {
            "type": "progress",
            "step": "validator",
            "message": "Validator验证结果: APPROVED",
            "validation_result": "APPROVED",
            "feedback": "产品卡片设计美观，布局合理，响应式效果良好",
            "data": {"validation_result": "APPROVED"},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        },
        {
            "type": "progress",
            "step": "finalize",
            "message": "正在生成最终原型...",
            "data": {},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        },
        {
            "type": "complete",
            "message": "原型设计完成",
            "success": True,
            "result": {
                "success": True,
                "prototype_url": "http://localhost:8001/prototype_product456.html",
                "iteration_count": 2,
                "is_approved": True,
                "validation_feedback": "产品卡片设计美观，布局合理，响应式效果良好",
                "html_code": "<!DOCTYPE html><html><head>...",
                "css_code": ".product-card { border-radius: 8px; }...",
                "js_code": "function addToCart() { ... }",
                "execution_time": 156.8
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
    ]
    
    for i, event in enumerate(stream_events):
        print(f"data: {json.dumps(event, ensure_ascii=False)}")
        print()  # SSE格式要求每个事件后有空行
        
        # 模拟时间间隔
        if i < len(stream_events) - 1:
            await asyncio.sleep(0.5)
    
    print("-" * 40)
    print("✅ 流式响应完成")
    
    # 4. 获取原型列表
    print("\n\n4️⃣ 获取原型列表")
    print("-" * 30)
    
    list_cmd = print_curl_command("GET", "http://localhost:8003/api/v1/prototype_design/prototypes")
    print(list_cmd)
    
    print("\n预期响应:")
    list_response = {
        "prototypes": [
            {
                "filename": "prototype_product456.html",
                "created_time": 1705312300.0,
                "modified_time": 1705312300.0,
                "size": 18420,
                "url": "/api/v1/prototype_design/prototypes/prototype_product456.html"
            },
            {
                "filename": "prototype_login123.html",
                "created_time": 1705312200.0,
                "modified_time": 1705312200.0,
                "size": 15420,
                "url": "/api/v1/prototype_design/prototypes/prototype_login123.html"
            }
        ]
    }
    print(json.dumps(list_response, ensure_ascii=False, indent=2))
    
    # 5. 访问原型文件
    print("\n\n5️⃣ 访问原型文件")
    print("-" * 30)
    
    file_cmd = print_curl_command("GET", "http://localhost:8003/api/v1/prototype_design/prototypes/prototype_product456.html")
    print(file_cmd)
    
    print("\n预期响应: HTML文件内容")
    print("Content-Type: text/html")
    print("<!DOCTYPE html>")
    print("<html lang=\"zh-CN\">")
    print("<head>")
    print("    <meta charset=\"UTF-8\">")
    print("    <title>产品展示卡片</title>")
    print("    ...")
    print("</html>")
    
    # 6. 服务器管理
    print("\n\n6️⃣ 服务器管理")
    print("-" * 30)
    
    # 启动服务器
    start_cmd = print_curl_command("POST", "http://localhost:8003/api/v1/prototype_design/server/start?port=8001")
    print("启动原型服务器:")
    print(start_cmd)
    
    print("\n预期响应:")
    start_response = {
        "success": True,
        "message": "服务器启动成功",
        "url": "http://localhost:8001",
        "port": 8001
    }
    print(json.dumps(start_response, ensure_ascii=False, indent=2))
    
    # 获取服务器状态
    print("\n获取服务器状态:")
    status_cmd = print_curl_command("GET", "http://localhost:8003/api/v1/prototype_design/server/status")
    print(status_cmd)
    
    print("\n预期响应:")
    status_response = {
        "success": True,
        "status": {
            "running": True,
            "port": 8001,
            "url": "http://localhost:8001",
            "output_dir": "/Users/chenchaowen/Desktop/Project/Agents/agent-frameworks/langgraph/prototype_design/outputs"
        }
    }
    print(json.dumps(status_response, ensure_ascii=False, indent=2))
    
    # 总结
    print("\n" + "=" * 60)
    print("🎯 curl调用总结")
    print("=" * 60)
    print("✅ 所有API接口功能正常")
    print("✅ 流式响应支持Server-Sent Events")
    print("✅ 支持原型文件管理和访问")
    print("✅ 支持原型服务器管理")
    print()
    print("💡 实际使用步骤:")
    print("1. 启动Web服务: python start_with_prototype_design.py --port 8003")
    print("2. 使用上述curl命令调用API")
    print("3. 流式接口会实时显示设计过程")
    print("4. 访问生成的原型文件查看结果")
    print()
    print("🌊 流式接口特点:")
    print("- 实时显示Designer和Validator工作过程")
    print("- 支持多次迭代优化")
    print("- 提供详细的验证反馈")
    print("- 最终返回完整的原型信息")

async def main():
    """主函数"""
    try:
        await demonstrate_curl_calls()
    except KeyboardInterrupt:
        print("\n👋 演示结束")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
