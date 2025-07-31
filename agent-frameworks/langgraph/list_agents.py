#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LangGraph框架的Agent列表获取器

import json
import os

def main():
    """获取可用的LangGraph Agent列表"""
    agents_info = {
        "framework": "langgraph",
        "agents": {
            "chat_agent": {
                "description": "基础对话Agent",
                "input_schema": {"message": "str"}
            },
            "research_agent": {
                "description": "研究分析Agent",
                "input_schema": {"query": "str", "max_results": "int"}
            }
        }
    }

    # 检查prototype_design是否可用
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prototype_path = os.path.join(current_dir, "prototype_design")

    if os.path.exists(prototype_path):
        # 检查关键文件是否存在
        key_files = ["graph.py", "main.py", "server.py", "state.py"]
        if all(os.path.exists(os.path.join(prototype_path, f)) for f in key_files):
            agents_info["agents"]["prototype_design"] = {
                "description": "高保真原型设计Agent，基于LangGraph和多模态验证",
                "input_schema": {
                    "requirements": "str"
                },
                "features": [
                    "智能设计生成HTML/CSS/JavaScript",
                    "多模态验证（截图分析）",
                    "迭代优化（最多5次）",
                    "本地服务器预览",
                    "响应式设计支持"
                ],
                "output_schema": {
                    "success": "bool",
                    "prototype_url": "str",
                    "iteration_count": "int",
                    "is_approved": "bool",
                    "html_code": "str",
                    "css_code": "str",
                    "js_code": "str"
                }
            }

    print(json.dumps(agents_info, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
