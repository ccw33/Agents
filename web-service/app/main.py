# FastAPI应用主入口
"""
AI Agent Web Service 主应用

提供统一的API接口来调用不同框架的AI Agent
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from app.api.v1 import agents, langgraph, autogen, crewai
from app.core.config import settings
from app.core.exceptions import AgentException

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# 创建FastAPI应用
app = FastAPI(
    title="AI Agent Web Service",
    description="统一的AI Agent服务接口，支持LangGraph、AutoGen、CrewAI框架",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理器
@app.exception_handler(AgentException)
async def agent_exception_handler(request: Request, exc: AgentException):
    logger.error("Agent执行异常", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("未处理的异常", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "内部服务器错误", "detail": "请联系管理员"}
    )

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-agent-web-service"}

# 注册API路由
app.include_router(agents.router, prefix="/api/v1", tags=["统一Agent接口"])
app.include_router(langgraph.router, prefix="/api/v1/langgraph", tags=["LangGraph"])
app.include_router(autogen.router, prefix="/api/v1/autogen", tags=["AutoGen"])
app.include_router(crewai.router, prefix="/api/v1/crewai", tags=["CrewAI"])

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("AI Agent Web Service 启动", version="1.0.0")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AI Agent Web Service 关闭")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
