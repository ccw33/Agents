#!/bin/bash

# 高保真原型设计Agent启动脚本

echo "🚀 启动高保真原型设计Agent"
echo "=================================="

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python版本过低，需要Python 3.8或更高版本"
    echo "当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env配置文件"
    if [ -f ".env.example" ]; then
        echo "📋 发现.env.example文件，是否复制为.env？(y/n): "
        read -p "" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp .env.example .env
            echo "✅ 已复制.env.example为.env"
            echo "⚠️  请编辑.env文件，填入您的DASHSCOPE_API_KEY"
            echo "然后重新运行此脚本"
            exit 1
        fi
    fi
    echo "请创建.env文件并配置必要的环境变量"
    exit 1
fi

# 检查并安装依赖
if [ -f "requirements.txt" ]; then
    echo "📦 检查依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
fi

# 显示使用选项
echo ""
echo "请选择运行模式:"
echo "1. 配置测试 (推荐首次运行)"
echo "2. 快速演示"
echo "3. 交互式模式"
echo "4. 命令行模式"
echo "5. 运行完整测试"
echo "6. 启动服务器"

read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo "🔧 运行配置测试..."
        python3 test_config.py
        ;;
    2)
        echo "🎯 启动快速演示..."
        python3 run_example.py
        ;;
    3)
        echo "💬 启动交互式模式..."
        python3 run_example.py interactive
        ;;
    4)
        echo "⌨️  命令行模式"
        echo "使用方法: python3 -m prototype_design.main design '你的需求'"
        echo "示例: python3 -m prototype_design.main design '创建一个登录页面'"
        ;;
    5)
        echo "🧪 运行完整测试..."
        python3 test_workflow.py
        ;;
    6)
        echo "🌐 启动服务器..."
        python3 -m prototype_design.main server
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "👋 感谢使用高保真原型设计Agent！"
