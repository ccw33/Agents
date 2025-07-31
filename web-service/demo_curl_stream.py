#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示PrototypeDesign流式API的curl调用效果

模拟真实的Server-Sent Events流式响应
"""

import asyncio
import json
import time
import sys
import os

# 添加项目路径
sys.path.insert(0, '.')

async def simulate_stream_response():
    """模拟流式响应的输出"""
    
    print("🌊 模拟curl流式调用:")
    print("curl -X POST http://localhost:8000/api/v1/prototype_design/design/stream \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -H 'Accept: text/event-stream' \\")
    print("  -N \\")
    print("  -d '{")
    print('    "requirements": "创建一个简单的登录页面，包含用户名、密码输入框和登录按钮",')
    print('    "config": {"max_iterations": 2}')
    print("  }'")
    print()
    print("📡 Server-Sent Events 响应:")
    print("-" * 60)
    
    # 模拟流式事件
    events = [
        {
            "type": "start",
            "message": "开始原型设计",
            "requirements": "创建一个简单的登录页面，包含用户名、密码输入框和登录按钮",
            "thread_id": "demo-12345"
        },
        {
            "type": "progress",
            "step": "designer",
            "message": "Designer正在工作... (第1次迭代)",
            "data": {"iteration_count": 1}
        },
        {
            "type": "progress", 
            "step": "validator",
            "message": "Validator验证结果: REJECTED",
            "validation_result": "REJECTED",
            "feedback": "登录按钮样式需要改进，建议使用更现代的设计风格",
            "data": {"validation_result": "REJECTED"}
        },
        {
            "type": "progress",
            "step": "designer", 
            "message": "Designer正在工作... (第2次迭代)",
            "data": {"iteration_count": 2}
        },
        {
            "type": "progress",
            "step": "validator",
            "message": "Validator验证结果: APPROVED", 
            "validation_result": "APPROVED",
            "feedback": "登录页面设计符合要求，界面美观，响应式设计良好",
            "data": {"validation_result": "APPROVED"}
        },
        {
            "type": "progress",
            "step": "finalize",
            "message": "正在生成最终原型...",
            "data": {}
        },
        {
            "type": "complete",
            "message": "原型设计完成",
            "success": True,
            "result": {
                "success": True,
                "prototype_url": "http://localhost:8001/prototype_demo123.html",
                "iteration_count": 2,
                "is_approved": True,
                "validation_feedback": "登录页面设计符合要求，界面美观，响应式设计良好",
                "execution_time": 125.6
            }
        }
    ]
    
    for i, event in enumerate(events):
        # 添加时间戳
        event["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # 输出SSE格式
        event_json = json.dumps(event, ensure_ascii=False, indent=None)
        print(f"data: {event_json}")
        print()  # SSE要求每个事件后有空行
        
        # 模拟网络延迟
        if i < len(events) - 1:
            await asyncio.sleep(1.5)
    
    print("-" * 60)
    print("✅ 流式响应完成")
    print()
    print("📋 响应解析:")
    print("- 总共7个事件")
    print("- 2次迭代（第1次被拒绝，第2次通过）")
    print("- 最终生成原型: http://localhost:8001/prototype_demo123.html")
    print("- 执行时间: 125.6秒")


async def demonstrate_api_calls():
    """演示各种API调用"""
    
    print("🚀 PrototypeDesign API调用演示")
    print("=" * 60)
    
    # 1. 健康检查
    print("\n1️⃣ 健康检查:")
    print("curl -X GET http://localhost:8000/api/v1/prototype_design/health")
    print()
    print("响应:")
    health_response = {
        "status": "healthy",
        "message": "PrototypeDesign服务正常",
        "path": "/Users/chenchaowen/Desktop/Project/Agents/agent-frameworks/langgraph/prototype_design",
        "server": {
            "running": False,
            "port": None,
            "url": None,
            "output_dir": "/Users/chenchaowen/Desktop/Project/Agents/agent-frameworks/langgraph/prototype_design/outputs"
        }
    }
    print(json.dumps(health_response, ensure_ascii=False, indent=2))
    
    # 2. 同步设计
    print("\n2️⃣ 同步设计:")
    print("curl -X POST http://localhost:8000/api/v1/prototype_design/design \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "requirements": "创建一个产品卡片",')
    print('    "config": {"max_iterations": 3}')
    print("  }'")
    print()
    print("响应:")
    sync_response = {
        "status": "success",
        "success": True,
        "prototype_url": "http://localhost:8001/prototype_abc123.html",
        "iteration_count": 1,
        "is_approved": True,
        "validation_feedback": "产品卡片设计美观，布局合理",
        "execution_time": 89.2,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    print(json.dumps(sync_response, ensure_ascii=False, indent=2))
    
    # 3. 流式设计
    print("\n3️⃣ 流式设计:")
    await simulate_stream_response()
    
    # 4. 获取原型列表
    print("\n4️⃣ 获取原型列表:")
    print("curl -X GET http://localhost:8000/api/v1/prototype_design/prototypes")
    print()
    print("响应:")
    list_response = {
        "prototypes": [
            {
                "filename": "prototype_demo123.html",
                "created_time": 1705312200.0,
                "modified_time": 1705312200.0,
                "size": 15420,
                "url": "/api/v1/prototype_design/prototypes/prototype_demo123.html"
            },
            {
                "filename": "prototype_abc123.html", 
                "created_time": 1705312100.0,
                "modified_time": 1705312100.0,
                "size": 12350,
                "url": "/api/v1/prototype_design/prototypes/prototype_abc123.html"
            }
        ]
    }
    print(json.dumps(list_response, ensure_ascii=False, indent=2))
    
    # 5. 服务器管理
    print("\n5️⃣ 启动原型服务器:")
    print("curl -X POST 'http://localhost:8000/api/v1/prototype_design/server/start?port=8001'")
    print()
    print("响应:")
    server_response = {
        "success": True,
        "message": "服务器启动成功",
        "url": "http://localhost:8001",
        "port": 8001
    }
    print(json.dumps(server_response, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("🎯 演示完成！")
    print()
    print("💡 实际使用步骤:")
    print("1. 启动Web服务: python start_with_prototype_design.py")
    print("2. 使用上述curl命令调用API")
    print("3. 流式接口会实时显示设计过程")
    print("4. 访问生成的原型文件查看结果")


async def main():
    """主函数"""
    try:
        await demonstrate_api_calls()
    except KeyboardInterrupt:
        print("\n👋 演示结束")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
