#!/usr/bin/env python3
"""
配置测试脚本
用于验证环境配置是否正确
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from config import get_config
    import openai
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖包:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def test_config():
    """测试配置"""
    print("🔧 测试环境配置...")
    print("=" * 50)
    
    try:
        # 获取配置
        config = get_config()
        
        # 打印配置摘要
        config.print_config_summary()
        
        # 检查必要的配置
        if not config.dashscope_api_key:
            print("❌ 缺少DASHSCOPE_API_KEY")
            return False
        
        print("\n✅ 配置检查通过！")
        return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False


def test_api_connection():
    """测试API连接"""
    print("\n🌐 测试API连接...")
    print("=" * 50)
    
    try:
        config = get_config()
        client_config = config.get_openai_client_config()
        
        # 创建客户端
        client = openai.OpenAI(
            api_key=client_config["api_key"],
            base_url=client_config["base_url"]
        )
        
        # 测试简单的API调用
        print("📡 正在测试API连接...")
        response = client.chat.completions.create(
            model=config.validator_model,  # 使用较小的模型测试
            messages=[
                {"role": "user", "content": "你好，请回复'连接成功'"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"📨 API响应: {result}")
        
        if response.usage:
            print(f"🔢 Token使用: {response.usage}")
        
        print("✅ API连接测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        print("请检查:")
        print("1. DASHSCOPE_API_KEY是否正确")
        print("2. 网络连接是否正常")
        print("3. API配额是否充足")
        return False


def test_models():
    """测试模型配置"""
    print("\n🤖 测试模型配置...")
    print("=" * 50)
    
    try:
        config = get_config()
        
        print(f"Designer模型: {config.designer_model}")
        print(f"Validator模型: {config.validator_model}")
        
        # 测试Designer模型
        print("\n🎨 测试Designer模型...")
        client_config = config.get_openai_client_config()
        client = openai.OpenAI(
            api_key=client_config["api_key"],
            base_url=client_config["base_url"]
        )
        
        response = client.chat.completions.create(
            model=config.designer_model,
            messages=[
                {"role": "user", "content": "生成一个简单的HTML按钮代码"}
            ],
            max_tokens=100
        )
        
        print(f"✅ Designer模型响应正常")
        if config.enable_debug:
            print(f"响应内容: {response.choices[0].message.content[:100]}...")
        
        # 测试Validator模型
        print("\n🔍 测试Validator模型...")
        response = client.chat.completions.create(
            model=config.validator_model,
            messages=[
                {"role": "user", "content": "验证这个HTML代码是否正确: <button>点击</button>"}
            ],
            max_tokens=50
        )
        
        print(f"✅ Validator模型响应正常")
        if config.enable_debug:
            print(f"响应内容: {response.choices[0].message.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 高保真原型设计Agent配置测试")
    print("=" * 60)
    
    # 检查.env文件
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("⚠️  未找到.env文件")
        print("请复制.env.example为.env并填入配置:")
        print("cp .env.example .env")
        return False
    
    tests = [
        ("配置检查", test_config),
        ("API连接", test_api_connection),
        ("模型测试", test_models),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except KeyboardInterrupt:
            print("\n👋 测试被用户中断")
            break
        except Exception as e:
            print(f"❌ {test_name} 发生异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统已准备就绪。")
        print("\n🚀 现在可以开始使用原型设计Agent:")
        print("python3 run_example.py")
        return True
    else:
        print("❌ 部分测试失败，请检查配置。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
