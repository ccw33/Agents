#!/usr/bin/env python3
# 启动包含PrototypeDesign的Web服务
"""
启动AI Agent Web Service，包含PrototypeDesign功能

使用方法:
    python start_with_prototype_design.py
    python start_with_prototype_design.py --port 8080
    python start_with_prototype_design.py --host 0.0.0.0 --port 8080
"""

import os
import sys
import argparse
import asyncio
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.main import app
from app.core.config import settings


def check_prototype_design_availability():
    """检查prototype_design是否可用"""
    print("🔍 检查PrototypeDesign可用性...")
    
    try:
        from app.core.config import get_agent_framework_path
        
        # 检查LangGraph路径
        langgraph_path = get_agent_framework_path("langgraph")
        if not os.path.exists(langgraph_path):
            print(f"  ❌ LangGraph路径不存在: {langgraph_path}")
            return False
        
        # 检查prototype_design路径
        prototype_path = os.path.join(langgraph_path, "prototype_design")
        if not os.path.exists(prototype_path):
            print(f"  ❌ PrototypeDesign路径不存在: {prototype_path}")
            return False
        
        # 检查关键文件
        key_files = ["graph.py", "main.py", "server.py", "state.py"]
        missing_files = []
        
        for file in key_files:
            file_path = os.path.join(prototype_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            print(f"  ❌ 缺少关键文件: {', '.join(missing_files)}")
            return False
        
        # 检查输出目录
        output_dir = os.path.join(prototype_path, "outputs")
        if not os.path.exists(output_dir):
            print(f"  📁 创建输出目录: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        
        print("  ✅ PrototypeDesign检查通过")
        print(f"  📁 路径: {prototype_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ 检查过程中出现异常: {e}")
        return False


def print_service_info(host: str, port: int):
    """打印服务信息"""
    print("\n" + "=" * 60)
    print("🚀 AI Agent Web Service 已启动")
    print("=" * 60)
    print(f"🌐 服务地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"📖 ReDoc文档: http://{host}:{port}/redoc")
    print(f"❤️  健康检查: http://{host}:{port}/health")
    print("\n📋 PrototypeDesign API接口:")
    print(f"  🎨 同步设计: POST http://{host}:{port}/api/v1/prototype_design/design")
    print(f"  🌊 流式设计: POST http://{host}:{port}/api/v1/prototype_design/design/stream")
    print(f"  📁 原型列表: GET http://{host}:{port}/api/v1/prototype_design/prototypes")
    print(f"  🌐 服务器管理: POST http://{host}:{port}/api/v1/prototype_design/server/start")
    print(f"  🔍 健康检查: GET http://{host}:{port}/api/v1/prototype_design/health")
    print("\n💡 使用示例:")
    print("  curl -X POST http://localhost:8000/api/v1/prototype_design/design \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"requirements\": \"创建一个登录页面\"}'")
    print("\n🧪 运行测试:")
    print(f"  python test_prototype_design.py http://{host}:{port}")
    print("=" * 60)


async def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 运行基本功能测试...")
    
    try:
        import httpx
        
        # 测试健康检查
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("  ✅ 主服务健康检查通过")
            else:
                print(f"  ❌ 主服务健康检查失败: {response.status_code}")
                return False
            
            # 测试PrototypeDesign健康检查
            response = await client.get("http://localhost:8000/api/v1/prototype_design/health")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ PrototypeDesign健康检查通过: {data.get('status')}")
            else:
                print(f"  ❌ PrototypeDesign健康检查失败: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 基本功能测试异常: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="启动AI Agent Web Service (包含PrototypeDesign)")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="启用自动重载")
    parser.add_argument("--log-level", default="info", help="日志级别")
    parser.add_argument("--skip-check", action="store_true", help="跳过可用性检查")
    parser.add_argument("--test", action="store_true", help="启动后运行测试")
    
    args = parser.parse_args()
    
    print("🚀 启动AI Agent Web Service (包含PrototypeDesign)")
    print("-" * 50)
    
    # 检查PrototypeDesign可用性
    if not args.skip_check:
        if not check_prototype_design_availability():
            print("\n❌ PrototypeDesign不可用，请检查配置")
            print("💡 提示:")
            print("  1. 确保agent-frameworks/langgraph/prototype_design目录存在")
            print("  2. 确保prototype_design的关键文件完整")
            print("  3. 或使用 --skip-check 参数跳过检查")
            sys.exit(1)
    else:
        print("⏭️  跳过可用性检查")
    
    # 打印服务信息
    print_service_info(args.host, args.port)
    
    # 启动服务器
    try:
        print(f"\n🔄 启动服务器 {args.host}:{args.port}...")
        
        # 如果需要测试，在后台启动服务器
        if args.test:
            import threading
            import time
            
            def run_server():
                uvicorn.run(
                    "app.main:app",
                    host=args.host,
                    port=args.port,
                    reload=args.reload,
                    log_level=args.log_level
                )
            
            # 在后台线程启动服务器
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # 等待服务器启动
            print("⏳ 等待服务器启动...")
            time.sleep(3)
            
            # 运行测试
            async def run_test():
                success = await test_basic_functionality()
                if success:
                    print("\n✅ 基本功能测试通过！")
                    print("🧪 运行完整测试: python test_prototype_design.py")
                else:
                    print("\n❌ 基本功能测试失败")
            
            asyncio.run(run_test())
            
            # 保持服务器运行
            print("\n🌐 服务器继续运行，按 Ctrl+C 停止...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 服务器已停止")
        else:
            # 正常启动服务器
            uvicorn.run(
                "app.main:app",
                host=args.host,
                port=args.port,
                reload=args.reload,
                log_level=args.log_level
            )
            
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
