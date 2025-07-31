# PrototypeDesign专用API接口
"""
PrototypeDesign Agent的专用API接口

提供流式响应和文件访问功能
"""

import json
import uuid
import asyncio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import structlog
import os
from typing import Dict, Any

from app.models.requests import PrototypeDesignRequest
from app.models.responses import PrototypeDesignResponse, PrototypeDesignStreamEvent
from app.services.agent_service import AgentServiceFactory
from app.services.prototype_server_service import get_prototype_server_service
from app.core.exceptions import AgentException
from app.core.config import get_agent_framework_path

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/design",
    response_model=PrototypeDesignResponse,
    summary="原型设计（同步）",
    description="同步执行原型设计，等待完成后返回结果"
)
async def design_prototype_sync(request: PrototypeDesignRequest):
    """
    同步原型设计接口
    
    - **requirements**: 原型设计需求描述
    - **config**: 设计配置（可选）
    """
    try:
        logger.info("开始同步原型设计", requirements=request.requirements[:100])
        
        # 获取LangGraph服务
        service = AgentServiceFactory.get_service("langgraph")
        
        # 准备输入数据
        input_data = {
            "requirements": request.requirements
        }
        
        # 执行原型设计
        result = await service.execute_with_timeout(
            agent_type="prototype_design",
            input_data=input_data,
            config=request.config,
            timeout=600  # 10分钟超时
        )
        
        # 构建响应
        agent_result = result.get("result", {})
        response = PrototypeDesignResponse(
            status=result["status"],
            success=agent_result.get("success", False),
            prototype_url=agent_result.get("prototype_url"),
            iteration_count=agent_result.get("iteration_count", 0),
            is_approved=agent_result.get("is_approved", False),
            validation_feedback=agent_result.get("validation_feedback"),
            html_code=agent_result.get("html_code"),
            css_code=agent_result.get("css_code"),
            js_code=agent_result.get("js_code"),
            error=agent_result.get("error"),
            execution_time=result["execution_time"]
        )
        
        return response
        
    except AgentException as e:
        logger.error("原型设计异常", error=str(e))
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
    except Exception as e:
        logger.error("原型设计失败", error=str(e))
        raise HTTPException(status_code=500, detail="原型设计失败")


@router.post(
    "/design/stream",
    summary="原型设计（流式）",
    description="流式执行原型设计，实时推送进度和结果"
)
async def design_prototype_stream(request: PrototypeDesignRequest):
    """
    流式原型设计接口
    
    - **requirements**: 原型设计需求描述
    - **config**: 设计配置（可选）
    
    返回Server-Sent Events流
    """
    async def event_generator():
        try:
            logger.info("开始流式原型设计", requirements=request.requirements[:100])
            
            # 获取LangGraph服务
            service = AgentServiceFactory.get_service("langgraph")
            
            # 流式执行原型设计
            async for event in service.execute_prototype_design_stream(
                requirements=request.requirements,
                config=request.config
            ):
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
                
                # 如果是完成或错误事件，结束流
                if event.get("type") in ["complete", "error"]:
                    break
            
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


@router.get(
    "/prototypes",
    summary="获取原型列表",
    description="获取所有已生成的原型文件列表"
)
async def list_prototypes():
    """获取原型列表"""
    try:
        # 获取prototype_design输出目录
        langgraph_path = get_agent_framework_path("langgraph")
        output_dir = os.path.join(langgraph_path, "prototype_design", "outputs")
        
        if not os.path.exists(output_dir):
            return {"prototypes": []}
        
        prototypes = []
        for file in os.listdir(output_dir):
            if file.endswith('.html'):
                filepath = os.path.join(output_dir, file)
                stat = os.stat(filepath)
                prototypes.append({
                    "filename": file,
                    "created_time": stat.st_ctime,
                    "modified_time": stat.st_mtime,
                    "size": stat.st_size,
                    "url": f"/api/v1/prototype_design/prototypes/{file}"
                })
        
        # 按修改时间排序
        prototypes.sort(key=lambda x: x["modified_time"], reverse=True)
        
        return {"prototypes": prototypes}
        
    except Exception as e:
        logger.error("获取原型列表失败", error=str(e))
        raise HTTPException(status_code=500, detail="获取原型列表失败")


@router.get(
    "/prototypes/{filename}",
    summary="访问原型文件",
    description="直接访问生成的原型HTML文件"
)
async def get_prototype_file(filename: str):
    """访问原型文件"""
    try:
        # 获取prototype_design输出目录
        langgraph_path = get_agent_framework_path("langgraph")
        output_dir = os.path.join(langgraph_path, "prototype_design", "outputs")
        file_path = os.path.join(output_dir, filename)
        
        # 安全检查：确保文件在输出目录内
        if not os.path.abspath(file_path).startswith(os.path.abspath(output_dir)):
            raise HTTPException(status_code=403, detail="访问被拒绝")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 返回文件
        return FileResponse(
            file_path,
            media_type="text/html",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("访问原型文件失败", filename=filename, error=str(e))
        raise HTTPException(status_code=500, detail="访问文件失败")


@router.post(
    "/server/start",
    summary="启动原型服务器",
    description="启动prototype_design本地服务器"
)
async def start_server(port: int = 8000):
    """启动原型服务器"""
    try:
        server_service = get_prototype_server_service()
        url = await server_service.start_server(port)

        return {
            "success": True,
            "message": "服务器启动成功",
            "url": url,
            "port": port
        }

    except Exception as e:
        logger.error("启动服务器失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"启动服务器失败: {str(e)}")


@router.post(
    "/server/stop",
    summary="停止原型服务器",
    description="停止prototype_design本地服务器"
)
async def stop_server():
    """停止原型服务器"""
    try:
        server_service = get_prototype_server_service()
        server_service.stop_server()

        return {
            "success": True,
            "message": "服务器已停止"
        }

    except Exception as e:
        logger.error("停止服务器失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"停止服务器失败: {str(e)}")


@router.get(
    "/server/status",
    summary="获取服务器状态",
    description="获取prototype_design服务器运行状态"
)
async def get_server_status():
    """获取服务器状态"""
    try:
        server_service = get_prototype_server_service()
        status = server_service.get_server_status()

        return {
            "success": True,
            "status": status
        }

    except Exception as e:
        logger.error("获取服务器状态失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取服务器状态失败: {str(e)}")


@router.get(
    "/health",
    summary="健康检查",
    description="检查PrototypeDesign服务状态"
)
async def health_check():
    """健康检查"""
    try:
        # 检查prototype_design路径是否存在
        langgraph_path = get_agent_framework_path("langgraph")
        prototype_path = os.path.join(langgraph_path, "prototype_design")

        if not os.path.exists(prototype_path):
            return {
                "status": "unhealthy",
                "message": "prototype_design路径不存在",
                "path": prototype_path
            }

        # 检查关键文件是否存在
        key_files = ["graph.py", "main.py", "server.py"]
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

        # 检查服务器状态
        server_service = get_prototype_server_service()
        server_status = server_service.get_server_status()

        return {
            "status": "healthy",
            "message": "PrototypeDesign服务正常",
            "path": prototype_path,
            "server": server_status
        }

    except Exception as e:
        logger.error("健康检查失败", error=str(e))
        return {
            "status": "error",
            "message": f"健康检查失败: {str(e)}"
        }
