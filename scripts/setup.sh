#!/bin/bash
# AI Agent项目初始化脚本

set -e

echo "🚀 AI Agent项目初始化开始..."

# 检查Python版本
echo "📋 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python版本过低，需要Python 3.10+，当前版本: $python_version"
    exit 1
fi
echo "✅ Python版本检查通过: $python_version"

# 创建必要的目录
echo "📁 创建项目目录结构..."
mkdir -p logs
mkdir -p docs
mkdir -p scripts

# 设置web-service环境
echo "🔧 设置web-service环境..."
cd web-service

# 复制环境变量文件
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ 已创建.env文件，请根据需要修改配置"
else
    echo "ℹ️  .env文件已存在"
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "🐍 创建Python虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "ℹ️  虚拟环境已存在"
fi

# 激活虚拟环境并安装依赖
echo "📦 安装Python依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ 依赖安装完成"

cd ..

# 检查agent-frameworks目录
echo "🔍 检查agent-frameworks目录..."
for framework in langgraph autogen crewai; do
    if [ -d "agent-frameworks/$framework" ]; then
        echo "✅ $framework 目录存在"
    else
        echo "⚠️  $framework 目录不存在，请确保已创建"
    fi
done

# 创建示例runner脚本
echo "📝 创建示例runner脚本..."
for framework in langgraph autogen crewai; do
    framework_dir="agent-frameworks/$framework"
    if [ -d "$framework_dir" ]; then
        # 创建示例runner.py
        if [ ! -f "$framework_dir/runner.py" ]; then
            cat > "$framework_dir/runner.py" << EOF
#!/usr/bin/env python3
# $framework框架的Agent执行器示例

import json
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='$framework Agent Runner')
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--agent-type', help='Agent类型')
    parser.add_argument('--agent-config', help='Agent配置')
    parser.add_argument('--crew-name', help='Crew名称')
    
    args = parser.parse_args()
    
    # 读取输入
    with open(args.input, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    print(f"执行$framework Agent: {input_data}")
    
    # TODO: 在这里实现具体的Agent执行逻辑
    result = {
        "status": "success",
        "output": f"$framework Agent执行完成",
        "framework": "$framework",
        "input_data": input_data
    }
    
    # 写入输出
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("执行完成")

if __name__ == "__main__":
    main()
EOF
            chmod +x "$framework_dir/runner.py"
            echo "✅ 已创建 $framework/runner.py 示例文件"
        fi
        
        # 创建示例list_agents.py
        if [ ! -f "$framework_dir/list_agents.py" ] && [ "$framework" != "crewai" ]; then
            cat > "$framework_dir/list_agents.py" << EOF
#!/usr/bin/env python3
# $framework框架的Agent列表获取器示例

import json

def main():
    # TODO: 在这里实现获取可用Agent列表的逻辑
    agents_info = {
        "framework": "$framework",
        "agents": {
            "example_agent": {
                "description": "示例Agent",
                "input_schema": {"message": "str"}
            }
        }
    }
    
    print(json.dumps(agents_info, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
EOF
            chmod +x "$framework_dir/list_agents.py"
            echo "✅ 已创建 $framework/list_agents.py 示例文件"
        fi
        
        # 为CrewAI创建list_crews.py
        if [ ! -f "$framework_dir/list_crews.py" ] && [ "$framework" = "crewai" ]; then
            cat > "$framework_dir/list_crews.py" << EOF
#!/usr/bin/env python3
# CrewAI框架的Crew列表获取器示例

import json

def main():
    # TODO: 在这里实现获取可用Crew列表的逻辑
    crews_info = {
        "framework": "crewai",
        "crews": {
            "example_crew": {
                "description": "示例Crew",
                "agents": ["agent1", "agent2"],
                "input_schema": {"topic": "str"}
            }
        }
    }
    
    print(json.dumps(crews_info, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
EOF
            chmod +x "$framework_dir/list_crews.py"
            echo "✅ 已创建 crewai/list_crews.py 示例文件"
        fi
    fi
done

echo ""
echo "🎉 AI Agent项目初始化完成！"
echo ""
echo "📋 下一步操作："
echo "1. 修改 web-service/.env 文件中的配置"
echo "2. 在各个agent-frameworks目录下实现具体的Agent"
echo "3. 运行 ./scripts/start_services.sh 启动服务"
echo ""
echo "🔗 有用的命令："
echo "  启动开发服务器: cd web-service && source venv/bin/activate && python app/main.py"
echo "  运行测试: cd web-service && source venv/bin/activate && pytest"
echo "  查看API文档: http://localhost:8000/docs"
echo ""
