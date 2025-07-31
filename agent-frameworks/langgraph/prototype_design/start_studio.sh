#!/bin/bash

# LangGraph Studio 启动脚本
# 用于快速启动原型设计Agent的LangGraph Studio环境

echo "🚀 启动LangGraph Studio - 原型设计Agent"
echo "================================================"

# 检查是否存在.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，正在创建..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已创建.env文件，请编辑并填入您的API密钥"
        echo "📝 需要配置的关键项目："
        echo "   - DASHSCOPE_API_KEY: 通义千问API密钥"
        echo "   - LANGSMITH_API_KEY: LangSmith API密钥（可选）"
        echo ""
        echo "⏸️  请先配置.env文件，然后重新运行此脚本"
        exit 1
    else
        echo "❌ 未找到.env.example文件"
        exit 1
    fi
fi

# 检查依赖
echo "🔍 检查依赖..."
if ! command -v langgraph &> /dev/null; then
    echo "❌ langgraph命令未找到，请先安装："
    echo "   pip install langgraph-cli"
    exit 1
fi

# 检查playwright
echo "🔍 检查playwright..."
if ! python -c "import playwright" &> /dev/null; then
    echo "⚠️  playwright未安装，正在安装..."
    pip install playwright
    playwright install
fi

# 检查其他依赖
echo "🔍 检查其他依赖..."
pip install -r requirements.txt

echo ""
echo "✅ 环境检查完成"
echo ""
echo "🌐 启动LangGraph Studio..."
echo "   - API服务器: http://127.0.0.1:2024"
echo "   - Studio界面: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
echo ""
echo "📋 使用说明："
echo "   1. 等待服务器启动完成"
echo "   2. 在浏览器中打开Studio界面"
echo "   3. 选择'prototype_design'图形"
echo "   4. 在Requirements字段输入您的需求"
echo "   5. 点击Submit开始执行"
echo ""
echo "🎯 示例需求："
echo "   创建一个现代化的登录页面，包含用户名、密码输入框和登录按钮"
echo ""
echo "⚠️  注意：首次运行可能需要下载模型，请耐心等待"
echo ""

# 启动LangGraph Studio
langgraph dev --no-browser --port 2024 --allow-blocking
