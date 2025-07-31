#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的PrototypeDesign API测试服务器

避免复杂的中间件配置问题，专注于验证API功能
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '.')

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

# 导入我们的模块
from app.models.requests import PrototypeDesignRequest
from app.models.responses import PrototypeDesignResponse, PrototypeDesignStreamEvent
from app.api.v1.prototype_design import health_check

# 创建简化的FastAPI应用
app = FastAPI(
    title="PrototypeDesign API Test Server",
    description="简化的PrototypeDesign API测试服务器",
    version="1.0.0"
)

@app.get("/health")
async def main_health():
    """主健康检查"""
    return {"status": "healthy", "service": "prototype-design-test-server"}

@app.get("/api/v1/prototype_design/health")
async def prototype_health():
    """PrototypeDesign健康检查"""
    try:
        result = await health_check()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/prototype_design/design")
async def design_sync(request: PrototypeDesignRequest):
    """同步设计接口"""
    try:
        # 模拟同步设计响应
        response = PrototypeDesignResponse(
            status="success",
            success=True,
            prototype_url=f"http://localhost:8001/prototype_test_{hash(request.requirements) % 1000}.html",
            iteration_count=1,
            is_approved=True,
            validation_feedback="测试模式：设计已完成",
            html_code="<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello World</h1></body></html>",
            css_code="body { font-family: Arial, sans-serif; }",
            js_code="console.log('Test prototype loaded');",
            error=None,
            execution_time=5.0
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/prototype_design/design/stream")
async def design_stream(request: PrototypeDesignRequest):
    """流式设计接口"""
    
    async def event_generator():
        try:
            # 模拟流式事件
            events = [
                {
                    "type": "start",
                    "message": "开始原型设计",
                    "requirements": request.requirements,
                    "thread_id": f"test-{hash(request.requirements) % 1000}"
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
                    "message": "Validator验证结果: APPROVED",
                    "validation_result": "APPROVED",
                    "feedback": "测试模式：设计符合要求",
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
                        "prototype_url": f"http://localhost:8001/prototype_stream_{hash(request.requirements) % 1000}.html",
                        "iteration_count": 1,
                        "is_approved": True,
                        "validation_feedback": "测试模式：设计已完成",
                        "html_code": "<!DOCTYPE html><html><head><title>Stream Test</title></head><body><h1>Stream Design</h1></body></html>",
                        "css_code": "body { background-color: #f0f0f0; }",
                        "js_code": "console.log('Stream prototype loaded');",
                        "execution_time": 8.5
                    }
                }
            ]
            
            for i, event in enumerate(events):
                # 转换为标准事件格式
                stream_event = PrototypeDesignStreamEvent(
                    type=event.get("type", "unknown"),
                    message=event.get("message", ""),
                    step=event.get("step"),
                    validation_result=event.get("validation_result"),
                    feedback=event.get("feedback"),
                    data=event.get("data"),
                    result=event.get("result"),
                    error=event.get("error")
                )
                
                # 发送事件
                yield f"data: {stream_event.json()}\n\n"
                
                # 模拟处理时间
                if i < len(events) - 1:
                    await asyncio.sleep(1.5)
            
        except Exception as e:
            # 发送错误事件
            error_event = PrototypeDesignStreamEvent(
                type="error",
                message=f"流式设计失败: {str(e)}",
                error=str(e)
            )
            yield f"data: {error_event.json()}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@app.get("/api/v1/prototype_design/prototypes")
async def list_prototypes():
    """获取原型列表"""
    return {
        "prototypes": [
            {
                "filename": "prototype_test_123.html",
                "created_time": 1705312200.0,
                "modified_time": 1705312200.0,
                "size": 1024,
                "url": "/api/v1/prototype_design/prototypes/prototype_test_123.html"
            },
            {
                "filename": "prototype_stream_456.html",
                "created_time": 1705312300.0,
                "modified_time": 1705312300.0,
                "size": 1536,
                "url": "/api/v1/prototype_design/prototypes/prototype_stream_456.html"
            }
        ]
    }

@app.get("/api/v1/prototype_design/prototypes/{filename}")
async def get_prototype_file(filename: str):
    """访问原型文件"""
    # 模拟HTML文件内容
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试原型 - {filename}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 PrototypeDesign 测试原型</h1>
        <div class="info">
            <p><strong>文件名:</strong> {filename}</p>
            <p><strong>生成时间:</strong> {{"2025-07-31 14:45:00"}}</p>
            <p><strong>状态:</strong> 测试模式</p>
        </div>
        <p>这是一个由PrototypeDesign API生成的测试原型文件。</p>
        <p>在实际使用中，这里会包含根据用户需求生成的完整HTML/CSS/JavaScript代码。</p>
    </div>
    <script>
        console.log('PrototypeDesign测试原型已加载: {filename}');
    </script>
</body>
</html>"""
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content, media_type="text/html")

@app.post("/api/v1/prototype_design/server/start")
async def start_server(port: int = 8001):
    """启动原型服务器"""
    return {
        "success": True,
        "message": "测试模式：服务器启动成功",
        "url": f"http://localhost:{port}",
        "port": port
    }

@app.get("/api/v1/prototype_design/server/status")
async def get_server_status():
    """获取服务器状态"""
    return {
        "success": True,
        "status": {
            "running": True,
            "port": 8001,
            "url": "http://localhost:8001",
            "output_dir": "/tmp/prototype_test"
        }
    }

def main():
    """启动测试服务器"""
    print("🚀 启动PrototypeDesign API测试服务器")
    print("=" * 50)
    print("服务地址: http://localhost:8003")
    print("API文档: http://localhost:8003/docs")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "simple_test_server:app",
            host="0.0.0.0",
            port=8003,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

if __name__ == "__main__":
    main()
