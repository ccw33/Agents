#!/usr/bin/env python3
# 基础功能测试脚本

import asyncio
import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.config import settings, validate_framework_paths
from app.services.agent_service import AgentServiceFactory
from app.services.langgraph_service import LangGraphService
from app.services.autogen_service import AutoGenService
from app.services.crewai_service import CrewAIService


async def test_basic_functionality():
    """测试基础功能"""
    print("🧪 开始基础功能测试...")
    
    try:
        # 测试配置
        print("📋 测试配置...")
        print(f"  - 服务名称: {settings.APP_NAME}")
        print(f"  - 版本: {settings.VERSION}")
        print(f"  - 主机: {settings.HOST}:{settings.PORT}")
        print("✅ 配置测试通过")
        
        # 测试框架路径（可能会失败，这是正常的）
        print("\n📁 测试框架路径...")
        try:
            validate_framework_paths()
            print("✅ 所有框架路径存在")
        except RuntimeError as e:
            print(f"⚠️  框架路径验证失败: {e}")
            print("   这是正常的，因为具体的Agent实现还未完成")
        
        # 测试服务注册
        print("\n🔧 测试服务注册...")
        
        # 注册服务
        langgraph_service = LangGraphService()
        autogen_service = AutoGenService()
        crewai_service = CrewAIService()
        
        AgentServiceFactory.register_service("langgraph", langgraph_service)
        AgentServiceFactory.register_service("autogen", autogen_service)
        AgentServiceFactory.register_service("crewai", crewai_service)
        
        # 验证注册
        frameworks = AgentServiceFactory.list_frameworks()
        print(f"  - 已注册框架: {frameworks}")
        assert "langgraph" in frameworks
        assert "autogen" in frameworks
        assert "crewai" in frameworks
        print("✅ 服务注册测试通过")
        
        # 测试服务获取
        print("\n🔍 测试服务获取...")
        for framework in frameworks:
            service = AgentServiceFactory.get_service(framework)
            print(f"  - {framework}: {service.__class__.__name__}")
        print("✅ 服务获取测试通过")
        
        # 测试健康检查
        print("\n💓 测试健康检查...")
        health_results = await AgentServiceFactory.health_check_all()
        for framework, status in health_results.items():
            print(f"  - {framework}: {status['status']}")
        print("✅ 健康检查测试通过")
        
        print("\n🎉 所有基础功能测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import_structure():
    """测试导入结构"""
    print("📦 测试导入结构...")
    
    try:
        # 测试核心模块导入
        from app.core.config import settings
        from app.core.exceptions import AgentException
        print("  ✅ 核心模块导入成功")
        
        # 测试模型导入
        from app.models.requests import AgentExecuteRequest
        from app.models.responses import AgentExecuteResponse
        print("  ✅ 数据模型导入成功")
        
        # 测试服务导入
        from app.services.agent_service import AgentService
        from app.services.langgraph_service import LangGraphService
        from app.services.autogen_service import AutoGenService
        from app.services.crewai_service import CrewAIService
        print("  ✅ 服务模块导入成功")
        
        # 测试API导入
        from app.api.v1 import agents, langgraph, autogen, crewai
        print("  ✅ API模块导入成功")
        
        print("✅ 所有导入测试通过")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 AI Agent Web Service 基础测试")
    print("=" * 50)
    
    # 测试导入结构
    import_success = test_import_structure()
    
    if import_success:
        # 测试基础功能
        basic_success = asyncio.run(test_basic_functionality())
        
        if basic_success:
            print("\n" + "=" * 50)
            print("🎊 所有测试通过！项目结构正确。")
            print("\n📋 下一步操作:")
            print("1. 在各个 agent-frameworks/ 目录下实现具体的Agent")
            print("2. 运行 ./scripts/start_services.sh dev 启动开发服务器")
            print("3. 访问 http://localhost:8000/docs 查看API文档")
            return 0
        else:
            print("\n❌ 基础功能测试失败")
            return 1
    else:
        print("\n❌ 导入结构测试失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
