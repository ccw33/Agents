#!/usr/bin/env python3
"""
快速运行示例
用于快速测试原型设计Agent的功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from graph import PrototypeDesignWorkflow
    from server import quick_start_server
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖包:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def quick_demo():
    """快速演示"""
    print("🚀 原型设计Agent快速演示")
    print("=" * 50)
    
    # 检查环境变量
    try:
        from config import get_config
        config = get_config()
        if not config.dashscope_api_key:
            print("⚠️  请设置 DASHSCOPE_API_KEY 环境变量")
            print("请在.env文件中配置或设置环境变量")
            return False
    except Exception as e:
        print(f"⚠️  配置检查失败: {e}")
        return False
    
    # 创建工作流
    workflow = PrototypeDesignWorkflow()
    
    # 简单的测试需求
    requirements = """
    创建一个简单的个人名片页面，包含：
    1. 个人头像（使用占位图片）
    2. 姓名和职位
    3. 联系方式（邮箱、电话）
    4. 简短的个人介绍
    5. 社交媒体链接
    6. 使用现代化的卡片设计
    """
    
    print(f"📋 演示需求: {requirements}")
    print("\n🔄 开始生成原型...")
    
    try:
        # 运行工作流
        result = workflow.run(requirements, thread_id="quick-demo")
        
        if result["success"]:
            print("\n✅ 原型生成成功！")
            print(f"🔄 迭代次数: {result['iteration_count']}")
            print(f"✔️  验证通过: {result['is_approved']}")
            
            # 启动服务器
            output_dir = os.path.join(current_dir, "outputs")
            server_url = quick_start_server(output_dir, port=8000, open_browser=True)
            print(f"🌐 原型地址: {server_url}")
            
            print("\n🎉 演示完成！浏览器应该已经自动打开原型页面。")
            print("按 Ctrl+C 停止服务器")
            
            # 保持服务器运行
            import time
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 服务器已停止")
            
            return True
        else:
            print(f"\n❌ 原型生成失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 执行过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def interactive_demo():
    """交互式演示"""
    print("🚀 原型设计Agent交互式演示")
    print("=" * 50)
    
    # 检查环境变量
    try:
        from config import get_config
        config = get_config()
        if not config.dashscope_api_key:
            print("⚠️  请设置 DASHSCOPE_API_KEY 环境变量")
            print("请在.env文件中配置或设置环境变量")
            return False
    except Exception as e:
        print(f"⚠️  配置检查失败: {e}")
        return False
    
    workflow = PrototypeDesignWorkflow()
    
    print("请输入你的原型需求（输入 'quit' 退出）:")
    
    while True:
        try:
            requirements = input("\n📋 需求描述: ").strip()
            
            if requirements.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if not requirements:
                print("⚠️  请输入有效的需求描述")
                continue
            
            print(f"\n🔄 正在生成原型...")
            
            # 生成唯一的线程ID
            import uuid
            thread_id = str(uuid.uuid4())[:8]
            
            result = workflow.run(requirements, thread_id=thread_id)
            
            if result["success"]:
                print(f"\n✅ 原型生成成功！")
                print(f"🔄 迭代次数: {result['iteration_count']}")
                print(f"✔️  验证通过: {result['is_approved']}")
                
                # 询问是否查看原型
                view = input("\n🌐 是否在浏览器中查看原型？(y/n): ").strip().lower()
                if view in ['y', 'yes']:
                    output_dir = os.path.join(current_dir, "outputs")
                    server_url = quick_start_server(output_dir, port=8000, open_browser=True)
                    print(f"🌐 原型地址: {server_url}")
            else:
                print(f"\n❌ 原型生成失败: {result.get('error', '未知错误')}")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_demo()
    else:
        quick_demo()


if __name__ == "__main__":
    main()
