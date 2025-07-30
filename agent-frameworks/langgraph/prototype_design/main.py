"""
高保真原型设计Agent主程序
提供命令行接口和API接口
"""

import os
import sys
import argparse
import uuid
from typing import Dict, Any
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from .graph import PrototypeDesignWorkflow
    from .server import quick_start_server, get_server
except ImportError:
    # 如果相对导入失败，使用直接导入
    from graph import PrototypeDesignWorkflow
    from server import quick_start_server, get_server
from langsmith import traceable


class PrototypeDesignCLI:
    """
    原型设计命令行接口
    """
    
    def __init__(self):
        """初始化CLI"""
        self.workflow = PrototypeDesignWorkflow()
        self.output_dir = os.path.join(os.path.dirname(__file__), "outputs")
        
        # 确保输出目录存在
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    @traceable(run_type="chain", name="CLI Run Prototype Design")
    def run_design(self, requirements: str, interactive: bool = False, auto_open: bool = True) -> Dict[str, Any]:
        """
        运行原型设计
        
        Args:
            requirements: 用户需求
            interactive: 是否交互模式
            auto_open: 是否自动打开浏览器
            
        Returns:
            设计结果
        """
        print("🚀 开始原型设计...")
        print(f"📋 需求：{requirements}")
        print("-" * 50)
        
        # 生成唯一的线程ID
        thread_id = str(uuid.uuid4())
        
        if interactive:
            # 交互模式：显示中间过程
            return self._run_interactive(requirements, thread_id, auto_open)
        else:
            # 非交互模式：直接返回结果
            return self._run_direct(requirements, thread_id, auto_open)
    
    def _run_interactive(self, requirements: str, thread_id: str, auto_open: bool) -> Dict[str, Any]:
        """交互模式运行"""
        print("🔄 交互模式：将显示设计过程...")
        
        for event in self.workflow.stream_run(requirements, thread_id):
            for node_name, node_data in event.items():
                if node_name == "designer":
                    print(f"🎨 Designer正在工作... (第{node_data.get('iteration_count', 0)}次迭代)")
                elif node_name == "validator":
                    result = node_data.get('validation_result', 'UNKNOWN')
                    print(f"🔍 Validator验证结果: {result}")
                    if result == "REJECTED":
                        feedback = node_data.get('validation_feedback', '')
                        print(f"💬 反馈: {feedback[:100]}...")
                elif node_name == "finalize":
                    print("✅ 正在生成最终原型...")
        
        # 获取最终结果
        result = self.workflow.run(requirements, thread_id)
        self._print_result(result, auto_open)
        return result
    
    def _run_direct(self, requirements: str, thread_id: str, auto_open: bool) -> Dict[str, Any]:
        """直接模式运行"""
        print("⏳ 正在生成原型，请稍候...")
        
        result = self.workflow.run(requirements, thread_id)
        self._print_result(result, auto_open)
        return result
    
    def _print_result(self, result: Dict[str, Any], auto_open: bool):
        """打印结果"""
        print("-" * 50)
        
        if result.get("success"):
            print("✅ 原型设计完成！")
            print(f"🔄 迭代次数: {result.get('iteration_count', 0)}")
            print(f"✔️  验证状态: {'通过' if result.get('is_approved') else '未通过'}")
            
            if result.get("prototype_url"):
                print(f"🌐 访问地址: {result['prototype_url']}")
                
                if auto_open:
                    # 启动服务器并打开浏览器
                    try:
                        quick_start_server(self.output_dir, open_browser=True)
                    except Exception as e:
                        print(f"⚠️  自动打开浏览器失败: {e}")
            
            if result.get("validation_feedback"):
                print(f"💬 最终反馈: {result['validation_feedback'][:200]}...")
        else:
            print("❌ 原型设计失败！")
            print(f"错误信息: {result.get('error', '未知错误')}")
    
    def list_prototypes(self):
        """列出已生成的原型"""
        server = get_server(self.output_dir)
        files = server.list_files()
        
        if not files:
            print("📁 暂无已生成的原型")
            return
        
        print("📁 已生成的原型:")
        for i, file in enumerate(files, 1):
            filepath = os.path.join(self.output_dir, file)
            mtime = os.path.getmtime(filepath)
            import datetime
            time_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {i}. {file} (创建时间: {time_str})")
    
    def start_server(self, port: int = 8000):
        """启动服务器"""
        print(f"🌐 启动原型服务器...")
        url = quick_start_server(self.output_dir, port, open_browser=True)
        print(f"✅ 服务器已启动: {url}")
        print("按 Ctrl+C 停止服务器")
        
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="高保真原型设计Agent")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 设计命令
    design_parser = subparsers.add_parser("design", help="生成原型")
    design_parser.add_argument("requirements", help="原型需求描述")
    design_parser.add_argument("-i", "--interactive", action="store_true", help="交互模式")
    design_parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    
    # 列表命令
    subparsers.add_parser("list", help="列出已生成的原型")
    
    # 服务器命令
    server_parser = subparsers.add_parser("server", help="启动原型服务器")
    server_parser.add_argument("-p", "--port", type=int, default=8000, help="端口号")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PrototypeDesignCLI()
    
    if args.command == "design":
        cli.run_design(
            args.requirements,
            interactive=args.interactive,
            auto_open=not args.no_open
        )
    elif args.command == "list":
        cli.list_prototypes()
    elif args.command == "server":
        cli.start_server(args.port)


if __name__ == "__main__":
    main()
