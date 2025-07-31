#!/usr/bin/env python3
"""
测试新的Validator Agent功能
使用qwen-vl-plus多模态模型和browser-use进行验证
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.validator import ValidatorAgent
from state import PrototypeState

async def test_validator():
    """测试validator功能"""
    
    # 创建测试状态
    test_state = PrototypeState(
        requirements="创建一个简单的登录页面，包含用户名和密码输入框，以及登录按钮",
        html_code="""
        <div class="login-container">
            <h2>用户登录</h2>
            <form class="login-form">
                <div class="form-group">
                    <label for="username">用户名:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">密码:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="login-btn">登录</button>
            </form>
        </div>
        """,
        css_code="""
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .login-container h2 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
        }
        
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .login-btn {
            width: 100%;
            padding: 12px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
        
        .login-btn:hover {
            background-color: #0056b3;
        }
        """,
        js_code="""
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.querySelector('.login-form');
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                if (username && password) {
                    alert('登录成功！用户名: ' + username);
                } else {
                    alert('请填写完整的用户名和密码');
                }
            });
        });
        """,
        iteration_count=0
    )
    
    print("🚀 开始测试Validator Agent...")
    print(f"📋 测试需求: {test_state['requirements']}")
    
    try:
        # 创建validator实例
        validator = ValidatorAgent()
        
        # 执行验证
        result = validator.validate_prototype(test_state)
        
        print("\n✅ 验证完成!")
        print(f"📊 验证结果: {result['validation_result']}")
        print(f"🔍 是否通过: {result['is_approved']}")
        print(f"📝 验证反馈:\n{result['validation_feedback']}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_validator())
