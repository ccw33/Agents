"""
测试脚本
用于验证原型设计工作流是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from .graph import PrototypeDesignWorkflow
    from .server import quick_start_server
    from .config import get_config
except ImportError:
    # 如果相对导入失败，使用直接导入
    from graph import PrototypeDesignWorkflow
    from server import quick_start_server
    from config import get_config


def test_basic_workflow():
    """测试基本工作流"""
    print("🧪 开始测试基本工作流...")
    
    # 创建工作流实例
    workflow = PrototypeDesignWorkflow()
    
    # 测试需求
    requirements = "创建一个简单的登录页面，包含用户名输入框、密码输入框和登录按钮。使用现代化的设计风格。"
    
    print(f"📋 测试需求: {requirements}")
    
    try:
        # 运行工作流
        result = workflow.run(requirements, thread_id="test-001")
        
        print("\n📊 测试结果:")
        print(f"✅ 成功: {result.get('success', False)}")
        print(f"🔄 迭代次数: {result.get('iteration_count', 0)}")
        print(f"✔️  验证通过: {result.get('is_approved', False)}")
        
        if result.get('success'):
            print(f"🌐 原型地址: {result.get('prototype_url', 'N/A')}")
            
            # 检查生成的代码
            if result.get('html_code'):
                print(f"📄 HTML代码长度: {len(result['html_code'])} 字符")
            if result.get('css_code'):
                print(f"🎨 CSS代码长度: {len(result['css_code'])} 字符")
            if result.get('js_code'):
                print(f"⚡ JS代码长度: {len(result['js_code'])} 字符")
            
            print("\n✅ 基本工作流测试通过！")
            return True
        else:
            print(f"\n❌ 工作流执行失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stream_workflow():
    """测试流式工作流"""
    print("\n🧪 开始测试流式工作流...")
    
    workflow = PrototypeDesignWorkflow()
    requirements = "创建一个产品卡片组件，包含产品图片、标题、价格和购买按钮。"
    
    print(f"📋 测试需求: {requirements}")
    
    try:
        print("\n🔄 流式执行过程:")
        for event in workflow.stream_run(requirements, thread_id="test-002"):
            for node_name, node_data in event.items():
                if node_name == "designer":
                    print(f"  🎨 Designer: 第{node_data.get('iteration_count', 0)}次迭代")
                elif node_name == "validator":
                    result = node_data.get('validation_result', 'UNKNOWN')
                    print(f"  🔍 Validator: {result}")
                elif node_name == "finalize":
                    print(f"  ✅ Finalize: 生成最终原型")
        
        print("\n✅ 流式工作流测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 流式测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server():
    """测试服务器功能"""
    print("\n🧪 开始测试服务器功能...")
    
    try:
        output_dir = os.path.join(os.path.dirname(__file__), "outputs")
        
        # 创建一个测试HTML文件
        test_html = """<!DOCTYPE html>
<html>
<head>
    <title>测试页面</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .test-card { background: #f0f0f0; padding: 20px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="test-card">
        <h1>测试页面</h1>
        <p>这是一个测试页面，用于验证服务器功能。</p>
        <button onclick="alert('测试成功！')">点击测试</button>
    </div>
</body>
</html>"""
        
        # 写入测试文件
        test_file = os.path.join(output_dir, "test.html")
        os.makedirs(output_dir, exist_ok=True)
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        print(f"📄 创建测试文件: {test_file}")
        
        # 启动服务器（不自动打开浏览器）
        server_url = quick_start_server(output_dir, port=8001, open_browser=False)
        print(f"🌐 服务器启动成功: {server_url}")
        print(f"🔗 测试地址: {server_url}/test.html")
        
        print("\n✅ 服务器功能测试通过！")
        print("💡 提示: 你可以在浏览器中访问上述地址查看测试页面")
        return True
        
    except Exception as e:
        print(f"\n❌ 服务器测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始原型设计Agent测试")
    print("=" * 50)
    
    # 检查环境变量
    try:
        config = get_config()
        config.print_config_summary()
    except Exception as e:
        print(f"⚠️  配置检查失败: {e}")
        print("请检查.env文件或环境变量设置")
        return False
    
    # 运行测试
    tests = [
        ("基本工作流", test_basic_workflow),
        ("流式工作流", test_stream_workflow),
        ("服务器功能", test_server),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 测试失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！原型设计Agent已准备就绪。")
        print("\n🚀 使用方法:")
        print("python -m prototype_design.main design '你的需求描述'")
        return True
    else:
        print("❌ 部分测试失败，请检查配置和代码。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
