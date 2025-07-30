"""
安装脚本
用于安装高保真原型设计Agent包
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取requirements文件
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="prototype-design-agent",
    version="1.0.0",
    author="Prototype Design Team",
    author_email="team@prototypedesign.ai",
    description="基于LangGraph和LangSmith的高保真原型设计Agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/prototype-design-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "enhanced": [
            "beautifulsoup4>=4.12.0",
            "Pillow>=10.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "prototype-design=prototype_design.main:main",
            "prototype-demo=prototype_design.run_example:main",
        ],
    },
    include_package_data=True,
    package_data={
        "prototype_design": [
            "templates/*.html",
            "outputs/.gitkeep",
        ],
    },
    keywords=[
        "langgraph",
        "langsmith",
        "prototype",
        "design",
        "agent",
        "ai",
        "frontend",
        "html",
        "css",
        "javascript",
        "ui",
        "ux"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-org/prototype-design-agent/issues",
        "Source": "https://github.com/your-org/prototype-design-agent",
        "Documentation": "https://github.com/your-org/prototype-design-agent/blob/main/README.md",
    },
)
