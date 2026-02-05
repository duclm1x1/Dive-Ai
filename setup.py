"""
Dive AI V20.2.1 Unified - Setup Configuration
Production-Ready Autonomous AI Platform with Memory Loop Architecture
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="dive-ai",
    version="20.2.1-unified",
    author="Duc Le",
    author_email="support@dive-ai.com",
    description="Production-Ready Autonomous AI Platform with Memory Loop Architecture",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/duclm1x1/Dive-Ai",
    project_urls={
        "Bug Tracker": "https://github.com/duclm1x1/Dive-Ai/issues",
        "Documentation": "https://github.com/duclm1x1/Dive-Ai/wiki",
        "Source Code": "https://github.com/duclm1x1/Dive-Ai",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dive-ai=deployment.first_run:main",
            "dive-memory=skills.dive-memory-v3.scripts.dive_memory:main",
            "dive-deploy=deploy_dive_ai_128_agents:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json"],
    },
    zip_safe=False,
    keywords=[
        "ai",
        "artificial-intelligence",
        "machine-learning",
        "deep-learning",
        "autonomous-ai",
        "memory-loop",
        "multi-agent",
        "code-generation",
        "llm",
        "chatgpt",
        "claude",
        "manus",
    ],
)
