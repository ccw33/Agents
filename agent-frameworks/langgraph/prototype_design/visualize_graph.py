#!/usr/bin/env python3
"""
图形可视化脚本
用于展示原型设计Agent的工作流图
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from graph import create_prototype_graph, visualize_graph, get_graph_mermaid
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)


def main():
    """主函数"""
    print("🎨 原型设计Agent图形可视化")
    print("=" * 50)
    
    try:
        # 创建图形
        print("📊 正在创建工作流图...")
        graph = create_prototype_graph()
        
        # 获取Mermaid代码
        print("🔍 获取Mermaid图形代码...")
        mermaid_code = get_graph_mermaid()
        
        if mermaid_code:
            print("\n📋 Mermaid图形代码:")
            print("-" * 30)
            print(mermaid_code)
            print("-" * 30)
        
        # 尝试可视化
        print("\n🖼️  尝试生成图形可视化...")
        output_path = current_dir / "outputs" / "workflow_graph.png"
        output_path.parent.mkdir(exist_ok=True)
        
        try:
            visualize_graph(str(output_path))
        except Exception as e:
            print(f"⚠️  图形生成失败: {e}")
            print("💡 建议使用 LangGraph Studio 进行可视化")
        
        # 显示图形结构信息
        print("\n📈 工作流图结构信息:")
        print(f"   节点数量: {len(graph.get_graph().nodes)}")
        print(f"   边数量: {len(graph.get_graph().edges)}")
        
        print("\n🔗 节点列表:")
        for node in graph.get_graph().nodes:
            print(f"   • {node}")
        
        print("\n🔀 边列表:")
        for edge in graph.get_graph().edges:
            print(f"   • {edge}")
        
        print("\n🌐 LangGraph Studio 访问地址:")
        print("   📱 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024")
        print("   🚀 API: http://127.0.0.1:2024")
        print("   📚 API Docs: http://127.0.0.1:2024/docs")
        
        print("\n✅ 图形可视化完成！")
        print("💡 提示: 使用 LangGraph Studio 可以获得最佳的交互式可视化体验")
        
    except Exception as e:
        print(f"❌ 可视化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
