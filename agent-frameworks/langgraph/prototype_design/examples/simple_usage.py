"""
简单使用示例
演示如何使用原型设计Agent
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from graph import PrototypeDesignWorkflow
    from server import quick_start_server
except ImportError:
    # 如果在examples目录下运行，尝试从上级目录导入
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    from graph import PrototypeDesignWorkflow
    from server import quick_start_server


def example_1_login_page():
    """示例1: 创建登录页面"""
    print("🔐 示例1: 创建登录页面")
    
    workflow = PrototypeDesignWorkflow()
    
    requirements = """
    创建一个现代化的登录页面，要求：
    1. 包含用户名和密码输入框
    2. 登录按钮和忘记密码链接
    3. 使用蓝色主题色
    4. 响应式设计，支持移动端
    5. 添加简单的表单验证
    """
    
    print(f"需求: {requirements}")
    
    result = workflow.run(requirements, thread_id="example-login")
    
    if result["success"]:
        print(f"✅ 登录页面创建成功!")
        print(f"🌐 访问地址: {result['prototype_url']}")
        print(f"🔄 迭代次数: {result['iteration_count']}")
    else:
        print(f"❌ 创建失败: {result['error']}")
    
    return result


def example_2_dashboard():
    """示例2: 创建仪表板"""
    print("\n📊 示例2: 创建数据仪表板")
    
    workflow = PrototypeDesignWorkflow()
    
    requirements = """
    设计一个数据仪表板页面，包含：
    1. 顶部导航栏，包含logo和用户头像
    2. 侧边栏菜单，包含主要功能模块
    3. 主内容区域包含4个统计卡片
    4. 一个图表展示区域（可以用占位符）
    5. 一个数据表格
    6. 使用现代化的设计风格，深色主题
    7. 支持响应式布局
    """
    
    print(f"需求: {requirements}")
    
    result = workflow.run(requirements, thread_id="example-dashboard")
    
    if result["success"]:
        print(f"✅ 仪表板创建成功!")
        print(f"🌐 访问地址: {result['prototype_url']}")
        print(f"🔄 迭代次数: {result['iteration_count']}")
    else:
        print(f"❌ 创建失败: {result['error']}")
    
    return result


def example_3_ecommerce():
    """示例3: 创建电商产品页面"""
    print("\n🛒 示例3: 创建电商产品页面")
    
    workflow = PrototypeDesignWorkflow()
    
    requirements = """
    创建一个电商产品详情页面，包含：
    1. 产品图片轮播（可以用占位图片）
    2. 产品标题、价格、评分
    3. 产品描述和规格参数
    4. 购买按钮和加入购物车按钮
    5. 用户评价区域
    6. 相关产品推荐
    7. 使用橙色作为主题色
    8. 移动端友好的设计
    """
    
    print(f"需求: {requirements}")
    
    result = workflow.run(requirements, thread_id="example-ecommerce")
    
    if result["success"]:
        print(f"✅ 电商页面创建成功!")
        print(f"🌐 访问地址: {result['prototype_url']}")
        print(f"🔄 迭代次数: {result['iteration_count']}")
    else:
        print(f"❌ 创建失败: {result['error']}")
    
    return result


def example_4_stream_mode():
    """示例4: 流式模式观察设计过程"""
    print("\n🔄 示例4: 流式模式观察设计过程")
    
    workflow = PrototypeDesignWorkflow()
    
    requirements = """
    创建一个博客文章列表页面，包含：
    1. 页面标题和搜索框
    2. 文章卡片列表，每个卡片包含标题、摘要、作者、发布时间
    3. 分页导航
    4. 侧边栏包含分类和热门文章
    5. 简洁的设计风格
    """
    
    print(f"需求: {requirements}")
    print("\n观察设计过程:")
    
    for event in workflow.stream_run(requirements, thread_id="example-blog"):
        for node_name, node_data in event.items():
            if node_name == "designer":
                iteration = node_data.get('iteration_count', 0)
                print(f"  🎨 Designer正在工作... (第{iteration}次迭代)")
            elif node_name == "validator":
                result = node_data.get('validation_result', 'UNKNOWN')
                print(f"  🔍 Validator验证结果: {result}")
                if result == "REJECTED":
                    feedback = node_data.get('validation_feedback', '')
                    print(f"  💬 反馈: {feedback[:100]}...")
            elif node_name == "finalize":
                print(f"  ✅ 正在生成最终原型...")
    
    print("\n✅ 博客页面设计完成!")


def start_server_for_examples():
    """启动服务器查看所有示例"""
    print("\n🌐 启动服务器查看所有生成的原型...")
    
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    
    try:
        server_url = quick_start_server(output_dir, port=8000, open_browser=True)
        print(f"✅ 服务器已启动: {server_url}")
        print("🔗 你可以在浏览器中查看所有生成的原型")
        print("按 Ctrl+C 停止服务器")
        
        # 保持服务器运行
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")


def main():
    """主函数"""
    print("🚀 原型设计Agent使用示例")
    print("=" * 50)
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  请设置 OPENAI_API_KEY 环境变量")
        return
    
    try:
        # 运行示例
        examples = [
            example_1_login_page,
            example_2_dashboard,
            example_3_ecommerce,
            example_4_stream_mode,
        ]
        
        for i, example_func in enumerate(examples, 1):
            print(f"\n{'='*20} 运行示例 {i} {'='*20}")
            try:
                example_func()
            except Exception as e:
                print(f"❌ 示例 {i} 执行失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 启动服务器
        print(f"\n{'='*20} 启动服务器 {'='*20}")
        start_server_for_examples()
        
    except KeyboardInterrupt:
        print("\n👋 示例演示结束")
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
