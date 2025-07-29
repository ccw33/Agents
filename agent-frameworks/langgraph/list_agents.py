#!/usr/bin/env python3
# ��架的Agent列表获取器示例

import json

def main():
    # TODO: 在这里实现获取可用Agent列表的逻辑
    agents_info = {
        "framework": "langgraph",
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
