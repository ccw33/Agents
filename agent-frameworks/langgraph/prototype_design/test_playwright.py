#!/usr/bin/env python3
"""
测试Playwright浏览器显示
"""

import asyncio
import tempfile
import os
from playwright.async_api import async_playwright

async def test_playwright_browser():
    """测试Playwright是否能显示浏览器"""
    
    # 创建测试HTML文件
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Playwright测试</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                color: white;
            }
            h1 { font-size: 3em; }
            p { font-size: 1.5em; }
        </style>
    </head>
    <body>
        <h1>🎭 Playwright 测试</h1>
        <p>如果您看到这个页面，说明Playwright正在工作！</p>
        <p>这个浏览器窗口将在5秒后自动关闭</p>
    </body>
    </html>
    """
    
    # 创建临时HTML文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        html_file = f.name
    
    try:
        print("🚀 启动Playwright测试...")
        
        # 启动playwright
        playwright = await async_playwright().start()
        
        # 启动浏览器 - 显示模式
        print("🌐 启动浏览器（显示模式）...")
        browser = await playwright.chromium.launch(
            headless=False,  # 显示浏览器
            slow_mo=1000     # 慢动作，便于观察
        )
        
        # 创建页面
        page = await browser.new_page(viewport={"width": 1280, "height": 1024})
        
        # 导航到HTML文件
        file_url = f"file://{os.path.abspath(html_file)}"
        print(f"📄 打开页面: {file_url}")
        await page.goto(file_url)
        
        # 等待5秒让用户看到
        print("⏰ 等待5秒...")
        await asyncio.sleep(5)
        
        # 截图
        print("📸 截图...")
        screenshot = await page.screenshot()
        
        # 关闭浏览器
        print("🔚 关闭浏览器...")
        await browser.close()
        
        print("✅ 测试完成！")
        print(f"📊 截图大小: {len(screenshot)} bytes")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 清理临时文件
        if os.path.exists(html_file):
            os.unlink(html_file)

if __name__ == "__main__":
    asyncio.run(test_playwright_browser())
