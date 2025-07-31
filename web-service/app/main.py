# FastAPI应用主入口
"""
AI Agent Web Service 主应用

提供统一的API接口来调用不同框架的AI Agent
支持PrototypeDesign Agent的完整流式响应和原型文件生成
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import structlog
import uvicorn
import asyncio
import json
import sys
import os
import threading
import http.server
import socketserver
from pathlib import Path
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 添加PrototypeDesign Agent路径
prototype_design_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "agent-frameworks", "langgraph", "prototype_design"
)
sys.path.insert(0, os.path.abspath(prototype_design_path))

# 直接导入需要的模块，避免复杂的依赖
from app.models.requests import PrototypeDesignRequest
from app.models.responses import PrototypeDesignResponse, PrototypeDesignStreamEvent

# 导入PrototypeDesign Agent
try:
    from graph import PrototypeDesignWorkflow
    from server import quick_start_server, get_server
    print("✅ PrototypeDesign Agent模块导入成功")
except ImportError as e:
    print(f"⚠️  PrototypeDesign Agent模块导入失败: {e}")
    PrototypeDesignWorkflow = None

# 配置日志
logger = structlog.get_logger()

# 全局变量
prototype_output_dir = None

def get_prototype_output_dir():
    """获取原型输出目录"""
    global prototype_output_dir
    if not prototype_output_dir:
        # 使用正确的prototype_design输出目录
        web_service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prototype_output_dir = os.path.join(web_service_dir, "..", "agent-frameworks", "langgraph", "prototype_design", "outputs")
        prototype_output_dir = os.path.abspath(prototype_output_dir)
        # 确保目录存在
        Path(prototype_output_dir).mkdir(parents=True, exist_ok=True)
    return prototype_output_dir

def generate_prototype_file(html_code: str, css_code: str, js_code: str, filename: str) -> str:
    """生成原型文件"""
    global prototype_output_dir

    if not prototype_output_dir:
        # 使用正确的prototype_design输出目录
        web_service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prototype_output_dir = os.path.join(web_service_dir, "..", "agent-frameworks", "langgraph", "prototype_design", "outputs")
        prototype_output_dir = os.path.abspath(prototype_output_dir)

    # 确保输出目录存在
    Path(prototype_output_dir).mkdir(parents=True, exist_ok=True)

    # 生成完整的HTML文件
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrototypeDesign - {filename}</title>
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
    file_path = os.path.join(prototype_output_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"📁 [文件生成] 原型文件已生成: {file_path}")
    return file_path

def get_web_service_port():
    """获取当前web service的端口"""
    # 默认端口8000，可以从环境变量或配置中获取
    return int(os.environ.get("WEB_SERVICE_PORT", "8000"))

# 创建FastAPI应用 - 最简配置
app = FastAPI(
    title="AI Agent Web Service",
    description="AI Agent统一Web服务，支持PrototypeDesign等多种Agent",
    version="1.0.0"
)

# 简单的CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加静态文件服务 - 用于提供原型文件访问
from fastapi.staticfiles import StaticFiles

# 挂载原型文件静态目录
@app.on_event("startup")
async def mount_static_files():
    """启动时挂载静态文件目录"""
    output_dir = get_prototype_output_dir()
    print(f"📁 [静态文件] 挂载原型文件目录: {output_dir}")
    app.mount("/prototypes", StaticFiles(directory=output_dir), name="prototypes")

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "prototype-design-api"}

@app.get("/api/v1/prototype_design/health")
async def prototype_health():
    """PrototypeDesign健康检查"""
    try:
        # 检查prototype_design路径
        from app.core.config import get_agent_framework_path
        
        langgraph_path = get_agent_framework_path("langgraph")
        prototype_path = os.path.join(langgraph_path, "prototype_design")
        
        if not os.path.exists(prototype_path):
            return {
                "status": "unhealthy",
                "message": "prototype_design路径不存在",
                "path": prototype_path
            }
        
        # 检查关键文件
        key_files = ["graph.py", "main.py", "server.py", "state.py"]
        missing_files = []
        for file in key_files:
            if not os.path.exists(os.path.join(prototype_path, file)):
                missing_files.append(file)
        
        if missing_files:
            return {
                "status": "unhealthy",
                "message": f"缺少关键文件: {', '.join(missing_files)}",
                "path": prototype_path
            }
        
        return {
            "status": "healthy",
            "message": "PrototypeDesign服务正常",
            "path": prototype_path,
            "server": {
                "running": False,
                "port": None,
                "url": None,
                "output_dir": os.path.join(prototype_path, "outputs")
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"健康检查失败: {str(e)}"
        }

@app.post("/api/v1/prototype_design/design")
async def design_sync(request: PrototypeDesignRequest):
    """同步设计接口"""
    try:
        # 模拟同步设计
        await asyncio.sleep(2)  # 模拟处理时间
        
        response = PrototypeDesignResponse(
            status="success",
            success=True,
            prototype_url=f"http://localhost:8001/prototype_sync_{hash(request.requirements) % 10000}.html",
            iteration_count=1,
            is_approved=True,
            validation_feedback="同步设计完成",
            html_code="<!DOCTYPE html><html><head><title>Sync Design</title></head><body><h1>同步设计结果</h1></body></html>",
            css_code="body { font-family: Arial, sans-serif; margin: 20px; }",
            js_code="console.log('同步设计加载完成');",
            error=None,
            execution_time=2.0
        )
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/prototype_design/design/stream")
async def design_stream(request: PrototypeDesignRequest):
    """流式设计接口 - 调用真实的PrototypeDesign Agent"""

    print(f"🌊 [服务器] 接收到流式设计请求")
    print(f"📝 [服务器] 需求: {request.requirements}")
    print(f"⚙️  [服务器] 配置: {request.config}")

    async def event_generator():
        try:
            print(f"🚀 [服务器] 开始调用PrototypeDesign Agent")

            # 检查Agent是否可用
            if PrototypeDesignWorkflow is None:
                error_event = PrototypeDesignStreamEvent(
                    type="error",
                    message="PrototypeDesign Agent不可用，请检查环境配置",
                    error="Agent模块导入失败"
                )
                yield f"data: {error_event.model_dump_json()}\n\n"
                return

            # 生成线程ID
            import uuid
            thread_id = f"stream-{uuid.uuid4().hex[:8]}"

            # 发送开始事件
            start_event = PrototypeDesignStreamEvent(
                type="start",
                message="开始原型设计",
                data={
                    "requirements": request.requirements,
                    "thread_id": thread_id,
                    "max_iterations": request.config.get("max_iterations", 5) if request.config else 5
                }
            )
            yield f"data: {start_event.model_dump_json()}\n\n"

            # 创建工作流实例
            workflow = PrototypeDesignWorkflow()

            # 流式运行工作流
            iteration_count = 0

            for event in workflow.stream_run(request.requirements, thread_id=thread_id):
                for node_name, node_data in event.items():
                    print(f"📡 [服务器] 接收到Agent事件: {node_name}")

                    if node_name == "designer":
                        iteration_count = node_data.get('iteration_count', iteration_count + 1)
                        progress_event = PrototypeDesignStreamEvent(
                            type="progress",
                            step="designer",
                            message=f"Designer正在工作... (第{iteration_count}次迭代)",
                            data={"iteration_count": iteration_count}
                        )
                        yield f"data: {progress_event.model_dump_json()}\n\n"

                    elif node_name == "validator":
                        validation_result = node_data.get('validation_result', 'UNKNOWN')
                        feedback = node_data.get('validation_feedback', '')

                        progress_event = PrototypeDesignStreamEvent(
                            type="progress",
                            step="validator",
                            message=f"Validator验证结果: {validation_result}",
                            validation_result=validation_result,
                            feedback=feedback,
                            data={"validation_result": validation_result}
                        )
                        yield f"data: {progress_event.model_dump_json()}\n\n"

                    elif node_name == "finalize":
                        finalize_event = PrototypeDesignStreamEvent(
                            type="progress",
                            step="finalize",
                            message="正在生成最终原型...",
                            data={}
                        )
                        yield f"data: {finalize_event.model_dump_json()}\n\n"

            # 获取最终结果
            print(f"🔧 [服务器] 获取Agent执行结果")
            final_result = workflow.run(request.requirements, thread_id=thread_id)

            if final_result.get("success"):
                print(f"✅ [服务器] Agent执行成功")

                # 构建web-service的原型访问URL
                web_service_port = get_web_service_port()
                prototype_url = final_result.get("prototype_url")

                if prototype_url:
                    # 从Agent返回的URL中提取文件名
                    import re
                    filename_match = re.search(r'prototype_[a-f0-9]+\.html', prototype_url)
                    if filename_match:
                        filename = filename_match.group()
                        # 构建web-service的静态文件URL
                        web_service_url = f"http://localhost:{web_service_port}/prototypes/{filename}"
                        print(f"🌐 [服务器] 原型访问地址: {web_service_url}")
                    else:
                        web_service_url = prototype_url
                else:
                    web_service_url = None

                complete_event = PrototypeDesignStreamEvent(
                    type="complete",
                    message="原型设计完成",
                    result={
                        "success": True,
                        "prototype_url": web_service_url,
                        "iteration_count": final_result.get("iteration_count", iteration_count),
                        "is_approved": final_result.get("is_approved", True),
                        "validation_feedback": final_result.get("validation_feedback", "设计完成"),
                        "html_code": final_result.get("html_code", ""),
                        "css_code": final_result.get("css_code", ""),
                        "js_code": final_result.get("js_code", ""),
                        "execution_time": 0  # Agent内部计算
                    }
                )
                yield f"data: {complete_event.model_dump_json()}\n\n"

            else:
                print(f"❌ [服务器] Agent执行失败: {final_result.get('error')}")
                error_event = PrototypeDesignStreamEvent(
                    type="error",
                    message=f"原型设计失败: {final_result.get('error', '未知错误')}",
                    error=final_result.get('error')
                )
                yield f"data: {error_event.model_dump_json()}\n\n"

            print(f"✅ [服务器] 流式事件发送完成")

        except Exception as e:
            print(f"❌ [服务器] 流式生成异常: {e}")
            # 发送错误事件
            error_event = PrototypeDesignStreamEvent(
                type="error",
                message=f"流式设计失败: {str(e)}",
                error=str(e)
            )
            yield f"data: {error_event.model_dump_json()}\n\n"
    
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
    try:
        output_dir = get_prototype_output_dir()
        web_service_port = get_web_service_port()

        prototypes = []

        if os.path.exists(output_dir):
            for filename in os.listdir(output_dir):
                if filename.endswith('.html'):
                    file_path = os.path.join(output_dir, filename)
                    file_stat = os.stat(file_path)

                    prototypes.append({
                        "filename": filename,
                        "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(file_stat.st_ctime)),
                        "modified_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(file_stat.st_mtime)),
                        "size": file_stat.st_size,
                        "url": f"http://localhost:{web_service_port}/prototypes/{filename}"
                    })

        # 按创建时间倒序排列
        prototypes.sort(key=lambda x: x['created_at'], reverse=True)

        return {
            "success": True,
            "prototypes": prototypes,
            "total": len(prototypes),
            "output_dir": output_dir
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prototypes": [],
            "total": 0
        }

# 原型文件通过静态文件服务 /prototypes/{filename} 直接访问

@app.get("/api/v1/prototype_design/server/status")
async def get_server_status():
    """获取服务器状态"""
    web_service_port = get_web_service_port()
    output_dir = get_prototype_output_dir()

    return {
        "success": True,
        "status": {
            "running": True,
            "service": "web-service",
            "port": web_service_port,
            "prototype_url_base": f"http://localhost:{web_service_port}/prototypes/",
            "output_dir": output_dir,
            "static_mount": "/prototypes"
        }
    }

if __name__ == "__main__":
    print("🚀 启动PrototypeDesign API服务 (干净版本)")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8003")
    print("API文档: http://0.0.0.0:8003/docs")
    print("=" * 50)
    
    uvicorn.run(
        "app.main_clean:app",
        host="0.0.0.0",
        port=8003,
        log_level="info",
        reload=False
    )
