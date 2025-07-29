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
